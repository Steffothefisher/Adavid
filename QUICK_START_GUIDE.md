# 🚀 QUICK START GUIDE: ADAVID Mit Echten Daten

## 5-Minuten Setup für Test-Datensätze

---

## **Option 1: Schnellster Start (2 Min)** 🔥

### Synthetische Daten generieren & ADAVID testen:

```python
# 1. ADAVID komponenten importieren
from adavid_scoring_system import (
    DataVerificationLayer,
    ADAVIDEngine,
    ADAVIDScoringEngine
)
from adavid_dataset_loader import ADDatasetLoader

# 2. Synthetische Daten generieren
loader = ADDatasetLoader()
clean_data = loader.load_synthetic(n_records=500, include_paradox=True)

# 3. Vollständige ADAVID Pipeline
verifier = DataVerificationLayer(clean_data)
verified_data = verifier.verify()

engine = ADAVIDEngine(verified_data)
audit_report = engine.run_audit()

scorer = ADAVIDScoringEngine(audit_report, verified_data)
score_report = scorer.run_scoring()

# 4. Ergebnisse anzeigen
print(score_report)
```

**Ausgabe:**
```
╔══════════════════════════════════════════════════════════════╗
║           ADAVID SCORING REPORT v1.7                        ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL SCORE: 72.4/100
   Risk Level: CONDITIONAL
   Approval Probability: 75.6%
   Confidence Interval (95%): [65.6, 79.2]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT BREAKDOWN:
Efficacy (Global)....... 78.5/100 (23.6 pts) ████████████████████░░░░░
Safety Profile........... 50.0/100 (12.5 pts) ██████████░░░░░░░░░░░░░░░
Data Quality............. 85.0/100 (12.75 pts) ███████████████████░░░░░░
Subgroup Consistency.... 75.0/100 (13.5 pts) ██████████████░░░░░░░░░░░
Statistical Power........ 80.0/100 (9.6 pts) ████████████████░░░░░░░░░

⚠️  EMPFEHLUNG: BEDINGTE GENEHMIGUNG
Simpson's Paradox erkannt...
```

---

## **Option 2: Real-World Data (10 Min)** 📊

### Von ClinicalTrials.gov herunterladen:

```bash
# Terminal:
python adavid_dataset_loader.py \
  --source clinicaltrials \
  --max-trials 1000 \
  --save \
  --info
```

**Oder im Python-Code:**

```python
from adavid_dataset_loader import ADDatasetLoader

loader = ADDatasetLoader()

# Lade Daten von ClinicalTrials.gov API
trials_df = loader.load_clinicaltrials(
    query="cancer drug efficacy",
    max_trials=1000
)

# Speichere für späteren Gebrauch
loader.save_to_csv("clinical_trials_data.csv")

# Daten-Übersicht
summary = loader.get_data_summary()
print(summary)
```

---

## **Option 3: Kaggle Dataset (5 Min, benötigt Account)** 🐼

### Voraussetzungen:
```bash
# 1. Kaggle API installieren
pip install kaggle

# 2. Kaggle Credentials einrichten
# Gehe zu: https://www.kaggle.com/settings/account
# Download "kaggle.json" → ~/.kaggle/kaggle.json
```

### Daten laden:
```python
from adavid_dataset_loader import ADDatasetLoader

loader = ADDatasetLoader()
kaggle_df = loader.load_kaggle()

print(f"Geladen: {len(kaggle_df)} Studien")
```

---

## **Option 4: MIMIC-III (Gold Standard, 20 Min)** 🏥

### Setup (einmalig):

```bash
# 1. Registrierung
# Gehe zu: https://physionet.org/content/mimiciii/1.4/
# Klick "Access the files" → Registrieren/Login

# 2. CITI Training (kostenlos, 30 min)
# Link von PhysioNet

# 3. Data Use Agreement unterzeichnen
# ~5 min

# 4. Download (PostgreSQL oder CSV)
# Empfehlung: Nutze MIMIC-Extract für vorbereitet Daten
```

### Daten laden (PostgreSQL):

```python
import psycopg2
import pandas as pd

# Verbinde zu lokaler MIMIC-III PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="mimic",
    user="postgres",
    password="password"
)

# Query ADMISSIONS & ICUSTAYS
query = """
SELECT 
    a.hadm_id,
    a.admittime,
    i.icustay_id,
    p.gender,
    EXTRACT(YEAR FROM age(a.admittime, p.dob)) as age,
    a.mortality_in_hospital
FROM admissions a
JOIN icustays i ON a.hadm_id = i.hadm_id
JOIN patients p ON a.subject_id = p.subject_id
LIMIT 5000;
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"Geladen: {len(df)} MIMIC Datensätze")
```

---

## 📋 VOLLSTÄNDIGE PIPELINE-BEISPIEL

```python
#!/usr/bin/env python3
"""
Komplettes ADAVID Workflow mit echten Daten
"""

import pandas as pd
from adavid_dataset_loader import ADDatasetLoader
from adavid_scoring_system import (
    DataVerificationLayer,
    ADAVIDEngine,
    ADAVIDScoringEngine
)

def main():
    # ===== SCHRITT 1: DATEN LADEN =====
    print("\n" + "="*60)
    print("SCHRITT 1: Daten laden")
    print("="*60)
    
    loader = ADDatasetLoader()
    
    # Wähle Datenquelle:
    # Option A: Synthetisch (schnell, für Testen)
    raw_data = loader.load_synthetic(n_records=500, include_paradox=True)
    
    # Option B: Von ClinicalTrials.gov (real, aber aggregiert)
    # raw_data = loader.load_clinicaltrials(max_trials=500)
    
    # Option C: Kaggle (einfach, vorverarbeitet)
    # raw_data = loader.load_kaggle()
    
    print(f"✅ Geladen: {len(raw_data)} Datensätze, {len(raw_data.columns)} Features")
    
    # ===== SCHRITT 2: DATENVERIFIKATION =====
    print("\n" + "="*60)
    print("SCHRITT 2: Datenverifikation (Pre-Flight)")
    print("="*60)
    
    verifier = DataVerificationLayer(raw_data)
    clean_data = verifier.verify()
    
    print(f"✅ Verifiziert: {len(clean_data)} saubere Datensätze")
    
    # ===== SCHRITT 3: AUDIT =====
    print("\n" + "="*60)
    print("SCHRITT 3: ADAVID Audit Engine")
    print("="*60)
    
    engine = ADAVIDEngine(clean_data)
    audit_report = engine.run_audit()
    
    print(f"✅ Global Efficacy: p={audit_report['global']['p_value']:.4f}")
    print(f"✅ Simpson's Paradox: {audit_report['segmentation']['simpson_paradox_detected']}")
    print(f"✅ Segments Analyzed: {audit_report['segmentation']['segments_analyzed']}")
    
    # ===== SCHRITT 4: SCORING =====
    print("\n" + "="*60)
    print("SCHRITT 4: ADAVID Scoring")
    print("="*60)
    
    scorer = ADAVIDScoringEngine(audit_report, clean_data)
    score_report = scorer.run_scoring()
    
    print(f"✅ Total Score: {score_report.total_score:.1f}/100")
    print(f"✅ Risk Level: {score_report.risk_level.value}")
    print(f"✅ Approval Probability: {score_report.approval_probability:.1%}")
    
    # ===== SCHRITT 5: BERICHT =====
    print("\n" + "="*60)
    print("SCHRITT 5: REGULATORY RECOMMENDATION")
    print("="*60)
    
    print(score_report.regulatory_recommendation)
    
    # ===== SCHRITT 6: EXPORT =====
    print("\n" + "="*60)
    print("SCHRITT 6: Ergebnisse exportieren")
    print("="*60)
    
    # CSV Export
    loader.data = clean_data
    loader.save_to_csv("adavid_cleaned_data.csv")
    
    # JSON Export
    import json
    report_json = {
        'total_score': round(score_report.total_score, 2),
        'risk_level': score_report.risk_level.value,
        'approval_probability': round(score_report.approval_probability, 4),
        'confidence_interval': [round(ci, 1) for ci in score_report.confidence_interval],
        'components': {
            name: {
                'raw_score': round(comp.raw_score, 1),
                'weight': comp.weight,
                'contribution': round(comp.calculate(), 2)
            }
            for name, comp in score_report.components.items()
        }
    }
    
    with open('adavid_report.json', 'w') as f:
        json.dump(report_json, f, indent=2)
    
    print("✅ Ergebnisse exportiert:")
    print("   - adavid_cleaned_data.csv")
    print("   - adavid_report.json")
    print("\n✅ ADAVID Pipeline abgeschlossen!")

if __name__ == "__main__":
    main()
```

**Ausführen:**
```bash
python adavid_complete_pipeline.py
```

---

## 🔄 WORKFLOWS NACH ANWENDUNGSFALL

### **A) SCHNELLE PROTOTYPISIERUNG** (5 min)
```python
from adavid_dataset_loader import generate_synthetic_trial_data
from adavid_scoring_system import ADAVIDScoringEngine, ADAVIDEngine, DataVerificationLayer

# Synthetische Daten
df = generate_synthetic_trial_data(n_records=500)

# Quick audit
verifier = DataVerificationLayer(df)
clean_data = verifier.verify()
engine = ADAVIDEngine(clean_data)
report = engine.run_audit()

# Scoring
scorer = ADAVIDScoringEngine(report, clean_data)
result = scorer.run_scoring()
print(f"Score: {result.total_score:.1f}/100")
```

### **B) VALIDIERUNG MIT REALEN DATEN** (30 min)
```python
# Lade von ClinicalTrials.gov
from adavid_dataset_loader import ADDatasetLoader

loader = ADDatasetLoader()
df = loader.load_clinicaltrials(max_trials=1000)

# Dann wie oben: verifier → engine → scorer
```

### **C) PRODUKTION (Multi-Dataset)** (1-2 Stunden)
```python
# Kombiniere mehrere Datenquellen
import pandas as pd

# Lade verschiedene Datasets
synthetics = loader.load_synthetic(n_records=1000)
clinicaltrials = loader.load_clinicaltrials(max_trials=500)

# Kombiniere (mit Vorsicht: Schema-Matching nötig)
combined = pd.concat([synthetics, clinicaltrials], axis=0, ignore_index=True)

# Pipeline wie oben
```

---

## 🛠️ TROUBLESHOOTING

### Problem: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas numpy scipy scikit-learn
```

### Problem: "Request timed out" bei ClinicalTrials.gov
```python
# Erhöhe Timeout
import socket
socket.setdefaulttimeout(30)

# Oder nutze kleinere Batches
df = loader.load_clinicaltrials(max_trials=100)  # Statt 1000
```

### Problem: "Data Use Agreement" für MIMIC-III
- Gehe zu: https://physionet.org/content/mimiciii/1.4/
- Registriere account
- Klick "Access the files"
- Folge Anweisungen (CITI Training + DUA)

### Problem: Kaggle API nicht funktionieren
```bash
# Stelle sicher, dass kaggle.json richtig liegt
mkdir -p ~/.kaggle
# Download von https://www.kaggle.com/settings/account
# Kopiere kaggle.json zu ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json  # Unix permissions
```

---

## 📊 NÄCHSTE SCHRITTE

### 1. **Daten erkunden**
```python
loader = ADDatasetLoader()
df = loader.load_synthetic()

# Daten-Übersicht
print(f"Shape: {df.shape}")
print(df.head())
print(df.describe())
print(df.dtypes)
```

### 2. **Visualisieren**
```python
import matplotlib.pyplot as plt

# Efficacy by group
df.groupby('Group')['Biomarker_Drop'].hist()
plt.show()

# Demographics
df['Age'].value_counts().plot.bar()
```

### 3. **Weitere Analysen**
```python
# Subgroup stratifizieren
df.groupby(['Age_Group', 'Group'])['Biomarker_Drop'].mean()

# Korrelationen
df[['Comorbidities_Count', 'Biomarker_Drop']].corr()
```

---

## 📚 DOKUMENTATIONS-LINKS

| Ressource | Link |
|-----------|------|
| ClinicalTrials.gov API | https://clinicaltrials.gov/api/ |
| MIMIC-III Dokumentation | https://mimic.mit.edu/ |
| PhysioNet | https://physionet.org/ |
| FDA Drugs@FDA | https://www.accessdata.fda.gov/ |
| Kaggle | https://www.kaggle.com/ |

---

## ✅ CHECKLIST: Erfolgreiches Setup

- [ ] Python 3.7+ installiert
- [ ] Abhängigkeiten: `pip install pandas numpy scipy scikit-learn`
- [ ] ADAVID-Dateien heruntergeladen
- [ ] Erstes Synthetisc-Test funktioniert
- [ ] Datenquelle ausgewählt (ClinicalTrials.gov / Kaggle / MIMIC)
- [ ] Erste echte Daten geladen
- [ ] ADAVID Pipeline läuft
- [ ] Ergebnisse exportiert

---

**Viel Erfolg mit ADAVID! 🚀**

---

**Version:** 1.0  
**Aktualisiert:** Mai 2026  
**Status:** Ready for Production
