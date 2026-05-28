# 🔍 ADAVID DEEP AUDIT - QUICK REFERENCE CARD

## WORKFLOW IN 4 SCHRITTEN

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  SCHRITT 1: GLOBALE ANALYSE                                      │
│  ═════════════════════════════════════════════════════════════   │
│  Population Level - Alle Patienten zusammen                      │
│                                                                   │
│  Efficacy Test:                                                  │
│    Biomarker_Drop (Treatment) vs (Control)                       │
│    → t-test p-value < 0.05? ✅ = Efficacy Signal                │
│                                                                   │
│  Mortality Test:                                                 │
│    Mortality Rate (Treatment) vs (Control)                       │
│    → χ² p-value < 0.05? ⚠️ = Safety Signal                      │
│                                                                   │
│  Baseline for Simpson's Paradox Detection:                       │
│    Global Cohen's d = baseline_effect                            │
│                                                                   │
│  Example Results:                                                │
│    ✓ Efficacy: p = 0.003 (PASS)                                │
│    ~ Mortality: p = 0.18 (PASS - not significant)              │
│    → Recommendation: "Looks promising, check subgroups"         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  SCHRITT 2: SUBGRUPPEN-ANALYSE                                   │
│  ═════════════════════════════════════════════════════════════   │
│  ISOLIERTE Analyse jeder Subgruppen-Kombination                  │
│                                                                   │
│  Groupby Dimensions:                                             │
│    • gender: M / F (2 levels)                                    │
│    • age_group: Young / Middle / Senior (3 levels)              │
│    • liver_function_low: True / False (2 levels)                │
│    → 2 × 3 × 2 = 12 base combinations                           │
│    → ~40 combinations mit ausreichender Größe                    │
│                                                                   │
│  Für JEDE Subgruppe separat testen:                             │
│    1. Efficacy (t-test p-value)                                 │
│    2. Mortality (χ² test p-value)                               │
│    3. Cohen's d (Effect Size)                                   │
│    4. Biomarker Change                                          │
│    5. Adverse Events                                            │
│                                                                   │
│  Simpson's Paradox Check:                                       │
│    IF global_d > 0 AND subgroup_d < 0:                         │
│      → PARADOX DETECTED!                                         │
│                                                                   │
│  Example Critical Subgroup:                                      │
│    ┌─────────────────────────────────────────────────┐          │
│    │ Elderly Females (Senior + F + any liver func)  │          │
│    │                                                 │          │
│    │ Efficacy:                                       │          │
│    │   p = 0.041 ✓ (significant)                    │          │
│    │   d = -0.35 ❌ (NEGATIVE! Drug makes worse)    │          │
│    │                                                 │          │
│    │ Mortality: 🚨 CRITICAL                          │          │
│    │   Treatment: 15%                                │          │
│    │   Control:   3.6%                               │          │
│    │   p = 0.021 ⚠️ (significant)                   │          │
│    │                                                 │          │
│    │ Status: CONTRAINDICATED                         │          │
│    └─────────────────────────────────────────────────┘          │
│                                                                   │
│  Repeat for all 40 subgroups...                                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  SCHRITT 3: KRITISCHE FINDINGS IDENTIFIZIEREN                    │
│  ═════════════════════════════════════════════════════════════   │
│                                                                   │
│  Flag Type #1: MORTALITY_SIGNAL                                  │
│    Criterion: mortality_p < 0.05 AND mortality_diff > 5%        │
│    Severity: CRITICAL                                            │
│    Example: 15% vs 3% mortality (p=0.021)                       │
│    Action: INVESTIGATE, HALT_OR_RESTRICT                        │
│                                                                   │
│  Flag Type #2: SIMPSONS_PARADOX                                  │
│    Criterion: global_d > 0 AND subgroup_d < 0                  │
│    Severity: HIGH                                                │
│    Example: Global +0.45 but Elderly Females -0.35             │
│    Action: CONTRAINDICATED_POPULATION, GENETIC_TESTING         │
│                                                                   │
│  Flag Type #3: NEGATIVE_EFFICACY                                 │
│    Criterion: Cohen's d < -0.5                                  │
│    Severity: HIGH                                                │
│    Action: ABSOLUTE_CONTRAINDICATION                            │
│                                                                   │
│  Flag Type #4: HIGH_AEV_RATE                                     │
│    Criterion: adverse_event_rate > 20%                          │
│    Severity: MEDIUM                                              │
│    Action: REQUIRE_GENETIC_TESTING_OR_DOSAGE_ADJUSTMENT        │
│                                                                   │
│  Flag Type #5: LOW_RESPONDER_RATE                                │
│    Criterion: responder_rate < 30% AND n_treatment > 20        │
│    Severity: MEDIUM                                              │
│    Action: POOR_RESPONDER_POPULATION_IDENTIFIED                 │
│                                                                   │
│  Count Critical Findings:                                        │
│    • Critical Severity: #3                                       │
│    • High Severity: #5                                           │
│    • Medium Severity: #2                                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  SCHRITT 4: REGULATORISCHE EMPFEHLUNG                            │
│  ═════════════════════════════════════════════════════════════   │
│                                                                   │
│  Decision Logic:                                                 │
│                                                                   │
│    IF critical_count > 0:                                        │
│      → 🚫 REJECT                                                │
│        "Multiple critical safety signals"                        │
│                                                                   │
│    ELIF high_count >= 2:                                        │
│      → ⚠️ CONDITIONAL APPROVAL                                   │
│        "Genetic testing & restricted distribution required"     │
│                                                                   │
│    ELIF high_count == 1:                                        │
│      → ⚠️ CONDITIONAL APPROVAL                                   │
│        "Monitoring in identified subgroup"                       │
│                                                                   │
│    ELIF global_efficacy_p < 0.05:                              │
│      → ✅ APPROVE                                               │
│        "Safe and efficacious across population"                │
│                                                                   │
│    ELSE:                                                         │
│      → ❌ REJECT                                                │
│        "Insufficient efficacy"                                   │
│                                                                   │
│  Required Actions (Example):                                     │
│    ✓ Black Box Warning for elderly females                      │
│    ✓ Liver function testing before prescribing                  │
│    ✓ Dosage restrictions for high-risk groups                   │
│    ✓ Post-market surveillance (6-month reports)                 │
│    ✓ REMS program (Restricted Distribution)                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚨 CRITICAL FINDING SEVERITY LEVELS

```
┌──────────┬───────────────────────┬────────────────────────┐
│ Severity │ Criteria              │ Recommended Action     │
├──────────┼───────────────────────┼────────────────────────┤
│ CRITICAL │ • Mortality p<0.05    │ HALT_TRIAL             │
│          │   diff >5%            │ REJECT                 │
│          │ • Safety concern >15% │ CONTRAINDICATE         │
│          │                       │ IMMEDIATE_INVESTIGATION│
├──────────┼───────────────────────┼────────────────────────┤
│ HIGH     │ • Simpson's Paradox   │ CONDITIONAL_APPROVAL   │
│          │   p<0.05              │ GENETIC_TESTING        │
│          │ • Negative efficacy   │ RESTRICTED_DISTRIBUTION│
│          │   d < -0.5            │ BLACK_BOX_WARNING      │
├──────────┼───────────────────────┼────────────────────────┤
│ MEDIUM   │ • High AEV rate 10-20%│ DOSAGE_ADJUSTMENT      │
│          │ • Low responder <30%  │ ENHANCED_MONITORING    │
│          │ • Mortality trend     │ POST_MARKET_STUDY      │
│          │   p<0.10              │                        │
├──────────┼───────────────────────┼────────────────────────┤
│ LOW      │ • Non-significant     │ CONTINUE_MONITORING    │
│          │ • Rare adverse events │ ROUTINE_SURVEILLANCE   │
│          │ • Trend <p<0.10       │                        │
└──────────┴───────────────────────┴────────────────────────┘
```

---

## 📊 EXAMPLE SUBGROUP ANALYSIS TABLE

```
┌────────────────────────────────────────────────────────────────────────┐
│ Subgroup Analysis Results (Top 10 of 40)                               │
├──────────┬─────────┬───────────┬──────────┬──────────┬─────────────────┤
│ Subgroup │ n (T/C) │ Eff p-val │ Mortal % │ Mort p   │ Status          │
├──────────┼─────────┼───────────┼──────────┼──────────┼─────────────────┤
│ F/Snr/✓  │ 24/28   │ 0.0412    │ 15/3.6   │ 0.021 ⚠️ │ 🚫 CONTRAINDIC  │
│ F/Snr/✗  │ 32/35   │ 0.0156    │ 8/2.8    │ 0.085    │ ⚠️ HIGH RISK   │
│ M/Snr/✓  │ 28/31   │ 0.0234    │ 9/4.2    │ 0.142    │ 🔍 REVIEW      │
│ M/Mid/✗  │ 45/48   │ 0.0023    │ 4/3.1    │ 0.512    │ ✅ PASS        │
│ M/Young/✓│ 18/22   │ 0.4821    │ 6/2.3    │ 0.203    │ 🔍 NO EFFECT   │
│ F/Mid/✗  │ 42/40   │ 0.0134    │ 5/2.5    │ 0.234    │ ✅ PASS        │
│ M/Young/✗│ 61/58   │ 0.0045    │ 3/2.7    │ 0.742    │ ✅ PASS        │
│ F/Young/✓│ 15/18   │ 0.3456    │ 7/1.1    │ 0.089    │ ⚠️ TREND       │
│ M/Mid/✓  │ 38/41   │ 0.0567    │ 6/3.8    │ 0.386    │ 🔍 MARGINAL    │
│ F/Young/✗│ 21/24   │ 0.0789    │ 4/1.6    │ 0.298    │ ✅ MARGINAL    │
└──────────┴─────────┴───────────┴──────────┴──────────┴─────────────────┘

Legend:
  F/M = Female/Male
  Young/Mid/Snr = Age Group
  ✓/✗ = Liver Function Low/Normal
  T/C = Treatment/Control
  ⚠️ = Significant finding
```

---

## 🎯 DECISION TREE

```
                    GLOBAL ANALYSIS
                         │
                    p < 0.05?
                    /        \
                  YES         NO
                  │           │
                  ↓           ↓
             EFFICACY    ❌ REJECT
             PASSED      (Insufficient Efficacy)
                  │
                  ↓
           SUBGROUP ANALYSIS
                  │
    ┌─────┬──────┼──────┬─────┐
    │     │      │      │     │
    ↓     ↓      ↓      ↓     ↓
   No   One    Two    3+   Simpson's
  Critical Critical Critical Critical Paradox
    │      │      │      │     │
    ↓      ↓      ↓      ↓     ↓
    ✅    ⚠️     ⚠️     ❌     ⚠️
  PASS   COND   COND  REJECT  COND
  (high  (low   (med  (halt   (restrict
   conf  risk)  risk) trial)  pop)
```

---

## 💻 USAGE QUICK START

### Option 1: Generate Synthetic Data with Safety Signals
```python
from adavid_deep_audit_engine import (
    CriticalSubgroupAnalyzer,
    generate_realistic_trial_data_with_safety_signals
)

# Generate data with known safety signals
data = generate_realistic_trial_data_with_safety_signals(
    n_records=800,
    include_mortality_signal=True,
    paradox_in_elderly_female=True,
    include_liver_tox=True
)
```

### Option 2: Load Your Own Data
```python
import pandas as pd

data = pd.read_csv('your_clinical_trial_data.csv')
# Required columns: Patient_ID, Group, Biomarker_Drop, 
#                   mortality, gender, age_group, liver_function_low
```

### Option 3: Run the Analysis
```python
analyzer = CriticalSubgroupAnalyzer(
    dataframe=data,
    groupby_columns=['gender', 'age_group', 'liver_function_low']
)

# Step 1: Global
global_metrics = analyzer.run_global_audit()

# Step 2: Subgroups
subgroup_results = analyzer.run_critical_subgroup_analysis()

# Step 3: Critical findings
critical_findings = analyzer.identify_critical_findings()

# Step 4: Report
report = analyzer.generate_regulatory_report()
analyzer.print_executive_summary()
```

### Option 4: Export Results
```python
import json

# Save detailed report
with open('audit_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

# Save subgroup metrics
pd.DataFrame([m.to_dict() for m in analyzer.subgroup_metrics]).to_csv(
    'subgroup_metrics.csv', index=False
)
```

---

## 📋 KEY METRICS AT A GLANCE

```
EFFICACY METRICS:
  ✓ p-value < 0.05             → Statistically significant
  ✓ Cohen's d > 0.5             → Moderate to large effect
  ✓ Responder Rate > 50%         → Majority respond well

SAFETY METRICS:
  ✓ Mortality p > 0.05          → No significant signal
  ✓ AEV Rate < 10%              → Minimal adverse events
  ✓ Serious AEV < 2%            → Very few severe events

RED FLAGS (STOP & INVESTIGATE):
  ❌ Mortality p < 0.05          → CRITICAL
  ❌ Cohen's d REVERSES          → PARADOX
  ❌ AEV Rate > 20%              → HIGH RISK
  ❌ Responder Rate < 30%        → POOR RESPONSE
  ❌ 2+ contraindicated groups   → SAFETY CONCERN
```

---

## 🔗 RELATED ANALYSES

```
ADAVID Deep Audit Engine
    ├─ Global Efficacy Analysis
    ├─ Subgroup Analysis (Multidimensional)
    ├─ Simpson's Paradox Detection
    ├─ Mortality Tracking
    ├─ Adverse Event Analysis
    └─ Regulatory Recommendation
        ├─ Black Box Warning Criteria
        ├─ Restricted Distribution
        ├─ Post-Market Surveillance
        └─ REMS Implementation
```

---

## 📞 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Not enough data in subgroup | Increase n_records or relax groupby criteria |
| No critical findings detected | Data may be synthetic; check mortality/paradox settings |
| High p-values everywhere | May indicate poor trial design; check data quality |
| Conflicting results | Expected - subgroups can have different responses |

---

**Version 1.0 | Hypothetical Deep Audit | Production Ready | May 2026**
