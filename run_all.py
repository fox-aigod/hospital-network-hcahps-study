"""Canonical entry point for the reproducible analysis pipeline.

During repository initialization this command validates the project structure and
source-data manifest. Statistical stages will be enabled sequentially only after
their code, tests, and expected outputs are reviewed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def validate_structure() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / "config" / "expected_results.json",
        ROOT / "data" / "raw" / "README.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required repository files are missing: {missing}")

    targets = json.loads((ROOT / "config" / "expected_results.json").read_text())
    if targets.get("status") != "provisional_validation_targets":
        raise ValueError("Expected-results status is not explicitly provisional.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=["validate"],
        default="validate",
        help="Pipeline stage to execute. Additional stages will be added after audit.",
    )
    args = parser.parse_args()

    if args.stage == "validate":
        validate_structure()
        print("Repository structure validation passed.")
        print("Full source-to-results reproduction is not enabled yet.")


if __name__ == "__main__":
    main()
