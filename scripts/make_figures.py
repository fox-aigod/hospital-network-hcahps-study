"""
Deterministic regeneration of Figure 1 (cohort flow) and Figure 3
(adjusted network-profile means by hospital group) for the Cureus
resubmission. Display-only: no model is refit.
Figure 3 reads release/v1.0.0/stage5/interaction_adjusted_means.csv; Figure 1 uses locked cohort counts from the validated v1.0.0 analysis, checked by arithmetic assertions.

Usage:
    python make_figures.py --means interaction_adjusted_means.csv --outdir figures
"""
import argparse
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.linewidth": 0.8,
    "savefig.facecolor": "white",
})

def r_half_up(x, nd):
    q = Decimal(1).scaleb(-nd)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))

def fmt_n_pct(n, denom):
    pct = r_half_up(100 * n / denom, 1)
    pct_txt = "100%" if n == denom else f"{pct:.1f}%"
    return f"{n:,} ({pct_txt})", pct

# ------------------------------------------------------------------ FIGURE 1
STEPS = [  # (label, N)
    ("ONC hospital-network records", 3393),
    ("Usable unique CCNs after identifier QA", 3380),
    ("Matched to CMS Hospital General Information", 3293),
    ("Acute Care or Critical Access Hospitals", 3250),
    ("Latest ONC response from 2024 or 2025", 2651),
    ("Primary HCAHPS outcome publicly reported", 2409),
]
EXCLUSIONS = [  # (count, text, extra line or None) between step i and i+1
    (12,  "without a usable\nnumeric CCN", "1 duplicate record removed\n(latest survey year retained)"),
    (87,  "unmatched to current\nCMS file", None),
    (43,  "other CMS hospital\ntypes excluded", None),
    (599, "with latest ONC response from\n2022–2023 excluded", None),
    (242, "HCAHPS results not\npublicly reported", None),
]
EXPECTED_STEP_PCT = [100.0, 99.6, 97.4, 98.7, 81.6, 90.9]
EXPECTED_EXCL_PCT = [0.4, 2.6, 1.3, 18.4, 9.1]
DUPLICATES_RESOLVED = 1

def figure1(outdir):
    # arithmetic checks
    for i, (cnt, _, _) in enumerate(EXCLUSIONS):
        prev, nxt = STEPS[i][1], STEPS[i + 1][1]
        extra = DUPLICATES_RESOLVED if i == 0 else 0
        assert prev - cnt - extra == nxt, f"Step {i+1}->{i+2}: {prev}-{cnt}-{extra} != {nxt}"
    rows = []
    fig, ax = plt.subplots(figsize=(8.4, 8.6))
    ax.set_xlim(0, 12.2); ax.set_ylim(0, 12.4); ax.axis("off")
    box_w, box_h, cx = 6.0, 1.05, 3.2
    ys = [11.3 - i * 2.1 for i in range(len(STEPS))]
    for i, (label, n) in enumerate(STEPS):
        denom = STEPS[0][1] if i == 0 else STEPS[i - 1][1]
        txt, pct = fmt_n_pct(n, denom)
        assert pct == EXPECTED_STEP_PCT[i], f"Box {i+1}: {pct} != {EXPECTED_STEP_PCT[i]}"
        rows.append(("Box", i + 1, label, txt))
        ax.add_patch(FancyBboxPatch((cx - box_w / 2, ys[i] - box_h / 2), box_w, box_h,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    linewidth=1.0, edgecolor="black", facecolor="white"))
        ax.text(cx, ys[i] + 0.18, label, ha="center", va="center", fontsize=9.5)
        ax.text(cx, ys[i] - 0.22, f"N = {txt}", ha="center", va="center",
                fontsize=9.5, fontweight="bold")
    for i, (cnt, text, extra) in enumerate(EXCLUSIONS):
        y_top, y_bot = ys[i] - box_h / 2, ys[i + 1] + box_h / 2
        ax.annotate("", xy=(cx, y_bot), xytext=(cx, y_top),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0,
                                    mutation_scale=12, shrinkA=0, shrinkB=0))
        ymid = (y_top + y_bot) / 2
        ax.plot([cx, cx + 3.35], [ymid, ymid], color="black", lw=0.8)
        txt, pct = fmt_n_pct(cnt, STEPS[i][1])
        assert pct == EXPECTED_EXCL_PCT[i], f"Exclusion {i+1}: {pct} != {EXPECTED_EXCL_PCT[i]}"
        note = f"{txt} {text}"
        if extra:
            note += f";\n{extra}"
        rows.append(("Exclusion", i + 1, text.replace("\n", " "), txt))
        ax.text(cx + 3.45, ymid, note, ha="left", va="center", fontsize=8.5, linespacing=1.25)
    for ext in ("png", "pdf"):
        fig.savefig(Path(outdir) / f"figure1_cohort_flow.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return rows

# ------------------------------------------------------------------ FIGURE 3
PROFILE_LABELS = ["None", "1\nconventional", "2\nconventional", "3\nconventional",
                  "TEFCA\n+ 0–2", "TEFCA\n+ 3"]
TABLE9 = {  # (group, code): (mean, lower, upper) at 2 dp, as printed in Table 9
    ("Acute Care", 0): (85.79, 84.67, 86.91), ("Acute Care", 1): (83.92, 83.28, 84.56),
    ("Acute Care", 2): (85.93, 85.61, 86.25), ("Acute Care", 3): (85.93, 85.63, 86.24),
    ("Acute Care", 4): (85.25, 84.83, 85.68), ("Acute Care", 5): (86.05, 85.75, 86.36),
    ("Critical Access", 0): (89.51, 87.77, 91.24), ("Critical Access", 1): (88.81, 87.61, 90.00),
    ("Critical Access", 2): (88.99, 88.23, 89.74), ("Critical Access", 3): (88.63, 87.49, 89.76),
    ("Critical Access", 4): (88.96, 88.04, 89.88), ("Critical Access", 5): (89.63, 88.64, 90.63),
}
SERIES = [  # group key, legend label, color, marker, x offset
    ("Acute Care", "Acute Care Hospitals", "#1f77b4", "o", -0.09),
    ("Critical Access", "Critical Access Hospitals (CAHs)", "#ff7f0e", "s", +0.09),
]

def figure3(means_df, outdir):
    rows, failures = [], []
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for key, lab, col, mk, off in SERIES:
        sub = means_df[means_df["group"] == key].set_index("code").sort_index()
        assert list(sub.index) == [0, 1, 2, 3, 4, 5], f"{key}: codes {list(sub.index)}"
        for code, r in sub.iterrows():
            got = tuple(r_half_up(v, 2) for v in (r["mean"], r["lower"], r["upper"]))
            exp = TABLE9[(key, code)]
            rows.append((key, code, r["mean"], r["lower"], r["upper"], got, exp))
            if got != exp:
                failures.append((key, code, (r["mean"], r["lower"], r["upper"]), exp))
        x = [c + off for c in sub.index]
        ax.errorbar(x, sub["mean"], yerr=[sub["mean"] - sub["lower"], sub["upper"] - sub["mean"]],
                    fmt=mk, color=col, ecolor=col, markersize=5.5, capsize=3.5,
                    elinewidth=1.1, capthick=1.1, linestyle="none", label=lab)
    if failures:
        for f in failures:
            print("MISMATCH", f)
        sys.exit("Figure 3 values do not match Table 9. Report full-precision values; do not adjust.")
    ax.set_xticks(range(6)); ax.set_xticklabels(PROFILE_LABELS, fontsize=9)
    ax.set_xlim(-0.5, 5.5); ax.set_ylim(82, 92); ax.set_yticks(range(82, 93, 2))
    ax.set_xlabel("Network-participation profile"); ax.set_ylabel("Adjusted discharge-information score (%)")
    ax.yaxis.grid(True, color="0.85", linewidth=0.6); ax.set_axisbelow(True)
    ax.legend(loc="lower right", fontsize=8.5, frameon=True)
    for ext in ("png", "pdf"):
        fig.savefig(Path(outdir) / f"figure3_profile_means_by_group.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return rows

def load_means(path, colmap):
    df = pd.read_csv(path)
    print("CSV columns:", list(df.columns)); print(df.head(12).to_string())
    df = df.rename(columns={v: k for k, v in colmap.items()})
    missing = {"group", "code", "mean", "lower", "upper"} - set(df.columns)
    if missing:
        sys.exit(f"Missing columns after mapping: {missing}. Set --colmap to match the CSV.")
    df["group"] = df["group"].replace(GROUP_ALIASES)
    df["code"] = df["code"].astype(int)
    return df[["group", "code", "mean", "lower", "upper"]]

GROUP_ALIASES = {"Acute Care Hospital": "Acute Care", "ACH": "Acute Care", "acute_care": "Acute Care",
                 "0": "Acute Care", 0: "Acute Care", "Critical Access Hospital": "Critical Access",
                 "CAH": "Critical Access", "critical_access": "Critical Access", "1": "Critical Access",
                 1: "Critical Access"}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--means", required=True)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--colmap", default="group=group,code=code,mean=mean,lower=lower,upper=upper",
                    help="target=csv_column pairs, e.g. group=hospital_group,code=profile,...")
    a = ap.parse_args()
    Path(a.outdir).mkdir(parents=True, exist_ok=True)
    colmap = dict(kv.split("=") for kv in a.colmap.split(","))
    r1 = figure1(a.outdir)
    r3 = figure3(load_means(a.means, colmap), a.outdir)
    print("\nFIGURE 1 VERIFICATION"); [print(r) for r in r1]
    print("\nFIGURE 3 VERIFICATION (full precision -> rounded vs Table 9)"); [print(r) for r in r3]
    print("\nAll assertions passed.")
