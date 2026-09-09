# Candidate v1.0.0 public-release inventory

This is the reviewed disposition plan for every tracked path class and every
proposed release item. It does not create a release or authorize an upload.

## Classification definitions

- **PUBLIC INCLUDE** — may appear in the public GitHub repository and tagged
  source archive.
- **PUBLIC EXCLUDE** — must remain outside the public repository and source
  archive.
- **ZENODO DATA RECORD INCLUDE** — proposed for the separately reviewed
  data/provenance record.
- **ZENODO SOFTWARE RECORD INCLUDE** — proposed for the separately reviewed
  software/reproducibility record.
- **HOLD** — must not be distributed until the stated rights issue is resolved.

## Tracked repository inventory

Every currently tracked path is covered below.

| Tracked path or class | Classification | Reason |
| --- | --- | --- |
| `.github/workflows/validate.yml` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Read-only, SHA-pinned CI validation. |
| `.gitignore` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Prevents accidental tracking of raw, row-level, and generated files. |
| `README.md`, `CITATION.cff`, `LICENSE` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Reviewed project, citation, and software-license metadata. |
| `requirements.txt`, `requirements-dev.txt`, `requirements-lock.txt` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Direct and locked execution-environment definitions. |
| `run_all.py` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Pipeline orchestration. |
| `config/*.json` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Source fingerprints, rights status, environment, analysis specifications, expected results, and release contracts; no row-level data. |
| `data/raw/README.md` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Checksum-first restoration instructions; no data. |
| `docs/*.md` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Reproducibility, rights, validation, decision, and release-governance records. |
| `scripts/*.py` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Publication-asset and model-suite execution code. |
| `scripts/stage5_source/README.md` and 14 `.pyfrag` files | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Hash-locked executable Stage 5 source provenance. |
| `src/*.py` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Scientific pipeline source. |
| `tests/*.py` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Unit, contract, orchestration, and data-dependent integration tests. |
| `release/v1.0.0/**` | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Curated, checksum-locked aggregate Stage 5/6 results, publication tables and figures, audits, provenance manifest, and rights documentation; no raw or row-level data. |

## Untracked and proposed items

| Item | Classification | Required disposition |
| --- | --- | --- |
| `data/raw/hospital_network_participation.csv` | ZENODO DATA RECORD INCLUDE | Deposit exact snapshot with ONC/ASTP attribution and AHA provenance caveat; never commit to GitHub. |
| `data/raw/cms_hospital_general_information.csv` | ZENODO DATA RECORD INCLUDE | Deposit exact checksum-matching snapshot with CMS citation and provenance; never commit to GitHub. |
| `data/raw/HCAHPS-Hospital.csv` | ZENODO DATA RECORD INCLUDE | Deposit exact checksum-matching snapshot with CMS citation and provenance; never commit to GitHub. |
| `data/raw/Ruralurbancontinuumcodes2023.csv` | ZENODO DATA RECORD INCLUDE | Deposit exact snapshot with USDA ERS attribution; never commit to GitHub. |
| `data/raw/chsp-hospital-linkage-2023.csv` | HOLD | Do not redistribute without written clarification; data record receives only fingerprint, citation, and acquisition instructions. |
| Any row-level file under `data/interim/`, `data/processed/`, or `outputs/` containing AHRQ-, IQVIA OneKey-, or AHA-linked fields | HOLD | Do not redistribute without written clarification. |
| Other row-level intermediate or analysis-ready datasets | PUBLIC EXCLUDE | Keep outside Git and public release packages; users regenerate after lawful source acquisition. |
| Transient logs, caches, virtual environments, local manifests, temporary validation paths, forensic workspaces, pre-sanitization bundles/mirrors, and operating-system artifacts | PUBLIC EXCLUDE | Local-only material, not scholarly release content. |
| Canonical Stage 5 aggregate and model-level results from the 16-file contract | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | **ASSEMBLED:** all 16 byte-verified artifacts are under `release/v1.0.0/stage5/`; none were excluded after row-level and rights review. Transient `outputs/stage5/**` remains ignored. |
| Canonical Stage 6 publication tables, manifests, and audits | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | **ASSEMBLED:** all 12 tabular/audit artifacts from the 17-file Stage 6 contract are preserved under `release/v1.0.0/stage6/tables/` and `release/v1.0.0/audits/`. The historical audit is explicitly identified as pre-synchronization; a separately fingerprinted final Stage 7.5 audit is also included. |
| Canonical Stage 6 figures | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | **ASSEMBLED:** all five byte-verified publication figures are under `release/v1.0.0/stage6/figures/`, with the publication-asset rights notice in `release/v1.0.0/RIGHTS.md`. |
| Stage 7.7B post-review aggregate audits | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Aggregate stratified results, flexible-size diagnostic, finite-m D1/cluster references, and expanded manuscript-value audit under `release/v1.0.0/postreview/`; no raw or hospital-level records. |
| Aggregate weighting and balance diagnostics containing no row-level records | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | **ASSEMBLED:** the reviewed aggregate/model-level diagnostics are included among the 16 Stage 5 artifacts; inspection found no hospital identifiers, row-level records, or restricted linkage fields. |
| Stage 4 imputation arrays, completed datasets, observation weights, and row-level diagnostics | PUBLIC EXCLUDE | Regenerated locally; not distributed because they are row-level or bulky analytical intermediates. |
| Standard GitHub-generated source archives | PUBLIC INCLUDE | Created automatically only after a separately authorized tag; no duplicate GitHub Release asset bundle is planned. |

## Generated-output decision

Canonical aggregate Stage 5 results, Stage 6 tables and figures, the historical
machine-readable manuscript audit, the separate final zero-mismatch audit, and
demonstrably aggregate diagnostics are assembled under `release/v1.0.0/`. The
curated set contains all 16 Stage 5 contract artifacts, all 17 Stage 6 contract
artifacts (including five figures), and one separately fingerprinted final audit;
no contract artifact was excluded after row-level and rights inspection. The
curated copies do not unignore their transient working paths and are not planned
as duplicate ad hoc GitHub Release attachments. Users may regenerate them from
lawful checksum-matching inputs, but regeneration is not the sole preservation
strategy.

The post-review artifacts supplement the curated contract with transparent
diagnostic and review-resolution evidence. They do not replace any Stage 4–6
contract or alter the canonical primary result files.

No generated row-level file, Stage 4 imputation array, completed dataset, or
restricted linkage diagnostic is eligible for that curated set.

## Two-record archival model

### Record 1 — data/provenance archive

Include the exact ONC, CMS Hospital General, CMS HCAHPS, and USDA RUCC snapshots;
checksums; byte sizes and dimensions; provenance; source citations; source-specific
terms; and acquisition instructions. Include only the AHRQ fingerprint, citation,
rights note, and official acquisition instructions while redistribution remains on
hold. Apply source-specific rights metadata rather than the repository MIT License.

### Record 2 — software/reproducibility release

Include the v1.0.0 GitHub code snapshot; locked environment; source fingerprint
manifest; Stage 4–6 release contracts; curated canonical aggregate Stage 5 results;
publication tables and figures; aggregate diagnostics; machine-readable manuscript
audit; and checksums. Exclude all raw and restricted row-level data. The MIT License
applies only to original software and software-oriented documentation; rights notes
must identify any release assets governed separately.

Neither archival record exists yet. The curated software-record inputs are
assembled locally in the private repository, but no Git tag, GitHub Release,
Zenodo record, or DOI exists yet.
