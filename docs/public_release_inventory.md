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
| Canonical Stage 5 aggregate result CSVs from the 16-file contract | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | In a separate reviewed step, copy the byte-verified aggregate CSVs into a curated release directory and commit them before the v1.0.0 tag. Do not unignore or commit transient `outputs/stage5/**`. |
| Canonical Stage 6 publication-table CSVs and machine-readable manuscript audit | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | In a separate reviewed step, copy the byte-verified aggregate files into a curated release directory and commit before the v1.0.0 tag. |
| Canonical Stage 6 figures | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | In a separate reviewed step, copy the byte-verified publication figures into a curated release directory and commit before the v1.0.0 tag, with an explicit publication-asset rights notice. |
| Aggregate weighting and balance diagnostics containing no row-level records | PUBLIC INCLUDE; ZENODO SOFTWARE RECORD INCLUDE | Curate, verify aggregation, and commit before the v1.0.0 tag; exclude any hospital-level identifiers or records. |
| Stage 4 imputation arrays, completed datasets, observation weights, and row-level diagnostics | PUBLIC EXCLUDE | Regenerated locally; not distributed because they are row-level or bulky analytical intermediates. |
| Standard GitHub-generated source archives | PUBLIC INCLUDE | Created automatically only after a separately authorized tag; no duplicate GitHub Release asset bundle is planned. |

## Generated-output decision

Canonical aggregate Stage 5 result CSVs, Stage 6 tables, figures, the
machine-readable manuscript audit, and demonstrably aggregate diagnostics will be
committed before v1.0.0 under a curated release path and included in the tagged
source archive and Zenodo software record. They will not be committed from their
ignored working paths, and they will not be duplicated as ad hoc GitHub Release
attachments. Users may regenerate them from lawful checksum-matching inputs, but
regeneration is not the sole preservation strategy.

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

Neither record exists yet. No DOI has been reserved or minted.
