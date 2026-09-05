from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.build_stage1_cohort import build_stage1_cohort
from src.build_stage2_hcahps import build_stage2_hcahps
from src.build_stage3_confounders import build_stage3_confounders
from src.build_stage4_imputation_weights import build_stage4_imputation_weights
from src.verify_raw_sources import verify_raw_sources

ROOT = Path(__file__).resolve().parents[1]
RAW_FILES = [
    ROOT / "data/raw/hospital_network_participation.csv",
    ROOT / "data/raw/cms_hospital_general_information.csv",
    ROOT / "data/raw/HCAHPS-Hospital.csv",
    ROOT / "data/raw/chsp-hospital-linkage-2023.csv",
    ROOT / "data/raw/Ruralurbancontinuumcodes2023.csv",
]

pytestmark = pytest.mark.skipif(
    not all(path.exists() for path in RAW_FILES),
    reason="Archived raw files are intentionally not committed to GitHub.",
)


def test_stage4_exact_legacy_reproduction_and_converged_canonical_weights() -> None:
    verify_raw_sources(ROOT)
    build_stage1_cohort(ROOT)
    build_stage2_hcahps(ROOT)
    build_stage3_confounders(ROOT)
    summary = build_stage4_imputation_weights(ROOT)

    assert summary["status"] == "stage4_official_release_environment_reproduced"
    assert summary["settings"]["source_n"] == 2651
    assert summary["settings"]["primary_outcome_observed_n"] == 2409
    assert summary["settings"]["imputations"] == 20
    assert summary["settings"]["cycles"] == 5

    assert summary["imputation_invariants"]["passed"] is True
    assert summary["imputation_model_fits"]["warnings"] == 0
    assert summary["imputation_model_fits"]["maximum_iterations"] == 46

    historical = summary["historical_reference_output_comparison"]
    assert historical["all_historical_reference_hashes_match"] is False
    assert not any(historical["historical_reference_hash_match"].values())
    assert historical["weighting"]["denominator_convergence_warnings"] == 18
    assert historical["weighting"]["maximum_absolute_smd_after"] == pytest.approx(
        0.17638799473300512
    )

    canonical = summary["canonical_converged_weighting"]
    assert canonical["denominator_convergence_warnings"] == 0
    assert canonical["numerator_convergence_warnings"] == 0
    assert canonical["denominator_iterations_max"] == 685
    assert canonical["mean_effective_sample_size"] == pytest.approx(
        2365.7512790600854
    )
    assert canonical["maximum_absolute_smd_after"] == pytest.approx(
        0.17650916012615167
    )

    comparison = summary["legacy_to_canonical_comparison"]
    assert comparison["maximum_absolute_normalized_weight_difference"] == pytest.approx(
        0.027822067846455356
    )
    assert comparison[
        "maximum_mean_absolute_normalized_weight_difference"
    ] == pytest.approx(0.0001426386525241508)

    release = summary["release_contract_validation"]
    assert release["all_exact"] is True
    assert release["files_checked"] == 14

    imputations = np.load(ROOT / "data/interim/stage4_imputations.npz")
    weights = np.load(ROOT / "data/interim/stage4_observation_weights.npz")
    assert imputations["log2_beds_plus1"].shape == (20, 2651)
    assert imputations["ownership_code"].shape == (20, 2651)
    assert weights["weights"].shape == (20, 2409)
    assert weights["denominator_probabilities"].shape == (20, 2651)
    assert np.allclose(weights["weights"].mean(axis=1), 1.0)
