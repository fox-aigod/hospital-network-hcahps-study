from __future__ import annotations

from pathlib import Path

import pytest

from src.build_stage5_models import build_reconciliation

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "outputs/stage5/legacy/primary_model_coefficients.csv",
    ROOT / "outputs/stage5/canonical/primary_model_coefficients.csv",
    ROOT / "outputs/stage5/legacy/analysis_summary.json",
    ROOT / "outputs/stage5/canonical/analysis_summary.json",
]

pytestmark = pytest.mark.skipif(
    not all(path.exists() for path in REQUIRED),
    reason="Stage 5 generated outputs are intentionally excluded from Git.",
)


def test_stage5_legacy_reproduction_and_canonical_reconciliation() -> None:
    summary = build_reconciliation(ROOT)
    assert summary["legacy_archived_reproduction"]["all_hashes_match"] is True
    assert summary["legacy_archived_reproduction"]["files_checked"] == 14
    assert summary["canonical_weight_model_fits"]["convergence_warnings"] == 0
    assert summary["canonical_weight_model_fits"]["maximum_iterations"] < 2000
    assert summary["reconciliation"]["p_value_inferences_unchanged"] is True
    assert (
        summary["reconciliation"][
            "all_primary_manuscript_values_unchanged_at_reported_precision"
        ]
        is True
    )

    primary = summary["primary_canonical_results"]
    assert primary["global_wald_df"] == 5
    assert primary["global_wald_chi2"] == pytest.approx(29.0083282635, abs=1e-8)
    assert primary["global_p"] == pytest.approx(2.3100517549e-05, rel=1e-8)
    contrast = primary["profile_5_vs_3"]
    assert contrast["estimate"] == pytest.approx(0.2757432236, abs=1e-9)
    assert contrast["p_value"] == pytest.approx(0.2059767511, abs=1e-9)
