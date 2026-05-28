import numpy as np
import pandas as pd
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# =====================================================================
# SCORING SYSTEM ENUMS & DATA STRUCTURES
# =====================================================================

class RiskLevel(Enum):
    """Regulatory Risk Classification"""
    APPROVED = "APPROVED"           # ≥ 85 points
    CONDITIONAL = "CONDITIONAL"     # 70-84 points
    REVIEW_REQUIRED = "REVIEW"      # 50-69 points
    REJECTED = "REJECTED"            # < 50 points

class SegmentPerformance(Enum):
    """Patient Subgroup Performance Categories"""
    EXCELLENT = 4      # p < 0.001, strong effect
    GOOD = 3           # p < 0.01, moderate effect
    ACCEPTABLE = 2     # p < 0.05, detectable effect
    MARGINAL = 1       # p < 0.10, weak effect
    FAILED = 0         # p ≥ 0.10, no effect

@dataclass
class ScoreComponent:
    """Individual scoring component"""
    name: str
    weight: float  # Importance multiplier (0.0-1.0)
    raw_score: float  # 0-100 points
    contribution: float  # weight * raw_score
    description: str
    
    def calculate(self) -> float:
        return self.weight * self.raw_score

@dataclass
class ADAVIDScore:
    """Complete audit score report"""
    total_score: float
    risk_level: RiskLevel
    approval_probability: float
    components: Dict[str, ScoreComponent]
    segment_breakdown: Dict[str, float]
    regulatory_recommendation: str
    confidence_interval: Tuple[float, float]
    
    def __str__(self) -> str:
        return f"""
╔══════════════════════════════════════════════════════════════╗
║           ADAVID SCORING REPORT v1.7                        ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL SCORE: {self.total_score:.1f}/100
   Risk Level: {self.risk_level.value}
   Approval Probability: {self.approval_probability:.1%}
   Confidence Interval (95%): [{self.confidence_interval[0]:.1f}, {self.confidence_interval[1]:.1f}]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT BREAKDOWN:

{self._format_components()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REGULATORY RECOMMENDATION:
{self.regulatory_recommendation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    
    def _format_components(self) -> str:
        lines = []
        for name, component in self.components.items():
            contribution = component.calculate()
            bar = "█" * int(contribution / 2) + "░" * (50 - int(contribution / 2))
            lines.append(f"{name:.<30} {component.raw_score:>5.1f}/100 ({contribution:>5.1f} pts) {bar}")
        return "\n".join(lines)

# =====================================================================
# CORE SCORING ENGINE
# =====================================================================

class ADAVIDScoringEngine:
    """
    Multidimensionales Scoring-System für klinische Studien.
    Bewertet: Efficacy, Safety, Data Quality, Subgroup Consistency, Statistical Power
    """
    
    # Scoring-Gewichte (insgesamt = 1.0)
    WEIGHTS = {
        'efficacy': 0.30,               # 30% - Hauptwirksamkeit
        'safety_paradox': 0.25,         # 25% - Simpson's Paradox / Nebenwirkungen
        'data_quality': 0.15,           # 15% - Datenreinigung & Validierung
        'subgroup_consistency': 0.18,   # 18% - Konsistenz über Patiententypen
        'statistical_power': 0.12,      # 12% - Stichprobengröße & Signifikanzen
    }
    
    def __init__(self, audit_report: Dict, clean_data: pd.DataFrame):
        """
        Args:
            audit_report: Report von ADAVIDEngine.run_audit()
            clean_data: Bereinigte DataFrame nach DataVerificationLayer
        """
        self.audit_report = audit_report
        self.clean_data = clean_data
        self.components: Dict[str, ScoreComponent] = {}
        
    def calculate_efficacy_score(self) -> ScoreComponent:
        """
        Bewertet die Grundwirksamkeit des Medikaments.
        
        Scoring:
        - p < 0.001: 95-100 Punkte
        - p < 0.01:  85-94 Punkte
        - p < 0.05:  70-84 Punkte (knapp signifikant)
        - p ≥ 0.05:  0-69 Punkte (keine Wirksamkeit)
        
        Plus: Effektgröße (Cohen's d)
        """
        global_result = self.audit_report['global']
        p_val = global_result['p_value']
        
        # Basis-Score basierend auf p-Wert
        if p_val < 0.001:
            base_score = 95
        elif p_val < 0.01:
            base_score = 85
        elif p_val < 0.05:
            base_score = 75
        else:
            base_score = 20  # Keine Signifikanz = hohes Risiko
        
        # Bonus für positive Trend
        if global_result['positive_trend']:
            trend_bonus = 5
        else:
            trend_bonus = -20  # Negative Trends sind gefährlich
        
        # Effektgröße-Bonus (Cohen's d)
        control = self.clean_data[self.clean_data['Group'] == 'Control']['Biomarker_Drop']
        treatment = self.clean_data[self.clean_data['Group'] == 'Treatment']['Biomarker_Drop']
        cohens_d = (treatment.mean() - control.mean()) / np.sqrt((treatment.std()**2 + control.std()**2) / 2)
        
        # Cohen's d Interpretation: 0.2=klein, 0.5=mittel, 0.8=groß
        if abs(cohens_d) >= 0.8:
            effect_bonus = 10
        elif abs(cohens_d) >= 0.5:
            effect_bonus = 5
        elif abs(cohens_d) >= 0.2:
            effect_bonus = 2
        else:
            effect_bonus = -5
        
        raw_score = min(100, max(0, base_score + trend_bonus + effect_bonus))
        
        return ScoreComponent(
            name='Efficacy (Global)',
            weight=self.WEIGHTS['efficacy'],
            raw_score=raw_score,
            contribution=0,
            description=f"Global p-value={p_val:.4f}, Cohen's d={cohens_d:.2f}, Trend={'✓' if global_result['positive_trend'] else '✗'}"
        )
    
    def calculate_safety_score(self) -> ScoreComponent:
        """
        Bewertet das Sicherheitsprofil.
        
        Scoring:
        - Kein Simpson's Paradox: +100 Punkte (Gold Standard)
        - Paradox mit <20% Patienten betroffen: 70-80 Punkte
        - Paradox mit >20% betroffen: 40-60 Punkte
        - Paradox mit gefährlichen Trends: <40 Punkte
        """
        paradox_detected = self.audit_report['segmentation']['simpson_paradox_detected']
        
        if not paradox_detected:
            # Kein Paradox = Sicherheit
            safety_score = 95
            description = "✓ Simpson's Paradox NOT detected - Drug is safe across subgroups"
        else:
            # Paradox erkannt → Berechne Schweregrad
            failed_segments = [
                seg for seg, data in self.audit_report['segmentation']['details'].items()
                if not data['effective']
            ]
            
            total_segments = len(self.audit_report['segmentation']['details'])
            failure_rate = len(failed_segments) / max(total_segments, 1)
            
            if failure_rate <= 0.20:
                safety_score = 75  # Mild
                description = f"⚠ Simpson's Paradox: {len(failed_segments)}/{total_segments} segments failed (mild)"
            elif failure_rate <= 0.50:
                safety_score = 50  # Moderate
                description = f"⚠⚠ Simpson's Paradox: {len(failed_segments)}/{total_segments} segments failed (moderate)"
            else:
                safety_score = 30  # Schwer
                description = f"🚨 Simpson's Paradox: {len(failed_segments)}/{total_segments} segments failed (SEVERE)"
        
        return ScoreComponent(
            name='Safety Profile',
            weight=self.WEIGHTS['safety_paradox'],
            raw_score=safety_score,
            contribution=0,
            description=description
        )
    
    def calculate_data_quality_score(self) -> ScoreComponent:
        """
        Bewertet die Datenqualität und Reinigung.
        
        Scoring:
        - 0-5% Datenverlust: 95-100 Punkte (ausgezeichnet)
        - 5-15% Datenverlust: 80-94 Punkte (gut)
        - 15-30% Datenverlust: 60-79 Punkte (akzeptabel)
        - >30% Datenverlust: <60 Punkte (kritisch)
        
        Plus: Null-Wert-Rate, fehlende Variablen
        """
        initial_rows = len(self.clean_data) / (1 - 0.10)  # Estimate (würde vom Verifier kommen)
        current_rows = len(self.clean_data)
        data_loss_rate = 1 - (current_rows / initial_rows) if initial_rows > 0 else 0.05
        
        # Basis-Score basierend auf Datenverlust
        if data_loss_rate <= 0.05:
            quality_score = 98
        elif data_loss_rate <= 0.15:
            quality_score = 85
        elif data_loss_rate <= 0.30:
            quality_score = 70
        else:
            quality_score = 40
        
        # Bonus/Malus für Null-Werte
        null_rate = self.clean_data.isnull().sum().sum() / (self.clean_data.shape[0] * self.clean_data.shape[1])
        if null_rate > 0.05:
            quality_score -= 20
        
        # Stichprobengröße (n < 50 = Problem)
        if len(self.clean_data) < 50:
            quality_score -= 30
        elif len(self.clean_data) < 100:
            quality_score -= 10
        
        raw_score = min(100, max(0, quality_score))
        
        return ScoreComponent(
            name='Data Quality',
            weight=self.WEIGHTS['data_quality'],
            raw_score=raw_score,
            contribution=0,
            description=f"Data Loss: {data_loss_rate:.1%} | Sample Size: {len(self.clean_data)} | Null Rate: {null_rate:.2%}"
        )
    
    def calculate_subgroup_consistency_score(self) -> ScoreComponent:
        """
        Bewertet die Konsistenz der Wirksamkeit über Patientengruppen.
        
        Scoring:
        - 100% Segmente erfolgreich: 95-100 Punkte
        - 75-99% Segmente erfolgreich: 80-94 Punkte
        - 50-74% Segmente erfolgreich: 60-79 Punkte
        - <50% Segmente erfolgreich: <60 Punkte
        """
        segment_details = self.audit_report['segmentation']['details']
        
        if not segment_details:
            return ScoreComponent(
                name='Subgroup Consistency',
                weight=self.WEIGHTS['subgroup_consistency'],
                raw_score=50,
                contribution=0,
                description="No subgroup data available"
            )
        
        successful_segments = sum(1 for data in segment_details.values() if data['effective'])
        total_segments = len(segment_details)
        success_rate = successful_segments / total_segments if total_segments > 0 else 0
        
        # Konsistenz-Score
        if success_rate >= 0.95:
            consistency_score = 98
        elif success_rate >= 0.85:
            consistency_score = 85
        elif success_rate >= 0.75:
            consistency_score = 75
        elif success_rate >= 0.60:
            consistency_score = 60
        elif success_rate >= 0.40:
            consistency_score = 40
        else:
            consistency_score = 20
        
        return ScoreComponent(
            name='Subgroup Consistency',
            weight=self.WEIGHTS['subgroup_consistency'],
            raw_score=consistency_score,
            contribution=0,
            description=f"Success Rate: {success_rate:.1%} ({successful_segments}/{total_segments} segments)"
        )
    
    def calculate_statistical_power_score(self) -> ScoreComponent:
        """
        Bewertet die statistische Power und Zuverlässigkeit.
        
        Scoring:
        - Großer Effekt (Cohen's d > 0.8) + große Stichprobe: 95-100
        - Mittlerer Effekt (0.5-0.8) + ausreichende Stichprobe: 80-94
        - Kleiner Effekt (0.2-0.5): 60-79
        - Sehr kleiner Effekt (<0.2): <60
        """
        control = self.clean_data[self.clean_data['Group'] == 'Control']['Biomarker_Drop']
        treatment = self.clean_data[self.clean_data['Group'] == 'Treatment']['Biomarker_Drop']
        
        # Cohen's d
        cohens_d = (treatment.mean() - control.mean()) / np.sqrt((treatment.std()**2 + control.std()**2) / 2)
        
        # Sample Size (n=385 für 80% Power, 0.05 alpha, 0.5 Cohen's d)
        n_total = len(self.clean_data)
        
        # Kombinierter Score
        if abs(cohens_d) >= 0.8 and n_total >= 300:
            power_score = 98
        elif abs(cohens_d) >= 0.5 and n_total >= 200:
            power_score = 85
        elif abs(cohens_d) >= 0.3 and n_total >= 100:
            power_score = 75
        elif abs(cohens_d) >= 0.2 and n_total >= 50:
            power_score = 60
        else:
            power_score = 40
        
        # Strafe für zu kleine Stichproben
        if n_total < 30:
            power_score -= 40
        
        raw_score = min(100, max(0, power_score))
        
        return ScoreComponent(
            name='Statistical Power',
            weight=self.WEIGHTS['statistical_power'],
            raw_score=raw_score,
            contribution=0,
            description=f"Cohen's d: {cohens_d:.2f} | Sample Size: {n_total}"
        )
    
    def calculate_approval_probability(self, total_score: float) -> float:
        """
        Konvertiert den Gesamtscore in Genehmigungswahrscheinlichkeit (Logistisch).
        
        Formula: P(approval) = 1 / (1 + e^(-k*(score-50)))
        """
        k = 0.1  # Steilheit der Kurve
        approval_prob = 1 / (1 + np.exp(-k * (total_score - 50)))
        return approval_prob
    
    def calculate_confidence_interval(self, total_score: float, std_error: float = 3.5) -> Tuple[float, float]:
        """
        95% Konfidenzintervall um den Score.
        """
        z_critical = 1.96  # 95% CI
        margin = z_critical * std_error
        return (
            max(0, total_score - margin),
            min(100, total_score + margin)
        )
    
    def generate_regulatory_recommendation(self, total_score: float, risk_level: RiskLevel) -> str:
        """
        Erzeugt eine detaillierte regulatorische Empfehlung.
        """
        recommendations = {
            RiskLevel.APPROVED: f"""
✅ EMPFEHLUNG: GENEHMIGUNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: {total_score:.1f}/100 | Dieser Wirkstoff zeigt:
  • Statistisch signifikante Wirksamkeit (p < 0.05)
  • Kein Simpson's Paradox erkannt
  • Konsistente positive Effekte über Patientengruppen
  • Hochwertige Datenqualität
  
MASSNAHMEN:
  1. Volle regulatorische Zulassung empfohlen
  2. Standardetikett ohne Warnungen
  3. Allgemeine Verschreibung zulässig
  4. Routineüberwachung nach Marktzulassung
            """,
            
            RiskLevel.CONDITIONAL: f"""
⚠️  EMPFEHLUNG: BEDINGTE ZULASSUNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: {total_score:.1f}/100 | Simpson's Paradox erkannt - Risiken in Subgruppen:
  • Globale Wirksamkeit: ✓ POSITIVE
  • Subgruppen-Performance: ⚠️ HETEROGEN
  
MASSNAHMEN (ERFORDERLICH):
  1. Genetische Testung VOR Verschreibung
  2. Altersgerechte Dosierungsrichtlinien
  3. Kontraindikationen für Non-Responder-Gruppen
  4. Intensivierte Pharmakovigilanz und Überwachung
  5. Post-Marketing-Studien in Risikogruppen
  6. Regelmässige Sicherheitsberichte (alle 6 Monate)
  
ZIELGRUPPE:
  → Nur Patienten mit positiver Genetischer/Alterseignung
            """,
            
            RiskLevel.REVIEW_REQUIRED: f"""
🔍 EMPFEHLUNG: DETAILLIERTE ÜBERPRÜFUNG ERFORDERLICH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: {total_score:.1f}/100 | Mehrere Bedenken:
  • Grenzwertige statistische Signifikanz
  • Datenqualitätsprobleme
  • Unzureichende Subgruppen-Daten
  
ERFORDERLICHE AKTIONEN:
  1. Zusätzliche klinische Studien (Phase III erweitert)
  2. Datenqualität-Verbesserungen
  3. Biologisches Verständnis vertiefen
  4. Vergleichsstudien mit Standard-Therapie
  5. Wiedereinreichung nach 12 Monaten
            """,
            
            RiskLevel.REJECTED: f"""
🚫 EMPFEHLUNG: ABLEHNUNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: {total_score:.1f}/100 | Kritische Mängel:
  • KEINE statistisch signifikante Wirksamkeit (p ≥ 0.05)
  • Oder: Signifikantes Sicherheitsrisiko
  • Unzureichende Datenqualität
  
ERGEBNIS:
  ❌ NICHT ZUR GENEHMIGUNG EMPFOHLEN
  
NÄCHSTE SCHRITTE:
  1. Neudesign oder Abbruch der Entwicklung
  2. Mechanismus der Nicht-Wirksamkeit untersuchen
  3. Falls Neuentwicklung: Minimum 2+ Jahre weitere Arbeit
            """
        }
        return recommendations.get(risk_level, "Unbekannter Status")
    
    def run_scoring(self) -> ADAVIDScore:
        """
        Führt das komplette Scoring aus und gibt strukturiertes Report.
        """
        logging.info("🔍 Starte ADAVID Scoring Engine...")
        
        # Berechne alle Komponenten
        self.components['efficacy'] = self.calculate_efficacy_score()
        self.components['safety'] = self.calculate_safety_score()
        self.components['data_quality'] = self.calculate_data_quality_score()
        self.components['consistency'] = self.calculate_subgroup_consistency_score()
        self.components['power'] = self.calculate_statistical_power_score()
        
        # Berechne Gesamtscore (gewichtete Summe)
        total_score = sum(comp.calculate() for comp in self.components.values())
        total_score = min(100, max(0, total_score))  # Clippen auf [0, 100]
        
        # Bestimme Risiko-Level
        if total_score >= 85:
            risk_level = RiskLevel.APPROVED
        elif total_score >= 70:
            risk_level = RiskLevel.CONDITIONAL
        elif total_score >= 50:
            risk_level = RiskLevel.REVIEW_REQUIRED
        else:
            risk_level = RiskLevel.REJECTED
        
        # Berechne Genehmigungswahrscheinlichkeit
        approval_prob = self.calculate_approval_probability(total_score)
        
        # Konfidenzintervall
        ci = self.calculate_confidence_interval(total_score)
        
        # Regulatory Recommendation
        recommendation = self.generate_regulatory_recommendation(total_score, risk_level)
        
        # Segment-Breakdown
        segment_breakdown = {
            name: data.get('p_value', 1.0) 
            for name, data in self.audit_report['segmentation']['details'].items()
        }
        
        logging.info(f"✅ Scoring abgeschlossen: {total_score:.1f}/100 ({risk_level.value})")
        
        return ADAVIDScore(
            total_score=total_score,
            risk_level=risk_level,
            approval_probability=approval_prob,
            components=self.components,
            segment_breakdown=segment_breakdown,
            regulatory_recommendation=recommendation,
            confidence_interval=ci
        )

# =====================================================================
# BEISPIEL: VOLLSTÄNDIGER WORKFLOW
# =====================================================================

if __name__ == "__main__":
    # Dummy-Daten (würden von echtem ADAVID kommen)
    from collections import namedtuple
    
    # Simuliere Audit-Report
    audit_report = {
        'global': {
            'p_value': 0.0342,
            'success': True,
            'positive_trend': True
        },
        'segmentation': {
            'segments_analyzed': 12,
            'simpson_paradox_detected': True,
            'details': {
                'Age:Young|VariantX:True|Comorb:0': {'effective': True, 'p_value': 0.0156, 'sample_size': 18},
                'Age:Young|VariantX:False|Comorb:1': {'effective': False, 'p_value': 0.4821, 'sample_size': 12},
                'Age:Middle-Aged|VariantX:False|Comorb:0': {'effective': True, 'p_value': 0.0023, 'sample_size': 15},
                'Age:Senior|VariantX:True|Comorb:2': {'effective': False, 'p_value': 0.0687, 'sample_size': 9},
                'Age:Middle-Aged|VariantX:True|Comorb:1': {'effective': True, 'p_value': 0.0412, 'sample_size': 11},
                'Age:Senior|VariantX:False|Comorb:0': {'effective': True, 'p_value': 0.0091, 'sample_size': 14},
                'Age:Young|VariantX:True|Comorb:2': {'effective': False, 'p_value': 0.5234, 'sample_size': 7},
                'Age:Senior|VariantX:True|Comorb:3': {'effective': False, 'p_value': 0.3456, 'sample_size': 6},
                'Age:Middle-Aged|VariantX:False|Comorb:2': {'effective': True, 'p_value': 0.0134, 'sample_size': 13},
                'Age:Young|VariantX:False|Comorb:3': {'effective': False, 'p_value': 0.7123, 'sample_size': 5},
                'Age:Middle-Aged|VariantX:True|Comorb:0': {'effective': True, 'p_value': 0.0056, 'sample_size': 16},
                'Age:Senior|VariantX:False|Comorb:1': {'effective': False, 'p_value': 0.2789, 'sample_size': 8},
            }
        }
    }
    
    # Simuliere saubere Daten
    np.random.seed(42)
    clean_data = pd.DataFrame({
        'Group': np.random.choice(['Control', 'Treatment'], size=450),
        'Biomarker_Drop': np.random.normal(loc=12, scale=4, size=450)
    })
    
    # Scoring ausführen
    scorer = ADAVIDScoringEngine(audit_report, clean_data)
    score_report = scorer.run_scoring()
    
    # Ergebnisse anzeigen
    print(score_report)
    
    # JSON-Export (für Integration in Dashboards)
    print("\n" + "="*60)
    print("JSON EXPORT (für API-Integration):")
    print("="*60)
    import json
    
    json_output = {
        'total_score': round(score_report.total_score, 2),
        'risk_level': score_report.risk_level.value,
        'approval_probability': round(score_report.approval_probability, 4),
        'confidence_interval': [round(ci, 2) for ci in score_report.confidence_interval],
        'components': {
            name: {
                'raw_score': round(comp.raw_score, 2),
                'weight': comp.weight,
                'contribution': round(comp.calculate(), 2),
                'description': comp.description
            }
            for name, comp in score_report.components.items()
        }
    }
    
    print(json.dumps(json_output, indent=2, ensure_ascii=False))
