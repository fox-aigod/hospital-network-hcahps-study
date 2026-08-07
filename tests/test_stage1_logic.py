from __future__ import annotations

import pandas as pd

from src.build_stage1_cohort import PROFILE_LABELS, profile_category
from src.common import normalize_ccn, parse_binary


def test_normalize_ccn_preserves_leading_zeroes() -> None:
    assert normalize_ccn("10021") == "010021"
    assert normalize_ccn("010021") == "010021"
    assert normalize_ccn("10021.0") == "010021"
    assert normalize_ccn("") == ""
    assert normalize_ccn(pd.NA) == ""


def test_parse_binary_is_conservative() -> None:
    assert parse_binary("1") == 1
    assert parse_binary("Yes") == 1
    assert parse_binary("0") == 0
    assert parse_binary("") == 0
    assert parse_binary("unanswered") == 0


def test_six_profile_mapping_is_exhaustive() -> None:
    observed = set()
    for hio in (0, 1):
        for national in (0, 1):
            for vendor in (0, 1):
                for tefca in (0, 1):
                    category = profile_category(hio, national, vendor, tefca)
                    assert category in PROFILE_LABELS
                    observed.add(category)
    assert observed == {0, 1, 2, 3, 4, 5}


def test_reference_and_primary_contrast_categories() -> None:
    assert profile_category(1, 1, 1, 0) == 3
    assert profile_category(1, 1, 1, 1) == 5
