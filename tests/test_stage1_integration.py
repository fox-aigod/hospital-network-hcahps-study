from __future__ import annotations

from pathlib import Path

import pytest

from src.build_stage1_cohort import build_stage1_cohort
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


def test_archived_raw_files_and_locked_stage1_counts() -> None:
    report = verify_raw_sources(ROOT)
    assert report["all_verified"] is True

    summary = build_stage1_cohort(ROOT)
    assert summary["onc"]["raw_rows"] == 3393
    assert summary["onc"]["missing_ccn_rows"] == 12
    assert summary["onc"]["unique_usable_ccns"] == 3380
    assert summary["linkage"]["matched_unique_onc_ccns"] == 3293
    assert summary["linkage"]["eligible_acute_and_cah_all_years"] == 3250

    locked = summary["locked_2024_2025_cohort"]
    assert locked["total"] == 2651
    assert locked["acute_care"] == 1871
    assert locked["critical_access"] == 780
    assert locked["survey_year_2024"] == 362
    assert locked["survey_year_2025"] == 2289
    assert locked["unique_ccns"] == 2651
