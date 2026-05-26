# ADAVID - Clinical Trial Audit Engine

**ADAVID** is a comprehensive statistical audit framework for detecting fraud and methodological issues in clinical trials.

## Features

ADAVID detects three critical classes of statistical anomalies:

### Level 1: Anti-p-Hacking Suite
- Compares claimed vs. actual p-values
- Detects data integrity violations
- Identifies potential selective reporting

### Level 2: Simpson's Paradox Detection
- Analyzes trend reversals in subgroup analyses
- Performs micro-segmentation by patient cohorts
- Flags contradictory findings across demographic groups

### Level 3: Base Rate Fallacy Assessment
- Calculates actual Positive Predictive Values (PPV)
- Applies Bayes' theorem for diagnostic accuracy
- Assesses real-world test performance

## Installation

```bash
git clone https://github.com/Steffothefisher/Adavid.git
cd Adavid
pip install -r requirements.txt
```

## Quick Start

```python
import pandas as pd
from src.adavid_engine import AdavidAuditEngine, AuditConfig

# Load your clinical trial data
trial_data = pd.read_csv('trial_data.csv')

# Create audit engine with custom config
config = AuditConfig(
    p_value_threshold=0.05,
    p_value_deviation_tolerance=0.01,
    min_sample_size=30
)

engine = AdavidAuditEngine(trial_data, config=config)

# Run full audit
results = engine.run_full_audit(claimed_p_value=0.032)
print(results)
```

## Data Requirements

Your trial data must contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string/int | Unique patient identifier |
| `age` | numeric | Patient age (0-150) |
| `treatment` | binary (0/1) | 0=Placebo, 1=Treatment |
| `outcome` | binary (0/1) | 0=Failure, 1=Success |
| `gender` | string | (Optional) Patient gender |

## API Documentation

### AdavidAuditEngine

#### `__init__(trial_data, config=None)`
Initialize the audit engine with clinical trial data.

#### `audit_p_hacking(claimed_p_value)`
Level 1 audit: Detect p-hacking and data integrity issues.

#### `audit_simpsons_paradox()`
Level 2 audit: Detect Simpson's Paradox in subgroup analyses.

#### `calculate_base_rate_efficiency(sensitivity, specificity, base_rate)` [Static]
Level 3 audit: Calculate actual PPV and assess diagnostic accuracy.

#### `run_full_audit(claimed_p_value)`
Run all three audit levels and return comprehensive results.

## Output Format

All audit methods return structured dictionaries with:
- `test_name`: Name of the audit
- `status`: PASS, FAIL, or WARNING
- `anomaly_detected`: Boolean flag
- Additional test-specific metrics and details

## Configuration

Customize audit behavior via `AuditConfig`:

```python
config = AuditConfig(
    p_value_threshold=0.05,                    # Statistical significance level
    p_value_deviation_tolerance=0.01,          # Allowed p-value mismatch
    min_sample_size=30,                        # Minimum per-group sample size
    ppv_threshold=0.10,                        # Base rate fallacy threshold
    age_bins=[0, 35, 60, 100],                 # Age cohort boundaries
    age_labels=['Young', 'Middle', 'Senior']   # Cohort labels
)
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

For commercial licensing, enterprise support, and secure enclave deployments, please contact us directly.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Add tests for new functionality
4. Commit your changes (`git commit -am 'Add improvement'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Open a Pull Request

## Changelog

### v1.0.0 (2026-05-26)
- Initial release
- Implemented three-level audit framework
- Added comprehensive input validation
- Full logging and error handling

## References

- FDA Biostatistics Guidance: [Statistical Principles for Clinical Trials](https://www.fda.gov/media/71107/download)
- Statsmodels Documentation: [Statistical Tests](https://www.statsmodels.org/stable/stats.html)
- Simpson's Paradox: [Educational Overview](https://en.wikipedia.org/wiki/Simpson%27s_paradox)
