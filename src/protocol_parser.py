"""
ADAVID v4.0 — Clinical Trial Audit Engine
Licensed under AGPL v3 (see LICENSE). Copyright (c) 2026 ADAVID Contributors.

This module provides data structures and parsing utilities to represent and ingest
study protocols (Soll-Protokolle) and final publications (Ist-Ergebnisse).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class OutcomeDefinition:
    """Represents a single outcome measure (primary or secondary)."""
    measure: str
    time_frame: str
    description: str = ""

    def clean_measure(self) -> str:
        """Helper to lowercase and strip special characters for robust comparison."""
        return re.sub(r"[^\w\s]", "", self.measure.lower()).strip()


@dataclass
class ProtocolSpecification:
    """Specification of the trial protocol as registered (Soll-Zustand)."""
    nct_id: str
    official_title: str
    target_enrollment: Optional[int] = None
    primary_outcomes: List[OutcomeDefinition] = field(default_factory=list)
    secondary_outcomes: List[OutcomeDefinition] = field(default_factory=list)
    min_age_years: Optional[float] = None
    max_age_years: Optional[float] = None
    allowed_sex: str = "ALL"  # "MALE", "FEMALE", "ALL"
    safety_endpoints: List[str] = field(default_factory=list)


@dataclass
class PublicationSpecification:
    """Specification of the reported results or publication details (Ist-Zustand)."""
    nct_id: str
    official_title: str
    actual_enrollment: Optional[int] = None
    primary_outcomes: List[OutcomeDefinition] = field(default_factory=list)
    secondary_outcomes: List[OutcomeDefinition] = field(default_factory=list)
    mean_age: Optional[float] = None
    sex_distribution: Dict[str, float] = field(default_factory=dict)  # e.g., {"MALE": 0.4, "FEMALE": 0.6}
    reported_adverse_events: List[Dict[str, Any]] = field(default_factory=list)
    all_reported_endpoints: List[str] = field(default_factory=list)


class ProtocolParser:
    """Parser to ingest study protocols and publications into unified formats."""

    @staticmethod
    def parse_age_to_years(age_str: Optional[str]) -> Optional[float]:
        """
        Converts age string like '18 Years', '6 Months', '2 Weeks' to years float.
        Returns None if parsing fails or input is None/empty.
        """
        if not age_str:
            return None
        
        age_str = age_str.strip().lower()
        match = re.search(r"(\d+(?:\.\d+)?)\s*(\w+)", age_str)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2)
        
        if "year" in unit:
            return value
        elif "month" in unit:
            return value / 12.0
        elif "week" in unit:
            return value / 52.14
        elif "day" in unit:
            return value / 365.25
        
        return value  # Default assumption is years if unit is unrecognized but numerical

    @classmethod
    def from_clinicaltrials_v2_json(cls, data: Dict[str, Any]) -> ProtocolSpecification:
        """
        Parses a ClinicalTrials.gov API v2 JSON representation of a study.
        Looks inside protocolSection for registry data.
        """
        protocol_section = data.get("protocolSection", {})
        
        # Identification
        ident = protocol_section.get("identificationModule", {})
        nct_id = ident.get("nctId", "UNKNOWN")
        official_title = ident.get("officialTitle", ident.get("briefTitle", "Unnamed Study"))
        
        # Design (Enrollment)
        design = protocol_section.get("designModule", {})
        enroll_info = design.get("enrollmentInfo", {})
        target_enrollment = None
        if "count" in enroll_info:
            try:
                target_enrollment = int(enroll_info["count"])
            except (ValueError, TypeError):
                pass
        
        # Outcomes
        outcomes_mod = protocol_section.get("outcomesModule", {})
        primary_outcomes: List[OutcomeDefinition] = []
        secondary_outcomes: List[OutcomeDefinition] = []
        
        for po in outcomes_mod.get("primaryOutcomes", []):
            measure = po.get("measure", "")
            if measure:
                primary_outcomes.append(
                    OutcomeDefinition(
                        measure=measure,
                        time_frame=po.get("timeFrame", ""),
                        description=po.get("description", "")
                    )
                )
                
        for so in outcomes_mod.get("secondaryOutcomes", []):
            measure = so.get("measure", "")
            if measure:
                secondary_outcomes.append(
                    OutcomeDefinition(
                        measure=measure,
                        time_frame=so.get("timeFrame", ""),
                        description=so.get("description", "")
                    )
                )
        
        # Eligibility (Age, Sex)
        elig = protocol_section.get("eligibilityModule", {})
        min_age_str = elig.get("minimumAge")
        max_age_str = elig.get("maximumAge")
        
        min_age_years = cls.parse_age_to_years(min_age_str)
        max_age_years = cls.parse_age_to_years(max_age_str)
        
        allowed_sex = elig.get("sex", "ALL").upper()
        if allowed_sex not in ["MALE", "FEMALE", "ALL"]:
            allowed_sex = "ALL"
            
        # Extract safety/toxicological endpoints from text/descriptions
        safety_endpoints: List[str] = []
        
        # Search study description for safety items
        desc_mod = protocol_section.get("descriptionModule", {})
        full_text = (
            desc_mod.get("briefSummary", "") + " " + desc_mod.get("detailedDescription", "")
        ).lower()
        
        # Common safety/adverse endpoints
        safety_keywords = [
            "adverse event", "toxicity", "death", "mortality", "safety", "tolerability",
            "side effect", "serious adverse event"
        ]
        for keyword in safety_keywords:
            if keyword in full_text:
                safety_endpoints.append(keyword)
                
        # Also check outcomes for safety markers
        for outcome in primary_outcomes + secondary_outcomes:
            out_lower = outcome.measure.lower() + " " + outcome.description.lower()
            for keyword in safety_keywords:
                if keyword in out_lower and keyword not in safety_endpoints:
                    safety_endpoints.append(keyword)

        return ProtocolSpecification(
            nct_id=nct_id,
            official_title=official_title,
            target_enrollment=target_enrollment,
            primary_outcomes=primary_outcomes,
            secondary_outcomes=secondary_outcomes,
            min_age_years=min_age_years,
            max_age_years=max_age_years,
            allowed_sex=allowed_sex,
            safety_endpoints=safety_endpoints
        )
