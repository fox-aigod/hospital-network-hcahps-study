"""Link the locked ONC-CMS cohort to archived hospital-level HCAHPS outcomes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .common import normalize_ccn, write_json

HCAHPS_REQUIRED = {
    "Facility ID",
    "HCAHPS Measure ID",
    "HCAHPS Answer Percent",
    "HCAHPS Answer Percent Footnote",
    "HCAHPS Linear Mean Value",
    "Number of Completed Surveys",
    "Survey Response Rate Percent",
    "Start Date",
    "End Date",
}

MEASURE_MAP = {
    "H_COMP_6_Y_P": ("discharge_information_yes_pct", "HCAHPS Answer Percent"),
    "H_COMP_5_A_P": ("medicines_always_pct", "HCAHPS Answer Percent"),
    "H_HSP_RATING_9_10": ("overall_rating_9_10_pct", "HCAHPS Answer Percent"),
    "H_RECMND_DY": ("definitely_recommend_pct", "HCAHPS Answer Percent"),
    "H_COMP_1_A_P": ("nurse_communication_always_pct", "HCAHPS Answer Percent"),
    "H_COMP_2_A_P": ("doctor_communication_always_pct", "HCAHPS Answer Percent"),
    "H_COMP_6_LINEAR_SCORE": (
        "discharge_information_linear_mean",
        "HCAHPS Linear Mean Value",
    ),
}
PRIMARY_MEASURE_ID = "H_COMP_6_Y_P"


def ensure_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def numeric_or_missing(series: pd.Series) -> pd.Series:
    """Convert published numeric strings to floats and suppression text to NaN."""
    return pd.to_numeric(series, errors="coerce")


def build_stage2_hcahps(root: Path) -> dict[str, Any]:
    locked_path = root / "data" / "processed" / "locked_onc_cms_cohort.csv"
    hcahps_path = root / "data" / "raw" / "HCAHPS-Hospital.csv"
    processed_dir = root / "data" / "processed"
    tables_dir = root / "outputs" / "tables"
    processed_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    locked = pd.read_csv(
        locked_path,
        dtype={"ccn": str, "profile_bits": str},
        keep_default_na=False,
    )
    hcahps = pd.read_csv(
        hcahps_path,
        dtype=str,
        keep_default_na=False,
        low_memory=False,
        encoding="utf-8-sig",
    )
    ensure_columns(hcahps, HCAHPS_REQUIRED, "CMS HCAHPS hospital file")
    hcahps["ccn"] = hcahps["Facility ID"].map(normalize_ccn)
    raw_facility_ids = int(hcahps["Facility ID"].nunique())
    excluded_non_ccn_rows = int(hcahps["ccn"].eq("").sum())
    valid_hcahps = hcahps.loc[hcahps["ccn"].ne("")].copy()

    duplicate_keys = int(
        valid_hcahps.duplicated(["ccn", "HCAHPS Measure ID"], keep=False).sum()
    )
    if duplicate_keys:
        raise ValueError(
            "HCAHPS contains duplicate facility-measure rows; explicit resolution is required."
        )

    periods = valid_hcahps[["Start Date", "End Date"]].drop_duplicates()
    if len(periods) != 1:
        raise ValueError(f"Expected one HCAHPS reporting period, found {len(periods)}")

    selected = valid_hcahps.loc[
        valid_hcahps["HCAHPS Measure ID"].isin(MEASURE_MAP)
    ].copy()
    available_ids = set(selected["HCAHPS Measure ID"].unique())
    missing_ids = sorted(set(MEASURE_MAP) - available_ids)
    if missing_ids:
        raise ValueError(f"Required HCAHPS measures are missing: {missing_ids}")

    cohort = locked.copy()
    for measure_id, (output_name, source_field) in MEASURE_MAP.items():
        measure = selected.loc[
            selected["HCAHPS Measure ID"].eq(measure_id),
            ["ccn", source_field],
        ].copy()
        measure[output_name] = numeric_or_missing(measure[source_field])
        measure = measure[["ccn", output_name]]
        cohort = cohort.merge(measure, on="ccn", how="left", validate="one_to_one")

    primary = selected.loc[
        selected["HCAHPS Measure ID"].eq(PRIMARY_MEASURE_ID),
        [
            "ccn",
            "HCAHPS Answer Percent Footnote",
            "Number of Completed Surveys",
            "Survey Response Rate Percent",
            "Start Date",
            "End Date",
        ],
    ].copy()
    primary = primary.rename(
        columns={
            "HCAHPS Answer Percent Footnote": "primary_outcome_footnote",
            "Start Date": "hcahps_start_date",
            "End Date": "hcahps_end_date",
        }
    )
    primary["number_completed_surveys"] = numeric_or_missing(
        primary.pop("Number of Completed Surveys")
    )
    primary["survey_response_rate_pct"] = numeric_or_missing(
        primary.pop("Survey Response Rate Percent")
    )
    cohort = cohort.merge(primary, on="ccn", how="left", validate="one_to_one")

    cohort["primary_outcome_available"] = (
        cohort["discharge_information_yes_pct"].notna().astype("int8")
    )

    output_order = list(locked.columns) + [
        "primary_outcome_available",
        "primary_outcome_footnote",
        "number_completed_surveys",
        "survey_response_rate_pct",
        "hcahps_start_date",
        "hcahps_end_date",
        "discharge_information_yes_pct",
        "medicines_always_pct",
        "overall_rating_9_10_pct",
        "definitely_recommend_pct",
        "nurse_communication_always_pct",
        "doctor_communication_always_pct",
        "discharge_information_linear_mean",
    ]
    cohort = cohort[output_order].sort_values("ccn", kind="mergesort")
    cohort.to_csv(processed_dir / "hospital_network_hcahps_cohort.csv", index=False)

    outcome_rows: list[dict[str, Any]] = []
    for output_name, _source_field in MEASURE_MAP.values():
        row: dict[str, Any] = {
            "outcome": output_name,
            "overall_total": int(len(cohort)),
            "overall_observed": int(cohort[output_name].notna().sum()),
        }
        for group, prefix in (
            ("Acute Care", "acute"),
            ("Critical Access", "cah"),
        ):
            subset = cohort.loc[cohort["hospital_group"].eq(group)]
            row[f"{prefix}_total"] = int(len(subset))
            row[f"{prefix}_observed"] = int(subset[output_name].notna().sum())
            row[f"{prefix}_observed_pct"] = round(
                100 * subset[output_name].notna().mean(), 6
            )
        outcome_rows.append(row)
    pd.DataFrame(outcome_rows).to_csv(
        tables_dir / "stage2_outcome_availability.csv", index=False
    )

    footnotes = (
        cohort.assign(
            primary_outcome_footnote=cohort["primary_outcome_footnote"].fillna("")
        )
        .groupby(["hospital_group", "primary_outcome_footnote"], dropna=False)
        .size()
        .rename("n")
        .reset_index()
    )
    footnotes.to_csv(tables_dir / "stage2_primary_footnote_counts.csv", index=False)

    locked_ccns = set(locked["ccn"])
    hcahps_ccns = set(valid_hcahps["ccn"])
    summary = {
        "hcahps_source": {
            "raw_rows": int(len(hcahps)),
            "unique_raw_facility_ids": raw_facility_ids,
            "excluded_non_ccn_rows": excluded_non_ccn_rows,
            "unique_valid_ccns": int(valid_hcahps["ccn"].nunique()),
            "unique_measure_ids": int(valid_hcahps["HCAHPS Measure ID"].nunique()),
            "duplicate_facility_measure_rows": duplicate_keys,
            "start_date": periods.iloc[0]["Start Date"],
            "end_date": periods.iloc[0]["End Date"],
        },
        "linkage": {
            "locked_hospitals": int(len(locked)),
            "locked_hospitals_present_in_hcahps": int(len(locked_ccns & hcahps_ccns)),
            "locked_hospitals_absent_from_hcahps": int(len(locked_ccns - hcahps_ccns)),
        },
        "primary_outcome": {
            "measure_id": PRIMARY_MEASURE_ID,
            "observed_total": int(cohort["primary_outcome_available"].sum()),
            "acute_observed": int(
                cohort.loc[
                    cohort["hospital_group"].eq("Acute Care"),
                    "primary_outcome_available",
                ].sum()
            ),
            "cah_observed": int(
                cohort.loc[
                    cohort["hospital_group"].eq("Critical Access"),
                    "primary_outcome_available",
                ].sum()
            ),
        },
        "linear_mean": {
            "observed_total": int(
                cohort["discharge_information_linear_mean"].notna().sum()
            ),
            "acute_observed": int(
                cohort.loc[
                    cohort["hospital_group"].eq("Acute Care"),
                    "discharge_information_linear_mean",
                ].notna().sum()
            ),
            "cah_observed": int(
                cohort.loc[
                    cohort["hospital_group"].eq("Critical Access"),
                    "discharge_information_linear_mean",
                ].notna().sum()
            ),
        },
    }
    write_json(tables_dir / "stage2_hcahps_summary.json", summary)
    return summary
