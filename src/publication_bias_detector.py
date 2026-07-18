"""
ADAVID v4.0 — Clinical Trial Audit Engine
Licensed under AGPL v3 (see LICENSE). Copyright (c) 2026 ADAVID Contributors.

This module provides advanced statistical methods for publication bias detection:
1. Egger's linear regression test for funnel plot asymmetry.
2. Begg & Mazumdar rank correlation test.
3. Duval & Tweedie trim-and-fill algorithm with meta-analysis models.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Study:
    """A single study/clinical trial in a meta-analysis context."""
    name: str
    effect_size: float
    standard_error: float

    @classmethod
    def from_sample_size(cls, name: str, effect_size: float, sample_size: int) -> Study:
        """Approximates standard error from sample size if not directly reported."""
        n = max(sample_size, 2)
        se = math.sqrt(4.0 / n + (effect_size ** 2) / (2.0 * n))
        return cls(name=name, effect_size=effect_size, standard_error=se)


@dataclass(frozen=True)
class MetaAnalysisResult:
    """Results of a meta-analysis synthesis."""
    method: str  # "fixed" or "random"
    combined_effect: float
    standard_error: float
    p_value: float
    ci_95: Tuple[float, float]
    q_statistic: float
    q_p_value: float
    tau_squared: float


@dataclass(frozen=True)
class EggersResult:
    """Result of Egger's regression test for funnel plot asymmetry."""
    intercept: float
    intercept_se: float
    intercept_t: float
    intercept_p_value: float
    intercept_ci_95: Tuple[float, float]
    slope: float
    n_studies: int
    bias_detected: bool
    significance_level: float
    interpretation: str


@dataclass(frozen=True)
class BeggsResult:
    """Result of Begg & Mazumdar rank correlation test."""
    kendall_tau: float
    p_value: float
    bias_detected: bool
    interpretation: str


@dataclass(frozen=True)
class TrimAndFillResult:
    """Result of Duval & Tweedie's trim-and-fill iteration."""
    n_filled: int
    original_effect: float
    adjusted_effect: float
    original_se: float
    adjusted_se: float
    filled_studies: List[Study]
    bias_detected: bool
    interpretation: str


@dataclass(frozen=True)
class PublicationBiasReport:
    """Unified report containing all publication bias analyses."""
    n_studies: int
    eggers_result: Optional[EggersResult]
    beggs_result: Optional[BeggsResult]
    trim_and_fill_result: Optional[TrimAndFillResult]
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    interpretation: str


# Meta-analysis Engine
def run_meta_analysis(studies: List[Study], method: str = "random") -> MetaAnalysisResult:
    """
    Runs fixed-effect (inverse-variance) or random-effects (DerSimonian-Laird) meta-analysis.
    """
    n = len(studies)
    if n == 0:
        raise ValueError("Must provide at least one study for meta-analysis.")

    effects = np.array([s.effect_size for s in studies], dtype=float)
    variances = np.array([s.standard_error ** 2 for s in studies], dtype=float)

    # 1. Fixed-effect calculation
    weights_fixed = 1.0 / variances
    sum_w = np.sum(weights_fixed)
    combined_effect_fixed = np.sum(weights_fixed * effects) / sum_w
    var_fixed = 1.0 / sum_w

    # Cochran's Q (heterogeneity test)
    q_stat = float(np.sum(weights_fixed * (effects - combined_effect_fixed) ** 2))
    df = n - 1
    q_p_value = float(stats.chi2.sf(q_stat, df)) if df > 0 else 1.0

    # 2. Random-effects (DerSimonian-Laird)
    if df > 0:
        sum_w2 = np.sum(weights_fixed ** 2)
        # Between-study variance tau_squared
        num_tau = q_stat - df
        denom_tau = sum_w - (sum_w2 / sum_w)
        tau_sq = max(0.0, num_tau / denom_tau)
    else:
        tau_sq = 0.0

    if method == "random" and df > 0:
        weights_random = 1.0 / (variances + tau_sq)
        sum_w_r = np.sum(weights_random)
        combined_effect = np.sum(weights_random * effects) / sum_w_r
        var_combined = 1.0 / sum_w_r
    else:
        combined_effect = combined_effect_fixed
        var_combined = var_fixed

    se = math.sqrt(var_combined)
    # Z-test for H0: effect = 0
    z_val = combined_effect / se
    p_value = 2.0 * stats.norm.sf(abs(z_val))

    # 95% Confidence Interval
    ci_low = combined_effect - 1.96 * se
    ci_high = combined_effect + 1.96 * se

    return MetaAnalysisResult(
        method=method,
        combined_effect=round(float(combined_effect), 4),
        standard_error=round(se, 4),
        p_value=round(float(p_value), 4),
        ci_95=(round(float(ci_low), 4), round(float(ci_high), 4)),
        q_statistic=round(q_stat, 4),
        q_p_value=round(q_p_value, 4),
        tau_squared=round(tau_sq, 4)
    )


class PublicationBiasDetector:
    """Comprehensive suite for publication bias detection."""

    @staticmethod
    def eggers_test(studies: List[Study], alpha: float = 0.05) -> Optional[EggersResult]:
        """
        Runs Egger's linear regression test for funnel plot asymmetry.
        Standardized effect (effect / SE) is regressed against precision (1 / SE).
        The intercept represents the asymmetry coefficient. H0: intercept = 0.
        """
        n = len(studies)
        if n < 3:
            return None

        effects = np.array([s.effect_size for s in studies], dtype=float)
        ses = np.array([s.standard_error for s in studies], dtype=float)

        if np.any(ses <= 0):
            raise ValueError("All standard errors must be > 0 for Egger's test.")

        precision = 1.0 / ses
        standardized_effect = effects / ses

        # OLS regression math
        x = precision
        y = standardized_effect
        x_mean = x.mean()
        y_mean = y.mean()

        ss_xx = np.sum((x - x_mean) ** 2)
        if ss_xx == 0:
            return None  # Cannot regress if all standard errors are identical

        ss_xy = np.sum((x - x_mean) * (y - y_mean))
        slope = ss_xy / ss_xx
        intercept = y_mean - slope * x_mean

        # Residual variance
        y_pred = intercept + slope * x
        residuals = y - y_pred
        df = n - 2
        if df <= 0:
            return None
            
        residual_var = np.sum(residuals ** 2) / df

        # Intercept standard error
        intercept_se = math.sqrt(residual_var * (1.0 / n + x_mean ** 2 / ss_xx))
        if intercept_se == 0:
            return None

        t_stat = intercept / intercept_se
        p_value = 2.0 * stats.t.sf(abs(t_stat), df)

        # 95% Confidence Interval for intercept
        t_crit = stats.t.ppf(1.0 - alpha / 2.0, df)
        ci_low = intercept - t_crit * intercept_se
        ci_high = intercept + t_crit * intercept_se

        bias_detected = p_value < alpha

        # Interpretation
        if bias_detected:
            interpretation = (
                f"Egger's test is significant (p={p_value:.4f} < {alpha}): funnel plot "
                f"is asymmetric (intercept={intercept:.3f}). Consistent with publication bias."
            )
        else:
            interpretation = (
                f"Egger's test is not significant (p={p_value:.4f} >= {alpha}): no "
                f"statistical evidence of funnel plot asymmetry."
            )
        if n < 10:
            interpretation += " CAUTION: underpowered due to small study count (n < 10)."

        return EggersResult(
            intercept=round(float(intercept), 4),
            intercept_se=round(float(intercept_se), 4),
            intercept_t=round(float(t_stat), 4),
            intercept_p_value=round(float(p_value), 4),
            intercept_ci_95=(round(float(ci_low), 4), round(float(ci_high), 4)),
            slope=round(float(slope), 4),
            n_studies=n,
            bias_detected=bool(bias_detected),
            significance_level=alpha,
            interpretation=interpretation
        )

    @staticmethod
    def beggs_test(studies: List[Study], alpha: float = 0.05) -> Optional[BeggsResult]:
        """
        Runs Begg & Mazumdar rank correlation test.
        Calculates Kendall's tau between standardized effect size deviations and standard errors.
        """
        n = len(studies)
        if n < 3:
            return None

        effects = np.array([s.effect_size for s in studies], dtype=float)
        ses = np.array([s.standard_error for s in studies], dtype=float)
        variances = ses ** 2

        # 1. Fixed-effect combined estimate
        weights = 1.0 / variances
        theta_F = np.sum(weights * effects) / np.sum(weights)
        v_F = 1.0 / np.sum(weights)

        # 2. Standardized deviations
        denom = np.sqrt(variances - v_F)
        # Avoid division by zero if a study has standard error very close to v_F
        denom = np.where(denom <= 0, 1e-9, denom)
        std_effects = (effects - theta_F) / denom

        # 3. Rank correlation
        tau, p_value = stats.kendalltau(std_effects, variances)
        
        # Handle nan return from kendalltau if data is degenerate
        if np.isnan(tau) or np.isnan(p_value):
            return None

        bias_detected = p_value < alpha

        if bias_detected:
            interpretation = (
                f"Begg's test is significant (p={p_value:.4f} < {alpha}): significant "
                f"rank correlation (tau={tau:.3f}) between effects and variances."
            )
        else:
            interpretation = (
                f"Begg's test is not significant (p={p_value:.4f} >= {alpha}): no "
                f"rank correlation evidence of bias."
            )

        return BeggsResult(
            kendall_tau=round(float(tau), 4),
            p_value=round(float(p_value), 4),
            bias_detected=bool(bias_detected),
            interpretation=interpretation
        )

    @staticmethod
    def trim_and_fill(
        studies: List[Study], 
        alpha: float = 0.05, 
        meta_method: str = "random"
    ) -> Optional[TrimAndFillResult]:
        """
        Implements Duval & Tweedie's iterative Trim-and-Fill algorithm (estimator L0).
        Fills missing studies on the left side (assumes bias favors positive effects).
        """
        n = len(studies)
        if n < 3:
            return None

        # Sort studies by effect size for indexing
        sorted_studies = sorted(studies, key=lambda s: s.effect_size)
        effects = np.array([s.effect_size for s in sorted_studies], dtype=float)
        ses = np.array([s.standard_error for s in sorted_studies], dtype=float)

        # Original meta-analysis
        orig_meta = run_meta_analysis(sorted_studies, method=meta_method)
        theta = orig_meta.combined_effect

        n_filled = 0
        max_iter = 50
        prev_n_filled = -1

        for _ in range(max_iter):
            # Centered effects
            y = effects - theta
            
            # Rank absolute values of y
            abs_y = np.abs(y)
            ranks = stats.rankdata(abs_y, method="average")
            
            # Calculate sum of positive ranks
            pos_mask = y > 0
            t_k = np.sum(ranks[pos_mask]) if np.any(pos_mask) else 0.0
            
            # Estimator L0
            # L0 = (4 * T_k - k * (k + 1)) / (2 * k - 1)
            est_l0 = (4.0 * t_k - n * (n + 1.0)) / (2.0 * n - 1.0)
            n_filled = max(0, int(round(est_l0)))

            if n_filled == prev_n_filled:
                break
            prev_n_filled = n_filled

            # Trim the n_filled studies with largest positive centered values
            if n_filled > 0:
                # Find indices of largest y values
                trim_indices = np.argsort(y)[-n_filled:]
                keep_mask = np.ones(n, dtype=bool)
                keep_mask[trim_indices] = False
                
                # Re-estimate theta with remaining
                trimmed_studies = [sorted_studies[i] for i in range(n) if keep_mask[i]]
                if not trimmed_studies:
                    break
                trimmed_meta = run_meta_analysis(trimmed_studies, method=meta_method)
                theta = trimmed_meta.combined_effect
            else:
                theta = orig_meta.combined_effect
                break

        # Create filled studies (mirroring the trimmed positive studies across theta)
        filled_list: List[Study] = []
        if n_filled > 0:
            # Re-calculate final centered values
            y_final = effects - theta
            # Identify the n_filled largest positive values to mirror
            mirror_indices = np.argsort(y_final)[-n_filled:]
            
            for idx in mirror_indices:
                orig_study = sorted_studies[idx]
                mirrored_effect = 2 * theta - orig_study.effect_size
                filled_list.append(
                    Study(
                        name=f"Filled_{orig_study.name}",
                        effect_size=mirrored_effect,
                        standard_error=orig_study.standard_error
                    )
                )

        # Final meta-analysis on original + filled studies
        combined_dataset = sorted_studies + filled_list
        adjusted_meta = run_meta_analysis(combined_dataset, method=meta_method)

        bias_detected = n_filled > 0
        
        if bias_detected:
            interpretation = (
                f"Duval & Tweedie Trim-and-Fill estimated {n_filled} missing studies. "
                f"Adjusted effect size: {adjusted_meta.combined_effect:.4f} "
                f"(Original: {orig_meta.combined_effect:.4f})."
            )
        else:
            interpretation = "Trim-and-Fill detected no missing studies. Effect size estimate is stable."

        return TrimAndFillResult(
            n_filled=n_filled,
            original_effect=orig_meta.combined_effect,
            adjusted_effect=adjusted_meta.combined_effect,
            original_se=orig_meta.standard_error,
            adjusted_se=adjusted_meta.standard_error,
            filled_studies=filled_list,
            bias_detected=bias_detected,
            interpretation=interpretation
        )

    @classmethod
    def run_publication_bias_audit(
        cls, 
        studies: List[Study], 
        alpha: float = 0.05, 
        meta_method: str = "random"
    ) -> PublicationBiasReport:
        """
        Runs Egger's, Begg's, and Trim-and-Fill analyses on the studies list
        and evaluates overall risk of publication bias.
        """
        n = len(studies)
        eggers = cls.eggers_test(studies, alpha=alpha)
        beggs = cls.beggs_test(studies, alpha=alpha)
        trim_fill = cls.trim_and_fill(studies, alpha=alpha, meta_method=meta_method)

        # Determine risk level
        # Start at LOW. Increment if bias is detected by statistical tests.
        risk_score = 0
        
        if eggers and eggers.bias_detected:
            risk_score += 2
        if beggs and beggs.bias_detected:
            risk_score += 1
        if trim_fill and trim_fill.n_filled > 0:
            risk_score += 1
            if trim_fill.n_filled > 3:
                risk_score += 1

        if n < 3:
            risk_level = "LOW"
            interpretation = "Insufficient studies (<3) to run publication bias tests."
        elif risk_score >= 4:
            risk_level = "CRITICAL"
            interpretation = "Critical publication bias detected across all metrics. Combined effect is highly unsafe."
        elif risk_score >= 2:
            risk_level = "HIGH"
            interpretation = "High risk of publication bias. Multiple indicators/asymmetry tests are statistically significant."
        elif risk_score == 1:
            risk_level = "MEDIUM"
            interpretation = "Moderate risk of publication bias. Weak or single positive test indicator."
        else:
            risk_level = "LOW"
            interpretation = "Low risk of publication bias. Funnel plot is statistically symmetric."

        return PublicationBiasReport(
            n_studies=n,
            eggers_result=eggers,
            beggs_result=beggs,
            trim_and_fill_result=trim_fill,
            risk_level=risk_level,
            interpretation=interpretation
        )
