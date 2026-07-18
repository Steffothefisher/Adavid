"""
ADAVID v4.0 — Clinical Trial Audit Engine
Licensed under AGPL v3 (see LICENSE). Copyright (c) 2026 ADAVID Contributors.

This module provides the discrepancy analysis engine that compares
a registered trial protocol (Soll) with its published results (Ist)
to detect endpoint modifications, demographic shifts, and safety omissions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from src.protocol_parser import OutcomeDefinition, ProtocolSpecification, PublicationSpecification


def _clean_tokens(text: str) -> Set[str]:
    """Tokenizes and cleans a text string, removing common stopwords."""
    stopwords = {
        "in", "of", "the", "a", "an", "at", "by", "for", "with", "from", "to", "on", "and", "or", "as", "is", "after"
    }
    # Remove punctuation and split into lowercase words
    words = re.findall(r"\w+", text.lower())
    return {w for w in words if w not in stopwords}


def calculate_jaccard_similarity(str1: str, str2: str) -> float:
    """Calculates Jaccard similarity of two strings based on their cleaned token sets."""
    set1 = _clean_tokens(str1)
    set2 = _clean_tokens(str2)
    
    if not set1 or not set2:
        return 0.0
        
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)


class DiscrepancyAnalyzer:
    """Engine to perform discrepancy audits on study protocols versus publication results."""

    def __init__(self, protocol: ProtocolSpecification, publication: PublicationSpecification):
        self.protocol = protocol
        self.publication = publication

    def _find_best_match(
        self, 
        outcome: OutcomeDefinition, 
        candidates: List[OutcomeDefinition], 
        threshold: float = 0.5
    ) -> Tuple[Optional[OutcomeDefinition], float]:
        """
        Finds the best matching outcome definition from a list of candidates.
        Returns the best candidate and its similarity score.
        """
        best_candidate = None
        best_score = 0.0
        
        clean_outcome = outcome.clean_measure()
        
        for candidate in candidates:
            clean_cand = candidate.clean_measure()
            
            # Exact clean match
            if clean_outcome == clean_cand:
                return candidate, 1.0
                
            # Substring match
            if clean_outcome in clean_cand or clean_cand in clean_outcome:
                score = 0.8
            else:
                score = calculate_jaccard_similarity(outcome.measure, candidate.measure)
                
            if score > best_score:
                best_score = score
                best_candidate = candidate
                
        if best_score >= threshold:
            return best_candidate, best_score
            
        return None, 0.0

    def check_endpoint_discrepancies(self) -> Dict[str, Any]:
        """
        Compares protocol planned endpoints with publication reported endpoints.
        Detects:
        - Mismatched (missing) primary endpoints.
        - Endpoint swapping (promotion/demotion).
        - Timeframe shifts.
        """
        mismatched_primaries: List[Dict[str, Any]] = []
        demoted_endpoints: List[Dict[str, Any]] = []
        promoted_endpoints: List[Dict[str, Any]] = []
        timeframe_shifts: List[Dict[str, Any]] = []
        
        # 1. Check planned primary endpoints
        for planned_primary in self.protocol.primary_outcomes:
            # Check in publication primary outcomes
            match_pub_primary, score_prim = self._find_best_match(
                planned_primary, self.publication.primary_outcomes
            )
            
            if match_pub_primary:
                # Found primary -> primary. Check timeframe shift
                if planned_primary.time_frame.strip().lower() != match_pub_primary.time_frame.strip().lower():
                    timeframe_shifts.append({
                        "endpoint": planned_primary.measure,
                        "planned_timeframe": planned_primary.time_frame,
                        "reported_timeframe": match_pub_primary.time_frame,
                        "context": "Primary endpoint timeframe changed."
                    })
                continue
                
            # Check in publication secondary outcomes (Demotion)
            match_pub_secondary, score_sec = self._find_best_match(
                planned_primary, self.publication.secondary_outcomes
            )
            
            if match_pub_secondary:
                demoted_endpoints.append({
                    "endpoint": planned_primary.measure,
                    "planned_role": "Primary",
                    "reported_role": "Secondary",
                    "similarity": round(score_sec, 3)
                })
            else:
                # Completely missing from reported endpoints
                mismatched_primaries.append({
                    "endpoint": planned_primary.measure,
                    "planned_timeframe": planned_primary.time_frame,
                    "reason": "Endpoint planned as primary in protocol but not found in publication outcomes."
                })
                
        # 2. Check for Endpoint Swapping / Promotion
        # (Secondary endpoints in protocol promoted to primary in publication)
        for planned_secondary in self.protocol.secondary_outcomes:
            match_pub_primary, score_prim = self._find_best_match(
                planned_secondary, self.publication.primary_outcomes
            )
            
            if match_pub_primary:
                # Swapping detected
                promoted_endpoints.append({
                    "endpoint": planned_secondary.measure,
                    "planned_role": "Secondary",
                    "reported_role": "Primary",
                    "similarity": round(score_prim, 3)
                })
                
        return {
            "mismatched_primary_endpoints": mismatched_primaries,
            "demoted_endpoints": demoted_endpoints,
            "promoted_endpoints": promoted_endpoints,
            "timeframe_shifts": timeframe_shifts
        }

    def check_cohort_discrepancies(self) -> Dict[str, Any]:
        """
        Detects deviations in enrollment and demographic specifications.
        """
        alerts: List[str] = []
        deviation_pct = None
        
        # Enrollment deviation
        if self.protocol.target_enrollment and self.publication.actual_enrollment:
            target = self.protocol.target_enrollment
            actual = self.publication.actual_enrollment
            deviation_pct = (actual - target) / target
            
            if deviation_pct < -0.20:
                alerts.append(
                    f"Significant under-enrollment: Actual cohort (N={actual}) is "
                    f"{abs(deviation_pct):.1%} smaller than planned target (N={target})."
                )
            elif deviation_pct > 0.50:
                alerts.append(
                    f"Large enrollment overflow: Actual cohort (N={actual}) is "
                    f"{deviation_pct:.1%} larger than planned target (N={target})."
                )
                
        # Age restriction violation
        if self.publication.mean_age is not None:
            mean_age = self.publication.mean_age
            min_age = self.protocol.min_age_years
            max_age = self.protocol.max_age_years
            
            if min_age is not None and mean_age < min_age:
                alerts.append(
                    f"Demographic mismatch: Reported cohort mean age ({mean_age} years) "
                    f"violates protocol eligibility minimum age ({min_age} years)."
                )
            if max_age is not None and mean_age > max_age:
                alerts.append(
                    f"Demographic mismatch: Reported cohort mean age ({mean_age} years) "
                    f"violates protocol eligibility maximum age ({max_age} years)."
                )
                
        # Sex criteria violation
        if self.protocol.allowed_sex in ["MALE", "FEMALE"] and self.publication.sex_distribution:
            allowed = self.protocol.allowed_sex
            # Check if there is representation of the disallowed sex
            disallowed = "FEMALE" if allowed == "MALE" else "MALE"
            disallowed_ratio = self.publication.sex_distribution.get(disallowed, 0.0)
            
            if disallowed_ratio > 0.02:  # >2% tolerance
                alerts.append(
                    f"Demographic eligibility violation: Protocol restricts cohort to '{allowed}', "
                    f"but publication includes {disallowed_ratio:.1%} '{disallowed}' patients."
                )
                
        return {
            "deviation_pct": deviation_pct,
            "alerts": alerts
        }

    def check_safety_omissions(self) -> List[str]:
        """
        Checks if safety/toxicity endpoints planned in the protocol
        are omitted in the publication results.
        """
        omitted_safety: List[str] = []
        
        # Collect all reported endpoints as clean sets
        reported_clean = {re.sub(r"[^\w\s]", "", ep.lower()).strip() for ep in self.publication.all_reported_endpoints}
        
        # Also clean reported primary and secondary outcomes
        for po in self.publication.primary_outcomes:
            reported_clean.add(po.clean_measure())
        for so in self.publication.secondary_outcomes:
            reported_clean.add(so.clean_measure())
            
        # Clean adverse event terms reported
        for ae in self.publication.reported_adverse_events:
            term = ae.get("term", ae.get("event", ""))
            if term:
                reported_clean.add(re.sub(r"[^\w\s]", "", term.lower()).strip())
                
        # Scan planned safety endpoints
        for safety_planned in self.protocol.safety_endpoints:
            cleaned_safety = re.sub(r"[^\w\s]", "", safety_planned.lower()).strip()
            
            # Look for matches (exact or clean substring)
            match_found = False
            for rep in reported_clean:
                if cleaned_safety in rep or rep in cleaned_safety:
                    match_found = True
                    break
                    
            if not match_found:
                omitted_safety.append(
                    f"Planned safety/toxicological endpoint '{safety_planned}' "
                    f"was not reported in outcomes or adverse events."
                )
                
        return omitted_safety

    def run_audit(self) -> Dict[str, Any]:
        """
        Runs the full discrepancy audit and calculates a final integrity score.
        Score ranges from 0 (critical discrepancies) to 100 (fully consistent).
        """
        endpoints = self.check_endpoint_discrepancies()
        cohort = self.check_cohort_discrepancies()
        safety = self.check_safety_omissions()
        
        # Deduct score starting from 100
        score = 100.0
        
        # Deduct for missing primaries (30 pts each)
        score -= len(endpoints["mismatched_primary_endpoints"]) * 30.0
        
        # Deduct for demoted/promoted outcomes (20 pts each)
        score -= len(endpoints["demoted_endpoints"]) * 20.0
        score -= len(endpoints["promoted_endpoints"]) * 20.0
        
        # Deduct for timeframe shifts (15 pts each)
        score -= len(endpoints["timeframe_shifts"]) * 15.0
        
        # Deduct for cohort alerts (15 pts each)
        score -= len(cohort["alerts"]) * 15.0
        
        # Deduct for safety omissions (25 pts each)
        score -= len(safety) * 25.0
        
        score = max(0.0, min(100.0, score))
        
        # Determine risk level
        if score >= 90.0:
            risk_level = "LOW"
        elif score >= 70.0:
            risk_level = "MEDIUM"
        elif score >= 50.0:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
            
        return {
            "nct_id": self.protocol.nct_id,
            "official_title": self.protocol.official_title,
            "endpoints": endpoints,
            "cohort": cohort,
            "safety_omissions": safety,
            "integrity_score": score,
            "risk_level": risk_level
        }
