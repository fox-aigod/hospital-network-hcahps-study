"""Build the locked 2024-2025 ONC-CMS hospital cohort from archived raw files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .common import normalize_ccn, parse_binary, write_json

ONC_REQUIRED = {
    "aha_id",
    "mstate",
    "mcrnum",
    "year",
    "national_network",
    "vendor_network",
    "hio",
    "tefca_part",
    "tefca_plan",
}
CMS_REQUIRED = {
    "Facility ID",
    "Facility Name",
    "State",
    "County/Parish",
    "Hospital Type",
    "Hospital Ownership",
    "Emergency Services",
    "Hospital overall rating",
}

PROFILE_LABELS = {
    0: "No coded participation",
    1: "One conventional network, no TEFCA",
    2: "Two conventional networks, no TEFCA",
    3: "Three conventional networks, no TEFCA",
    4: "TEFCA plus zero to two conventional networks",
    5: "TEFCA plus all three conventional networks",
}


def ensure_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def profile_category(hio: int, national: int, vendor: int, tefca: int) -> int:
    conventional = hio + national + vendor
    if tefca == 0:
        return conventional
    return 5 if conventional == 3 else 4


def prepare_onc(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    ensure_columns(raw, ONC_REQUIRED, "ONC network-participation file")

    frame = raw.copy()
    frame["ccn"] = frame["mcrnum"].map(normalize_ccn)
    frame["survey_year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    for column in (
        "hio",
        "national_network",
        "vendor_network",
        "tefca_part",
        "tefca_plan",
    ):
        frame[column] = frame[column].map(parse_binary).astype("int8")

    missing_ccn = int(frame["ccn"].eq("").sum())
    usable = frame.loc[frame["ccn"].ne("")].copy()
    duplicate_ccns = sorted(
        usable.loc[usable.duplicated("ccn", keep=False), "ccn"].unique()
    )

    # The source represents each hospital by its most recent available survey.
    # Sort order makes cross-year duplicate resolution explicit and deterministic;
    # AHA ID is a final tie-breaker only.
    usable = usable.sort_values(
        ["ccn", "survey_year", "aha_id"],
        ascending=[True, False, False],
        kind="mergesort",
    )
    latest = usable.drop_duplicates("ccn", keep="first").copy()

    audit = {
        "raw_rows": int(len(raw)),
        "missing_ccn_rows": missing_ccn,
        "usable_rows": int(len(usable)),
        "unique_usable_ccns": int(latest["ccn"].nunique()),
        "duplicate_ccns_resolved": duplicate_ccns,
    }
    return latest, audit


def prepare_cms(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    ensure_columns(raw, CMS_REQUIRED, "CMS Hospital General Information file")
    frame = raw.copy()
    frame["ccn"] = frame["Facility ID"].map(normalize_ccn)

    # CMS contains duplicate six-digit identifiers for some federal facilities.
    # None overlaps the archived ONC source, but collapse deterministically so a
    # future source refresh cannot inherit file-order-dependent behavior.
    frame["_nonfederal_priority"] = (
        ~frame["Hospital Type"].str.contains(
            "Department of Defense|Veterans Administration",
            case=False,
            regex=True,
        )
    ).astype(int)
    frame = frame.sort_values(
        ["ccn", "_nonfederal_priority", "State", "Facility Name"],
        ascending=[True, False, True, True],
        kind="mergesort",
    )
    duplicates = sorted(
        frame.loc[frame.duplicated("ccn", keep=False), "ccn"].unique()
    )
    unique = frame.drop_duplicates("ccn", keep="first").drop(
        columns="_nonfederal_priority"
    )
    audit = {
        "raw_rows": int(len(raw)),
        "unique_ccns": int(unique["ccn"].nunique()),
        "duplicate_ccns_resolved": duplicates,
    }
    return unique, audit


def build_stage1_cohort(root: Path) -> dict[str, Any]:
    raw_dir = root / "data" / "raw"
    interim_dir = root / "data" / "interim"
    processed_dir = root / "data" / "processed"
    tables_dir = root / "outputs" / "tables"
    for directory in (interim_dir, processed_dir, tables_dir):
        directory.mkdir(parents=True, exist_ok=True)

    onc, onc_audit = prepare_onc(raw_dir / "hospital_network_participation.csv")
    cms, cms_audit = prepare_cms(raw_dir / "cms_hospital_general_information.csv")

    merged = onc.merge(
        cms,
        on="ccn",
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    matched = merged.loc[merged["_merge"].eq("both")].copy()
    unmatched = merged.loc[merged["_merge"].eq("left_only")].copy()

    type_map = {
        "Acute Care Hospitals": "Acute Care",
        "Critical Access Hospitals": "Critical Access",
    }
    matched["hospital_group"] = matched["Hospital Type"].map(type_map).fillna("Other")
    eligible_all_years = matched.loc[
        matched["hospital_group"].isin(["Acute Care", "Critical Access"])
    ].copy()
    locked = eligible_all_years.loc[
        eligible_all_years["survey_year"].isin([2024, 2025])
    ].copy()

    locked["profile_bits"] = (
        locked["hio"].astype(str)
        + locked["national_network"].astype(str)
        + locked["vendor_network"].astype(str)
        + locked["tefca_part"].astype(str)
    )
    locked["network_count"] = locked[
        ["hio", "national_network", "vendor_network", "tefca_part"]
    ].sum(axis=1).astype("int8")
    locked["profile_category_code"] = locked.apply(
        lambda row: profile_category(
            int(row["hio"]),
            int(row["national_network"]),
            int(row["vendor_network"]),
            int(row["tefca_part"]),
        ),
        axis=1,
    ).astype("int8")
    locked["profile_category_label"] = locked["profile_category_code"].map(
        PROFILE_LABELS
    )

    output_columns = [
        "ccn",
        "aha_id",
        "survey_year",
        "Facility Name",
        "State",
        "County/Parish",
        "Hospital Type",
        "hospital_group",
        "Hospital Ownership",
        "Emergency Services",
        "Hospital overall rating",
        "hio",
        "national_network",
        "vendor_network",
        "tefca_part",
        "tefca_plan",
        "network_count",
        "profile_bits",
        "profile_category_code",
        "profile_category_label",
    ]
    locked = locked[output_columns].rename(
        columns={
            "Facility Name": "facility_name",
            "State": "state",
            "County/Parish": "county",
            "Hospital Type": "hospital_type",
            "Hospital Ownership": "ownership",
            "Emergency Services": "emergency_services",
            "Hospital overall rating": "overall_rating",
            "tefca_part": "current_tefca",
            "tefca_plan": "planned_tefca",
        }
    ).sort_values("ccn", kind="mergesort")

    onc.to_csv(interim_dir / "onc_latest_per_ccn.csv", index=False)
    matched.drop(columns="_merge").to_csv(
        interim_dir / "onc_cms_matched.csv", index=False
    )
    unmatched.to_csv(interim_dir / "onc_unmatched_to_cms.csv", index=False)
    locked.to_csv(processed_dir / "locked_onc_cms_cohort.csv", index=False)

    profile_counts = (
        locked.groupby(
            ["profile_category_code", "profile_category_label", "hospital_group"],
            observed=True,
        )
        .size()
        .rename("n")
        .reset_index()
    )
    profile_counts.to_csv(tables_dir / "stage1_profile_counts.csv", index=False)

    summary = {
        "onc": onc_audit,
        "cms": cms_audit,
        "linkage": {
            "matched_unique_onc_ccns": int(len(matched)),
            "unmatched_unique_onc_ccns": int(len(unmatched)),
            "match_rate_pct": round(100 * len(matched) / len(onc), 6),
            "eligible_acute_and_cah_all_years": int(len(eligible_all_years)),
        },
        "locked_2024_2025_cohort": {
            "total": int(len(locked)),
            "acute_care": int(
                (locked["hospital_group"] == "Acute Care").sum()
            ),
            "critical_access": int(
                (locked["hospital_group"] == "Critical Access").sum()
            ),
            "survey_year_2024": int((locked["survey_year"] == 2024).sum()),
            "survey_year_2025": int((locked["survey_year"] == 2025).sum()),
            "unique_ccns": int(locked["ccn"].nunique()),
            "states_and_dc": int(locked["state"].nunique()),
        },
    }
    write_json(tables_dir / "stage1_linkage_summary.json", summary)
    return summary
