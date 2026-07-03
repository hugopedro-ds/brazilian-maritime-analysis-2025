# Post 9 — Methodology

**Container carrier deployment in Brazilian ports, 2025**

Author: Hugo Pedreira — [LinkedIn](https://www.linkedin.com/in/hugo-pedreira)
Data cutoff: ANTAQ 2025 (Jan–Nov)
Publication target: LinkedIn + GitHub case study

---

## 1. Research question

*"For a Trade Lane Manager buying China–Brazil container transport: who actually serves the lane at scale in Brazilian container ports, where is the real optionality at port level, and where does the data show carrier concentration that a spreadsheet-based procurement model tends to miss?"*

The output aims to be procurement-actionable, not academic.

---

## 2. Data sources

| Source | What | Coverage | Access |
|---|---|---|---|
| ANTAQ — Estatístico Aquaviário 2025, table *Atracação* | Every vessel berthing at a Brazilian port | 116.098 records, Jan–Nov 2025 | [antaq.gov.br](https://web3.antaq.gov.br/) |
| VesselFinder public vessel page | Vessel name and type by IMO | 975 IMOs scraped (100% OK) | vesselfinder.com/vessels/details/{imo} |
| Vessels Master (from prior Post 4 work) | 1.378 IMOs with carrier + TEU already enriched | Cross-checked as fallback source | Internal |

No AIS data was used. The identification of the carrier is derived from vessel names and pattern matching, not real-time positioning.

---

## 3. Scope filters (applied in order)

Starting universe: 116.098 ANTAQ berthings.

**Filter 1 — International navigation only**
`Tipo de Navegação da Atracação == "Longo Curso"`
→ Excludes cabotagem and interior navigation.
→ Remaining: 22.746

**Filter 2 — Container terminal whitelist**
Built from operational knowledge of the Brazilian port sector. Only berthings at terminals whose primary business is container handling.

| Port | Terminal (ANTAQ label) | Operator |
|---|---|---|
| Santos | Cais da Santos Brasil (SSZ 16) | Santos Brasil |
| Santos | Cais da BTP (SSZ 41) | Brasil Terminal Portuário |
| Santos | Cais da Ecoporto (SSZ 35) | Ecoporto Santos |
| Santos | Cais do TEV (SSZ 18) | DP World Santos |
| Paranaguá | TCP | Terminal de Contêineres de Paranaguá |
| Rio Grande | Cais Tecon Rio Grande | Wilson Sons Tecon |
| Rio de Janeiro | Multi-Rio | Multi-Rio Operações Portuárias |
| Rio de Janeiro | ICTSI | ICTSI Rio Brasil |
| Salvador | TECON / TECON Área 2 | Wilson Sons Tecon Salvador |
| São Francisco do Sul | TESC | Terminal Santa Catarina |
| Itajaí | Cais Arrendado Transitoriamente | APM Terminals Itajaí |
| Vitória | Cais de Capuaba | TVV / Log-In |
| Navegantes (registered as "Portonave" in ANTAQ) | Portonave | Portonave |
| Manaus (registered as "Super Terminais" in ANTAQ) | Super Terminais | Super Terminais |
| Ceará (registered as "Pecém" in ANTAQ) | Terminal Portuário do Pecém | Complexo do Pecém |

→ Remaining: 5.231 berthings across 15 container terminals in 11 ports.

**Filter 3 — Valid IMO (7-digit numeric)**
Removes rows with malformed or missing IMO numbers.
→ Remaining: 5.229 berthings across 1.019 unique IMOs.

**Filter 4 — Non-container vessel exclusion**
Vessels whose *VesselFinder ship type* was in a non-container class were excluded. This was necessary because some whitelisted terminals (notably TESC in São Francisco do Sul and Cais de Capuaba in Vitória) also receive multipurpose, general cargo, and Ro-Ro vessels.

Blacklisted vessel types:
`car carrier`, `vehicles carrier`, `roll-on`, `ro-ro`, `cruise`, `passenger`, `crude oil`, `chemical`, `lpg`, `lng`, `bulk carrier`, `ore carrier`, `tanker`, `cement`, `livestock`, `fishing`, `tug`, `supply`, `research`, `yacht`, `general cargo`, `heavy lift`, `multi-purpose`.

→ Remaining: **4.226 vessel calls across 433 unique IMOs and 9 ports**.

Two ports (São Francisco do Sul and Vitória) fell below 20 container calls after this filter and were excluded from all three panels of the chart for consistency:

- São Francisco do Sul: 2 container calls (dominant traffic is general cargo — Arrow family, UBC Tampa, Star Laguna)
- Vitória: 2 container calls (dominant traffic is Ro-Ro Grimaldi and BBC / Chipolbrok multipurpose)

This exclusion is a methodological limit, not a claim that these ports do not handle containers — they simply are not primarily container ports in the 2025 dataset.

---

## 4. Carrier identification

The ANTAQ dataset does not carry a "carrier" or "shipping line" column. Identification is derived from vessel names via regex pattern matching, with alliance mapping applied for the February 2025 configuration.

**Sources of vessel names, in order of priority:**

1. **VesselFinder scrape** — 975 IMOs, public web page, HTML parse of the `<title>` element. Rate-limited to 8–12 s per request; 100% OK, 0 failures.
2. **Vessels Master (prior Post 4 work)** — 1.378 IMOs with carrier already curated. Used as fallback where scrape was not possible.

**Pattern matching logic**

Regex applied to the upper-cased vessel name, ordered from most specific to most general. Examples:

| Regex | Carrier assigned | Alliance |
|---|---|---|
| `^\s*CMA[\s-]*CGM\b` | CMA CGM | Ocean Alliance |
| `^\s*MAERSK\b` | Maersk | Gemini Cooperation |
| `\bMAERSK\s*$` (suffix) | Maersk (charter fleet: SAN RAPHAEL MAERSK etc.) | Gemini Cooperation |
| `^\s*(HAPAG[\s-]*LLOYD\|HH\s+[A-Z]+\b)` | Hapag-Lloyd | Gemini Cooperation |
| `^\s*[A-Z]+(\s+[A-Z]+){0,2}\s+(EXPRESS\|EXP)\b` (with negative lookahead on other-carrier prefixes) | Hapag-Lloyd (Express family, e.g. ESPIRITO SANTO EXP) | Gemini Cooperation |
| `^\s*(MSC\|MEDITERRANEAN\s+SHIPPING)\b` | MSC | MSC (standalone) |
| `^\s*(COSCO\|CSCL)` | Cosco Shipping | Ocean Alliance |
| `^\s*EVER(\s+[A-Z]+\|\b)` | Evergreen | Ocean Alliance |
| `^\s*OOCL\b` | OOCL | Ocean Alliance |
| `^\s*ONE\s+(?!OFF\b)[A-Z]+` | Ocean Network Express | Premier Alliance |
| `^\s*HMM\b` or `^\s*HYUNDAI\b` | HMM | Premier Alliance |
| `^\s*(YANG\s+MING\|YM)\s+[A-Z]+` | Yang Ming | Premier Alliance |
| `^\s*ZIM\b` | ZIM | Non-aligned |
| `^\s*KOTA\s+[A-Z]+` | PIL (Pacific International Lines) | Non-aligned |
| `^\s*WAN\s*HAI\b` | Wan Hai | Non-aligned |
| `^\s*APL\b` | APL | Ocean Alliance (CMA CGM group) |
| `^\s*MERCOSUL\b` | Mercosul Line | Regional / affiliated carrier (CMA CGM group by ownership, but intra-BR/LatAm deployment) |
| `^\s*ALIAN(C\|Ç)A\b` | Aliança | Gemini Cooperation (Maersk group) |
| `^\s*SEALAND\b` | Sealand | Gemini Cooperation (Maersk group) |
| `^\s*(HAMBURG\s+SUD\|CAP\s+SAN\|MONTE\s+[A-Z]+\|POLAR\s+ECUADOR\|CCNI\s+[A-Z]+)\b` | Hamburg Süd | Gemini Cooperation (Maersk group) |
| `^\s*KMTC\b`, `^\s*SITC\b`, `^\s*SINOTRANS\b`, `^\s*HEUNG[-\s]*A\b` | Respective carrier | Non-aligned |
| `^\s*LOG[-\s]*IN\b` | Log-In | Regional / affiliated carrier (cabotagem BR + short-sea LatAm) |

Two hierarchical levels are computed on top of the carrier:

- **Parent group** — corporate consolidation. Example: MAERSK + HAMBURG SUD + SEALAND + ALIANCA = Maersk Group; CMA CGM + APL + MERCOSUL + ANL = CMA CGM Group.
- **Alliance** — commercial cooperation as of February 2025: **Gemini Cooperation** (Maersk + Hapag-Lloyd), **Ocean Alliance** (CMA CGM + Cosco + Evergreen + OOCL), **Premier Alliance** (ONE + HMM + Yang Ming, ex-THE Alliance), **MSC standalone**, **Non-aligned** (ZIM, PIL, Wan Hai, etc.).

The 2M dissolution and the launch of Gemini are captured because the dataset spans the transition (Feb 2025 onwards).

---

## 5. Coverage and the UNKNOWN bucket

Of the 4,226 container calls in scope:

- **3,137 identified (74.5%)** — a carrier, parent group and alliance were assigned
- **1,089 UNKNOWN (25.5%)** — no pattern match; grouped as "Unknown" for HHI calculation

The UNKNOWN bucket is dominated by charter and tramp tonnage without a carrier brand in the name. Examples audited: TIGER PLATA, CZECH, SPIRIT OF DUBAI, CAPE ARTEMISIO, GSL ARCADIA. These vessels can be operating for any of the identified carriers under a time-charter or spot-charter arrangement — attribution would require voyage-level service data (from carrier schedules, not from ANTAQ or public AIS).

**Decision:** UNKNOWN is not distributed proportionally or attributed to a most-likely carrier. This would risk introducing a bias. Both HHI variants are reported:

- **HHI raw** — treats UNKNOWN as a single competitor (upper-bound on concentration)
- **HHI identified-only** — excludes UNKNOWN and re-normalises the shares (lower-bound on concentration)

Conclusions in the post hold under both readings.

### Regional / affiliated carrier classification (Mercosul, Log-In)

Two carriers were reclassified during audit:

- **Mercosul Line** — CMA CGM group by ownership since 2017, but operates as an intra-Brazil / intra-LatAm regional carrier, **not as an Ocean Alliance long-haul service**. Classifying Mercosul under Ocean Alliance would have inflated the alliance's share (from 13.8% to 15.7%) and hidden a legitimate procurement category — the regional/affiliated services that operate alongside global alliances.
- **Log-In Logística Intermodal** — Cabotagem BR + short-sea LatAm operator. Not part of any global alliance.

Both are now grouped as **Regional / affiliated carrier** (3.5% of calls combined). This is a deliberate choice: for a Trade Lane Manager, these carriers are not procurement substitutes for the alliance-led long-haul services on the China–Brazil corridor.

### Final alliance-level HHI

After the reclassification above:

- **HHI carrier level (identified only):** 2,129 — moderately concentrated
- **HHI parent-group level (identified only):** 2,273 — moderately concentrated
- **HHI alliance level (identified only):** **2,791 — highly concentrated**

The alliance-level HHI is the headline number for the post because it reflects the actual negotiation surface a procurement team faces on the China–Brazil corridor: 3 alliance blocks + MSC standalone.

---

## 6. Herfindahl-Hirschman index

HHI is computed as the sum of squared market shares (in %), with the standard DOJ/FTC thresholds:

- HHI < 1.500 → unconcentrated
- 1.500 ≤ HHI < 2.500 → moderately concentrated
- HHI ≥ 2.500 → highly concentrated

Computed at three levels: carrier, parent group, alliance. Reported both port-level (in the chart) and market-level (in the post text).

**Ports with fewer than 20 container calls** are excluded from the HHI ranking. This threshold is arbitrary but sensible — HHI is unstable with tiny samples (e.g., 2 calls from 2 carriers at 50/50 mechanically produces HHI 5.000, which is not a meaningful concentration signal).

---

## 7. Known limitations (declared upfront)

1. **Vessel-name matching is a proxy for carrier deployment.** It captures branded fleets well and charter fleets poorly. Real vessel-service assignment would require carrier schedule data (Alphaliner Axsmarine, Sea/net, or Sea-Intelligence commercial feeds).

2. **Call counts do not equal TEU-weighted capacity.** MSC's 28,9% call share does not mean 28,9% of moved boxes — some carriers deploy larger vessels. Where TEU capacity was available (via Vessels Master), we also report TEU-weighted shares in the CSVs (see `carrier_summary.csv`).

3. **The dataset is Jan–Nov 2025.** Alliance shares reflect the Feb 2025 configuration but only capture 5 months post-Gemini launch. Sustained shift claims should be re-tested with full 2025 + 2026 data.

4. **Two ports excluded from HHI panels** (São Francisco do Sul, Vitória) for insufficient container sample — see filter 4.

5. **UNKNOWN 25,5% is a data limitation, not a modelling flaw.** Charter tonnage in Brazil is opaque by design; no vessel-name pattern will ever hit 100% without proprietary carrier schedule data.

6. **This is a case study, not a commercial report.** Numbers are directional. A procurement team should validate against carrier service maps before acting.

---

## 8. Reproducibility

All code and data pipelines are in this repository:

```
scripts/
  extract_imos_v2.py           # ANTAQ → container-terminal IMO list
  scrape_vessel_names.py       # VesselFinder public page scraper
  carrier_from_vessel_name_v2.py  # Regex classification + HHI + outputs
  chart_final.py               # 3-panel composite chart
data/
  atracacao_2025.csv           # ANTAQ raw (large file — see README for source link)
  vessel_names.csv             # 975 IMOs scraped
  carrier_by_call.csv          # Every classified call
  carrier_summary.csv          # Carrier-level aggregates
  group_summary.csv            # Parent-group aggregates
  alliance_summary.csv         # Alliance-level aggregates
  hhi_summary.csv              # All HHI variants
  unknown_vessels_audit.csv    # Top-100 UNKNOWN for manual review
outputs/
  post9_chart_final.png        # Final chart
```

To reproduce end-to-end:

```
python scripts/extract_imos_v2.py
python scripts/scrape_vessel_names.py       # ~2-3 hours, respectful rate limit
python scripts/carrier_from_vessel_name_v2.py
python scripts/chart_final.py
```

The scraping step is respectful (8–12 s per request, backoff on 429) and requests only publicly available data (vessel name, ship type). No account or authentication is used. No paywalled data (owner, manager, position history) is accessed.

---

## 9. What this study is NOT

- Not a claim about who "wins" the Brazil container market — capacity share and revenue share are different things.
- Not a substitute for carrier schedule data — this is a snapshot inferred from deployment, not a service map.
- Not comparable across years without re-running with matching methodology.
- Not a critique of MSC or any other carrier — dominant market position is a fact of the current alliance structure, not a value judgment.

---

*If you spot a methodological gap or a factual error, open an issue on the repo. This is a case study — feedback improves the work.*
