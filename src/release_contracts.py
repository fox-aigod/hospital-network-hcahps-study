"""Fail-closed validation for official release environments and artifacts."""

from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

from threadpoolctl import threadpool_info

from .common import sha256_file


def _os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
    return values


def release_environment_mismatches(root: Path) -> dict[str, dict[str, Any]]:
    """Return exact official-environment mismatches without changing state."""
    contract = json.loads(
        (root / "config/computational_environment.json").read_text(encoding="utf-8")
    )
    expected = contract["official_release_environment"]
    observed: dict[str, Any] = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "pip_version": importlib.metadata.version("pip"),
        "operating_system": _os_release().get("ID", platform.system()).lower(),
        "operating_system_version": _os_release().get("VERSION_ID", ""),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count(),
        "requirements_lock_sha256": sha256_file(root / "requirements-lock.txt"),
    }
    mismatches = {
        key: {"expected": value, "observed": observed.get(key)}
        for key, value in expected.items()
        if key in observed and observed.get(key) != value
    }

    required_packages = contract["numerical_libraries"]
    for distribution, expected_version in required_packages.items():
        observed_version = importlib.metadata.version(distribution)
        if observed_version != expected_version:
            mismatches[f"package:{distribution}"] = {
                "expected": expected_version,
                "observed": observed_version,
            }

    expected_backend = contract["numerical_backend"]
    blas = [
        item
        for item in threadpool_info()
        if item.get("internal_api") == expected_backend["internal_api"]
        and item.get("user_api") == "blas"
    ]
    if not blas:
        mismatches["numerical_backend"] = {
            "expected": expected_backend["internal_api"],
            "observed": "not loaded",
        }
    else:
        for key in ("version", "threading_layer", "architecture", "num_threads"):
            observed_values = sorted({item.get(key) for item in blas}, key=str)
            if observed_values != [expected_backend[key]]:
                mismatches[f"numerical_backend:{key}"] = {
                    "expected": expected_backend[key],
                    "observed": observed_values,
                }
    return mismatches


def require_official_release_environment(root: Path) -> None:
    """Fail before scientific execution outside the normative release target."""
    mismatches = release_environment_mismatches(root)
    if mismatches:
        raise RuntimeError(
            "Official release environment mismatch: "
            + json.dumps(mismatches, sort_keys=True)
        )
    if sys.implementation.name != "cpython":
        raise RuntimeError("Official release execution requires CPython.")


def validate_artifact_contract(root: Path, contract_path: Path) -> dict[str, Any]:
    """Require exact size and SHA-256 identity for every contracted artifact."""
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    failures: dict[str, dict[str, Any]] = {}
    for artifact in contract["artifacts"]:
        relative = artifact["path"]
        path = root / relative
        if not path.is_file():
            failures[relative] = {"expected": "file", "observed": "missing"}
            continue
        observed_size = path.stat().st_size
        observed_sha256 = sha256_file(path)
        if (
            observed_size != artifact["bytes"]
            or observed_sha256 != artifact["sha256"]
        ):
            failures[relative] = {
                "expected_bytes": artifact["bytes"],
                "observed_bytes": observed_size,
                "expected_sha256": artifact["sha256"],
                "observed_sha256": observed_sha256,
            }
    if failures:
        raise RuntimeError(
            "Release artifact contract mismatch: "
            + json.dumps(failures, sort_keys=True)
        )
    return {
        "contract": str(contract_path.relative_to(root)),
        "files_checked": len(contract["artifacts"]),
        "all_exact": True,
    }
