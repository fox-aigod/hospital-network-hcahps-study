# Reproducibility decision log

## 2026-08-06 — Canonical Stage 1 rebuild

### Decision

Rebuild the ONC-to-CMS cohort as a new, modular Python stage rather than treating the earlier compact reproduction scripts as the final computational record.

### Reason

A clean rerun of the preserved legacy sequence reproduced the initial ONC-CMS feasibility counts, but the preserved compact HCAHPS script omitted fields required by the subsequent confounder-linkage script, including county. As a result, the three compact scripts could not execute end to end without intervention.

This does **not** show that the preserved analytic dataset or manuscript values are wrong. It shows that the earlier packaged scripts were not a complete source-to-analysis pipeline and therefore cannot serve as the final reproducibility record.

### Stage 1 rules

1. Verify archived source files by SHA-256, byte count, row count, and column count.
2. Normalize CMS Certification Numbers to six characters.
3. Retain each ONC hospital's latest survey response using explicit deterministic sorting.
4. Resolve CMS duplicate identifiers deterministically rather than relying on file order.
5. Link ONC to CMS one-to-one by CCN.
6. Restrict the hospital cohort to Acute Care Hospitals and Critical Access Hospitals.
7. Lock the primary exposure cohort to ONC survey years 2024 and 2025.
8. Derive the 16-bit profile and prespecified six-category exposure in code.
9. Generate all counts and audit outputs from the script.

### Validation targets

- 3,393 raw ONC rows
- 12 ONC rows without a usable CCN
- 3,380 unique usable ONC CCNs
- 3,293 ONC-CMS matches
- 3,250 Acute Care and Critical Access Hospitals across all source years
- 2,651 hospitals in the locked 2024-2025 cohort
- 1,871 Acute Care Hospitals
- 780 Critical Access Hospitals

### Local validation result

The rebuilt Stage 1 cohort matched the preserved analysis-ready dataset on all 2,651 CCNs and on survey year, hospital group, four participation indicators, planned TEFCA, profile bits, and six-category profile assignment. No mismatches were observed in those fields.
