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

### AHRQ identifier handling

The AHRQ file contains 6,800 rows. Of these, 154 use alphanumeric federal identifiers and 124 have no CCN. After excluding those 278 rows, 6,522 unique valid numeric CCNs remain. There are no duplicate valid numeric CCNs in the archived file.

The earlier linkage script stripped alphabetic suffixes before matching. That created artificial duplicate identifiers for two cohort hospitals, `050006` and `050014`, even though the correct numeric AHRQ rows were ultimately selected through state, acute-hospital status, and name concordance. The canonical pipeline excludes the federal identifiers first. These two records are now correctly labeled `Exact CCN` rather than `Duplicate CCN resolved...`. No covariate or analytical value changed.

### AHRQ linkage result

AHRQ matched 2,624 of 2,651 hospitals. Twenty-seven hospitals lack a same-CCN row in the 2023 AHRQ file and remain in the cohort with missing AHRQ/HCRIS variables.

### USDA geography rules

The RUCC stage first attempts exact normalized county matching, then spacing and punctuation normalization. Remaining cases use explicit configuration rather than fuzzy matching:

- Connecticut hospital cities are mapped to the nine 2023 planning regions.
- Valdez and Cordova are mapped from the former Valdez-Cordova Census Area to Chugach Census Area.
- Five documented county-name aliases or typographic corrections are stored in `config/geography_crosswalks.json`.

The final method counts are:

- 2,581 exact normalized county matches
- 37 spacing or punctuation normalization matches
- 21 Connecticut planning-region crosswalks
- 10 documented county-name alias corrections
- 2 Alaska post-split crosswalks

All 2,651 hospitals received a 2023 RUCC code.

### Covariate derivations

- Health-system affiliation equals 1 when a matched AHRQ row contains a Compendium system ID and 0 when a matched row has no system ID.
- AHRQ/HCRIS ownership codes 1 and 3 are nonprofit, code 2 is government, and code 5 is for-profit.
- CMS ownership is mapped independently to nonprofit, government, or for-profit for the required sensitivity analysis.
- Bed size is transformed as `log2(beds + 1)` and categorized as `<25`, `25–99`, `100–399`, or `≥400`.
- Metro is RUCC 1–3; nonmetro is RUCC 4–9.
- Complete required covariates means all eight locked covariates are observed before imputation.

### Validation result

- AHRQ matched: 2,624/2,651
- RUCC matched: 2,651/2,651
- Complete required covariates: 2,580/2,651
- Acute Care complete: 1,826/1,871
- Critical Access complete: 754/780
- Ownership both observed: 2,600
- Ownership agreement: 1,588
- Ownership disagreement: 1,012

The regenerated 63-column analysis-ready file was compared cell by cell with the frozen file. All substantive values matched across all 2,651 hospitals. The only differences were the two corrected AHRQ match-status labels described above.
