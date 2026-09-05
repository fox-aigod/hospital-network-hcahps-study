# Reproducibility decision log

## 2026-08-06 — Canonical Stage 1 rebuild

The ONC-to-CMS cohort was rebuilt as a modular Python stage rather than treating the earlier compact scripts as the final computational record. The legacy sequence reproduced the initial ONC-CMS feasibility counts, but the compact HCAHPS script omitted fields needed by the later confounder-linkage script. The earlier package was therefore incomplete as an end-to-end source-to-analysis pipeline even though the preserved analytical dataset remained internally consistent.

Stage 1 verifies archived source files, normalizes six-digit CCNs, resolves the one ONC cross-year duplicate deterministically, links ONC to CMS one-to-one, restricts to Acute Care and Critical Access Hospitals, locks survey years 2024–2025, and derives the six-category network profile.

The regenerated cohort contained 2,651 hospitals: 1,871 Acute Care Hospitals and 780 Critical Access Hospitals. It matched the frozen dataset across all tested exposure and profile fields.

## 2026-08-06 — Numeric CCN namespace and HCAHPS linkage

CMS Hospital General Information and HCAHPS contain federal identifiers with alphabetic suffixes, such as `10021F`. These are not six-digit Medicare CCNs. Stripping the suffix can create a false numeric identifier and a collision with another hospital. The canonical normalizer therefore rejects any identifier containing alphabetic characters and zero-pads only genuinely numeric identifiers.

This correction excluded 164 federal facilities from the numeric CMS identifier space and 11,152 HCAHPS rows corresponding to those facilities. It did not alter the 2,651-hospital nonfederal study cohort.

Stage 2 preserves suppression text, verifies one reporting period, requires one row per valid numeric CCN and measure, retains footnotes and survey metadata, and links the prespecified primary, secondary, and linear-mean outcomes.

The primary outcome was reproduced for 2,409 hospitals: 1,852 Acute Care Hospitals and 557 Critical Access Hospitals. All tested HCAHPS fields matched the frozen cohort.

## 2026-08-06 — AHRQ and USDA confounder linkage

The AHRQ file contains 6,800 rows. Of these, 154 use alphanumeric federal identifiers and 124 have no CCN. After excluding those records, 6,522 unique valid numeric CCNs remain. The earlier linkage script stripped alphabetic suffixes, creating artificial duplicate identifiers for `050006` and `050014`; the correct rows were nevertheless selected. The canonical pipeline excludes the federal identifiers first, so these records are correctly labeled exact matches. No analytical value changed.

AHRQ matched 2,624 of 2,651 hospitals. USDA RUCC linkage reached 100% through exact normalization and explicit configured crosswalks, not fuzzy matching. Complete required covariates were available for 2,580 hospitals. Ownership agreement between AHRQ/HCRIS and CMS was 1,588 of 2,600 hospitals with both sources observed.

The regenerated 63-column analysis-ready file matched the frozen file cell by cell for every substantive field across all 2,651 hospitals.

## 2026-08-06 — Stage 4 imputation and observation-model convergence amendment

### Exact legacy reproduction

The preserved statistical script was rerun unchanged against the regenerated Stage 3 dataset. The imputation diagnostics, observation-weight diagnostics, overall balance diagnostics, and within-stratum balance diagnostics reproduced byte for byte, including the archived SHA-256 hashes. This establishes exact recovery of the original analytical inputs.

The imputation specification is 20 imputations, five chained-equation cycles, base seed `20260805`, and seed increment `1009`. Continuous variables use predictive mean matching with five donors after Bayesian ridge prediction. Binary variables use stochastic Bernoulli draws from logistic models, and AHRQ ownership uses stochastic multinomial class draws. Fixed predictors include exposure, CAH status, state, RUCC, survey year, outcome-observation status, filled observed outcome plus a missingness indicator, HCAHPS survey-count and response-rate auxiliaries, CMS ownership, emergency services, and network indicators.

All 700 imputation-model fits completed without warnings. The largest iteration count was 46. No observed value changed; every continuous imputation came from an observed donor; and all binary and categorical imputations remained in their valid domains.

### Hidden observation-model convergence issue

The legacy script globally suppressed warnings. When warnings were restored, 17 of 20 denominator observation models reached the 500-iteration limit. All numerator models converged. Because the weights enter every primary and sensitivity model, this could not be ignored even though the archived outputs reproduced exactly.

### Computational amendment

The canonical denominator model retains the same variables, transformations, standardization, near-unpenalized logistic specification (`C=100`), solver, tolerance, probability clipping, stabilization, 1st/99th percentile trimming, and mean-one normalization. Only the iteration limit increases from 500 to 2,000. All 20 canonical fits converged, requiring 419–665 iterations.

The legacy weights remain stored separately for audit reproduction. The converged weights are the canonical Stage 5 inputs. The maximum absolute normalized-weight difference was 0.015768 and the maximum mean absolute difference was 0.000110. Mean effective sample size changed from 2,365.786 to 2,365.769. Maximum residual within-stratum SMD changed from 0.176465 to 0.176338 and remained attributable to bed size among 2024 Critical Access Hospitals.

This is a convergence correction, not a change in the estimand, covariate set, missing-data assumptions, or weighting strategy. Structural-model results will be recomputed and compared formally in Stage 5 before the manuscript is updated.


## 2026-08-06 — Stage 4 convergence amendment and Stage 5 structural models

The archived imputation and observation-weighting process was reconstructed exactly from the frozen analysis-ready dataset. Twenty deterministic imputations and four archived diagnostic outputs reproduced byte for byte. Restoring warnings revealed that 17 of the 20 primary denominator observation models reached the archived 500-iteration limit. The archived numerical outputs remained exactly reproducible, but convergence had not been demonstrated.

The canonical analysis retains the same logistic models, variables, interactions, regularization, solver, tolerance, probability clipping, stabilized-weight numerator, 1st/99th percentile trimming, and mean-one normalization. Only the permitted maximum iterations increased from 500 to 2,000. All primary denominator models then converged, requiring 419 to 665 iterations. The largest normalized-weight change was 0.0158, mean effective sample size changed from 2,365.786 to 2,365.769, and the residual balance pattern was unchanged.

Stage 5 loads the exact Stage 4 completed datasets. Legacy mode uses the archived weights and 500-iteration limit to reproduce the historical model suite. Fourteen archived result CSVs reproduced byte for byte. Canonical mode uses the converged primary weights and a 2,000-iteration limit for every recomputed sensitivity, subgroup, and alternative observation model. All 200 additional canonical weight-model fits converged, with a maximum of 797 iterations.

The canonical primary results were Wald chi-square 29.0083 (5 df, p=0.0000231), profile 5 versus profile 3 difference 0.2757 percentage points (95% CI -0.1516 to 0.7031; p=0.2060), and global profile-by-CAH interaction Wald chi-square 7.1932 (5 df; p=0.2067). All primary manuscript values remained unchanged at the reported precision, and no p-value inference at alpha 0.05 changed across the reconciled primary, secondary, interaction, stratified, or sensitivity results.

## 2026-09-04 — Release-environment contract canonicalization

Final-release testing discovered that the four historically validated Stage 4
artifact hashes were not reproducible in the newly locked release environment.
The preserved manuscript identified CPython 3.13.5, but controlled macOS arm64 and
Ubuntu x86-64 replays with that Python version and the documented direct dependencies
reproduced zero of the four historical hashes. The exact original numerical backend
was not preserved. The historical hashes remain unchanged as provenance under
`historical_reference_output_sha256`; they are not characterized as erroneous.

The normative release target remains Ubuntu 24.04 x86-64, CPython 3.13.14, pip
26.2.1, and the exact dependency lock. Two independent fresh QEMU environments using
that specification produced byte-identical outputs for all 14 Stage 4, 16 Stage 5,
and 16 Stage 6 generated publication artifacts. The deterministic Stage 6 validation
summary was then reproduced independently and added as its seventeenth contracted
file. Exact release-environment hashes therefore
replace the irrecoverable historical bytes as the fail-closed v1.0.0 execution gate.
This decision does not claim cross-platform bitwise identity.

The Stage 7.3C2 comparison matched 1,110 historical scientific values, including 95
unique hypothesis tests. Although 699 full-precision values differed, no significance,
estimate-sign, confidence-interval, FDR, primary-scientific, or substantive-manuscript
conclusion changed. Nine manuscript display locations and 49 publication-table cells
will be synchronized only after the final all-data reproduction succeeds. No model,
estimand, covariate, imputation or weighting specification, random seed, numerical
setting, outcome definition, or interpretation was changed in this contract migration.
