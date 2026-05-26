import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk classification for audit results"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditStatus(Enum):
    """Audit pass/fail status"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


@dataclass
class AuditConfig:
    """Configuration for audit parameters"""
    p_value_threshold: float = 0.05
    p_value_deviation_tolerance: float = 0.01
    min_sample_size: int = 30
    ppv_threshold: float = 0.10
    max_acceptable_fatality_increase: float = 0.02
    age_bins: List[int] = field(default_factory=lambda: [0, 35, 60, 100])
    age_labels: List[str] = field(default_factory=lambda: ['Jung', 'Mittel', 'Alt'])


class AdavidAuditEngine:
    """
    ADAVID Audit Engine for detecting statistical fraud and safety issues in clinical trials.
    
    Detects:
    - Level 1: p-hacking and data integrity issues
    - Level 2: Simpson's Paradox in subgroup analyses
    - Level 3: Base rate fallacies in diagnostic tests
    - Level 4: Fatality rates and hidden toxicity
    
    Expected DataFrame columns:
        - patient_id: Unique patient identifier
        - age: Patient age (numeric)
        - gender: Patient gender (optional)
        - treatment: Treatment group (0=Placebo, 1=Treatment)
        - outcome: Primary outcome (0=Failure, 1=Success)
        - fatality: Fatality indicator (0=Survived, 1=Fatal) (optional)
    """
    
    def __init__(self, trial_data: pd.DataFrame, config: Optional[AuditConfig] = None):
        """
        Initialize ADAVID Audit Engine with clinical trial data.
        
        Args:
            trial_data: DataFrame containing patient trial data
            config: AuditConfig object with audit parameters
            
        Raises:
            TypeError: If trial_data is not a DataFrame
            ValueError: If required columns are missing or data is invalid
        """
        self.config = config or AuditConfig()
        self._validate_input_data(trial_data)
        self.data = trial_data.copy()
        logger.info(f"Initialized ADAVID with {len(self.data)} patient records")
    
    def _validate_input_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data integrity.
        
        Raises:
            TypeError: If input is not a DataFrame
            ValueError: If required columns missing, data types invalid, or data is malformed
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pd.DataFrame, got {type(df)}")
        
        required_columns = {'patient_id', 'age', 'treatment', 'outcome'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for duplicates
        if df['patient_id'].duplicated().any():
            logger.warning("Duplicate patient IDs detected")
        
        # Validate data types and ranges
        if not pd.api.types.is_numeric_dtype(df['age']):
            raise ValueError("'age' column must be numeric")
        if not pd.api.types.is_numeric_dtype(df['treatment']):
            raise ValueError("'treatment' column must be numeric")
        if not pd.api.types.is_numeric_dtype(df['outcome']):
            raise ValueError("'outcome' column must be numeric")
        
        # Check value ranges
        if not df['age'].between(0, 150).all():
            raise ValueError("Age values outside valid range [0, 150]")
        if not df['treatment'].isin([0, 1]).all():
            raise ValueError("'treatment' must be binary (0 or 1)")
        if not df['outcome'].isin([0, 1]).all():
            raise ValueError("'outcome' must be binary (0 or 1)")
        
        # Check for excessive missing data
        missing_pct = df.isnull().sum() / len(df)
        if (missing_pct > 0.05).any():
            logger.warning(f"Columns with >5% missing data:\n{missing_pct[missing_pct > 0.05]}")
    
    def audit_p_hacking(self, claimed_p_value: float) -> Dict:
        """
        Level 1: Anti-p-Hacking Suite.
        Detects data integrity issues and p-hacking by comparing claimed vs. actual p-values.
        
        Args:
            claimed_p_value: The p-value reported in the study
            
        Returns:
            Dictionary with audit results
            
        Raises:
            ValueError: If claimed_p_value is not in valid range [0, 1]
        """
        if not 0 <= claimed_p_value <= 1:
            raise ValueError(f"p-value must be in [0, 1], got {claimed_p_value}")
        
        treatment_group = self.data[self.data['treatment'] == 1]['outcome'].dropna()
        placebo_group = self.data[self.data['treatment'] == 0]['outcome'].dropna()
        
        # Check minimum sample sizes
        if len(treatment_group) < self.config.min_sample_size or len(placebo_group) < self.config.min_sample_size:
            logger.warning(f"Small sample sizes detected: treatment={len(treatment_group)}, placebo={len(placebo_group)}")
        
        try:
            t_stat, actual_p = stats.ttest_ind(treatment_group, placebo_group)
        except Exception as e:
            logger.error(f"T-test failed: {e}")
            return {
                "test_name": "Data Integrity & p-Hacking Check",
                "status": AuditStatus.FAIL.value,
                "error": str(e),
                "anomaly_detected": True
            }
        
        # Anomaly detection with configurable thresholds
        p_value_mismatch = abs(actual_p - claimed_p_value) > self.config.p_value_deviation_tolerance
        p_value_invalid = actual_p > self.config.p_value_threshold
        anomaly_detected = p_value_mismatch or p_value_invalid
        
        status = AuditStatus.FAIL if anomaly_detected else AuditStatus.PASS
        
        return {
            "test_name": "Data Integrity & p-Hacking Check",
            "claimed_p_value": claimed_p_value,
            "actual_p_value": round(actual_p, 4),
            "t_statistic": round(t_stat, 4),
            "treatment_n": len(treatment_group),
            "placebo_n": len(placebo_group),
            "p_value_deviation": round(abs(actual_p - claimed_p_value), 4),
            "anomaly_detected": anomaly_detected,
            "status": status.value,
            "details": {
                "p_value_mismatch": p_value_mismatch,
                "statistical_significance_issue": p_value_invalid
            }
        }
    
    def audit_simpsons_paradox(self) -> Dict:
        """
        Level 2: Simpson's Paradox Micro-Segmentation Engine.
        Detects trend reversals in subgroup analyses.
        
        Returns:
            Dictionary with paradox detection results and cohort breakdowns
        """
        # Calculate overall effect
        overall_treatment_success = self.data[self.data['treatment'] == 1]['outcome'].mean()
        overall_placebo_success = self.data[self.data['treatment'] == 0]['outcome'].mean()
        overall_positive = overall_treatment_success > overall_placebo_success
        
        # Create age cohorts
        try:
            self.data['age_group'] = pd.cut(
                self.data['age'],
                bins=self.config.age_bins,
                labels=self.config.age_labels,
                include_lowest=True
            )
        except Exception as e:
            logger.error(f"Failed to create age groups: {e}")
            return {
                "test_name": "Simpson's Paradox Micro-Segmentation",
                "status": AuditStatus.FAIL.value,
                "error": str(e)
            }
        
        paradox_detected = False
        cohort_results = {}
        empty_cohorts = []
        
        for cohort_name, cohort_data in self.data.groupby('age_group', observed=True):
            treatment_data = cohort_data[cohort_data['treatment'] == 1]['outcome']
            placebo_data = cohort_data[cohort_data['treatment'] == 0]['outcome']
            
            # Handle empty cohorts
            if len(treatment_data) == 0 or len(placebo_data) == 0:
                empty_cohorts.append(str(cohort_name))
                continue
            
            treat_succ = treatment_data.mean()
            plac_succ = placebo_data.mean()
            cohort_positive = treat_succ > plac_succ
            
            # Detect trend reversal
            if cohort_positive != overall_positive:
                paradox_detected = True
                logger.warning(f"Simpson's Paradox detected in cohort '{cohort_name}'")
            
            cohort_results[str(cohort_name)] = {
                "n_treatment": len(treatment_data),
                "n_placebo": len(placebo_data),
                "treatment_success_rate": round(treat_succ, 4),
                "placebo_success_rate": round(plac_succ, 4),
                "effect_size": round(treat_succ - plac_succ, 4),
                "cohort_trend_matches_overall": cohort_positive == overall_positive
            }
        
        if empty_cohorts:
            logger.warning(f"Empty cohorts detected: {empty_cohorts}")
        
        status = AuditStatus.FAIL if paradox_detected else AuditStatus.PASS
        
        return {
            "test_name": "Simpson's Paradox Micro-Segmentation",
            "overall_treatment_success": round(overall_treatment_success, 4),
            "overall_placebo_success": round(overall_placebo_success, 4),
            "overall_trend_positive": overall_positive,
            "simpsons_paradox_detected": paradox_detected,
            "cohort_metrics": cohort_results,
            "empty_cohorts": empty_cohorts,
            "status": status.value
        }
    
    def audit_fatality_rates(self, max_acceptable_fatality_increase: Optional[float] = None) -> Dict:
        """
        Level 4: Fatality Rate & Hidden Toxicity Audit.
        Detects critical safety issues by analyzing fatality rates globally and by cohort.
        
        Args:
            max_acceptable_fatality_increase: Maximum acceptable fatality increase (default from config)
            
        Returns:
            Dictionary with fatality analysis results
        """
        if max_acceptable_fatality_increase is None:
            max_acceptable_fatality_increase = self.config.max_acceptable_fatality_increase
        
        # Check if fatality column exists
        if 'fatality' not in self.data.columns:
            logger.warning("Fatality column not present in data. Skipping fatality audit.")
            return {
                "test_name": "Fatality Rate & Hidden Toxicity Audit",
                "status": AuditStatus.WARNING.value,
                "message": "Fatality column not found in data"
            }
        
        # Create age cohorts if not already present
        if 'age_group' not in self.data.columns:
            try:
                self.data['age_group'] = pd.cut(
                    self.data['age'],
                    bins=self.config.age_bins,
                    labels=self.config.age_labels,
                    include_lowest=True
                )
            except Exception as e:
                logger.error(f"Failed to create age groups: {e}")
                return {
                    "test_name": "Fatality Rate & Hidden Toxicity Audit",
                    "status": AuditStatus.FAIL.value,
                    "error": str(e)
                }
        
        # Calculate global fatality rates
        treatment_data = self.data[self.data['treatment'] == 1]['fatality'].dropna()
        placebo_data = self.data[self.data['treatment'] == 0]['fatality'].dropna()
        
        if len(treatment_data) == 0 or len(placebo_data) == 0:
            logger.warning("Insufficient fatality data for analysis")
            return {
                "test_name": "Fatality Rate & Hidden Toxicity Audit",
                "status": AuditStatus.WARNING.value,
                "message": "Insufficient fatality data"
            }
        
        fatality_treatment = treatment_data.mean()
        fatality_placebo = placebo_data.mean()
        global_delta = fatality_treatment - fatality_placebo
        
        critical_toxicity_detected = global_delta > max_acceptable_fatality_increase
        cohort_alerts = {}
        
        # Cohort-specific fatality analysis
        for cohort_name, cohort_data in self.data.groupby('age_group', observed=True):
            treat_fatal = cohort_data[cohort_data['treatment'] == 1]['fatality'].dropna()
            plac_fatal = cohort_data[cohort_data['treatment'] == 0]['fatality'].dropna()
            
            if len(treat_fatal) == 0 or len(plac_fatal) == 0:
                continue
            
            f_treat = treat_fatal.mean()
            f_plac = plac_fatal.mean()
            cohort_delta = f_treat - f_plac
            
            if cohort_delta > max_acceptable_fatality_increase:
                critical_toxicity_detected = True
                cohort_alerts[str(cohort_name)] = {
                    "alert": "CRITICAL TOXICITY SPIKE",
                    "treatment_fatality": round(f_treat, 4),
                    "placebo_fatality": round(f_plac, 4),
                    "delta": round(cohort_delta, 4),
                    "n_treatment": len(treat_fatal),
                    "n_placebo": len(plac_fatal)
                }
                logger.critical(f"Critical toxicity spike detected in cohort '{cohort_name}': delta={cohort_delta:.4f}")
        
        status = AuditStatus.FAIL if critical_toxicity_detected else AuditStatus.PASS
        
        return {
            "test_name": "Fatality Rate & Hidden Toxicity Audit",
            "global_treatment_fatality": round(fatality_treatment, 4),
            "global_placebo_fatality": round(fatality_placebo, 4),
            "global_delta": round(global_delta, 4),
            "treatment_n": len(treatment_data),
            "placebo_n": len(placebo_data),
            "critical_toxicity_detected": critical_toxicity_detected,
            "cohort_specific_failures": cohort_alerts,
            "status": status.value
        }
    
    @staticmethod
    def calculate_base_rate_efficiency(
        sensitivity: float,
        specificity: float,
        base_rate: float
    ) -> Dict:
        """
        Level 3: Base Rate Fallacy Calculator.
        Computes actual Positive Predictive Value (PPV) using Bayes' theorem.
        
        Args:
            sensitivity: True Positive Rate (0-1)
            specificity: True Negative Rate (0-1)
            base_rate: Disease prevalence in population (0-1)
            
        Returns:
            Dictionary with PPV calculation and risk assessment
            
        Raises:
            ValueError: If parameters are not in valid ranges
        """
        # Validate inputs
        for param_name, param_value in [('sensitivity', sensitivity), 
                                        ('specificity', specificity), 
                                        ('base_rate', base_rate)]:
            if not 0 <= param_value <= 1:
                raise ValueError(f"{param_name} must be in [0, 1], got {param_value}")
        
        # Calculate PPV using Bayes' theorem
        true_positives = sensitivity * base_rate
        false_positives = (1 - specificity) * (1 - base_rate)
        denominator = true_positives + false_positives
        
        # Handle edge case: division by zero
        if denominator == 0:
            logger.warning("PPV is undefined: no predicted positive cases")
            actual_ppv = 0.0
            risk_level = RiskLevel.CRITICAL.value
        else:
            actual_ppv = true_positives / denominator
            
            # Classify risk based on configurable threshold
            if actual_ppv < 0.05:
                risk_level = RiskLevel.CRITICAL.value
            elif actual_ppv < 0.10:
                risk_level = RiskLevel.HIGH.value
            elif actual_ppv < 0.50:
                risk_level = RiskLevel.MEDIUM.value
            else:
                risk_level = RiskLevel.LOW.value
        
        return {
            "test_name": "Base Rate Fallacy Assessment",
            "input_sensitivity": sensitivity,
            "input_specificity": specificity,
            "population_base_rate": base_rate,
            "true_positive_rate": round(true_positives, 4),
            "false_positive_rate": round(false_positives, 4),
            "actual_positive_predictive_value": round(actual_ppv, 4),
            "risk_level": risk_level,
            "interpretation": f"With a test sensitivity of {sensitivity:.1%} and specificity of {specificity:.1%}, "
                            f"the actual probability of disease given a positive test is {actual_ppv:.1%} "
                            f"(base rate: {base_rate:.1%})"
        }
    
    def run_full_audit(self, claimed_p_value: float) -> Dict:
        """
        Run all four audit levels in sequence.
        
        Args:
            claimed_p_value: The p-value reported in the study
            
        Returns:
            Dictionary containing all audit results
        """
        logger.info("Starting full audit suite...")
        
        audit_results = {
            "audit_timestamp": pd.Timestamp.now().isoformat(),
            "total_patients": len(self.data),
            "level_1_p_hacking": self.audit_p_hacking(claimed_p_value),
            "level_2_simpsons": self.audit_simpsons_paradox(),
            "level_4_fatality": self.audit_fatality_rates()
        }
        
        # Determine overall status
        all_pass = all(
            result.get("status") == AuditStatus.PASS.value 
            for result in [
                audit_results["level_1_p_hacking"],
                audit_results["level_2_simpsons"],
                audit_results["level_4_fatality"]
            ]
        )
        
        audit_results["overall_status"] = AuditStatus.PASS.value if all_pass else AuditStatus.FAIL.value
        
        logger.info(f"Audit complete. Overall status: {audit_results['overall_status']}")
        return audit_results
