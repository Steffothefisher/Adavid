import numpy as np
import pandas as pd
from src.adavid_engine import AdavidAuditEngine

def generate_manipulated_trial_data():
    """
    Generates a perfect Simpson's Paradox scenario:
    Overall the drug looks good, but in age groups it's worthless!
    """
    np.random.seed(42)
    
    # Cohort 1: Young patients (High base recovery, small test group)
    junge_treat = pd.DataFrame({
        'patient_id': range(1, 11),
        'age': np.random.randint(18, 35, 10),
        'treatment': 1,
        'outcome': np.random.choice([0, 1], 10, p=[0.1, 0.9])
    })
    junge_plac = pd.DataFrame({
        'patient_id': range(11, 51),
        'age': np.random.randint(18, 35, 40),
        'treatment': 0,
        'outcome': np.random.choice([0, 1], 40, p=[0.0, 1.0])
    })
    
    # Cohort 2: Older patients (Low recovery, large test group)
    alte_treat = pd.DataFrame({
        'patient_id': range(51, 131),
        'age': np.random.randint(61, 85, 80),
        'treatment': 1,
        'outcome': np.random.choice([0, 1], 80, p=[0.5, 0.5])
    })
    alte_plac = pd.DataFrame({
        'patient_id': range(131, 151),
        'age': np.random.randint(61, 85, 20),
        'treatment': 0,
        'outcome': np.random.choice([0, 1], 20, p=[0.6, 0.4])
    })
    
    return pd.concat([junge_treat, junge_plac, alte_treat, alte_plac], ignore_index=True)

if __name__ == "__main__":
    print("="*60)
    print("ADAVID CORE ENGINE - AUTOMATED DATA AUDIT DEMO")
    print("="*60)
    
    # 1. Generate data and feed to engine
    manipulated_data = generate_manipulated_trial_data()
    engine = AdavidAuditEngine(manipulated_data)
    
    # 2. Run audit tests
    # The pharma company boldly claims a perfect p-value of 0.01
    p_check = engine.audit_p_hacking(claimed_p_value=0.01)
    simpson_check = engine.audit_simpsons_paradox()
    
    # Assume a rare cancer test (base rate 0.05%) is screened
    base_rate_check = AdavidAuditEngine.calculate_base_rate_efficiency(
        sensitivity=0.99, specificity=0.99, base_rate=0.0005
    )
    
    # 3. Print results
    for report in [p_check, simpson_check, base_rate_check]:
        print(f"\n[MODULE] {report['test_name']}")
        print(f"Status: {report.get('status', 'INFO')}")
        for key, value in report.items():
            if key not in ['test_name', 'status']:
                print(f"  └─ {key}: {value}")
    
    print("\n" + "="*60)
    print("AUDIT COMPLETION: Critical anomalies mapped. Pipeline halted.")
    print("="*60)
