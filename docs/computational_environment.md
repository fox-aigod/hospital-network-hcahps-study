# Computational environment

## Normative release environment

The v1.0.0 computational-reproduction target is CPython 3.13.14 on Ubuntu
24.04 LTS, x86-64, with four virtual CPUs and pip 26.2.1.
config/computational_environment.json is the machine-readable authority.
requirements-lock.txt fixes every direct and transitive Python distribution.
The validated numerical backend is OpenBLAS 0.3.30 using pthreads, the Katmai
kernel, and four threads. The standard numerical thread environment variables
are unset.

The independently tested environments were built from the same verified Ubuntu
image and separately built from the signed Python.org source. The image,
CPython source, and requirements-lock SHA-256 values are recorded in the
machine-readable contract. Stage 4 through Stage 6 reproduced byte-for-byte
between the two fresh virtual machines.

The direct dependency files have separate purposes:

- requirements.txt contains packages imported by the scientific runtime.
- requirements-dev.txt adds pytest for repository validation.
- requirements-lock.txt is the complete exact release and CI environment.

The lock preserves the validated versions and does not authorize upgrades.

## Historical manuscript environment

Preserved manuscript and supplement text establish CPython 3.13.5 with NumPy
2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3, and statsmodels 0.14.6
as the historical manuscript environment. That fact remains provenance, but it
does not define the release target. Controlled CPython 3.13.5 replays on
macOS arm64 and Ubuntu x86-64 each reproduced zero of the four historical
Stage 4 hashes. Python 3.13.5 therefore did not recover the unrecorded original
numerical backend and is not a superior reproducibility target.

## Dependency audit

| Classification | Packages | Basis |
| --- | --- | --- |
| Runtime | numpy, pandas, scipy, statsmodels, scikit-learn, joblib, matplotlib, Pillow | Imported by Stages 1–6 or the assembled Stage 5 program. Pillow validates Stage 6 images. |
| Test/development | pytest | Imported only by the test suite. |
| Not used by a tracked reproducibility path | openpyxl, jupyter, nbconvert | No tracked stage reads/writes Excel, executes notebooks, or converts notebooks. |

## Rebuilding the lock

Regenerate the lock only in a clean four-vCPU x86-64 Ubuntu 24.04 environment
with CPython 3.13.14:

    python3.13 -m venv .venv
    . .venv/bin/activate
    python -m pip install "pip==26.2.1"
    python -m pip install --requirement requirements-dev.txt
    python -m pip freeze --exclude pip > requirements-lock.txt
    python -m pip check

Review every changed direct and transitive version. A dependency change requires
new scientific validation and must not be treated as a formatting-only refresh.

Install the official release environment with:

    python -m pip install "pip==26.2.1"
    python -m pip install --requirement requirements-lock.txt
    python -m pip check

Ordinary GitHub Actions uses the same Python, pip, lock, and Ubuntu release but
does not possess the archived raw data. Full contract reproduction is therefore
performed only by the separate all-data release-validation procedure.
