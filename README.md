# Hospital Network Participation and HCAHPS Study

## Overview

This repository contains the research software, reproducibility contracts, tests, and release-governance documentation for the study:

> **Association of Health Information Network Participation Profiles With Patient-Reported Discharge Information in U.S. Acute Care and Critical Access Hospitals: A National Cross-Sectional Study**

## Research question and study scope

Among U.S. nonfederal acute-care hospitals represented in the 2024–2025 Office of the National Coordinator for Health Information Technology network-participation data, are health-information-network participation profiles associated with patient-reported discharge-information performance, and does the association differ by Critical Access Hospital status?

## Repository status

**Validated v1.0.0 reproducibility release.** The complete Stage 1–6 source-to-results workflow passed in the locked Ubuntu 24.04 x86-64 release environment. The final validation verified all five canonical raw snapshots (5/5), reproduced the Stage 4, Stage 5, and Stage 6 contracts (14/14, 16/16, and 17/17 artifacts), and completed the all-data test suite with 40 passed, 0 failed, and 0 skipped. All 95 historical inferential decisions remained stable. Manuscript and supplement synchronization passed, final authorship and declarations are locked, and the curated aggregate release artifacts are assembled and checksum-validated under `release/v1.0.0/`.

Independent external computational/statistical review and manuscript verification
were completed, and reviewer findings were independently adjudicated and corrected.
Post-review robustness diagnostics preserved the primary scientific conclusions;
canonical scientific code, results, and contracts remained unchanged during the
review corrections. The immutable GitHub release identifier is `v1.0.0`. Zenodo
archiving and its DOI are handled separately; no DOI or journal publication is claimed.

Stage 7.7B added a controlled post-review correction record under
`release/v1.0.0/postreview/`. It documents aggregate stratified analyses, finite-
multiple-imputation and state-cluster reference diagnostics, the post-review
flexible-size sensitivity, and an expanded zero-mismatch manuscript audit. These
diagnostics do not replace or alter the canonical Stage 4–6 contracts. The six
`p_value=0` fields in adjusted-mean rows of both `stage5/adjusted_profile_means.csv`
and `postreview/flexible_bed_size_sensitivity.csv` are tests of each adjusted mean
against zero, not profile-comparison p-values. Profile-comparison inference must
be taken from global tests, planned contrasts, and interaction contrasts; the
validated canonical artifact bytes remain unchanged. Stage 7.7D added the final
post-correction audits and reporting clarifications without changing those bytes.

## Data sources

The analysis uses five exact source snapshots identified by filename and SHA-256 in `config/raw_sources.json`:

| Agency/source | Study file | Analytical role | Current archival position |
| --- | --- | --- | --- |
| ONC/ASTP | `hospital_network_participation.csv` | Network-participation exposure | Eligible with attribution and an AHA provenance caveat |
| CMS | `cms_hospital_general_information.csv` | Hospital cohort and characteristics | Eligible |
| CMS | `HCAHPS-Hospital.csv` | Patient-reported outcomes | Eligible |
| AHRQ Compendium | `chsp-hospital-linkage-2023.csv` | Health-system and ownership linkage | **HOLD pending written redistribution clarification** |
| USDA Economic Research Service | `Ruralurbancontinuumcodes2023.csv` | Rurality classification | Eligible with attribution |

The recorded `2026-08-05` manifest date is the analytical snapshot/freeze date, not an asserted original retrieval date for every source. See `config/data_rights.json` and `docs/data_rights_and_availability.md` for the source-specific rights and archival dispositions.

## Reproducibility architecture

```text
public source files
    -> integrity checks
    -> ONC-CMS cohort
    -> HCAHPS outcome linkage
    -> AHRQ and USDA confounder linkage
    -> multiple imputation
    -> outcome-observation weighting
    -> primary and sensitivity models
    -> tables, figures, and manuscript-value audit
```

## Validation and testing

Ordinary GitHub Actions validation installs the locked environment, validates repository contracts, and runs the complete test suite available without the five archived raw snapshots. The data-dependent integration tests are expected to skip in GitHub Actions because those snapshots are not stored in Git. The distinct final all-data procedure is documented in `docs/release_validation_procedure.md`.

### Stage 1 — ONC-CMS cohort: reproduced

- 3,393 raw ONC rows
- 3,380 unique usable ONC CCNs
- 3,293 ONC-CMS matches
- **2,651 hospitals in the locked 2024–2025 cohort**
  - 1,871 Acute Care Hospitals
  - 780 Critical Access Hospitals

The regenerated cohort matched the frozen dataset across all tested exposure and profile fields.

### Stage 2 — HCAHPS linkage: reproduced

- 325,856 HCAHPS rows
- Reporting period: July 1, 2024–June 30, 2025
- All 2,651 locked hospitals present in the HCAHPS source
- **2,409 hospitals with the primary discharge-information outcome**
  - 1,852 Acute Care Hospitals
  - 557 Critical Access Hospitals
- 1,988 hospitals with the discharge-information linear-mean outcome

The regenerated HCAHPS cohort matched every tested outcome, availability, footnote, survey-count, response-rate, and reporting-period field.

### Stage 3 — AHRQ and USDA confounder linkage: reproduced

- AHRQ matched **2,624 of 2,651 hospitals (99.0%)**
- USDA 2023 RUCC matched **2,651 of 2,651 hospitals (100%)**
- Complete required covariates: **2,580 hospitals (97.3%)**
  - 1,826 Acute Care Hospitals
  - 754 Critical Access Hospitals
- AHRQ/HCRIS and CMS ownership both observed for 2,600 hospitals
- Ownership agreement: **1,588 of 2,600 (61.1%)**

All substantive values in the regenerated 63-column analysis-ready file matched the frozen file across all 2,651 hospitals. Two audit-status labels were corrected after excluding federal alphanumeric identifiers before numeric-CCN linkage; the selected hospitals and analytical values were unchanged.

### Stage 4 — multiple imputation and observation weighting: release contract reproduced

- 20 deterministic imputations
- Five chained-equation cycles per imputation
- Base seed `20260805`, incremented by `1009`
- Seven imputed confounder fields
- 700 imputation-model fits with zero warnings
- No observed values changed
- Every continuous imputation came from an observed predictive-mean-matching donor
- Four historical diagnostic hashes retained as provenance
- Fourteen official-release Stage 4 artifacts independently reproduced byte for byte

The historical denominator observation models used a 500-iteration limit. In the
official release environment, 18 of 20 reach that limit. The canonical pipeline
preserves those legacy-mode weights for comparison and separately refits the same
model with a 2,000-iteration limit. All 20 canonical fits converge, requiring at
most 685 iterations. The unrecovered original numerical backend generated different
historical bytes; see `docs/numerical_reproducibility.md`.

The correction was numerically small:

- Maximum absolute denominator-probability change: 0.01201
- Maximum absolute normalized-weight change: 0.02782
- Maximum mean absolute normalized-weight change: 0.000143
- Mean effective sample size: 2,365.8
- Maximum residual within-stratum SMD: 0.17651, still driven by bed size among 2024 Critical Access Hospitals

The canonical converged imputations and weights are the locked inputs for Stage 5.

### Stage 5 — structural models and sensitivities: reproduced and validated

- Sixteen canonical Stage 5 artifacts independently reproduced byte for byte
- Canonical primary and sensitivity models used the converged weights
- 200 canonical observation-model fits completed with zero convergence warnings; maximum iterations required: 684
- Global six-profile test: Wald chi-square 29.0319, 5 df, p=0.0000229
- Profile 5 versus profile 3: 0.2760 percentage points, 95% CI -0.1514 to 0.7033, p=0.2057
- Global profile-by-CAH interaction: Wald chi-square 7.1823, 5 df, p=0.2074
- No significance, estimate-sign, confidence-interval, or FDR decision changed across 95 historical tests

The canonical and historical results are reconciled in `outputs/stage5/reconciliation/` when the pipeline is executed.

### Stage 6 — publication tables, figures, and manuscript-value audit: generated and verified

- Three main manuscript tables generated directly from canonical Stage 5 outputs and the locked analysis-ready cohort
- Six supplementary tables generated directly from canonical outputs
- Four main figures and one supplementary balance figure generated by executable Python
- Cohort-flow counts read from the Stage 1 and Stage 2 machine-readable summaries rather than hard-coded values
- Table S1 profile bits preserved as four-character strings, including leading zeroes
- Main Table 2 reconciles to 2,651 source hospitals and 2,409 observed primary outcomes
- 2025-only sensitivity global statistic displays as 31.04 (5)
- All five figures exceed 1,600 pixels in width
- The release-contract audit records the two historical display differences that initiated manuscript synchronization

The final all-data reproduction passed before the separate Stage 7.4 and 7.4A
manuscript/supplement synchronization. The nine manuscript display locations, 49
publication-table cells, methods environment text, and reproducibility wording were
independently reconciled to the official release values. The final manuscript audit
reported 71/71 checks passing with zero numerical mismatches, and the final table audit
reported 812 audited cells with zero mismatches. No figure or scientific conclusion
changed.

## Current model benchmarks

These are the official release-environment values:

- Global six-profile test: **Wald chi-square 29.03, 5 df, p < 0.001**
- Profile 5 versus profile 3 contrast: **0.276 percentage points; 95% CI -0.151 to 0.703; p = 0.206**
- Profile-by-CAH interaction: **Wald chi-square 7.18, 5 df, p = 0.207**

## Computational environment

Create the supported CPython 3.13.14 environment and install the exact direct and transitive dependency lock:

```bash
python -m pip install "pip==26.2.1"
python -m pip install --requirement requirements-lock.txt
python -m pip check
```

The complete environment contract and lock-regeneration procedure are documented in `docs/computational_environment.md`.

## Running the analysis

After restoring the archived files listed in `data/raw/README.md`:

```bash
python run_all.py --stage verify-raw
python run_all.py --stage stage1
python run_all.py --stage stage2
python run_all.py --stage stage3
python run_all.py --stage stage4
python run_all.py --stage stage5
python run_all.py --stage stage6
pytest -q
```

Generated datasets and outputs are excluded from Git and remain local unless explicitly archived as release artifacts.

## Reproducibility standard

The final repository must:

1. Start from archived, checksum-verified source files.
2. Use relative paths and a documented software environment.
3. Generate datasets, results, tables, and figures without manual editing.
4. Record warnings, convergence information, random seeds, and package versions.
5. Test cohort counts, linkage rules, profile definitions, and manuscript values.
6. Run successfully in the locked Python environment and GitHub Actions.
7. Archive a tagged public release through Zenodo after validation.

## Data availability and rights

Raw source data are not committed. `config/raw_sources.json` records each analytical filename, source page, manifest snapshot/freeze date, size, dimensions, and SHA-256 checksum; refreshed web files are not silently substituted for the analytical snapshots.

The MIT License covers original repository software and software-oriented documentation, not third-party source data. Source-specific rights and archival dispositions are documented in `docs/data_rights_and_availability.md` and `config/data_rights.json`. The AHRQ snapshot and restricted row-level derivatives remain on hold pending written redistribution clarification; no AHRQ raw data are authorized for public archiving at this stage.

## Citation

Scholarly software citation metadata, version `1.0.0`, and the release date are
provided in `CITATION.cff`. No archive DOI, article DOI, or preferred article
citation is asserted. Any later identifier requires separate verification.

## License

Original software source code and software-oriented documentation authored for this repository are licensed under the MIT License; see `LICENSE`. This license does not relicense third-party datasets, externally sourced material, manuscript/article content governed by an eventual publisher license, or publication assets assigned a different license. See `docs/data_rights_and_availability.md` for the complete scope statement.

## Study authors

- **Elechi Ubalaeze Solomon** — Business Administration, Lee Business School, University of Nevada, Las Vegas, Las Vegas, Nevada, USA. ORCID: [0009-0002-3474-1002](https://orcid.org/0009-0002-3474-1002).
- **Chiderah Akubuiro** — Obstetrics and Gynecology, Trinity Medical Sciences University, Ribishi, St. Vincent and the Grenadines.
- **Abone Kindson** — Faculty of Dentistry, University of Nigeria Teaching Hospital, Ituku/Ozalla, Enugu State, Nigeria.
- **Mohamed Albert Tarawallie, BSc, MSc** — Public Health, Institute for Health Professionals Development (IHPD), Freetown, Sierra Leone.

These are the final study/manuscript authors. Repository and software authorship is a
separate attribution: `CITATION.cff` identifies Elechi Ubalaeze Solomon as the author
of this software/reproducibility package. The other study authors are not represented
as software authors because their finalized contributions do not include software or
code development.

## Author contributions

- **Elechi Ubalaeze Solomon:** Conceptualization, Methodology, Investigation, Data Curation, Formal Analysis, Writing – Original Draft, Writing – Review & Editing, Project Administration.
- **Chiderah Akubuiro:** Clinical Interpretation, Validation, Writing – Review & Editing, Critical Review of the Clinical Relevance of Patient-Reported Discharge Information and Hospital Care Processes.
- **Abone Kindson:** Clinical Interpretation, Validation, Literature Review, Writing – Review & Editing, Critical Review of the Patient-Experience and Healthcare-Delivery Implications.
- **Mohamed Albert Tarawallie:** Formal Analysis, Validation, Writing – Review & Editing, Critical Review of the Statistical Methodology, Analytical Results, and Interpretation.

## Ethics, funding, and competing interests

This study used publicly available hospital-level secondary data and did not involve
human subjects or identifiable private information. IRB review and informed consent
were not required. This research received no external funding. The authors declare no
conflicts of interest.

## AI assistance

ChatGPT assisted with code drafting and debugging, reproducibility auditing,
literature searching, figure-generation code, language editing, document organization,
and formatting. The human authors retain responsibility for the data, analyses,
citations, interpretation, and final content. AI assistance is not authorship and did
not replace human scientific judgment.

## Release status

The complete Stage 1–6 pipeline, all five raw-source checks, all 47 Stage 4–6 artifact contracts, the 40-test no-skip suite, manuscript/supplement synchronization, and final governance review have passed. The curated aggregate Stage 5/6 artifacts and final audit are assembled and checksum-validated under `release/v1.0.0/`. The annotated `v1.0.0` tag identifies the immutable GitHub software/reproducibility release. Raw and restricted row-level data are excluded. Zenodo records, DOI registration, and journal submission remain separate actions subject to the release boundaries in `docs/public_release_inventory.md`; no archive DOI or journal publication is claimed.
