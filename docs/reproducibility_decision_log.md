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

## 2026-08-06 — Numeric CCN namespace and HCAHPS linkage

### Identifier decision

CMS Hospital General Information and hospital-level HCAHPS include federal facility identifiers containing alphabetic suffixes, such as `10021F`. These values are not six-digit Medicare CCNs. Stripping the suffix would create a false numeric identifier and could collide with a different hospital. The canonical normalizer therefore rejects any identifier containing alphabetic characters and zero-pads only genuinely numeric identifiers.

This correction excluded 164 federal facilities from the numeric CMS identifier space and 11,152 HCAHPS rows corresponding to those facilities. It did not alter the 2,651-hospital nonfederal locked cohort.

### Stage 2 rules

1. Read the archived hospital-level HCAHPS file without replacing suppression text.
2. Exclude nonnumeric facility identifiers from numeric CCN linkage.
3. Require one row per valid numeric CCN and measure identifier.
4. Require a single reporting period in the archived file.
5. Preserve the primary outcome footnote, completed-survey count, response rate, and reporting dates.
6. Convert only published numeric values to numbers; suppressed and unavailable strings remain missing.
7. Link the prespecified primary, secondary, and linear-mean outcomes one-to-one by CCN.
8. Generate outcome-availability and footnote audits directly from code.

### Stage 2 validation result

The clean rerun found 325,856 HCAHPS rows, 4,792 raw facility identifiers, 4,628 valid numeric CCNs, 68 measure identifiers, no duplicate valid facility-measure keys, and one reporting period from July 1, 2024 through June 30, 2025.

All 2,651 locked hospitals were present in HCAHPS. The primary outcome was observed for 2,409 hospitals: 1,852 Acute Care Hospitals and 557 Critical Access Hospitals. The discharge-information linear mean was observed for 1,988 hospitals: 1,765 Acute Care Hospitals and 223 Critical Access Hospitals.

The rebuilt HCAHPS cohort matched the preserved cohort on all 2,651 CCNs and all tested outcome, availability, footnote, survey-count, response-rate, and date fields. No mismatches were observed.
