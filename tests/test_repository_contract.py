from __future__ import annotations

import json
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
        "run_all.py",
        "data/raw/README.md",
        "config/expected_results.json",
    ]
    assert not [path for path in required if not (ROOT / path).exists()]


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
