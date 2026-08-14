# Full release-validation procedure

This procedure is designed for the final release candidate. It is intentionally not part of ordinary push and pull-request CI because the five exact archived raw snapshots are not stored in Git.

## Preconditions

1. Use an isolated x86-64 Ubuntu 24.04 environment with CPython 3.13.14 and pip 26.2.1.
2. Check out the exact reviewed release-candidate commit with no uncommitted files.
3. Install `requirements-lock.txt` and require `python -m pip check` to pass.
4. Place all five canonical files listed in `config/raw_sources.json` under `data/raw/`. Do not download or substitute refreshed files during validation.
5. Record the commit SHA, operating-system release, architecture, Python version, pip version, and `python -m pip freeze --all` output in an environment manifest.

## Fail-closed raw-source gate

Run:

```bash
python run_all.py --stage verify-raw
```

The release run must stop on a missing file or any byte-size, row-count, column-count, or SHA-256 mismatch. The five calculated SHA-256 values and the matching `config/raw_sources.json` entries must be copied into the release-validation report.

## Complete scientific execution

Run the canonical pipeline through the Stage 6 entry point:

```bash
python run_all.py --stage stage6
```

This executes raw verification and Stages 1–6 in dependency order. Preserve the console log. Do not continue if a stage fails, emits an unreviewed warning, or changes a locked scientific decision.

## Complete tests and integrity checks

With all raw and generated files still present, run:

```bash
python run_all.py --stage validate
pytest -q -rs
python -m compileall -q run_all.py src scripts
python -m json.tool config/raw_sources.json >/dev/null
```

The final report must show that every data-dependent integration test ran rather than skipped. It must also record the Stage 5 fragment count, assembled byte count, expected and observed SHA-256, and successful compilation.

## Result-contract reconciliation

Require all of the following before release:

- every legacy Stage 5 archived-output hash matches `config/stage5_analysis_spec.json`;
- the canonical Stage 5 convergence and manuscript-value reconciliation reports have zero failures;
- Stage 6's machine-readable manuscript-value audit has zero failures;
- regenerated cohort counts and primary estimates reconcile with `config/expected_results.json` at the documented precision;
- canonical result CSVs, publication tables, figures, diagnostics, and balance summaries are present and internally consistent;
- `git status --short` shows no unintended tracked-file modification after the run.

## Required validation records

Create, review, and archive two machine-readable/text records with the final release artifacts:

1. An environment manifest containing the commit SHA, UTC run time, OS and architecture, exact Python and pip versions, the full direct/transitive package list, and NumPy/SciPy numerical configuration.
2. A release-validation report containing raw-file checksums, commands and exit statuses, test pass/fail/skip counts, Stage 1–6 summaries, Stage 5 source-integrity values, result-contract reconciliation, warnings, and reviewer sign-off.

This document defines the later procedure only. It does not authorize fetching data, publishing the repository, creating a tag or release, or uploading an archive.
