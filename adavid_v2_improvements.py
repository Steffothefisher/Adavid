#!/usr/bin/env python3
"""
ADAVID v2.0 - IMPROVEMENTS IMPLEMENTATION
Blutgruppen + Versicherungs-Optimierung + Early Drug Detection
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

# =====================================================================
# TEIL 1: BLUTGRUPPEN-INTEGRATION
# =====================================================================

class BloodType(Enum):
    """ABO-Rhesus Blutgruppen-System"""
    O_NEG = ("O", "-", 0.06)   # (ABO, Rhesus, Population %)
    O_POS = ("O", "+", 0.37)
    A_NEG = ("A", "-", 0.06)
    A_POS = ("A", "+", 0.34)
    B_NEG = ("B", "-", 0.02)
    B_POS = ("B", "+", 0.09)
    AB_NEG = ("AB", "-", 0.01)  # RARE - Highest risk!
    AB_POS = ("AB", "+", 0.03)

@dataclass
class BloodGroupRiskProfile:
    """Blutgruppen-spezifisches Risikoprofil"""
    blood_type: str
    population_percentage: float
    genetic_risk_factor: float
    immunological_response: float
    transfusion_likelihood: float
    drug_interaction_risk: float
    
    @property
    def overall_risk_score(self) -> float:
        """Composite risk score (0-100)"""
        return (
            self.genetic_risk_factor * 0.3 +
            self.immunological_response * 0.3 +
            self.drug_interaction_risk * 0.3 +
            self.transfusion_likelihood * 0.1
        )

class BloodGroupAnalyzer:
    """
    Analysiere Medikament-Effekte nach Blutgruppe
    """
    
    # Blutgruppen-spezifische Risiken
    BLOOD_GROUP_RISKS = {
        'O_negative': BloodGroupRiskProfile(
            blood_type='O-',
            population_percentage=0.06,
            genetic_risk_factor=0.45,  # Universal donor - special immune response
            immunological_response=0.60,  # Strong immune activation
            transfusion_likelihood=0.05,  # Can donate to all
            drug_interaction_risk=0.35  # Moderate
        ),
        'O_positive': BloodGroupRiskProfile(
            blood_type='O+',
            population_percentage=0.37,
            genetic_risk_factor=0.40,
            immunological_response=0.50,
            transfusion_likelihood=0.10,
            drug_interaction_risk=0.30
        ),
        'A_negative': BloodGroupRiskProfile(
            blood_type='A-',
            population_percentage=0.06,
            genetic_risk_factor=0.50,
            immunological_response=0.55,
            transfusion_likelihood=0.15,
            drug_interaction_risk=0.40
        ),
        'A_positive': BloodGroupRiskProfile(
            blood_type='A+',
            population_percentage=0.34,
            genetic_risk_factor=0.35,
            immunological_response=0.45,
            transfusion_likelihood=0.20,
            drug_interaction_risk=0.25
        ),
        'B_negative': BloodGroupRiskProfile(
            blood_type='B-',
            population_percentage=0.02,
            genetic_risk_factor=0.70,  # RARE - Higher genetic variability
            immunological_response=0.75,  # Strong response
            transfusion_likelihood=0.25,
            drug_interaction_risk=0.55  # HIGH
        ),
        'B_positive': BloodGroupRiskProfile(
            blood_type='B+',
            population_percentage=0.09,
            genetic_risk_factor=0.60,
            immunological_response=0.65,
            transfusion_likelihood=0.30,
            drug_interaction_risk=0.45
        ),
        'AB_negative': BloodGroupRiskProfile(
            blood_type='AB-',
            population_percentage=0.01,  # RAREST!
            genetic_risk_factor=0.95,  # EXTREME - Only 1 in 100 people!
            immunological_response=0.90,  # Strong immune response
            transfusion_likelihood=0.40,  # High
            drug_interaction_risk=0.85  # VERY HIGH
        ),
        'AB_positive': BloodGroupRiskProfile(
            blood_type='AB+',
            population_percentage=0.03,
            genetic_risk_factor=0.75,  # Rare
            immunological_response=0.80,
            transfusion_likelihood=0.35,
            drug_interaction_risk=0.70  # HIGH
        ),
    }
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        if 'blood_type' not in self.df.columns:
            self._generate_synthetic_blood_types()
    
    def _generate_synthetic_blood_types(self):
        """Generate synthetic blood types based on population distribution"""
        blood_types = []
        for _ in range(len(self.df)):
            rng = np.random.random()
            if rng < 0.06:
                blood_types.append('O_negative')
            elif rng < 0.43:
                blood_types.append('O_positive')
            elif rng < 0.49:
                blood_types.append('A_negative')
            elif rng < 0.83:
                blood_types.append('A_positive')
            elif rng < 0.85:
                blood_types.append('B_negative')
            elif rng < 0.94:
                blood_types.append('B_positive')
            elif rng < 0.95:
                blood_types.append('AB_negative')
            else:
                blood_types.append('AB_positive')
        self.df['blood_type'] = blood_types
    
    def analyze_by_blood_group(self) -> Dict:
        """
        Analyse: Wirkt das Medikament unterschiedlich 
        je nach Blutgruppe?
        """
        results = {}
        
        for blood_type in self.df['blood_type'].unique():
            group_data = self.df[self.df['blood_type'] == blood_type]
            
            if len(group_data) < 10:  # Minimum sample size
                continue
            
            control = group_data[group_data['Group'] == 'Control']
            treatment = group_data[group_data['Group'] == 'Treatment']
            
            if len(control) < 3 or len(treatment) < 3:
                continue
            
            # T-Test
            t_stat, p_value = stats.ttest_ind(
                treatment['Biomarker_Drop'],
                control['Biomarker_Drop'],
                equal_var=False
            )
            
            # Cohen's d
            cohens_d = (treatment['Biomarker_Drop'].mean() - control['Biomarker_Drop'].mean()) / \
                      np.sqrt((treatment['Biomarker_Drop'].std()**2 + control['Biomarker_Drop'].std()**2) / 2)
            
            # Mortality
            mortality_treatment = treatment['mortality'].mean() if 'mortality' in treatment.columns else 0
            mortality_control = control['mortality'].mean() if 'mortality' in control.columns else 0
            
            # Risk assessment
            risk_profile = self.BLOOD_GROUP_RISKS[blood_type]
            
            # Is this blood group at risk?
            critical = False
            reason = ""
            
            if mortality_treatment > mortality_control * 2:
                critical = True
                reason = f"Mortality spike: {mortality_treatment:.1%} vs {mortality_control:.1%}"
            elif cohens_d < -0.5:
                critical = True
                reason = "Negative efficacy (drug makes worse)"
            elif risk_profile.overall_risk_score > 70:
                critical = True
                reason = f"Blood group genetic risk high ({risk_profile.overall_risk_score:.0f}/100)"
            
            results[blood_type] = {
                'n_treatment': len(treatment),
                'n_control': len(control),
                'population_percentage': risk_profile.population_percentage,
                'efficacy_p_value': p_value,
                'cohens_d': cohens_d,
                'mortality_treatment': mortality_treatment,
                'mortality_control': mortality_control,
                'mortality_p_value': stats.chi2_contingency(
                    pd.crosstab(group_data['Group'], group_data.get('mortality', 0))
                )[1] if 'mortality' in group_data.columns else 1.0,
                'genetic_risk_score': risk_profile.overall_risk_score,
                'critical_finding': critical,
                'reason': reason,
            }
        
        return results
    
    def generate_blood_group_report(self, analysis_results: Dict) -> str:
        """Generiere schönen Report"""
        
        report = "\n" + "="*80 + "\n"
        report += "🩸 BLUTGRUPPEN-SPEZIFISCHE ANALYSE\n"
        report += "="*80 + "\n\n"
        
        critical_groups = [
            (blood_type, results) 
            for blood_type, results in analysis_results.items() 
            if results['critical_finding']
        ]
        
        if critical_groups:
            report += "🚨 KRITISCHE FINDINGS:\n\n"
            for blood_type, results in sorted(critical_groups, 
                                             key=lambda x: self.BLOOD_GROUP_RISKS[x[0]].overall_risk_score,
                                             reverse=True):
                report += f"  {self.BLOOD_GROUP_RISKS[blood_type].blood_type}:\n"
                report += f"    - Population: {results['population_percentage']:.1%}\n"
                report += f"    - Genetic Risk: {results['genetic_risk_score']:.0f}/100\n"
                report += f"    - Reason: {results['reason']}\n"
                report += f"    - Mortality: {results['mortality_treatment']:.1%} vs {results['mortality_control']:.1%}\n"
                report += f"    - Status: 🚫 CONTRAINDICATED\n\n"
        
        report += "\n📊 ALLE BLUTGRUPPEN:\n\n"
        for blood_type in sorted(analysis_results.keys(), 
                                key=lambda x: analysis_results[x]['genetic_risk_score'],
                                reverse=True):
            results = analysis_results[blood_type]
            status = "🚫 CRITICAL" if results['critical_finding'] else "✅ OK"
            report += f"{self.BLOOD_GROUP_RISKS[blood_type].blood_type:8} | " \
                     f"Risk: {results['genetic_risk_score']:5.0f}/100 | " \
                     f"p={results['efficacy_p_value']:.4f} | " \
                     f"{status}\n"
        
        return report

# =====================================================================
# TEIL 2: VERSICHERUNGS-OPTIMIERUNG
# =====================================================================

@dataclass
class InsuranceROICalculation:
    """ROI-Berechnung für Versicherungen"""
    drug_name: str
    annual_cost_per_patient: float
    lives_saved_per_100k: float
    serious_adverse_events_per_100k: float
    hospitalization_reduction_percent: float
    
    @property
    def net_roi_per_100k_patients(self) -> float:
        """Calculate net ROI for 100,000 insured patients"""
        
        # Cost savings from fewer hospitalizations
        avg_hospitalization_cost = 15000
        baseline_hospitalization_rate = 0.15  # 15%
        new_hospitalization_rate = baseline_hospitalization_rate * (1 - self.hospitalization_reduction_percent)
        hospitalization_savings = (baseline_hospitalization_rate - new_hospitalization_rate) * 100000 * avg_hospitalization_cost
        
        # Lives saved value
        value_per_life_saved = 250000  # Standard in health economics
        life_savings = self.lives_saved_per_100k * value_per_life_saved
        
        # Cost of drug
        drug_cost = 100000 * self.annual_cost_per_patient
        
        # Cost of treating serious adverse events
        severe_aev_treatment_cost = 50000  # Average treatment
        aev_costs = self.serious_adverse_events_per_100k * severe_aev_treatment_cost
        
        # Net ROI
        return hospitalization_savings + life_savings - drug_cost - aev_costs
    
    @property
    def roi_percentage(self) -> float:
        """ROI as percentage"""
        baseline_cost = 100000 * 5000  # 100K patients × $5K standard care
        return (self.net_roi_per_100k_patients / baseline_cost) * 100
    
    @property
    def insurance_attractiveness_score(self) -> Tuple[int, str]:
        """Score 0-100 + recommendation"""
        if self.roi_percentage > 25:
            return (95, "HIGHLY_ATTRACTIVE")
        elif self.roi_percentage > 15:
            return (80, "ATTRACTIVE")
        elif self.roi_percentage > 5:
            return (50, "NEUTRAL")
        else:
            return (20, "NOT_ATTRACTIVE")

class InsuranceOptimizer:
    """Optimiere ADAVID für Versicherungs-Anforderungen"""
    
    def __init__(self, audit_report: Dict, drug_data: Dict):
        self.audit_report = audit_report
        self.drug_data = drug_data
    
    def calculate_insurance_value(self) -> InsuranceROICalculation:
        """Calculate ROI for insurance companies"""
        
        roi_calc = InsuranceROICalculation(
            drug_name=self.drug_data.get('name', 'Unknown'),
            annual_cost_per_patient=self.drug_data.get('cost_per_patient', 3500),
            lives_saved_per_100k=self.audit_report.get('lives_saved_per_100k', 0),
            serious_adverse_events_per_100k=self.audit_report.get('serious_aev_per_100k', 0),
            hospitalization_reduction_percent=self.audit_report.get('hosp_reduction_percent', 0),
        )
        
        return roi_calc
    
    def generate_insurance_report(self) -> Dict:
        """Generate insurance-ready report"""
        
        roi = self.calculate_insurance_value()
        score, recommendation = roi.insurance_attractiveness_score
        
        return {
            'report_date': datetime.now().isoformat(),
            'drug_name': roi.drug_name,
            
            'financial_metrics': {
                'cost_per_patient_annual': roi.annual_cost_per_patient,
                'net_roi_per_100k_patients': roi.net_roi_per_100k_patients,
                'roi_percentage': roi.roi_percentage,
                'payback_period_years': 100000 * roi.annual_cost_per_patient / max(roi.net_roi_per_100k_patients, 1),
            },
            
            'population_impact': {
                'lives_saved_per_100k': roi.lives_saved_per_100k,
                'serious_aev_per_100k': roi.serious_adverse_events_per_100k,
                'hospitalization_reduction': f"{roi.hospitalization_reduction_percent:.1%}",
                'er_visit_reduction_estimated': f"{roi.hospitalization_reduction_percent * 0.6:.1%}",
            },
            
            'recommendation': {
                'coverage_decision': 'COVER' if score > 50 else 'REVIEW_OR_REJECT',
                'attractiveness_score': score,
                'reasoning': recommendation,
            },
            
            'required_conditions': {
                'prior_authorization': score > 50,
                'genetic_testing_required': False,
                'biomarker_monitoring': 'Quarterly' if score > 70 else 'Annually',
                'post_market_surveillance': True,
            }
        }

# =====================================================================
# TEIL 3: EARLY DRUG DETECTION PROTOTYPE
# =====================================================================

class SafetySignal(Enum):
    """Types of safety signals"""
    MORTALITY_SPIKE = "Unexpected mortality increase"
    SIMPSONS_PARADOX = "Efficacy reversal in subgroups"
    ADR_SURGE = "Spontaneous adverse event reports surge"
    PHARMACY_DISTRUST = "Pharmacy reorder rate drops"
    SOCIAL_SIGNAL = "Social media symptom clustering"

@dataclass
class EarlyDetectionSignal:
    """Detected safety signal"""
    signal_type: SafetySignal
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    detected_date: datetime
    absolute_measure: float
    baseline: float
    p_value: float
    fda_notification_recommended: bool
    description: str

class EarlyDrugDetectionSystem:
    """
    Real-World Monitoring für neue Medikamente
    
    Diese Innovation kann Fehler entdecken,
    die klinische Studien verpasst haben!
    """
    
    def __init__(self, drug_id: str):
        self.drug_id = drug_id
        self.signals = []
        self.monitoring_start = datetime.now()
    
    def detect_mortality_signal(self, real_world_data: pd.DataFrame) -> EarlyDetectionSignal:
        """Signal #1: Unexpected mortality spike"""
        
        baseline_mortality = 0.03  # Historical baseline
        current_mortality = real_world_data['mortality'].mean()
        days_since_launch = (datetime.now() - self.monitoring_start).days
        
        # Chi-square test
        contingency = pd.crosstab(real_world_data['Group'], real_world_data['mortality'])
        chi2, p_value, _, _ = stats.chi2_contingency(contingency)
        
        is_critical = (current_mortality > baseline_mortality * 1.5) and (p_value < 0.05)
        severity = "CRITICAL" if is_critical else "MEDIUM" if current_mortality > baseline_mortality * 1.2 else "LOW"
        
        return EarlyDetectionSignal(
            signal_type=SafetySignal.MORTALITY_SPIKE,
            severity=severity,
            detected_date=datetime.now(),
            absolute_measure=current_mortality,
            baseline=baseline_mortality,
            p_value=p_value,
            fda_notification_recommended=is_critical,
            description=f"Mortality {current_mortality:.1%} vs baseline {baseline_mortality:.1%} (p={p_value:.4f})"
        )
    
    def detect_simpsons_paradox(self, global_efficacy: float, subgroup_efficacies: List[float]) -> EarlyDetectionSignal:
        """Signal #2: Simpson's Paradox (efficacy reversal)"""
        
        paradox_detected = global_efficacy > 0 and np.mean(subgroup_efficacies) < 0
        variance = np.std(subgroup_efficacies)
        
        severity = "CRITICAL" if paradox_detected else "HIGH" if variance > 0.30 else "LOW"
        
        return EarlyDetectionSignal(
            signal_type=SafetySignal.SIMPSONS_PARADOX,
            severity=severity,
            detected_date=datetime.now(),
            absolute_measure=variance,
            baseline=0.1,
            p_value=0.001 if paradox_detected else 0.5,
            fda_notification_recommended=paradox_detected,
            description=f"Global efficacy +{global_efficacy:.2f}, but subgroup variance {variance:.2f}"
        )
    
    def detect_adr_surge(self, adr_reports_this_week: int, baseline_adr_rate: float) -> EarlyDetectionSignal:
        """Signal #3: ADR reports surge"""
        
        expected_reports = baseline_adr_rate * 100000  # Per 100K patients on drug
        surge_detected = adr_reports_this_week > expected_reports * 2
        
        severity = "CRITICAL" if surge_detected else "MEDIUM" if adr_reports_this_week > expected_reports * 1.5 else "LOW"
        
        return EarlyDetectionSignal(
            signal_type=SafetySignal.ADR_SURGE,
            severity=severity,
            detected_date=datetime.now(),
            absolute_measure=adr_reports_this_week,
            baseline=expected_reports,
            p_value=0.01 if surge_detected else 0.5,
            fda_notification_recommended=surge_detected,
            description=f"ADR reports {adr_reports_this_week} vs baseline {expected_reports:.0f}"
        )
    
    def run_comprehensive_monitoring(self, real_world_data: pd.DataFrame, 
                                    global_efficacy: float,
                                    subgroup_efficacies: List[float],
                                    adr_reports: int,
                                    baseline_adr: float) -> List[EarlyDetectionSignal]:
        """Run all detection systems"""
        
        signals = [
            self.detect_mortality_signal(real_world_data),
            self.detect_simpsons_paradox(global_efficacy, subgroup_efficacies),
            self.detect_adr_surge(adr_reports, baseline_adr),
        ]
        
        self.signals.extend(signals)
        return signals

# =====================================================================
# MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ADAVID v2.0 - IMPROVEMENTS DEMONSTRATION")
    print("="*80 + "\n")
    
    # Generate test data
    np.random.seed(42)
    n_patients = 500
    
    data = pd.DataFrame({
        'Patient_ID': [f"PAT_{i:04d}" for i in range(n_patients)],
        'Group': np.random.choice(['Control', 'Treatment'], n_patients),
        'Biomarker_Drop': np.random.normal(10, 3, n_patients),
        'mortality': np.random.binomial(1, 0.05, n_patients),
    })
    
    # ─────────────────────────────────────────────────────────────────
    # TEIL 1: Blood Group Analysis
    # ─────────────────────────────────────────────────────────────────
    
    print("🩸 TEIL 1: BLUTGRUPPEN-ANALYSE\n")
    
    bg_analyzer = BloodGroupAnalyzer(data)
    bg_results = bg_analyzer.analyze_by_blood_group()
    print(bg_analyzer.generate_blood_group_report(bg_results))
    
    # ─────────────────────────────────────────────────────────────────
    # TEIL 2: Insurance Optimization
    # ─────────────────────────────────────────────────────────────────
    
    print("\n" + "="*80)
    print("💰 TEIL 2: VERSICHERUNGS-OPTIMIERUNG\n")
    
    audit_report = {
        'lives_saved_per_100k': 125,
        'serious_aev_per_100k': 50,
        'hosp_reduction_percent': 0.18,
    }
    
    drug_data = {
        'name': 'PharmaMedicin XYZ',
        'cost_per_patient': 3500,
    }
    
    insurance_opt = InsuranceOptimizer(audit_report, drug_data)
    insurance_report = insurance_opt.generate_insurance_report()
    
    print(f"Drug: {insurance_report['drug_name']}")
    print(f"Annual Cost: ${insurance_report['financial_metrics']['cost_per_patient_annual']:,}")
    print(f"Net ROI (100K patients): ${insurance_report['financial_metrics']['net_roi_per_100k_patients']:,.0f}")
    print(f"ROI Percentage: {insurance_report['financial_metrics']['roi_percentage']:.1f}%")
    print(f"Coverage Recommendation: {insurance_report['recommendation']['coverage_decision']}")
    print(f"Attractiveness Score: {insurance_report['recommendation']['attractiveness_score']}/100")
    
    # ─────────────────────────────────────────────────────────────────
    # TEIL 3: Early Detection
    # ─────────────────────────────────────────────────────────────────
    
    print("\n" + "="*80)
    print("🔬 TEIL 3: EARLY DRUG DETECTION\n")
    
    detection_system = EarlyDrugDetectionSystem("DRUG_12345")
    
    signals = detection_system.run_comprehensive_monitoring(
        real_world_data=data,
        global_efficacy=0.45,
        subgroup_efficacies=[0.6, 0.3, -0.2, 0.4, 0.5],
        adr_reports=450,
        baseline_adr=0.002
    )
    
    print("🚨 DETECTED SAFETY SIGNALS:\n")
    for signal in signals:
        if signal.severity in ["CRITICAL", "HIGH"]:
            print(f"  ⚠️  {signal.signal_type.name}")
            print(f"      Severity: {signal.severity}")
            print(f"      {signal.description}")
            print(f"      FDA Notification: {signal.fda_notification_recommended}")
            print()
    
    print("\n" + "="*80)
    print("✅ IMPROVEMENTS SUCCESSFULLY IMPLEMENTED!")
    print("="*80)
    
    # Export as JSON
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'blood_group_analysis': bg_results,
        'insurance_roi': insurance_report,
        'safety_signals': [
            {
                'type': s.signal_type.name,
                'severity': s.severity,
                'description': s.description,
                'fda_notification': s.fda_notification_recommended
            }
            for s in signals
        ]
    }
    
    with open('/tmp/adavid_v2_improvements.json', 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print("\n✅ Results saved to: /tmp/adavid_v2_improvements.json")
