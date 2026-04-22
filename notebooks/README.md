# Brazilian Maritime Market Analysis — 2025

📊 **[View rendered notebooks with charts and outputs → nbviewer](https://nbviewer.org/github/hugopedro-ds/brazilian-maritime-analysis-2025/)**
Exploratory analysis of Brazil's container shipping market  
using public data from ANTAQ, ComexStat and UNCTAD.

**Scope:** 22,746 deep sea port calls | 1,378 vessels | 8 carriers | 10 ports

---

## Key Findings

1. **Pre-berthing wait — not terminal inefficiency — drives TEstadia.**  
   Median 23.2h before berthing in deep sea calls (2025).  
   Brazil operates at 2.1x the developing country average  
   (UNCTAD RMT 2025 benchmark: 10.9h).

2. **Within the Feeder Max segment (1k–3k TEU), CMA CGM holds 68.9% of
   deployed capacity (HHI = 5,480 — highly concentrated intra-segment).**  
   Not a Brazil-wide monopoly: the country overall is split across 8 carriers.
   The concentration is specific to this vessel class. CMA CGM is also the
   most operationally efficient carrier within the segment
   (75h vs 104h median TEstadia without CMA CGM).

3. **No carrier allocates more than 12% of its registered fleet to Brazil.**  
   COSCO: 335 vessels registered, 25 active (7.5%).  
   Maersk: 261 registered, 21 active (8.0%).  
   Structurally underpenetrated relative to South-South  
   trade growth of 8.7% in 2024 (UNCTAD RMT 2025, Ch. I).

4. **Berth occupancy correlates with TEstadia across the 9-port sample.**  
   Spearman ρ = 0.82, point estimate (n = 9 ports, São Francisco do Sul  
   excluded as structural outlier).  
   Bootstrap 95% CI = [0.23, 1.00] — wide due to small n. Leave-one-out  
   range: 0.74 – 0.98 depending on which port is removed. Suape (65.7%  
   occupancy / 54.6h TEstadia) is the counter-example within the sample.  
   Paranaguá at 77% occupancy / 98h is the saturation case.  
   → Full robustness analysis: `outputs/figures/nb15_03_bootstrap_loo.png`

---

## Notebooks

| # | Notebook | Topic |
|---|---|---|
| 01 | diagnostico_dados | Dataset inventory and quality audit |
| 02 | eficiencia_terminais | Terminal efficiency decomposition |
| 03 | evolucao_sistema | System evolution and cabotage growth |
| 04 | graficos_frota_vessel | Fleet structure by carrier and segment |
| 05 | port_compatibility | Physical fleet × port constraint analysis |
| 06 | fleet_renewal | CII exposure and fleet renewal pressure |
| 07 | market_power_feeder | Feeder Max market concentration (HHI) |
| 08 | kpis_operacionais | Operational KPIs by carrier (2025) |
| 09 | fundeio_carrier | Anchorage analysis by carrier |
| 10 | presenca_operacional | Fleet registered vs active in Brazil |
| 11 | comexstat_valor | Economic value by port (ComexStat) |
| 12 | testadia_vessel_segment | TEstadia by vessel segment × port |
| 13 | ocupacao_bercos | Berth occupancy rate analysis |
| 14 | custo_espera_carrier | Waiting cost per carrier (USD) |
| 15 | robustez_correlacao | Spearman robustness test |
| 16 | auditoria_bercos_santos | Santos 55-berth audit |

---

## Data Sources

- **ANTAQ SGMM** — port calls, berthing times, stoppage events (2025)
- **ComexStat / MDIC** — trade flows by NCM, UF, partner country (2023–2024)
- **UNCTAD Review of Maritime Transport 2025** — international benchmarks
- **Web scraping** — vessel dimensions (LOA, beam) to enrich fleet dataset

---

## Methodology

Every headline number in this repository has a fixed operational definition,
source column, filter, and reference notebook documented in
[`docs/definitions.md`](../docs/definitions.md). That document exists so that
any reader — analyst, carrier commercial team, academic — can reproduce each
figure without ambiguity, and so that the known trade-offs of each metric are
explicit rather than hidden.

Brief notes on the most sensitive choices:

- **TEstadia = Data Desatracação − Data Chegada.** Includes pre-berth wait,
  berth dwell before operation, operation itself, and post-operation wait.
- **Pre-berth wait (TEsperaAtracacao) = Data Atracação − Data Chegada.** Based
  on port-reported arrival timestamp; not AIS-validated.
- **Feeder Max = 1k–3k TEU capacity band.** HHI and CMA CGM share are
  computed **within this segment only**, not across the full Brazilian
  container market.
- **Carrier fleet allocation** is measured as unique-vessel count
  (`vessels_in_Brazil / registered_fleet`), not TEU-weighted.
- **UNCTAD 10.9h benchmark** is derived from AIS-based UN Global Platform
  data; not directly equivalent to administrative ANTAQ TEstadia. The 2.1×
  ratio should be read as order-of-magnitude, not a strict like-for-like.
- **Correlation ρ = 0.82** uses 9 ports after excluding São Francisco do Sul
  (structural bulk-grain outlier, TEstadia = 240h). Bootstrap CI and
  leave-one-out are in `outputs/processed_data/robustez_*.csv`.

---

## Key Limitations

**Data-level**
- No AIS data — static fleet analysis, not real-time deployment.
- DWT 100% null — draught-based port constraint not calculable.
- LOA / beam missing for 24% of vessels (concentrated in COSCO, CMA CGM).
- Cargo files truncated at Excel row limit (1,048,575 rows).
- IMO coverage: 93.6% for deep sea + cabotage; 49% for full dataset.

**Methodological**
- Single year of data (2025). No multi-year seasonality or trend confirmation.
- ANTAQ monthly granularity. No per-call queue-time at berth.
- UNCTAD comparison is order-of-magnitude, not strictly homogeneous (AIS vs
  administrative timestamps).
- Correlation sample is n = 9 ports. Point estimate is defensible
  (ρ = 0.82) but the 95% bootstrap CI is wide [0.23, 1.00]; with n this
  small, the uncertainty cannot be eliminated — only disclosed.
- "Slot management absence" is inferred from TEspera + TAtracado
  decomposition, not proven causally. AIS data would allow
  ship-berth synchronisation analysis proper.

**Scope**
- No tariff or revenue data — operational view only, not commercial margin.
- No weather data — cannot isolate weather-driven stoppages from structural
  congestion.
- Foreign ports only appear as origin/destination strings — no foreign-side
  performance comparison.

All limitations are declared explicitly in the notebook that produces the
affected metric.

---

## International Benchmark

Brazil's pre-berthing wait (23.2h) vs UNCTAD peer average (10.9h)
points to slot management absence as the likely structural driver — not
terminal-side operational inefficiency alone. The ratio is an
order-of-magnitude comparison: ANTAQ reports administrative timestamps,
UNCTAD derives time in port from AIS. Both capture time not spent
operating, but the exact intervals measured differ.

> *"Rising containership congestion and longer container handling times  
> in 2024 strained operational efficiency in ports."*  
> — UNCTAD Review of Maritime Transport 2025, Chapter IV

---

## Stack

Python · Pandas · SciPy · Matplotlib · Seaborn · Jupyter