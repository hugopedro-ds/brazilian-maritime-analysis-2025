# Brazilian Maritime Trade Analysis — 2025

Case studies on Brazil's container shipping market and bilateral maritime trade flows, built from public data — ANTAQ, ComexStat, UNCTAD.

**Written for** container shipping line commercial and operations teams, freight forwarders, port operators, and trade analysts evaluating Brazil-related deployment, pricing, and procurement decisions.

**Author:** Hugo Pedro — Data Analyst | BI & Analytics | Maritime Logistics focus
**LinkedIn:** [linkedin.com/in/hugopedro](https://www.linkedin.com/in/hugopedro/)

---

## Posts in this repository

| # | Post | Date | Theme | Folder |
|---|---|---|---|---|
| 6 | Brazilian port carrier concentration (HHI) | 16 Jun 2026 | Port-level carrier concentration | (foundational, see below) |
| 7 | The landed-cost framework for Brazilian port selection | 18 Jun 2026 | Procurement framework | (foundational, see below) |
| **8** | **Brazil-China trade asymmetry — cargo and ports** | **22 Jun 2026** | **Bilateral trade structure** | [`posts/post08-china-brazil/`](posts/post08-china-brazil/) |

Each post folder contains its own README, methodology, scripts, data, and outputs. Posts are self-contained and reproducible.

---

## Foundational study: Brazilian container shipping market (ANTAQ-based)

The original study underlying Posts 6 and 7 — covers Brazil's container port performance using ANTAQ deep-sea call data 2025.

**Scope:** 22,746 deep-sea port calls · 1,378 vessels · 8 carriers · 10 ports · 2025.

**Rendered notebooks (charts + outputs):** [nbviewer.org/github/hugopedro-ds/brazilian-maritime-analysis-2025/](https://nbviewer.org/github/hugopedro-ds/brazilian-maritime-analysis-2025/)

### The question the foundational study answers

Is Brazil's container port underperformance a **terminal problem** (handling productivity, infrastructure) — or a **coordination problem** (slot management, berth scheduling) between carrier and port?

The answer matters because it changes where a carrier should push: harder negotiations on terminal productivity versus investment in arrival coordination and dedicated windows.

### Key findings (foundational study)

#### 1 — Pre-berth wait, not terminal handling, drives port stay

Median pre-berth wait in deep-sea calls is **23.2h**. Median total TEstadia is **84h**. Roughly a quarter of the port stay happens before the vessel ever touches the berth.

UNCTAD RMT 2025 reports a developing-country median time-in-port of 10.9h. Brazil runs at roughly 2.1× that benchmark. The comparison is order-of-magnitude — UNCTAD is AIS-derived, ANTAQ is administrative — but the direction is clear: slot management absence is the most likely driver, though association isn't proof.

**Notebooks:** `08_kpis_operacionais_2025` · `12_testadia_vessel_segment_2025`

#### 2 — The Feeder Max segment is highly concentrated; the Brazilian market overall is not

Within the Feeder Max class (1k–3k TEU), CMA CGM holds 68.9% of deployed capacity, giving a segment HHI of 5,480 — highly concentrated by DOJ/FTC thresholds.

This concentration is intra-segment only. Across the full Brazilian container market, the 8 carriers analysed are distributed with no single dominant player (COSCO 22.5%, MSC 21.5%, MAERSK 15.3%, CMA CGM 12.6%, etc. by global TEU).

Within Feeder Max, CMA CGM is also the most efficient operator: 75h median TEstadia versus 104h for the rest of the segment. Whether efficiency comes from network design (dedicated windows, call-size tuning) or from route concentration itself is an open question.

**Notebook:** `07_market_power_feeder`

#### 3 — No carrier allocates more than 12% of its registered fleet to Brazil

Measured as unique vessels calling Brazil at least once in 2025, divided by total registered fleet:

| Carrier | Registered fleet | Vessels in Brazil | % |
|---|---|---|---|
| EVERGREEN | 142 | 17 | **12.0%** |
| MSC | 220 | 19 | 8.6% |
| MAERSK | 261 | 21 | 8.0% |
| COSCO | 335 | 25 | 7.5% |
| Hapag-Lloyd | 100 | 6 | 6.0% |
| CMA CGM | 231 | 13 | 5.6% |
| ZIM | 31 | 1 | 3.2% |
| ONE | 58 | 1 | 1.7% |

The 12% ceiling is low given UNCTAD's 8.7% South-South trade growth in 2024 (RMT 2025, Ch. I) and Brazil's share of global container trade. The gap between registered fleet and Brazil deployment is where the commercial opportunity sits for any carrier willing to push capacity here.

**Caveat:** measured in unique vessels, not TEU-weighted. A TEU-weighted version may change the ranking.

**Notebook:** `10_presenca_operacional_carrier_2025`

#### 4 — Berth occupancy correlates with port stay across the 9-port sample

Spearman ρ = 0.82 (point estimate) between average berth occupancy rate and median TEstadia, across 9 ports — São Francisco do Sul excluded as a structural bulk-grain outlier (240h TEstadia, not representative of a container-typical port).

With n = 9, the 95% bootstrap confidence interval is wide: [0.23, 1.00]. Leave-one-out ranges between 0.74 and 0.98 depending on which port is removed. The pattern is consistent with a positive relationship, but the small sample precludes narrow uncertainty bounds.

The clearest saturation case is Paranaguá — 77% occupancy, 98h median TEstadia. The most interesting counter-example is Suape (65.7% occupancy, 54.6h TEstadia): high utilisation without saturation penalty, suggesting that the relationship is modulated by factors beyond occupancy alone (berth scheduling discipline, vessel mix, pre-arrival coordination).

**See robustness analysis:** [`outputs/figures/nb15_03_bootstrap_loo.png`](outputs/figures/nb15_03_bootstrap_loo.png)
**Notebooks:** `13_ocupacao_bercos_2025` · `15_robustez_correlacao_ocupacao_testadia`

---

## Methodology and definitions

Each headline number has a defined formula, source column, filter, and reference notebook in [`docs/definitions.md`](docs/definitions.md). Start there if you want to reproduce a specific value or cross-check it against another source.

### Short version of the most sensitive choices (foundational study)

- **TEstadia** = `Data Desatracação` – `Data Chegada`. Includes pre-berth wait, berth dwell before operation, operation itself, and post-operation wait. It is the port-reported view, not an AIS-derived one.
- **Pre-berth wait** = `Data Atracação` – `Data Chegada`. Subject to port-reporting quality; not AIS-validated.
- **Feeder Max** = 1k–3k TEU capacity. Segment-defined, not port-defined. HHI and CMA CGM share are within-segment.
- **Fleet allocation** is unique-vessel count, not TEU-weighted.
- **UNCTAD 10.9h benchmark** is AIS-derived. The 2.1× ratio is order-of-magnitude, not strictly homogeneous.
- **Correlation sample is n = 9.** Point estimate is ρ = 0.82; uncertainty is disclosed in bootstrap CI and leave-one-out.

For methodology specific to each new post (Post 8 onwards), see the methodology file inside each post folder.

---

## What is NOT in this repository

Worth being explicit about where ANTAQ alone falls short.

**No AIS data.** Everything is static: registered fleet, port-reported timestamps, monthly aggregates. Ship-berth synchronisation analysis, true congestion events, and route-level deployment over time are not possible with this dataset. A follow-up using AIS would close most of the gaps below.

**Single year (2025).** No multi-year seasonality or trend confirmation. "Structural" claims are hypothesis, not proof — they would need 2023 and 2024 data to anchor properly.

**No tariff or revenue.** Operational view only. Margin, price elasticity, and commercial terms are outside the dataset.

**No weather data.** ANTAQ records weather stoppages as a paralisação cause, but cannot separate structural congestion from weather-driven delay.

**No foreign-side performance.** Origin and destination ports appear as strings. No matching European, North-American or Asian data is merged, so Brazil's relative position cannot be placed inside a lane-level comparison.

**n = 9 for the occupancy / TEstadia correlation.** Point estimate holds up but the confidence interval is wide — that's what a 9-port sample gives you.

All limitations are also declared per-notebook and per-post.

---

## Data sources

| Source | Content | Volume |
|---|---|---|
| [ANTAQ Open Data](https://web3.antaq.gov.br/ea/sense/download.html) | Berthing, operations, stoppages 2023–2025 | 316,850 berthing records |
| ANTAQ | Occupancy rates 2025 | berth-level monthly |
| [ComexStat / MDIC](https://comexstat.mdic.gov.br/) | Trade flows 2023–2025 | by NCM, UF, partner |
| [UNCTAD RMT 2025](https://unctad.org/publication/review-maritime-transport-2025) | Benchmarks | time in port, LSCI, fleet |
| [World Bank CPPI 2023](https://www.worldbank.org/en/topic/ports/brief/the-container-port-performance-index) | Container port performance | 398 ports global |

Raw data files are not versioned (~4.5 GB). Reproducing the analysis requires downloading ANTAQ SGMM and ComexStat exports.

---

## Repository structure

```
brazilian-maritime-analysis-2025/
│
├── README.md                       ← you are here (portfolio hub)
├── LICENSE                         ← MIT
├── requirements.txt
├── .gitignore
│
├── posts/                          ← case studies organised by LinkedIn post
│   └── post08-china-brazil/
│       ├── README.md
│       ├── methodology.md
│       ├── data/
│       ├── scripts/
│       ├── outputs/
│       └── docs/
│
├── docs/                           ← foundational study documentation
│   └── definitions.md              ← operational definition of every headline number
│
├── notebooks/                      ← foundational study notebooks
│   ├── 01_diagnostico_dados.ipynb  ← data quality and inventory
│   ├── 07_market_power_feeder.ipynb           ← finding #2
│   ├── 08_kpis_operacionais_2025.ipynb        ← finding #1
│   ├── 10_presenca_operacional_carrier_2025.ipynb  ← finding #3
│   ├── 13_ocupacao_bercos_2025.ipynb          ← finding #4
│   ├── 15_robustez_correlacao_ocupacao_testadia.ipynb  ← robustness test for #4
│   └── (16 notebooks total — see notebooks/README.md)
│
├── scripts/                        ← reusable scripts
│   └── robustness_bootstrap_loo.py ← bootstrap CI + leave-one-out
│
├── outputs/                        ← foundational study outputs
│   ├── figures/                    ← generated charts
│   └── processed_data/             ← intermediate CSVs
│
└── antaq_inventario.py             ← ANTAQ data inventory utility
```

---

## Reproducibility

```bash
pip install -r requirements.txt
# Place raw ANTAQ and ComexStat files in their target folders (see structure above)
# For foundational study: run notebooks in numerical order
# For Post 8: cd posts/post08-china-brazil && python scripts/post8_china_brazil_analysis.py
```

**Stack:** Python 3.10+ · Pandas · NumPy · SciPy · Matplotlib · Seaborn · Jupyter.

---

## Author

**Hugo Pedro** — Senior maritime logistics and supply chain analytics professional. 17+ years in international shipping and multimodal logistics across Angola, Mozambique and Brazil, with extensive carrier negotiations and performance reporting experience.

**Full profile and contact:** [linkedin.com/in/hugopedro](https://www.linkedin.com/in/hugopedro/)

This repository is a public case study portfolio for container shipping lines, freight forwarders, port operators, and trade analysts evaluating Brazil commercial and operational strategy.

Feedback, challenges, and corrections welcome via issues or pull requests.

---

## License

MIT — see [LICENSE](LICENSE).
