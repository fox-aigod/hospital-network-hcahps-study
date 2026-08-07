from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def assembled_stage5_source() -> str:
    return "".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "scripts/stage5_source").glob("part_*.pyfrag"))
    )


def test_stage5_spec_locks_archived_outputs_and_reference_profile() -> None:
    spec = json.loads((ROOT / "config/stage5_analysis_spec.json").read_text())
    assert spec["execution"]["profile_reference"] == 3
    assert spec["execution"]["planned_contrast"] == "Profile 5 minus Profile 3"
    assert spec["execution"]["primary_covariance"] == "HC3"
    assert spec["execution"]["pooling"] == "Rubin rules"
    assert len(spec["archived_output_sha256"]) == 14
    assert all(len(value) == 64 for value in spec["archived_output_sha256"].values())


def test_stage5_runner_is_explicitly_dual_mode() -> None:
    source = assembled_stage5_source()
    runner = (ROOT / "scripts/run_stage5_model_suite.py").read_text()
    assert "MODE not in {'legacy', 'canonical'}" in source
    assert "WEIGHT_MAX_ITER = 500 if MODE == 'legacy' else 2000" in source
    assert "stage4_imputations.npz" in source
    assert "stage4_observation_weights.npz" in source
    assert 'compile(source, "<stage5_model_suite>", "exec")' in runner


def test_assembled_stage5_source_compiles() -> None:
    source = assembled_stage5_source()
    assert source.strip()
    compile(source, "<stage5_model_suite>", "exec")
