"""Shared utilities used by the reproducible analysis pipeline."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def normalize_ccn(value: Any) -> str:
    """Return a six-character CMS Certification Number or an empty string.

    Values exported by spreadsheet software sometimes appear as ``123456.0``;
    the decimal suffix is removed before non-digits are stripped.
    """
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6)[-6:] if digits else ""


def parse_binary(value: Any) -> int:
    """Map documented affirmative values to 1 and all other values to 0."""
    if value is None or pd.isna(value):
        return 0
    return int(str(value).strip().lower() in {"1", "1.0", "true", "yes", "y"})


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
