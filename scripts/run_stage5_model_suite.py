"""Execute one locked Stage 5 model suite from ordered source fragments."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source_dir = ROOT / "scripts" / "stage5_source"
contract = json.loads(
    (ROOT / "config" / "stage5_source_contract.json").read_text(encoding="utf-8")
)
parts = sorted(source_dir.glob("part_*.pyfrag"))
actual_names = [path.name for path in parts]
if actual_names != contract["fragments"]:
    raise RuntimeError(
        "Stage 5 source fragment set or order differs from the integrity contract."
    )
source = contract["separator"].join(
    path.read_text(encoding=contract["encoding"]) for path in parts
)
source_bytes = source.encode(contract["encoding"])
if len(source_bytes) != contract["assembled_bytes"]:
    raise RuntimeError("Stage 5 assembled-source byte count does not match the contract.")
actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
if actual_sha256 != contract["assembled_sha256"]:
    raise RuntimeError("Stage 5 assembled-source SHA-256 does not match the contract.")
namespace = {"__name__": "__main__", "__file__": str(ROOT / "scripts" / "run_stage5_model_suite.py")}
exec(compile(source, "<stage5_model_suite>", "exec"), namespace, namespace)
