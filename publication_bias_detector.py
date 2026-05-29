"""
ADAVID v4.0 — Pharmaceutical Audit Engine
Licensed under AGPL v3 — See LICENSE file for details
Copyright (c) 2026 ADAVID Contributors

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version. Distributed WITHOUT ANY WARRANTY.
Full terms: https://www.gnu.org/licenses/agpl-3.0.html
"""

# =============================================================================
# Publication Bias Detection (Improvements #21-23)
# =============================================================================
#
# This module attempts to detect whether clinical studies are being withheld
# from publication, using the asymmetry of the observed studies as evidence.
#
#   #21  Funnel-plot asymmetry      -> signals that negative studies may be missing
#   #22  Trim-and-fill estimate     -> guesses HOW MANY studies are missing
#   #23  Regulatory gating          -> turns that evidence into an economic demand
#
# -----------------------------------------------------------------------------
# IMPORTANT HONESTY NOTE — READ BEFORE TRUSTING ANY OUTPUT
# -----------------------------------------------------------------------------
# Several numbers in this module are SIMPLIFIED HEURISTICS or FIXED ASSUMPTIONS,
# not validated statistical estimates. Throughout the code these are tagged:
#
#   # [COMPUTED]     -> derived from the input data via a defined formula
#   # [HEURISTIC]    -> a rough rule of thumb, NOT a peer-reviewed method
#   # [ASSUMPTION]   -> a fixed value we chose, NOT derived from data
#   # [ILLUSTRATIVE] -> a hand-written example figure, NOT a real calculation
#
# A real regulatory submission would need the [HEURISTIC]/[ASSUMPTION] items
# replaced with validated methods (e.g. a proper Egger's test with a p-value,
# and the genuine Duval & Tweedie iterative trim-and-fill algorithm).
# =============================================================================

import math
from dataclasses import dataclass
from typing import Dict, List


# -----------------------------------------------------------------------------
# Data structures
# -----------------------------------------------------------------------------

@dataclass
class Study:
    """A single clinical trial."""
    name: str
    sample_size: int
    effect_size: float          # Cohen's d, or log odds ratio
    publication_status: str     # "published" | "unpublished" | "assumed_hidden"


@dataclass
class FunnelAnalysis:
    """Result of a funnel-plot publication-bias analysis."""
    studies: List[Study]
    symmetry_score: float           # [HEURISTIC] -1 (left bias) .. +1 (right bias)
    asymmetry_confidence: float     # [HEURISTIC] 0..1 rough confidence, NOT a p-value
    estimated_hidden_studies: int   # [HEURISTIC] rough count of missing studies
    risk_assessment: str            # "NO_BIAS" | "POSSIBLE_BIAS" | "SEVERE_BIAS"
    recommendation: str


# Thresholds used to translate a symmetry score into a risk label.
# [ASSUMPTION] These cutoffs were chosen by hand, not calibrated against data.
_SEVERE_BIAS_CUTOFF = 0.5
_POSSIBLE_BIAS_CUTOFF = 0.2

# Minimum studies required before any bias analysis is meaningful.
_MIN_STUDIES_FUNNEL = 4
_MIN_STUDIES_TRIM_FILL = 3


# =============================================================================
# #21 — Publication Bias Detection via Funnel-Plot Asymmetry
# =============================================================================

class PublicationBiasDetector:
    """
    Detects possibly-hidden studies from funnel-plot asymmetry.

    Idea: in an unbiased literature, study effect sizes form a symmetric
    "funnel" when plotted against precision (a proxy for sample size). Large
    studies cluster near the true effect; small studies scatter symmetrically
    around it. If negative small studies are suppressed, the funnel's left
    side goes missing and the remaining points look asymmetric.

    CAVEAT: the asymmetry measure below is a simplified slope-based heuristic,
    not the full Egger regression test (which would also yield a p-value and a
    confidence interval). See per-line tags.
    """

    def __init__(self) -> None:
        self.studies: List[Study] = []

    def add_study(self, study: Study) -> None:
        self.studies.append(study)

    def analyze_funnel(self) -> FunnelAnalysis:
        """Run the (heuristic) funnel-plot asymmetry analysis."""
        if len(self.studies) < _MIN_STUDIES_FUNNEL:
            return self._insufficient_data_result()

        # [COMPUTED] Precision proxy: sqrt(n). True Egger's uses 1/standard_error,
        # which requires each study's SE — not available from these inputs.
        precisions = [math.sqrt(s.sample_size) for s in self.studies]
        effects = [s.effect_size for s in self.studies]

        slope, intercept = self._linear_regression(precisions, effects)

        symmetry_score = self._symmetry_score(intercept, effects)
        estimated_hidden = self._estimate_hidden_from_small_studies(precisions, effects)
        confidence = self._asymmetry_confidence(intercept, effects)
        risk, recommendation = self._assess_risk(symmetry_score, estimated_hidden)

        return FunnelAnalysis(
            studies=self.studies,
            symmetry_score=round(symmetry_score, 3),
            asymmetry_confidence=round(confidence, 3),
            estimated_hidden_studies=estimated_hidden,
            risk_assessment=risk,
            recommendation=recommendation,
        )

    # -- helpers --------------------------------------------------------------

    def _insufficient_data_result(self) -> FunnelAnalysis:
        return FunnelAnalysis(
            studies=self.studies,
            symmetry_score=0.0,
            asymmetry_confidence=0.0,
            estimated_hidden_studies=0,
            risk_assessment="INSUFFICIENT_DATA",
            recommendation=f"Need at least {_MIN_STUDIES_FUNNEL} studies for bias detection.",
        )

    @staticmethod
    def _linear_regression(xs: List[float], ys: List[float]) -> tuple:
        """
        [COMPUTED] Ordinary least-squares fit of y = intercept + slope * x.

        In Egger's test the intercept being non-zero is the bias signal. Note:
        a real implementation would also return the standard error of the
        intercept and a p-value; this version returns neither.
        """
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n

        covariance = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
        variance_x = sum((xs[i] - mean_x) ** 2 for i in range(n))

        slope = covariance / variance_x if variance_x else 0.0
        intercept = mean_y - slope * mean_x
        return slope, intercept

    @staticmethod
    def _symmetry_score(intercept: float, effects: List[float]) -> float:
        """
        [HEURISTIC] Normalise the regression intercept into a -1..+1 score.

        Positive => small studies skew positive (classic publication bias).
        This normalisation by mean effect is an ad-hoc choice, not a standard
        statistic.
        """
        mean_effect = sum(effects) / len(effects)
        raw = intercept / max(0.1, abs(mean_effect))
        return min(1.0, max(-1.0, raw))

    @staticmethod
    def _estimate_hidden_from_small_studies(precisions: List[float],
                                            effects: List[float]) -> int:
        """
        [HEURISTIC] Count small studies with positive effects and assume an
        equal number of equally-small NEGATIVE studies were suppressed.

        This is a crude stand-in for the real trim-and-fill iteration. It will
        over- or under-count whenever the true effect is genuinely non-zero.
        """
        mean_precision = sum(precisions) / len(precisions)
        small_cutoff = mean_precision / 2  # [ASSUMPTION] "small" = below half the mean precision

        positive_small = sum(
            1 for p, e in zip(precisions, effects) if p < small_cutoff and e > 0
        )
        negative_small = sum(
            1 for p, e in zip(precisions, effects) if p < small_cutoff and e < 0
        )
        return max(0, positive_small - negative_small)

    @staticmethod
    def _asymmetry_confidence(intercept: float, effects: List[float]) -> float:
        """
        [HEURISTIC] A pseudo-confidence in [0, 0.99].

        WARNING: this is NOT a statistical confidence level or (1 - p-value).
        It is a monotonic transform of the intercept magnitude and should not
        be reported to regulators as a confidence figure.
        """
        mean_effect = sum(effects) / len(effects)
        return min(0.99, abs(intercept) / max(0.1, abs(mean_effect)))

    @staticmethod
    def _assess_risk(symmetry_score: float, estimated_hidden: int) -> tuple:
        """[COMPUTED] Map the score onto a risk label and recommendation text."""
        if symmetry_score > _SEVERE_BIAS_CUTOFF:
            return ("SEVERE_BIAS",
                    f"Severe asymmetry: roughly {estimated_hidden} negative studies "
                    f"may be unpublished. Request the full trial registry before approval.")
        if symmetry_score > _POSSIBLE_BIAS_CUTOFF:
            return ("POSSIBLE_BIAS",
                    f"Possible asymmetry: up to {estimated_hidden} studies may be missing. "
                    f"Recommend an independent meta-analysis.")
        return ("NO_BIAS",
                "Funnel plot looks symmetric — no asymmetry-based evidence of missing studies.")

    def plot_funnel_data(self) -> Dict:
        """[COMPUTED] Return plotting-ready points for matplotlib/Plotly."""
        return {
            "title": "Funnel Plot (Publication Bias Detection)",
            "x_axis": "Effect Size (Cohen's d)",
            "y_axis": "Precision (sqrt of sample size)",
            "points": [
                {
                    "name": s.name,
                    "effect": s.effect_size,
                    "precision": math.sqrt(s.sample_size),
                    "sample_size": s.sample_size,
                    "color": "green" if s.effect_size > 0 else "red",
                }
                for s in self.studies
            ],
            "interpretation": (
                "Symmetric funnel = no asymmetry signal. "
                "Missing left side = negative studies may be suppressed."
            ),
        }


# =============================================================================
# #22 — Trim-and-Fill: Estimate the Number / Effect of Hidden Studies
# =============================================================================

# [ASSUMPTION] Assumed mean effect of any suppressed study. The real Duval &
# Tweedie method imputes mirror-image studies rather than using a fixed value.
# Changing this number directly changes the "true effect" output below, so it
# must NOT be presented as a data-derived result.
_ASSUMED_HIDDEN_STUDY_EFFECT = -0.1


class TrimAndFillEstimator:
    """
    A simplified stand-in for the Duval & Tweedie trim-and-fill method.

    The genuine method iteratively trims asymmetric studies, re-estimates the
    centre, and "fills" mirror-image studies until symmetry is reached. The
    version here does a single counting pass and applies a fixed assumed effect
    for the imputed studies — easier to read, but materially less rigorous.
    """

    @staticmethod
    def estimate_missing_studies(published_studies: List[Study]) -> Dict:
        if len(published_studies) < _MIN_STUDIES_TRIM_FILL:
            return {"error": f"Need at least {_MIN_STUDIES_TRIM_FILL} studies."}

        positive = [s for s in published_studies if s.effect_size > 0]
        negative = [s for s in published_studies if s.effect_size <= 0]

        # [COMPUTED] Split into small vs large by mean sample size; small studies
        # are the usual candidates for suppression because they are easier to bury.
        mean_n = sum(s.sample_size for s in published_studies) / len(published_studies)
        small_positive = [s for s in published_studies
                          if s.sample_size < mean_n and s.effect_size > 0]
        small_negative = [s for s in published_studies
                          if s.sample_size < mean_n and s.effect_size <= 0]

        # [HEURISTIC] Assume the positive-small surplus equals the number hidden.
        estimated_hidden_count = max(0, len(small_positive) - len(small_negative))

        published_mean = sum(s.effect_size for s in published_studies) / len(published_studies)  # [COMPUTED]

        # [HEURISTIC + ASSUMPTION] Re-pool after adding the assumed hidden studies.
        all_effects = [s.effect_size for s in published_studies]
        all_effects += [_ASSUMED_HIDDEN_STUDY_EFFECT] * estimated_hidden_count
        adjusted_mean = sum(all_effects) / len(all_effects) if all_effects else 0.0

        return {
            "published_count": len(published_studies),       # [COMPUTED]
            "positive_count": len(positive),                 # [COMPUTED]
            "negative_count": len(negative),                 # [COMPUTED]
            "estimated_hidden_count": estimated_hidden_count,  # [HEURISTIC]
            "published_pooled_effect": round(published_mean, 4),  # [COMPUTED]
            "estimated_true_effect_with_hidden": round(adjusted_mean, 4),  # [HEURISTIC]
            "method_note": (
                "Simplified single-pass estimate using a fixed assumed hidden-study "
                f"effect of {_ASSUMED_HIDDEN_STUDY_EFFECT}. NOT the validated Duval & "
                "Tweedie iterative algorithm. Treat as indicative only."
            ),
            "interpretation": (
                f"If ~{estimated_hidden_count} studies are hidden, the pooled effect "
                f"could fall from {published_mean:.3f} (published) to "
                f"{adjusted_mean:.3f} (adjusted)."
            ),
            "recommendation": (
                "Request the full trial registry. If the company cannot produce the "
                f"~{estimated_hidden_count} apparently-missing studies, the published "
                "set may be selectively reported."
            ),
        }


# =============================================================================
# #23 — Regulatory Gating: Turning the Evidence into an Economic Demand
# =============================================================================

# [ASSUMPTION] Fixed business-model figures used in the demand letter and
# forecast below. None are measured; they are placeholders for illustration.
_ASSUMED_DRUG_MARKET_SHARE = 0.05      # fraction of payer budget a single drug captures
_ASSUMED_COMPLIANCE_COST_USD = 5e6     # one-off cost for a company to disclose data
_DISCLOSURE_DEADLINE_DAYS = 30


class RegulatoryGate:
    """
    Models how a healthcare payer could use an ADAVID audit as a condition of
    reimbursement: "full data, or no market access".

    The economic figures here are ASSUMPTIONS for illustration, not measured
    market data. They should be replaced with real payer-specific numbers
    before any operational use.
    """

    def __init__(self, healthcare_payer: str, annual_budget_usd: float) -> None:
        self.payer = healthcare_payer
        self.budget = annual_budget_usd
        self.drug_approvals: Dict[str, Dict] = {}

    def request_full_disclosure(self, drug_name: str, pharma_company: str) -> Dict:
        """Compose a formal data-disclosure request with the economic stakes attached."""
        revenue_at_stake = self.budget * _ASSUMED_DRUG_MARKET_SHARE  # [ASSUMPTION-based]
        budget_billions = self.budget / 1e9

        letter_body = f"""NOTICE OF DATA DISCLOSURE REQUIREMENT

Dear {pharma_company},

We are evaluating {drug_name} for inclusion in our reimbursement catalogue.
Our annual budget is ${self.budget:,.0f} USD.

Per our ADAVID-certified audit protocol, we require:
  1. Full, unfiltered trial-registry access (clinicaltrials.gov export)
  2. All clinical trial data ever generated (Phase I-IV), including
     terminated, negative, "commercially unfavourable", and harm-related trials
  3. De-identified patient-level data (HIPAA-compliant)
  4. Analysis code and statistical specifications

Without disclosure: status REJECTED, reimbursement $0/yr, market access DENIED.
With full disclosure: ADAVID performs a complete audit (decision in 4-6 weeks),
with a possible status of APPROVED, subset-approval, or conditional approval.

Data due within {_DISCLOSURE_DEADLINE_DAYS} days, or we proceed with rejection.

Sincerely,
ADAVID Regulatory Gate — {self.payer}
"""

        return {
            "to": pharma_company,
            "from": self.payer,
            "re": f"Data Disclosure Requirement for {drug_name}",
            "body": letter_body,
            # NOTE: every figure below is illustrative (see _ASSUMED_* constants).
            "economic_leverage": {
                "payer_annual_budget": self.budget,
                "assumed_drug_market_share": _ASSUMED_DRUG_MARKET_SHARE,   # [ASSUMPTION]
                "estimated_revenue_at_stake": revenue_at_stake,            # [ASSUMPTION-based]
                "assumed_compliance_cost": _ASSUMED_COMPLIANCE_COST_USD,   # [ASSUMPTION]
                "note": "Illustrative figures only — replace with real payer data.",
            },
        }

    def audit_and_certify(self, drug_name: str, analysis_results: Dict) -> Dict:
        """
        [COMPUTED] Decide a certification status from supplied analysis metrics.

        The decision logic itself is deterministic; the QUALITY of the decision
        depends entirely on the quality of `analysis_results` passed in.
        """
        bias_score = analysis_results.get("publication_bias_score", 0.5)  # [ASSUMPTION] default if absent
        bonferroni_violations = analysis_results.get("bonferroni_violations", [])
        power_adequate = analysis_results.get("power_adequate", False)

        if bias_score > 0.7:  # [ASSUMPTION] rejection threshold chosen by hand
            status = "REJECTED"
            reason = "Severe publication bias — insufficient data quality."
        elif bonferroni_violations:
            status = "CONDITIONAL_APPROVAL"
            reason = "Multiple-testing violations — approval limited to registered subgroups."
        elif not power_adequate:
            status = "CONDITIONAL_APPROVAL"
            reason = "Underpowered — requires Phase IV post-market surveillance."
        else:
            status = "APPROVED"
            reason = "Full transparency and statistical standards met."

        coverage = {
            "APPROVED": "Full reimbursement authorised",
            "CONDITIONAL_APPROVAL": "Reimbursement with restrictions",
            "REJECTED": "No reimbursement",
        }[status]

        return {
            "drug": drug_name,
            "certification_status": status,
            "rationale": reason,
            "insurance_coverage": coverage,
            "audit_trail": "Full ADAVID audit report available to the health ministry.",
        }

    def industry_impact_forecast(self) -> Dict:
        """
        [ILLUSTRATIVE] A hypothetical narrative of how the market might respond.

        WARNING: none of the figures or year-by-year outcomes here are modelled
        or evidence-based. They are a hand-written scenario for discussion only
        and must never be cited as a prediction or projection.
        """
        return {
            "disclaimer": "ILLUSTRATIVE SCENARIO — not a model output, not evidence-based.",
            "scenario": "ADAVID adopted by major healthcare payers",
            "timeline": "3-5 years to full implementation (illustrative)",
            "narrative": {
                "year_1": "Some companies refuse and lose market access (illustrative).",
                "year_2": "Mid-size companies begin 