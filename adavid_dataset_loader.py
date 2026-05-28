#!/usr/bin/env python3
"""
ADAVID Dataset Loader & Processor
Utility für automatisches Herunterladen und Laden von öffentlichen klinischen Datensätzen

Usage:
    python adavid_dataset_loader.py --source clinicaltrials --format csv
    python adavid_dataset_loader.py --source mimic --sample-size 1000
"""

import os
import json
import urllib.request
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================================
# DATASET SOURCES ENUM & CONFIGURATION
# =====================================================================

class DatasetSource(Enum):
    """Verfügbare öffentliche Datensätze"""
    MIMIC_III = "mimic_iii"
    MIMIC_IV = "mimic_iv"
    CLINICALTRIALS_GOV = "clinicaltrials_gov"
    AACT = "aact"
    CTO_BENCHMARK = "cto_benchmark"
    KAGGLE = "kaggle"
    SYNTHETIC = "synthetic"

DATASET_CONFIG = {
    DatasetSource.MIMIC_III: {
        'name': 'MIMIC-III (Beth Israel, 2001-2012)',
        'size': '46,520 unique patients',
        'url': 'https://physionet.org/content/mimiciii/1.4/',
        'access': 'Data Use Agreement required',
        'registration': True,
        'format': ['PostgreSQL', 'CSV'],
        'fields': ['vital_signs', 'labs', 'medications', 'diagnoses', 'outcomes'],
        'biomarkers': ['lactate', 'potassium', 'sodium', 'hemoglobin', 'creatinine'],
    },
    
    DatasetSource.MIMIC_IV: {
        'name': 'MIMIC-IV (Beth Israel, 2008-2019)',
        'size': '315,460 unique patients',
        'url': 'https://physionet.org/content/mimiciv/3.1/',
        'access': 'Data Use Agreement required',
        'registration': True,
        'format': ['PostgreSQL', 'Parquet', 'CSV'],
        'fields': ['vital_signs', 'labs', 'medications', 'diagnoses', 'outcomes'],
        'biomarkers': ['lactate', 'potassium', 'sodium', 'hemoglobin', 'creatinine'],
    },
    
    DatasetSource.CLINICALTRIALS_GOV: {
        'name': 'ClinicalTrials.gov (500K+ trials)',
        'size': '500,000+ registered trials',
        'url': 'https://clinicaltrials.gov/api/v2/',
        'access': 'Public, API available',
        'registration': False,
        'format': ['JSON (API)', 'XML'],
        'fields': ['enrollment', 'outcomes', 'demographics', 'study_type', 'status'],
        'biomarkers': ['primary_outcome', 'secondary_outcomes'],
    },
    
    DatasetSource.AACT: {
        'name': 'AACT (ClinicalTrials.gov in PostgreSQL)',
        'size': '500K trials, structured',
        'url': 'https://aact.ctti-clinicaltrials.org/',
        'access': 'Public, free downloads',
        'registration': False,
        'format': ['PostgreSQL', 'CSV'],
        'fields': ['studies', 'results', 'outcomes', 'participants'],
        'biomarkers': ['outcome_measures'],
    },
    
    DatasetSource.CTO_BENCHMARK: {
        'name': 'Clinical Trial Outcome Benchmark (Nature)',
        'size': '125,000 drug trials',
        'url': 'https://www.nature.com/articles/s44360-026-00081-6',
        'access': 'Research access',
        'registration': False,
        'format': ['CSV', 'JSON'],
        'fields': ['drug_name', 'phase', 'outcome', 'success', 'demographics'],
        'biomarkers': ['efficacy_measure'],
    },
    
    DatasetSource.KAGGLE: {
        'name': 'Kaggle: ClinicalTrials.gov Dataset',
        'size': '400K trials',
        'url': 'https://www.kaggle.com/datasets/danielansted/clinicaltrials-gov-clinical-trials-dataset',
        'access': 'Public, Kaggle account needed',
        'registration': True,
        'format': ['CSV', 'Parquet'],
        'fields': ['trial_metadata', 'outcomes'],
        'biomarkers': ['endpoints'],
    },
    
    DatasetSource.SYNTHETIC: {
        'name': 'Synthetic Data (ADAVID Generated)',
        'size': 'Configurable (default 500)',
        'url': 'Local generation',
        'access': 'Instant',
        'registration': False,
        'format': ['DataFrame', 'CSV'],
        'fields': ['all_adavid_fields'],
        'biomarkers': ['Biomarker_Drop'],
    }
}

# =====================================================================
# CLINICALTRIALS.GOV API CLIENT
# =====================================================================

class ClinicalTrialsClient:
    """Client für ClinicalTrials.gov API v2"""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    
    def __init__(self):
        self.session = urllib.request.urlopen
    
    @staticmethod
    def fetch_trials(
        query: str = "",
        page_size: int = 100,
        max_trials: int = 1000,
        condition: Optional[str] = None,
        recruitment_status: Optional[str] = None,
    ) -> List[Dict]:
        """
        Hole Studiendaten von ClinicalTrials.gov API
        
        Args:
            query: Suchbegriff (z.B. "cancer drug efficacy")
            page_size: Studien pro Seite (max 100)
            max_trials: Maximale Anzahl der heruntergeladenen Studien
            condition: Filter nach Indikation (z.B. "Cancer")
            recruitment_status: Filter nach Status (RECRUITING, ACTIVE, COMPLETED, etc.)
        
        Returns:
            Liste von Studien (JSON parsed)
        """
        logger.info(f"🔍 Fetching trials from ClinicalTrials.gov (max {max_trials})...")
        
        trials = []
        page = 1
        total_fetched = 0
        
        while total_fetched < max_trials:
            # Build URL
            url = f"{ClinicalTrialsClient.BASE_URL}/studies"
            params = f"pageSize={page_size}&pageNumber={page}"
            
            if query:
                params += f"&query={query.replace(' ', '+')}"
            if condition:
                params += f"&condition={condition.replace(' ', '+')}"
            if recruitment_status:
                params += f"&recruitmentStatus={recruitment_status}"
            
            full_url = f"{url}?{params}"
            
            try:
                logger.debug(f"Requesting page {page}: {full_url}")
                response = urllib.request.urlopen(full_url, timeout=10)
                data = json.loads(response.read().decode('utf-8'))
                
                if 'studies' not in data:
                    logger.warning("Keine 'studies' in Antwort gefunden")
                    break
                
                studies = data['studies']
                trials.extend(studies)
                total_fetched += len(studies)
                
                logger.info(f"  ✓ Page {page}: {len(studies)} trials (total: {total_fetched})")
                
                # Check if more pages available
                if len(studies) < page_size:
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"❌ Fehler beim Abrufen von Seite {page}: {e}")
                break
        
        logger.info(f"✅ Total {total_fetched} trials fetched")
        return trials
    
    @staticmethod
    def parse_trial_outcomes(trial: Dict) -> Dict:
        """Extrahiere Outcome-Daten aus Trial-JSON"""
        outcome_data = {
            'nct_id': trial.get('protocolSection', {}).get('identificationModule', {}).get('nctId'),
            'title': trial.get('protocolSection', {}).get('identificationModule', {}).get('officialTitle'),
            'enrollment': trial.get('protocolSection', {}).get('designModule', {}).get('enrollmentInfo', {}).get('count'),
            'status': trial.get('protocolSection', {}).get('statusModule', {}).get('overallStatus'),
            'primary_outcomes': [],
        }
        
        # Parse outcomes
        outcomes_module = trial.get('resultsSection', {}).get('outcomesModule', {})
        if outcomes_module:
            for outcome in outcomes_module.get('primaryOutcomes', []):
                outcome_data['primary_outcomes'].append({
                    'measure': outcome.get('measure'),
                    'description': outcome.get('description'),
                    'time_frame': outcome.get('timeFrame'),
                })
        
        return outcome_data

# =====================================================================
# SYNTHETIC DATA GENERATOR
# =====================================================================

def generate_synthetic_trial_data(
    n_records: int = 500,
    include_paradox: bool = False,
    paradox_severity: float = 0.3
) -> pd.DataFrame:
    """
    Generiere synthetische Klinische Trial-Daten (ADAVID-kompatibel)
    
    Args:
        n_records: Anzahl der Patienten
        include_paradox: Ob Simpson's Paradox eingebaut sein soll
        paradox_severity: Stärke des Paradox (0.0-1.0)
    
    Returns:
        pandas DataFrame mit trial data
    """
    logger.info(f"🔧 Generiere synthetische Daten (n={n_records}, paradox={include_paradox})...")
    
    np.random.seed(42)
    
    data = {
        'Patient_ID': [f"PAT_{i:04d}" for i in range(n_records)],
        'Group': np.random.choice(['Control', 'Treatment'], size=n_records),
        'Age': np.random.choice([25, 34, 45, 67, 72, 81, None], size=n_records, p=[0.15, 0.2, 0.2, 0.2, 0.15, 0.08, 0.02]),
        'Gender': np.random.choice(['M', 'F', 'O'], size=n_records),
        'Comorbidities_Count': np.random.choice([0, 1, 2, 3, 4], size=n_records, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
        'Genetic_Variant_X': np.random.choice([True, False], size=n_records, p=[0.3, 0.7]),
    }
    
    df = pd.DataFrame(data)
    
    # Generate biomarker response
    if not include_paradox:
        # Simple positive effect across all groups
        df['Biomarker_Drop'] = np.where(
            df['Group'] == 'Treatment',
            np.random.normal(loc=14, scale=3.5, size=n_records),  # Better response
            np.random.normal(loc=10, scale=4.0, size=n_records)   # Control
        )
    else:
        # Simpson's Paradox: Global positive, but negative in subgroups
        df['Biomarker_Drop'] = 0.0
        
        for idx in df.index:
            if df.loc[idx, 'Group'] == 'Treatment':
                # Base improvement
                base_effect = 3.5 + np.random.normal(0, 1)
                
                # Subgroup penalty (Simpson's Paradox)
                if df.loc[idx, 'Age'] in [25, 34] and df.loc[idx, 'Genetic_Variant_X'] == False:
                    # Young, non-carriers: drug doesn't work (or harms)
                    base_effect *= -(1 - paradox_severity)
                
                df.loc[idx, 'Biomarker_Drop'] = 12 + base_effect + np.random.normal(0, 1.5)
            else:
                df.loc[idx, 'Biomarker_Drop'] = 10 + np.random.normal(0, 2)
    
    logger.info(f"✅ Synthetic data generated: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

# =====================================================================
# DATA LOADER FACADE
# =====================================================================

class ADDatasetLoader:
    """Hauptklasse für Datenladen"""
    
    def __init__(self, cache_dir: str = "./data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.data = None
    
    def list_available_datasets(self) -> Dict:
        """Zeige alle verfügbaren Datensätze"""
        print("\n" + "="*80)
        print("AVAILABLE PUBLIC DATASETS FOR ADAVID")
        print("="*80 + "\n")
        
        for source, config in DATASET_CONFIG.items():
            print(f"📊 {source.value.upper()}")
            print(f"   Name: {config['name']}")
            print(f"   Size: {config['size']}")
            print(f"   URL: {config['url']}")
            print(f"   Registration Required: {'✅ Yes' if config['registration'] else '❌ No'}")
            print(f"   Formats: {', '.join(config['format'])}")
            print()
        
        return DATASET_CONFIG
    
    def load_clinicaltrials(
        self,
        query: str = "cancer drug efficacy",
        max_trials: int = 500
    ) -> pd.DataFrame:
        """Lade Daten von ClinicalTrials.gov"""
        logger.info(f"📥 Loading from ClinicalTrials.gov...")
        
        client = ClinicalTrialsClient()
        trials = client.fetch_trials(query=query, max_trials=max_trials)
        
        # Parse zu DataFrame
        data_list = []
        for trial in trials:
            parsed = client.parse_trial_outcomes(trial)
            data_list.append(parsed)
        
        df = pd.DataFrame(data_list)
        logger.info(f"✅ Loaded {len(df)} trials from ClinicalTrials.gov")
        
        self.data = df
        return df
    
    def load_synthetic(
        self,
        n_records: int = 500,
        include_paradox: bool = False
    ) -> pd.DataFrame:
        """Lade synthetische ADAVID-kompatible Daten"""
        self.data = generate_synthetic_trial_data(n_records, include_paradox)
        return self.data
    
    def load_kaggle(self, kaggle_dataset: str = "danielansted/clinicaltrials-gov-clinical-trials-dataset"):
        """
        Lade Daten von Kaggle (benötigt Kaggle API konfiguriert)
        """
        try:
            import kaggle
            logger.info(f"📥 Downloading {kaggle_dataset} from Kaggle...")
            
            # Download dataset
            kaggle.api.dataset_download_files(kaggle_dataset, path=self.cache_dir, unzip=True)
            
            # Find CSV files
            csv_files = list(self.cache_dir.glob("*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
                logger.info(f"✅ Loaded {len(df)} rows from Kaggle")
                self.data = df
                return df
            else:
                logger.error("❌ No CSV files found in downloaded data")
                return None
        except ImportError:
            logger.error("❌ kaggle package not installed. Install with: pip install kaggle")
            return None
    
    def save_to_csv(self, filename: str = "clinical_data.csv"):
        """Speichere geladen Daten als CSV"""
        if self.data is None:
            logger.error("❌ No data loaded")
            return
        
        filepath = self.cache_dir / filename
        self.data.to_csv(filepath, index=False)
        logger.info(f"✅ Saved {len(self.data)} rows to {filepath}")
        return filepath
    
    def get_data_summary(self) -> Dict:
        """Gebe Zusammenfassung der geladenen Daten"""
        if self.data is None:
            return {'error': 'No data loaded'}
        
        return {
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'column_names': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1e6,
            'null_counts': self.data.isnull().sum().to_dict(),
        }

# =====================================================================
# COMMAND-LINE INTERFACE
# =====================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ADAVID Dataset Loader Utility')
    parser.add_argument('--list', action='store_true', help='Liste alle verfügbaren Datensätze')
    parser.add_argument('--source', choices=['synthetic', 'clinicaltrials', 'kaggle'], 
                       default='synthetic', help='Datensatz-Quelle')
    parser.add_argument('--n-records', type=int, default=500, help='Anzahl der Datensätze (synthetic only)')
    parser.add_argument('--paradox', action='store_true', help='Simpson\'s Paradox in synthetischen Daten einbauen')
    parser.add_argument('--max-trials', type=int, default=500, help='Max trials (ClinicalTrials.gov)')
    parser.add_argument('--save', action='store_true', help='Daten als CSV speichern')
    parser.add_argument('--info', action='store_true', help='Dateninfos anzeigen')
    
    args = parser.parse_args()
    
    loader = ADDatasetLoader()
    
    if args.list:
        loader.list_available_datasets()
    
    elif args.source == 'synthetic':
        logger.info("Loading SYNTHETIC data...")
        df = loader.load_synthetic(args.n_records, args.paradox)
        
    elif args.source == 'clinicaltrials':
        logger.info("Loading ClinicalTrials.gov data...")
        df = loader.load_clinicaltrials(max_trials=args.max_trials)
        
    elif args.source == 'kaggle':
        logger.info("Loading Kaggle data...")
        df = loader.load_kaggle()
    
    # Output information
    if args.info and loader.data is not None:
        print("\n" + "="*80)
        print("DATA SUMMARY")
        print("="*80)
        summary = loader.get_data_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
        print("\nFirst 5 rows:")
        print(loader.data.head())
    
    # Save if requested
    if args.save and loader.data is not None:
        loader.save_to_csv()
    
    logger.info("✅ Done!")
