"""Execute one locked Stage 5 model suite from ordered source fragments."""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source_dir = ROOT / "scripts" / "stage5_source"
parts = sorted(source_dir.glob("part_*.pyfrag"))
if not parts:
    raise FileNotFoundError("Stage 5 source fragments are missing.")
source = "".join(path.read_text(encoding="utf-8") for path in parts)
namespace = {"__name__": "__main__", "__file__": str(ROOT / "scripts" / "run_stage5_model_suite.py")}
exec(compile(source, "<stage5_model_suite>", "exec"), namespace, namespace)
