"""Canonical command-line entry point for the reproducible analysis pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.build_stage1_cohort import build_stage1_cohort
from src.build_stage2_hcahps import build_stage2_hcahps
from src.build_stage3_confounders import build_stage3_confounders
from src.verify_raw_sources import verify_raw_sources

ROOT = Path(__file__).resolve().parent


def validate_structure() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / "config" / "expected_results.json",
        ROOT / "config" / "raw_sources.json",
        ROOT / "config" / "geography_crosswalks.json",
        ROOT / "data" / "raw" / "README.md",
        ROOT / "src" / "build_stage1_cohort.py",
        ROOT / "src" / "build_stage2_hcahps.py",
        ROOT / "src" / "build_stage3_confounders.py",
        ROOT / "src" / "verify_raw_sources.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required repository files are missing: {missing}")

    targets = json.loads(
        (ROOT / "config" / "expected_results.json").read_text(encoding="utf-8")
    )
    if targets.get("status") != "provisional_validation_targets":
        raise ValueError("Expected-results status is not explicitly provisional.")


def run_stage1() -> dict:
    summary = build_stage1_cohort(ROOT)
    locked = summary["locked_2024_2025_cohort"]
    print(
        "Stage 1 passed: "
        f"{locked['total']} hospitals "
        f"({locked['acute_care']} acute care; "
        f"{locked['critical_access']} critical access)."
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["validate", "verify-raw", "stage1", "stage2", "stage3"],
        default="validate",
    )
    args = parser.parse_args()

    validate_structure()
    if args.stage == "validate":
        print("Repository structure validation passed.")
        return

    report = verify_raw_sources(ROOT)
    if args.stage == "verify-raw":
        print(f"Verified {len(report['results'])} archived raw source files.")
        return

    run_stage1()
    if args.stage == "stage1":
        return

    summary = build_stage2_hcahps(ROOT)
    primary = summary["primary_outcome"]
    print(
        "Stage 2 passed: primary HCAHPS outcome observed for "
        f"{primary['observed_total']} hospitals "
        f"({primary['acute_observed']} acute care; "
        f"{primary['cah_observed']} critical access)."
    )
    if args.stage == "stage2":
        return

    summary3 = build_stage3_confounders(ROOT)
    complete = summary3["complete_required_covariates"]
    print(
        "Stage 3 passed: AHRQ matched "
        f"{summary3['ahrq_linkage']['matched']} hospitals; RUCC matched "
        f"{summary3['rucc_linkage']['matched']}; complete required "
        f"covariates for {complete['complete_n']} hospitals."
    )


if __name__ == "__main__":
    main()
