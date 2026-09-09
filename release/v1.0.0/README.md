# Curated v1.0.0 aggregate release artifacts

This directory is the curated preservation copy of deterministic aggregate
scientific outputs prepared for the future v1.0.0 software/reproducibility
release. Preparing this directory does not create a Git tag, GitHub Release,
Zenodo record, DOI, or publication claim.

All Stage 5 and Stage 6 contract artifacts were copied byte for byte from the
preserved Stage 7.3R execution in the locked Ubuntu 24.04 x86-64 environment.
Their original computational paths, exact sizes, SHA-256 hashes, semantic roles,
data levels, and rights notes are recorded in `release_manifest.json`. The
authoritative working-path counterparts and hashes remain defined by
`config/stage5_release_contract.json` and `config/stage6_release_contract.json`.

The directory contains:

- all 16 canonical Stage 5 aggregate or model-level artifacts;
- all 17 Stage 6 contract artifacts, including five publication figures;
- the historical Stage 6 pre-synchronization manuscript audit under an explicit
  historical filename;
- the historical Stage 6 validation summary under an explicit historical
  filename; and
- the separate final Stage 7.5 manuscript-value audit, which contains 41 passing
  checks and zero mismatches.

The Stage 6 contract was created before the final Stage 7.4/7.5 manuscript
synchronization. Its byte-exact `manuscript_value_audit.csv` records 39 passing
checks and two expected historical display differences. It is preserved as
`audits/historical_presynchronization_manuscript_value_audit.csv`; it must not be
interpreted as the final document audit. The final zero-mismatch record is
`audits/final_manuscript_value_audit.csv` and is fingerprinted separately from
the Stage 6 contract.

The `postreview/` directory records the controlled Stage 7.7B correction round:
aggregate hospital-group stratified analyses, the post-review flexible bed-size
diagnostic, finite-multiple-imputation D1 and state-cluster reference audits, and
the expanded final manuscript-value audit. These are diagnostic/provenance
artifacts; the canonical primary analysis and its 16 Stage 5 artifact bytes are
unchanged. The six `p_value=0` fields in `stage5/adjusted_profile_means.csv`
are tests of adjusted means against zero, not inferential profile-comparison
p-values; the file remains byte-identical to its validated contract.

Raw inputs, hospital-level datasets, completed imputations, observation-weight
arrays, row-level linkage diagnostics, and restricted derivatives are
intentionally excluded. Users can regenerate the outputs after lawfully
acquiring the exact source snapshots listed in `config/raw_sources.json` and
passing the checksum gate.

The AHRQ Hospital Linkage source and all row-level derivatives containing AHRQ-,
IQVIA OneKey-, or AHA-linked fields are not redistributed. See `RIGHTS.md` and
`docs/data_rights_and_availability.md` before reusing any artifact.

Verify the curated tree with:

```bash
shasum -a 256 -c release/v1.0.0/SHA256SUMS.txt
pytest -q tests/test_curated_release.py
```
