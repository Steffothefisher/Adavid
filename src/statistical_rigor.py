"""
ADAVID v4.0 — Pharmaceutical Audit Engine
Licensed under AGPL v3 (see LICENSE). Copyright (c) 2026 ADAVID Contributors.

This module provides robust multiple-comparison correction utilities and
basic statistical helpers for clinical-trial audit workflows.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence


def _validate_p_values(p_values: Sequence[float]) -> List[float]:
    """Validate and normalize a sequence of p-values."""
    if p_values is None:
        raise ValueError("p_values must not be None")

    values = list(p_values)
    if not values:
        raise ValueError("p_values must not be empty")

    for idx, value in enumerate(values):
        if not isinstance(value, (int, float)):
            raise TypeError(f"p_values[{idx}] must be numeric")
        if not 0 <= float(value) <= 1:
            raise ValueError(f"p_values[{idx}] must be in [0, 1], got {value}")

    return [float(value) for value in values]


def bonferroni_correction(p_values: Sequence[float]) -> List[float]:
    """Apply Bonferroni correction by multiplying each p-value by m."""
    values = _validate_p_values(p_values)
    m = len(values)
    return [min(1.0, value * m) for value in values]


def holm_correction(p_values: Sequence[float]) -> List[float]:
    """Apply Holm-Bonferroni step-down correction."""
    values = _validate_p_values(p_values)
    m = len(values)

    order = sorted(range(m), key=lambda idx: values[idx])
    adjusted_sorted: List[float] = []
    running_max = 0.0

    for rank, idx in enumerate(order, start=1):
        adjusted_value = values[idx] * (m - rank + 1)
        running_max = max(running_max, adjusted_value)
        adjusted_sorted.append(min(1.0, running_max))

    adjusted = [0.0] * m
    for rank, idx in enumerate(order):
        adjusted[idx] = adjusted_sorted[rank]

    return adjusted


def benjamini_hochberg_correction(p_values: Sequence[float]) -> List[float]:
    """Apply Benjamini-Hochberg FDR correction."""
    values = _validate_p_values(p_values)
    m = len(values)

    order = sorted(range(m), key=lambda idx: values[idx])
    adjusted_sorted = [min(1.0, values[idx] * m / rank) for rank, idx in enumerate(order, start=1)]

    for idx in range(m - 2, -1, -1):
        adjusted_sorted[idx] = min(adjusted_sorted[idx], adjusted_sorted[idx + 1])

    adjusted = [0.0] * m
    for rank, idx in enumerate(order):
        adjusted[idx] = adjusted_sorted[rank]

    return adjusted


class MultipleComparisonCorrector:
    """Convenience wrapper around the multiple-testing correction functions."""

    @staticmethod
    def bonferroni(p_values: Sequence[float]) -> List[float]:
        return bonferroni_correction(p_values)

    @staticmethod
    def holm(p_values: Sequence[float]) -> List[float]:
        return holm_correction(p_values)

    @staticmethod
    def benjamini_hochberg(p_values: Sequence[float]) -> List[float]:
        return benjamini_hochberg_correction(p_values)


@dataclass(frozen=True)
class PowerAnalysisResult:
    achieved_power: float
    sample_size_required: int
    effect_size: float
    alpha: float
    interpretation: str
    exact_power: Optional[float] = None
    approximation_error: Optional[float] = None


class PowerAnalysis:
    """Lightweight power estimation for two-sample comparisons."""

    @staticmethod
    def two_sample_t_test(effect_size: float, n_per_group: int, alpha: float = 0.05) -> PowerAnalysisResult:
        if effect_size <= 0:
            raise ValueError("effect_size must be positive")
        if n_per_group <= 0:
            raise ValueError("n_per_group must be positive")
        if not 0 < alpha < 1:
            raise ValueError("alpha must be in (0, 1)")

        # Normal approximation
        z_alpha = 1.96 if alpha == 0.05 else _inv_normal(1 - alpha / 2)
        ncp = effect_size * (n_per_group / 2) ** 0.5
        approx_power = 1 - _normal_cdf(z_alpha - ncp)

        exact_power = None
        approx_error = None
        power = approx_power

        # Attempt exact calculation using scipy
        try:
            from scipy import stats
            df = 2 * n_per_group - 2
            delta = effect_size * math.sqrt(n_per_group / 2)
            t_crit = stats.t.ppf(1 - alpha / 2, df)
            exact_val = 1.0 - stats.nct.cdf(t_crit, df, delta) + stats.nct.cdf(-t_crit, df, delta)
            exact_power = round(float(exact_val), 4)
            approx_error = round(float(approx_power - exact_val), 4)
            power = exact_val
        except ImportError:
            pass

        z_beta = 0.8416
        n_required = math.ceil(2 * ((z_alpha + z_beta) / effect_size) ** 2) if effect_size > 0 else 0
        
        if power >= 0.8:
            interpretation = "Adequately powered (≥80%)"
        elif power >= 0.5:
            interpretation = f"Underpowered ({power:.0%}) — borderline, results uncertain"
        else:
            interpretation = f"Severely underpowered ({power:.0%}) — trial likely cannot detect effect of this size"

        if approx_error is not None and approx_error >= 0.05:
            interpretation += f" (Warning: normal approximation overestimates power by {approx_error:.1%})"

        return PowerAnalysisResult(
            achieved_power=round(power, 4),
            sample_size_required=n_required,
            effect_size=effect_size,
            alpha=alpha,
            interpretation=interpretation,
            exact_power=exact_power,
            approximation_error=approx_error
        )


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _inv_normal(p: float) -> float:
    if not 0 < p < 1:
        raise ValueError(f"p must be in (0,1), got {p}")

    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02, 1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02, 6.680131188771972e01, -1.328068155288572e01]

    q = p - 0.5
    if abs(q) <= 0.425:
        r = q * q
        return (q * (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])) / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)

    r = math.sqrt(-math.log(min(p, 1 - p)))
    sign = 1 if p > 0.5 else -1
    return sign * (2.515517 + 0.802853 * r + 0.010328 * r * r) / (1 + 1.432788 * r + 0.189269 * r * r + 0.001308 * r * r * r)


__all__ = [
    'MultipleComparisonCorrector',
    'PowerAnalysis',
    'PowerAnalysisResult',
    'benjamini_hochberg_correction',
    'bonferroni_correction',
    'holm_correction',
]
