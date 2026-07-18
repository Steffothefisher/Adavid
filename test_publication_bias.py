import pytest
from src.publication_bias_detector import Study, PublicationBiasDetector, run_meta_analysis


def test_meta_analysis_fixed_vs_random():
    """Verify fixed-effect and random-effects computations on a small dataset."""
    studies = [
        Study("Study1", 0.5, 0.1),
        Study("Study2", 0.2, 0.2),
        Study("Study3", 0.8, 0.15)
    ]
    
    # 1. Run fixed effect
    res_fixed = run_meta_analysis(studies, method="fixed")
    assert res_fixed.method == "fixed"
    assert res_fixed.combined_effect > 0.4
    assert res_fixed.standard_error < 0.1
    
    # 2. Run random effects
    res_random = run_meta_analysis(studies, method="random")
    assert res_random.method == "random"
    # Q statistic should be computed
    assert res_random.q_statistic >= 0
    assert res_random.tau_squared >= 0


def test_eggers_test_symmetric():
    """Verify Egger's test flags symmetric data as unbiased."""
    symmetric_studies = [
        Study("A", 0.30, 0.05),
        Study("B", 0.28, 0.10),
        Study("C", 0.32, 0.10),
        Study("D", 0.20, 0.20),
        Study("E", 0.40, 0.20),
        Study("F", 0.10, 0.30),
        Study("G", 0.50, 0.30),
    ]
    
    res = PublicationBiasDetector.eggers_test(symmetric_studies)
    assert res is not None
    assert res.bias_detected is False
    assert res.intercept_p_value >= 0.05
    # The true effect (slope) should be close to 0.3
    assert abs(res.slope - 0.3) < 0.1


def test_eggers_test_asymmetric():
    """Verify Egger's test flags asymmetric data as biased."""
    asymmetric_studies = [
        Study("Large1", 0.15, 0.04),
        Study("Large2", 0.14, 0.05),
        Study("Large3", 0.16, 0.05),
        Study("Small1", 0.55, 0.25),
        Study("Small2", 0.62, 0.28),
        Study("Small3", 0.50, 0.30),
        Study("Small4", 0.70, 0.32),
    ]
    
    res = PublicationBiasDetector.eggers_test(asymmetric_studies)
    assert res is not None
    assert res.bias_detected is True
    assert res.intercept_p_value < 0.05
    assert res.intercept > 0  # Significant positive intercept due to small positive study inflation


def test_beggs_test():
    """Verify Begg & Mazumdar rank correlation test results."""
    symmetric_studies = [
        Study("A", 0.30, 0.05),
        Study("B", 0.28, 0.10),
        Study("C", 0.32, 0.10),
        Study("D", 0.20, 0.20),
        Study("E", 0.40, 0.20),
        Study("F", 0.10, 0.30),
        Study("G", 0.50, 0.30),
    ]
    res_sym = PublicationBiasDetector.beggs_test(symmetric_studies)
    assert res_sym is not None
    assert res_sym.bias_detected is False
    
    asymmetric_studies = [
        Study("Large1", 0.15, 0.04),
        Study("Large2", 0.14, 0.05),
        Study("Large3", 0.16, 0.05),
        Study("Small1", 0.55, 0.25),
        Study("Small2", 0.62, 0.28),
        Study("Small3", 0.50, 0.30),
        Study("Small4", 0.70, 0.32),
    ]
    res_asym = PublicationBiasDetector.beggs_test(asymmetric_studies)
    # Begg's test has lower power but should calculate p-value
    assert res_asym is not None
    assert res_asym.p_value is not None


def test_trim_and_fill_symmetric():
    """Verify Trim-and-Fill doesn't fill studies on symmetric data."""
    symmetric_studies = [
        Study("A", 0.30, 0.05),
        Study("B", 0.28, 0.10),
        Study("C", 0.32, 0.10),
        Study("D", 0.20, 0.20),
        Study("E", 0.40, 0.20),
        Study("F", 0.10, 0.30),
        Study("G", 0.50, 0.30),
    ]
    
    res = PublicationBiasDetector.trim_and_fill(symmetric_studies)
    assert res is not None
    assert res.n_filled == 0
    assert res.original_effect == res.adjusted_effect


def test_trim_and_fill_asymmetric():
    """Verify Trim-and-Fill mirrors and adjusts asymmetric data."""
    asymmetric_studies = [
        Study("Large1", 0.15, 0.04),
        Study("Large2", 0.14, 0.05),
        Study("Large3", 0.16, 0.05),
        Study("Small1", 0.55, 0.25),
        Study("Small2", 0.62, 0.28),
        Study("Small3", 0.50, 0.30),
        Study("Small4", 0.70, 0.32),
    ]
    
    res = PublicationBiasDetector.trim_and_fill(asymmetric_studies, meta_method="random")
    assert res is not None
    assert res.n_filled > 0
    # Because positive studies were trimmed/mirrored, adjusted effect must be smaller than original
    assert res.adjusted_effect < res.original_effect
    assert len(res.filled_studies) == res.n_filled
    assert all(fs.effect_size < res.original_effect for fs in res.filled_studies)


def test_publication_bias_audit_risk_reporting():
    """Verify unified report maps risk levels correctly."""
    # Underpowered/insufficient studies
    short_studies = [Study("A", 0.5, 0.1)]
    report_short = PublicationBiasDetector.run_publication_bias_audit(short_studies)
    assert report_short.risk_level == "LOW"
    assert "insufficient" in report_short.interpretation.lower()
    
    # Highly biased data
    asymmetric_studies = [
        Study("Large1", 0.15, 0.04),
        Study("Large2", 0.14, 0.05),
        Study("Large3", 0.16, 0.05),
        Study("Small1", 0.55, 0.25),
        Study("Small2", 0.62, 0.28),
        Study("Small3", 0.50, 0.30),
        Study("Small4", 0.70, 0.32),
    ]
    report_bias = PublicationBiasDetector.run_publication_bias_audit(asymmetric_studies)
    assert report_bias.risk_level in ["HIGH", "CRITICAL"]
    assert report_bias.eggers_result.bias_detected is True
