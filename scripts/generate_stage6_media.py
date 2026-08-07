"""Generate publication figures from canonical pipeline outputs."""
from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CAN = ROOT / "outputs" / "stage5" / "canonical"
OUT = ROOT / "outputs" / "stage6" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

LABELS_SHORT = {
    0: "None",
    1: "1 conventional",
    2: "2 conventional",
    3: "3 conventional",
    4: "TEFCA + 0–2",
    5: "TEFCA + 3",
}
LABELS_LONG = {
    0: "No coded participation",
    1: "One conventional",
    2: "Two conventional",
    3: "Three conventional",
    4: "TEFCA + 0–2",
    5: "TEFCA + three",
}


def require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required Stage 6 input is missing: {path.relative_to(ROOT)}")
    return path


def generate_figure_1() -> None:
    stage1 = json.loads(require(ROOT / "outputs" / "tables" / "stage1_linkage_summary.json").read_text())
    stage2 = json.loads(require(ROOT / "outputs" / "tables" / "stage2_hcahps_summary.json").read_text())

    raw_onc = int(stage1["onc"]["raw_rows"])
    unique_ccn = int(stage1["onc"]["unique_usable_ccns"])
    matched = int(stage1["linkage"]["matched_unique_onc_ccns"])
    eligible = int(stage1["linkage"]["eligible_acute_and_cah_all_years"])
    locked = int(stage1["locked_2024_2025_cohort"]["total"])
    outcome = int(stage2["primary_outcome"]["observed_total"])
    missing_ccn = int(stage1["onc"]["missing_ccn_rows"])
    duplicate_ccn = len(stage1["onc"].get("duplicate_ccns_resolved", []))

    boxes = [
        (0.5, 0.91, f"ONC hospital-network records\nN = {raw_onc:,}"),
        (0.5, 0.76, f"Usable unique CCNs after identifier QA\nN = {unique_ccn:,}"),
        (0.5, 0.61, f"Matched to CMS Hospital\nGeneral Information\nN = {matched:,}"),
        (0.5, 0.46, f"Acute Care or Critical Access Hospitals\nN = {eligible:,}"),
        (0.5, 0.31, f"ONC response from 2024 or 2025\nN = {locked:,}"),
        (0.5, 0.16, f"Primary HCAHPS outcome\npublicly reported\nN = {outcome:,}"),
    ]
    notes = [
        (0.83, 0.83, f"{missing_ccn} missing CCN;\n{duplicate_ccn} duplicate CCN resolved"),
        (0.83, 0.68, f"{unique_ccn-matched} unmatched to\ncurrent CMS file"),
        (0.83, 0.53, f"{matched-eligible} other hospital\ntypes excluded"),
        (0.83, 0.38, f"{eligible-locked} responses from\n2022–2023 excluded"),
        (0.83, 0.23, f"{locked-outcome} HCAHPS results\nnot publicly reported"),
    ]

    fig, ax = plt.subplots(figsize=(11, 10.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for x, y, text in boxes:
        width, height = 0.48, 0.075
        patch = FancyBboxPatch(
            (x - width / 2, y - height / 2),
            width,
            height,
            boxstyle="round,pad=0.008",
            fill=False,
            linewidth=1.2,
        )
        ax.add_patch(patch)
        ax.text(x, y, text, ha="center", va="center", fontsize=10.5, linespacing=1.0)
    for x, y, text in notes:
        ax.text(x, y, text, ha="center", va="center", fontsize=9)
    for i in range(len(boxes) - 1):
        ax.annotate(
            "",
            xy=(0.5, boxes[i + 1][1] + 0.045),
            xytext=(0.5, boxes[i][1] - 0.045),
            arrowprops=dict(arrowstyle="->", lw=1.2),
        )
    fig.savefig(OUT / "Figure_1_Cohort_Flow.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def generate_figure_2() -> None:
    means = pd.read_csv(require(CAN / "adjusted_profile_means.csv")).sort_values("profile_category")
    x = np.arange(len(means))
    y = means["estimate"].to_numpy()
    lower = y - means["ci_low"].to_numpy()
    upper = means["ci_high"].to_numpy() - y
    fig, ax = plt.subplots(figsize=(11, 6.7))
    ax.errorbar(x, y, yerr=np.vstack([lower, upper]), fmt="o", capsize=5)
    ax.set_xticks(x, [LABELS_SHORT[int(i)] for i in means.profile_category], rotation=25, ha="right")
    ax.set_ylabel("Adjusted discharge-information score (%)")
    ax.set_xlabel("Network-participation profile")
    ax.set_title("Adjusted HCAHPS discharge-information scores by network profile")
    ax.grid(axis="y", alpha=0.25)
    ax.set_ylim(min(means.ci_low) - 0.15, max(means.ci_high) + 0.15)
    fig.tight_layout()
    fig.savefig(OUT / "Figure_2_Adjusted_Profile_Means.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def generate_figure_3() -> None:
    sensitivity = pd.read_csv(require(CAN / "sensitivity_analyses.csv"))
    ypos = np.arange(len(sensitivity))[::-1]
    estimate = sensitivity.contrast_estimate.to_numpy()
    lower = estimate - sensitivity.contrast_ci_low.to_numpy()
    upper = sensitivity.contrast_ci_high.to_numpy() - estimate
    fig, ax = plt.subplots(figsize=(12, 7.6))
    ax.errorbar(estimate, ypos, xerr=np.vstack([lower, upper]), fmt="o", capsize=4)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(ypos, sensitivity.analysis)
    ax.set_xlabel("Adjusted percentage-point difference: profile 5 minus profile 3")
    ax.set_title("Prespecified TEFCA contrast across sensitivity analyses")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "Figure_3_TEFCA_Contrast_Sensitivities.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def generate_figure_4() -> None:
    interaction = pd.read_csv(require(CAN / "interaction_adjusted_means.csv"))
    fig, ax = plt.subplots(figsize=(12, 7.2))
    for offset, (group, marker) in zip(
        [-0.10, 0.10],
        [("Acute Care", "o"), ("Critical Access", "s")],
    ):
        subset = interaction[interaction.hospital_group == group].sort_values("profile_category")
        xx = np.arange(6) + offset
        yy = subset.estimate.to_numpy()
        lower = yy - subset.ci_low.to_numpy()
        upper = subset.ci_high.to_numpy() - yy
        ax.errorbar(xx, yy, yerr=np.vstack([lower, upper]), fmt=marker, capsize=5, label=group)
    ax.set_xticks(np.arange(6), [LABELS_LONG[i] for i in range(6)], rotation=22, ha="right")
    ax.set_ylabel("Adjusted discharge-information score (%)")
    ax.set_xlabel("Network-participation profile")
    ax.set_title("Adjusted network-profile means by hospital group")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    ax.text(
        0.5,
        -0.22,
        "Profiles are categorical and are therefore not connected. The vertical axis is truncated to display adjusted differences.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(OUT / "Figure_4_Profile_Means_by_Hospital_Group.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def generate_figure_s1() -> None:
    balance = pd.read_csv(require(CAN / "balance_diagnostics_by_stratum.csv")).copy()
    label_map = {
        "log2_beds_plus1": "Hospital size, log2(beds + 1)",
        "ownership_forprofit": "For-profit ownership",
        "ownership_nonprofit": "Nonprofit ownership",
        "profile_0": "No coded participation",
        "profile_1": "One conventional network",
        "profile_2": "Two conventional networks",
        "profile_4": "TEFCA + 0–2 conventional networks",
        "profile_5": "TEFCA + three conventional networks",
        "high_uncompensated_care_flag": "High uncompensated-care burden",
        "uncompensated_care_burden": "Uncompensated-care burden",
        "high_dsh_flag": "High DSH patient percentage",
        "health_system_affiliated": "Health-system affiliated",
        "teaching_intensity": "Teaching intensity",
        "nonmetro": "Nonmetropolitan county",
        "year2025": "ONC survey year 2025",
        "CAH": "CAH status",
    }
    balance["rank"] = balance[["max_abs_smd_before", "max_abs_smd_after"]].max(axis=1)
    subset = balance.sort_values("rank", ascending=False).head(14).iloc[::-1].copy()
    subset["label"] = [
        f"{label_map.get(variable, variable)} — {group}, {year}"
        for variable, group, year in zip(subset.variable, subset.hospital_group, subset.onc_survey_year)
    ]
    y = np.arange(len(subset))
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.scatter(subset.max_abs_smd_before, y, marker="x", label="Before weighting")
    ax.scatter(subset.max_abs_smd_after, y, marker="o", label="After weighting")
    ax.axvline(0.10, linestyle="--", linewidth=1)
    ax.set_yticks(y, subset.label)
    ax.set_xlabel("Maximum absolute standardized mean difference")
    ax.set_title("Outcome-observation weight balance diagnostics")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "Figure_S1_Weight_Balance.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4()
    generate_figure_s1()
    expected = {
        "Figure_1_Cohort_Flow.png",
        "Figure_2_Adjusted_Profile_Means.png",
        "Figure_3_TEFCA_Contrast_Sensitivities.png",
        "Figure_4_Profile_Means_by_Hospital_Group.png",
        "Figure_S1_Weight_Balance.png",
    }
    actual = {path.name for path in OUT.glob("*.png")}
    missing = expected - actual
    if missing:
        raise RuntimeError(f"Stage 6 figure generation incomplete: {sorted(missing)}")
    print("generated", sorted(expected))


if __name__ == "__main__":
    main()
