from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.build_stage4_imputation_weights import TARGET_SPECS

ROOT = Path(__file__).resolve().parents[1]


def test_stage4_seed_sequence_is_locked() -> None:
    spec = json.loads((ROOT / "config/stage4_analysis_spec.json").read_text())
    settings = spec["imputation"]
    seeds = [
        settings["base_seed"] + settings["seed_increment"] * index
        for index in range(settings["imputations"])
    ]
    assert len(seeds) == 20
    assert seeds[0] == 20260805
    assert seeds[-1] == 20279976
    assert len(set(seeds)) == 20


def test_stage4_target_order_and_types_are_locked() -> None:
    assert TARGET_SPECS == [
        ("health_system_affiliated", "binary"),
        ("log2_beds_plus1", "continuous"),
        ("ownership_code", "categorical"),
        ("teaching_intensity", "continuous"),
        ("high_dsh_flag", "binary"),
        ("uncompensated_care_burden", "continuous"),
        ("high_uncompensated_care_flag", "binary"),
    ]


def test_canonical_iteration_limit_exceeds_legacy_limit() -> None:
    spec = json.loads((ROOT / "config/stage4_analysis_spec.json").read_text())
    weighting = spec["observation_weighting"]
    assert weighting["legacy_max_iter"] == 500
    assert weighting["canonical_max_iter"] == 2000
    assert weighting["canonical_max_iter"] > weighting["legacy_max_iter"]
    assert weighting["trim_quantiles"] == [0.01, 0.99]
    assert np.isclose(weighting["normalize_mean"], 1.0)
