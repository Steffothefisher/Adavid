"""
ADAVID — Real Egger's Regression Test for Publication Bias
Licensed under AGPL v3 — Copyright (c) 2026 ADAVID Contributors

This is the GENUINE Egger's linear regression test, not a heuristic.
It computes an intercept, its standard error, a t-statistic, and a p-value
using scipy. Every reported value is [COMPUTED] from the input data.

Reference:
  Egger M, Davey Smith G, Schneider M, Minder C (1997).
  "Bias in meta-analysis detected by a simple, graphical test."
  BMJ 315(7109):629-634.

Method:
  Egger's test regresses the standardized effect (effect / SE) against
  precision (1 / SE). In the absence of bias, the intercept of this
  regression should be ~0. A non-zero intercept (tested via its p-value)
  indicates funnel-plot asymmetry, often interpreted as publication bias.
"""

import math
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from scipy import stats


@dataclass
class Study:
    """A single clinical trial with the data Egger's test actually needs."""
    name: str
    effect_size: float          # observed effect (e.g. log odds ratio, Cohen's d)
    standard_error: float       # SE of the effect estimate (REQUIRED for real Egger's)

    @classmethod
    def from_sample_size(cls, name: str, effect_size: float, sample_size: int) -> "Study":
        """
        [COMPUTED] Approximate SE from sample size when SE is unavailable.

        For a standardized mean difference (Cohen's d), a common approximation
        is SE ≈ sqrt(4/n + d²/(2n)). This is itself an approximation; a real
        meta-analysis should use each study's reported SE or confidence interval.
        """
        n = max(sample_size, 2)
        se = math.sqrt(4.0 / n + (effect_size ** 2) / (2.0 * n))
        return cls(name=name, effect_size=effect_size, standard_error=se)


@dataclass
class EggersResult:
    """Result of Egger's regression test. All fields are [COMPUTED]."""
    intercept: float                 # the bias coefficient (should be ~0 if unbiased)
    intercept_se: float              # standard error of the intercept
    intercept_t: float               # t-statistic for intercept = 0
    intercept_p_value: float         # p-value (the actual bias test)
    intercept_ci_95: tuple           # 95% confidence interval for the intercept
    slope: float                     # regression slope (the estimated true effect)
    n_studies: int
    bias_detected: bool              # True if p < significance level
    significance_level: float
    interpretation: str


# Minimum studies below which Egger's test is unreliable (per literature).
_MIN_STUDIES_EGGERS = 3
# Egger's is known to be underpowered with few studies; the original paper and
# later guidance recommend caution below ~10 studies.
_RECOMMENDED_MIN_STUDIES = 10


class EggersTest:
    """
    Genuine Egger's regression test for funnel-plot asymmetry.

    Unlike the earlier heuristic, this returns a real p-value computed from a
    t-distribution, so the bias claim is statistically defined and falsifiable.
    """

    @staticmethod
    def run(studies: List[Study], significance_level: float = 0.05) -> Optional[EggersResult]:
        """
        [COMPUTED] Run Egger's regression.

        Egger's test (precision-weighted form):
          - Independent variable: precision = 1 / SE
          - Dependent variable:   standardized effect = effect / SE
          - Fit:                  standardized_effect = intercept + slope * precision
          - The INTERCEPT is the bias measure; H0: intercept = 0.

        Returns None if there are too few studies to run the test at all.
        """
        n = len(studies)
        if n < _MIN_STUDIES_EGGERS:
            return None

        # [COMPUTED] Build Egger's regression variables
        effects = np.array([s.effect_size for s in studies], dtype=float)
        ses = np.array([s.standard_error for s in studies], dtype=float)

        if np.any(ses <= 0):
            raise ValueError("All standard errors must be > 0 for Egger's test.")

        precision = 1.0 / ses                 # [COMPUTED] x-axis
        standardized_effect = effects / ses   # [COMPUTED] y-axis

        # [COMPUTED] OLS regression with full statistics via scipy.
        # scipy's linregress gives slope, intercept, and the SE of the slope,
        # but we need the SE of the INTERCEPT, so we compute the fit directly.
        x = precision
        y = standardized_effect
        x_mean = x.mean()
        y_mean = y.mean()

        ss_xx = np.sum((x - x_mean) ** 2)
        ss_xy = np.sum((x - x_mean) * (y - y_mean))

        slope = ss_xy / ss_xx                       # [COMPUTED] estimated true effect
        intercept = y_mean - slope * x_mean         # [COMPUTED] bias coefficient

        # [COMPUTED] Residual standard error of the regression
        y_pred = intercept + slope * x
        residuals = y - y_pred
        df = n - 2                                  # two parameters estimated
        if df <= 0:
            return None
        residual_var = np.sum(residuals ** 2) / df

        # [COMPUTED] Standard error of the intercept (standard OLS formula)
        intercept_se = math.sqrt(residual_var * (1.0 / n + x_mean ** 2 / ss_xx))

        # [COMPUTED] t-statistic and two-sided p-value for H0: intercept = 0
        if intercept_se == 0:
            return None
        t_stat = intercept / intercept_se
        p_value = 2.0 * stats.t.sf(abs(t_stat), df)   # [COMPUTED] via t-distribution

        # [COMPUTED] 95% confidence interval for the intercept
        t_crit = stats.t.ppf(1.0 - significance_level / 2.0, df)
        ci_low = intercept - t_crit * intercept_se
        ci_high = intercept + t_crit * intercept_se

        bias_detected = p_value < significance_level

        interpretation = EggersTest._interpret(
            bias_detected, p_value, intercept, n, significance_level
        )

        return EggersResult(
            intercept=round(float(intercept), 4),
            intercept_se=round(float(intercept_se), 4),
            intercept_t=round(float(t_stat), 4),
            intercept_p_value=round(float(p_value), 4),
            intercept_ci_95=(round(float(ci_low), 4), round(float(ci_high), 4)),
            slope=round(float(slope), 4),
            n_studies=n,
            bias_detected=bool(bias_detected),
            significance_level=significance_level,
            interpretation=interpretation,
        )

    @staticmethod
    def _interpret(bias_detected: bool, p_value: float, intercept: float,
                   n: int, alpha: float) -> str:
        """[COMPUTED] Plain-language reading of the result, with honest caveats."""
        parts = []
        if bias_detected:
            parts.append(
                f"Egger's test is significant (p={p_value:.4f} < {alpha}): the funnel "
                f"plot is asymmetric (intercept={intercept:.3f}). This is consistent "
                f"with publication bias, but asymmetry can also arise from genuine "
                f"heterogeneity, small-study effects, or chance."
            )
        else:
            parts.append(
                f"Egger's test is not significant (p={p_value:.4f} >= {alpha}): no "
                f"statistical evidence of funnel-plot asymmetry. Note this does NOT "
                f"prove the absence of bias — the test is underpowered with few studies."
            )
        if n < _RECOMMENDED_MIN_STUDIES:
            parts.append(
                f"CAUTION: only {n} studies. Egger's test is unreliable below ~"
                f"{_RECOMMENDED_MIN_STUDIES}; treat this result as weak evidence either way."
            )
        return " ".join(parts)


# =============================================================================
# Self-validation against a known textbook case
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("VALIDATION 1: Symmetric data (no bias) — expect p NOT significant")
    print("=" * 70)
    # Studies scattered symmetrically around a true effect of ~0.30.
    symmetric = [
        Study("A", 0.30, 0.05),
        Study("B", 0.28, 0.10),
        Study("C", 0.32, 0.10),
        Study("D", 0.20, 0.20),
        Study("E", 0.40, 0.20),
        Study("F", 0.10, 0.30),
        Study("G", 0.50, 0.30),
    ]
    r = EggersTest.run(symmetric)
    print(f"intercept = {r.intercept} (SE {r.intercept_se}), t = {r.intercept_t}")
    print(f"p-value   = {r.intercept_p_value}")
    print(f"slope (≈ true effect) = {r.slope}")
    print(f"bias_detected = {r.bias_detected}")
    print(f"-> {r.interpretation}")

    print()
    print("=" * 70)
    print("VALIDATION 2: Asymmetric data (small studies inflated) — expect significant")
    print("=" * 70)
    # Large precise studies near 0.15; small imprecise studies inflated to 0.5-0.7.
    asymmetric = [
        Study("Large1", 0.15, 0.04),
        Study("Large2", 0.14, 0.05),
        Study("Large3", 0.16, 0.05),
        Study("Small1", 0.55, 0.25),
        Study("Small2", 0.62, 0.28),
        Study("Small3", 0.50, 0.30),
        Study("Small4", 0.70, 0.32),
    ]
    r2 = EggersTest.run(asymmetric)
    print(f"intercept = {r2.intercept} (SE {r2.intercept_se}), t = {r2.intercept_t}")
    print(f"p-value   = {r2.intercept_p_value}")
    print(f"slope (≈ true effect) = {r2.slope}")
    print(f"bias_detected = {r2.bias_detected}")
    print(f"-> {r2.interpretation}")

    print()
    print("=" * 70)
    print("VALIDATION 3: Too few studies — expect None")
    print("=" * 70)
    print("Result:", EggersTest.run([Study("X", 0.3, 0.1), Study("Y", 0.2, 0.1)]))
