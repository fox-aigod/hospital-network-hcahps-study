# Full release-validation procedure

This fail-closed procedure is for a reviewed release candidate. It is separate
from ordinary push/PR CI because the five exact raw snapshots are not in Git.

## Preconditions and environment manifest

1. Use a fresh four-vCPU x86-64 Ubuntu 24.04 environment that exactly matches
   config/computational_environment.json: CPython 3.13.14, pip 26.2.1,
   requirements-lock.txt, and the recorded numerical backend.
2. Check out the reviewed release-candidate commit with a clean worktree.
3. Install requirements-lock.txt without upgrading any package and require
   python -m pip check to pass.
4. Place the five canonical files from config/raw_sources.json in data/raw/.
   Do not fetch or substitute current versions.
5. Record commit/tree SHAs, UTC time, OS/image and architecture, CPU count,
   Python and pip versions, pip freeze --all, numerical-library configuration,
   thread settings, and installer/source fingerprints in an external manifest.

## A. Exact raw-source gate

Run:

    python run_all.py --stage verify-raw

Stop on any missing file or byte-size, row-count, column-count, or SHA-256
mismatch. Record all five calculated hashes in the external validation report.

## B–D. Official environment and exact Stage 4–6 contracts

Run the canonical pipeline:

    python run_all.py --stage stage6

The pipeline first rejects a nonofficial environment. Stage 4 must reproduce
every byte and size in config/stage4_release_contract.json. Stage 5 must
reproduce every canonical result file and exact scientific payload in
config/stage5_release_contract.json. Stage 6 must reproduce the tables, audit,
manifest, and figures in config/stage6_release_contract.json; the Stage 5 CSV
contracts are the primary scientific source-data contract for figures.

The four values under historical_reference_output_sha256 in
config/stage4_analysis_spec.json are provenance from the earlier validated
analysis. They are deliberately not the v1.0.0 execution gate because their
unrecorded numerical backend could not be recovered. They must remain present
and must never be silently replaced.

## E. Complete tests with data present

Run:

    python run_all.py --stage validate
    pytest -q -rs
    python -m compileall -q run_all.py src scripts

All data-dependent integration tests must execute with zero skips. Also validate
every tracked JSON file, CITATION.cff, the 14-fragment Stage 5 assembly byte
count/SHA-256/compilation contract, and exact Stage 4–6 release contracts.

## F. Release-value and manuscript reconciliation

Require config/expected_results.json and the Stage 5 contract to match the fresh
machine-readable output exactly. Require:

- 95/95 historical comparator hypothesis decisions remain unchanged;
- zero significance, sign, confidence-interval conclusion, or FDR changes;
- zero primary or substantive manuscript conclusion changes;
- the generated manuscript audit and every proposed display synchronization
  are reconciled to official release values.

The manuscript files are not updated by this computational procedure. The
separately reviewed Stage 7.4 and 7.4A synchronization has been completed, and
Stage 7.5 finalized authorship and declarations. A release-candidate rerun must
compare its generated values with those locked final documents and require zero
unresolved numerical or table differences; it does not silently edit either
document.

## G. Tree integrity and required external report

Require git status --short to show no unintended tracked changes after the run.
Confirm every raw file and generated output remains ignored/untracked.

The external release-validation report must record commands and exit statuses,
environment fingerprints, raw checksums, test pass/fail/skip counts, Stage 1–6
summaries, warnings, all artifact-contract results, expected-results
reconciliation, manuscript reconciliation, scientific-source hashes, and
reviewer sign-off.

This procedure does not authorize publishing the repository, tagging, creating
a release, changing a license/citation record, uploading data, or creating a
Zenodo record.
