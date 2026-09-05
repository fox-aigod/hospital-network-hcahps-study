from __future__ import annotations

from pathlib import Path

import pytest

from src.build_stage5_models import validate_release_results

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [ROOT / "outputs/stage5/canonical/analysis_summary.json"]

pytestmark = pytest.mark.skipif(
    not all(path.exists() for path in REQUIRED),
    reason="Stage 5 generated outputs are intentionally excluded from Git.",
)


def test_stage5_official_release_contract_and_scientific_payload() -> None:
    summary = validate_release_results(ROOT)
    assert summary["status"] == "stage5_official_release_results_reproduced"
    assert summary["release_contract_validation"]["all_exact"] is True
    assert summary["release_contract_validation"]["files_checked"] == 16
    assert all(summary["scientific_payload_matches"].values())
    assert summary["canonical_weight_model_fits"]["convergence_warnings"] == 0
    assert summary["canonical_weight_model_fits"]["maximum_iterations"] < 2000
    primary = summary["primary_canonical_results"]
    assert primary["global_wald_df"] == 5
    assert primary["global_wald_chi2"] == pytest.approx(29.0319471391483)
    assert primary["global_p"] == pytest.approx(2.2855353712037596e-05)
    contrast = primary["profile_5_vs_3"]
    assert contrast["estimate"] == pytest.approx(0.2759584405062885)
    assert contrast["p_value"] == pytest.approx(0.20567061995680996)
