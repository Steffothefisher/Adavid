import pytest
from src.protocol_parser import ProtocolParser, ProtocolSpecification, PublicationSpecification, OutcomeDefinition
from src.discrepancy_analyzer import DiscrepancyAnalyzer, calculate_jaccard_similarity


def test_parse_age_to_years():
    """Verify age parsing converts various units to years float correctly."""
    assert ProtocolParser.parse_age_to_years("18 Years") == 18.0
    assert ProtocolParser.parse_age_to_years("6 Months") == 0.5
    assert ProtocolParser.parse_age_to_years("26 Weeks") == pytest.approx(0.5, abs=0.01)  # 26 / 52.14 is approx 0.498
    assert ProtocolParser.parse_age_to_years(None) is None
    assert ProtocolParser.parse_age_to_years("Invalid String") is None
    
    # Approx check for days/weeks
    weeks = ProtocolParser.parse_age_to_years("52 Weeks")
    assert abs(weeks - 1.0) < 0.01


def test_parse_clinicaltrials_v2_json():
    """Verify parser extracts correct specifications from v2 JSON structure."""
    sample_json = {
        "protocolSection": {
            "identificationModule": {
                "nctId": "NCT09876543",
                "officialTitle": "Test Trial of Agent X in Healthy Volunteers"
            },
            "designModule": {
                "enrollmentInfo": {
                    "count": "150"
                }
            },
            "outcomesModule": {
                "primaryOutcomes": [
                    {
                        "measure": "Systolic Blood Pressure (SBP)",
                        "timeFrame": "12 Weeks",
                        "description": "Baseline to Week 12 change."
                    }
                ],
                "secondaryOutcomes": [
                    {
                        "measure": "Diastolic Blood Pressure (DBP)",
                        "timeFrame": "12 Weeks"
                    }
                ]
            },
            "eligibilityModule": {
                "minimumAge": "18 Years",
                "maximumAge": "60 Years",
                "sex": "FEMALE"
            },
            "descriptionModule": {
                "briefSummary": "Evaluates safety, tolerability and efficacy of Agent X.",
                "detailedDescription": "Explores adverse event occurrences."
            }
        }
    }
    
    spec = ProtocolParser.from_clinicaltrials_v2_json(sample_json)
    assert spec.nct_id == "NCT09876543"
    assert spec.official_title == "Test Trial of Agent X in Healthy Volunteers"
    assert spec.target_enrollment == 150
    assert len(spec.primary_outcomes) == 1
    assert spec.primary_outcomes[0].measure == "Systolic Blood Pressure (SBP)"
    assert spec.primary_outcomes[0].time_frame == "12 Weeks"
    assert len(spec.secondary_outcomes) == 1
    assert spec.min_age_years == 18.0
    assert spec.max_age_years == 60.0
    assert spec.allowed_sex == "FEMALE"
    
    # Check safety keywords extracted
    assert "safety" in spec.safety_endpoints
    assert "adverse event" in spec.safety_endpoints


def test_jaccard_similarity():
    """Verify Jaccard similarity word matching ignores standard stopwords."""
    # "Change in blood pressure" vs "blood pressure change"
    sim1 = calculate_jaccard_similarity("Change in blood pressure", "blood pressure change")
    assert sim1 == 1.0  # clean words: {'change', 'blood', 'pressure'} for both, 'in' is stopword
    
    # Unrelated strings
    sim2 = calculate_jaccard_similarity("Heart rate", "Diabetic neuropathy")
    assert sim2 == 0.0


def test_analyzer_perfect_match():
    """Verify analyzer returns score 100 when Soll-Protocol and Ist-Publication perfectly align."""
    protocol = ProtocolSpecification(
        nct_id="NCT00000001",
        official_title="Consistent Trial",
        target_enrollment=100,
        primary_outcomes=[OutcomeDefinition("HbA1c Reduction", "24 weeks")],
        secondary_outcomes=[OutcomeDefinition("Fasting Glucose", "24 weeks")],
        min_age_years=18.0,
        max_age_years=65.0,
        allowed_sex="ALL",
        safety_endpoints=["safety", "adverse events"]
    )
    
    publication = PublicationSpecification(
        nct_id="NCT00000001",
        official_title="Consistent Trial Publication",
        actual_enrollment=95,
        primary_outcomes=[OutcomeDefinition("HbA1c Reduction", "24 weeks")],
        secondary_outcomes=[OutcomeDefinition("Fasting Glucose", "24 weeks")],
        mean_age=45.0,
        sex_distribution={"MALE": 0.5, "FEMALE": 0.5},
        reported_adverse_events=[{"term": "Serious adverse events", "count": 2}],
        all_reported_endpoints=["safety", "HbA1c Reduction", "Fasting Glucose"]
    )
    
    analyzer = DiscrepancyAnalyzer(protocol, publication)
    report = analyzer.run_audit()
    
    assert report["integrity_score"] == 100.0
    assert report["risk_level"] == "LOW"
    assert len(report["endpoints"]["mismatched_primary_endpoints"]) == 0
    assert len(report["safety_omissions"]) == 0


def test_analyzer_discrepancies():
    """Verify analyzer flags swaps, demotions, shifts, and omitted safety endpoints."""
    protocol = ProtocolSpecification(
        nct_id="NCT00000002",
        official_title="Inconsistent Trial",
        target_enrollment=100,
        primary_outcomes=[
            OutcomeDefinition("HbA1c Reduction", "24 weeks"),
            OutcomeDefinition("Weight Loss", "24 weeks")
        ],
        secondary_outcomes=[
            OutcomeDefinition("Fasting Glucose", "24 weeks")
        ],
        min_age_years=18.0,
        max_age_years=65.0,
        allowed_sex="FEMALE",
        safety_endpoints=["hepatic toxicity", "adverse events"]
    )
    
    publication = PublicationSpecification(
        nct_id="NCT00000002",
        official_title="Inconsistent Trial Publication",
        actual_enrollment=50,  # 50% under-enrolled -> Alert
        primary_outcomes=[
            OutcomeDefinition("Fasting Glucose", "24 weeks"),  # Promoted from secondary
            OutcomeDefinition("Weight Loss", "12 weeks")       # Timeframe shift (24 -> 12 weeks)
        ],
        secondary_outcomes=[
            OutcomeDefinition("HbA1c Reduction", "24 weeks")   # Demoted from primary
        ],
        mean_age=72.0,                                         # Out of age bounds (>65) -> Alert
        sex_distribution={"MALE": 0.4, "FEMALE": 0.6},          # Violates FEMALE exclusion -> Alert
        reported_adverse_events=[{"term": "Mild headaches", "count": 12}],
        # "hepatic toxicity" is completely omitted
        all_reported_endpoints=["Fasting Glucose", "Weight Loss", "HbA1c Reduction", "adverse events"]
    )
    
    analyzer = DiscrepancyAnalyzer(protocol, publication)
    report = analyzer.run_audit()
    
    assert report["integrity_score"] < 50.0  # Should be CRITICAL risk
    assert report["risk_level"] == "CRITICAL"
    
    # Endpoint swaps
    endpoints = report["endpoints"]
    assert len(endpoints["demoted_endpoints"]) == 1
    assert endpoints["demoted_endpoints"][0]["endpoint"] == "HbA1c Reduction"
    assert len(endpoints["promoted_endpoints"]) == 1
    assert endpoints["promoted_endpoints"][0]["endpoint"] == "Fasting Glucose"
    
    # Timeframe shifts
    assert len(endpoints["timeframe_shifts"]) == 1
    assert endpoints["timeframe_shifts"][0]["endpoint"] == "Weight Loss"
    
    # Cohort alerts
    cohort_alerts = report["cohort"]["alerts"]
    assert len(cohort_alerts) == 3
    assert any("under-enrollment" in a for a in cohort_alerts)
    assert any("mean age" in a for a in cohort_alerts)
    assert any("eligibility" in a or "sex" in a for a in cohort_alerts)
    
    # Safety omissions
    assert len(report["safety_omissions"]) == 1
    assert "hepatic toxicity" in report["safety_omissions"][0]
