"""Link AHRQ hospital characteristics and USDA 2023 rurality to the cohort."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .common import normalize_ccn, read_json, write_json

AHRQ_REQUIRED = {
    "compendium_hospital_id",
    "ccn",
    "hospital_name",
    "hospital_city",
    "hospital_state",
    "hospital_zip",
    "acutehosp_flag",
    "health_sys_id",
    "health_sys_name",
    "hos_beds",
    "hos_dsch",
    "hos_res",
    "hos_children",
    "hos_majteach",
    "hos_vmajteach",
    "hos_teachint",
    "hos_highdpp",
    "hos_ucburden",
    "hos_highuc",
    "hos_ownership",
}
RUCC_REQUIRED = {"FIPS", "State", "County_Name", "Attribute", "Value"}
REQUIRED_COVARIATES = [
    "beds",
    "health_system_affiliated",
    "ahrq_ownership_3cat",
    "teaching_intensity",
    "high_dsh_flag",
    "uncompensated_care_burden",
    "high_uncompensated_care_flag",
    "rucc_2023",
]


def ensure_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", pd.NA), errors="coerce")


def normalized_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value).strip())
    text = text.encode("ascii", "ignore").decode().upper()
    return " ".join(re.sub(r"[^A-Z0-9 ]+", " ", text).split())


def normalized_county(value: Any) -> str:
    text = normalized_text(value)
    text = re.sub(r"\bSAINT\b", "ST", text)
    text = re.sub(r"\bCITY AND BOROUGH\b", "", text)
    for suffix in (
        r"\bCOUNTY\b",
        r"\bPARISH\b",
        r"\bBOROUGH\b",
        r"\bCENSUS AREA\b",
        r"\bMUNICIPALITY\b",
    ):
        text = re.sub(suffix, "", text)
    return " ".join(text.split())


def compact_county(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]", "", normalized_county(value))


def map_ahrq_ownership(code: Any) -> str | None:
    value = str(code).strip() if code is not None and not pd.isna(code) else ""
    return {
        "1": "Nonprofit",
        "1.0": "Nonprofit",
        "3": "Nonprofit",
        "3.0": "Nonprofit",
        "2": "Government",
        "2.0": "Government",
        "5": "For-profit",
        "5.0": "For-profit",
    }.get(value)


def map_cms_ownership(value: Any) -> str | None:
    text = normalized_text(value)
    if text.startswith("VOLUNTARY NON PROFIT"):
        return "Nonprofit"
    if text.startswith("GOVERNMENT"):
        return "Government"
    if text == "PROPRIETARY":
        return "For-profit"
    return None


def prepare_ahrq(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="cp1252")
    ensure_columns(raw, AHRQ_REQUIRED, "AHRQ Hospital Linkage file")
    frame = raw.copy()
    raw_ccn = frame["ccn"].str.strip()
    alphanumeric_ccn_rows = int(raw_ccn.str.contains(r"[A-Za-z]", regex=True).sum())
    missing_ccn_rows = int(raw_ccn.eq("").sum())
    frame["ccn_norm"] = frame["ccn"].map(normalize_ccn)
    excluded_non_ccn = int(frame["ccn_norm"].eq("").sum())
    valid = frame.loc[frame["ccn_norm"].ne("")].copy()

    duplicates = sorted(
        valid.loc[valid.duplicated("ccn_norm", keep=False), "ccn_norm"].unique()
    )
    if duplicates:
        valid["_acute_priority"] = pd.to_numeric(
            valid["acutehosp_flag"], errors="coerce"
        ).fillna(0)
        valid = (
            valid.sort_values(
                ["ccn_norm", "_acute_priority", "hospital_state", "hospital_name"],
                ascending=[True, False, True, True],
                kind="mergesort",
            )
            .drop_duplicates("ccn_norm", keep="first")
            .drop(columns="_acute_priority")
        )

    audit = {
        "raw_rows": int(len(raw)),
        "excluded_ccn_rows_total": excluded_non_ccn,
        "alphanumeric_federal_identifier_rows": alphanumeric_ccn_rows,
        "missing_ccn_rows": missing_ccn_rows,
        "valid_numeric_ccn_rows": int(len(valid)),
        "unique_valid_numeric_ccns": int(valid["ccn_norm"].nunique()),
        "duplicate_valid_numeric_ccns_resolved": duplicates,
    }
    return valid, audit


def prepare_rucc(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="cp1252")
    ensure_columns(raw, RUCC_REQUIRED, "USDA 2023 RUCC file")
    frame = raw.copy()
    frame["fips"] = frame["FIPS"].str.strip().str.zfill(5)
    wide = (
        frame.pivot(
            index=["fips", "State", "County_Name"],
            columns="Attribute",
            values="Value",
        )
        .reset_index()
    )
    required_attrs = {"RUCC_2023", "Description"}
    missing_attrs = sorted(required_attrs - set(wide.columns))
    if missing_attrs:
        raise ValueError(f"RUCC source is missing required attributes: {missing_attrs}")
    missing_rucc_rows = int(wide["RUCC_2023"].isna().sum())
    wide = wide.loc[wide["RUCC_2023"].notna()].copy()
    wide["rucc_2023"] = pd.to_numeric(wide["RUCC_2023"], errors="raise").astype(int)
    wide["county_norm"] = wide["County_Name"].map(normalized_county)
    wide["county_compact"] = wide["County_Name"].map(compact_county)
    audit = {
        "raw_rows": int(len(raw)),
        "unique_county_equivalents_with_rucc": int(wide["fips"].nunique()),
        "county_equivalents_without_rucc": missing_rucc_rows,
        "attribute_count": int(frame["Attribute"].nunique()),
    }
    return wide, audit


def choose_rucc(
    state: str,
    source_county: str,
    ahrq_city: str,
    rucc: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[str, str]:
    county_norm = normalized_county(source_county)
    county_compact = compact_county(source_county)

    exact = rucc.loc[
        (rucc["State"] == state) & (rucc["county_norm"] == county_norm)
    ]
    if len(exact) == 1:
        return str(exact.iloc[0]["fips"]), "Exact normalized county"

    compact = rucc.loc[
        (rucc["State"] == state) & (rucc["county_compact"] == county_compact)
    ]
    if len(compact) == 1:
        return (
            str(compact.iloc[0]["fips"]),
            "Exact after spacing/punctuation normalization",
        )

    city = normalized_text(ahrq_city)
    city = config["city_aliases"].get(city, city)
    if state == "CT":
        fips = config["connecticut_city_to_planning_region_fips"].get(city)
        if fips:
            return fips, "Connecticut town-to-2023 planning-region crosswalk"

    alaska_key = f"{state}|{county_norm}|{city}"
    if alaska_key in config["alaska_post_split"]:
        return (
            config["alaska_post_split"][alaska_key],
            "Alaska post-split crosswalk to Chugach Census Area",
        )

    alias_key = f"{state}|{county_norm}"
    if alias_key in config["county_aliases"]:
        return (
            config["county_aliases"][alias_key],
            "Documented county-name alias or typographic correction",
        )

    raise ValueError(
        f"No unique RUCC match for state={state!r}, "
        f"county={source_county!r}, city={ahrq_city!r}"
    )


def bed_category(beds: pd.Series) -> pd.Series:
    return pd.cut(
        beds,
        bins=[-np.inf, 24, 99, 399, np.inf],
        labels=["<25", "25–99", "100–399", "≥400"],
    ).astype("object")


def build_stage3_confounders(root: Path) -> dict[str, Any]:
    cohort_path = root / "data" / "processed" / "hospital_network_hcahps_cohort.csv"
    raw_dir = root / "data" / "raw"
    processed_dir = root / "data" / "processed"
    tables_dir = root / "outputs" / "tables"
    diagnostics_dir = root / "outputs" / "diagnostics"
    for directory in (processed_dir, tables_dir, diagnostics_dir):
        directory.mkdir(parents=True, exist_ok=True)

    cohort = pd.read_csv(
        cohort_path, dtype={"ccn": str, "profile_bits": str}
    )
    ahrq, ahrq_audit = prepare_ahrq(
        raw_dir / "chsp-hospital-linkage-2023.csv"
    )
    rucc, rucc_audit = prepare_rucc(
        raw_dir / "Ruralurbancontinuumcodes2023.csv"
    )
    geo_config = read_json(root / "config" / "geography_crosswalks.json")

    merged = cohort.merge(
        ahrq,
        left_on="ccn",
        right_on="ccn_norm",
        how="left",
        validate="one_to_one",
        indicator="_ahrq_merge",
        suffixes=("", "_ahrq_raw"),
    )
    merged["ahrq_match_status"] = np.where(
        merged["_ahrq_merge"].eq("both"), "Exact CCN", "Unmatched"
    )

    merged["ahrq_compendium_hospital_id"] = merged[
        "compendium_hospital_id"
    ].replace("", pd.NA)
    merged["ahrq_hospital_name"] = merged["hospital_name"].replace("", pd.NA)
    merged["ahrq_hospital_city"] = merged["hospital_city"].replace("", pd.NA)
    merged["ahrq_hospital_zip"] = merged["hospital_zip"].replace("", pd.NA)

    is_matched = merged["_ahrq_merge"].eq("both")
    system_id = merged["health_sys_id"].replace("", pd.NA)
    merged["health_system_affiliated"] = pd.Series(
        pd.NA, index=merged.index, dtype="Int64"
    )
    merged.loc[is_matched, "health_system_affiliated"] = (
        system_id.loc[is_matched].notna().astype(int)
    )
    merged["health_sys_id"] = system_id
    merged["health_sys_name"] = merged["health_sys_name"].replace("", pd.NA)

    field_map = {
        "hos_beds": "beds",
        "hos_dsch": "discharges",
        "hos_res": "residents_fte",
        "hos_children": "childrens_hospital_flag",
        "hos_majteach": "major_teaching_flag",
        "hos_vmajteach": "very_major_teaching_flag",
        "hos_teachint": "teaching_intensity",
        "hos_highdpp": "high_dsh_flag",
        "hos_ucburden": "uncompensated_care_burden",
        "hos_highuc": "high_uncompensated_care_flag",
        "hos_ownership": "ahrq_ownership_code",
    }
    integer_targets = {
        "childrens_hospital_flag",
        "major_teaching_flag",
        "very_major_teaching_flag",
        "high_dsh_flag",
        "high_uncompensated_care_flag",
        "ahrq_ownership_code",
    }
    for source, target in field_map.items():
        values = numeric(merged[source])
        merged[target] = (
            values.astype("Int64") if target in integer_targets else values
        )
    merged["ahrq_ownership_3cat"] = merged["ahrq_ownership_code"].map(
        map_ahrq_ownership
    )
    merged["cms_ownership_3cat"] = merged["ownership"].map(map_cms_ownership)
    both_ownership = merged[
        ["ahrq_ownership_3cat", "cms_ownership_3cat"]
    ].notna().all(axis=1)
    merged["ownership_agreement_flag"] = pd.Series(
        pd.NA, index=merged.index, dtype="Int64"
    )
    merged.loc[both_ownership, "ownership_agreement_flag"] = (
        merged.loc[both_ownership, "ahrq_ownership_3cat"]
        == merged.loc[both_ownership, "cms_ownership_3cat"]
    ).astype(int)

    rucc_lookup = rucc.set_index("fips")
    fips_values: list[str] = []
    rucc_methods: list[str] = []
    for row in merged.itertuples(index=False):
        fips, method = choose_rucc(
            row.state,
            row.county,
            "" if pd.isna(row.ahrq_hospital_city) else row.ahrq_hospital_city,
            rucc,
            geo_config,
        )
        fips_values.append(fips)
        rucc_methods.append(method)
    merged["county_fips_2023"] = fips_values
    merged["rucc_match_status"] = rucc_methods
    merged["county_equivalent_2023"] = merged["county_fips_2023"].map(
        rucc_lookup["County_Name"]
    )
    merged["rucc_2023"] = merged["county_fips_2023"].map(
        rucc_lookup["rucc_2023"]
    ).astype(int)
    merged["rucc_description"] = merged["county_fips_2023"].map(
        rucc_lookup["Description"]
    )
    merged["rurality_binary"] = np.where(
        merged["rucc_2023"].le(3), "Metro", "Nonmetro"
    )

    merged["log2_beds_plus1"] = np.log2(merged["beds"] + 1)
    merged["bed_category"] = bed_category(merged["beds"])
    merged["complete_required_covariates"] = (
        merged[REQUIRED_COVARIATES].notna().all(axis=1).astype(int)
    )

    merged = merged.rename(columns={"survey_year": "onc_survey_year"})
    base_columns = [
        "ccn",
        "aha_id",
        "facility_name",
        "state",
        "county",
        "hospital_type",
        "hospital_group",
        "ownership",
        "emergency_services",
        "onc_survey_year",
        "hio",
        "national_network",
        "vendor_network",
        "current_tefca",
        "planned_tefca",
        "network_count",
        "profile_bits",
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
        "profile_category_code",
        "profile_category_label",
    ]
    added_columns = [
        "ahrq_match_status",
        "rucc_match_status",
        "county_fips_2023",
        "county_equivalent_2023",
        "rucc_2023",
        "rucc_description",
        "rurality_binary",
        "ahrq_compendium_hospital_id",
        "ahrq_hospital_name",
        "ahrq_hospital_city",
        "ahrq_hospital_zip",
        "health_system_affiliated",
        "health_sys_id",
        "health_sys_name",
        "beds",
        "discharges",
        "residents_fte",
        "childrens_hospital_flag",
        "major_teaching_flag",
        "very_major_teaching_flag",
        "teaching_intensity",
        "high_dsh_flag",
        "uncompensated_care_burden",
        "high_uncompensated_care_flag",
        "ahrq_ownership_code",
        "ahrq_ownership_3cat",
        "cms_ownership_3cat",
        "ownership_agreement_flag",
        "log2_beds_plus1",
        "bed_category",
        "complete_required_covariates",
    ]
    output = merged[base_columns + added_columns].sort_values(
        "ccn", kind="mergesort"
    )
    output.to_csv(
        processed_dir / "Hospital_Network_Analysis_Ready_v1.csv", index=False
    )

    variable_specs = [
        ("Hospital beds", "beds", "Continuous"),
        ("Health-system affiliation", "health_system_affiliated", "Binary"),
        ("AHRQ/HCRIS ownership", "ahrq_ownership_3cat", "Categorical"),
        ("Teaching intensity", "teaching_intensity", "Continuous"),
        ("High DSH flag", "high_dsh_flag", "Binary"),
        (
            "Uncompensated-care burden",
            "uncompensated_care_burden",
            "Continuous",
        ),
        (
            "High uncompensated-care flag",
            "high_uncompensated_care_flag",
            "Binary",
        ),
        ("2023 RUCC", "rucc_2023", "Categorical"),
    ]
    completeness_rows = []
    group_rows = []
    for label, field, field_type in variable_specs:
        available = int(output[field].notna().sum())
        completeness_rows.append(
            {
                "variable": label,
                "field": field,
                "type": field_type,
                "available_n": available,
                "cohort_n": int(len(output)),
                "available_pct": 100 * available / len(output),
                "threshold_70_met": available / len(output) >= 0.70,
            }
        )
        for group, subset in output.groupby("hospital_group", sort=False):
            group_n = int(len(subset))
            observed = int(subset[field].notna().sum())
            group_rows.append(
                {
                    "hospital_group": group,
                    "variable": label,
                    "available_n": observed,
                    "group_n": group_n,
                    "available_pct": 100 * observed / group_n,
                }
            )
    pd.DataFrame(completeness_rows).to_csv(
        tables_dir / "stage3_variable_completeness.csv", index=False
    )
    pd.DataFrame(group_rows).to_csv(
        tables_dir / "stage3_group_completeness.csv", index=False
    )

    ownership_crosscheck = (
        output.dropna(
            subset=["cms_ownership_3cat", "ahrq_ownership_3cat"]
        )
        .groupby(["cms_ownership_3cat", "ahrq_ownership_3cat"])
        .size()
        .rename("hospital_n")
        .reset_index()
    )
    ownership_crosscheck.to_csv(
        tables_dir / "stage3_ownership_crosscheck.csv", index=False
    )

    rucc_distribution = (
        output.groupby(
            ["rucc_2023", "rurality_binary", "rucc_description"]
        )
        .agg(
            all_n=("ccn", "size"),
            acute_n=(
                "hospital_group",
                lambda values: int((values == "Acute Care").sum()),
            ),
            cah_n=(
                "hospital_group",
                lambda values: int((values == "Critical Access").sum()),
            ),
        )
        .reset_index()
    )
    rucc_distribution["percent_of_cohort"] = (
        100 * rucc_distribution["all_n"] / len(output)
    )
    rucc_distribution.to_csv(
        tables_dir / "stage3_rucc_distribution.csv", index=False
    )

    output.loc[
        output["ahrq_match_status"].eq("Unmatched"),
        ["ccn", "facility_name", "state", "hospital_group", "onc_survey_year"],
    ].to_csv(diagnostics_dir / "stage3_ahrq_unmatched.csv", index=False)
    output.loc[
        ~output["rucc_match_status"].eq("Exact normalized county"),
        [
            "ccn",
            "facility_name",
            "state",
            "county",
            "ahrq_hospital_city",
            "county_fips_2023",
            "county_equivalent_2023",
            "rucc_2023",
            "rucc_match_status",
        ],
    ].to_csv(
        diagnostics_dir / "stage3_geography_crosswalk_review.csv", index=False
    )

    both_count = int(both_ownership.sum())
    agreement_count = int((merged["ownership_agreement_flag"] == 1).sum())
    summary = {
        "ahrq_source": ahrq_audit,
        "rucc_source": rucc_audit,
        "ahrq_linkage": {
            "matched": int(is_matched.sum()),
            "unmatched": int((~is_matched).sum()),
            "match_rate_pct": 100 * is_matched.mean(),
        },
        "rucc_linkage": {
            "matched": int(output["rucc_2023"].notna().sum()),
            "unmatched": int(output["rucc_2023"].isna().sum()),
            "match_rate_pct": 100 * output["rucc_2023"].notna().mean(),
        },
        "complete_required_covariates": {
            "complete_n": int(output["complete_required_covariates"].sum()),
            "cohort_n": int(len(output)),
            "complete_pct": 100 * output["complete_required_covariates"].mean(),
            "acute_complete_n": int(
                output.loc[
                    output["hospital_group"].eq("Acute Care"),
                    "complete_required_covariates",
                ].sum()
            ),
            "cah_complete_n": int(
                output.loc[
                    output["hospital_group"].eq("Critical Access"),
                    "complete_required_covariates",
                ].sum()
            ),
        },
        "ownership_crosscheck": {
            "both_observed_n": both_count,
            "agreement_n": agreement_count,
            "disagreement_n": both_count - agreement_count,
            "agreement_pct": 100 * agreement_count / both_count,
        },
    }
    write_json(tables_dir / "stage3_confounder_summary.json", summary)
    return summary
