"""
Post 9 — Carousel v3.

Layout matches Hugo's approved reference:
  Slide 1: heatmap deployment (wide format, colorbar on the right)
  Slide 2: HHI ranking (left) + Alliance share (right) — dual-panel wide

Styling matches Post 8:
  - Centered declarative title
  - Centered subtitle (grey, medium)
  - Small centered meta (light grey, italic)
  - Restricted palette: dark red HIGH / amber MODERATE / single-hue red heatmap
  - Two-line footer: scope | source | github URL

Format: 1600×900 landscape (16:9) — reads well on LinkedIn feed
        both slides same aspect ratio for carousel consistency
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# =============================================================================
# Paths + data prep
# =============================================================================

_script_dir = Path(__file__).resolve().parent
cowork_root = _script_dir.parent.parent
DATA_DIR = cowork_root / "Data" / "post9"
OUT_DIR = cowork_root / "Outputs" / "post9"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_DIR / "carrier_by_call.csv", sep=";", encoding="utf-8-sig")

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

carrier_totals = df["carrier"].value_counts()
TOP_10 = [c for c in carrier_totals.head(11).index.tolist() if c != "UNKNOWN"][:10]

MIN_CALLS = 20
port_totals = df["Porto_short"].value_counts()
PORT_ORDER = port_totals[port_totals >= MIN_CALLS].index.tolist()
df = df[df["Porto_short"].isin(PORT_ORDER)].copy()

# Alliance grouping (for slide 1 side-labels)
ALLIANCE_GROUPS = [
    ("MSC (standalone)",    ["MSC"]),
    ("Gemini Cooperation",  ["MAERSK", "HAPAG-LLOYD"]),
    ("Ocean Alliance",       ["CMA CGM", "COSCO", "EVERGREEN", "MERCOSUL"]),
    ("Premier Alliance",     ["HMM"]),
    ("Non-aligned",          ["PIL"]),
    ("Non-aligned (reg.)",   ["LOG-IN"]),
]
CARRIERS_ORDER = []
GROUP_BOUNDARIES = []
GROUP_LABELS = []
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
    GROUP_BOUNDARIES.append(pos - 0.5)
for c in TOP_10:
    if c not in CARRIERS_ORDER:
        CARRIERS_ORDER.append(c)
CARRIERS_ORDER.append("UNKNOWN")
GROUP_LABELS.append((len(CARRIERS_ORDER) - 1, "Unknown"))

# Matrix
matrix = (df.groupby(["carrier", "Porto_short"]).size()
          .unstack(fill_value=0)
          .reindex(index=CARRIERS_ORDER, columns=PORT_ORDER, fill_value=0))
matrix_pct = matrix.div(matrix.sum(axis=0), axis=1) * 100
hhi_per_port = (matrix_pct ** 2).sum(axis=0)

# Alliance shares per port
alliance_matrix = (df.groupby(["alliance", "Porto_short"]).size()
                   .unstack(fill_value=0))
alliance_pct = alliance_matrix.div(alliance_matrix.sum(axis=0), axis=1) * 100
# Alliance order (Feb 2025 config, validated with Hugo):
#   MSC standalone | Gemini | Ocean Alliance | Premier | Non-aligned | Regional | Unknown
ALLIANCE_ORDER = [
    "MSC (standalone)",
    "Gemini Cooperation",
    "Ocean Alliance",
    "Premier Alliance",
    "Non-aligned",
    "Regional / affiliated carrier",
    "Unknown",
]
alliance_pct = alliance_pct.reindex(ALLIANCE_ORDER, fill_value=0)[PORT_ORDER]

# =============================================================================
# Styling
# =============================================================================

COLOR_HIGH       = "#8B2929"
COLOR_MODERATE   = "#D4772A"
COLOR_TEXT_DARK  = "#222222"
COLOR_TEXT_GREY  = "#666666"
COLOR_TEXT_LIGHT = "#888888"

ALLIANCE_COLORS = {
    "MSC (standalone)":              "#FEC00A",
    "Gemini Cooperation":            "#0055A4",
    "Ocean Alliance":                 "#00A651",
    "Premier Alliance":               "#DA1F26",
    "Non-aligned":                    "#666666",
    "Regional / affiliated carrier":  "#B85A3F",   # rust/terracotta — reads distinct from all others
    "Unknown":                        "#DDDDDD",
}

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

cmap_heat = LinearSegmentedColormap.from_list(
    "post8_reds",
    ["#FBFBFB", "#F4D4C0", "#E39270", "#B85F3F", "#8B2929"],
    N=256,
)

GITHUB_URL = "github.com/hugopedreira/brazilian-maritime-analysis-2025"

# Base numbers for headers/footers
total_calls = len(df)
n_vessels = df["imo"].nunique()
identification_pct = (df["carrier"] != "UNKNOWN").sum() / total_calls * 100


def add_footer(fig, scope_text, caveats_text=None):
    """
    Three-line footer:
      Line 1 (top):    scope / metrics — centered, italic grey
      Line 2 (mid):    caveats (exclusions, timeline) — centered, italic light grey
      Line 3 (bottom): source (left) | github URL (right) — light grey
    """
    fig.text(0.5, 0.075, scope_text, ha="center", va="bottom",
             fontsize=9, color=COLOR_TEXT_GREY, style="italic")
    if caveats_text:
        fig.text(0.5, 0.049, caveats_text, ha="center", va="bottom",
                 fontsize=8.5, color=COLOR_TEXT_LIGHT, style="italic")
    fig.text(0.05, 0.020,
             "Source:  ANTAQ 2025 (Brazilian Port Authority)  ·  "
             "vessel-carrier attribution via name pattern matching",
             ha="left", va="bottom",
             fontsize=8.5, color=COLOR_TEXT_LIGHT)
    fig.text(0.95, 0.020, GITHUB_URL, ha="right", va="bottom",
             fontsize=8.5, color=COLOR_TEXT_LIGHT)


def _add_footer_3lines(fig, scope_text, caveats_text):
    """Common 3-line footer used by both slides for visual identity.

    Line 1 (top):    scope / metrics or HHI thresholds — italic grey
    Line 2 (mid):    caveats (exclusions, timeline, methodology) — italic light grey
    Line 3 (bottom): source (left) + github URL (right)
    """
    fig.text(0.5, 0.080, scope_text, ha="center", va="bottom",
             fontsize=9, color=COLOR_TEXT_GREY, style="italic")
    fig.text(0.5, 0.052, caveats_text, ha="center", va="bottom",
             fontsize=8.5, color=COLOR_TEXT_LIGHT, style="italic")
    fig.text(0.05, 0.022,
             "Source: ANTAQ 2025 (Brazilian Port Authority) + VesselFinder  ·  "
             "vessel-carrier attribution via name pattern matching",
             ha="left", va="bottom",
             fontsize=8.5, color=COLOR_TEXT_LIGHT)
    fig.text(0.95, 0.022, GITHUB_URL, ha="right", va="bottom",
             fontsize=8.5, color=COLOR_TEXT_LIGHT)


def add_footer_slide1(fig):
    """Slide 1 footer — scope numbers + shared caveats."""
    _add_footer_3lines(
        fig,
        scope_text=(
            f"Scope:  9 main Brazilian container ports  ·  "
            f"15 container terminals  ·  "
            f"{total_calls:,} vessel calls  ·  "
            f"{n_vessels:,} unique IMOs  ·  "
            f"{identification_pct:.1f}% carrier-identified"
        ),
        caveats_text=(
            "Long-haul container calls only  ·  "
            "Feb 2025 alliance configuration  ·  "
            "Unknown = unclassified calls pending validation  ·  "
            "S. Francisco and Vitória excluded (n<20 container calls)  ·  "
            "Full-year 2025 dataset (ANTAQ 2026 not yet consolidated)  ·  "
            "Full methodology on GitHub"
        ),
    )


def add_footer_slide2(fig):
    """Slide 2 footer — HHI formula + DOJ/FTC bands + shared caveats."""
    _add_footer_3lines(
        fig,
        scope_text=(
            "Scope:  9 main Brazilian container ports  ·  "
            "HHI = Σ (share)²  ·  "
            "DOJ/FTC bands:  >2,500 highly concentrated,  "
            "1,500–2,500 moderate,  <1,500 competitive"
        ),
        caveats_text=(
            "Feb 2025 alliance configuration  ·  "
            "S. Francisco and Vitória excluded (n<20 container calls)  ·  "
            "Full-year 2025 dataset (ANTAQ 2026 not yet consolidated)  ·  "
            "Full methodology on GitHub"
        ),
    )


def add_header(fig, title, subtitle, meta, meta_y=None):
    """Header with optional meta_y override for multi-line subtitles."""
    fig.text(0.5, 0.945, title, ha="center", va="top",
             fontsize=24, fontweight="bold", color=COLOR_TEXT_DARK)
    fig.text(0.5, 0.885, subtitle, ha="center", va="top",
             fontsize=15, color=COLOR_TEXT_GREY,
             linespacing=1.25)
    # If meta_y not provided, use default. Multi-line subtitles need lower meta.
    if meta_y is None:
        meta_y = 0.815 if "\n" in subtitle else 0.842
    fig.text(0.5, meta_y, meta, ha="center", va="top",
             fontsize=11, color=COLOR_TEXT_LIGHT, style="italic")


# =============================================================================
# SLIDE 1 — Heatmap deployment (wide)
# =============================================================================

fig1 = plt.figure(figsize=(16, 9), dpi=100, facecolor="white")

add_header(
    fig1,
    title="Brazil's container market looks competitive — until you look port by port.",
    subtitle=(
        "In every port analysed, one identified carrier accounts for at least "
        "one quarter of container vessel calls.\n"
        "Shares based on calls, not TEU capacity."
    ),
    meta="Container carrier deployment (% of calls) by port — 2025",
)

# Heatmap area — bottom lifted to 0.22 to fit 3-line footer (no info dropped).
ax1 = fig1.add_axes([0.14, 0.22, 0.76, 0.55])
max_val = max(35, matrix_pct.values.max())
im = ax1.imshow(matrix_pct.values, cmap=cmap_heat, aspect="auto", vmin=0, vmax=max_val)

ax1.set_xticks(range(len(PORT_ORDER)))
ax1.set_xticklabels(PORT_ORDER, rotation=25, ha="right", fontsize=10.5, color=COLOR_TEXT_DARK)
# Carrier ytick labels — bold. Subtitles for MSC and UNKNOWN added below.
ax1.set_yticks(range(len(CARRIERS_ORDER)))
ax1.set_yticklabels(CARRIERS_ORDER, fontsize=10.5, color=COLOR_TEXT_DARK,
                    fontweight="bold")
ax1.tick_params(axis="both", length=0)

# Subtitles under MSC / UNKNOWN removed per Hugo's spec.
# The alliance context is carried by the right-side alliance labels only.

# Cell annotations — "%" suffix; empty cells display "—" per Hugo's spec
for i in range(len(CARRIERS_ORDER)):
    for j in range(len(PORT_ORDER)):
        v = matrix_pct.values[i, j]
        if v < 0.5:
            ax1.text(j, i, "—", ha="center", va="center",
                     fontsize=10, color="#BBBBBB")
            continue
        color = "white" if v > max_val * 0.55 else COLOR_TEXT_DARK
        ax1.text(j, i, f"{v:.0f}%", ha="center", va="center",
                 fontsize=9, color=color)

# Alliance group separators kept for visual scanning
for b in GROUP_BOUNDARIES[:-1]:
    ax1.axhline(b, color=COLOR_TEXT_DARK, lw=1.0, alpha=0.55)

# Right-side alliance labels — same styling as left-side carrier labels
# (bold, dark), per Hugo's spec.
for pos_center, label in GROUP_LABELS:
    ax1.text(len(PORT_ORDER) - 0.35, pos_center, label,
             fontsize=10.5, color=COLOR_TEXT_DARK, va="center", ha="left",
             fontweight="bold")
# Column header for the alliance column
ax1.text(len(PORT_ORDER) - 0.35, -0.85, "Alliance / group",
         fontsize=10, color=COLOR_TEXT_GREY, va="bottom", ha="left",
         fontweight="bold", clip_on=False)
ax1.set_xlim(-0.5, len(PORT_ORDER) - 0.5 + 1.4)

for spine in ax1.spines.values():
    spine.set_visible(False)

# New footer wording per Hugo's spec — condensed to 2 lines:
#   Line A: source + methodology one-liner (as approved by Hugo)
#   Line B: github URL right-aligned
add_footer_slide1(fig1)

plt.savefig(OUT_DIR / "post9_slide1_deployment.png",
            dpi=120, facecolor="white")
print(f"Saved: {OUT_DIR / 'post9_slide1_deployment.png'}")
plt.close(fig1)


# =============================================================================
# SLIDE 2 — HHI + Alliance side-by-side
# =============================================================================

fig2 = plt.figure(figsize=(16, 9), dpi=100, facecolor="white")

n_high = (hhi_per_port >= 2500).sum()
n_moderate = ((hhi_per_port >= 1500) & (hhi_per_port < 2500)).sum()
n_total = len(hhi_per_port)

add_header(
    fig2,
    title="Carrier concentration limits port-level optionality in Brazil.",
    subtitle=(
        f"Using common HHI bands, {n_high} of {n_total} ports appear highly concentrated; "
        f"the others are moderately concentrated.\n"
        f"Based on vessel calls, not TEU capacity."
    ),
    meta="HHI (left) and alliance share (right) by port · Feb 2025 alliance config · 2025",
)

# Left panel: HHI ranking. Bottom = 0.28 to fit legend + 3-line footer.
ax2a = fig2.add_axes([0.06, 0.28, 0.38, 0.46])

hhi_sorted = hhi_per_port.sort_values(ascending=False)
colors_hhi = [COLOR_HIGH if v >= 2500 else COLOR_MODERATE for v in hhi_sorted.values]

y_pos = np.arange(len(hhi_sorted))
ax2a.barh(y_pos, hhi_sorted.values, color=colors_hhi,
          edgecolor="white", linewidth=0.4, height=0.68)
ax2a.set_yticks(y_pos)
ax2a.set_yticklabels(hhi_sorted.index, fontsize=10.5, color=COLOR_TEXT_DARK)
ax2a.tick_params(axis="y", length=0)
ax2a.invert_yaxis()

# Inline optionality labels — number of carriers with >5% share
# (excluding UNKNOWN). This shows procurement optionality without naming
# any single carrier — the message is concentration, not who leads.
def n_carriers_above_threshold(port_col, threshold=5.0):
    port_data = matrix_pct[port_col].drop("UNKNOWN", errors="ignore")
    return int((port_data > threshold).sum())

for i, port in enumerate(hhi_sorted.index):
    n_opt = n_carriers_above_threshold(port, threshold=5.0)
    label = f"{n_opt} carrier >5%" if n_opt == 1 else f"{n_opt} carriers >5%"
    ax2a.text(80, i, label, va="center", ha="left",
              fontsize=9.5, color="white", fontweight="bold")

# HHI values on the right of each bar
for i, v in enumerate(hhi_sorted.values):
    ax2a.text(v + 60, i, f"{v:,.0f}".replace(",", "."),
              va="center", ha="left",
              fontsize=10.5, color=COLOR_TEXT_DARK, fontweight="bold")

# Threshold lines — labels moved BELOW the bars area, centred at the axis
xmax = hhi_sorted.max() * 1.20
ax2a.axvline(1500, ls="--", color=COLOR_TEXT_LIGHT, lw=0.7, alpha=0.6)
ax2a.axvline(2500, ls="--", color=COLOR_TEXT_LIGHT, lw=0.7, alpha=0.6)
ax2a.text(1500, len(hhi_sorted) - 0.3, "1,500\nmoderate", ha="center", va="top",
          fontsize=8, color=COLOR_TEXT_GREY,
          bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                    edgecolor="none", alpha=0.85))
ax2a.text(2500, len(hhi_sorted) - 0.3, "2,500\nhigh", ha="center", va="top",
          fontsize=8, color=COLOR_TEXT_GREY,
          bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                    edgecolor="none", alpha=0.85))

ax2a.set_xlim(0, xmax)
ax2a.set_xlabel("Herfindahl-Hirschman Index (HHI)", fontsize=10,
                color=COLOR_TEXT_DARK, labelpad=6)
ax2a.tick_params(axis="x", labelsize=8.5, color=COLOR_TEXT_GREY, labelcolor=COLOR_TEXT_GREY)

for spine_name, spine in ax2a.spines.items():
    if spine_name == "bottom":
        spine.set_color(COLOR_TEXT_GREY)
        spine.set_linewidth(0.5)
    else:
        spine.set_visible(False)
ax2a.grid(False)
# Title above the axis area — centred with the left panel
fig2.text(0.25, 0.755, "Carrier concentration by port (HHI)",  # panel title y-axis level
          fontsize=13, fontweight="bold", color=COLOR_TEXT_DARK,
          ha="center")

# Right panel: Alliance stacked share
ax2b = fig2.add_axes([0.53, 0.28, 0.43, 0.46])

bottom = np.zeros(len(PORT_ORDER))
port_alli_order = list(PORT_ORDER)
for alli in ALLIANCE_ORDER:
    vals = alliance_pct.loc[alli, port_alli_order].values
    ax2b.barh(range(len(port_alli_order)), vals, left=bottom, label=alli,
              color=ALLIANCE_COLORS[alli], edgecolor="white", linewidth=0.4, height=0.68)
    bottom += vals

ax2b.set_yticks(range(len(port_alli_order)))
ax2b.set_yticklabels(port_alli_order, fontsize=10.5, color=COLOR_TEXT_DARK)
ax2b.tick_params(axis="y", length=0)
ax2b.invert_yaxis()
ax2b.set_xlim(0, 100)
ax2b.set_xlabel("% of container calls", fontsize=10, color=COLOR_TEXT_DARK, labelpad=6)
ax2b.tick_params(axis="x", labelsize=8.5, color=COLOR_TEXT_GREY, labelcolor=COLOR_TEXT_GREY)

for spine_name, spine in ax2b.spines.items():
    if spine_name == "bottom":
        spine.set_color(COLOR_TEXT_GREY)
        spine.set_linewidth(0.5)
    else:
        spine.set_visible(False)
ax2b.grid(False)
# Title above the axis area — centred with the right panel
fig2.text(0.745, 0.755, "Alliance share by port (Feb 2025 config)",
          fontsize=13, fontweight="bold", color=COLOR_TEXT_DARK,
          ha="center")

# Legend centred under the Alliance panel — above the 3-line footer
fig2.legend(*ax2b.get_legend_handles_labels(),
            loc="lower center", bbox_to_anchor=(0.745, 0.17),
            fontsize=9, ncol=4, frameon=False)

# Slide 2 footer — same identity as Slide 1: 1 line centred + github URL right
add_footer_slide2(fig2)

plt.savefig(OUT_DIR / "post9_slide2_concentration.png",
            dpi=120, facecolor="white")
print(f"Saved: {OUT_DIR / 'post9_slide2_concentration.png'}")
plt.close(fig2)

print("\nBoth slides: 16:9 landscape · Post-8 styling · ready for LinkedIn carousel")
