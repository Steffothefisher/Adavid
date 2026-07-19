# ADAVID (Algorithmic Data Audit and Validation for Integrous Diagnostics)

⚠️ **PROJECT STATUS: EARLY-STAGE PROTOTYPE (RESEARCH & FEASIBILITY)**
This repository contains an early-stage algorithmic prototype exploring mathematical verification methods for publication bias and statistical anomalies in clinical trial data. 

**Important Disclaimers:**
- **Not Regulatory-Grade:** This software does not conform to IEC 62304, ISO 13485, or ISO 14971. It is NOT a medical device and is not cleared for clinical or regulatory decision-making.
- **Under Active Development:** Financial impact projections (€13.5B) and safety metrics presented in early concept pitches are theoretical macro-estimates for modeling purposes and have not been validated against live insurance datasets.
- **Test Coverage:** The testing suite and CI/CD pipelines have been established. Current test coverage is 77% (real, verified).

[![Coverage](https://img.shields.io/badge/coverage-77%25-success?style=for-the-badge)](#test)

### Benchmark Datasets
For validation against published meta-analyses and reference datasets:
- **RCT_Bench**: 50 real-world RCT datasets (29,094 participants) with standardized variables, trial metadata, demographics, and pre-computed covariate-adjustment results. See [syl051088/RCT_Bench](https://github.com/syl051088/RCT_Bench)

---

## Current Capabilities (What Works Today)
The core mathematical foundation is located in `statistical_rigor.py` and contains verified implementations of:
- Multiple-comparison corrections (Bonferroni, Holm, Benjamini-Hochberg).
- Basic normal-approximation power analysis and exact power analysis using scipy's non-central t-distribution.

Modules regarding external APIs (`faers_integration.py`, `live_data_clients.py`) and publication bias estimation (`publication_bias_detector.py`) have been fully refactored, wired, and tested.

---

## Active Development Backlog & Roadmap (Q2/Q3 2026)

### Epic 1 — Scientific Validity
- [x] Replace heuristic funnel asymmetry with formal Egger's regression (with explicit SE and p-values).
- [x] Implement iterative Duval & Tweedie Trim-and-Fill algorithm (replacing single-pass heuristics).
- [ ] Benchmark core statistics against published meta-analyses reference datasets.

### Epic 2 — Data Provenance
- [x] Wire live ClinicalTrials.gov API v2 clients with robust error handling.
- [x] Implement immutable snapshot tracking to ensure full reproducibility of data audits.

### Epic 3 — Software Quality
- [x] Build comprehensive unit test suite for all statistical components.
- [x] Set up GitHub Actions CI pipeline for real-time coverage measurement.

---
## License
MIT License
