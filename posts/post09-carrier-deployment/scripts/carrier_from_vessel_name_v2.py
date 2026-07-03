"""
Post 9 — Carrier identification v2 (uses scraped VesselFinder names).

CHANGES vs v1:
  1. Uses vessel_names.csv (VesselFinder scrape) as PRIMARY name source
  2. Filters by container-terminal whitelist (not top-10 cities)
  3. Regex patterns expanded — Hapag-Lloyd, PIL, regional feeders, ex-brands
  4. HHI computed BOTH with and without UNKNOWN (transparency)
  5. parent_group column for consolidated HHI (Maersk+HS+Sealand, CMA CGM+APL+Mercosul)
  6. Alliance layer (Feb 2025 config: Gemini, Premier, Ocean, MSC-solo)

OUTPUTS (Data/post9/):
  - carrier_by_call.csv          — every call with vessel_name, carrier, group, alliance
  - carrier_summary.csv          — carrier volumes + shares
  - carrier_port_matrix.csv      — carrier × port pivot
  - alliance_summary.csv         — alliance-level shares
  - group_summary.csv            — parent-group shares (Maersk = Maersk + HS + Sealand)
  - hhi_summary.csv              — HHI (raw), HHI (identified-only), by group, by alliance
  - unknown_vessels_audit.csv    — top-100 UNKNOWN vessels for manual review
"""

import re
import sys
from pathlib import Path
import pandas as pd

# =============================================================================
# Path resolution (Cowork vs Hugo PC)
# =============================================================================

_script_dir = Path(__file__).resolve().parent

# Try Cowork layout: Scripts/post9 → Data/post9 (sibling of Scripts)
cowork_root = _script_dir.parent.parent
if (cowork_root / "Data" / "antaq" / "atracacao_2025.csv").exists():
    DATA_DIR = cowork_root / "Data"
    POST9_DIR = DATA_DIR / "post9"
    ATRACACAO_CSV = DATA_DIR / "antaq" / "atracacao_2025.csv"
    VESSELS_MASTER_CSV = DATA_DIR / "antaq" / "vessels_master_enriched.csv"
    VESSEL_NAMES_CSV = POST9_DIR / "vessel_names.csv"
    IMOS_LOOKUP_CSV = POST9_DIR / "imos_to_lookup.csv"
# Hugo PC: scripts/ → data/ (sibling of scripts)
elif (_script_dir.parent / "data" / "imos_to_lookup.csv").exists():
    POST9_DIR = _script_dir.parent / "data"
    ATRACACAO_CSV = POST9_DIR / "atracacao_2025.csv"          # if copied over
    VESSELS_MASTER_CSV = POST9_DIR / "vessels_master_enriched.csv"
    VESSEL_NAMES_CSV = POST9_DIR / "vessel_names.csv"
    IMOS_LOOKUP_CSV = POST9_DIR / "imos_to_lookup.csv"
else:
    print("ERROR: could not locate data files. Check paths.")
    sys.exit(1)

POST9_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Carrier patterns (ordered — specific first)
# =============================================================================

# Format: (carrier, parent_group, alliance_feb2025, regex_pattern)
# Alliances (Feb 2025):
#   - Gemini Cooperation: Maersk + Hapag-Lloyd
#   - Ocean Alliance:     CMA CGM + Cosco + Evergreen + OOCL
#   - Premier Alliance:   ONE + HMM + Yang Ming
#   - MSC standalone (ex-2M partner, solo since Feb 2025)
#   - Others: ZIM, PIL, Wan Hai, KMTC, SITC, Hyundai (non-Premier), Sinotrans, regional

CARRIER_PATTERNS = [
    # (carrier, parent_group, alliance, regex)
    # Order: most specific patterns first

    # ---- CMA CGM group ----
    ("CMA CGM",       "CMA CGM Group", "Ocean Alliance", r"^\s*CMA[\s-]*CGM\b"),
    ("APL",           "CMA CGM Group", "Ocean Alliance", r"^\s*APL\b"),
    # Mercosul Line = CMA CGM group by ownership, but operates as an
    # intra-Brazil / intra-LatAm regional carrier, NOT as an Ocean Alliance
    # long-haul service. Classifying it under Ocean Alliance would inflate
    # that alliance's share and hide the "regional / affiliated" category.
    ("MERCOSUL",      "CMA CGM Group", "Regional / affiliated carrier", r"^\s*MERCOSUL\b"),
    ("ANL",           "CMA CGM Group", "Ocean Alliance", r"^\s*ANL\b"),

    # ---- Maersk group ----
    ("MAERSK",        "Maersk Group",  "Gemini Cooperation", r"^\s*MAERSK\b"),
    # Maersk charter fleet: "[Nome] MAERSK" (e.g. SAN RAPHAEL MAERSK, SAN MARCO MAERSK).
    # Industry convention (Alphaliner) counts charter tonnage under the commercial operator.
    ("MAERSK",        "Maersk Group",  "Gemini Cooperation", r"\bMAERSK\s*$"),
    ("HAMBURG SUD",   "Maersk Group",  "Gemini Cooperation",
        r"^\s*(HAMBURG\s+SUD|HAMBURG\s+SÜD|HAMB\.?\s*SUD|CAP\s+SAN\b|MONTE\s+[A-Z]+\b|POLAR\s+ECUADOR|CCNI\s+[A-Z]+)\b"),
    ("SEALAND",       "Maersk Group",  "Gemini Cooperation", r"^\s*SEALAND\b"),
    ("ALIANCA",       "Maersk Group",  "Gemini Cooperation", r"^\s*ALIAN(C|Ç)A\b"),

    # ---- Hapag-Lloyd (naming: [City/Region] Express, HH prefix) ----
    ("HAPAG-LLOYD",   "Hapag-Lloyd",   "Gemini Cooperation",
        r"^\s*(HAPAG[\s-]*LLOYD|HH\s+[A-Z]+\b)"),
    # Generic Hapag Express pattern: any word(s) + EXPRESS or EXP at end.
    # Excludes false positives via negative prefix lookahead for other carriers.
    # Real-world example missed by literal city list: ESPIRITO SANTO EXP (BR).
    ("HAPAG-LLOYD",   "Hapag-Lloyd",   "Gemini Cooperation",
        r"^\s*(?!MSC|MAERSK|CMA|COSCO|EVER|OOCL|ONE|HMM|YM|YANG|ZIM|WAN|APL|SEALAND|"
        r"KOTA|SITC|KMTC|HEUNG|SINOTRANS|HYUNDAI|MERCOSUL|ALIAN|HAMBURG|SAN\s|MONTE\s|"
        r"POLAR|CCNI|CAP\s|LOG[-\s]?IN)"
        r"[A-Z]+(\s+[A-Z]+){0,2}\s+(EXPRESS|EXP)\b"),

    # ---- MSC (standalone from Feb 2025) ----
    ("MSC",           "MSC",           "MSC (standalone)",
        r"^\s*(MSC|MEDITERRANEAN\s+SHIPPING)\b"),

    # ---- Cosco Shipping ----
    # Handles: COSCO XXX, COSCO SHIPPING XXX, COSCOSHIPPING XXX (concatenated), CSCL XXX.
    ("COSCO",         "Cosco Shipping","Ocean Alliance",
        r"^\s*(COSCO|CSCL)"),

    # ---- Evergreen ----
    # EVER + any second word (avoids listing every ship name)
    ("EVERGREEN",     "Evergreen",     "Ocean Alliance", r"^\s*EVER(\s+[A-Z]+|\b)"),

    # ---- OOCL ----
    ("OOCL",          "OOCL",          "Ocean Alliance", r"^\s*OOCL\b"),

    # ---- ONE (Ocean Network Express) ----
    ("ONE",           "ONE",           "Premier Alliance",
        r"^\s*ONE\s+(?!OFF\b)[A-Z]+"),

    # ---- HMM ----
    ("HMM",           "HMM",           "Premier Alliance", r"^\s*HMM\b"),

    # ---- Yang Ming ----
    ("YANG MING",     "Yang Ming",     "Premier Alliance", r"^\s*(YANG\s+MING|YM)\s+[A-Z]+"),

    # ---- ZIM (non-aligned since Premier config) ----
    ("ZIM",           "ZIM",           "Non-aligned", r"^\s*ZIM\b"),

    # ---- PIL (Pacific International Lines) — vessels are KOTA XYZ ----
    ("PIL",           "PIL",           "Non-aligned", r"^\s*KOTA\s+[A-Z]+"),

    # ---- Wan Hai Lines ----
    ("WAN HAI",       "Wan Hai",       "Non-aligned", r"^\s*WAN\s*HAI\b"),

    # ---- Hyundai (careful: HMM is ex-Hyundai Merchant Marine, now separate) ----
    # Vessels labeled "HYUNDAI" are typically old HMM ships not yet renamed
    ("HMM",           "HMM",           "Premier Alliance", r"^\s*HYUNDAI\b"),

    # ---- Regional / intra-Asia / feeders ----
    ("KMTC",          "KMTC",          "Non-aligned", r"^\s*KMTC\b"),
    ("SITC",          "SITC",          "Non-aligned", r"^\s*SITC\b"),
    ("SINOTRANS",     "Sinotrans",     "Non-aligned", r"^\s*SINOTRANS\b"),
    ("HEUNG-A",       "Heung-A",       "Non-aligned", r"^\s*HEUNG[-\s]*A\b"),

    # ---- Brazil-Argentina regional feeder ----
    # Log-In Logística Intermodal — cabotagem BR + short-sea LatAm.
    # Regional operator, not part of any global alliance.
    ("LOG-IN",        "Log-In",        "Regional / affiliated carrier", r"^\s*LOG[-\s]*IN\b"),
]


def match_carrier(vessel_name: str):
    """Return (carrier, parent_group, alliance) or ('UNKNOWN', 'UNKNOWN', 'Unknown')."""
    if not isinstance(vessel_name, str) or not vessel_name.strip():
        return "UNKNOWN", "UNKNOWN", "Unknown"
    name_upper = vessel_name.upper().strip()
    for carrier, group, alliance, pattern in CARRIER_PATTERNS:
        if re.search(pattern, name_upper):
            return carrier, group, alliance
    return "UNKNOWN", "UNKNOWN", "Unknown"


# =============================================================================
# Container-terminal whitelist (same as extract_imos_v2.py)
# =============================================================================

CONTAINER_TERMINALS = [
    ("Santos", "Cais da Santos Brasil (SSZ 16) - Privativo"),
    ("Santos", "Cais da BTP (SSZ 41) - Privativo"),
    ("Santos", "Cais da Ecoporto (SSZ 35) - Privativo"),
    ("Santos", "Cais do TEV (SSZ 18) - Privativo"),
    ("Paranaguá", "TCP"),
    ("Rio Grande", "Cais Tecon Rio Grande S.A."),
    ("Rio de Janeiro", "Multi-Rio"),
    ("Rio de Janeiro", "ICTSI"),
    ("Salvador", "TECON"),
    ("Salvador", "TECON Área 2"),
    ("São Francisco do Sul", "TESC"),
    ("Itajaí", "Cais Arrendado Transitoriamente"),
    ("Vitória", "Cais de Capuaba"),
    ("Portonave - Terminais Portuários de Navegantes",
     "Portonave - Terminais Portuários de Navegantes"),
    ("Super Terminais Comércio e Indústria",
     "Super Terminais Comércio e Indústria"),
    ("Terminal Portuário do Pecém",
     "Terminal Portuário do Pecém"),
]

# =============================================================================
# Load data
# =============================================================================

print("=" * 70)
print("Post 9 — Carrier identification v2")
print("=" * 70)

print("\n[1/7] Loading ANTAQ atracação 2025...")
atrac = pd.read_csv(ATRACACAO_CSV, sep=";", encoding="utf-8-sig", low_memory=False)
print(f"      Loaded {len(atrac):,} rows")

print("\n[2/7] Filtering to container terminals...")
atrac = atrac[atrac["Tipo de Navegação da Atracação"] == "Longo Curso"]
atrac["port_terminal"] = list(zip(atrac["Porto Atracação"], atrac["Terminal"]))
atrac = atrac[atrac["port_terminal"].isin(set(CONTAINER_TERMINALS))]
atrac["imo"] = pd.to_numeric(atrac["Nº do IMO"], errors="coerce")
atrac = atrac[atrac["imo"].notna()].copy()
atrac["imo"] = atrac["imo"].astype("int64")
print(f"      Container-terminal calls: {len(atrac):,}")
print(f"      Unique IMOs:              {atrac['imo'].nunique():,}")

# =============================================================================
# Build vessel_name lookup (VesselFinder scrape + vessels_master fallback)
# =============================================================================

print("\n[3/7] Building vessel name lookup...")

# Primary source: VesselFinder scrape
if VESSEL_NAMES_CSV.exists():
    vnames = pd.read_csv(VESSEL_NAMES_CSV, sep=";", encoding="utf-8-sig")
    vnames = vnames[vnames["status"] == "OK"][["imo", "vessel_name", "vessel_type"]].copy()
    vnames["imo"] = vnames["imo"].astype("int64")
    print(f"      VesselFinder scraped names (OK): {len(vnames):,}")
else:
    vnames = pd.DataFrame(columns=["imo", "vessel_name", "vessel_type"])
    print("      vessel_names.csv NOT FOUND — proceeding with vessels_master only")

# Fallback: vessels_master
if VESSELS_MASTER_CSV.exists():
    vm = pd.read_csv(VESSELS_MASTER_CSV, sep=",", encoding="utf-8-sig")
    vm = vm[["NÚMERO IMO", "NOME DO NAVIO", "SHIPPING LINE", "CAPACIDADE (TEU)", "vessel_segment"]].copy()
    vm.columns = ["imo", "vessel_name_master", "shipping_line_master", "teu_capacity", "vessel_segment"]
    vm["imo"] = pd.to_numeric(vm["imo"], errors="coerce")
    vm = vm[vm["imo"].notna()].copy()
    vm["imo"] = vm["imo"].astype("int64")
    print(f"      vessels_master rows:              {len(vm):,}")
else:
    vm = pd.DataFrame(columns=["imo", "vessel_name_master", "shipping_line_master",
                               "teu_capacity", "vessel_segment"])

# Consolidate: vessel_name preferred from scrape, fallback to master
names = vnames.merge(vm, on="imo", how="outer")
names["vessel_name_final"] = names["vessel_name"].fillna(names["vessel_name_master"])
names["vessel_type_final"] = names.get("vessel_type", pd.Series(dtype=object)).fillna("")

print(f"      Consolidated name entries:        {len(names):,}")
print(f"      IMOs with a resolved name:        {names['vessel_name_final'].notna().sum():,}")

# =============================================================================
# Filter names to CONTAINER vessels only (using vessel_type from VesselFinder)
# =============================================================================

# VesselFinder types: "Container Ship", "Container Ship (Fully Cellular)",
# "General Cargo Ship" (some misclassified feeders), etc.
CONTAINER_TYPES_KEYWORDS = ["container", "cellular"]

def is_container_type(vt):
    if not isinstance(vt, str):
        return None  # unknown → keep
    vt_low = vt.lower()
    if any(k in vt_low for k in CONTAINER_TYPES_KEYWORDS):
        return True
    # Non-container types we want to exclude
    for bad in ["car carrier", "vehicles carrier", "roll-on", "ro-ro", "cruise",
                "passenger", "crude oil", "chemical", "lpg", "lng",
                "bulk carrier", "ore carrier", "tanker", "cement", "livestock",
                "fishing", "tug", "supply", "research", "yacht",
                # Added after S. Francisco / Vitória audit — these are the
                # non-container vessels ANTAQ was letting through container
                # terminal calls (TESC in SFS receives general cargo; Capuaba
                # in Vitória receives Ro-Ro Grimaldi):
                "general cargo", "heavy lift", "multi-purpose", "multipurpose"]:
        if bad in vt_low:
            return False
    return None  # ambiguous → keep

names["is_container"] = names["vessel_type_final"].apply(is_container_type)

# Report vessel-type audit
print("\n      Vessel type breakdown (from VesselFinder scrape):")
if "vessel_type" in names.columns:
    vt_counts = names["vessel_type"].value_counts().head(15)
    for vt, n in vt_counts.items():
        print(f"        {vt[:50]:<50} {n:>4}")

# =============================================================================
# Merge names into atracacao
# =============================================================================

print("\n[4/7] Joining atracação × vessel names...")
merged = atrac.merge(
    names[["imo", "vessel_name_final", "shipping_line_master", "teu_capacity",
           "vessel_segment", "vessel_type_final", "is_container"]],
    on="imo", how="left"
)

# Filter to container vessels only (drop known non-container)
n_before = len(merged)
merged = merged[merged["is_container"] != False].copy()
print(f"      Dropped non-container vessel calls: {n_before - len(merged):,}")
print(f"      Remaining container calls:          {len(merged):,}")

# =============================================================================
# Classify
# =============================================================================

print("\n[5/7] Classifying carriers from vessel names...")

# Apply matching
classified = merged["vessel_name_final"].apply(match_carrier)
merged["carrier"] = classified.apply(lambda x: x[0])
merged["parent_group"] = classified.apply(lambda x: x[1])
merged["alliance"] = classified.apply(lambda x: x[2])

# Where shipping_line_master is available and non-empty, prefer it for carrier field
mask_has_master = merged["shipping_line_master"].notna() & (merged["shipping_line_master"] != "")
# Only override if master says something different AND was clearly identified
# (heuristic: master value takes precedence when regex returned UNKNOWN)
mask_unknown = merged["carrier"] == "UNKNOWN"
merged.loc[mask_has_master & mask_unknown, "carrier"] = merged.loc[
    mask_has_master & mask_unknown, "shipping_line_master"]

# Coverage report
print("\n      Coverage by carrier source:")
n_total = len(merged)
n_identified = (merged["carrier"] != "UNKNOWN").sum()
n_unknown = (merged["carrier"] == "UNKNOWN").sum()
print(f"        Total container calls:  {n_total:,}")
print(f"        Identified:             {n_identified:,} ({n_identified/n_total*100:.1f}%)")
print(f"        UNKNOWN:                {n_unknown:,} ({n_unknown/n_total*100:.1f}%)")

# =============================================================================
# Aggregate
# =============================================================================

print("\n[6/7] Aggregating carrier, group, and alliance summaries...")

def build_agg(df, key):
    agg = df.groupby(key).agg(
        n_calls=("imo", "count"),
        n_unique_vessels=("imo", "nunique"),
        total_teu=("teu_capacity", "sum"),
        avg_teu=("teu_capacity", "mean"),
    ).reset_index().sort_values("n_calls", ascending=False)
    agg["share_calls_pct"] = (agg["n_calls"] / agg["n_calls"].sum() * 100).round(2)
    agg["share_teu_pct"] = (agg["total_teu"] / agg["total_teu"].sum() * 100).round(2) \
        if agg["total_teu"].sum() > 0 else 0
    return agg

carrier_agg = build_agg(merged, "carrier")
group_agg = build_agg(merged, "parent_group")
alliance_agg = build_agg(merged, "alliance")

print("\n      Top carriers by calls:")
print(carrier_agg.head(12)[["carrier", "n_calls", "share_calls_pct",
                             "n_unique_vessels"]].to_string(index=False))

print("\n      Groups by calls:")
print(group_agg[["parent_group", "n_calls", "share_calls_pct",
                 "n_unique_vessels"]].to_string(index=False))

print("\n      Alliances by calls:")
print(alliance_agg[["alliance", "n_calls", "share_calls_pct",
                    "n_unique_vessels"]].to_string(index=False))

# =============================================================================
# HHI — dual computation
# =============================================================================

print("\n[7/7] Computing HHI...")

def hhi_class(hhi):
    if hhi is None:
        return "N/A"
    if hhi < 1500: return "Unconcentrated"
    if hhi < 2500: return "Moderately concentrated"
    return "Highly concentrated"

def hhi_from_shares(df, share_col="share_calls_pct", exclude=None):
    """Compute HHI. If exclude is set, drop those values and re-normalize shares."""
    if exclude:
        d = df[~df.iloc[:, 0].isin(exclude)].copy()
        total = d[share_col].sum()
        if total == 0: return None
        # Re-normalize to sum to 100
        d["share_norm"] = d[share_col] / total * 100
        return (d["share_norm"] ** 2).sum()
    return (df[share_col] ** 2).sum()

# HHI variants
hhi_carrier_raw = hhi_from_shares(carrier_agg)                                       # includes UNKNOWN
hhi_carrier_id  = hhi_from_shares(carrier_agg, exclude=["UNKNOWN"])                  # identified-only
hhi_group_raw   = hhi_from_shares(group_agg)
hhi_group_id    = hhi_from_shares(group_agg, exclude=["UNKNOWN"])
hhi_alliance_raw = hhi_from_shares(alliance_agg)
hhi_alliance_id  = hhi_from_shares(alliance_agg, exclude=["Unknown"])

# Concentration ratios (identified only)
ci = carrier_agg[carrier_agg["carrier"] != "UNKNOWN"].copy()
total_id = ci["share_calls_pct"].sum()
if total_id > 0:
    ci["share_norm"] = ci["share_calls_pct"] / total_id * 100
    top1_id = ci.iloc[0]["share_norm"]
    top3_id = ci.head(3)["share_norm"].sum()
    top5_id = ci.head(5)["share_norm"].sum()
else:
    top1_id = top3_id = top5_id = 0

print(f"\n      HHI (carrier level):")
print(f"        Raw (incl. UNKNOWN):   {hhi_carrier_raw:>7.0f} → {hhi_class(hhi_carrier_raw)}")
print(f"        Identified-only:       {hhi_carrier_id:>7.0f} → {hhi_class(hhi_carrier_id)}")
print(f"      HHI (parent group):")
print(f"        Raw:                   {hhi_group_raw:>7.0f} → {hhi_class(hhi_group_raw)}")
print(f"        Identified-only:       {hhi_group_id:>7.0f} → {hhi_class(hhi_group_id)}")
print(f"      HHI (alliance):")
print(f"        Raw:                   {hhi_alliance_raw:>7.0f} → {hhi_class(hhi_alliance_raw)}")
print(f"        Identified-only:       {hhi_alliance_id:>7.0f} → {hhi_class(hhi_alliance_id)}")
print(f"\n      Concentration (identified-only):")
print(f"        Top-1:  {top1_id:.2f}%   Top-3:  {top3_id:.2f}%   Top-5:  {top5_id:.2f}%")

# =============================================================================
# Carrier × Port matrix
# =============================================================================

pivot = merged.pivot_table(
    index="carrier", columns="Porto Atracação",
    values="imo", aggfunc="count", fill_value=0
)
pivot["_total"] = pivot.sum(axis=1)
pivot = pivot.sort_values("_total", ascending=False).drop(columns="_total")

# =============================================================================
# Save outputs
# =============================================================================

print("\n[SAVE] Writing outputs...")

merged[["imo", "vessel_name_final", "vessel_type_final", "carrier", "parent_group",
        "alliance", "Porto Atracação", "Terminal", "Data Atracação",
        "teu_capacity"]].to_csv(POST9_DIR / "carrier_by_call.csv",
                                sep=";", index=False, encoding="utf-8-sig")

carrier_agg.to_csv(POST9_DIR / "carrier_summary.csv", sep=";",
                   index=False, encoding="utf-8-sig")
group_agg.to_csv(POST9_DIR / "group_summary.csv", sep=";",
                 index=False, encoding="utf-8-sig")
alliance_agg.to_csv(POST9_DIR / "alliance_summary.csv", sep=";",
                    index=False, encoding="utf-8-sig")
pivot.to_csv(POST9_DIR / "carrier_port_matrix.csv",
             sep=";", encoding="utf-8-sig")

hhi_summary = pd.DataFrame([
    {"metric": "HHI_carrier_raw",       "value": round(hhi_carrier_raw, 1),
     "classification": hhi_class(hhi_carrier_raw)},
    {"metric": "HHI_carrier_identified","value": round(hhi_carrier_id, 1),
     "classification": hhi_class(hhi_carrier_id)},
    {"metric": "HHI_group_raw",         "value": round(hhi_group_raw, 1),
     "classification": hhi_class(hhi_group_raw)},
    {"metric": "HHI_group_identified",  "value": round(hhi_group_id, 1),
     "classification": hhi_class(hhi_group_id)},
    {"metric": "HHI_alliance_raw",      "value": round(hhi_alliance_raw, 1),
     "classification": hhi_class(hhi_alliance_raw)},
    {"metric": "HHI_alliance_identified","value": round(hhi_alliance_id, 1),
     "classification": hhi_class(hhi_alliance_id)},
    {"metric": "top1_share_pct_identified", "value": round(top1_id, 2),
     "classification": ci.iloc[0]["carrier"] if len(ci) else ""},
    {"metric": "top3_share_pct_identified", "value": round(top3_id, 2), "classification": ""},
    {"metric": "top5_share_pct_identified", "value": round(top5_id, 2), "classification": ""},
    {"metric": "total_container_calls", "value": int(n_total), "classification": ""},
    {"metric": "identified_calls",      "value": int(n_identified), "classification": ""},
    {"metric": "unknown_calls",         "value": int(n_unknown), "classification": ""},
    {"metric": "identification_coverage_pct",
     "value": round(n_identified/n_total*100, 2) if n_total > 0 else 0,
     "classification": ""},
])
hhi_summary.to_csv(POST9_DIR / "hhi_summary.csv",
                   sep=";", index=False, encoding="utf-8-sig")

# Unknown vessels audit — for manual review
unknown_audit = (merged[merged["carrier"] == "UNKNOWN"]
                 .groupby("vessel_name_final")
                 .agg(n_calls=("imo", "count"),
                      imo=("imo", "first"),
                      vessel_type=("vessel_type_final", "first"))
                 .reset_index()
                 .sort_values("n_calls", ascending=False)
                 .head(100))
unknown_audit.to_csv(POST9_DIR / "unknown_vessels_audit.csv",
                     sep=";", index=False, encoding="utf-8-sig")

print(f"\n  Saved: carrier_by_call.csv       ({len(merged):,} rows)")
print(f"  Saved: carrier_summary.csv       ({len(carrier_agg):,} carriers)")
print(f"  Saved: group_summary.csv         ({len(group_agg):,} groups)")
print(f"  Saved: alliance_summary.csv      ({len(alliance_agg):,} alliances)")
print(f"  Saved: carrier_port_matrix.csv   ({len(pivot):,} × {len(pivot.columns)})")
print(f"  Saved: hhi_summary.csv")
print(f"  Saved: unknown_vessels_audit.csv (top-100 for manual review)")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
