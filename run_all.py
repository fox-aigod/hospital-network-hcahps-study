"""Canonical command-line entry point for the reproducible analysis pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.build_stage1_cohort import build_stage1_cohort
from src.verify_raw_sources import verify_raw_sources

ROOT = Path(__file__).resolve().parent


def validate_structure() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / "config" / "expected_results.json",
        ROOT / "config" / "raw_sources.json",
        ROOT / "data" / "raw" / "README.md",
        ROOT / "src" / "build_stage1_cohort.py",
        ROOT / "src" / "verify_raw_sources.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required repository files are missing: {missing}")

    targets = json.loads((ROOT / "config" / "expected_results.json").read_text())
    if targets.get("status") != "provisional_validation_targets":
        raise ValueError("Expected-results status is not explicitly provisional.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["validate", "verify-raw", "stage1"],
        default="validate",
    )
    args = parser.parse_args()

    validate_structure()
    if args.stage == "validate":
        print("Repository structure validation passed.")
        return
    if args.stage == "verify-raw":
        report = verify_raw_sources(ROOT)
        print(f"Verified {len(report['results'])} archived raw source files.")
        return

    verify_raw_sources(ROOT)
    summary = build_stage1_cohort(ROOT)
    locked = summary["locked_2024_2025_cohort"]
    print(
        "Stage 1 passed: "
        f"{locked['total']} hospitals "
        f"({locked['acute_care']} acute care; "
        f"{locked['critical_access']} critical access)."
    )


if __name__ == "__main__":
    main()
