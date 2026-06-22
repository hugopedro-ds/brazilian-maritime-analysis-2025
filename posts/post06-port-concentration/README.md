# Post 6 — Carrier concentration at Brazilian container ports (HHI)

**Published on LinkedIn:** 16 June 2026
**Author:** Hugo Pedro — [linkedin.com/in/hugopedro](https://www.linkedin.com/in/hugopedro/)

## The thesis

Brazilian container ports offer less carrier optionality than procurement models often assume. Across the 10 main container terminals, all sit at or above DOJ/FTC 2010 moderate-concentration thresholds — and 7 of 10 are highly concentrated.

## The chart

![Carrier concentration (HHI) by Brazilian container port](outputs/post6_hhi_chart.png)

## Key findings

### 1 — No Brazilian container port qualifies as competitive

Across the 10 main container terminals (ANTAQ 2025 deep-sea call data):

- **7 of 10 are highly concentrated** under DOJ/FTC 2010 thresholds (HHI > 2,500)
- **3 of 10 are moderately concentrated** (HHI 1,500–2,500)
- **0 fall in the unconcentrated range**

Under the stricter DOJ/FTC 2023 update (threshold 1,800), all 10 terminals would qualify as highly concentrated.

### 2 — The extremes set the picture

- **Fortaleza:** HHI 5,679 — CMA CGM holds 74% of identifiable calls (near-monopoly at terminal level)
- **Santos:** HHI 2,057 — Brazil's largest container gateway, also the least concentrated of the 10, yet still moderately concentrated

### 3 — Specialty ports are carrier-captured

At the most concentrated terminals — Fortaleza, Pecém, Portonave, Vila do Conde, Itapoá — a single carrier dominates the call pattern. Shipping through Fortaleza ≈ shipping with CMA CGM. Through Itapoá ≈ Maersk. Through Portonave ≈ Evergreen.

### 4 — Practical implication for procurement

Port selection cannot be separated from carrier optionality. The real question for shippers is not only "which port is cheaper?" but also "which port gives us real carrier optionality?"

## HHI by port

| # | Port | HHI | Top carrier | Top share |
|---|---|---|---|---|
| 1 | Fortaleza | 5,679 | CMA CGM | 74% |
| 2 | Pecém | 5,125 | MSC | 58% |
| 3 | Portonave | 4,489 | Evergreen | 63% |
| 4 | Vila do Conde | 4,256 | COSCO | 50% |
| 5 | Itapoá | 4,120 | Maersk | 61% |
| 6 | DP World Santos | 3,156 | Evergreen | 37% |
| 7 | Itajaí | 3,070 | Maersk | 39% |
| 8 | Paranaguá | 2,373 | Maersk | 38% |
| 9 | Rio de Janeiro | 2,112 | MSC | 36% |
| 10 | Santos | 2,057 | Maersk | 30% |

## Data source

**ANTAQ 2025 (Atracação)** — vessel call data, deep-sea (Longo Curso) container vessels with identifiable IMO numbers.

## Methodology

```
HHI = Σ (carrier_share_in_percent)²
```

Computed per port, based on identifiable deep-sea container calls in ANTAQ 2025.

**DOJ/FTC 2010 thresholds applied:**
- HHI < 1,500 → Unconcentrated
- HHI 1,500–2,500 → Moderately concentrated
- HHI > 2,500 → Highly concentrated

The 2010 thresholds are retained for consistency with shipping/logistics industry practice. The 2023 DOJ/FTC update lowered the bands to 1,000 / 1,800 — under that stricter framework, all 10 terminals would qualify as highly concentrated.

The foundational analysis behind these numbers is in the repo root: see `notebooks/` and `docs/definitions.md` for full methodology, including vessel identification, carrier mapping, and call-classification rules.

## Limitations

- **Call-based concentration, not TEU-weighted cargo share.** Measures operational carrier presence at the terminal (vessel calls), not actual booked container volume. A TEU-weighted concentration could differ — particularly at terminals where vessel sizes vary substantially by carrier.
- **Sample is 705 identifiable deep-sea container calls** in ANTAQ 2025 (3.1% of total Longo Curso atracações). Coverage depends on vessel IMO being identifiable in the Vessels_Master dataset. The top 10 ports analysed cover 73.5% of this identifiable subset.
- **2025 single-year snapshot.** Rotational changes by carriers (service reshuffles, alliance changes) may have shifted concentration before or after this period.
- **No causality claim.** Concentration may reflect carrier strategy, terminal partnership economics, or operational fit — not necessarily an "abnormal" market structure.

## Repository structure (this post)

```
posts/post06-port-concentration/
├── README.md                ← you are here
├── docs/
│   └── post_draft.md        ← LinkedIn post text (English)
├── scripts/
│   └── build_post6_hhi.py   ← chart generation script (data hardcoded from foundational study)
└── outputs/
    └── post6_hhi_chart.png  ← final chart
```

The underlying ANTAQ data and full analysis pipeline are in the foundational study at the repo root (`notebooks/`, `docs/definitions.md`).

## Reproduce the chart

The chart script is self-contained (HHI values and carrier shares hardcoded from the foundational analysis):

```bash
python scripts/build_post6_hhi.py
```

Requires Python 3.10+ with matplotlib and numpy.

## What this post does NOT claim

- That concentration is inherently bad. Carrier-terminal partnerships can deliver real operational benefits (dedicated windows, predictable scheduling, throughput efficiency).
- That shippers have no alternatives. Carriers offer multi-port options. The post is about **terminal-level** carrier optionality, not corridor-level.
- Anything about TEU volumes, freight rates, or container booking patterns.

## Citation

> Pedro, H. (2026). Post 6 — Carrier concentration at Brazilian container ports (HHI). GitHub case study, hugopedro-ds/brazilian-maritime-analysis-2025.
