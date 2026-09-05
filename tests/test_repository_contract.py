from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

from src.release_contracts import validate_artifact_contract

ROOT = Path(__file__).resolve().parents[1]


def test_expected_results_are_official_release_results() -> None:
    payload = json.loads((ROOT / "config" / "expected_results.json").read_text())
    assert payload["status"] == "official_release_results"
    assert payload["provenance"]["independently_reproduced_environments"] == 2


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
        "CITATION.cff",
        "LICENSE",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-lock.txt",
        "run_all.py",
        "data/raw/README.md",
        "config/computational_environment.json",
        "config/data_rights.json",
        "config/expected_results.json",
        "config/stage4_release_contract.json",
        "config/stage5_source_contract.json",
        "config/stage5_release_contract.json",
        "config/stage6_release_contract.json",
        "docs/computational_environment.md",
        "docs/data_rights_and_availability.md",
        "docs/numerical_reproducibility.md",
        "docs/release_validation_procedure.md",
    ]
    assert not [path for path in required if not (ROOT / path).exists()]


def test_scholarly_metadata_contains_only_reviewed_prerelease_facts() -> None:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert citation.startswith("cff-version: 1.2.0\n")
    assert "type: software" in citation
    assert "family-names: Elechi" in citation
    assert 'given-names: "Ubalaeze Solomon"' in citation
    assert 'orcid: "https://orcid.org/0009-0002-3474-1002"' in citation
    assert "Lee Business School, University of Nevada, Las Vegas" in citation
    assert "repository-code: " in citation
    assert "license: MIT" in citation
    forbidden_fields = {
        "email",
        "doi",
        "version",
        "date-released",
        "preferred-citation",
    }
    present_fields = {
        line.lstrip().split(":", 1)[0]
        for line in citation.splitlines()
        if ":" in line
    }
    assert not (forbidden_fields & present_fields)


def test_mit_license_is_locked_to_the_approved_standard_text() -> None:
    license_bytes = (ROOT / "LICENSE").read_bytes()
    assert hashlib.sha256(license_bytes).hexdigest() == (
        "8e75f2d0d79f73ddc0eef8aceba1a36ba463c8124757e01d8f3ac57223b37fc5"
    )


def test_data_rights_inventory_matches_raw_manifest_and_holds_ahrq() -> None:
    raw = json.loads((ROOT / "config/raw_sources.json").read_text(encoding="utf-8"))
    rights = json.loads(
        (ROOT / "config/data_rights.json").read_text(encoding="utf-8")
    )
    raw_filenames = {item["filename"] for item in raw["sources"]}
    by_filename = {item["study_filename"]: item for item in rights["sources"]}
    assert set(by_filename) == raw_filenames
    assert rights["manifest_snapshot_date"] == raw["snapshot_date"] == "2026-08-05"
    assert "not asserted to be the original retrieval" in rights["date_semantics"]
    assert {
        filename: item["redistribution_status"]
        for filename, item in by_filename.items()
    } == {
        "hospital_network_participation.csv": "eligible_with_attribution",
        "cms_hospital_general_information.csv": "eligible",
        "HCAHPS-Hospital.csv": "eligible",
        "chsp-hospital-linkage-2023.csv": "hold_pending_clarification",
        "Ruralurbancontinuumcodes2023.csv": "eligible_with_attribution",
    }
    ahrq = by_filename["chsp-hospital-linkage-2023.csv"]
    assert "Do not place the raw snapshot" in ahrq["archival_disposition"]
    assert ahrq["third_party_sources"] == [
        "IQVIA OneKey",
        "American Hospital Association information",
    ]


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
    validated = contract["official_release_environment"]
    assert validated["python_version"] == "3.13.14"
    assert validated["pip_version"] == "26.2.1"
    assert validated["operating_system"] == "ubuntu"
    assert validated["operating_system_version"] == "24.04"
    assert validated["architecture"] == "x86_64"
    assert validated["github_actions_runner"] == "ubuntu-24.04"

    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert 'python-version: "3.13.14"' in workflow
    assert 'python -m pip install "pip==26.2.1"' in workflow
    assert "requirements-lock.txt" in workflow


def test_release_contracts_cover_all_deterministic_artifacts() -> None:
    expected_counts = {
        "stage4_release_contract.json": 14,
        "stage5_release_contract.json": 16,
        "stage6_release_contract.json": 17,
    }
    for filename, expected_count in expected_counts.items():
        payload = json.loads((ROOT / "config" / filename).read_text(encoding="utf-8"))
        artifacts = payload["artifacts"]
        assert len(artifacts) == expected_count
        assert len({item["path"] for item in artifacts}) == expected_count
        assert all(item["bytes"] > 0 for item in artifacts)
        assert all(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in artifacts)
        assert all(item["semantic_role"] for item in artifacts)


def test_historical_stage4_hashes_are_preserved_separately_from_release_gate() -> None:
    spec = json.loads((ROOT / "config/stage4_analysis_spec.json").read_text())
    assert spec["historical_reference_output_sha256"] == {
        "imputation_diagnostics.csv": "828ad7d78f9bd38c304a38d524c008325d0c108b88f5bd962018ba529b006de6",
        "weight_diagnostics.csv": "1dacb33acccf60e511cae10a39428b6347320279de5ccf05570b960bacc3b5a3",
        "balance_diagnostics.csv": "785a58292ca16d26425db63149882e508b37c5859c110fec4339e656385d8f96",
        "balance_diagnostics_by_stratum.csv": "838abb916b80e3cf39011757d4d48876c84f8bbbbd970c1aae0f8a5dafd8e6e7",
    }
    release = json.loads((ROOT / "config/stage4_release_contract.json").read_text())
    release_hashes = {item["sha256"] for item in release["artifacts"]}
    assert not (set(spec["historical_reference_output_sha256"].values()) & release_hashes)
    assert "historical_reference_output_sha256" not in release


def test_release_artifact_contract_fails_on_altered_output(tmp_path: Path) -> None:
    artifact = tmp_path / "result.csv"
    artifact.write_bytes(b"canonical\n")
    expected_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "path": "result.csv",
                        "bytes": artifact.stat().st_size,
                        "sha256": expected_sha,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert validate_artifact_contract(tmp_path, contract)["all_exact"] is True
    artifact.write_bytes(b"altered\n")
    with pytest.raises(RuntimeError, match="Release artifact contract mismatch"):
        validate_artifact_contract(tmp_path, contract)


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
