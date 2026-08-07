from __future__ import annotations

import pandas as pd

from src.build_stage2_hcahps import numeric_or_missing


def test_hcahps_suppression_strings_become_missing() -> None:
    values = pd.Series(["88", "Not Available", "Not Applicable", "", "72.5"])
    parsed = numeric_or_missing(values)
    assert parsed.iloc[0] == 88
    assert pd.isna(parsed.iloc[1])
    assert pd.isna(parsed.iloc[2])
    assert pd.isna(parsed.iloc[3])
    assert parsed.iloc[4] == 72.5
