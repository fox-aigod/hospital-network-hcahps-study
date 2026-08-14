# Computational environment

## Supported release environment

The locked release environment is CPython 3.13.14 on Ubuntu 24.04 LTS, x86-64, installed with pip 26.2.1. `config/computational_environment.json` is the machine-readable environment contract. `requirements-lock.txt` records every direct and transitive Python distribution used by the repository validation suite. The numerical-library versions are also repeated in the environment contract so that they are easy to audit.

The direct dependency files have separate purposes:

- `requirements.txt` contains packages imported by the scientific runtime.
- `requirements-dev.txt` adds pytest for repository validation.
- `requirements-lock.txt` is the complete, exact release and CI environment.

The lock preserves all previously validated direct versions. It does not authorize dependency upgrades.

## Dependency audit

The tracked Python programs, source fragments, scripts, and tests were inspected as a complete execution graph.

| Classification | Packages | Basis |
| --- | --- | --- |
| Runtime | numpy, pandas, scipy, statsmodels, scikit-learn, joblib, matplotlib, Pillow | Imported by Stages 1–6 or the assembled Stage 5 program. Pillow is used by Stage 6 image validation. |
| Test/development | pytest | Imported only by the test suite. |
| Not used by a tracked reproducibility path | openpyxl, jupyter, nbconvert | No tracked stage reads or writes Excel workbooks, launches or executes notebooks, or converts notebooks. The pipeline consumes CSV/JSON/NPZ inputs and produces CSV/JSON/PNG outputs. Their indirect dependency stacks are likewise not invoked. |

Removing the unused packages changes the environment surface only; it does not change analysis code, model specifications, inputs, seeds, or results.

## Rebuilding the lock

Regenerate the lock only in a clean x86-64 Ubuntu 24.04 environment with CPython 3.13.14. Start from a clean clone and do not reuse an existing virtual environment:

```bash
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install "pip==26.2.1"
python -m pip install --requirement requirements-dev.txt
python -m pip freeze --exclude pip > requirements-lock.txt
python -m pip check
```

Review the resulting diff. A changed direct or transitive version requires a new scientific validation; it must not be accepted as a formatting-only lock refresh. Confirm that the direct versions in `requirements.txt` and `requirements-dev.txt` appear unchanged in the regenerated lock.

Install the release environment with:

```bash
python -m pip install "pip==26.2.1"
python -m pip install --requirement requirements-lock.txt
python -m pip check
```

GitHub Actions performs these same commands on the supported runner. Other operating systems may be useful for development, but they are not the locked release-validation platform.
