#!/usr/bin/env python3
"""
ADAVID Deep Audit Engine - Kritische Subgruppen-Analyse
Hypothetischer Advanced-Mode für isolierte Gruppen-Analysen
mit Wirksamkeit, Simpson's Paradoxon und Mortalität-Tracking

Hauptziel: Finde verborgene Sicherheitsrisiken in Patient-Subgruppen
die bei Aggregated-Analyse übersehen würden
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =====================================================================
# CRITICAL SUBGROUP DEFINITIONS
# =====================================================================

class DemographicFactor(Enum):
    """Kritische demographische Faktoren für Deep Audit"""
    GENDER = "gender"
    AGE_GROUP = "age_group"
    LIVER_FUNCTION = "liver_function_low"
    KIDNEY_FUNCTION = "kidney_function_low"
    GENETIC_MARKER = "genetic_variant_x"
    COMORBIDITIES = "comorbidities_count"

@dataclass
class SubgroupProfile:
    """Definition einer kritischen Subgruppe"""
    name: str
    criteria: Dict[str, any]  # z.B. {'gender': 'F', 'age_group': 'Senior', 'liver_function_low': True}
    criticality_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    regulatory_flags: List[str]  # FDA/EMA Warnsignale

# =====================================================================
# HYPOTHETICAL SAFETY METRICS
# =====================================================================

@dataclass
class SafetyMetrics:
    """Sicherheits-Metriken für eine Subgruppe"""
    subgroup_name: str
    n_control: int
    n_treatment: int
    
    # Efficacy Metrics
    efficacy_p_value: float
    efficacy_effect_size: float  # Cohen's d
    responder_rate_treatment: float
    responder_rate_control: float
    
    # Safety Metrics
    mortality_rate_treatment: float  # % der Treatment-Patienten die starben
    mortality_rate_control: float
    mortality_p_value: float  # Ist Unterschied signifikant?
    adverse_event_rate: float
    serious_adverse_events: int
    
    # Simpson's Paradox Detection
    simpson_detected: bool
    paradox_explanation: Optional[str]
    
    # Biomarker Change
    biomarker_drop_treatment: float  # Mean
    biomarker_drop_control: float
    
    def to_dict(self) -> Dict:
        return {
            'subgroup': self.subgroup_name,
            'n_treatment': self.n_treatment,
            'n_control': self.n_control,
            'efficacy_p': round(self.efficacy_p_value, 5),
            'mortality_p': round(self.mortality_p_value, 5),
            'mortality_treatment': round(self.mortality_rate_treatment, 4),
            'mortality_control': round(self.mortality_rate_control, 4),
            'simpson_detected': self.simpson_detected,
        }

# =====================================================================
# CRITICAL SUBGROUP ANALYZER
# =====================================================================

class CriticalSubgroupAnalyzer:
    """
    Hypothetischer Deep-Audit Mode für ADAVID
    Analysiert jede Subgruppen-Kombination isoliert auf:
    1. Efficacy (mit Simpson's Paradox Detection)
    2. Mortality Rate Differenzen
    3. Adverse Events
    4. Drug-Drug/Drug-Disease Interactions
    """
    
    def __init__(self, dataframe: pd.DataFrame, 
                 groupby_columns: List[str] = None):
        """
        Args:
            dataframe: Patient-Level Daten mit allen Variablen
            groupby_columns: Spalten für Subgruppen-Definition
                Default: ['gender', 'age_group', 'liver_function_low']
        """
        self.df = dataframe.copy()
        self.groupby_columns = groupby_columns or [
            'gender', 
            'age_group', 
            'liver_function_low'
        ]
        
        # Ensure required columns exist
        self._validate_dataframe()
        
        # Store results
        self.subgroup_metrics: List[SafetyMetrics] = []
        self.global_metrics: Optional[SafetyMetrics] = None
        self.critical_findings: List[Dict] = []
    
    def _validate_dataframe(self):
        """Überprüfe dass alle erforderlichen Spalten existieren"""
        required_cols = [
            'Group',  # Control vs Treatment
            'Biomarker_Drop',
            'Patient_ID',
        ]
        
        # Mortality tracking
        if 'mortality' not in self.df.columns:
            logger.warning("⚠️  'mortality' Spalte nicht gefunden. Generiere synthetisch...")
            self.df['mortality'] = np.random.binomial(1, 0.08, len(self.df))
        
        # Adverse events
        if 'adverse_events' not in self.df.columns:
            logger.warning("⚠️  'adverse_events' Spalte nicht gefunden. Generiere synthetisch...")
            self.df['adverse_events'] = np.random.poisson(0.5, len(self.df))
        
        # Verify groupby columns
        for col in self.groupby_columns:
            if col not in self.df.columns:
                logger.error(f"❌ Erforderliche Spalte '{col}' nicht gefunden!")
                raise ValueError(f"Missing column: {col}")
    
    def run_global_audit(self) -> SafetyMetrics:
        """
        Schritt 1: Global-Analyse (Population Level)
        Basislinie für Simpson's Paradox Detection
        """
        logger.info("="*70)
        logger.info("SCHRITT 1: GLOBAL EFFICACY & SAFETY AUDIT")
        logger.info("="*70)
        
        control = self.df[self.df['Group'] == 'Control']
        treatment = self.df[self.df['Group'] == 'Treatment']
        
        # Efficacy Test
        t_stat, p_eff = stats.ttest_ind(
            treatment['Biomarker_Drop'],
            control['Biomarker_Drop'],
            equal_var=False
        )
        
        # Cohen's d
        cohens_d = (treatment['Biomarker_Drop'].mean() - control['Biomarker_Drop'].mean()) / \
                   np.sqrt((treatment['Biomarker_Drop'].std()**2 + control['Biomarker_Drop'].std()**2) / 2)
        
        # Mortality Comparison
        mort_treat = control['mortality'].sum() / len(control) if len(control) > 0 else 0
        mort_ctrl = treatment['mortality'].sum() / len(treatment) if len(treatment) > 0 else 0
        
        chi2, p_mort = stats.chi2_contingency(
            pd.crosstab(self.df['Group'], self.df['mortality'])
        )[:2]
        
        # Responder Rate (defined as Biomarker_Drop > median)
        median_drop = self.df['Biomarker_Drop'].median()
        responder_treat = (treatment['Biomarker_Drop'] > median_drop).sum() / len(treatment) if len(treatment) > 0 else 0
        responder_ctrl = (control['Biomarker_Drop'] > median_drop).sum() / len(control) if len(control) > 0 else 0
        
        self.global_metrics = SafetyMetrics(
            subgroup_name="GLOBAL_POPULATION",
            n_control=len(control),
            n_treatment=len(treatment),
            efficacy_p_value=p_eff,
            efficacy_effect_size=cohens_d,
            responder_rate_treatment=responder_treat,
            responder_rate_control=responder_ctrl,
            mortality_rate_treatment=mort_treat,
            mortality_rate_control=mort_ctrl,
            mortality_p_value=p_mort,
            adverse_event_rate=self.df['adverse_events'].mean(),
            serious_adverse_events=int((self.df['adverse_events'] >= 2).sum()),
            simpson_detected=False,
            paradox_explanation=None,
            biomarker_drop_treatment=treatment['Biomarker_Drop'].mean(),
            biomarker_drop_control=control['Biomarker_Drop'].mean(),
        )
        
        # Print Global Results
        print("\n📊 GLOBAL EFFICACY RESULTS:")
        print(f"   Treatment n={len(treatment)}, Control n={len(control)}")
        print(f"   Efficacy p-value: {p_eff:.6f} {'✅ SIGNIFICANT' if p_eff < 0.05 else '❌ NOT SIGNIFICANT'}")
        print(f"   Cohen's d: {cohens_d:.3f} ({'Large' if abs(cohens_d) > 0.8 else 'Medium' if abs(cohens_d) > 0.5 else 'Small'} effect)")
        print(f"   Responder Rate: Treatment {responder_treat:.1%} vs Control {responder_ctrl:.1%}")
        
        print("\n⚠️  GLOBAL MORTALITY (SAFETY SIGNAL):")
        print(f"   Treatment: {mort_treat:.2%} | Control: {mort_ctrl:.2%}")
        print(f"   Mortality p-value: {p_mort:.6f} {'⚠️  SIGNIFICANT' if p_mort < 0.05 else ''}")
        
        return self.global_metrics
    
    def run_critical_subgroup_analysis(self) -> List[SafetyMetrics]:
        """
        Schritt 2: Deep Subgroup Analysis
        Teste jede Kombination aus ['gender', 'age_group', 'liver_function_low']
        ISOLIERT auf:
        - Efficacy (Simpson's Paradox Test)
        - Mortality Rate Differenzen
        - Adverse Events
        """
        logger.info("\n" + "="*70)
        logger.info("SCHRITT 2: KRITISCHE SUBGRUPPEN-AUDIT")
        logger.info("="*70)
        
        # Create critical grouping
        kritische_gruppen = self.df.groupby(self.groupby_columns)
        
        print(f"\n🔍 Analysiere {kritische_gruppen.ngroups} Subgruppen-Kombinationen...")
        print(f"   Dimensionen: {' × '.join(self.groupby_columns)}")
        
        subgroup_results = []
        
        for group_keys, group_df in kritische_gruppen:
            if len(group_df) < 10:  # Minimum group size for validity
                logger.debug(f"⊘ Skip {group_keys} (n={len(group_df)} < 10)")
                continue
            
            # Create descriptive name
            subgroup_name = self._create_subgroup_name(group_keys)
            
            # Split by treatment
            control = group_df[group_df['Group'] == 'Control']
            treatment = group_df[group_df['Group'] == 'Treatment']
            
            # Skip if either group too small
            if len(control) < 5 or len(treatment) < 5:
                logger.debug(f"⊘ Skip {subgroup_name} (insufficient group sizes)")
                continue
            
            # ===== EFFICACY TEST =====
            try:
                t_stat, p_eff = stats.ttest_ind(
                    treatment['Biomarker_Drop'],
                    control['Biomarker_Drop'],
                    equal_var=False
                )
            except:
                p_eff = 1.0
            
            # Cohen's d
            try:
                cohens_d = (treatment['Biomarker_Drop'].mean() - control['Biomarker_Drop'].mean()) / \
                           np.sqrt((treatment['Biomarker_Drop'].std()**2 + control['Biomarker_Drop'].std()**2) / 2)
            except:
                cohens_d = 0.0
            
            # Responder Rate
            median_drop = group_df['Biomarker_Drop'].median()
            responder_treat = (treatment['Biomarker_Drop'] > median_drop).sum() / len(treatment) if len(treatment) > 0 else 0
            responder_ctrl = (control['Biomarker_Drop'] > median_drop).sum() / len(control) if len(control) > 0 else 0
            
            # ===== MORTALITY TEST =====
            try:
                mort_treat = control['mortality'].sum() / len(control) if len(control) > 0 else 0
                mort_ctrl = treatment['mortality'].sum() / len(treatment) if len(treatment) > 0 else 0
                
                # Chi-square test for mortality difference
                contingency = pd.crosstab(group_df['Group'], group_df['mortality'])
                if contingency.shape == (2, 2):
                    chi2, p_mort, dof, expected = stats.chi2_contingency(contingency)
                else:
                    p_mort = 1.0
            except:
                mort_treat = mort_ctrl = 0.0
                p_mort = 1.0
            
            # ===== SIMPSON'S PARADOX CHECK =====
            global_positive = self.global_metrics.efficacy_effect_size > 0
            subgroup_positive = cohens_d > 0
            simpson_detected = global_positive and not subgroup_positive and len(treatment) > 5
            
            # ===== ADVERSE EVENTS =====
            try:
                aev_rate = group_df['adverse_events'].mean()
                severe_aev = int((group_df['adverse_events'] >= 2).sum())
            except:
                aev_rate = 0.0
                severe_aev = 0
            
            # Create SafetyMetrics
            metrics = SafetyMetrics(
                subgroup_name=subgroup_name,
                n_control=len(control),
                n_treatment=len(treatment),
                efficacy_p_value=p_eff,
                efficacy_effect_size=cohens_d,
                responder_rate_treatment=responder_treat,
                responder_rate_control=responder_ctrl,
                mortality_rate_treatment=mort_treat,
                mortality_rate_control=mort_ctrl,
                mortality_p_value=p_mort,
                adverse_event_rate=aev_rate,
                serious_adverse_events=severe_aev,
                simpson_detected=simpson_detected,
                paradox_explanation=f"Global: {cohens_d:.2f} (positive) | Subgroup: {cohens_d:.2f} (negative)" if simpson_detected else None,
                biomarker_drop_treatment=treatment['Biomarker_Drop'].mean(),
                biomarker_drop_control=control['Biomarker_Drop'].mean(),
            )
            
            subgroup_results.append(metrics)
        
        self.subgroup_metrics = subgroup_results
        logger.info(f"✅ Analysiert: {len(subgroup_results)} valide Subgruppen")
        
        return subgroup_results
    
    def _create_subgroup_name(self, group_keys: Tuple) -> str:
        """Erstelle aussagekräftigen Namen für Subgruppe"""
        names = []
        for col, val in zip(self.groupby_columns, group_keys):
            if isinstance(val, bool):
                val_str = "✓" if val else "✗"
            else:
                val_str = str(val)[:8]
            names.append(f"{col}:{val_str}")
        return " | ".join(names)
    
    def identify_critical_findings(self) -> List[Dict]:
        """
        Schritt 3: Identifiziere KRITISCHE Sicherheits-Signals
        
        Kriterien für "CRITICAL":
        1. Significante Mortalitäts-Differenz (p < 0.05)
        2. Simpson's Paradox (Global positive, subgroup negative)
        3. Kontra-indiziert population (Biomarker Drop < Control)
        4. High Adverse Event Rate (>20%)
        """
        logger.info("\n" + "="*70)
        logger.info("SCHRITT 3: KRITISCHE SICHERHEITS-SIGNALS IDENTIFIZIEREN")
        logger.info("="*70)
        
        critical_flags = []
        
        for metrics in self.subgroup_metrics:
            finding = {
                'subgroup': metrics.subgroup_name,
                'severity': 'LOW',
                'flags': [],
                'recommendation': 'CONTINUE_MONITORING',
            }
            
            # FLAG 1: Mortality Signal
            if metrics.mortality_p_value < 0.05:
                finding['flags'].append({
                    'type': 'MORTALITY_SIGNAL',
                    'severity': 'CRITICAL',
                    'message': f"Signifikante Mortalitäts-Differenz: {metrics.mortality_rate_treatment:.2%} (treatment) vs {metrics.mortality_rate_control:.2%} (control), p={metrics.mortality_p_value:.5f}",
                    'recommendation': 'IMMEDIATE_INVESTIGATION',
                })
                finding['severity'] = 'CRITICAL'
                finding['recommendation'] = 'HALT_OR_RESTRICT'
            
            # FLAG 2: Simpson's Paradox
            if metrics.simpson_detected:
                finding['flags'].append({
                    'type': 'SIMPSONS_PARADOX',
                    'severity': 'HIGH',
                    'message': f"Simpson's Paradox: Global effect ist positiv, aber in '{metrics.subgroup_name}' ist Effect negativ!",
                    'recommendation': 'CONTRAINDICATED_POPULATION',
                })
                finding['severity'] = 'HIGH'
            
            # FLAG 3: Negative Efficacy (drug makes worse)
            if metrics.efficacy_effect_size < -0.5:
                finding['flags'].append({
                    'type': 'NEGATIVE_EFFICACY',
                    'severity': 'HIGH',
                    'message': f"Drug makes condition worse in this subgroup (Cohen's d = {metrics.efficacy_effect_size:.3f})",
                    'recommendation': 'ABSOLUTE_CONTRAINDICATION',
                })
                finding['severity'] = 'HIGH'
            
            # FLAG 4: High Adverse Event Rate
            if metrics.adverse_event_rate > 0.20:
                finding['flags'].append({
                    'type': 'HIGH_AEV_RATE',
                    'severity': 'MEDIUM',
                    'message': f"High adverse event rate: {metrics.adverse_event_rate:.1%}",
                    'recommendation': 'REQUIRE_GENETIC_TESTING_OR_DOSAGE_ADJUSTMENT',
                })
                if finding['severity'] != 'CRITICAL':
                    finding['severity'] = 'MEDIUM'
            
            # FLAG 5: Very Low Responder Rate
            if metrics.responder_rate_treatment < 0.30 and metrics.n_treatment > 20:
                finding['flags'].append({
                    'type': 'LOW_RESPONDER_RATE',
                    'severity': 'MEDIUM',
                    'message': f"Very low responder rate: {metrics.responder_rate_treatment:.1%} (should be >50% in responsive population)",
                    'recommendation': 'POOR_RESPONDER_POPULATION_IDENTIFIED',
                })
                if finding['severity'] == 'LOW':
                    finding['severity'] = 'MEDIUM'
            
            # Only add if findings exist
            if finding['flags']:
                critical_flags.append(finding)
        
        self.critical_findings = critical_flags
        
        # Print Critical Findings
        if critical_flags:
            print(f"\n🚨 FOUND {len(critical_flags)} CRITICAL SUBGROUPS:\n")
            for i, finding in enumerate(critical_flags, 1):
                print(f"{i}. {finding['subgroup']}")
                print(f"   Severity: {finding['severity']}")
                print(f"   Recommendation: {finding['recommendation']}")
                for flag in finding['flags']:
                    print(f"   - {flag['type']}: {flag['message']}")
                print()
        else:
            print("\n✅ No critical safety signals detected in subgroups!")
        
        return critical_flags
    
    def generate_regulatory_report(self) -> Dict:
        """
        Schritt 4: Generiere FDA/EMA-konforme Audit-Report
        """
        logger.info("\n" + "="*70)
        logger.info("SCHRITT 4: REGULATORISCHER AUDIT-REPORT")
        logger.info("="*70)
        
        report = {
            'title': 'ADAVID Deep Subgroup Audit Report',
            'timestamp': pd.Timestamp.now().isoformat(),
            
            'global_analysis': {
                'n_total': len(self.df),
                'n_treatment': len(self.df[self.df['Group'] == 'Treatment']),
                'n_control': len(self.df[self.df['Group'] == 'Control']),
                'efficacy_p_value': round(self.global_metrics.efficacy_p_value, 6),
                'mortality_p_value': round(self.global_metrics.mortality_p_value, 6),
                'global_assessment': 'PASS' if self.global_metrics.efficacy_p_value < 0.05 else 'FAIL',
            },
            
            'subgroup_analysis': {
                'total_subgroups_analyzed': len(self.subgroup_metrics),
                'subgroups_with_efficacy': sum(1 for m in self.subgroup_metrics if m.efficacy_p_value < 0.05),
                'subgroups_with_mortality_signal': sum(1 for m in self.subgroup_metrics if m.mortality_p_value < 0.05),
                'subgroups_with_simpsons_paradox': sum(1 for m in self.subgroup_metrics if m.simpson_detected),
                'metrics': [m.to_dict() for m in self.subgroup_metrics[:15]],  # Top 15
            },
            
            'critical_findings': self.critical_findings,
            
            'regulatory_recommendation': self._make_recommendation(),
            
            'required_actions': self._list_required_actions(),
        }
        
        return report
    
    def _make_recommendation(self) -> str:
        """Generiere regulatorische Empfehlung basierend auf Befunde"""
        critical_count = sum(1 for f in self.critical_findings if f['severity'] == 'CRITICAL')
        high_count = sum(1 for f in self.critical_findings if f['severity'] == 'HIGH')
        
        if critical_count > 0:
            return "🚫 REJECT - Multiple critical safety signals identified in important subgroups"
        elif high_count >= 2:
            return "⚠️  CONDITIONAL APPROVAL - Requires genetic testing, biomarker monitoring, and restricted distribution"
        elif high_count == 1:
            return "⚠️  CONDITIONAL APPROVAL - Requires monitoring in identified subgroup and potential labeling changes"
        elif self.global_metrics.efficacy_p_value < 0.05:
            return "✅ APPROVE - Safe and efficacious across population"
        else:
            return "❌ REJECT - Insufficient efficacy in population"
    
    def _list_required_actions(self) -> List[str]:
        """Liste erforderliche regulatorische Maßnahmen"""
        actions = []
        
        critical_count = sum(1 for f in self.critical_findings if f['severity'] == 'CRITICAL')
        if critical_count > 0:
            actions.append("1. HALT TRIAL - Investigate mortality signals immediately")
            actions.append("2. Conduct full safety review with independent Data Safety Monitoring Board")
            actions.append("3. Determine if contraindicated populations need exclusion criteria")
        
        paradox_count = sum(1 for f in self.critical_findings if any(flag['type'] == 'SIMPSONS_PARADOX' for flag in f['flags']))
        if paradox_count > 0:
            actions.append(f"4. Implement genetic/biomarker testing - {paradox_count} subgroups contraindicated")
            actions.append("5. Restrict prescribing to tested/screened populations")
            actions.append("6. Add Black Box Warning for vulnerable populations")
        
        high_count = sum(1 for f in self.critical_findings if f['severity'] == 'HIGH')
        if high_count > 0:
            actions.append(f"7. Add dosage adjustment recommendations for {high_count} identified subgroups")
            actions.append("8. Implement pharmacovigilance monitoring plan")
            actions.append("9. Require ongoing safety reporting every 6 months")
        
        if not actions:
            actions.append("Continue standard post-market surveillance")
        
        return actions
    
    def print_executive_summary(self):
        """Drucke Executive Summary für schnellen Überblick"""
        print("\n" + "="*80)
        print("        ADAVID DEEP AUDIT - EXECUTIVE SUMMARY")
        print("="*80)
        
        report = self.generate_regulatory_report()
        
        print("\n📊 GLOBAL RESULTS:")
        print(f"   Total Patients: {report['global_analysis']['n_total']}")
        print(f"   Treatment: {report['global_analysis']['n_treatment']} | Control: {report['global_analysis']['n_control']}")
        print(f"   Global Efficacy: p={report['global_analysis']['efficacy_p_value']:.6f}")
        print(f"   Assessment: {report['global_analysis']['global_assessment']}")
        
        print("\n🔍 SUBGROUP FINDINGS:")
        sg = report['subgroup_analysis']
        print(f"   Total Subgroups Analyzed: {sg['total_subgroups_analyzed']}")
        print(f"   With Efficacy Signal: {sg['subgroups_with_efficacy']}")
        print(f"   With Mortality Signal: {sg['subgroups_with_mortality_signal']}")
        print(f"   With Simpson's Paradox: {sg['subgroups_with_simpsons_paradox']}")
        
        print("\n🚨 CRITICAL FINDINGS:")
        print(f"   Total: {len(report['critical_findings'])}")
        if report['critical_findings']:
            for finding in report['critical_findings']:
                print(f"   - {finding['subgroup']}: {finding['severity']}")
        else:
            print("   None detected")
        
        print("\n⚖️  REGULATORY RECOMMENDATION:")
        print(f"   {report['regulatory_recommendation']}")
        
        print("\n📋 REQUIRED ACTIONS:")
        for action in report['required_actions']:
            print(f"   {action}")
        
        return report

# =====================================================================
# HYPOTHETICAL DATA GENERATOR WITH REALISTIC SAFETY SIGNALS
# =====================================================================

def generate_realistic_trial_data_with_safety_signals(
    n_records: int = 800,
    include_mortality_signal: bool = True,
    paradox_in_elderly_female: bool = True,
    include_liver_tox: bool = True,
) -> pd.DataFrame:
    """
    Generiere REALISTISCHE Klinische Trial-Daten mit:
    1. Globale Efficacy ✓
    2. Aber versteckte Mortalitäts-Signale in Subgruppen
    3. Simpson's Paradoxon in elderly females
    4. Leber-Toxizität in Patienten mit schlechter Leber-Funktion
    """
    logger.info(f"🔧 Generiere realistische Trial-Daten mit Safety Signals...")
    
    np.random.seed(42)
    
    data = {
        'Patient_ID': [f"PAT_{i:04d}" for i in range(n_records)],
        'Group': np.random.choice(['Control', 'Treatment'], size=n_records, p=[0.5, 0.5]),
        'gender': np.random.choice(['M', 'F'], size=n_records, p=[0.45, 0.55]),
        'age_group': np.random.choice(['Young', 'Middle', 'Senior'], size=n_records, p=[0.3, 0.4, 0.3]),
        'liver_function_low': np.random.choice([False, True], size=n_records, p=[0.8, 0.2]),
        'kidney_function_low': np.random.choice([False, True], size=n_records, p=[0.85, 0.15]),
        'genetic_variant_x': np.random.choice([False, True], size=n_records, p=[0.7, 0.3]),
        'comorbidities_count': np.random.poisson(1.5, size=n_records),
    }
    
    df = pd.DataFrame(data)
    
    # ===== GENERATE BIOMARKER WITH GLOBAL EFFICACY BUT SUBGROUP RISKS =====
    df['Biomarker_Drop'] = 0.0
    
    for idx in df.index:
        base_effect = 10.0  # Control baseline
        
        if df.loc[idx, 'Group'] == 'Treatment':
            # GLOBAL POSITIVE EFFECT (Simpson's Paradoxon Setup)
            treatment_effect = 3.5 + np.random.normal(0, 1.5)
            
            # PARADOX: Elderly females - drug doesn't work
            if paradox_in_elderly_female:
                if df.loc[idx, 'age_group'] == 'Senior' and df.loc[idx, 'gender'] == 'F':
                    treatment_effect *= -0.3  # REVERSE EFFECT!
            
            # LIVER TOXICITY: Low liver function patients have worse outcomes
            if include_liver_tox:
                if df.loc[idx, 'liver_function_low']:
                    treatment_effect *= 0.4  # Reduced efficacy + higher toxicity risk
            
            base_effect += treatment_effect
        
        df.loc[idx, 'Biomarker_Drop'] = base_effect + np.random.normal(0, 2)
    
    # ===== GENERATE MORTALITY WITH SAFETY SIGNALS =====
    df['mortality'] = 0
    
    for idx in df.index:
        # Base mortality rate
        base_mortality = 0.03 if df.loc[idx, 'Group'] == 'Control' else 0.05
        
        # MORTALITY SIGNAL: Elderly females in treatment group
        if df.loc[idx, 'Group'] == 'Treatment' and paradox_in_elderly_female:
            if df.loc[idx, 'age_group'] == 'Senior' and df.loc[idx, 'gender'] == 'F':
                base_mortality = 0.15  # CRITICAL SIGNAL: 15% vs 3% in control!
        
        # LIVER-RELATED MORTALITY
        if include_liver_tox:
            if df.loc[idx, 'Group'] == 'Treatment' and df.loc[idx, 'liver_function_low']:
                base_mortality = 0.12  # High risk!
        
        df.loc[idx, 'mortality'] = 1 if np.random.random() < base_mortality else 0
    
    # ===== GENERATE ADVERSE EVENTS =====
    df['adverse_events'] = 0
    
    for idx in df.index:
        base_aev = 0.2
        
        if df.loc[idx, 'Group'] == 'Treatment':
            base_aev = 0.5
            
            # Higher AEV in liver impaired patients
            if df.loc[idx, 'liver_function_low']:
                base_aev = 2.0
        
        df.loc[idx, 'adverse_events'] = np.random.poisson(base_aev)
    
    logger.info(f"✅ Generated {len(df)} records with realistic safety signals")
    logger.info(f"   Mortality Rate (Treatment): {df[df['Group']=='Treatment']['mortality'].mean():.2%}")
    logger.info(f"   Mortality Rate (Control): {df[df['Group']=='Control']['mortality'].mean():.2%}")
    
    return df

# =====================================================================
# MAIN EXECUTION: HYPOTHETICAL DEEP AUDIT
# =====================================================================

if __name__ == "__main__":
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  ADAVID DEEP AUDIT ENGINE - KRITISCHE SUBGRUPPEN ANALYSE".center(78) + "█")
    print("█" + "  Hypothetisches Szenario: Drogen mit versteckten Sicherheitsrisiken".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")
    
    # ===== GENERATE REALISTIC DATA WITH SAFETY SIGNALS =====
    print("SETUP: Generiere realistische Trial-Daten mit versteckten Safety Signals...\n")
    
    trial_data = generate_realistic_trial_data_with_safety_signals(
        n_records=800,
        include_mortality_signal=True,
        paradox_in_elderly_female=True,
        include_liver_tox=True,
    )
    
    print(f"Data shape: {trial_data.shape}")
    print(f"Columns: {list(trial_data.columns)}\n")
    
    # ===== RUN DEEP AUDIT =====
    print("\n" + "█"*80)
    print("█ STARTING DEEP AUDIT PROCESS".center(80) + "█")
    print("█"*80)
    
    analyzer = CriticalSubgroupAnalyzer(
        dataframe=trial_data,
        groupby_columns=['gender', 'age_group', 'liver_function_low']
    )
    
    # Step 1: Global Audit
    global_metrics = analyzer.run_global_audit()
    
    # Step 2: Subgroup Analysis
    subgroup_results = analyzer.run_critical_subgroup_analysis()
    
    # Step 3: Critical Findings
    critical_findings = analyzer.identify_critical_findings()
    
    # Step 4: Print Executive Summary
    print("\n")
    report = analyzer.print_executive_summary()
    
    # ===== EXPORT RESULTS =====
    print("\n" + "="*80)
    print("EXPORTING RESULTS")
    print("="*80)
    
    # Save detailed report as JSON
    import json
    with open('/tmp/adavid_deep_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("✅ Detailed report saved to: /tmp/adavid_deep_audit_report.json")
    
    # Save subgroup metrics as CSV
    subgroup_df = pd.DataFrame([m.to_dict() for m in analyzer.subgroup_metrics])
    subgroup_df.to_csv('/tmp/adavid_subgroup_metrics.csv', index=False)
    print("✅ Subgroup metrics saved to: /tmp/adavid_subgroup_metrics.csv")
    
    # Save critical findings
    with open('/tmp/adavid_critical_findings.json', 'w') as f:
        json.dump(analyzer.critical_findings, f, indent=2, default=str)
    print("✅ Critical findings saved to: /tmp/adavid_critical_findings.json")
    
    print("\n" + "█"*80)
    print("█ AUDIT COMPLETE".center(80) + "█")
    print("█"*80)
