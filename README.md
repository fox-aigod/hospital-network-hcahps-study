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

All substantive values in the regenerated 63-column analysis-ready file matched the frozen file across all 2,651 hospitals. Two audit-status labels were corrected after excluding federal alphanumeric identifiers before numeric-CCN linkage; the selected hospitals and analytical values were unchanged.

### Stage 4 — multiple imputation and observation weighting: reproduced and convergence-corrected

- 20 deterministic imputations
- Five chained-equation cycles per imputation
- Base seed `20260805`, incremented by `1009`
- Seven imputed confounder fields
- 700 imputation-model fits with zero warnings
- No observed values changed
- Every continuous imputation came from an observed predictive-mean-matching donor
- Archived imputation, weight, and balance diagnostics reproduced byte for byte

The archived denominator observation models used a 500-iteration limit; 17 of 20 reached that limit, but the earlier script suppressed the warnings. The canonical pipeline preserves those legacy weights for exact audit reproduction and separately refits the same model with a 2,000-iteration limit. All 20 canonical fits converged, requiring at most 665 iterations.

The correction was numerically small:

- Maximum absolute denominator-probability change: 0.00583
- Maximum absolute normalized-weight change: 0.01577
- Maximum mean absolute normalized-weight change: 0.000110
- Mean effective sample size: 2,365.8
- Maximum residual within-stratum SMD: 0.17634, still driven by bed size among 2024 Critical Access Hospitals

The canonical converged imputations and weights are the locked inputs for Stage 5.

### Stage 5 — structural models and sensitivities: reproduced and validated

- Fourteen archived model-result CSV files reproduced byte for byte in legacy mode
- Canonical primary and sensitivity models used the converged weights
- 200 additional canonical observation-model fits completed with zero convergence warnings; maximum iterations required: 797
- Global six-profile test: Wald chi-square 29.0083, 5 df, p=0.0000231
- Profile 5 versus profile 3: 0.2757 percentage points, 95% CI -0.1516 to 0.7031, p=0.2060
- Global profile-by-CAH interaction: Wald chi-square 7.1932, 5 df, p=0.2067
- All primary manuscript values were unchanged at their reported precision
- All p-value decisions at alpha 0.05 were unchanged across primary, secondary, subgroup, and sensitivity comparisons

The canonical and historical results are reconciled in `outputs/stage5/reconciliation/` when the pipeline is executed.

### Next stage

Generate final manuscript tables and figures directly from the canonical outputs, update every reported number, and build a machine-readable manuscript-value audit.

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
python run_all.py --stage stage4
python run_all.py --stage stage5
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
