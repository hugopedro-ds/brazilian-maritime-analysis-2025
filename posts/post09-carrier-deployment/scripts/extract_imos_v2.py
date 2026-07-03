"""
Post 9 — Step 1 v2: Extract unique IMOs from ANTAQ 2025 filtered by CONTAINER TERMINAL.

Rationale for v2 (vs v1):
  v1 filtered by "Longo Curso" + top-10 port cities. That returned 3,463 IMOs but
  ~80% turned out to be car carriers, cruise, tankers, bulk — because "Longo Curso"
  means "international navigation", not container.

  v2 filters by TERMINAL whitelist (container-dedicated or container-primary).
  This is a proxy for "vessel that moved a container box in Brazil in 2025".

Whitelist source: operational knowledge of Brazilian container terminals.
  Trade-off: multipurpose terminals (Capuaba/TVV, Itajaí APM Arrendado) let some
  break-bulk vessels through; documented in methodology.md.

Output: Data/post9/imos_to_lookup.csv (replaces v1)
Backup of v1: Data/post9/imos_to_lookup_v1_backup.csv
"""

import shutil
import pandas as pd
from pathlib import Path

# =============================================================================
# Config
# =============================================================================

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "Data"
OUT_DIR = DATA_DIR / "post9"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ATRACACAO_CSV = DATA_DIR / "antaq" / "atracacao_2025.csv"
VESSELS_MASTER_CSV = DATA_DIR / "antaq" / "vessels_master_enriched.csv"

# =============================================================================
# CONTAINER TERMINAL WHITELIST
# =============================================================================
# Each entry = (Porto Atracação, Terminal). Match is exact on both fields.
# Validated 2026-07-02 with Hugo (DP World operational background).

CONTAINER_TERMINALS = [
    # Santos — 4 terminais container-only ou container-primary
    ("Santos", "Cais da Santos Brasil (SSZ 16) - Privativo"),  # Santos Brasil (Tecon)
    ("Santos", "Cais da BTP (SSZ 41) - Privativo"),            # Brasil Terminal Portuário
    ("Santos", "Cais da Ecoporto (SSZ 35) - Privativo"),       # Ecoporto Santos
    ("Santos", "Cais do TEV (SSZ 18) - Privativo"),            # DP World Santos

    # Paranaguá
    ("Paranaguá", "TCP"),                                       # Terminal de Contêineres de Paranaguá

    # Rio Grande
    ("Rio Grande", "Cais Tecon Rio Grande S.A."),               # Wilson Sons Tecon

    # Rio de Janeiro
    ("Rio de Janeiro", "Multi-Rio"),                            # Multi-Rio Operações Portuárias
    ("Rio de Janeiro", "ICTSI"),                                # ICTSI Rio Brasil

    # Salvador
    ("Salvador", "TECON"),                                      # Wilson Sons Tecon Salvador
    ("Salvador", "TECON Área 2"),                               # Wilson Sons Tecon Salvador

    # São Francisco do Sul
    ("São Francisco do Sul", "TESC"),                           # Terminal Santa Catarina

    # Itajaí — Cais Arrendado (APM Terminals)
    ("Itajaí", "Cais Arrendado Transitoriamente"),              # APM Terminals Itajaí

    # Vitória — TVV (multipurpose, dominante container)
    ("Vitória", "Cais de Capuaba"),                             # TVV / Log-In

    # Portos privativos registados separadamente na ANTAQ
    ("Portonave - Terminais Portuários de Navegantes",
     "Portonave - Terminais Portuários de Navegantes"),         # Portonave (Navegantes)
    ("Super Terminais Comércio e Indústria",
     "Super Terminais Comércio e Indústria"),                    # Super Terminais (Manaus)
    ("Terminal Portuário do Pecém",
     "Terminal Portuário do Pecém"),                             # Pecém (Ceará)
]

# =============================================================================
# Load ANTAQ
# =============================================================================

print("=" * 70)
print("Step 1 v2 — Extract container IMOs from ANTAQ 2025 (terminal whitelist)")
print("=" * 70)

print("\n[1/6] Loading ANTAQ atracação 2025...")
atrac = pd.read_csv(ATRACACAO_CSV, sep=";", encoding="utf-8-sig", low_memory=False)
print(f"      Loaded {len(atrac):,} rows")

# =============================================================================
# Filters
# =============================================================================

print("\n[2/6] Applying filters...")

# Filter 1: Longo Curso only
n_before = len(atrac)
atrac = atrac[atrac["Tipo de Navegação da Atracação"] == "Longo Curso"]
print(f"      Longo Curso only:            {n_before:>8,} → {len(atrac):>8,}")

# Filter 2: Container terminal whitelist
n_before = len(atrac)
whitelist_set = set(CONTAINER_TERMINALS)
atrac["port_terminal"] = list(zip(atrac["Porto Atracação"], atrac["Terminal"]))
atrac = atrac[atrac["port_terminal"].isin(whitelist_set)]
print(f"      Container terminals only:    {n_before:>8,} → {len(atrac):>8,}")

# Filter 3: Valid IMO
n_before = len(atrac)
atrac["imo_clean"] = pd.to_numeric(atrac["Nº do IMO"], errors="coerce")
atrac = atrac[atrac["imo_clean"].notna()]
atrac["imo_clean"] = atrac["imo_clean"].astype("int64")
atrac = atrac[(atrac["imo_clean"] >= 1_000_000) & (atrac["imo_clean"] <= 9_999_999)]
print(f"      Valid 7-digit IMO:           {n_before:>8,} → {len(atrac):>8,}")

# =============================================================================
# Terminal-level breakdown (for methodology transparency)
# =============================================================================

print("\n[3/6] Terminal-level breakdown:")
tbreak = atrac.groupby(["Porto Atracação", "Terminal"]).agg(
    calls=("imo_clean", "count"),
    unique_imos=("imo_clean", "nunique"),
).sort_values("calls", ascending=False)
for (port, term), row in tbreak.iterrows():
    print(f"      {port:<50} {term[:45]:<45} {row['calls']:>5} calls | {row['unique_imos']:>4} IMOs")

# =============================================================================
# Aggregate: unique IMOs
# =============================================================================

print("\n[4/6] Aggregating unique IMOs...")
imos = (
    atrac.groupby("imo_clean")
    .agg(
        n_calls_container_terminals=("Porto Atracação", "count"),
        first_seen_port=("Porto Atracação", "first"),
        first_seen_terminal=("Terminal", "first"),
        first_seen_date=("Data Atracação", "min"),
        n_distinct_ports=("Porto Atracação", "nunique"),
    )
    .reset_index()
    .rename(columns={"imo_clean": "imo"})
    .sort_values("n_calls_container_terminals", ascending=False)
    .reset_index(drop=True)
)
print(f"      Unique IMOs found: {len(imos):,}")

# =============================================================================
# Cross-reference with vessels_master_enriched
# =============================================================================

print("\n[5/6] Cross-referencing with vessels_master_enriched...")
vessels_known = pd.read_csv(VESSELS_MASTER_CSV, sep=",", encoding="utf-8-sig")
known_imos = set(pd.to_numeric(vessels_known["NÚMERO IMO"], errors="coerce")
                 .dropna().astype("int64"))

imos["already_known"] = imos["imo"].isin(known_imos)
imos_to_lookup = imos[~imos["already_known"]].copy()
imos_already_known = imos[imos["already_known"]].copy()

print(f"      IMOs already in vessels_master: {len(known_imos):,}")
print(f"      IMOs to lookup (new):           {len(imos_to_lookup):,}")
print(f"      IMOs already enriched:          {len(imos_already_known):,}")

# =============================================================================
# Save outputs
# =============================================================================

print("\n[6/6] Saving outputs...")

# Backup v1 if exists
v1_path = OUT_DIR / "imos_to_lookup.csv"
if v1_path.exists():
    backup = OUT_DIR / "imos_to_lookup_v1_backup.csv"
    shutil.copy(v1_path, backup)
    print(f"      Backed up v1 → {backup.name}")

imos_to_lookup[[
    "imo", "n_calls_container_terminals", "first_seen_port",
    "first_seen_terminal", "first_seen_date", "n_distinct_ports"
]].to_csv(v1_path, sep=";", index=False, encoding="utf-8-sig")

imos_already_known[[
    "imo", "n_calls_container_terminals", "first_seen_port",
    "first_seen_terminal", "first_seen_date", "n_distinct_ports"
]].to_csv(OUT_DIR / "imos_already_known.csv", sep=";", index=False, encoding="utf-8-sig")

# Save terminal breakdown for methodology.md
tbreak.to_csv(OUT_DIR / "container_terminals_breakdown.csv", sep=";", encoding="utf-8-sig")

# Human summary
with open(OUT_DIR / "imos_summary.txt", "w", encoding="utf-8") as f:
    f.write("Post 9 — IMO extraction v2 (container-terminal whitelist)\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Container terminal calls (Longo Curso): {len(atrac):,}\n")
    f.write(f"Unique IMOs found:                      {len(imos):,}\n")
    f.write(f"Already enriched (vessels_master):      {len(imos_already_known):,}\n")
    f.write(f"To lookup in VesselFinder:              {len(imos_to_lookup):,}\n\n")
    f.write("Terminal whitelist (n=15):\n")
    for port, term in CONTAINER_TERMINALS:
        f.write(f"  - {port}: {term}\n")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"  Container terminal calls:      {len(atrac):>8,}")
print(f"  Unique IMOs found:             {len(imos):>8,}")
print(f"  Already enriched:              {len(imos_already_known):>8,}")
print(f"  → To lookup in VesselFinder:   {len(imos_to_lookup):>8,}")
est_h = len(imos_to_lookup) * 10 / 3600
print(f"\n  Estimated scraping time (10s/req): {est_h:.1f}h")
print("=" * 70)
