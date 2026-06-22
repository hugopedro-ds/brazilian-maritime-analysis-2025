# Methodology — Post 8: Brazil-China trade asymmetry (2025)

## Scope

This analysis covers **bilateral container and bulk trade between Brazil and China in 2025**, restricted to **maritime mode only**. It excludes:

- Air freight (negligible in volume terms for both directions)
- Bonded transit through Brazilian customs offices not directly attached to a port
- Any non-Brazil/China origin or destination

## Data sources

Three ComexStat queries (Brazilian government open data) + one ANTAQ extract:

| Source | Query | Granularity | Rows | Purpose |
|---|---|---|---|---|
| ComexStat / MDIC 2025 | Brazil → China exports, by HS2 chapter | 89 chapters | 89 | Cargo composition (exports) |
| ComexStat / MDIC 2025 | China → Brazil imports, by HS2 chapter | 93 chapters | 93 | Cargo composition (imports) + freight/insurance/CIF data |
| ComexStat / MDIC 2025 | China → Brazil imports, by URF (port of customs) | 38 URFs | 38 | Port concentration of imports |
| ComexStat / MDIC 2025 | Brazil → China exports, by URF (port of customs) | 25 URFs | 25 | Port concentration of exports |
| ANTAQ 2025 (Atracação) | All vessel calls in Brazilian ports | 116,098 calls | (reference only) | Context for future carrier analysis (Post 9) |

All ComexStat queries filtered to **Via = MARÍTIMA** to exclude air, road, and inland transport.

## HS2 chapter classification (3-bucket framework)

Each HS2 chapter (Harmonized System, 2-digit) is classified into one of three structural categories based on stage of processing:

### Raw / commodities
Chapters dominated by extracted, grown, or minimally processed materials:
- 01-15 (live animals, meat, fish, dairy, eggs, vegetables, fruits, grains, oilseeds, vegetable oils)
- 25 (salt, sulphur)
- 26 (mineral ores)
- 27 (mineral fuels — oil, coal, natural gas)
- 31 (fertilizers)
- 41 (raw hides and skins)
- 44 (raw wood)
- 47 (pulp)

**Override applied:** HS 17 (sugar) treated as raw despite being technically semi-processed. Brazilian sugar exports to China are largely VHP (Very High Polarization) raw sugar destined for refining in destination — commodity-grade by shipping logic.

### Semi-processed / intermediate goods
Chapters dominated by intermediate manufacturing:
- 16-24 (prepared foods, beverages, tobacco — excluding sugar override)
- 28-30 (basic chemicals, pharmaceuticals)
- 32-38 (paints, soaps, photographic chemicals, perfumes, essential oils)
- 39-40 (plastics primary forms, rubber)
- 45-49 (cork, basket, paper, paper articles)
- 50-53 (raw textile fibers — silk, wool, cotton, vegetable fibers)
- 72 (iron and steel)
- 74-81 (copper, nickel, aluminum, lead, zinc, tin, other base metals)

### Finished goods / manufactured products
Chapters dominated by end-stage consumer or industrial products:
- 42-43 (leather goods, fur articles)
- 54-71 (textiles finished, clothing, footwear, stone, ceramic, glass, jewelry)
- 73 (iron/steel articles, fabricated)
- 82-83 (tools, hardware)
- 84-92 (machinery, electronics, vehicles, ships, aircraft, optical instruments, clocks)
- 93 (arms)
- 94-97 (furniture, toys, miscellaneous, art)

### Edge cases acknowledged

- **HS 11 (milling products — flour, starch):** classified as raw. Defensible as basic agri-derived commodity, though the boundary with semi-processed is debatable.
- **HS 23 (food residues — including soybean meal):** classified as semi. Brazilian soybean meal exports could be argued as commodity-grade, but the HS code groups multiple processed feed types.
- **HS 02 (meat) and HS 03 (fish/seafood):** classified as raw. Refrigerated/frozen containerized cargo, but commodity-grade by shipping economics.
- **Classification is a simplification.** Different analysts may classify ~10-15% of trade differently. The directional asymmetry holds under any reasonable classification because the dominant chapters (12, 26, 27 in exports; 84, 85, 87 in imports) are unambiguous.

## URF cleaning

URF = Unidade da Receita Federal (Brazilian customs unit). Not all URFs correspond to physical maritime ports — some are inland customs offices that process cargo arriving under bond from coastal ports.

### Blacklist applied to imports (CN → BR)

Removed 13 URFs identified as airports or interior customs offices:

| Code | Name | Reason |
|---|---|---|
| 0120200 | ANAPOLIS | Interior (Goiás) |
| 0610400 | JUIZ DE FORA | Interior |
| 0610600 | VARGINHA | Interior |
| 0617700 | ALF - BELO HORIZONTE | Interior |
| 0710251 | IRF CAMPOS DOS GOYTACAZES | Excluded from imports (no maritime import role); see exports note below |
| 0710300 | NOVA IGUACU | Interior |
| 0710500 | VOLTA REDONDA | Interior |
| 0811000 | SOROCABA | Interior |
| 0817700 | AEROPORTO INTERNACIONAL DE VIRACOPOS | Airport (despite Via=MARITIMA filter; likely bonded transit) |
| 0817900 | SAO PAULO | City customs, not port |
| 0917900 | ALF - CURITIBA | Interior |
| 1010600 | CAXIAS DO SUL | Interior |
| 1010700 | NOVO HAMBURGO | Interior |

Total FOB removed: **USD 85 million (0.14% of total imports)**. Effect on analysis: negligible.

### Blacklist applied to exports (BR → CN)

No URFs removed from exports. Exception preserved:

- **0710251 IRF CAMPOS DOS GOYTACAZES** is kept in the exports dataset. This URF processes the customs declaration for petroleum extracted from offshore platforms in the Bacia de Campos basin. The cargo is loaded at sea via FSO (Floating Storage and Offloading) or monobuoys. There is no conventional onshore port terminal, but the URF represents a legitimate maritime export route for ~7% of Brazil-China exports.

## HHI (Herfindahl-Hirschman Index)

For port concentration analysis, HHI is computed as:

```
HHI = Σ (market_share_in_percent)²
```

across all cleaned URFs.

### DOJ/FTC 2010 thresholds applied

- **HHI < 1,500** → Unconcentrated market
- **HHI 1,500-2,500** → Moderately concentrated
- **HHI > 2,500** → Highly concentrated

Note: The DOJ/FTC updated these thresholds in 2023 to 1,000 and 1,800 respectively. The 2010 thresholds are retained here for methodological consistency with prior posts (Post 6 used DOJ/FTC 2010 for carrier concentration).

### Results

- **Imports (CN → BR):** HHI = 2,078 — Moderately concentrated, near the upper threshold
- **Exports (BR → CN):** HHI = 1,603 — Moderately concentrated, just above the lower threshold

## US$ per tonne calculation

```
USD_per_tonne = FOB_USD / (kg / 1000)
```

Computed at the category level (raw / semi / finished) and at the aggregate level for each direction.

## Limitations declared

### Data quality flags

- **kg = 0 reporting:** Two export URFs (São Luís and Itaguaí, both Vale's iron-ore terminals) report FOB values without registered weight in the ComexStat extract used. The FOB values are valid and used in the analysis; kg-based metrics for these specific URFs are excluded. This appears to be a known ComexStat limitation for heavy bulk cargo in some periods.
- **URF Campos dos Goytacazes** processes offshore oil exports but is not a conventional port terminal. Anyone treating it as a port should note the offshore loading mechanism.

### Methodological boundaries

- **HS2 classification is a simplification.** A finer HS6 or HS8 classification would shift category boundaries for ~10-15% of trade. Direction of asymmetry would not change.
- **Single year (2025) scope.** No longitudinal trend analysis. Structural claims are inferred from one annual snapshot — defensible given the stability of Brazil-China trade composition over the prior decade, but not formally tested.
- **No carrier-level analysis.** This post does not include carrier deployment, vessel deployment, or service-level concentration. That dimension is reserved for Post 9, which requires enriched vessel data from sources beyond the included ANTAQ extract.
- **No transit-time or schedule reliability data.** AIS data is not used. Operational metrics (port stay, vessel turnaround, schedule reliability) are out of scope.
- **No tariff or revenue data.** Trade values are FOB (and CIF for imports). Margin, freight rates per TEU, and commercial terms are outside the dataset.
- **No weather or seasonality breakdown.** Annual aggregates only.

### What the post does NOT claim

- That HHI = 2,078 (imports) is necessarily "bad" or that ports should be deconcentrated. Concentration may reflect rational economic scale.
- That specialised export terminals are inefficient. They are specialised for legitimate operational reasons (cargo type, vessel compatibility).
- Anything about carriers, services, transit times, or freight rates — those are outside this analysis.

## Reproducibility

To reproduce the analysis from scratch:

1. **Pull ComexStat queries** from https://comexstat.mdic.gov.br/ with these parameters:
   - Period: 2025 January to December
   - País: China; Via: MARITIMA
   - Three queries: by HS2 chapter (exports and imports separately), and by URF for both directions
2. **Place CSVs** in `data/` with the exact filenames used by the scripts.
3. **Run the analysis script:**
   ```
   python scripts/post8_china_brazil_analysis.py
   ```
   This generates the cleaned datasets and HHI metrics in `outputs/`.
4. **Generate the chart:**
   ```
   python scripts/build_post8_chart.py
   ```
   This produces `outputs/post8_china_brazil_chart.png`.

Required Python libraries (in `requirements.txt`):
- pandas
- matplotlib
- numpy

Python 3.10 or higher recommended.

## Citation

If you use or reference this analysis, please cite:

> Pedro, H. (2026). Brazil-China trade asymmetry 2025: cargo composition and port concentration. GitHub case study, hugopedro-ds/brazilian-maritime-analysis-2025.

## Feedback

Methodology challenges, classification disputes, and corrections are welcome via GitHub issues or pull requests.
