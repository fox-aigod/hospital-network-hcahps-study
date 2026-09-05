"""Canonical command-line entry point for the reproducible analysis pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from src.build_stage1_cohort import build_stage1_cohort
from src.build_stage2_hcahps import build_stage2_hcahps
from src.build_stage3_confounders import build_stage3_confounders
from src.build_stage4_imputation_weights import build_stage4_imputation_weights
from src.build_stage5_models import build_stage5_models
from src.build_stage6_publication_assets import build_stage6_publication_assets
from src.verify_raw_sources import verify_raw_sources

ROOT = Path(__file__).resolve().parent


def validate_structure() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "CITATION.cff",
        ROOT / "LICENSE",
        ROOT / "requirements.txt",
        ROOT / "requirements-dev.txt",
        ROOT / "requirements-lock.txt",
        ROOT / "config" / "computational_environment.json",
        ROOT / "config" / "data_rights.json",
        ROOT / "config" / "expected_results.json",
        ROOT / "config" / "raw_sources.json",
        ROOT / "config" / "stage5_source_contract.json",
        ROOT / "config" / "stage4_release_contract.json",
        ROOT / "config" / "stage5_release_contract.json",
        ROOT / "config" / "stage6_release_contract.json",
        ROOT / "data" / "raw" / "README.md",
        ROOT / "docs" / "data_rights_and_availability.md",
        ROOT / "docs" / "numerical_reproducibility.md",
        ROOT / "src" / "build_stage1_cohort.py",
        ROOT / "src" / "build_stage2_hcahps.py",
        ROOT / "src" / "build_stage3_confounders.py",
        ROOT / "src" / "build_stage4_imputation_weights.py",
        ROOT / "src" / "build_stage5_models.py",
        ROOT / "src" / "build_stage6_publication_assets.py",
        ROOT / "scripts" / "run_stage5_model_suite.py",
        ROOT / "scripts" / "build_stage6_publication_assets.py",
        ROOT / "scripts" / "generate_stage6_media.py",
        ROOT / "config" / "stage4_analysis_spec.json",
        ROOT / "config" / "stage5_analysis_spec.json",
        ROOT / "config" / "stage6_publication_spec.json",
        ROOT / "config" / "geography_crosswalks.json",
        ROOT / "src" / "verify_raw_sources.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required repository files are missing: {missing}")

    targets = json.loads(
        (ROOT / "config" / "expected_results.json").read_text(encoding="utf-8")
    )
    if targets.get("status") != "official_release_results":
        raise ValueError("Expected-results status is not the official release contract.")

    raw_sources = json.loads(
        (ROOT / "config" / "raw_sources.json").read_text(encoding="utf-8")
    )
    data_rights = json.loads(
        (ROOT / "config" / "data_rights.json").read_text(encoding="utf-8")
    )
    raw_filenames = {item["filename"] for item in raw_sources["sources"]}
    rights_filenames = {
        item["study_filename"] for item in data_rights["sources"]
    }
    if raw_filenames != rights_filenames:
        raise ValueError("Raw-source and data-rights file inventories differ.")
    allowed_rights_statuses = {
        "eligible",
        "eligible_with_attribution",
        "hold_pending_clarification",
    }
    if any(
        item["redistribution_status"] not in allowed_rights_statuses
        for item in data_rights["sources"]
    ):
        raise ValueError("Data-rights metadata contains an uncontrolled status.")

    source_contract = json.loads(
        (ROOT / "config" / "stage5_source_contract.json").read_text(
            encoding="utf-8"
        )
    )
    source_dir = ROOT / "scripts" / "stage5_source"
    parts = sorted(source_dir.glob("part_*.pyfrag"))
    if [path.name for path in parts] != source_contract["fragments"]:
        raise ValueError("Stage 5 source fragment set or order is not locked.")
    source = source_contract["separator"].join(
        path.read_text(encoding=source_contract["encoding"]) for path in parts
    )
    source_bytes = source.encode(source_contract["encoding"])
    if len(source_bytes) != source_contract["assembled_bytes"]:
        raise ValueError("Stage 5 assembled-source byte count does not match.")
    if hashlib.sha256(source_bytes).hexdigest() != source_contract["assembled_sha256"]:
        raise ValueError("Stage 5 assembled-source SHA-256 does not match.")
    compile(source, "<stage5_model_suite>", "exec")


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
        choices=["validate", "verify-raw", "stage1", "stage2", "stage3", "stage4", "stage5", "stage6"],
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
    if args.stage == "stage3":
        return

    summary4 = build_stage4_imputation_weights(ROOT)
    canonical = summary4["canonical_converged_weighting"]
    print(
        "Stage 4 passed: 20 deterministic imputations; official release "
        "artifacts reproduced exactly; canonical observation models converged with mean "
        f"effective sample size {canonical['mean_effective_sample_size']:.1f}."
    )
    if args.stage == "stage4":
        return

    summary5 = build_stage5_models(ROOT)
    primary5 = summary5["primary_canonical_results"]
    print(
        "Stage 5 passed: official release results reproduced exactly; canonical "
        "sensitivity models converged without warnings; primary global "
        f"Wald chi-square {primary5['global_wald_chi2']:.2f} and planned "
        f"contrast {primary5['profile_5_vs_3']['estimate']:.3f} percentage points."
    )
    if args.stage == "stage5":
        return

    summary6 = build_stage6_publication_assets(ROOT)
    print(
        "Stage 6 passed: generated "
        f"{summary6['main_tables']} main tables, "
        f"{summary6['supplement_tables']} supplement tables, and "
        f"{summary6['figures']} figures; acknowledged pending manuscript-display "
        f"updates in the embedded audit: {summary6['manuscript_value_audit_failures']}."
    )


if __name__ == "__main__":
    main()
