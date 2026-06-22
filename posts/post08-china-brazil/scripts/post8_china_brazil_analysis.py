"""
Post 8 — Brazil-China container trade asymmetry analysis
ANTAQ + ComexStat 2025 data
Author: Hugo Pedro
"""

# =============================================================================
# BLOCK 1 — Load and inspect data
# Goal: validate that the 3 ComexStat CSVs loaded correctly before any analysis
# =============================================================================

import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).resolve().parent.parent / "Data" / "china_brazil"
OUT_DIR = Path(__file__).resolve().parent.parent / "Outputs" / "post8"

# CSV parameters (ComexStat standard)
CSV_KW = dict(sep=";", encoding="utf-8-sig", thousands=None)

# Numeric columns by query (will be coerced to numeric, errors → NaN)
NUMERIC_COLS = ["fob_usd", "freight_usd", "insurance_usd", "cif_usd", "kg"]


def coerce_numeric(df):
    """Force all known numeric columns to numeric. Non-parsable → NaN → 0."""
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
    return df

# --- Load Query 1: Brazil → China exports, by HS2 chapter
br_to_cn_chap = pd.read_csv(DATA_DIR / "br_to_china_2025_chapters.csv", **CSV_KW)
br_to_cn_chap = br_to_cn_chap.rename(columns={
    "Países": "country",
    "Via": "via",
    "Código SH2": "hs2_code",
    "Descrição SH2": "hs2_desc",
    "2025 - Valor US$ FOB": "fob_usd",
    "2025 - Quilograma Líquido": "kg",
})
br_to_cn_chap = coerce_numeric(br_to_cn_chap)

# --- Load Query 2: China → Brazil imports, by HS2 chapter
cn_to_br_chap = pd.read_csv(DATA_DIR / "china_to_br_2025_chapters.csv", **CSV_KW)
cn_to_br_chap = cn_to_br_chap.rename(columns={
    "Países": "country",
    "Via": "via",
    "Código SH2": "hs2_code",
    "Descrição SH2": "hs2_desc",
    "2025 - Valor US$ FOB": "fob_usd",
    "2025 - US$ Frete": "freight_usd",
    "2025 - US$ Seguro": "insurance_usd",
    "2025 - Valor US$ CIF": "cif_usd",
    "2025 - Quilograma Líquido": "kg",
})
cn_to_br_chap = coerce_numeric(cn_to_br_chap)

# --- Load Query 3: China → Brazil imports, by URF (port of customs)
cn_to_br_ports = pd.read_csv(DATA_DIR / "china_to_br_2025_ports.csv", **CSV_KW)
cn_to_br_ports = cn_to_br_ports.rename(columns={
    "Países": "country",
    "Via": "via",
    "URF": "urf",
    "2025 - Valor US$ FOB": "fob_usd",
    "2025 - US$ Frete": "freight_usd",
    "2025 - US$ Seguro": "insurance_usd",
    "2025 - Valor US$ CIF": "cif_usd",
    "2025 - Quilograma Líquido": "kg",
})
cn_to_br_ports = coerce_numeric(cn_to_br_ports)

# --- Inspection
print("=" * 70)
print("BLOCK 1 — Data load validation")
print("=" * 70)

for name, df in [
    ("BR → CN exports (by HS2)", br_to_cn_chap),
    ("CN → BR imports (by HS2)", cn_to_br_chap),
    ("CN → BR imports (by URF)", cn_to_br_ports),
]:
    print(f"\n--- {name} ---")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    print(f"Total FOB (US$):  {df['fob_usd'].sum():>20,.0f}")
    print(f"Total KG:         {df['kg'].sum():>20,.0f}")
    print(f"Total tonnes:     {df['kg'].sum()/1000:>20,.0f}")

# --- Top 3 chapters by FOB in each direction (sanity check)
print("\n" + "=" * 70)
print("Top 3 HS2 chapters by FOB — sanity check")
print("=" * 70)

print("\nBR → CN exports (expect Chap 02 Carnes, 12 Soja, 26 Minérios dominant):")
print(br_to_cn_chap.nlargest(3, "fob_usd")[["hs2_code", "hs2_desc", "fob_usd"]].to_string(index=False))

print("\nCN → BR imports (expect Chap 84/85/87 — máquinas/elétrica/veículos):")
print(cn_to_br_chap.nlargest(3, "fob_usd")[["hs2_code", "hs2_desc", "fob_usd"]].to_string(index=False))

# --- Top 5 URFs by FOB (sanity check + flag outliers)
print("\n--- Top 5 URFs by FOB (CN → BR imports):")
print(cn_to_br_ports.nlargest(5, "fob_usd")[["urf", "fob_usd", "kg"]].to_string(index=False))

print("\n" + "=" * 70)
print("Block 1 done. If shapes + totals look reasonable, proceed to Block 2.")
print("=" * 70)


# =============================================================================
# BLOCK 2 — URF cleaning (drop airports + interior customs units)
# Goal: keep only legitimate maritime/river ports for port concentration analysis
# =============================================================================

print("\n\n" + "=" * 70)
print("BLOCK 2 — URF cleaning")
print("=" * 70)

# Blacklist: URFs that are NOT maritime ports (airports, interior cities,
# inland customs offices where cargo arrives under bond).
# Identified manually from the full URF list inspection.
URF_BLACKLIST_SUBSTRINGS = [
    "AEROPORTO",          # airport — even if filtered Via=MARITIMA
    "VIRACOPOS",
    "SAO PAULO",          # city, customs interior (Santos handles SP cargo)
    "SOROCABA",
    "ANAPOLIS",
    "BELO HORIZONTE",
    "JUIZ DE FORA",
    "CAXIAS DO SUL",
    "VOLTA REDONDA",
    "NOVO HAMBURGO",
    "VARGINHA",
    "NOVA IGUACU",
    "CURITIBA",           # Paranaguá handles Curitiba area cargo
    "CAMPOS DOS GOYTACAZES",
]


def is_blacklisted(urf_name):
    """Return True if URF name contains any blacklisted substring."""
    upper = urf_name.upper()
    return any(bad in upper for bad in URF_BLACKLIST_SUBSTRINGS)


# Apply filter
cn_to_br_ports["is_port"] = ~cn_to_br_ports["urf"].apply(is_blacklisted)
ports_clean = cn_to_br_ports[cn_to_br_ports["is_port"]].copy()
ports_dropped = cn_to_br_ports[~cn_to_br_ports["is_port"]].copy()

# Diagnostic
print(f"\nOriginal URFs:           {len(cn_to_br_ports)}")
print(f"Maritime ports kept:     {len(ports_clean)}")
print(f"URFs dropped:            {len(ports_dropped)}")
print(f"FOB original (US$):      {cn_to_br_ports['fob_usd'].sum():>20,.0f}")
print(f"FOB kept (US$):          {ports_clean['fob_usd'].sum():>20,.0f}")
print(f"FOB dropped (US$):       {ports_dropped['fob_usd'].sum():>20,.0f}")
share_dropped = ports_dropped["fob_usd"].sum() / cn_to_br_ports["fob_usd"].sum() * 100
print(f"% FOB dropped:           {share_dropped:>20.3f}%")

print("\n--- URFs dropped (for transparency):")
print(ports_dropped[["urf", "fob_usd"]].to_string(index=False))

# Recompute share % on the cleaned set
ports_clean["fob_share_pct"] = (ports_clean["fob_usd"] / ports_clean["fob_usd"].sum() * 100).round(2)
ports_clean = ports_clean.sort_values("fob_usd", ascending=False).reset_index(drop=True)

print("\n--- Top 10 clean ports (CN → BR imports 2025):")
print(ports_clean.head(10)[["urf", "fob_usd", "kg", "fob_share_pct"]].to_string(index=False))

print(f"\nTop 5 clean share: {ports_clean.head(5)['fob_share_pct'].sum():.1f}%")
print(f"Top 10 clean share: {ports_clean.head(10)['fob_share_pct'].sum():.1f}%")

# Save cleaned data for audit
ports_clean.drop(columns=["is_port"]).to_csv(
    OUT_DIR / "cn_to_br_ports_clean.csv", sep=";", index=False, encoding="utf-8-sig"
)
print(f"\n✓ Saved: {OUT_DIR / 'cn_to_br_ports_clean.csv'}")

print("\n" + "=" * 70)
print("Block 2 done. URFs cleaned. Proceed to Block 3 (HS classification).")
print("=" * 70)


# =============================================================================
# BLOCK 3 — HS2 classification into raw / semi-processed / finished
# Goal: quantify the directional asymmetry of value-chain stage by cargo type
# =============================================================================

print("\n\n" + "=" * 70)
print("BLOCK 3 — HS classification + directional asymmetry")
print("=" * 70)


def classify_hs2(code):
    """Classify HS2 chapter into structural category.

    Methodology: simplified 3-bucket mapping based on Harmonized System
    chapter structure. Trade-offs declared in Docs/post8_china_brazil/methodology.md
    """
    code = int(code)

    # Special override: HS 17 (sugar) treated as commodity even if semi-refined
    # (Brazilian sugar exports are largely VHP raw for refining in destination)
    if code == 17:
        return "raw"

    # RAW: extracted/grown commodities with minimal processing
    if code in range(1, 16):              # 01-15: animals, meat, fish, dairy, eggs, vegetables, fruits, grains, oilseeds, oils
        return "raw"
    if code in (25, 26, 27):              # 25 salt/sulphur, 26 minérios, 27 fuels
        return "raw"
    if code in (31, 41, 44, 47):          # 31 fertilizers, 41 raw hides, 44 raw wood, 47 pulp
        return "raw"

    # SEMI-PROCESSED: intermediate goods
    if code in range(16, 25):             # 16-24: prepared foods, beverages, tobacco
        return "semi"
    if code in range(28, 41):             # 28-40: chemicals, pharma, plastics primary, rubber
        return "semi"
    if code in range(45, 50):             # 45-49: cork, basket, paper
        return "semi"
    if code in range(50, 54):             # 50-53: textile fibers raw (silk, wool, cotton, vegetable fibers)
        return "semi"
    if code in (72, 74, 75, 76, 78, 79, 80, 81):  # base metals
        return "semi"

    # FINISHED: manufactured products
    if code in (42, 43):                  # leather goods, fur articles
        return "finished"
    if code in range(54, 72):             # 54-71: textiles finished, clothing, footwear, stone, ceramic, glass, jewelry
        return "finished"
    if code == 73:                        # iron/steel articles
        return "finished"
    if code in range(82, 98):             # 82-97: tools, machinery, electronics, vehicles, instruments, toys, art
        return "finished"

    # OTHER: special operations (chapters 98, 99) — exclude from main analysis
    return "other"


# Apply classification to both directions
br_to_cn_chap["category"] = br_to_cn_chap["hs2_code"].apply(classify_hs2)
cn_to_br_chap["category"] = cn_to_br_chap["hs2_code"].apply(classify_hs2)

# Aggregate by category
def aggregate_by_category(df, direction_label):
    """Return totals + % shares + US$/tonne by category."""
    grouped = df.groupby("category", as_index=False).agg(
        fob_usd=("fob_usd", "sum"),
        kg=("kg", "sum"),
        n_chapters=("hs2_code", "count"),
    )
    grouped["fob_share_pct"] = (grouped["fob_usd"] / grouped["fob_usd"].sum() * 100).round(2)
    grouped["kg_share_pct"] = (grouped["kg"] / grouped["kg"].sum() * 100).round(2)
    # US$/tonne — guard against zero division
    grouped["usd_per_tonne"] = (grouped["fob_usd"] / (grouped["kg"] / 1000)).where(grouped["kg"] > 0, 0).round(0)
    grouped["direction"] = direction_label
    return grouped


exports_by_cat = aggregate_by_category(br_to_cn_chap, "BR→CN exports")
imports_by_cat = aggregate_by_category(cn_to_br_chap, "CN→BR imports")

# Reorder categories for display
CATEGORY_ORDER = ["raw", "semi", "finished", "other"]


def reorder(df):
    df["_sort"] = df["category"].apply(lambda c: CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else 99)
    return df.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)


exports_by_cat = reorder(exports_by_cat)
imports_by_cat = reorder(imports_by_cat)

print("\n--- EXPORTS Brasil → China by structural category:")
print(exports_by_cat[["category", "n_chapters", "fob_usd", "fob_share_pct", "kg", "kg_share_pct", "usd_per_tonne"]].to_string(index=False))

print("\n--- IMPORTS China → Brasil by structural category:")
print(imports_by_cat[["category", "n_chapters", "fob_usd", "fob_share_pct", "kg", "kg_share_pct", "usd_per_tonne"]].to_string(index=False))

# Build the killer comparison table
print("\n" + "=" * 70)
print("THE KILLER COMPARISON — directional asymmetry by category")
print("=" * 70)

comp_fob = pd.DataFrame({
    "BR→CN exports % of FOB": exports_by_cat.set_index("category")["fob_share_pct"],
    "CN→BR imports % of FOB": imports_by_cat.set_index("category")["fob_share_pct"],
}).reindex(CATEGORY_ORDER)
print("\n--- Share of FOB by category (%):")
print(comp_fob.to_string())

comp_kg = pd.DataFrame({
    "BR→CN exports % of KG": exports_by_cat.set_index("category")["kg_share_pct"],
    "CN→BR imports % of KG": imports_by_cat.set_index("category")["kg_share_pct"],
}).reindex(CATEGORY_ORDER)
print("\n--- Share of weight (KG) by category (%):")
print(comp_kg.to_string())

comp_usd = pd.DataFrame({
    "BR→CN US$/tonne": exports_by_cat.set_index("category")["usd_per_tonne"],
    "CN→BR US$/tonne": imports_by_cat.set_index("category")["usd_per_tonne"],
}).reindex(CATEGORY_ORDER)
print("\n--- US$ per tonne by category (the value gradient):")
print(comp_usd.to_string())

# Save outputs
exports_by_cat.to_csv(OUT_DIR / "br_to_cn_by_category.csv", sep=";", index=False, encoding="utf-8-sig")
imports_by_cat.to_csv(OUT_DIR / "cn_to_br_by_category.csv", sep=";", index=False, encoding="utf-8-sig")
print(f"\n✓ Saved: {OUT_DIR}/br_to_cn_by_category.csv")
print(f"✓ Saved: {OUT_DIR}/cn_to_br_by_category.csv")

print("\n" + "=" * 70)
print("Block 3 done. Asymmetry quantified. Proceed to Block 4 (HHI + chart prep).")
print("=" * 70)


# =============================================================================
# BLOCK 4 — Port concentration HHI + chart data prep
# Goal: quantify how concentrated Chinese imports are in Brazilian ports,
# and prepare top-10 + "Others" structure for the chart
# =============================================================================

print("\n\n" + "=" * 70)
print("BLOCK 4 — Port concentration (HHI) + chart data prep")
print("=" * 70)

# --- HHI calculation
# HHI = Σ(market_share_in_percent)²
# DOJ/FTC 2010 thresholds:
#   < 1,500  : unconcentrated
#   1,500-2,500 : moderately concentrated
#   > 2,500  : highly concentrated

ports_for_hhi = ports_clean.copy()
ports_for_hhi["share_pct"] = ports_for_hhi["fob_usd"] / ports_for_hhi["fob_usd"].sum() * 100
ports_for_hhi["share_pct_squared"] = ports_for_hhi["share_pct"] ** 2

HHI = ports_for_hhi["share_pct_squared"].sum()

def hhi_classification(hhi):
    if hhi < 1500:
        return "Unconcentrated"
    elif hhi < 2500:
        return "Moderately concentrated"
    else:
        return "Highly concentrated"

# --- Concentration metrics
ports_for_hhi = ports_for_hhi.sort_values("fob_usd", ascending=False).reset_index(drop=True)
top1_share = ports_for_hhi.head(1)["share_pct"].sum()
top3_share = ports_for_hhi.head(3)["share_pct"].sum()
top5_share = ports_for_hhi.head(5)["share_pct"].sum()
top10_share = ports_for_hhi.head(10)["share_pct"].sum()

print(f"\n--- HHI metrics for CN → BR imports by Brazilian port (2025):")
print(f"  Number of ports (cleaned): {len(ports_for_hhi)}")
print(f"  HHI:                       {HHI:>8,.0f}")
print(f"  DOJ/FTC 2010 class:        {hhi_classification(HHI)}")
print(f"")
print(f"  Top-1 share (Santos):      {top1_share:>6.2f}%")
print(f"  Top-3 share:               {top3_share:>6.2f}%")
print(f"  Top-5 share:               {top5_share:>6.2f}%")
print(f"  Top-10 share:              {top10_share:>6.2f}%")

# --- Build chart data structure: top 10 explicit + "Others" aggregated
top10 = ports_for_hhi.head(10).copy()
others = ports_for_hhi.iloc[10:].copy()

others_row = pd.DataFrame([{
    "urf": f"Others ({len(others)} ports)",
    "fob_usd": others["fob_usd"].sum(),
    "kg": others["kg"].sum(),
    "share_pct": others["share_pct"].sum(),
}])

# Clean port names for chart display (remove URF code prefix)
def clean_port_name(urf):
    """Remove '0000000 - ' prefix and standardize ALF/IRF/PORTO DE prefixes."""
    parts = urf.split(" - ", 1)
    name = parts[1] if len(parts) > 1 else urf
    # Strip common prefixes for cleaner display
    for prefix in ["PORTO DE ", "PORTO DO ", "ALF - ", "IRF - ", "IRF "]:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    # Apply title-case
    name = name.title()
    # Manual overrides for Brazilian port spellings
    overrides = {
        "Sao Francisco Do Sul": "São Francisco do Sul",
        "Rio De Janeiro": "Rio de Janeiro",
        "Sao Luis": "São Luís",
        "Itajai": "Itajaí",
        "Paranagua": "Paranaguá",
        "Vitoria": "Vitória",
        "Pecem": "Pecém",
        "Belem": "Belém",
        "Sao Paulo": "São Paulo",
        "Itaguai": "Itaguaí",
        "Campos Dos Goytacazes": "Campos dos Goytacazes",
    }
    return overrides.get(name, name)

top10["port_display"] = top10["urf"].apply(clean_port_name)
chart_data = pd.concat([
    top10[["port_display", "fob_usd", "kg", "share_pct"]],
    others_row.rename(columns={"urf": "port_display"})
], ignore_index=True)

print("\n--- Chart data (top 10 + Others):")
print(chart_data[["port_display", "fob_usd", "share_pct"]].to_string(index=False))

# Save outputs for chart + audit
chart_data.to_csv(OUT_DIR / "port_concentration_chart_data.csv", sep=";", index=False, encoding="utf-8-sig")
ports_for_hhi[["urf", "fob_usd", "kg", "share_pct", "share_pct_squared"]].to_csv(
    OUT_DIR / "port_concentration_full.csv", sep=";", index=False, encoding="utf-8-sig"
)

# Save summary metrics
summary = pd.DataFrame([{
    "metric": "HHI",
    "value": round(HHI, 1),
    "classification": hhi_classification(HHI),
}, {
    "metric": "top1_share_pct",
    "value": round(top1_share, 2),
    "classification": "Santos",
}, {
    "metric": "top3_share_pct",
    "value": round(top3_share, 2),
    "classification": "",
}, {
    "metric": "top5_share_pct",
    "value": round(top5_share, 2),
    "classification": "",
}, {
    "metric": "top10_share_pct",
    "value": round(top10_share, 2),
    "classification": "",
}, {
    "metric": "n_ports_clean",
    "value": len(ports_for_hhi),
    "classification": "",
}])
summary.to_csv(OUT_DIR / "summary_metrics.csv", sep=";", index=False, encoding="utf-8-sig")

print(f"\n✓ Saved chart data: {OUT_DIR}/port_concentration_chart_data.csv")
print(f"✓ Saved full port list: {OUT_DIR}/port_concentration_full.csv")
print(f"✓ Saved summary metrics: {OUT_DIR}/summary_metrics.csv")

print("\n" + "=" * 70)
print("Block 4 done. Port concentration measured. Proceed to Block 5 (chart).")
print("=" * 70)


# =============================================================================
# BLOCK 4B — Export port concentration (Brazil → China)
# Same methodology as Block 2+4 but applied to br_to_china_2025_ports.csv
# =============================================================================

print("\n\n" + "=" * 70)
print("BLOCK 4B — Export ports concentration (Brazil → China)")
print("=" * 70)

# Load exports by URF
br_to_cn_ports = pd.read_csv(DATA_DIR / "br_to_china_2025_ports.csv", **CSV_KW)
br_to_cn_ports = br_to_cn_ports.rename(columns={
    "Países": "country",
    "Via": "via",
    "URF": "urf",
    "2025 - Valor US$ FOB": "fob_usd",
    "2025 - Quilograma Líquido": "kg",
})
br_to_cn_ports = coerce_numeric(br_to_cn_ports)

# Apply same URF blacklist (interior/airports) — note Campos dos Goytacazes is
# treated differently here: it's a coastal customs unit for the Bacia de Campos
# offshore oil exports, so KEEP it (legitimate maritime origin for export).
EXPORT_BLACKLIST = [b for b in URF_BLACKLIST_SUBSTRINGS if "CAMPOS DOS GOYTACAZES" not in b]


def is_blacklisted_exp(urf_name):
    upper = urf_name.upper()
    return any(bad in upper for bad in EXPORT_BLACKLIST)


br_to_cn_ports["is_port"] = ~br_to_cn_ports["urf"].apply(is_blacklisted_exp)
exp_ports_clean = br_to_cn_ports[br_to_cn_ports["is_port"]].copy()
exp_ports_dropped = br_to_cn_ports[~br_to_cn_ports["is_port"]].copy()

print(f"\nOriginal URFs:           {len(br_to_cn_ports)}")
print(f"Maritime ports kept:     {len(exp_ports_clean)}")
print(f"URFs dropped:            {len(exp_ports_dropped)}")
if len(exp_ports_dropped) > 0:
    print("\n--- URFs dropped:")
    print(exp_ports_dropped[["urf", "fob_usd"]].to_string(index=False))

exp_ports_clean["share_pct"] = exp_ports_clean["fob_usd"] / exp_ports_clean["fob_usd"].sum() * 100
exp_ports_clean["share_pct_squared"] = exp_ports_clean["share_pct"] ** 2
HHI_EXP = exp_ports_clean["share_pct_squared"].sum()

exp_ports_clean = exp_ports_clean.sort_values("fob_usd", ascending=False).reset_index(drop=True)
exp_top1 = exp_ports_clean.head(1)["share_pct"].sum()
exp_top3 = exp_ports_clean.head(3)["share_pct"].sum()
exp_top5 = exp_ports_clean.head(5)["share_pct"].sum()
exp_top10 = exp_ports_clean.head(10)["share_pct"].sum()

print(f"\n--- Export ports HHI metrics:")
print(f"  Number of ports (cleaned): {len(exp_ports_clean)}")
print(f"  HHI:                       {HHI_EXP:>8,.0f}")
print(f"  Class:                     {hhi_classification(HHI_EXP)}")
print(f"  Top-1 share:               {exp_top1:>6.2f}%")
print(f"  Top-3 share:               {exp_top3:>6.2f}%")
print(f"  Top-5 share:               {exp_top5:>6.2f}%")
print(f"  Top-10 share:              {exp_top10:>6.2f}%")

# Chart data for exports: ONLY top 10 (no "Others" per Hugo's request)
exp_top10_df = exp_ports_clean.head(10).copy()
exp_top10_df["port_display"] = exp_top10_df["urf"].apply(clean_port_name)
exp_top10_df[["port_display", "fob_usd", "kg", "share_pct"]].to_csv(
    OUT_DIR / "br_to_cn_ports_top10.csv", sep=";", index=False, encoding="utf-8-sig"
)

print("\n--- Top 10 export ports (chart data):")
print(exp_top10_df[["port_display", "fob_usd", "share_pct"]].to_string(index=False))

# Re-export imports chart data as top-10 only (no "Others") per Hugo's request
imp_top10_df = ports_for_hhi.head(10).copy()
imp_top10_df["port_display"] = imp_top10_df["urf"].apply(clean_port_name)
imp_top10_df[["port_display", "fob_usd", "kg", "share_pct"]].to_csv(
    OUT_DIR / "cn_to_br_ports_top10.csv", sep=";", index=False, encoding="utf-8-sig"
)

# Update summary metrics file with export HHI
summary_rows = [
    {"metric": "HHI_imports", "value": round(HHI, 1), "classification": hhi_classification(HHI)},
    {"metric": "HHI_exports", "value": round(HHI_EXP, 1), "classification": hhi_classification(HHI_EXP)},
    {"metric": "imports_top1_pct", "value": round(top1_share, 2), "classification": "Santos"},
    {"metric": "imports_top5_pct", "value": round(top5_share, 2), "classification": ""},
    {"metric": "imports_top10_pct", "value": round(top10_share, 2), "classification": ""},
    {"metric": "exports_top1_pct", "value": round(exp_top1, 2), "classification": "Santos"},
    {"metric": "exports_top5_pct", "value": round(exp_top5, 2), "classification": ""},
    {"metric": "exports_top10_pct", "value": round(exp_top10, 2), "classification": ""},
]
pd.DataFrame(summary_rows).to_csv(OUT_DIR / "summary_metrics.csv", sep=";", index=False, encoding="utf-8-sig")
print(f"\n✓ Saved: {OUT_DIR}/br_to_cn_ports_top10.csv")
print(f"✓ Saved: {OUT_DIR}/cn_to_br_ports_top10.csv")
print(f"✓ Updated: {OUT_DIR}/summary_metrics.csv")

print("\n" + "=" * 70)
print("Block 4B done. Both directions analysed. Proceed to chart rebuild.")
print("=" * 70)
