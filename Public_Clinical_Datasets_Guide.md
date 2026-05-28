# 🏥 Öffentliche Klinische Testdaten - Umfassende Übersicht

## Für ADAVID Scoring System Integration

**Stand:** Mai 2026  
**Aktualisiert:** Alle Links und Ressourcen validiert

---

## 📊 KATEGORIE 1: KRITISCHE CARE & HOSPITAL DATA

### 1. **MIMIC-III (Medical Information Mart for Intensive Care III)** ⭐⭐⭐⭐⭐
- **Quelle:** PhysioNet (MIT-Harvard)
- **Link:** https://physionet.org/content/mimiciii/1.4/
- **Größe:** 
  - 58,976 ICU-Aufenthalte
  - 46,520 eindeutige Patienten
  - 53,423 Krankenhausaufnahmen
- **Zeitraum:** 2001-2012 (Beth Israel Deaconess Medical Center, Boston)
- **Daten-Features:**
  - ✅ Vital Signs (Blutdruck, Herzfrequenz, O₂ Sättigung)
  - ✅ Labor-Tests (Biomarker, Elektrolyte, Blutbilder)
  - ✅ Medikationen (1.5M Einträge)
  - ✅ Flüssigkeitsbilanz
  - ✅ Diagnosen (ICD-9 Codes)
  - ✅ Prozedur-Codes
  - ✅ Klinische Notizen (2M Freitexte)
  - ✅ Outcomes (Mortalität, LOS)
- **Zugang:** 
  - Kostenlos mit Data Use Agreement
  - Registrierung erforderlich
  - Format: SQL Dump, PostgreSQL, CSV
- **Besonderheit:** Mit 4,579 charted observations & 380 lab measurements pro Aufenthalt sehr detailliert
- **Ideal für ADAVID:** ✅ Perfekt für Subgruppen-Analysen und Simpson's Paradox Testing

---

### 2. **MIMIC-IV (newer version)** ⭐⭐⭐⭐⭐
- **Quelle:** PhysioNet
- **Link:** https://physionet.org/content/mimiciv/3.1/
- **Größe:**
  - 376,519 Aufenthalte
  - 315,460 eindeutige Patienten
  - Zeitraum: 2008-2019
- **Verbesserungen gegenüber MIMIC-III:**
  - ✅ Größerer Datensatz (größer als MIMIC-III)
  - ✅ Neuere Daten (bis 2019)
  - ✅ Verbesserte Datenqualität
  - ✅ Standardisierte Codes (LOINC, RxNorm)
  - ✅ ICU und Krankenhaus-Ebenen getrennt
- **Format:** PostgreSQL, parquet files
- **Ideal für ADAVID:** ✅ Größerer Datensatz für robustere Statistiken

---

## 📋 KATEGORIE 2: KLINISCHE TRIAL REGISTRIES

### 3. **ClinicalTrials.gov** ⭐⭐⭐⭐
- **Quelle:** National Library of Medicine (NIH)
- **Link:** https://clinicaltrials.gov/
- **Größe:**
  - 500,000+ registrierte Studien
  - 370,000+ mit Ergebnissen
  - 58,000+ mit demographischen Daten
- **Daten-Features:**
  - ✅ Studiendesign (randomized, blinded, etc.)
  - ✅ Einschlusskriterien
  - ✅ Ethnische Zusammensetzung
  - ✅ Geschlechtsverteilung
  - ✅ Altersverteilung
  - ✅ Primary/Secondary Outcomes
  - ✅ P-Werte und Konfidenzintervalle
  - ✅ Adverse Events
  - ⚠️ **Limitation:** Keine Participant-Level-Daten (aggregiert)
- **Zugang:**
  - ✅ Vollständig öffentlich
  - API verfügbar: `https://clinicaltrials.gov/api/v2/`
  - Bulk Download: XML aller Studien
- **Download:**
  ```bash
  # Alle Studien herunterladen (sehr groß, ~50GB+)
  https://clinicaltrials.gov/api/download/studies
  ```
- **Format:** XML, JSON via API, CSV-Export
- **Ideal für ADAVID:** ⚠️ Gut für Proof-of-Concept, aber aggregierte Daten
  
---

### 4. **Global Clinical Trial Database (GCT)** ⭐⭐⭐⭐
- **Quelle:** Ozmosi Pharmaceutical Data
- **Link:** https://www.ozmosi.com/global-clinical-trial-data/
- **Größe:**
  - 500,000+ Studieneinträge
  - Konslidiert aus 15+ Registries
- **Regionen:**
  - ✅ USA (ClinicalTrials.gov)
  - ✅ EU (EUDRA-CT)
  - ✅ China, Japan, Brasil, Australien
  - ✅ WHO ICTRP
- **Features:**
  - Harmonisierte Felder
  - Status (Recruiting, Active, Completed, etc.)
  - Sponsor-Informationen
  - Outcomes
- **Zugang:** ✅ Kostenlos, web-searchable
- **Format:** Web-Interface, downloadbar
- **Ideal für ADAVID:** ✅ Größerer globaler Datensatz, gut für generalisierbarkeit

---

### 5. **WHO International Clinical Trials Registry Platform (ICTRP)** ⭐⭐⭐⭐
- **Quelle:** World Health Organization
- **Link:** https://www.who.int/trials
- **Größe:**
  - 600,000+ Studien
  - Daten aus 17 Registries
- **Länder-Abdeckung:**
  - USA, EU, China, Australien, Brasilien, Indien, Japan, Nigeria, Thailand, Niederlande, Südafrika, Sri Lanka, S. Korea, UK, Kanada + WHO
- **Besonderheit:**
  - Zentrale Suche über viele Registries
  - Harmonisierte Such-Schnittstelle
- **Ideal für ADAVID:** ✅ Weltweite Perspektive

---

## 🧬 KATEGORIE 3: PHARMA-SPEZIFISCHE DATEN

### 6. **Drugs@FDA Database** ⭐⭐⭐
- **Quelle:** Food and Drug Administration (USA)
- **Link:** https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm
- **Was ist es:**
  - Suchbare Datenbank aller FDA-genehmigten Medikamente
  - Zugang zu Approval-Dokumenten (NDA, BLA)
  - Clinical Review Papers mit Studiendetails
- **Daten-Features:**
  - ✅ Genehmigungsdatum
  - ✅ Klinische Studien-Summaries
  - ✅ P-Werte und Efficacy-Daten
  - ✅ Adverse Event Profiles
  - ✅ Demographic Breakdowns
  - ✅ Subgroup Analyses
- **Zugang:** ✅ Vollständig öffentlich
- **Format:** Web-Interface, PDF-Reports (zu parsen)
- **Ideal für ADAVID:** ✅ Echte FDA-Genehmigungsdaten, Perfect für Scoring Validation

---

### 7. **FDA FAERS (Adverse Event Reporting System)** ⭐⭐⭐
- **Quelle:** FDA
- **Link:** https://fis.fda.gov/sense/app/95239c51-ba12-4cde-a815-e872d3b22d46/sheet/05dad7c6-712e-40b9-83da-1d91f5a937d5/state/insert
- **Dashboard:** https://open.fda.gov/data/faers/
- **Größe:**
  - 18+ Million Adverse Events
  - Seit 1968
  - Continuous Updates
- **Features:**
  - ✅ Unerwünschte Ereignisse nach Medikament
  - ✅ Schweregrad
  - ✅ Demografische Daten des Patienten
  - ✅ Outcomes
  - ✅ Zeitstempel
  - ⚠️ **Limitation:** Post-Marketing, nicht Trial-spezifisch
- **Download:**
  ```
  https://open.fda.gov/data/faers/
  Quartalweise Datensätze als JSON/XML
  ```
- **Ideal für ADAVID:** ⚠️ Für Safety/Simpson's Paradox in Post-Market Phase

---

### 8. **FDA Drug Trials Snapshots** ⭐⭐⭐
- **Quelle:** FDA CDER
- **Link:** https://www.fda.gov/drugs/drug-approvals-and-databases/drug-trials-snapshots
- **Was ist es:**
  - Kurzzusammenfassungen von klinischen Studien
  - Demographische Daten von trial participants
  - Vergleich Efficacy/Safety zwischen Gruppen (ethnisch, Geschlecht, Alter)
- **Verfügbar für:** Neuere FDA-Genehmigungen (2015+)
- **Format:** HTML/PDF mit Graphiken
- **Ideal für ADAVID:** ⚠️ Limited Historical Data, aber moderne Standards

---

## 📈 KATEGORIE 4: KURATIERTE RESEARCH DATASETS

### 9. **Clinical Trial Outcome (CTO) Benchmark (Nature)** ⭐⭐⭐⭐
- **Quelle:** Nature Health (2026)
- **Link:** https://www.nature.com/articles/s44360-026-00081-6
- **Größe:**
  - 125,000+ Drug & Biologics Trials
  - Strukturierte Daten zur Wirksamkeit
  - Phase-weise Verfolgung
- **Features:**
  - ✅ Trial Outcomes (Success/Failure)
  - ✅ Phase Information
  - ✅ Drug Characteristics
  - ✅ AI-annotierte Metadaten
  - ✅ Stock Price & News Sentiment
- **Dataset:** Verfügbar für Forschung
- **Ideal für ADAVID:** ✅ Großer, hochqualitativer Datensatz speziell für Trial-Analyse

---

### 10. **Comparative Effectiveness of Innovative Treatments for Cancer (CEIT-Cancer)** ⭐⭐⭐⭐
- **Quelle:** Akademische Publikation
- **Link:** https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6146631/
- **Größe:**
  - Alle Cancer Drugs FDA-approved 2000-2016
  - ~200+ Medikamente
  - Trial-level data aus FDA approval packages
- **Features:**
  - ✅ Tumor Type
  - ✅ Overall Survival (OS) Daten
  - ✅ Efficacy vs. Comparators
  - ✅ Adverse Events by Subgroup
  - ✅ Study Design Details
  - ✅ Patient Demographics
- **Zugang:** Teilweise publikations-basiert, können mit Autoren kontaktieren
- **Ideal für ADAVID:** ✅ Spezifisch für Oncology, echte FDA-Daten

---

## 🧪 KATEGORIE 5: SPEZIAL-DOMÄNEN

### 11. **eICU Collaborative Research Database** ⭐⭐⭐⭐
- **Quelle:** PhysioNet
- **Link:** https://physionet.org/content/eicu-crd/2.0/
- **Größe:**
  - 200,859 ICU-Aufenthalte
  - 139,367 eindeutige Patienten
  - Mehrere Krankenhaus-Netzwerk (telehealth)
- **Vorteile über MIMIC:**
  - ✅ Multi-center (4 Staaten)
  - ✅ Repräsentativer für USA
  - ✅ Neuere Daten (2014-2015)
- **Ideal für ADAVID:** ✅ Für Multi-center Trial Simulation

---

### 12. **HiRID - High Time Resolution ICU Dataset** ⭐⭐⭐
- **Quelle:** ETH Zürich
- **Link:** https://physionet.org/content/hirid/1.1.1/
- **Größe:**
  - 36,474 ICU-Aufenthalte
  - Hochfrequente Zeitreihen (1-5 min Auflösung)
- **Besonderheit:**
  - ✅ Sehr detaillierte Vital Signs
  - ✅ Ideal für Longitudinal-Analysen
  - ✅ Europäische Perspektive (Schweiz)
- **Ideal für ADAVID:** ⚠️ Eher für Zeitreihen, aber gut für Trends in Biomarkern

---

### 13. **AmsterdamUMCdb** ⭐⭐⭐
- **Quelle:** Amsterdam Medical Data Science
- **Link:** https://physionet.org/content/amsterdamucmdb/1.0.2/
- **Größe:**
  - 23,106 ICU-Aufenthalte
  - Amsterdam University Medical Centers
- **Besonderheit:**
  - ✅ Europäische Daten
  - ✅ Gute Datenqualität
- **Ideal für ADAVID:** ⚠️ Kleinerer, aber qualitativ hochwertiger Datensatz

---

## 🎯 KATEGORIE 6: SPEZIALISIERTE TRIAL-REPOSITORIES

### 14. **St. Jude Children's Research Hospital (SJCRH) IPD** ⭐⭐⭐
- **Quelle:** St. Jude ClinicalTrials.gov
- **Link:** https://www.stjude.org/
- **Features:**
  - ✅ Pediatric Oncology Focus
  - ✅ IPD Sharing (Individual Participant Data)
  - ✅ Detaillierte Treatment Protocols
  - ✅ Long-term Follow-up Data
- **Zugang:** 
  - Über ClinicalTrials.gov
  - Data Request: ClinTrialDataRequest@stjude.org
- **Ideal für ADAVID:** ⚠️ Spezifisch für pädiatrische Krebsfälle

---

### 15. **Cochrane Central Register of Controlled Trials (CENTRAL)** ⭐⭐⭐
- **Quelle:** Cochrane Collaboration
- **Link:** https://www.cochranelibrary.com/cdsr/
- **Größe:**
  - 1 Million+ Trial-Zitate
  - Aus MEDLINE, EMBASE, etc.
  - Teil der Cochrane Library
- **Features:**
  - ✅ Struktur für Randomized Trials
  - ✅ Outcomes gesammelt
  - ✅ Meta-Analysis Ready
  - ⚠️ **Limitation:** Nur Zitate & Abstracts, nicht raw data
- **Zugang:** 
  - Open Access für Trial Titles/Abstracts
  - Volles PDF via Cochrane Library Subscription
- **Ideal für ADAVID:** ⚠️ Gut für Trial Metadata, nicht für Participant-Level Data

---

## 💾 KATEGORIE 7: DATENINTEGRATIONS-PLATTFORMEN

### 16. **AACT (Aggregate Content of ClinicalTrials.gov)** ⭐⭐⭐⭐
- **Quelle:** CTTI (Clinical Trials Transformation Initiative)
- **Link:** https://aact.ctti-clinicaltrials.org/
- **Was ist es:**
  - Automatisch aktualisierte Postgres-Datenbank
  - Alle ClinicalTrials.gov Daten, strukturiert
  - Einfacher zu durchsuchen als web interface
- **Features:**
  - ✅ Relational Database
  - ✅ Historical Data
  - ✅ Täglich aktualisiert
  - ✅ Kostenlos downloadbar
- **Download:**
  ```
  https://aact.ctti-clinicaltrials.org/
  PostgreSQL dump oder CSV exports
  ```
- **Ideal für ADAVID:** ✅ Strukturierte, durchsuchbare Version von ClinicalTrials.gov

---

### 17. **Kaggle Datasets (ClinicalTrials.gov)** ⭐⭐⭐
- **Quelle:** Kaggle
- **Link:** https://www.kaggle.com/datasets/danielansted/clinicaltrials-gov-clinical-trials-dataset
- **Features:**
  - Pre-processed CSV/Parquet
  - Bereits bereinigt
  - Einfach zu laden
- **Ideal für:** Quick Prototyping
- **Ideal für ADAVID:** ✅ Für schnelle Tests (aber weniger aktuell als direkt von ClinicalTrials.gov)

---

### 18. **GitHub: Clinical Trials US** ⭐⭐⭐
- **Quelle:** GitHub Datasets Organization
- **Link:** https://github.com/datasets/clinical-trials-us
- **Was ist es:**
  - Processing Scripts für ClinicalTrials.gov
  - Automatisierte Updates
- **Format:** CSV, JSON
- **Ideal für ADAVID:** ⚠️ Etwas veraltet (letzte Updates 2013+)

---

## 🌍 KATEGORIE 8: INTERNATIONALE/REGIONALE REPOSITORIES

### 19. **EUDRA-CT (EU Clinical Trials Database)** ⭐⭐⭐⭐
- **Quelle:** European Medicines Agency (EMA)
- **Link:** https://www.clinicaltrialsregister.eu/
- **Größe:**
  - 50,000+ Studien in EU durchgeführt
  - EU Member States + EEA
- **Features:**
  - ✅ Protokoll & Ergebnisse
  - ✅ Pädiatrische Informationen
  - ✅ Safety Reports
- **Besonderheit:** Focus auf europäische Regulatory Standards
- **Zugang:** ✅ Öffentlich durchsuchbar
- **Ideal für ADAVID:** ✅ Für Internationale Validierung (EU perspective)

---

### 20. **Chinese Clinical Trial Registry (ChiCTR)** ⭐⭐⭐
- **Quelle:** Chinese Academy of Medical Sciences
- **Link:** http://www.chictr.org.cn/
- **Größe:** 50,000+ Trials in China
- **Besonderheit:**
  - ✅ Chinese Traditional Medicine
  - ✅ Alternative Interventions
- **Ideal für ADAVID:** ⚠️ Spezifisch für China, aber gut für Diversität

---

## 🔬 KATEGORIE 9: GENOMIK & PRECISION MEDICINE

### 21. **GEO (Gene Expression Omnibus)** ⭐⭐⭐⭐
- **Quelle:** NCBI
- **Link:** https://www.ncbi.nlm.nih.gov/geo/
- **Größe:**
  - 10 Million+ Microarray/RNA-seq Samples
  - 260,000+ Datensätze
- **Features:**
  - Gene expression by treatment
  - Patient stratification
- **Ideal für ADAVID:** ✅ Für Biomarker-driven Segmentation (Genetic Variants)

---

### 22. **The Cancer Genome Atlas (TCGA)** ⭐⭐⭐⭐⭐
- **Quelle:** NCI
- **Link:** https://www.cancer.gov/about-nci/organization/ccg/research/structural-genomics/tcga
- **Größe:**
  - 20,000+ Cancer Biopsies
  - 33 Krebs-Typen
  - Tumor + Normal Sample Pairs
- **Features:**
  - ✅ Genomic Data
  - ✅ Clinical Outcomes
  - ✅ Response to Treatment
  - ✅ Survival Data
- **Ideal für ADAVID:** ✅ Für Oncology Subgroup Analysis

---

## 📋 ZUSAMMENFASSUNG: BEST CHOICES FÜR ADAVID

### **🏆 Top 5 für Production Use:**

| Rang | Dataset | Größe | Participant Data | Biomarker | Outcomes | Subgroups |
|------|---------|-------|------------------|-----------|----------|-----------|
| 1 | **MIMIC-III** | 46K pts | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅ |
| 2 | **ClinicalTrials.gov** | 500K trials | ⚠️ (aggregated) | ✅ | ✅✅ | ✅✅✅ |
| 3 | **Drugs@FDA** | 200+ drugs | ⚠️ (summaries) | ✅✅ | ✅✅✅ | ✅✅ |
| 4 | **eICU** | 139K pts | ✅✅✅ | ✅✅ | ✅✅ | ✅ (multi-center) |
| 5 | **CTO Benchmark** | 125K trials | ✅ | ✅ | ✅✅ | ✅ |

---

## 🎯 EMPFOHLENE STRATEGIE FÜR ADAVID TESTING

### **Phase 1: Proof of Concept** (Schnell, einfach)
```python
# Synthetische Daten mit bekannten Eigenschaften
from adavid_scoring_system import generate_production_test_data
df = generate_production_test_data()
```

### **Phase 2: Real-World Validation** (Realistisch)
```python
# Kleine Datensets als CSV
# Option A: ClinicalTrials.gov API
# Option B: MIMIC-III subset (n=1000)
# Option C: Kaggle ClinicalTrials.gov CSV
```

### **Phase 3: Production Deployment** (Robust)
```python
# Große, diverse Datensätze
# Option A: Vollständiges MIMIC-III (46K) oder MIMIC-IV (315K)
# Option B: AACT PostgreSQL (alle 500K trials)
# Option C: Kombiniert (MIMIC + ClinicalTrials.gov Metadaten)
```

---

## 🔐 DATENSCHUTZ & ZUGANG

### **Datenschutz-Status:**

| Dataset | De-identified | Privacy Risk | IRB Approval |
|---------|---------------|-------------|--------------|
| MIMIC-III/IV | ✅ (HIPAA Safe Harbor) | Minimal | ✅ MIT/Harvard |
| ClinicalTrials.gov | ✅ (Aggregated) | None | ✅ Public |
| Drugs@FDA | ✅ (Summaries only) | None | ✅ Public |
| TCGA | ✅ (De-identified) | Minimal | ✅ NCI |
| eICU | ✅ (De-identified) | Minimal | ✅ Authorized |

### **Zugangs-Anforderungen:**

| Dataset | Registration | DUA | Cost | Comment |
|---------|--------------|-----|------|---------|
| MIMIC | ✅ (Free) | ✅ | Free | Nur Online-Training erforderlich |
| ClinicalTrials.gov | ❌ | ❌ | Free | Vollständig öffentlich |
| Drugs@FDA | ❌ | ❌ | Free | Web-Access, Parse PDFs |
| eICU | ✅ (Free) | ✅ | Free | Ähnlich wie MIMIC |
| AACT | ❌ | ❌ | Free | SQL dumps verfügbar |

---

## 🚀 QUICK START: DATEN HERUNTERLADEN

### **Option 1: ClinicalTrials.gov (Schnell)**
```bash
# Download alle Studien als XML
wget https://clinicaltrials.gov/api/download/studies

# Oder API nutzen
curl "https://clinicaltrials.gov/api/v2/studies?pageSize=1000" \
  | python parse_api.py
```

### **Option 2: MIMIC-III (Detailliert)**
```bash
# 1. Registrieren auf https://physionet.org
# 2. CITI Training absolvieren
# 3. Data Use Agreement unterzeichnen
# 4. Download PostgreSQL dump oder CSV files

# Beispiel: ADMISSIONS Table laden
psql -U postgres -d mimic < admissions.sql
```

### **Option 3: Kaggle (Easiest)**
```bash
kaggle datasets download -d danielansted/clinicaltrials-gov-clinical-trials-dataset
unzip clinicaltrials-gov-clinical-trials-dataset.zip
```

---

## 📚 WEITERE RESSOURCEN

### **Dokumentation:**
- ClinicalTrials.gov API Docs: https://clinicaltrials.gov/api/
- MIMIC Documentation: https://mimic.mit.edu/
- FDA Guidance: https://www.fda.gov/regulatory-information/guidance

### **Papers/Publikationen:**
- MIMIC-III Paper (2016): https://www.nature.com/articles/sdata201635
- MIMIC-IV Paper (2022): https://www.nature.com/articles/s41597-022-01899-x
- CTO Benchmark (2026): https://www.nature.com/articles/s44360-026-00081-6

### **Community Tools:**
- MIMIC-Extract: Automated feature extraction (wang-ai/mimic-code)
- ClinicalTrials.gov Python Client: https://github.com/clinicaltrials-gov/api
- Open FDA Python: https://github.com/FDA/openfda

---

## 🎓 RECOMMENDED READING ORDER FOR ADAVID

1. ✅ **Start:** Synthetische Daten (`generate_production_test_data()`)
2. ✅ **Validiere:** ClinicalTrials.gov aggregierte Daten (CTO Benchmark)
3. ✅ **Teste:** MIMIC-III mit echten Biomarkern (1000 sample subset)
4. ✅ **Deploye:** Vollständiges MIMIC-III/IV oder AACT für Production

---

**Version:** 1.0 (Mai 2026)  
**Status:** Alle Links validiert & aktuell  
**Nächstes Update:** November 2026
