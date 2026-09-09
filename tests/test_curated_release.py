from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release" / "v1.0.0"
MANIFEST = RELEASE / "release_manifest.json"
CHECKSUMS = RELEASE / "SHA256SUMS.txt"

FORBIDDEN_FILENAMES = {
    "hospital_network_participation.csv",
    "cms_hospital_general_information.csv",
    "HCAHPS-Hospital.csv",
    "chsp-hospital-linkage-2023.csv",
    "Ruralurbancontinuumcodes2023.csv",
}
FORBIDDEN_SUFFIXES = {
    ".docx",
    ".npy",
    ".npz",
    ".parquet",
    ".pickle",
    ".pkl",
}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def release_files() -> set[str]:
    return {
        path.relative_to(RELEASE).as_posix()
        for path in RELEASE.rglob("*")
        if path.is_file()
    }


def test_curated_release_manifest_is_complete_and_exact() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0.0"
    assert payload["release_candidate"] == "v1.0.0"
    assert payload["preparation_source_head"] == (
        "15192c198d2c9f14248412f00246c84384857efb"
    )
    assert payload["preparation_source_tree"] == (
        "34f838160245cd9f21e67180749ba8e12768a0f3"
    )
    assert payload["stage5_release_contract"]["artifacts_reviewed"] == 16
    assert payload["stage5_release_contract"]["artifacts_included"] == 16
    assert payload["stage5_release_contract"]["artifacts_excluded"] == 0
    assert payload["stage6_release_contract"]["artifacts_reviewed"] == 17
    assert payload["stage6_release_contract"]["artifacts_included"] == 17
    assert payload["stage6_release_contract"]["artifacts_excluded"] == 0
    assert payload["curated_counts"] == {
        "contract_artifacts": 33,
        "stage5_artifacts": 16,
        "stage6_artifacts": 17,
        "figures": 5,
        "audits": 3,
        "separate_final_audits": 1,
        "postreview_artifacts": 9,
        "total_scientific_and_audit_artifacts": 43,
    }

    artifacts = payload["artifacts"]
    assert len(artifacts) == 43
    required_fields = {
        "curated_path",
        "original_computational_path",
        "source_contract",
        "semantic_role",
        "byte_size",
        "sha256",
        "eligibility_classification",
        "data_level",
        "contains_row_level_data",
        "rights_note",
    }
    curated_paths = [item["curated_path"] for item in artifacts]
    assert len(curated_paths) == len(set(curated_paths))

    for item in artifacts:
        assert required_fields <= item.keys()
        relative = PurePosixPath(item["curated_path"])
        assert not relative.is_absolute()
        assert ".." not in relative.parts
        path = RELEASE / relative
        assert path.is_file()
        assert not path.is_symlink()
        assert path.stat().st_size == item["byte_size"]
        assert sha256(path) == item["sha256"]
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
        assert item["eligibility_classification"] == "PUBLIC INCLUDE"
        assert item["data_level"] in {"aggregate", "model-level", "figure", "audit"}
        assert item["contains_row_level_data"] is False
        assert item["source_contract"]
        assert item["semantic_role"]
        assert item["rights_note"]


def test_curated_release_checksum_manifest_covers_every_other_file() -> None:
    entries: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
        assert relative not in entries
        entries[relative] = digest

    assert set(entries) == release_files() - {"SHA256SUMS.txt"}
    assert len(entries) == 46
    for relative, expected in entries.items():
        assert sha256(RELEASE / relative) == expected


def test_curated_release_excludes_restricted_and_private_material() -> None:
    files = [path for path in RELEASE.rglob("*") if path.is_file()]
    assert not [path for path in files if path.name in FORBIDDEN_FILENAMES]
    assert not [path for path in files if path.suffix.lower() in FORBIDDEN_SUFFIXES]
    assert not [path for path in RELEASE.rglob("*") if path.is_symlink()]

    forbidden_text_patterns = {
        "personal email": re.compile(
            re.escape("elechiuba" + "@" + "gmail.com"), re.IGNORECASE
        ),
        "any email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
        "macOS absolute path": re.compile(r"/Users/"),
        "Linux home path": re.compile(r"/home/"),
        "Google Drive link": re.compile(r"https?://(?:drive|docs)\.google\.com", re.IGNORECASE),
        "private GitHub URL": re.compile(r"https?://github\.com/[^\s]+(?:private|token)", re.IGNORECASE),
        "private key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    }
    findings: list[str] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in forbidden_text_patterns.items():
            if pattern.search(text):
                findings.append(f"{label}: {path.relative_to(RELEASE)}")
    assert not findings


def test_historical_and_final_manuscript_audits_are_distinguished() -> None:
    historical_path = (
        RELEASE / "audits" / "historical_presynchronization_manuscript_value_audit.csv"
    )
    final_path = RELEASE / "audits" / "final_manuscript_value_audit.csv"

    with historical_path.open(newline="", encoding="utf-8") as stream:
        historical = list(csv.DictReader(stream))
    with final_path.open(newline="", encoding="utf-8") as stream:
        final = list(csv.DictReader(stream))

    assert len(historical) == 41
    assert sum(row["status"] == "PASS" for row in historical) == 39
    assert sum(row["status"] == "FAIL" for row in historical) == 2
    assert len(final) == 41
    assert all(row["status"] == "PASS" for row in final)


def test_final_postcorrection_audits_are_complete_and_zero_mismatch() -> None:
    numeric_path = RELEASE / "postreview" / "final_comprehensive_manuscript_value_audit.csv"
    table_path = RELEASE / "postreview" / "final_table_cell_audit.csv"
    with numeric_path.open(newline="", encoding="utf-8") as stream:
        numeric = list(csv.DictReader(stream))
    with table_path.open(newline="", encoding="utf-8") as stream:
        table = list(csv.DictReader(stream))
    assert len(numeric) == 71
    assert len(table) == 812
    assert all(row["status"] == "PASS" for row in numeric)
    assert all(row["status"] in {"PASS", "PASS_NORMALIZED"} for row in table)
    assert {row["table"] for row in table} >= {
        "manuscript_table_1.csv", "manuscript_table_2.csv", "manuscript_table_3.csv",
        "supplement_table_S1.csv", "supplement_table_S2.csv", "supplement_table_S3.csv",
        "supplement_table_S4.csv", "supplement_table_S5.csv", "supplement_table_S6.csv",
        "supplement_table_S7.csv", "supplement_table_S8.csv",
    }
    assert sum(row["document"] == "supplement" and row["metric"].startswith("D1 ") for row in numeric) == 6
    assert sum(row["document"] == "supplement" and "small-sample" in row["metric"] for row in numeric) == 2
    assert sum(row["document"] == "supplement" and row["metric"].startswith("Flexible-size") for row in numeric) == 4
