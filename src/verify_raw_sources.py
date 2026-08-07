"""Verify archived raw files against the repository source manifest."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .common import read_json, sha256_file, write_json


def csv_shape(path: Path) -> tuple[int, int]:
    """Return data-row and column counts without loading the whole file."""
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, errors="strict", newline="") as stream:
                reader = csv.reader(stream)
                header = next(reader)
                rows = sum(1 for _ in reader)
            return rows, len(header)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise RuntimeError(f"Unable to decode {path}") from last_error


def verify_raw_sources(root: Path) -> dict[str, Any]:
    manifest_path = root / "config" / "raw_sources.json"
    raw_dir = root / "data" / "raw"
    manifest = read_json(manifest_path)

    results: list[dict[str, Any]] = []
    failures: list[str] = []

    for source in manifest["sources"]:
        path = raw_dir / source["filename"]
        item: dict[str, Any] = {
            "id": source["id"],
            "filename": source["filename"],
            "exists": path.exists(),
        }
        if not path.exists():
            item["status"] = "missing"
            failures.append(f"Missing raw file: {source['filename']}")
            results.append(item)
            continue

        rows, columns = csv_shape(path)
        observed = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "rows": rows,
            "columns": columns,
        }
        item.update(observed)
        mismatches = [
            key
            for key in ("bytes", "sha256", "rows", "columns")
            if observed[key] != source[key]
        ]
        item["status"] = "verified" if not mismatches else "mismatch"
        item["mismatches"] = mismatches
        if mismatches:
            failures.append(
                f"{source['filename']} differs from the archived snapshot: "
                + ", ".join(mismatches)
            )
        results.append(item)

    report = {
        "manifest_version": manifest["manifest_version"],
        "all_verified": not failures,
        "results": results,
        "failures": failures,
    }
    write_json(root / "outputs" / "logs" / "raw_source_verification.json", report)
    if failures:
        raise RuntimeError("Raw-source verification failed:\n- " + "\n- ".join(failures))
    return report
