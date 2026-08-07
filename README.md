# Hospital Network Participation and HCAHPS Study

Reproducible computational repository for the study:

> **Association of Health Information Network Participation Profiles With Patient-Reported Discharge Information in U.S. Acute Care and Critical Access Hospitals: A National Cross-Sectional Study**

## Repository status

**Private validation workspace. Results remain provisional until the complete source-to-results pipeline has been rerun in a clean environment and every manuscript value passes automated reconciliation.**

The repository provides a transparent chain from source data to the final manuscript:

```text
public source files
    -> integrity checks
    -> cleaning and linkage
    -> locked analytic cohort
    -> HCAHPS outcome linkage
    -> confounder linkage
    -> multiple imputation
    -> outcome-observation weighting
    -> primary and sensitivity models
    -> tables, figures, and manuscript-value audit
```

## Study question

Among U.S. nonfederal acute-care hospitals represented in the 2024–2025 Office of the National Coordinator for Health Information Technology network-participation data, are health-information-network participation profiles associated with patient-reported discharge-information performance, and does the association differ by Critical Access Hospital status?

## Current validation status

### Stage 1 — archived-source verification and ONC-CMS cohort: **reproduced exactly**

The canonical Stage 1 code verifies all five archived source files, normalizes valid six-digit CMS Certification Numbers, resolves duplicate records deterministically, links ONC records to CMS Hospital General Information, restricts the population to Acute Care and Critical Access Hospitals, locks the exposure cohort to 2024–2025, and derives the prespecified six-category exposure.

The clean rerun reproduced:

- 3,393 raw ONC rows;
- 12 ONC rows without a usable CCN;
- 3,380 unique usable ONC CCNs;
- 3,293 ONC-CMS matches;
- 3,250 eligible Acute Care and Critical Access Hospitals across all source years; and
- **2,651 hospitals in the locked 2024–2025 cohort: 1,871 Acute Care Hospitals and 780 Critical Access Hospitals.**

The rebuilt cohort matched the preserved analysis-ready dataset across all 2,651 CCNs and all tested exposure and profile fields, with no mismatches.

### Stage 2 — HCAHPS outcome linkage: **reproduced exactly**

The canonical Stage 2 code reads the archived hospital-level HCAHPS file, excludes alphanumeric federal facility identifiers from the numeric CCN namespace, verifies a single reporting period, preserves suppression footnotes and survey metadata, and links the primary and secondary outcomes one-to-one by CCN.

The clean rerun reproduced:

- 325,856 HCAHPS rows and 68 measure identifiers;
- reporting period July 1, 2024 through June 30, 2025;
- all 2,651 locked hospitals present in the HCAHPS source;
- **2,409 hospitals with the primary discharge-information outcome: 1,852 Acute Care Hospitals and 557 Critical Access Hospitals;** and
- 1,988 hospitals with the discharge-information linear-mean sensitivity outcome.

The rebuilt HCAHPS cohort matched the preserved cohort across all 2,651 CCNs and every tested primary outcome, secondary outcome, availability flag, suppression footnote, survey count, response rate, and reporting-period field, with no mismatches.

### Next stage

Rebuild the AHRQ Hospital Linkage and USDA Rural-Urban Continuum Code linkages, reproduce covariate completeness, and confirm the ownership-sensitivity variables before multiple imputation.

## Current locked benchmarks

These remain validation targets until the full pipeline is complete:

- Source cohort: **2,651 hospitals**
- Primary outcome observed: **2,409 hospitals**
- Global six-profile test: **Wald chi-square 29.01, 5 df, p < 0.001**
- Prespecified profile 5 versus profile 3 contrast: **0.276 percentage points; 95% CI -0.152 to 0.703; p = 0.206**
- Global profile-by-CAH interaction: **Wald chi-square 7.19, 5 df, p = 0.207**

Every benchmark must be regenerated and reconciled before release.

## Running the current pipeline

After restoring the archived files listed in `data/raw/README.md`:

```bash
python run_all.py --stage verify-raw
python run_all.py --stage stage1
python run_all.py --stage stage2
pytest -q
```

Generated data and outputs are excluded from Git and remain local unless explicitly archived as a release artifact.

## Reproducibility standard

The final repository must:

1. Start from archived, checksum-verified source files.
2. Use relative paths and a documented software environment.
3. Generate analytic datasets, results, tables, and figures without manual editing.
4. Record warnings, convergence information, random seeds, and package versions.
5. Test cohort counts, profile definitions, linkage rules, and manuscript values.
6. Run successfully in both a local Jupyter/Python environment and GitHub Actions.
7. Archive a tagged public release through Zenodo after validation.

## Repository structure

```text
.
├── .github/workflows/       Automated validation
├── config/                  Source fingerprints and expected-result contracts
├── data/
│   ├── raw/                 Archived source files kept out of Git
│   ├── interim/             Rebuilt intermediate files
│   └── processed/           Locked analytic datasets
├── docs/                    Protocol and reproducibility decision log
├── notebooks/               Executed explanatory notebooks
├── outputs/
│   ├── diagnostics/
│   ├── figures/
│   ├── logs/
│   └── tables/
├── src/                     Canonical production pipeline
├── tests/                   Automated scientific and structural checks
├── run_all.py               Command-line pipeline entry point
└── requirements.txt         Pinned Python dependencies
```

## Data policy

Raw public data are not committed automatically. `config/raw_sources.json` records the official source page, archived filename, snapshot date, file size, row and column counts, and SHA-256 checksum for every source. Refreshed web files are not silently substituted for the archived analytical snapshots.

## Authorship and use of AI

All scientific decisions, code, outputs, interpretations, and manuscript statements remain the responsibility of the human authors. AI assistance may be used for code drafting, debugging, documentation, and language editing, but no result is accepted without execution in a documented statistical environment and verification against saved outputs.

## Maintainer

Elechi Ubalaeze Solomon

## License

No reuse license has been selected during private validation. A license will be chosen before public release.
