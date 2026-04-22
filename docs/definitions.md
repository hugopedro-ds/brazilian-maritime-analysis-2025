# Definições Operacionais — Métricas do Post LinkedIn e README

Este documento fixa a definição exacta, a fonte, os filtros e o notebook de origem de cada
número citado no post de LinkedIn e no README principal. Existe para que qualquer leitor
técnico (shipping line, analista, académico) possa reproduzir cada afirmação sem ambiguidade
e para blindar o projecto contra questionamento sobre metodologia.

**Janela temporal:** ano civil 2025 (01-jan-2025 a 31-dez-2025), dados ANTAQ abertos.
**Base geográfica:** portos brasileiros informantes à ANTAQ.
**Unidade de observação base:** atracação (registo único `IDAtracacao`).

---

## 1. Escopo — 22.746 deep sea port calls

**Valor reportado:** 22.746 atracações.

**Definição:**
Atracações no conjunto de dados `2025_Atracacao.csv` com o filtro
`Tipo de Navegação da Atracação == "Longo Curso"`.

**Colunas ANTAQ usadas:**
- `IDAtracacao` (chave única)
- `Tipo de Navegação da Atracação` (filtro)
- `Ano` (filtro = 2025)

**Nota interpretativa:**
"Longo Curso" na nomenclatura ANTAQ corresponde ao conceito internacional de *deep sea*
(navegação de longo percurso internacional). Inclui todos os tipos de operação
(movimentação de carga, passageiro, abastecimento, etc.), não apenas contentores.

**Notebook de referência:** `01_diagnostico_dados.ipynb`, `08_kpis_operacionais_2025.ipynb`.

---

## 2. TEstadia mediana em Longo Curso — 84h

**Valor reportado no post:** "84 hours median port stay in deep sea calls"
(variação no README: 83h; ambos são aproximações da mediana do conjunto LC completo).

**Definição:**
Mediana da coluna `TEstadia` (em horas) do dataset `2025_Tempos_Atracacao.csv`,
filtrado para `Tipo de Navegação == "Longo Curso"` via join com `2025_Atracacao.csv`
pela chave `IDAtracacao`.

**Definição do intervalo temporal TEstadia:**
TEstadia = `Data Desatracação` − `Data Chegada` (tempo total do navio no porto,
desde a chegada à área portuária até à desatracação do berço). Inclui espera de
atracação, esperas dentro do berço e operação.

**Decomposição disponível** (notebook 08, 12):
- TEspera Atracação: tempo desde chegada até atracar
- TEspera Início Operação: tempo desde atracar até início de operação
- TOperacao: duração da operação
- TEspera Desatracação: tempo desde fim de operação até desatracar

**Benchmark de comparação (UNCTAD RMT 2025):** 10,9h de mediana em países em
desenvolvimento. **Limitação crítica:** UNCTAD usa definição própria de "time in port"
derivada de AIS; não é directamente comparável à TEstadia ANTAQ sem normalização. A
afirmação de "2,1x acima" deve ser lida como ordem de grandeza, não como comparação
estritamente homogénea.

**Notebook de referência:** `08_kpis_operacionais_2025.ipynb`, `12_testadia_vessel_segment_2025.ipynb`.

---

## 3. TEspera antes de atracar — 23h

**Valor reportado:** "23 happen before the vessel even berths" (23,2h no README).

**Definição:**
Mediana da coluna `TEsperaAtracacao` (em horas) no subset Longo Curso. Equivale a
`Data Atracação` − `Data Chegada`: tempo entre a chegada do navio à área portuária e
a primeira amarração no berço.

**Nota interpretativa:**
Este intervalo capta o tempo em fundeio ou em área de espera antes de ocupar
qualquer berço. É a métrica que reflecte a coordenação (ou ausência dela) entre navio
e janela de berço — o conceito de *slot management*.

**Limitação:**
ANTAQ regista `Data Chegada` informada pelo porto; não há validação com AIS. Se a
chegada for sub-reportada (ex. navio chega mas só é registado ao aproximar-se do
berço), a TEspera real é superior ao que os dados mostram. Direcção do enviesamento:
**subestima** a espera real.

**Notebook de referência:** `08_kpis_operacionais_2025.ipynb`, `09_fundeio_por_carrier_2025.ipynb`.

---

## 4. Concentração Feeder Max — CMA CGM 68,9% / HHI 5.480

**Valores reportados:**
- CMA CGM detém 68,9% da capacidade TEU no segmento Feeder Max
- HHI do segmento Feeder Max = 5.480 ("altamente concentrado")
- TEstadia mediana CMA CGM no segmento: 75h
- TEstadia mediana dos outros carriers no segmento: 104h

**Definição do segmento Feeder Max:**
Navios com capacidade entre 1.000 e 3.000 TEU, conforme classificação em
`Vessels_Master_Enriched.csv` (coluna `vessel_segment == "Feeder Max (1k-3k TEU)"`).

**Definição do share 68,9%:**
Soma de capacidade TEU dos navios Feeder Max operando no Brasil em 2025 por
carrier, dividida pelo total Feeder Max do universo analisado (8 carriers).

Fonte: `fleet_q4_feeder_mainliner.csv`.

Cálculo explícito:
- CMA CGM Feeder: 202.919 TEU
- Restantes (COSCO 0 + MSC 5.000 + MAERSK 4.690 + EVERGREEN 79.432 +
  Hapag-Lloyd 2.500 + ONE 0 + ZIM 0): 91.622 TEU
- Total segmento: 294.541 TEU
- Share CMA CGM: 202.919 / 294.541 = **68,9%**

**Definição do HHI = 5.480:**
Herfindahl-Hirschman Index intra-segmento, calculado como soma dos quadrados
dos shares percentuais de cada carrier no total TEU do segmento Feeder Max.
Interpretação DOJ/FTC: HHI > 2.500 = mercado altamente concentrado.
Fonte: `fleet_q3_hhi_segmento.csv`.

**Definição das 75h vs 104h:**
Fonte: `feeder_max_cma_cgm_2025.csv`.
- Feeder Max (todas as carriers): n=92, mediana TEstadia = 85,7h
- CMA CGM apenas: n=63, mediana TEstadia = 75,45h
- Sem CMA CGM: n=29, mediana TEstadia = 104,0h

**Limitação:**
HHI = 5.480 é métrica **intra-segmento Feeder Max, não do mercado brasileiro total**.
Ler como "CMA CGM domina o Brasil" é incorrecto — o país como um todo está
pulverizado por 8 carriers. A concentração só se manifesta dentro do nicho Feeder
Max (1k-3k TEU). Esta distinção tem de ficar clara em qualquer comunicação externa.

**Notebook de referência:** `07_market_power_feeder.ipynb`.

---

## 5. Nenhum carrier >12% da frota registada no Brasil

**Valor reportado:** "No carrier allocates more than 12% of its registered fleet to Brazil."

**Definição:**
Rácio `Navios_Atracaram_BR / Frota_Registada` por carrier. Ambas as medidas são em
contagem de navios únicos (não TEU). Fonte: `resumo_carrier_2025.csv`.

**Frota_Registada:** número de navios únicos listados como pertencentes ao carrier
no dataset `Vessels_Master_Enriched.csv` (frota global do carrier, não apenas Brasil).

**Navios_Atracaram_BR:** número de navios únicos (por IMO) do carrier com pelo
menos uma atracação no Brasil em 2025.

**Valores por carrier (2025):**
| Carrier | Frota Registada | Navios no Brasil | % |
|---|---|---|---|
| EVERGREEN | 142 | 17 | 12,0% |
| MSC | 220 | 19 | 8,6% |
| MAERSK | 261 | 21 | 8,0% |
| COSCO | 335 | 25 | 7,5% |
| Hapag-Lloyd | 100 | 6 | 6,0% |
| CMA CGM | 231 | 13 | 5,6% |
| ZIM | 31 | 1 | 3,2% |
| ONE | 58 | 1 | 1,7% |

Valor máximo: EVERGREEN com 12,0% exactos.

**Limitação:**
Métrica em contagem, não TEU — um carrier com poucos navios ULCV no Brasil pode ter
% baixa em contagem mas alta em capacidade efectivamente alocada. Para fins de
alocação comercial, a versão TEU-weighted seria mais precisa e deve ser adicionada.

**Notebook de referência:** `10_presenca_operacional_carrier_2025.ipynb`.

---

## 6. Correlação ocupação de berço × TEstadia — ρ = 0,817

**Valor reportado no post:** ρ = 0,817, p = 0,007, n = 9 portos.

**Definição:**
Correlação de Spearman (ρ) entre:
- `Taxa_Media_Pct`: taxa média de ocupação de berço do porto em 2025 (% do tempo
  em que o berço esteve ocupado)
- `TEstadia_Med`: TEstadia mediana em horas no porto para o conjunto de
  atracações relevantes

Fonte: `ocupacao_testadia_porto_2025.csv` (input) e
`robustez_correlacao_ocupacao_testadia.csv` (output).

**Valores dos 3 cenários de robustez (notebook 15):**
| Cenário | n portos | ρ TEstadia | p-value | Interpretação |
|---|---|---|---|---|
| A — Todos os portos | 10 | 0,855 | 0,002 | Robusta |
| B — Sem São Francisco do Sul | 9 | **0,817** | 0,007 | Robusta |
| C — Sem SFS e Paranaguá | 8 | 0,738 | 0,037 | Robusta (marginal) |

**Escolha do cenário reportado:**
O post e o README usam o cenário B. Justificação: São Francisco do Sul é um outlier
estrutural (TEstadia mediana = 240h, dominado por rotas Ásia-SFS com graneleiros
especializados, não representativo de porto contentor típico). A sua inclusão infla
ρ artificialmente.

**Declaração de transparência obrigatória:**
A correlação reportada (ρ = 0,817) é o valor **após remoção de SFS**. Isto deve ser
mencionado explicitamente em comunicações externas; caso contrário, induz leitura
de que o resultado é "bruto".

**Limitações:**
- n = 9 é amostra pequena. Mesmo com p < 0,01, intervalos de confiança são largos.
- Spearman mede associação monotónica, não causalidade.
- Correlação com ρ = 0,738 no cenário mais agressivo (sem 2 outliers) sugere a
  relação é real mas não excessivamente forte. Recomenda-se reportar os 3 cenários
  juntos em publicações técnicas.
- Falta intervalo de confiança bootstrap e análise leave-one-out sistemática
  (tarefa pendente — notebook 15 fará extensão).

**Notebook de referência:** `13_ocupacao_bercos_2025.ipynb` (cálculo de ocupação),
`15_robustez_correlacao_ocupacao_testadia.ipynb` (teste de robustez).

---

## 7. Benchmark UNCTAD RMT 2025 — 10,9h

**Valor reportado:** UNCTAD RMT 2025 cita 10,9h como mediana de tempo em porto
para países em desenvolvimento.

**Fonte:** UNCTAD, *Review of Maritime Transport 2025*, Capítulo IV.

**Limitação crítica — comparabilidade:**
UNCTAD calcula tempo em porto a partir de dados AIS globais (MarineTraffic /
UN Global Platform), não a partir de registos operacionais portuários. A definição
provável é: intervalo entre a primeira e a última mensagem AIS do navio dentro da
área portuária definida.

A TEstadia ANTAQ é reportada pelo porto com base em eventos administrativos
(`Data Chegada` informada, `Data Desatracação`). Estas duas métricas **não são
perfeitamente comparáveis**:

- AIS capta movimento físico; ANTAQ capta eventos reportados
- Área portuária AIS pode incluir zonas de fundeio extensas; ANTAQ pode começar
  a contar só na área mais próxima do berço
- Segmentação UNCTAD é "container ships" global; ANTAQ é "Longo Curso" todo

**Direcção provável do enviesamento:**
AIS tende a capturar janelas temporais mais longas (fundeio distante incluído),
o que sugere que a TEstadia ANTAQ poderia ser ainda mais elevada em comparação
directa. O rácio de 2,1x é, portanto, **cota inferior** — não sobrestimada.

**Recomendação:**
Em comunicações externas, acompanhar a comparação com a ressalva: "aproximação
de ordem de grandeza; metodologias de medição diferem".

---

## Metadados comuns

**Fonte de todos os dados ANTAQ:** https://www.gov.br/antaq/pt-br/acesso-a-informacao/dados-abertos
(acesso em 2026).

**Ficheiros principais usados:**
- `2025_Atracacao.csv` (atracações 2025)
- `2025_Tempos_Atracacao.csv` (tempos por atracação)
- `2025_Tempos_Atracacao_Paralisacao.csv` (eventos de paralisação)
- `2025_Taxa_Ocupacao.csv` (taxa de ocupação de berços)
- `Vessels_Master_Enriched.csv` (enriquecimento de frota: segmento, TEU, LOA, beam)

**Reprodutibilidade:**
Todos os valores deste documento estão nos CSVs em `outputs/processed_data/`.
Para regenerar, correr os notebooks na ordem numérica.
