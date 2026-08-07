from __future__ import annotations

import pandas as pd

from src.build_stage3_confounders import (
    bed_category,
    compact_county,
    map_ahrq_ownership,
    map_cms_ownership,
    normalized_county,
)


def test_ownership_mappings() -> None:
    assert map_ahrq_ownership("1") == "Nonprofit"
    assert map_ahrq_ownership("3") == "Nonprofit"
    assert map_ahrq_ownership("2") == "Government"
    assert map_ahrq_ownership("5") == "For-profit"
    assert map_ahrq_ownership("") is None

    assert map_cms_ownership("Voluntary non-profit - Private") == "Nonprofit"
    assert (
        map_cms_ownership("Government - Hospital District or Authority")
        == "Government"
    )
    assert map_cms_ownership("Proprietary") == "For-profit"
    assert map_cms_ownership("Physician") is None


def test_county_normalization_and_compaction() -> None:
    assert normalized_county("St. Louis County") == "ST LOUIS"
    assert normalized_county("E Baton Rouge Parish") == "E BATON ROUGE"
    assert normalized_county("Valdez-Cordova Census Area") == "VALDEZ CORDOVA"
    assert compact_county("De Soto County") == "DESOTO"


def test_bed_categories_use_locked_boundaries() -> None:
    values = pd.Series(
        [4, 24, 25, 99, 100, 399, 400, pd.NA], dtype="Float64"
    )
    observed = bed_category(values).tolist()
    assert observed[:7] == [
        "<25",
        "<25",
        "25–99",
        "25–99",
        "100–399",
        "100–399",
        "≥400",
    ]
    assert pd.isna(observed[7])
