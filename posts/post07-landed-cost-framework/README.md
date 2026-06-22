# Post 7 — The landed-cost framework for Brazilian port selection

**Published on LinkedIn:** 18 June 2026
**Author:** Hugo Pedro — [linkedin.com/in/hugopedro](https://www.linkedin.com/in/hugopedro/)

## The thesis

In Brazil, port selection is a landed-cost decision — not just a logistics one. The "best" port often depends on tax math, not just freight cost or transit time. But fiscal optimization without accounting for **carrier optionality** can save tax today and cost negotiation leverage tomorrow.

## The chart

![Landed-cost equation: Tax benefit + Inland cost + Service reliability + Carrier optionality](outputs/post7_landed_cost.png)

## The framework

```
Tax benefit + Inland cost + Service reliability + Carrier optionality
                                 ↓
                  A real port-procurement decision
```

Four dimensions, four cost categories. Most procurement models in Brazil capture the first two well. The last two — service reliability and carrier optionality — are often under-priced or omitted entirely.

## Key concepts

### 1 — Brazilian port selection is structurally fiscal, not just logistical

Brazil has state-level ICMS incentive regimes — Santa Catarina, Espírito Santo and others have built decades of import incentives around their ports. The "best" port in Brazil is often the one where the **tax math works**, not the closest or fastest.

This is structurally different from markets where port selection is dominated by logistics economics. African ports I worked in (Luanda, Maputo, Beira, Nacala) often had a single terminal per port — no fiscal layer to optimise. In Brazil, the fiscal layer is the decisive one.

### 2 — But carrier optionality is being missed

Following [Post 6](../post06-port-concentration/), all 10 main Brazilian container terminals are at least moderately concentrated under DOJ/FTC 2010 HHI thresholds. **Choosing a port for fiscal reasons can also mean narrowing carrier optionality — without explicitly pricing that risk.**

A port can be fiscally attractive AND still reduce carrier optionality. What you save in tax today, you may pay later in carrier dependency and weaker negotiation leverage.

### 3 — The reform changes the time horizon

Brazil's 2023 tax reform (EC 132/2023) and Complementary Law 214/2025 phase down ICMS incentives from 2029, with full sunset by 2033. **The fiscal layer is in transition; the carrier-structure layer is not.**

Procurement teams modelling Brazil port decisions over a 5–10 year horizon need to weight these two layers differently than they have historically — the fiscal benefit erodes; the structural carrier dependency does not.

### 4 — Practical implication

For importers, freight forwarders, customs brokers and procurement teams modelling landed cost in Brazil: include carrier optionality as a risk factor, not just freight + tax + inland cost.

## Why this matters

Most landed-cost models in Brazilian ocean freight procurement use a 2–3 component equation: freight + duties + inland cost. This post argues for explicit inclusion of **service reliability and carrier optionality** as structural cost dimensions, particularly given Brazil's HHI port concentration profile.

## Repository structure (this post)

```
posts/post07-landed-cost-framework/
├── README.md                ← you are here
├── docs/
│   └── post_draft.md        ← LinkedIn post text (English)
├── scripts/
│   └── build_post7_image.py ← chart generation script
└── outputs/
    └── post7_landed_cost.png ← final chart
```

## Reproduce the chart

The chart is a framework visualisation (4 input chips + outcome chip + connector), generated programmatically:

```bash
python scripts/build_post7_image.py
```

Requires Python 3.10+ with matplotlib.

## Sources and context

- **EC 132/2023** — Brazil's constitutional amendment for tax reform
- **Complementary Law 214/2025** (Lei Complementar 214/2025) — implementing law for ICMS phase-down
- **Senate Resolution 13/2012** — 4% interstate ICMS on imports ("guerra dos portos")
- **State-level ICMS incentive regimes** — Santa Catarina (Pró-Emprego, TTD), Espírito Santo (FUNDAP legacy programs), and others
- **Post 6 of this repository** — HHI port concentration analysis, foundational input for the carrier-optionality dimension of the framework

## What this post does NOT claim

- That fiscal optimization is wrong. It is often commercially rational and remains legal until the ICMS phase-down completes.
- That a specific port is "better" than another. Port selection depends on the importer's cargo type, volumes, route structure, and risk tolerance.
- Anything about specific carriers' commercial terms or contracts.
- That the framework is exhaustive. Other dimensions (warehousing, customs clearance speed, hinterland infrastructure) matter too — these four are highlighted as the most-overlooked.

## Connection to other posts in this repository

- **[Post 6 — Port concentration (HHI)](../post06-port-concentration/)** — provides the empirical basis for the "carrier optionality" dimension
- **[Post 8 — Brazil-China trade asymmetry](../post08-china-brazil/)** — applies similar structural-asymmetry thinking to a specific bilateral lane

## Citation

> Pedro, H. (2026). Post 7 — The landed-cost framework for Brazilian port selection. GitHub case study, hugopedro-ds/brazilian-maritime-analysis-2025.
