from __future__ import annotations

from pathlib import Path

import pytest

from src.build_stage1_cohort import build_stage1_cohort
from src.build_stage2_hcahps import build_stage2_hcahps
from src.verify_raw_sources import verify_raw_sources

ROOT = Path(__file__).resolve().parents[1]
RAW_FILES = [
    ROOT / "data/raw/hospital_network_participation.csv",
    ROOT / "data/raw/cms_hospital_general_information.csv",
    ROOT / "data/raw/HCAHPS-Hospital.csv",
    ROOT / "data/raw/chsp-hospital-linkage-2023.csv",
    ROOT / "data/raw/Ruralurbancontinuumcodes2023.csv",
]

pytestmark = pytest.mark.skipif(
    not all(path.exists() for path in RAW_FILES),
    reason="Archived raw files are intentionally not committed to GitHub.",
)


def test_locked_hcahps_linkage_and_outcome_counts() -> None:
    verify_raw_sources(ROOT)
    build_stage1_cohort(ROOT)
    summary = build_stage2_hcahps(ROOT)

    source = summary["hcahps_source"]
    assert source["raw_rows"] == 325856
    assert source["unique_raw_facility_ids"] == 4792
    assert source["excluded_non_ccn_rows"] == 11152
    assert source["unique_valid_ccns"] == 4628
    assert source["unique_measure_ids"] == 68
    assert source["duplicate_facility_measure_rows"] == 0
    assert source["start_date"] == "07/01/2024"
    assert source["end_date"] == "06/30/2025"

    linkage = summary["linkage"]
    assert linkage["locked_hospitals"] == 2651
    assert linkage["locked_hospitals_present_in_hcahps"] == 2651
    assert linkage["locked_hospitals_absent_from_hcahps"] == 0

    primary = summary["primary_outcome"]
    assert primary["observed_total"] == 2409
    assert primary["acute_observed"] == 1852
    assert primary["cah_observed"] == 557

    linear = summary["linear_mean"]
    assert linear["observed_total"] == 1988
    assert linear["acute_observed"] == 1765
    assert linear["cah_observed"] == 223
