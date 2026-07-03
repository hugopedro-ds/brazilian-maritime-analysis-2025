"""
Post 9 — Chart final (dados reais).

Lê:
  - Data/post9/carrier_by_call.csv (dataset completo classificado)
  - Data/post9/hhi_summary.csv     (métricas HHI)
  - Data/post9/alliance_summary.csv

Gera:
  - Outputs/post9/post9_chart_final.png

Layout (validado com Hugo):
  - 3 painéis composto (heatmap + HHI por porto + alliance stacked bar)
  - 11 portos individualmente
  - Top-10 carriers + UNKNOWN incluído no heatmap
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec

# =============================================================================
# Paths
# =============================================================================

_script_dir = Path(__file__).resolve().parent
cowork_root = _script_dir.parent.parent
if (cowork_root / "Outputs").exists():
    DATA_DIR = cowork_root / "Data" / "post9"
    OUT_DIR = cowork_root / "Outputs" / "post9"
else:
    DATA_DIR = _script_dir.parent / "data"
    OUT_DIR = _script_dir.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Load real data
# =============================================================================

df = pd.read_csv(DATA_DIR / "carrier_by_call.csv", sep=";", encoding="utf-8-sig")

# Short port labels for the x-axis
PORT_SHORT = {
    "Santos": "Santos",
    "Paranaguá": "Paranaguá",
    "Rio Grande": "Rio Grande",
    "Portonave - Terminais Portuários de Navegantes": "Portonave",
    "Rio de Janeiro": "Rio Janeiro",
    "Itajaí": "Itajaí",
    "Vitória": "Vitória",
    "São Francisco do Sul": "S. Francisco",
    "Salvador": "Salvador",
    "Terminal Portuário do Pecém": "Pecém",
    "Super Terminais Comércio e Indústria": "Manaus",
}
df["Porto_short"] = df["Porto Atracação"].map(PORT_SHORT)

# Top-10 carriers + UNKNOWN, ordered by alliance (validated with Hugo).
# Purpose: heatmap tells the alliance-level story visually — carriers of the
# same alliance sit together, so the reader sees blocks not scattered points.
carrier_totals = df["carrier"].value_counts()
TOP_10 = [c for c in carrier_totals.head(11).index.tolist() if c != "UNKNOWN"][:10]

# Alliance grouping for top-10 (Feb 2025 config)
ALLIANCE_GROUPS = [
    ("MSC (standalone)",   ["MSC"]),
    ("Gemini Cooperation", ["MAERSK", "HAPAG-LLOYD"]),
    ("Ocean Alliance",      ["CMA CGM", "COSCO", "EVERGREEN", "MERCOSUL"]),
    ("Premier Alliance",    ["HMM"]),
    ("Non-aligned",         ["PIL"]),
    ("Non-aligned (reg.)",  ["LOG-IN"]),
]
CARRIERS_ORDER = []
GROUP_BOUNDARIES = []  # positions where to draw a separator line
GROUP_LABELS = []       # (position_center, label) for alliance grouping ticks
pos = 0
for alli_name, members in ALLIANCE_GROUPS:
    in_top = [c for c in members if c in TOP_10]
    if not in_top:
        continue
    start = pos
    for c in in_top:
        CARRIERS_ORDER.append(c)
        pos += 1
    end = pos - 1
    GROUP_LABELS.append(((start + end) / 2, alli_name))
    GROUP_BOUNDARIES.append(pos - 0.5)  # boundary after this group
# Any TOP_10 carriers not yet added
for c in TOP_10:
    if c not in CARRIERS_ORDER:
        CARRIERS_ORDER.append(c)
# UNKNOWN last
CARRIERS_ORDER.append("UNKNOWN")
GROUP_LABELS.append((len(CARRIERS_ORDER) - 1, "Unknown"))

# --- Coherence rule: exclude ports with fewer than MIN_CALLS across all 3 panels
MIN_CALLS_FOR_INCLUSION = 20
port_totals = df["Porto_short"].value_counts()
PORT_ORDER = port_totals[port_totals >= MIN_CALLS_FOR_INCLUSION].index.tolist()
ports_excluded = port_totals[port_totals < MIN_CALLS_FOR_INCLUSION]
EXCLUDED_NOTE = ""
if len(ports_excluded) > 0:
    EXCLUDED_NOTE = "Excluded: " + ", ".join(
        [f"{p} ({int(n)} container calls)" for p, n in ports_excluded.items()]
    )
    # Filter the dataframe so all 3 panels use the same port set
    df = df[df["Porto_short"].isin(PORT_ORDER)].copy()

# =============================================================================
# Build matrix (%)
# =============================================================================

matrix = (df.groupby(["carrier", "Porto_short"]).size()
          .unstack(fill_value=0)
          .reindex(index=CARRIERS_ORDER, columns=PORT_ORDER, fill_value=0))

# Convert to % of port total
matrix_pct = matrix.div(matrix.sum(axis=0), axis=1) * 100

# HHI per port (from % matrix)
hhi_per_port = (matrix_pct ** 2).sum(axis=0)

# =============================================================================
# Alliance shares per port
# =============================================================================

alliance_matrix = (df.groupby(["alliance", "Porto_short"]).size()
                   .unstack(fill_value=0))
alliance_pct = alliance_matrix.div(alliance_matrix.sum(axis=0), axis=1) * 100

# Order alliances for stacking (identified first, unknown last)
ALLIANCE_ORDER = [
    "MSC (standalone)",
    "Gemini Cooperation",
    "Ocean Alliance",
    "Premier Alliance",
    "Non-aligned",
    "Regional / affiliated carrier",
    "Unknown",
]
alliance_pct = alliance_pct.reindex(ALLIANCE_ORDER, fill_value=0)
alliance_pct = alliance_pct[PORT_ORDER]

# =============================================================================
# Colours
# =============================================================================

ALLIANCE_COLORS = {
    "MSC (standalone)":              "#FEC00A",
    "Gemini Cooperation":            "#0055A4",
    "Ocean Alliance":                 "#00A651",
    "Premier Alliance":               "#DA1F26",
    "Non-aligned":                    "#666666",
    "Regional / affiliated carrier":  "#B85A3F",
    "Unknown":                        "#DDDDDD",
}

# Colour bar heatmap
cmap = LinearSegmentedColormap.from_list(
    "biz_gradient", ["#F5F5F5", "#FFC98A", "#F27200", "#8B2500"], N=256
)

# =============================================================================
# Plot
# =============================================================================

fig = plt.figure(figsize=(18, 13), dpi=110)
gs = GridSpec(3, 2, figure=fig,
              height_ratios=[0.65, 3.2, 2.6], width_ratios=[1, 1],
              hspace=0.55, wspace=0.22,
              left=0.05, right=0.97, top=0.94, bottom=0.06)

# ---- Header ----
ax_h = fig.add_subplot(gs[0, :])
ax_h.axis("off")
total_calls = len(df)
n_identified = (df["carrier"] != "UNKNOWN").sum()
identification_pct = n_identified / total_calls * 100
n_vessels = df["imo"].nunique()

ax_h.text(0.0, 0.85,
          "Container carrier deployment — Brazilian ports, 2025",
          fontsize=24, fontweight="bold", va="top")
n_ports_shown = len(PORT_ORDER)
ax_h.text(0.0, 0.42,
          f"Longo Curso  •  {n_ports_shown} container ports  •  "
          f"{total_calls:,} vessel calls  •  {n_vessels:,} unique IMOs  •  "
          f"{identification_pct:.1f}% carrier-identified  •  "
          "Source: ANTAQ 2025 + VesselFinder",
          fontsize=11, va="top", color="#555555")
if EXCLUDED_NOTE:
    ax_h.text(0.0, 0.10, EXCLUDED_NOTE + "  (insufficient container sample)",
              fontsize=9, va="top", color="#888", style="italic")

# ---- Panel 1: Heatmap ----
ax1 = fig.add_subplot(gs[1, :])
max_val = max(35, matrix_pct.values.max())
im = ax1.imshow(matrix_pct.values, cmap=cmap, aspect="auto", vmin=0, vmax=max_val)
ax1.set_xticks(range(len(PORT_ORDER)))
ax1.set_xticklabels(PORT_ORDER, rotation=30, ha="right", fontsize=11)
ax1.set_yticks(range(len(CARRIERS_ORDER)))
ax1.set_yticklabels(CARRIERS_ORDER, fontsize=11)
ax1.set_title("Deployment share by carrier × port  (% of container calls)",
              fontsize=14, fontweight="bold", loc="left", pad=12)

# Annotate cells
for i in range(len(CARRIERS_ORDER)):
    for j in range(len(PORT_ORDER)):
        v = matrix_pct.values[i, j]
        if v < 0.5:
            continue
        color = "white" if v > max_val * 0.55 else "#222222"
        ax1.text(j, i, f"{v:.0f}", ha="center", va="center",
                 fontsize=9, color=color)

# Draw horizontal separators between alliance groups
for b in GROUP_BOUNDARIES[:-1]:  # skip the last (bottom of chart)
    ax1.axhline(b, color="#333333", lw=1.2, alpha=0.85)

# Add right-side alliance labels
for pos_center, label in GROUP_LABELS:
    ax1.text(len(PORT_ORDER) - 0.3, pos_center, label,
             fontsize=9, color="#444", va="center", ha="left",
             style="italic")

# Extend x range a bit to fit alliance labels on the right
ax1.set_xlim(-0.5, len(PORT_ORDER) - 0.5 + 2.5)

cbar = plt.colorbar(im, ax=ax1, fraction=0.025, pad=0.10)
cbar.set_label("% of calls", fontsize=10)
cbar.ax.tick_params(labelsize=9)

# ---- Panel 2: HHI per port ----
ax2 = fig.add_subplot(gs[2, 0])
hhi_sorted = hhi_per_port.sort_values(ascending=True)
colors_hhi = ["#2E7D32" if v < 1500 else ("#F27200" if v < 2500 else "#C62828")
              for v in hhi_sorted.values]
bars = ax2.barh(range(len(hhi_sorted)), hhi_sorted.values, color=colors_hhi,
                edgecolor="white", linewidth=0.6)
ax2.set_yticks(range(len(hhi_sorted)))
ax2.set_yticklabels(hhi_sorted.index, fontsize=11)
ax2.set_xlabel("HHI (call-weighted, all carriers incl. UNKNOWN)", fontsize=10)
ax2.set_title("Carrier concentration by port (HHI)",
              fontsize=14, fontweight="bold", loc="left", pad=12)

xmax = hhi_sorted.max() * 1.20
ax2.axvline(1500, ls="--", color="#666", lw=0.8, alpha=0.5)
ax2.axvline(2500, ls="--", color="#666", lw=0.8, alpha=0.5)
# Threshold labels — placed at the TOP of the panel (above bars, in blank area)
ax2.text(1500, len(hhi_sorted) - 0.3, "Moderate\n(1500)", fontsize=8, color="#666",
         ha="center", va="top",
         bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                   edgecolor="none", alpha=0.85))
ax2.text(2500, len(hhi_sorted) - 0.3, "High\n(2500)", fontsize=8, color="#666",
         ha="center", va="top",
         bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                   edgecolor="none", alpha=0.85))

for i, v in enumerate(hhi_sorted.values):
    ax2.text(v + xmax * 0.015, i, f"{v:.0f}",
             va="center", fontsize=10, fontweight="bold")

ax2.set_xlim(0, xmax)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

# ---- Panel 3: Alliance stacked bar ----
ax3 = fig.add_subplot(gs[2, 1])
bottom = np.zeros(len(PORT_ORDER))
for alli in ALLIANCE_ORDER:
    vals = alliance_pct.loc[alli].values
    ax3.barh(range(len(PORT_ORDER)), vals, left=bottom, label=alli,
             color=ALLIANCE_COLORS[alli], edgecolor="white", linewidth=0.6)
    bottom += vals

ax3.set_yticks(range(len(PORT_ORDER)))
ax3.set_yticklabels(PORT_ORDER, fontsize=11)
ax3.set_xlabel("% of container calls", fontsize=10)
ax3.set_title("Alliance share by port (Feb 2025 config)",
              fontsize=14, fontweight="bold", loc="left", pad=12)
ax3.set_xlim(0, 100)
ax3.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14),
           fontsize=9, ncol=4, frameon=False)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.invert_yaxis()

# Save
out_file = OUT_DIR / "post9_chart_final.png"
plt.savefig(out_file, dpi=140, bbox_inches="tight", facecolor="white")
print(f"Saved: {out_file}")

# Print key numbers for post writing
print("\n=== KEY NUMBERS FOR POST ===")
print(f"Total container calls: {total_calls:,}")
print(f"Unique IMOs: {n_vessels:,}")
print(f"Coverage identified: {identification_pct:.1f}%")
print(f"\nTop-10 carriers by calls (% of total):")
for c in TOP_10:
    n = matrix.loc[c].sum()
    print(f"  {c:15} {n:>5,} calls ({n/total_calls*100:>5.2f}%)")
print(f"  {'UNKNOWN':15} {matrix.loc['UNKNOWN'].sum():>5,} calls ({matrix.loc['UNKNOWN'].sum()/total_calls*100:>5.2f}%)")

print(f"\nHHI per port (sorted highest → lowest):")
for port, hhi in hhi_per_port.sort_values(ascending=False).items():
    marker = " HIGH" if hhi >= 2500 else (" MOD" if hhi >= 1500 else "")
    print(f"  {port:15} {hhi:>6.0f}{marker}")

print(f"\nAlliance shares (% of total calls):")
alliance_totals = df["alliance"].value_counts()
for alli, n in alliance_totals.items():
    print(f"  {alli:25} {n:>5,} ({n/total_calls*100:>5.2f}%)")
