# Hospital Network Participation and HCAHPS Study

Reproducible computational repository for the study:

> **Association of Health Information Network Participation Profiles With Patient-Reported Discharge Information in U.S. Acute Care and Critical Access Hospitals: A National Cross-Sectional Study**

## Repository status

**Private validation workspace. Results are provisional until the complete pipeline has been rerun from the archived public-source files in a clean environment and all automated checks pass.**

This repository is being built to provide a transparent chain from source data to the final manuscript:

```text
public source files
    -> integrity checks
    -> cleaning and linkage
    -> locked analytic cohort
    -> multiple imputation
    -> outcome-observation weighting
    -> primary and sensitivity models
    -> tables, figures, and manuscript-value audit
```

## Study question

Among U.S. nonfederal acute-care hospitals represented in the 2024–2025 Office of the National Coordinator for Health Information Technology network-participation data, are health-information-network participation profiles associated with patient-reported discharge-information performance, and does the association differ by Critical Access Hospital status?

## Current locked benchmarks

These values are validation targets, not substitutes for rerunning the code:

- Source cohort: **2,651 hospitals**
- Acute Care Hospitals: **1,871**
- Critical Access Hospitals: **780**
- Primary outcome observed: **2,409 hospitals**
- Global six-profile test: **Wald chi-square 29.01, 5 df, p < 0.001**
- Prespecified profile 5 versus profile 3 contrast: **0.276 percentage points; 95% CI -0.152 to 0.703; p = 0.206**
- Global profile-by-CAH interaction: **Wald chi-square 7.19, 5 df, p = 0.207**

Every benchmark must be regenerated and reconciled before release.

## Reproducibility standard

The final repository must:

1. Start from archived, checksum-verified source files.
2. Use relative paths and a documented software environment.
3. Generate analytic datasets, results, tables, and figures without manual editing.
4. Record warnings, convergence information, random seeds, and package versions.
5. Test cohort counts, profile definitions, linkage rules, and manuscript values.
6. Run successfully in both a local Jupyter/Python environment and GitHub Actions.
7. Archive a tagged public release through Zenodo after validation.

## Planned structure

```text
.
├── .github/workflows/       Automated validation and reproduction
├── data/
│   ├── raw/                 Source files kept out of Git
│   ├── interim/             Rebuilt intermediate files
│   └── processed/           Locked analytic datasets
├── docs/                    Protocol, decision log, and reproduction guide
├── legacy/                  Preserved pre-repository scripts for audit only
├── notebooks/               Executed explanatory notebooks
├── outputs/
│   ├── diagnostics/
│   ├── figures/
│   ├── logs/
│   └── tables/
├── src/                     Canonical production pipeline
├── tests/                   Automated scientific and structural checks
├── run_all.py               One-command pipeline entry point
└── requirements.txt         Pinned Python dependencies
```

## Current phase

**Phase 1: repository initialization and source-file inventory.**

The earlier scripts will be preserved under `legacy/` and then refactored into a clean, modular, testable pipeline. They are not yet the final reproducible implementation.

## Data policy

Raw public data are not committed automatically. The repository records official source pages, archived filenames, access dates, file sizes, and SHA-256 checksums. A future download/restore script will either retrieve the exact archived files or instruct the user where to place them.

## Authorship and use of AI

All scientific decisions, code, outputs, interpretations, and manuscript statements remain the responsibility of the human authors. AI assistance may be used for code drafting, debugging, documentation, and language editing, but no result is accepted without execution in a documented statistical environment and verification against saved outputs.

## Maintainer

Elechi Ubalaeze Solomon

## License

No reuse license has been selected during private validation. A license will be chosen before public release.
