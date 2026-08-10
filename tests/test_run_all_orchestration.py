from __future__ import annotations

import sys

import pytest

import run_all


def patch_pipeline_builders(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    def record(name: str, result: dict):
        def builder(*_args, **_kwargs):
            calls.append(name)
            return result

        return builder

    monkeypatch.setattr(
        run_all,
        "verify_raw_sources",
        record("verify-raw", {"results": []}),
    )
    monkeypatch.setattr(
        run_all,
        "build_stage1_cohort",
        record(
            "stage1",
            {
                "locked_2024_2025_cohort": {
                    "total": 2651,
                    "acute_care": 1871,
                    "critical_access": 780,
                }
            },
        ),
    )
    monkeypatch.setattr(
        run_all,
        "build_stage2_hcahps",
        record(
            "stage2",
            {
                "primary_outcome": {
                    "observed_total": 2409,
                    "acute_observed": 1852,
                    "cah_observed": 557,
                }
            },
        ),
    )
    monkeypatch.setattr(
        run_all,
        "build_stage3_confounders",
        record(
            "stage3",
            {
                "ahrq_linkage": {"matched": 2624},
                "rucc_linkage": {"matched": 2651},
                "complete_required_covariates": {"complete_n": 2580},
            },
        ),
    )
    monkeypatch.setattr(
        run_all,
        "build_stage4_imputation_weights",
        record(
            "stage4",
            {"canonical_converged_weighting": {"mean_effective_sample_size": 2365.8}},
        ),
    )
    monkeypatch.setattr(
        run_all,
        "build_stage5_models",
        record(
            "stage5",
            {
                "primary_canonical_results": {
                    "global_wald_chi2": 29.0083282635,
                    "profile_5_vs_3": {"estimate": 0.2757432236},
                }
            },
        ),
    )
    monkeypatch.setattr(
        run_all,
        "build_stage6_publication_assets",
        record(
            "stage6",
            {
                "main_tables": 3,
                "supplement_tables": 6,
                "figures": 5,
                "manuscript_value_audit_failures": 0,
            },
        ),
    )
    return calls


def test_stage5_cli_accepts_actual_planned_contrast_key(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls = patch_pipeline_builders(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["run_all.py", "--stage", "stage5"])

    run_all.main()

    output = capsys.readouterr().out
    assert calls == ["verify-raw", "stage1", "stage2", "stage3", "stage4", "stage5"]
    assert "Wald chi-square 29.01" in output
    assert "contrast 0.276 percentage points" in output


def test_stage6_cli_proceeds_after_stage5_and_reports_summary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls = patch_pipeline_builders(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["run_all.py", "--stage", "stage6"])

    run_all.main()

    output = capsys.readouterr().out
    assert calls == [
        "verify-raw",
        "stage1",
        "stage2",
        "stage3",
        "stage4",
        "stage5",
        "stage6",
    ]
    assert (
        "Stage 6 passed: generated 3 main tables, 6 supplement tables, and "
        "5 figures; manuscript-value audit failures: 0."
    ) in output
