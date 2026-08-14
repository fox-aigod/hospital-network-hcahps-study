from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_expected_results_are_explicitly_provisional() -> None:
    payload = json.loads((ROOT / "config" / "expected_results.json").read_text())
    assert payload["status"] == "provisional_validation_targets"


def test_locked_cohort_counts_reconcile() -> None:
    payload = json.loads((ROOT / "config" / "expected_results.json").read_text())
    cohort = payload["cohort"]
    assert cohort["acute_care"] + cohort["critical_access"] == cohort["total"]
    assert cohort["primary_outcome_observed"] <= cohort["total"]


def test_primary_interval_contains_estimate() -> None:
    payload = json.loads((ROOT / "config" / "expected_results.json").read_text())
    model = payload["primary_model"]
    assert model["profile_5_vs_3_ci_low_pp"] <= model["profile_5_vs_3_estimate_pp"]
    assert model["profile_5_vs_3_estimate_pp"] <= model["profile_5_vs_3_ci_high_pp"]


def test_repository_contract_files_exist() -> None:
    required = [
        "README.md",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-lock.txt",
        "run_all.py",
        "data/raw/README.md",
        "config/computational_environment.json",
        "config/expected_results.json",
        "config/stage5_source_contract.json",
        "docs/computational_environment.md",
        "docs/release_validation_procedure.md",
    ]
    assert not [path for path in required if not (ROOT / path).exists()]


def test_dependency_contract_separates_runtime_test_and_unused_packages() -> None:
    runtime = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    development = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
    locked = (ROOT / "requirements-lock.txt").read_text(encoding="utf-8").splitlines()
    runtime_names = {line.split("==", 1)[0].lower() for line in runtime if "==" in line}
    development_names = {
        line.split("==", 1)[0].lower() for line in development if "==" in line
    }
    locked_names = {line.split("==", 1)[0].lower() for line in locked if "==" in line}

    assert runtime_names <= locked_names
    assert development_names <= locked_names
    assert "pytest" not in runtime_names
    assert "pytest" in development_names
    assert not ({"openpyxl", "jupyter", "nbconvert"} & locked_names)


def test_machine_readable_environment_contract_matches_ci_lock() -> None:
    contract = json.loads(
        (ROOT / "config/computational_environment.json").read_text(encoding="utf-8")
    )
    validated = contract["validated_environment"]
    assert validated["python_version"] == "3.13.14"
    assert validated["pip_version"] == "26.2.1"
    assert validated["operating_system"] == "Ubuntu 24.04 LTS"
    assert validated["architecture"] == "x86_64"
    assert validated["github_actions_runner"] == "ubuntu-24.04"

    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert 'python-version: "3.13.14"' in workflow
    assert 'python -m pip install "pip==26.2.1"' in workflow
    assert "requirements-lock.txt" in workflow


def test_github_actions_contract_is_read_only_and_immutably_pinned() -> None:
    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in workflow
    assert "runs-on: ubuntu-24.04" in workflow
    assert "persist-credentials: false" in workflow
    uses = re.findall(r"^\s*uses:\s*(\S+)$", workflow, flags=re.MULTILINE)
    assert uses == [
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
    ]
    assert all(re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", item) for item in uses)


def test_generated_stage5_and_stage6_outputs_are_gitignored() -> None:
    generated_paths = [
        "outputs/stage5/canonical/analysis_summary.json",
        "outputs/stage5/legacy/primary_model_coefficients.csv",
        "outputs/stage5/reconciliation/stage5_summary.json",
        "outputs/stage6/tables/stage6_validation_summary.json",
        "outputs/stage6/figures/figure_1_cohort_flow.png",
    ]
    for path in generated_paths:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", path],
            cwd=ROOT,
            check=False,
        )
        assert result.returncode == 0, f"Generated output is not ignored: {path}"
