from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage6_spec_locks_publication_assets() -> None:
    spec = json.loads((ROOT / "config/stage6_publication_spec.json").read_text())
    assert len(spec["main_tables"]) == 3
    assert len(spec["supplement_tables"]) == 6
    assert len(spec["figures"]) == 5
    assert spec["validation"]["main_table_2_source_total"] == 2651
    assert spec["validation"]["main_table_2_outcome_total"] == 2409
    assert spec["validation"]["main_table_3_2025_global_chi2_display"] == "31.03 (5)"
    assert re.fullmatch(spec["validation"]["supplement_table_S1_bits_regex"], "0001")
    assert not re.fullmatch(spec["validation"]["supplement_table_S1_bits_regex"], "1")


def test_stage6_generators_use_repository_relative_paths() -> None:
    table_source = (ROOT / "scripts/build_stage6_publication_assets.py").read_text()
    figure_source = (ROOT / "scripts/generate_stage6_media.py").read_text()
    assert "Path(__file__).resolve().parents[1]" in table_source
    assert "Path(__file__).resolve().parents[1]" in figure_source
    assert "Path('/mnt/data" not in table_source
    assert "Path('/mnt/data" not in figure_source


def test_stage6_cohort_flow_uses_pipeline_summaries() -> None:
    figure_source = (ROOT / "scripts/generate_stage6_media.py").read_text()
    assert "stage1_linkage_summary.json" in figure_source
    assert "stage2_hcahps_summary.json" in figure_source
    assert 'raw_onc = int(stage1["onc"]["raw_rows"])' in figure_source
    assert "N = 3,393" not in figure_source
