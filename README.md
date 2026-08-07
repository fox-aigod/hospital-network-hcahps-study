# Hospital Network Participation and HCAHPS Study

Reproducible computational repository for the study:

> **Association of Health Information Network Participation Profiles With Patient-Reported Discharge Information in U.S. Acute Care and Critical Access Hospitals: A National Cross-Sectional Study**

## Repository status

**Private validation workspace. Results remain provisional until the complete source-to-results pipeline has been rerun in a clean environment and every manuscript value passes automated reconciliation.**

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

## Study question

Among U.S. nonfederal acute-care hospitals represented in the 2024–2025 Office of the National Coordinator for Health Information Technology network-participation data, are health-information-network participation profiles associated with patient-reported discharge-information performance, and does the association differ by Critical Access Hospital status?

## Current validation status

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
- Ownership disagreement: 1,012 hospitals

All substantive values in the regenerated 63-column analysis-ready file matched the frozen file across all 2,651 hospitals. Two audit-status labels changed because the earlier script stripped alphabetic suffixes from federal identifiers and then described two valid numeric rows as duplicate resolutions. The corrected pipeline excludes those federal identifiers before linkage; the selected hospitals and all analytical values are unchanged.

### Next stage

Rebuild the locked multiple-imputation and outcome-observation-weighting pipeline, preserve all random seeds and diagnostics, and reproduce the primary model inputs before fitting the structural regressions.

## Current model benchmarks

These remain provisional validation targets:

- Global six-profile test: **Wald chi-square 29.01, 5 df, p < 0.001**
- Profile 5 versus profile 3 contrast: **0.276 percentage points; 95% CI -0.152 to 0.703; p = 0.206**
- Profile-by-CAH interaction: **Wald chi-square 7.19, 5 df, p = 0.207**

## Running the current pipeline

After restoring the archived files listed in `data/raw/README.md`:

```bash
python run_all.py --stage verify-raw
python run_all.py --stage stage1
python run_all.py --stage stage2
python run_all.py --stage stage3
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
6. Run successfully in a local Python/Jupyter environment and GitHub Actions.
7. Archive a tagged public release through Zenodo after validation.

## Data policy

Raw public data are not committed automatically. `config/raw_sources.json` records the archived filename, source page, snapshot date, size, dimensions, and SHA-256 checksum for every source. Refreshed web files are not silently substituted for the archived analytical snapshots.

## Authorship and AI assistance

All scientific decisions, code, outputs, interpretations, and manuscript statements remain the responsibility of the human authors. AI assistance may support code drafting, debugging, documentation, and language editing, but no result is accepted without execution in a documented statistical environment and verification against saved outputs.

## Maintainer

Elechi Ubalaeze Solomon

## License

No reuse license has been selected during private validation. A license will be chosen before public release.
