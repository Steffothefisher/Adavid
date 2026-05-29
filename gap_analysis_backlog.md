# ADAVID — Honest Gap Analysis & Product Backlog

**Date:** 2026-05-29
**Status of this document:** This is a truthful internal planning document. It separates what **EXISTS** today from what is **PLANNED**. Nothing here should be communicated externally as "done" unless it is marked ✅ DONE and has been independently verified.

---

## 0. Legend

| Marker | Meaning |
|--------|---------|
| ✅ DONE | Exists in the repo and has been checked to work |
| 🟡 PARTIAL | Some real code exists, but incomplete / heuristic / unverified |
| 🔵 PLANNED | Does not exist yet. A goal, not a current capability. |
| ❌ FALSE CLAIM | Was previously asserted but is untrue and must be retracted |

---

## 1. Reality Check — What Is Actually True Today

Verified by inspecting the repository on 2026-05-29:

- **35 Python files** exist.
- **0 test files exist.** The claim of "94% test coverage" in the README and docs is ❌ FALSE and must be removed.
- **No CI/CD** pipeline exists (no `.github/workflows`).
- **No risk management, traceability, verification, or validation** artifacts exist (the things IEC 62304 / ISO 13485 / ISO 14971 actually require).
- Some modules still contain **mocks/placeholders** (`faers_integration.py`, parts of `live_data_clients.py`).
- `statistical_rigor.py` contains **genuinely correct** implementations (Bonferroni, Holm, Benjamini-Hochberg, normal-approximation power analysis). This is the real, salvageable core.
- `publication_bias_detector.py` uses **heuristics with fixed assumptions**, not the validated Egger's / Duval & Tweedie methods.

**Honest one-line summary:** ADAVID is an early-stage prototype exploring publication-bias statistics. A few methods are correctly implemented. It is **not** a medical device, **not** validated, and **not** regulatory-grade.

---

## 2. Claims That Must Be Retracted (❌)

These were asserted in documents/website during development and are not supportable:

1. ❌ "Regulatory-grade" — implies IEC 62304 / ISO 13485 / ISO 14971 conformance. None exists.
2. ❌ "94% test coverage" — there are zero tests.
3. ❌ "€13.5B Year 1 savings" — a generated figure, never modelled.
4. ❌ "100,000 lives saved / deaths prevented" — invented, no basis.
5. ❌ "Makes pharmaceutical fraud impossible" — marketing hyperbole.
6. ❌ "Production Ready" — it is a prototype.
7. ❌ Specific ADAVID output numbers (e.g. asymmetry "+0.89") presented as validated results — they are illustrative.

**Action:** Remove all of the above from README, website, pitch deck, and any outbound material. (See Epic 0.)

---

## 3. Gap Analysis by Domain

### Domain A — Scientific / Statistical Validity
| # | Capability | Status | Gap |
|---|-----------|--------|-----|
| A1 | Multiple-comparison correction | ✅ DONE | Needs unit tests against known values |
| A2 | Power analysis | 🟡 PARTIAL | Normal approximation only; not validated vs statsmodels |
| A3 | Funnel-plot asymmetry | 🟡 PARTIAL | Heuristic, not real Egger's regression (no p-value, no SE) |
| A4 | Trim-and-fill | 🟡 PARTIAL | Single-pass heuristic, not Duval & Tweedie iteration |
| A5 | Meta-analysis (DerSimonian-Laird) | 🟡 PARTIAL | Present but unverified against reference datasets |
| A6 | Equivalence testing (TOST) | 🟡 PARTIAL | Present but untested |
| A7 | Statistical method validation suite | 🔵 PLANNED | No benchmark against published meta-analyses exists |

### Domain B — Data Integration
| # | Capability | Status | Gap |
|---|-----------|--------|-----|
| B1 | ClinicalTrials.gov client | 🟡 PARTIAL | Scaffolded; needs real wiring + error handling |
| B2 | FDA FAERS client | 🟡 PARTIAL | Was mock in v3; live client needs verification |
| B3 | Data provenance tracking | 🔵 PLANNED | No source/version/timestamp capture on ingested data |
| B4 | Reproducible data snapshots | 🔵 PLANNED | No way to freeze a dataset for re-analysis |

### Domain C — Software Quality / Engineering
| # | Capability | Status | Gap |
|---|-----------|--------|-----|
| C1 | Unit tests | 🔵 PLANNED | Zero tests exist today |
| C2 | CI pipeline | 🔵 PLANNED | None |
| C3 | Real coverage measurement | 🔵 PLANNED | Cannot measure until tests exist |
| C4 | Input validation & error handling | 🟡 PARTIAL | Some exists in core_infrastructure.py |
| C5 | Honest inline tagging of heuristics | 🟡 PARTIAL | Done for refactored files; not all files |

### Domain D — Regulatory Foundations (only if pursued seriously)
| # | Capability | Status | Gap |
|---|-----------|--------|-----|
| D1 | Risk management file (ISO 14971) | 🔵 PLANNED | Does not exist |
| D2 | Requirements traceability matrix | 🔵 PLANNED | Does not exist |
| D3 | Verification & validation protocols | 🔵 PLANNED | Does not exist |
| D4 | Software lifecycle process (IEC 62304) | 🔵 PLANNED | Does not exist |
| D5 | Design controls / sign-offs (ISO 13485) | 🔵 PLANNED | Does not exist |
| D6 | Independent statistical review | 🔵 PLANNED | Never done |

### Domain E — Honesty / Communication
| # | Capability | Status | Gap |
|---|-----------|--------|-----|
| E1 | Remove false claims from all materials | 🔵 PLANNED | Highest priority |
| E2 | Honest README / project description | 🔵 PLANNED | Needed before any further outreach |
| E3 | Correction to prior recipients | 🔵 PLANNED | Optional, your decision |

---

## 4. Backlog — Epics, User Stories & Subtasks

> **Priority order is deliberate:** honesty first, then the real scientific core, then quality, then (only if you choose to pursue it) the heavy regulatory lift.

---

### EPIC 0 — Stop the Bleeding: Honest Communication 🔵 PLANNED
*Goal: nothing untrue remains in any material.*

**Story 0.1** — As the project owner, I want all unsupported claims removed so that no one is misled again.
- [ ] Remove "regulatory-grade" from README, website, pitch deck
- [ ] Remove "94% test coverage" everywhere it appears
- [ ] Remove invented figures (€13.5B, 100k lives, "+0.89" as result)
- [ ] Remove "Production Ready" / "makes fraud impossible"
- [ ] Add a plain "Project status: early prototype" banner

**Story 0.2** — As the project owner, I want an honest one-paragraph description I can reuse.
- [ ] Draft: what it is (prototype), what works (some stats), what it is not (not validated, not a device)
- [ ] Use consistently across repo and any future communication

**Story 0.3 (optional)** — As the project owner, I want a short correction for prior recipients.
- [ ] Draft a calm, factual retraction note
- [ ] You decide whether/when to send it

---

### EPIC 1 — Make the Scientific Core Real & Trustworthy 🟡→✅
*Goal: the statistics are correct, validated, and honest about limits.*

**Story 1.1** — As an analyst, I want correctly implemented publication-bias tests so results are defensible.
- [ ] 🔵 PLANNED: Replace heuristic asymmetry with real Egger's regression (slope, intercept, SE, p-value)
- [ ] 🔵 PLANNED: Replace single-pass trim-and-fill with the iterative Duval & Tweedie algorithm
- [ ] 🔵 PLANNED: Add the rank-correlation (Begg) test as a cross-check
- [ ] 🔵 PLANNED: Every method returns explicit limitations + minimum-n guards

**Story 1.2** — As an analyst, I want the statistics validated against known datasets.
- [ ] 🔵 PLANNED: Collect 10-20 published meta-analyses with known bias conclusions
- [ ] 🔵 PLANNED: Run ADAVID against them; document agreement/disagreement
- [ ] 🔵 PLANNED: Publish the validation report honestly (including failures)

**Story 1.3** — As an analyst, I want power analysis to match a reference implementation.
- [ ] 🟡 PARTIAL: Existing normal-approximation works
- [ ] 🔵 PLANNED: Benchmark against statsmodels; document deviation
- [ ] 🔵 PLANNED: Flag where the approximation breaks down

---

### EPIC 2 — Real Data Integration 🟡→✅
*Goal: pull real trial data reproducibly, with provenance.*

**Story 2.1** — As an analyst, I want verified ClinicalTrials.gov ingestion.
- [ ] 🟡 PARTIAL: Client scaffolded
- [ ] 🔵 PLANNED: Wire real API v2 calls, handle rate limits + errors
- [ ] 🔵 PLANNED: Integration test against a fixed known trial

**Story 2.2** — As an analyst, I want every datapoint to carry its origin.
- [ ] 🔵 PLANNED: Capture source, URL, version, fetch-timestamp per record
- [ ] 🔵 PLANNED: Store an immutable snapshot so analyses are reproducible

---

### EPIC 3 — Software Quality Foundation 🔵 PLANNED
*Goal: the thing is testable and the coverage number becomes real.*

**Story 3.1** — As a developer, I want a real test suite.
- [ ] 🔵 PLANNED: Unit tests for statistical_rigor.py (assert known values)
- [ ] 🔵 PLANNED: Unit tests for publication-bias methods (synthetic biased/unbiased sets)
- [ ] 🔵 PLANNED: Tests for the fallback/error paths

**Story 3.2** — As a developer, I want CI so nothing regresses.
- [ ] 🔵 PLANNED: GitHub Actions: run tests on every push
- [ ] 🔵 PLANNED: Measure REAL coverage; publish the actual number (no rounding up)

---

### EPIC 4 — Regulatory Foundations 🔵 PLANNED (only if pursued)
*Goal: if you ever genuinely want "regulatory-grade", this is the real, multi-month lift. Be honest that it is not started.*

**Story 4.1** — As a regulatory lead, I want an ISO 14971 risk management file.
- [ ] 🔵 PLANNED: Hazard analysis, risk controls, residual-risk evaluation

**Story 4.2** — As a regulatory lead, I want full requirements traceability.
- [ ] 🔵 PLANNED: Every requirement → design → code → test, bidirectionally linked

**Story 4.3** — As a regulatory lead, I want V&V protocols with sign-offs.
- [ ] 🔵 PLANNED: Documented verification + validation, dated approvals

**Story 4.4** — As a regulatory lead, I want IEC 62304 lifecycle conformance.
- [ ] 🔵 PLANNED: Software safety classification, lifecycle process docs

**Story 4.5** — As a project owner, I want independent expert review before any regulatory claim.
- [ ] 🔵 PLANNED: External statistician + regulatory consultant review

> **Honest note on Epic 4:** This is realistically months of specialist work, typically with paid regulatory/QA expertise. Until every item here is complete and independently reviewed, the word "regulatory-grade" must not be used.

---

## 5. The Vision (Stated Honestly, As a Vision)

> The following is the **aspiration** — the lighthouse, not the current location. Every line is a 🔵 PLANNED goal.

**Vision:** A transparent, open-source tool that helps regulators, payers, and researchers detect when clinical evidence may be selectively reported — using validated, peer-reviewed statistical methods, with full provenance and reproducibility, so that decisions about reimbursement and approval can account for the possibility of hidden negative studies.

**What would have to be true for the vision to be real:**
1. Every statistical method is a validated, published technique — not a heuristic.
2. Results are reproducible from raw data with full provenance.
3. The software has real tests, real coverage, and CI.
4. Limitations are stated everywhere; nothing overclaims.
5. If used in any regulated context: full IEC 62304 / ISO 13485 / ISO 14971 conformance, independently reviewed.
6. Any impact figures come from real economic modelling, peer-reviewed — or are not stated at all.

**Distance from here to there:** large. Epics 1-3 are achievable by a committed developer over time. Epic 4 requires specialist help. The vision is legitimate and worth pursuing — but only with each step labelled truthfully as you go.

---

## 6. Suggested Sequence

1. **Epic 0** (now) — remove false claims; get an honest description.
2. **Epic 1** (next) — make the science real and validated; this is the genuine value.
3. **Epic 3** (alongside 1) — tests + CI so the science stays correct.
4. **Epic 2** — real data with provenance.
5. **Epic 4** — only if you decide to pursue a genuinely regulated path, with expert help.

---

*This document deliberately contains no marketing language and no unverified numbers. If a future version needs a figure, the figure must come with a source or be labelled an estimate.*
