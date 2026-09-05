from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stage5_source_contract() -> dict:
    return json.loads(
        (ROOT / "config/stage5_source_contract.json").read_text(encoding="utf-8")
    )


def assembled_stage5_source() -> str:
    contract = stage5_source_contract()
    source_dir = ROOT / "scripts/stage5_source"
    parts = sorted(source_dir.glob("part_*.pyfrag"))
    assert [path.name for path in parts] == contract["fragments"]
    return contract["separator"].join(
        path.read_text(encoding=contract["encoding"]) for path in parts
    )


def test_stage5_spec_preserves_historical_outputs_and_reference_profile() -> None:
    spec = json.loads((ROOT / "config/stage5_analysis_spec.json").read_text())
    assert spec["execution"]["profile_reference"] == 3
    assert spec["execution"]["planned_contrast"] == "Profile 5 minus Profile 3"
    assert spec["execution"]["primary_covariance"] == "HC3"
    assert spec["execution"]["pooling"] == "Rubin rules"
    assert len(spec["historical_reference_output_sha256"]) == 14
    assert all(
        len(value) == 64
        for value in spec["historical_reference_output_sha256"].values()
    )


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


def test_assembled_stage5_source_matches_integrity_contract() -> None:
    contract = stage5_source_contract()
    source_bytes = assembled_stage5_source().encode(contract["encoding"])
    assert len(contract["fragments"]) == 14
    assert len(source_bytes) == contract["assembled_bytes"] == 46565
    assert hashlib.sha256(source_bytes).hexdigest() == contract["assembled_sha256"]
