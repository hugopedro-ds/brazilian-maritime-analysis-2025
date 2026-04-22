# Inventário Completo de Datasets
**Projecto:** Sistema Portuário Brasileiro — ANTAQ  
**Data:** 2026-04-14  
**Total de ficheiros mapeados:** 53  

---

## GRUPO 01 — CADASTROS (Tabelas de Referência)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Relatorio_Instalacao_Portuaria.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 735  
Nº colunas: 4  
Período temporal coberto: atemporal (cadastro estático)  
Granularidade: por instalação portuária  
Fonte provável: ANTAQ  
COLUNAS:
- Código | object | 0% | BRAC002
- Nome da Instalação | object | 0% | Porto Fluvial de Cruzeiro do Sul
- Empresa | object | 0% | DEPARTAMENTO DE ESTRADAS DE RODAGEM
- Tipo | object | 0% | Registro - Instalação de apoio

QUALIDADE:
- % linhas completas: 100%
- Colunas com >20% missing: nenhuma
- Duplicatas: 0
- Inconsistências: nenhuma detectada

CRUZAMENTOS POSSÍVEIS:
- Pode cruzar com Atracacao via CDTUP (código da instalação)
- Pode cruzar com Relatorio_Berco via código de instalação

LIMITAÇÕES:
- Não contém dimensões físicas dos berços (LOA máx, calado, profundidade)
- Não tem dados históricos de capacidade

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Relatorio_Berco.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 875  
Nº colunas: 5  
Período temporal coberto: atemporal  
Granularidade: por berço  
Fonte provável: ANTAQ  
COLUNAS:
- Código do Berço | object | 0% | BRPA2145001
- Nome do Berço | object | 0% | Cais Flutuante - Berço 1
- Porto Organizado/Instalação Portuária | object | 0% | ABI Miritituba
- Instalação de Acostagem | object | 0% | ABI Miritituba
- Código Instalação de Acostagem | object | 1% | BRPA214

QUALIDADE:
- % linhas completas: 98.7%
- Colunas com >20% missing: nenhuma
- Duplicatas: 0
- Inconsistências: nenhuma detectada

CRUZAMENTOS POSSÍVEIS:
- Pode cruzar com Atracacao via IDBerco
- Pode cruzar com Taxa_Ocupacao via IDBerco

LIMITAÇÕES:
- Não contém restrições físicas (LOA máx, calado máx, profundidade) — dado crítico em falta

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Relatorio_Portos.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 25.565  
Nº colunas: 4  
Período temporal coberto: atemporal  
Granularidade: por porto (mundial)  
Fonte provável: ANTAQ  
COLUNAS:
- Bigrama do Porto | object | 0% | AF
- Trigrama do Porto | object | 0% | BIN
- Nome do Porto | object | 0% | Santos
- País | object | 0% | BRASIL

QUALIDADE:
- % linhas completas: 99.9%
- Duplicatas: 0

CRUZAMENTOS POSSÍVEIS:
- Pode cruzar com Carga via Origem/Destino (bigrama = 2 primeiros chars = país ISO)
- Pode cruzar com Instalacao_Destino via CDBigramaDestino

LIMITAÇÕES:
- Lista mundial, não só Brasil — precisa filtrar para análise doméstica

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Relatorio_Armador_Estrangeiro.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 4.788  
Nº colunas: 5  
Período temporal coberto: atemporal  
Granularidade: por armador  
Fonte provável: ANTAQ  
COLUNAS:
- Código Armador | object | 0% | ZA001051
- País | object | 0% | ÁFRICA DO SUL
- Apelido | object | 0% | GENERAL SHIPPING
- Nome | object | 0% | GENERAL SHIPPING SERVICES PTY LTD
- Ativo | object | 0% | Ativo

QUALIDADE:
- % linhas completas: 100%
- Duplicatas: 0

CRUZAMENTOS POSSÍVEIS:
- Potencial cruzamento com Atracacao via armador (campo não existe directamente na Atracação — chave fraca)

LIMITAÇÕES:
- Não tem chave directa com Atracacao. Ligação por nome do armador é frágil (variações de grafia)

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Relatorio_Embarcação_Estrangeira.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 29.844  
Nº colunas: 11  
Período temporal coberto: atemporal  
Granularidade: por embarcação  
Fonte provável: ANTAQ  
COLUNAS:
- ID Embarcação | int64 | 0% | 10719
- Nome da Embarcação | object | 0% | 29KIM
- IMO | float64 | 1% | 11134
- Tipo da Embarcação | object | 0% | CARGA GERAL
- País | object | 0% | AFEGANISTÃO
- IRIN | object | 37% | ICKU
- Ano Construção | float64 | 38% | 2007
- Arqueacao Bruta | object | 20% | 161175
- TPB | object | 18% | 200
- Tipo de Navegação | object | 2% | Não Informado
- Situação da Embarcação | object | 16% | Em Operação

QUALIDADE:
- % linhas completas: 57.7%
- Colunas com >20% missing: IRIN (37%), Ano Construção (38%)
- Duplicatas: 0

CRUZAMENTOS POSSÍVEIS:
- Pode cruzar com Atracacao via IMO (Nº do IMO — mas IMO é 49% nulo na Atracação)
- Pode cruzar com Vessels_Master via IMO

LIMITAÇÕES:
- Não tem LOA, beam, calado — inutilizável para análise de restrições físicas
- Sem TEU capacity — não substitui Vessels_Master para análise de shipping lines

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Relatorio_Mercadoria.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 1.402 | Nº colunas: 4 | Completas: 100% | Duplicatas: 0  
Granularidade: por código SH4 (Nomenclatura Aduaneira)  
COLUNAS: Código SH2, Descrição SH2, Código SH4, Descrição SH4  
CRUZAMENTOS: Carga via CDMercadoria → CDNCMSH2  
LIMITAÇÕES: tabela de referência estática; sem dados de volume

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Vessels_Master.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 1.378  
Nº colunas: 9  
Período temporal coberto: 2023–2025 (navios únicos que escalaram o Brasil)  
Granularidade: por navio (IMO único)  
Fonte provável: produzido internamente a partir de Atracacao  
COLUNAS:
- NÚMERO IMO | int64 | 0% | 9839131
- SHIPPING LINE | object | 0% | CMA CGM
- NOME DO NAVIO | object | 0% | CMA CGM CHAMPS ELYSEES
- CAPACIDADE (TEU) | int64 | 0% | 23112
- N_REGISTOS_ORIGINAIS | int64 | 0% | 1
- NOMES_UNICOS | int64 | 0% | 1
- LINHAS_UNICAS | int64 | 0% | 1
- TEUS_UNICOS | int64 | 0% | 1
- QUALIDADE_REGISTO | object | 0% | ALTA

QUALIDADE:
- % linhas completas: 100%
- Duplicatas: 0
- Inconsistências: nenhuma detectada

CRUZAMENTOS POSSÍVEIS:
- Cruzamento principal com Vessels_Master_Enriched via NÚMERO IMO
- Cruzamento com Atracacao via Nº do IMO (limitado: 49% nulo na Atracação)

LIMITAÇÕES:
- Apenas navios de shipping lines de contentores — sem outros tipos de carga
- Sem dimensões físicas (LOA, beam, calado)

---

## GRUPO 02 — OPERAÇÕES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: 2023_Atracacao.csv / 2024_Atracacao.csv / 2025_Atracacao.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 93.918 / 106.834 / 116.098  
Nº colunas: 29 (idêntico nos 3 anos)  
Período temporal coberto: Jan 2023–Dez 2025 (dados 2025 vão até Nov)  
Granularidade: por evento de atracação  
Fonte provável: ANTAQ — sistema SGMM  
COLUNAS PRINCIPAIS:
- IDAtracacao | int64 | 0% | chave primária
- CDTUP | object | 0% | código da instalação portuária (ex: BRSAS)
- IDBerco | object | 0% | código do berço
- Porto Atracação | object | 0% | nome do porto
- Data Atracação | object | 0% | 09/09/2023 14:55:00
- Data Chegada | object | 0% | 09/09/2023 14:00:00
- Data Desatracação | object | 0% | 11/09/2023 14:20:00
- Data Início Operação | object | 5–8% | 09/09/2023 15:05:00
- Data Término Operação | object | 5–8% | 11/09/2023 14:00:00
- Tipo de Operação | object | 0% | Marinha / Longo Curso / Cabotagem
- Tipo de Navegação da Atracação | object | 0% | Cabotagem
- Terminal | object | 0% | Cais Comercial
- Município / UF / Região Geográfica | object | 0% | contexto geográfico
- Nº do IMO | float64 | **49%** | 9482263
- Nº da Capitania | object | 36–37% | 211009059
- Apelido Instalação Portuária | object | 68–71% | nome alternativo
- Região Hidrográfica | object | 54–56% | Atlântico Sul

QUALIDADE:
- % linhas completas: 0.4–0.6% (arrasta pela combinação de nulos em IMO + Região Hidrográfica + Apelido)
- Colunas com >20% missing: Apelido (68–71%), Região Hidrográfica (54–56%), Nº Capitania (36–37%), **Nº IMO (49%)**
- Duplicatas: 0
- Inconsistências: Nº IMO com valor 0.0 contabilizado como preenchido — efectivamente mais de 49% são inutilizáveis

CRUZAMENTOS POSSÍVEIS:
- Cruzamento principal com Carga via IDAtracacao (chave 1:N)
- Pode cruzar com Tempos_Atracacao via IDAtracacao
- Pode cruzar com Vessels_Master via Nº IMO (limitado: 49% null)
- Pode cruzar com Relatorio_Berco via IDBerco
- Pode cruzar com Relatorio_Instalacao via CDTUP

LIMITAÇÕES:
- Nº IMO 49% nulo — impossível ligar a maioria das atracações a um navio específico
- "Tipo de Operação" inclui Apoio Marítimo, Marinha Militar, Offshore — mistura com operações comerciais
- Datas como string — precisam parse antes de qualquer cálculo temporal

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: 2023_Carga.csv / 2024_Carga.csv / 2025_Carga.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: **1.048.575 / 1.048.575 / 1.048.575** ⚠️ TRUNCADOS  
Nº colunas: 27 (idêntico nos 3 anos)  
Período temporal coberto: 2023 / 2024 / 2025 (parcial)  
Granularidade: por registo de carga dentro de uma atracação  
Fonte provável: ANTAQ  

> ⚠️ **ALERTA CRÍTICO:** Os 3 ficheiros têm exactamente 1.048.575 linhas — limite de linhas do Excel (2²⁰ - 1). Os dados reais são superiores. Volume real desconhecido.

COLUNAS PRINCIPAIS:
- IDCarga | int64 | 0% | chave primária
- IDAtracacao | int64 | 0% | chave estrangeira → Atracacao
- Origem / Destino | object | 6–7% | LOCODE (ex: BRSAS, KRPUS)
- CDMercadoria | object | 0% | código NCM/SH
- Tipo Operação da Carga | object | 0% | Longo Curso Exportação
- Natureza da Carga | object | 0% | Carga Geral / Granel Sólido
- ConteinerEstado | object | **22–26%** | Cheio / Vazio
- FlagConteinerTamanho | object | **21–25%** | 20 / 40
- TEU | object | 0% | valor numérico em string
- QTCarga | int64 | 0% | quantidade
- VLPesoCargaBruta | object | 0% | peso em string com vírgula decimal
- Sentido | object | 0% | Embarcados / Desembarcados
- Percurso Transporte Interiores | object | 84–87% | percurso fluvial
- Percurso em vias Interiores | object | 93–95% | detalhamento fluvial

QUALIDADE:
- % linhas completas: 0.6–1.3% (arrasta por colunas de contentores e percurso interior)
- Colunas com >20% missing: ConteinerEstado (22–26%), FlagConteinerTamanho (21–25%), Percurso Interior (84–93%)
- Duplicatas: 0
- **TRUNCAMENTO:** cada ano tem exactamente 1.048.575 linhas — dados incompletos

CRUZAMENTOS POSSÍVEIS:
- Cruzamento principal com Atracacao via IDAtracacao
- Pode cruzar com Mercadoria via CDMercadoria
- Pode cruzar com Instalacao_Destino via Destino (LOCODE)
- Pode cruzar com Relatorio_Portos via Origem/Destino (bigrama = país)
- Pode cruzar com ComexStat via CO_NCM (mapeando CDMercadoria → NCM)

LIMITAÇÕES:
- **TRUNCAMENTO é o problema central:** análises de volume agregado estão subvalorizadas
- ConteinerEstado e FlagConteinerTamanho com 22–26% null — análise de contentores fica comprometida
- TEU e VLPesoCargaBruta em string — precisam conversão
- Percurso Interior inutilizável (84–93% null)

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: Vessels_Master_Enriched.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 1.378  
Nº colunas: 13  
Período temporal coberto: 2023–2025 (navios únicos)  
Granularidade: por navio (IMO único)  
Fonte provável: Vessels_Master + enriquecimento por web scraping  
COLUNAS:
- NÚMERO IMO | int64 | 0% | 9839131
- mmsi | float64 | **24%** | 228386800
- call_sign | object | **24%** | FLZF
- NOME DO NAVIO | object | 0% | CMA CGM CHAMPS ELYSEES
- SHIPPING LINE | object | 0% | CMA CGM
- vessel_type | float64 | **100%** | NULL ← inutilizável
- vessel_segment | object | 0% | Ultra Large (> 18k TEU)
- CAPACIDADE (TEU) | int64 | 0% | 23112
- dwt | float64 | **100%** | NULL ← inutilizável
- loa | float64 | **24%** | 399.0
- beam | float64 | **24%** | 61.0
- year_built | float64 | 14% | 2020
- flag | object | **24%** | France

QUALIDADE:
- % linhas completas: 0% (arrastado pelos campos 100% nulos)
- Colunas com >20% missing: vessel_type (100%), dwt (100%), mmsi/call_sign/loa/beam/flag (24%)
- Duplicatas: 0
- Inconsistências: ZIM NORFOLK LOA=661m (outlier — erro de dados)
- Os 335 registos com loa/beam null são exactamente os mesmos (mesmos navios)

CRUZAMENTOS POSSÍVEIS:
- Cruzamento com Vessels_Master via NÚMERO IMO (1:1)
- Cruzamento com Atracacao via Nº IMO (limitado: 49% null na Atracação)
- Cruzamento com vessels_scraping_final via IMO

LIMITAÇÕES:
- DWT e vessel_type 100% nulos — calado e tipo de navio indisponíveis
- 24% dos navios sem LOA/beam — análise de restrições físicas incompleta
- Frota registada, não deployment real — sem dados AIS

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: vessels_scraping_final.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 3.499  
Nº colunas: 52  
Granularidade: por navio (IMO)  
Fonte provável: web scraping (MarineTraffic ou similar)  
COLUNAS ÚTEIS:
- IMO | int64 | 0% | chave
- Length Overall (m) | object | 0% | 183.28
- Beam (m) | object | 0% | 32.25
- Deadweight (t) | float64 | 0% | 47470
- Gross Tonnage | float64 | 0% | 28068
- Year of Build | float64 | 0% | 2006
- Current draught | object | 0% | 11.6 m
- AIS Type / Ship Type | object | 0% | Oil Products Tanker

QUALIDADE:
- % linhas completas: 0% (31 colunas com >20% null)
- Colunas críticas com >80% missing: Draught (93%), Length BP (86%), Engine Builder (89%), Registered Owner (100%)
- Inconsistências: Course/Speed 100% null

CRUZAMENTOS POSSÍVEIS:
- Cruzamento com Vessels_Master_Enriched via IMO — pode preencher LOA/beam em falta
- 3.499 navios vs 1.378 no Vessels_Master — universo maior, inclui não-contentores

LIMITAÇÕES:
- 3.499 navios incluem tipos não-conteineres (tankers, bulk, etc.) — precisa filtrar
- Dados de scraping têm qualidade variável
- **Oportunidade não explorada:** cruzar com Vessels_Master_Enriched para preencher os 335 nulos em LOA/beam

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASETS DERIVADOS (produzidos internamente)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Ficheiro | Linhas | Nota |
|---|---|---|
| vessels_master_clean.csv | 1.905 | Vessels_Master antes de deduplicação — 527 registos a mais |
| vessels_master_gold.csv | 1.378 | Idêntico ao Vessels_Master.csv — redundante |
| exportacao_detalhe_brasil.csv | 50.000 | **92% duplicatas** — extract de Carga, truncado e com alta redundância |
| importacao_detalhe_brasil.csv | 50.000 | **85% duplicatas** — mesmo problema |
| top_destinos_brasil.csv | 1.070 | Agregado de destinos por frequência — útil mas derivado |
| top_origens_brasil.csv | 958 | Agregado de origens — útil mas derivado |
| df_santos_enriquecido.csv | 109 | Santos específico, muito pequeno, 90% missing em campos VesselFinder |
| CPPI_Brasil_2023.csv | 8 | 8 portos brasileiros com CPPI — derivado de CPPI_2020_2024 |
| KPIs_Terminais_2025.csv | 12 | KPIs de 12 terminais contentores — origem indeterminada |
| Terminais_Conteiner_Brasil.csv | 12 | Capacidade/infra de 12 terminais — origem indeterminada |

---

## GRUPO 03 — INDICADORES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: 2025_Tempos_Atracacao.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 116.098  
Nº colunas: 7  
Período: 2025 (espelha exactamente o número de atracações de 2025)  
Granularidade: por atracação  
Fonte provável: ANTAQ — cálculos SGMM  
COLUNAS:
- IDAtracacao | int64 | 0% | chave → Atracacao 2025
- TEsperaAtracacao | object | 0% | 11.55 (horas, vírgula decimal)
- TEsperaInicioOp | object | 0% | 0.016
- TOperacao | object | 0% | 0.066
- TEsperaDesatracacao | object | 0% | 0.033
- TAtracado | object | 0% | 0.116
- TEstadia | object | 0% | 11.666

QUALIDADE:
- % linhas completas: 100%
- Duplicatas: 0
- Todos os tempos em horas (vírgula decimal — precisa replace(',','.') antes de float())

CRUZAMENTOS POSSÍVEIS:
- Cruzamento com Atracacao 2025 via IDAtracacao — permite análise de KPIs operacionais por porto/terminal/navio

LIMITAÇÕES:
- Apenas 2025 — sem equivalente para 2023/2024 (ficheiros não existem na pasta)
- Não tem identificação do terminal directamente — precisa join com Atracacao

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: 2025_Tempos_Atracacao_Paralisacao.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 228.249  
Nº colunas: 5  
Granularidade: por evento de paralisação dentro de uma atracação  
Fonte provável: ANTAQ  
COLUNAS:
- IDTemposDescontos | int64 | 0% | PK
- IDAtracacao | int64 | 0% | FK → Atracacao
- DescricaoTempoDesconto | object | 0% | "Sem operação por conveniência do operador"
- DTInicio | object | 0% | 2025-10-16 09:55:00
- DTTermino | object | 0% | 2025-10-16 10:19:00

QUALIDADE: 100% completo | 0 duplicatas

CRUZAMENTOS POSSÍVEIS:
- Join com Atracacao + Tempos_Atracacao via IDAtracacao — permite calcular taxa não-operacional real

LIMITAÇÕES:
- Apenas 2025
- Duração da paralisação precisa ser calculada (DTTermino - DTInicio)

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASETS: 2025_Taxa_Ocupacao.csv / _Com_Carga / _TO_Atracacao**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 325.945 / 325.945 / 349.305  
Granularidade: por berço por dia  
Colunas: IDBerco, Dia, Mês, Ano, TempoEmMinutos  
Qualidade: 100% completo  
CRUZAMENTOS: via IDBerco → Relatorio_Berco, Atracacao  
LIMITAÇÕES: apenas 2025; em minutos/dias (precisa normalização); sem identificação de terminal directamente

---

## GRUPO 04 — BENCHMARK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASET: CPPI_2020_2024.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: 403 (portos mundiais)  
Nº colunas: 18  
Período: 2020–2024  
Granularidade: por porto por ano  
Fonte provável: World Bank — Container Port Performance Index  
COLUNAS PRINCIPAIS:
- Port, LOCODE, Territory, World Bank Region
- CPPI 2020/2021/2022/2023/2024 (ranking global)
- Berth hours in % of port hours, Statistical Index, Administrative Index

QUALIDADE:
- % linhas completas: 77.4%
- CPPI 2020: 20% missing (portos sem dados históricos)
- Duplicatas: 0

CRUZAMENTOS POSSÍVEIS:
- Pode cruzar com CPPI_Brasil_2023 via nome do porto
- Pode cruzar com Relatorio_Portos via LOCODE

LIMITAÇÕES:
- Ranking ordinal, não métrica de performance absoluta
- Metodologia CPPI muda entre edições — comparação inter-anual requer cautela

---

**DATASETS UNCTAD (US_*.csv):**

| Dataset | Linhas | Cobertura | Utilidade |
|---|---|---|---|
| US_LSCI.csv | 14.470 | 2006–presente, por país/trimestre | LSCI — conectividade marítima Brasil |
| US_PLSCI.csv | 73.191 | 2006–presente, por porto/trimestre | PLSCI Santos, Paranaguá |
| US_ContPortThroughput.csv | 2.786 | 2010–presente, por país/ano | Volume TEU Brasil vs mundo |
| US_PortCalls.csv | 1.197 | 2018–presente, por país | Escala de navios no Brasil |
| US_MerchantFleet.csv | 62.228 | 1980–presente, por país/tipo | Frota sob bandeira brasileira |
| US_PortCallsArrivals.csv | — | variável | Chegadas de navios |
| US_SDG_LULFRG.csv | — | SDG 17 | Frete — métrica de desenvolvimento |
| US_SDG_PORFVOL.csv | — | SDG — volume portuário | TEU por país |
| US_VesselValueByRegistration.csv | — | valor de frota por bandeira | % frota mundial |

LIMITAÇÕES comuns: colunas "Footnote" e "Missing value" 100% nulas — devem ser excluídas; dados são ao nível de país, não de porto individual (excepção: US_PLSCI)

---

## GRUPO 05 — CLASSIFICAÇÕES AUXILIARES

| Dataset | Linhas | Chave | Uso |
|---|---|---|---|
| Mercadoria.csv | 1.403 | CDMercadoria → Carga | Descrição de mercadorias SH2/SH4 |
| Mercadoria_Conteinerizada.csv | 1.296 | CDMercadoriaConteinerizada | Mercadorias específicas de contentores |
| Instalacao_Destino.csv | 5.271 | Destino (LOCODE) → Carga | Nome e país de destinos/origens |

Instalacao_Destino tem CDTUPDestino com **95% missing** — não serve para ligar a instalações portuárias brasileiras.

---

## GRUPO 07 — COMEXSTAT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DATASETS: EXP_2023/2024.csv e IMP_2023/2024.csv**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nº linhas: EXP_2023=1.56M | EXP_2024=1.60M | IMP_2023=2.09M | IMP_2024=2.27M  
Nº colunas: 11 (exp) / 13 (imp)  
Período: 2020–2025 (há ficheiros de 2020 a 2025 na pasta, mas apenas 2023/2024 foram verificados)  
Granularidade: por transação NCM × mês × país × UF  
Fonte provável: MDIC / ComexStat  
COLUNAS:
- CO_ANO, CO_MES | int64 | 0% | período
- CO_NCM | int64 | 0% | código produto NCM 8 dígitos
- CO_PAIS | int64 | 0% | código país
- SG_UF_NCM | object | 0% | UF de origem/destino
- CO_VIA | int64 | 0% | modal (4=marítimo)
- QT_ESTAT | int64 | 0% | quantidade estatística
- KG_LIQUIDO | int64 | 0% | peso líquido kg
- VL_FOB | int64 | 0% | valor FOB USD
- VL_FRETE | int64 | 0% | (só importação) frete USD
- VL_SEGURO | int64 | 0% | (só importação) seguro USD

QUALIDADE:
- % linhas completas: 100%
- Duplicatas: 0

CRUZAMENTOS POSSÍVEIS:
- Pode cruzar com Carga via NCM (CDMercadoria → CDNCMSH2 → CO_NCM com mapeamento)
- CO_VIA=4 filtra modal marítimo — compatível com ANTAQ
- Pode adicionar dimensão de valor (USD FOB) que o ANTAQ não tem

LIMITAÇÕES:
- Granularidade por NCM × UF × país, não por porto específico
- Sem identificação do porto de embarque/desembarque directamente
- VL_FOB e VL_FRETE em inteiros (sem decimais) — perda de precisão em pequenos valores
- Não tem 2025 completo verificado

---

## TABELA RESUMO — CLASSIFICAÇÃO FINAL

| # | Dataset | Linhas | Colunas | % Completas | Classificação |
|---|---|---|---|---|---|
| 1 | 2023_Atracacao | 93.918 | 29 | 0.6% | **UTILIZÁVEL COM RESSALVAS** |
| 2 | 2024_Atracacao | 106.834 | 29 | 0.4% | **UTILIZÁVEL COM RESSALVAS** |
| 3 | 2025_Atracacao | 116.098 | 29 | 0.4% | **UTILIZÁVEL COM RESSALVAS** |
| 4 | 2023_Carga | 1.048.575 | 27 | 1.3% | **INCOMPLETO** (truncado) |
| 5 | 2024_Carga | 1.048.575 | 27 | 0.6% | **INCOMPLETO** (truncado) |
| 6 | 2025_Carga | 1.048.575 | 27 | 0.9% | **INCOMPLETO** (truncado) |
| 7 | Vessels_Master | 1.378 | 9 | 100% | **COMPLETO** |
| 8 | Vessels_Master_Enriched | 1.378 | 13 | 0% | **UTILIZÁVEL COM RESSALVAS** |
| 9 | vessels_scraping_final | 3.499 | 52 | 0% | **UTILIZÁVEL COM RESSALVAS** |
| 10 | 2025_Tempos_Atracacao | 116.098 | 7 | 100% | **COMPLETO** |
| 11 | 2025_Tempos_Paralisacao | 228.249 | 5 | 100% | **COMPLETO** |
| 12 | 2025_Taxa_Ocupacao | 325.945 | 5 | 100% | **COMPLETO** |
| 13 | CPPI_2020_2024 | 403 | 18 | 77.4% | **COMPLETO** |
| 14 | KPIs_Terminais_2025 | 12 | 8 | 100% | **COMPLETO** (pequeno) |
| 15 | Terminais_Conteiner_Brasil | 12 | 8 | 100% | **COMPLETO** (pequeno) |
| 16 | EXP_2023 / EXP_2024 | 1.56M / 1.60M | 11 | 100% | **COMPLETO** |
| 17 | IMP_2023 / IMP_2024 | 2.09M / 2.27M | 13 | 100% | **COMPLETO** |
| 18 | US_LSCI / US_PLSCI | 14k / 73k | variável | parcial | **UTILIZÁVEL COM RESSALVAS** |
| 19 | Relatorio_Instalacao | 735 | 4 | 100% | **COMPLETO** |
| 20 | Relatorio_Berco | 875 | 5 | 98.7% | **COMPLETO** |
| 21 | Relatorio_Portos | 25.565 | 4 | 99.9% | **COMPLETO** |
| 22 | Relatorio_Embarcação | 29.844 | 11 | 57.7% | **UTILIZÁVEL COM RESSALVAS** |
| 23 | Mercadoria | 1.403 | 6 | 99.5% | **COMPLETO** |
| 24 | exportacao_detalhe_brasil | 50.000 | 5 | 100% | **INCOMPLETO** (92% dups, truncado) |
| 25 | importacao_detalhe_brasil | 50.000 | 5 | 100% | **INCOMPLETO** (85% dups, truncado) |

---

## RESPOSTAS ÀS PERGUNTAS FINAIS

### 1. Que análises são possíveis com os dados disponíveis?

**Alta confiança:**
- KPIs operacionais de atracação (TEstadia, TEspera, TOperação) por porto/terminal/ano — dados ANTAQ completos
- Evolução de volumes de atracação 2023–2025 por porto, tipo de navegação, região
- Taxa de ocupação de berços (2025 apenas)
- Análise de frota por shipping line (TEU, vessel_segment, LOA, beam) com ressalva de 24% missing
- Ranking CPPI dos portos brasileiros e benchmark global 2020–2024
- LSCI/PLSCI Brasil — conectividade marítima por trimestre
- Comércio exterior por NCM × UF × país (ComexStat 2023–2024) com ligação modal marítimo

**Possível com ressalvas:**
- Rotas Origem–Destino via Carga × Instalacao_Destino — dados truncados e 6–7% null em Origem/Destino
- Análise por tipo de carga (Natureza da Carga) — truncamento compromete volumes absolutos
- Perfil físico de frota (LOA, beam) para análise de compatibilidade portuária — 24% missing

**Não possível com dados actuais:**
- Calado real de navios (DWT e Draught 93–100% nulos)
- Ligação directa navio → atracação para a maioria dos eventos (IMO 49% null na Atracação)
- Análise de routing real (AIS — não existe)
- Tempos operacionais para 2023/2024 (ficheiros Tempos_Atracacao apenas existem para 2025)

---

### 2. Que análises feitas podem estar comprometidas por missing data?

**NB02 — Eficiência de Terminais:**
- Baseado em Atracação + Carga. IMO 49% null na Atracação impede ligar escalas a navios específicos.
- Prancha (TEU/h) calculada sobre volumes de Carga truncados — subestimação sistemática.
- TEstadia e TEspera usam datas como strings — se o parse falhou em algum registo, os cálculos KPI ficam silenciosamente errados.

**NB03 — Evolução do Sistema:**
- Volumes de Carga truncados nos 3 anos — tendências de crescimento podem estar distorcidas se o truncamento é assimétrico (ex: 2025 tem mais registos reais que 2023, mas ambos foram cortados no mesmo limite).
- H4 (China 34.9%/39.3%) baseado em dados de rota com 6–7% null em Origem/Destino — participação real pode ser diferente.

**Fleet Analysis (NB04):**
- vessel_type 100% null — segmentação baseada só em TEU (vessel_segment derivado).
- DWT 100% null — calado indisponível, análise de restrições portuárias incompleta.
- 24% missing em LOA/beam concentrado em COSCO (29%) e CMA CGM (28.6%) — os dois maiores carriers têm maior incerteza.

**Port Compatibility (NB05):**
- Análise baseada apenas em LOA e beam. Sem calado, portos como Paranaguá (calado máx 13.5m) e Pecém (12m) podem ter restrições não capturadas.
- ZIM NORFOLK com LOA=661m (outlier) se não for detectado afecta métricas do ZIM.

---

### 3. Que dados estão em falta para completar o case study?

**Críticos (sem eles, análises centrais têm lacunas não colmatáveis):**

1. **Calado dos navios** — DWT e draught 100% nulos. Fonte para obter: IHS Markit / Clarksons / MarineTraffic API. Sem isto, port compatibility é análise parcial.
2. **Tempos de Atracação para 2023 e 2024** — só existe para 2025. Para comparação inter-anual de KPIs operacionais, estes ficheiros são indispensáveis.
3. **Ficheiros Carga sem truncamento** — os 3 anos estão cortados no limite Excel. O download directo via API ANTAQ ou portal web retorna o ficheiro completo.
4. **IMO nas Atracações** — 49% nulo impede ligar eventos de atracação a navios específicos. Parte do problema é estrutural (navios de apoio, marinha) mas a ligação para contentores devia ser possível.

**Importantes (melhorariam qualidade das análises):**

5. **Dimensões físicas dos berços** (LOA máx, calado máx) em Relatorio_Berco — actualmente não existem nessa tabela. Permitiriam substituir os limites estáticos por ANTAQ usados no NB05 por dados reais por berço.
6. **Atracacao 2020–2022** — para séries temporais mais longas. Actualmente o projecto cobre 3 anos.
7. **Taxa_Ocupacao e Tempos_Paralisacao para 2023 e 2024** — análise de tendência de eficiência operacional.
8. **vessels_scraping_final × Vessels_Master_Enriched** — cruzar os dois via IMO preencheria os 335 registos com LOA/beam nulos. Este cruzamento ainda não foi feito e é a solução mais imediata para melhorar o NB05.

**Desejáveis (ampliariam o scope do projecto):**

9. **Dados AIS** (posições de navios) — deployment real vs frota registada.
10. **Tarifas portuárias** por terminal — análise de custo operacional.
11. **Dados de congestão em tempo real** — fila de espera histórica por porto.

---

*Inventário gerado em 2026-04-14. Total: 53 ficheiros mapeados.*
