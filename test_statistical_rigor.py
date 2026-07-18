import pytest
import numpy as np
from statistical_rigor import bonferroni_correction, holm_correction, benjamini_hochberg_correction

def test_bonferroni_correction_basic():
    """
    Prüft, ob die Bonferroni-Korrektur die p-Werte korrekt mit m multipliziert
    und bei 1.0 deckelt.
    """
    p_values = [0.01, 0.02, 0.05, 0.5]
    m = len(p_values)
    
    # Erwartete Werte: [0.04, 0.08, 0.20, 1.00]
    expected = [0.04, 0.08, 0.20, 1.0]
    
    adjusted = bonferroni_correction(p_values)
    np.testing.assert_allclose(adjusted, expected, rtol=1e-5)

def test_holm_correction_ordering():
    """
    Prüft, ob die Holm-Korrektur (sequenzielle Bonferroni-Methode) 
    die schrittweise Multiplikation (m - i + 1) korrekt auf sortierte p-Werte anwendet.
    """
    # Drei Hypothesen
    p_values = [0.01, 0.04, 0.05]
    
    # Rechnung Holm:
    # p1_adj = 0.01 * 3 = 0.03
    # p2_adj = max(0.03, 0.04 * 2) = 0.08
    # p3_adj = max(0.08, 0.05 * 1) = 0.08
    expected = [0.03, 0.08, 0.08]
    
    adjusted = holm_correction(p_values)
    np.testing.assert_allclose(adjusted, expected, rtol=1e-5)

def test_benjamini_hochberg_fdr():
    """
    Prüft die Benjamini-Hochberg False Discovery Rate (FDR) Kontrolle.
    Formel: p_adj = p * m / i (wobei i der 1-basierte Rang nach Sortierung ist).
    Unter Einhaltung der Monotonie (von hinten nach vorne glätten).
    """
    p_values = [0.01, 0.04, 0.05]
    
    # Rechnung BH:
    # Sortiert: i=1: 0.01, i=2: 0.04, i=3: 0.05
    # p3_adj = 0.05 * 3 / 3 = 0.05
    # p2_adj = min(0.05, 0.04 * 3 / 2) = min(0.05, 0.06) = 0.05
    # p1_adj = min(0.05, 0.01 * 3 / 1) = min(0.05, 0.03) = 0.03
    expected = [0.03, 0.05, 0.05]
    
    adjusted = benjamini_hochberg_correction(p_values)
    np.testing.assert_allclose(adjusted, expected, rtol=1e-5)

def test_empty_and_edge_cases():
    """Stellt sicher, dass leere Listen oder p-Werte außerhalb von [0,1] abgefangen werden."""
    with pytest.raises(ValueError):
        bonferroni_correction([])
        
    with pytest.raises(ValueError):
        # p-Wert > 1 darf nicht unkorrigiert durchgehen
        bonferroni_correction([0.05, 1.2])


def test_power_analysis_validation():
    """Verify input validation rules for power analysis parameters."""
    from statistical_rigor import PowerAnalysis
    
    with pytest.raises(ValueError):
        PowerAnalysis.two_sample_t_test(effect_size=-0.5, n_per_group=10)
        
    with pytest.raises(ValueError):
        PowerAnalysis.two_sample_t_test(effect_size=0.5, n_per_group=-5)
        
    with pytest.raises(ValueError):
        PowerAnalysis.two_sample_t_test(effect_size=0.5, n_per_group=10, alpha=1.5)


def test_power_analysis_exact_vs_approx():
    """Verify exact power calculation and compare it to normal approximation."""
    from statistical_rigor import PowerAnalysis
    
    # 1. Small sample size: normal approximation should overestimate power, triggering a warning
    res_small = PowerAnalysis.two_sample_t_test(effect_size=0.8, n_per_group=10)
    assert res_small.exact_power is not None
    assert res_small.exact_power > 0
    assert res_small.exact_power < 1
    assert res_small.approximation_error is not None
    # For n=10, Cohen's d=0.8, the normal approximation overestimates power
    assert res_small.approximation_error >= 0.0
    
    # 2. Larger sample size: approximation error should be small
    res_large = PowerAnalysis.two_sample_t_test(effect_size=0.5, n_per_group=80)
    assert res_large.exact_power is not None
    assert abs(res_large.approximation_error) < 0.02
    assert "Warning" not in res_large.interpretation

