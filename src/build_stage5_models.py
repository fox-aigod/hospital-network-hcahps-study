"""Orchestrate Stage 5 model suites and reconcile canonical results."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from .common import write_json
from .release_contracts import (
    require_official_release_environment,
    validate_artifact_contract,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_model_suite(root: Path, mode: str) -> None:
    if mode not in {"legacy", "canonical"}:
        raise ValueError("mode must be legacy or canonical")
    env = os.environ.copy()
    env["HN_ROOT"] = str(root)
    env["HN_WEIGHT_MODE"] = mode
    script = root / "scripts" / "run_stage5_model_suite.py"
    subprocess.run([sys.executable, str(script)], cwd=root, env=env, check=True)


def _append_metric(
    rows: list[dict[str, Any]],
    category: str,
    result: str,
    metric: str,
    legacy: float,
    canonical: float,
    *,
    p_value: bool = False,
) -> None:
    legacy_value = float(legacy)
    canonical_value = float(canonical)
    rows.append(
        {
            "category": category,
            "result": result,
            "metric": metric,
            "legacy": legacy_value,
            "canonical": canonical_value,
            "absolute_difference": abs(canonical_value - legacy_value),
            "equal_at_3_decimals": round(legacy_value, 3) == round(canonical_value, 3),
            "inference_at_0_05_unchanged": (
                (legacy_value < 0.05) == (canonical_value < 0.05)
                if p_value
                else ""
            ),
        }
    )


def build_reconciliation(root: Path) -> dict[str, Any]:
    legacy_dir = root / "outputs" / "stage5" / "legacy"
    canonical_dir = root / "outputs" / "stage5" / "canonical"
    reconciliation_dir = root / "outputs" / "stage5" / "reconciliation"
    reconciliation_dir.mkdir(parents=True, exist_ok=True)

    spec = json.loads(
        (root / "config" / "stage5_analysis_spec.json").read_text(encoding="utf-8")
    )

    hashes = {}
    hash_matches = {}
    for filename, expected in spec["historical_reference_output_sha256"].items():
        observed = sha256_file(legacy_dir / filename)
        hashes[filename] = observed
        hash_matches[filename] = observed == expected
    if not all(hash_matches.values()):
        raise RuntimeError(f"Legacy model outputs failed archived reconciliation: {hash_matches}")

    legacy_summary = json.loads(
        (legacy_dir / "analysis_summary.json").read_text(encoding="utf-8")
    )
    canonical_summary = json.loads(
        (canonical_dir / "analysis_summary.json").read_text(encoding="utf-8")
    )
    rows: list[dict[str, Any]] = []

    for metric in ("statistic", "p_value"):
        _append_metric(
            rows,
            "Primary model",
            "Global six-profile test",
            metric,
            legacy_summary["primary_global"][metric],
            canonical_summary["primary_global"][metric],
            p_value=metric == "p_value",
        )
    for metric in ("estimate", "se", "ci_low", "ci_high", "p_value"):
        _append_metric(
            rows,
            "Primary model",
            "Profile 5 minus Profile 3",
            metric,
            legacy_summary["primary_planned_contrast"][metric],
            canonical_summary["primary_planned_contrast"][metric],
            p_value=metric == "p_value",
        )
    for metric in ("statistic", "p_value"):
        _append_metric(
            rows,
            "Interaction model",
            "Global profile-by-CAH interaction",
            metric,
            legacy_summary["interaction_global"][metric],
            canonical_summary["interaction_global"][metric],
            p_value=metric == "p_value",
        )

    def compare_csv(
        filename: str,
        category: str,
        key_columns: list[str],
        metrics: list[str],
        p_columns: set[str],
    ) -> None:
        left = pd.read_csv(legacy_dir / filename)
        right = pd.read_csv(canonical_dir / filename)
        merged = left.merge(right, on=key_columns, suffixes=("_legacy", "_canonical"))
        for _, record in merged.iterrows():
            label = " | ".join(str(record[column]) for column in key_columns)
            for metric in metrics:
                _append_metric(
                    rows,
                    category,
                    label,
                    metric,
                    record[f"{metric}_legacy"],
                    record[f"{metric}_canonical"],
                    p_value=metric in p_columns,
                )

    compare_csv(
        "interaction_planned_contrasts.csv",
        "Interaction contrasts",
        ["hospital_group", "contrast"],
        ["estimate", "se", "ci_low", "ci_high", "p_value"],
        {"p_value"},
    )
    compare_csv(
        "sensitivity_analyses.csv",
        "Sensitivity analyses",
        ["analysis"],
        [
            "global_statistic",
            "global_p",
            "contrast_estimate",
            "contrast_se",
            "contrast_ci_low",
            "contrast_ci_high",
            "contrast_p",
        ],
        {"global_p", "contrast_p"},
    )
    compare_csv(
        "stratified_analyses.csv",
        "Stratified analyses",
        ["hospital_group", "analysis"],
        [
            "global_statistic",
            "global_p",
            "contrast_estimate",
            "contrast_se",
            "contrast_ci_low",
            "contrast_ci_high",
            "contrast_p",
        ],
        {"global_p", "contrast_p"},
    )
    compare_csv(
        "secondary_outcomes.csv",
        "Secondary outcomes",
        ["outcome_field", "outcome"],
        [
            "global_statistic",
            "global_p",
            "global_bh_fdr",
            "contrast_estimate",
            "contrast_se",
            "contrast_ci_low",
            "contrast_ci_high",
            "contrast_p",
        ],
        {"global_p", "global_bh_fdr", "contrast_p"},
    )
    compare_csv(
        "adjusted_profile_means.csv",
        "Adjusted profile means",
        ["profile_category"],
        ["estimate", "se", "ci_low", "ci_high", "p_value"],
        {"p_value"},
    )
    compare_csv(
        "interaction_adjusted_means.csv",
        "Interaction adjusted means",
        ["hospital_group", "profile_category"],
        ["estimate", "se", "ci_low", "ci_high", "p_value"],
        {"p_value"},
    )

    reconciliation = pd.DataFrame(rows)
    reconciliation.to_csv(
        reconciliation_dir / "canonical_vs_legacy_results.csv", index=False
    )

    legacy_fit = legacy_summary["weight_model_fit_summary"]
    canonical_fit = canonical_summary["weight_model_fit_summary"]
    p_rows = reconciliation[reconciliation["metric"].str.contains("p", case=False)]
    manuscript_precision_checks = {
        "primary_global_chi2_2dp": round(legacy_summary["primary_global"]["statistic"], 2)
        == round(canonical_summary["primary_global"]["statistic"], 2),
        "primary_contrast_estimate_3dp": round(legacy_summary["primary_planned_contrast"]["estimate"], 3)
        == round(canonical_summary["primary_planned_contrast"]["estimate"], 3),
        "primary_contrast_ci_3dp": (
            round(legacy_summary["primary_planned_contrast"]["ci_low"], 3),
            round(legacy_summary["primary_planned_contrast"]["ci_high"], 3),
        )
        == (
            round(canonical_summary["primary_planned_contrast"]["ci_low"], 3),
            round(canonical_summary["primary_planned_contrast"]["ci_high"], 3),
        ),
        "primary_contrast_p_3dp": round(legacy_summary["primary_planned_contrast"]["p_value"], 3)
        == round(canonical_summary["primary_planned_contrast"]["p_value"], 3),
        "interaction_chi2_2dp": round(legacy_summary["interaction_global"]["statistic"], 2)
        == round(canonical_summary["interaction_global"]["statistic"], 2),
        "interaction_p_3dp": round(legacy_summary["interaction_global"]["p_value"], 3)
        == round(canonical_summary["interaction_global"]["p_value"], 3),
    }

    summary = {
        "status": "stage5_reproduced_and_canonical_models_validated",
        "legacy_archived_reproduction": {
            "files_checked": len(hash_matches),
            "all_hashes_match": all(hash_matches.values()),
            "hashes": hashes,
            "hash_matches": hash_matches,
        },
        "canonical_weight_model_fits": canonical_fit,
        "legacy_weight_model_fits": legacy_fit,
        "primary_canonical_results": {
            "global_wald_chi2": canonical_summary["primary_global"]["statistic"],
            "global_wald_df": canonical_summary["primary_global"]["df"],
            "global_p": canonical_summary["primary_global"]["p_value"],
            "profile_5_vs_3": canonical_summary["primary_planned_contrast"],
            "interaction_global": canonical_summary["interaction_global"],
        },
        "reconciliation": {
            "metrics_compared": int(len(reconciliation)),
            "all_equal_at_3_decimals": bool(
                reconciliation["equal_at_3_decimals"].all()
            ),
            "p_value_inferences_unchanged": bool(
                p_rows["inference_at_0_05_unchanged"].eq(True).all()
            ),
            "maximum_absolute_difference_across_compared_metrics": float(
                reconciliation["absolute_difference"].max()
            ),
            "manuscript_precision_checks": manuscript_precision_checks,
            "all_primary_manuscript_values_unchanged_at_reported_precision": bool(
                all(manuscript_precision_checks.values())
            ),
        },
    }
    write_json(reconciliation_dir / "stage5_summary.json", summary)
    return summary


def validate_release_results(root: Path) -> dict[str, Any]:
    """Validate the fresh canonical suite against the official release contract."""
    contract_path = root / "config" / "stage5_release_contract.json"
    validation = validate_artifact_contract(root, contract_path)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    summary = json.loads(
        (root / "outputs/stage5/canonical/analysis_summary.json").read_text(
            encoding="utf-8"
        )
    )
    expected = contract["scientific_payload"]
    comparisons = {
        "primary_global": summary["primary_global"] == {
            **expected["primary_global"],
            "terms": summary["primary_global"]["terms"],
        },
        "profile_5_minus_profile_3": (
            summary["primary_planned_contrast"]
            == expected["profile_5_minus_profile_3"]
        ),
        "profile_by_cah_interaction": summary["interaction_global"] == {
            **expected["profile_by_cah_interaction"],
            "terms": summary["interaction_global"]["terms"],
        },
        "weight_summary": summary["weight_summary"] == expected["weight_summary"],
        "weight_model_fit_summary": (
            summary["weight_model_fit_summary"]
            == expected["weight_model_fit_summary"]
        ),
    }
    if not all(comparisons.values()):
        raise RuntimeError(f"Stage 5 scientific payload mismatch: {comparisons}")
    return {
        "status": "stage5_official_release_results_reproduced",
        "release_contract_validation": validation,
        "scientific_payload_matches": comparisons,
        "canonical_weight_model_fits": summary["weight_model_fit_summary"],
        "primary_canonical_results": {
            "global_wald_chi2": summary["primary_global"]["statistic"],
            "global_wald_df": summary["primary_global"]["df"],
            "global_p": summary["primary_global"]["p_value"],
            "profile_5_vs_3": summary["primary_planned_contrast"],
            "interaction_global": summary["interaction_global"],
        },
    }


def build_stage5_models(root: Path) -> dict[str, Any]:
    require_official_release_environment(root)
    run_model_suite(root, "canonical")
    return validate_release_results(root)
