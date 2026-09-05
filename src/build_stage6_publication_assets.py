"""Run and validate the canonical Stage 6 publication-asset generators."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image
from .release_contracts import (
    require_official_release_environment,
    validate_artifact_contract,
)


def build_stage6_publication_assets(root: Path) -> dict[str, Any]:
    require_official_release_environment(root)
    spec_path = root / "config" / "stage6_publication_spec.json"
    if not spec_path.exists():
        raise FileNotFoundError("Stage 6 publication specification is missing.")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    subprocess.run([sys.executable, str(root / "scripts" / "build_stage6_publication_assets.py")], cwd=root, check=True)
    subprocess.run([sys.executable, str(root / "scripts" / "generate_stage6_media.py")], cwd=root, check=True)

    table_dir = root / "outputs" / "stage6" / "tables"
    figure_dir = root / "outputs" / "stage6" / "figures"

    required_tables = spec["main_tables"] + spec["supplement_tables"] + ["manuscript_value_audit.csv"]
    missing_tables = [name for name in required_tables if not (table_dir / name).exists()]
    missing_figures = [name for name in spec["figures"] if not (figure_dir / name).exists()]
    if missing_tables or missing_figures:
        raise RuntimeError(f"Stage 6 outputs missing: tables={missing_tables}, figures={missing_figures}")

    with (table_dir / "manuscript_table_2.csv").open(encoding="utf-8-sig", newline="") as stream:
        table2 = list(csv.DictReader(stream))
    source_total = sum(int(row["Source N"]) for row in table2)
    outcome_total = sum(int(row["Outcome N"]) for row in table2)

    with (table_dir / "manuscript_table_3.csv").open(encoding="utf-8-sig", newline="") as stream:
        table3 = list(csv.DictReader(stream))
    row_2025 = next(row for row in table3 if row["Analysis"] == "2025 ONC responses only")

    with (table_dir / "supplement_table_S1.csv").open(encoding="utf-8-sig", newline="") as stream:
        s1 = list(csv.DictReader(stream))
    bits_pattern = re.compile(spec["validation"]["supplement_table_S1_bits_regex"])
    invalid_bits = sorted({row["Bits"] for row in s1 if not bits_pattern.fullmatch(row["Bits"])})

    with (table_dir / "manuscript_value_audit.csv").open(encoding="utf-8-sig", newline="") as stream:
        audit = list(csv.DictReader(stream))
    audit_failures = [row for row in audit if row["status"] != "PASS"]

    widths: dict[str, int] = {}
    for name in spec["figures"]:
        with Image.open(figure_dir / name) as image:
            widths[name] = int(image.width)

    expected = spec["validation"]
    checks = {
        "main_table_2_source_total": source_total == expected["main_table_2_source_total"],
        "main_table_2_outcome_total": outcome_total == expected["main_table_2_outcome_total"],
        "main_table_3_rows": len(table3) == expected["main_table_3_rows"],
        "main_table_3_2025_global_chi2_display": row_2025["Global χ² (df)"] == expected["main_table_3_2025_global_chi2_display"],
        "supplement_table_S1_rows": len(s1) == expected["supplement_table_S1_rows"],
        "supplement_table_S1_bits_valid": not invalid_bits,
        "figure_widths": min(widths.values()) >= expected["minimum_figure_width_pixels"],
        "manuscript_value_audit": len(audit_failures) == expected["required_manuscript_value_audit_failures"],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"Stage 6 validation failed: {failed}")
    summary = {
        "main_tables": len(spec["main_tables"]),
        "supplement_tables": len(spec["supplement_tables"]),
        "figures": len(spec["figures"]),
        "manuscript_value_audit_rows": len(audit),
        "manuscript_value_audit_failures": len(audit_failures),
        "minimum_figure_width_pixels": min(widths.values()),
        "checks": checks,
    }
    summary_path = table_dir / "stage6_validation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_validation = validate_artifact_contract(
        root, root / "config" / "stage6_release_contract.json"
    )
    return {**summary, "release_contract_validation": contract_validation}
