from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.build_stage1_cohort import build_stage1_cohort
from src.build_stage2_hcahps import build_stage2_hcahps
from src.build_stage3_confounders import build_stage3_confounders
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


def test_ahrq_rucc_linkage_and_covariate_completeness() -> None:
    verify_raw_sources(ROOT)
    build_stage1_cohort(ROOT)
    build_stage2_hcahps(ROOT)
    summary = build_stage3_confounders(ROOT)

    ahrq = summary["ahrq_source"]
    assert ahrq["raw_rows"] == 6800
    assert ahrq["alphanumeric_federal_identifier_rows"] == 154
    assert ahrq["missing_ccn_rows"] == 124
    assert ahrq["valid_numeric_ccn_rows"] == 6522
    assert ahrq["duplicate_valid_numeric_ccns_resolved"] == []

    assert summary["ahrq_linkage"]["matched"] == 2624
    assert summary["ahrq_linkage"]["unmatched"] == 27
    assert summary["rucc_linkage"]["matched"] == 2651
    assert summary["rucc_linkage"]["unmatched"] == 0

    complete = summary["complete_required_covariates"]
    assert complete["complete_n"] == 2580
    assert complete["acute_complete_n"] == 1826
    assert complete["cah_complete_n"] == 754

    ownership = summary["ownership_crosscheck"]
    assert ownership["both_observed_n"] == 2600
    assert ownership["agreement_n"] == 1588
    assert ownership["disagreement_n"] == 1012

    output = pd.read_csv(
        ROOT / "data/processed/Hospital_Network_Analysis_Ready_v1.csv"
    )
    assert len(output) == 2651
    assert output["beds"].notna().sum() == 2611
    assert output["health_system_affiliated"].notna().sum() == 2624
    assert output["uncompensated_care_burden"].notna().sum() == 2580
    assert output["rucc_2023"].notna().sum() == 2651
    assert output["rucc_match_status"].value_counts().to_dict() == {
        "Exact normalized county": 2581,
        "Exact after spacing/punctuation normalization": 37,
        "Connecticut town-to-2023 planning-region crosswalk": 21,
        "Documented county-name alias or typographic correction": 10,
        "Alaska post-split crosswalk to Chugach Census Area": 2,
    }
