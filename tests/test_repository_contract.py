from __future__ import annotations

import json
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
