from __future__ import annotations

import importlib.util
from pathlib import Path


def test_display_only_figures_from_canonical_release(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "make_figures", root / "scripts" / "make_figures.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    colmap = {
        "group": "hospital_group",
        "code": "profile_category",
        "mean": "estimate",
        "lower": "ci_low",
        "upper": "ci_high",
    }
    module.figure1(tmp_path)
    module.figure3(
        module.load_means(
            root / "release/v1.0.0/stage5/interaction_adjusted_means.csv", colmap
        ),
        tmp_path,
    )
    assert (tmp_path / "figure1_cohort_flow.png").is_file()
    assert (tmp_path / "figure3_profile_means_by_group.png").is_file()
