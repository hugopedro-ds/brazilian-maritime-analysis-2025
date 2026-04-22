# -*- coding: utf-8 -*-
"""
Gera todos os gráficos do projeto ANTAQ e salva em outputs/figures/
Execute: py scripts/gerar_graficos.py
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 130
plt.rcParams["figure.figsize"] = (12, 5)

BASE = Path(r"C:\Users\hdped\Desktop\ANTAQ_Projeto")
FIG  = BASE / "outputs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  ANTAQ — Geração de Gráficos")
print("=" * 60)

# ── Carregamento ────────────────────────────────────────────
print("\n[1/4] Carregando atracações 2023–2025...")
atrac_frames = []
for ano in [2023, 2024, 2025]:
    df = pd.read_csv(
        BASE / "data" / "02_Operacoes" / f"{ano}_Atracacao.csv",
        sep=";", encoding="latin-1", low_memory=False
    )
    df["Ano_Arquivo"] = ano
    atrac_frames.append(df)
atrac = pd.concat(atrac_frames, ignore_index=True)
print(f"   {len(atrac):,} atracações carregadas")

# Tempos 2025
print("[2/4] Carregando tempos 2025...")
tempos = pd.read_csv(
    BASE / "data" / "03_Indicadores" / "2025_Tempos_Atracacao.csv",
    sep=";", encoding="latin-1"
)
# colunas de tempo chegam como string com virgula decimal — converter
tempo_cols = ["TEsperaAtracacao", "TEsperaInicioOp", "TOperacao",
              "TEsperaDesatracacao", "TAtracado", "TEstadia"]
for c in tempo_cols:
    if c in tempos.columns:
        tempos[c] = pd.to_numeric(tempos[c].astype(str).str.replace(",", "."), errors="coerce")
print(f"   {len(tempos):,} registros de tempos")

# Shipping lines
print("[3/4] Carregando shipping lines...")
vessels = pd.read_csv(
    BASE / "data" / "02_Operacoes" / "Vessels_Master_Enriched.csv",
    encoding="utf-8-sig"
)

# Join atracação 2025 + tempos + shipping line
atrac_2025 = atrac[atrac["Ano_Arquivo"] == 2025].copy()
imo_col = [c for c in atrac_2025.columns if "IMO" in c.upper() and "Capitania" not in c][0]

id_col = [c for c in atrac_2025.columns if "IDAtracacao" in c][0]
tempos_id_col = [c for c in tempos.columns if "IDAtracacao" in c][0]

base_sl = (
    atrac_2025[atrac_2025[imo_col] > 1_000_000]
    .merge(tempos.rename(columns={tempos_id_col: id_col}), on=id_col, how="inner")
    .merge(
        vessels[["NÚMERO IMO", "SHIPPING LINE", "vessel_type", "vessel_segment", "CAPACIDADE (TEU)", "dwt"]],
        left_on=imo_col, right_on="NÚMERO IMO", how="inner"
    )
)
print(f"   {len(base_sl):,} atracações com shipping line identificada")

# ── GRÁFICO 1 — Volume por Ano ───────────────────────────────
print("\n[4/4] Gerando graficos...")
print("  > Grafico 1: Atracacoes por ano e regiao")

col_regiao = [c for c in atrac.columns if "Regi" in c and "Hidro" not in c][0]
col_nav    = [c for c in atrac.columns if "Navega" in c][0]
col_porto  = [c for c in atrac.columns if "Porto" in c and "Atr" in c][0]

vol_ano = atrac.groupby("Ano_Arquivo").size().reset_index(name="N")
vol_reg = atrac.groupby(["Ano_Arquivo", col_regiao]).size().reset_index(name="N")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.barplot(data=vol_ano, x="Ano_Arquivo", y="N", ax=axes[0])
axes[0].set_title("Atracações por Ano")
axes[0].set_xlabel("Ano")
axes[0].set_ylabel("Atracações")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
for p in axes[0].patches:
    axes[0].annotate(f"{p.get_height()/1e3:.0f}k",
                     (p.get_x() + p.get_width()/2, p.get_height()),
                     ha="center", va="bottom", fontsize=9)

sns.barplot(data=vol_reg, x=col_regiao, y="N", hue="Ano_Arquivo", ax=axes[1])
axes[1].set_title("Atracações por Região Geográfica")
axes[1].set_xlabel("")
axes[1].set_ylabel("")
axes[1].tick_params(axis="x", rotation=15)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
axes[1].legend(title="Ano")

plt.suptitle("Volume de Atracações nos Portos Brasileiros (2023–2025)", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(FIG / "01_atracacoes_ano_regiao.png", bbox_inches="tight")
plt.close()

# ── GRÁFICO 2 — Top 10 Portos ───────────────────────────────
print("  > Grafico 2: Top 10 portos")
top_portos = (
    atrac[col_porto].value_counts()
    .head(10).reset_index()
    .rename(columns={"index": "Porto", col_porto: "N", "count": "N"})
)
# compatibilidade pandas 2.x
top_portos.columns = ["Porto", "N"] if len(top_portos.columns) == 2 else top_portos.columns

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=top_portos, x="N", y=top_portos.columns[0], ax=ax, orient="h")
ax.set_title("Top 10 Portos por Número de Atracações (2023–2025)")
ax.set_xlabel("Atracações")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
plt.tight_layout()
plt.savefig(FIG / "02_top10_portos.png")
plt.close()

# ── GRÁFICO 3 — Tipo de Navegação ───────────────────────────
print("  >Gráfico 3: Tipo de navegação")
MAP_NAV = {1:"Interior", 2:"Apoio Portuário", 3:"Cabotagem", 4:"Apoio Marítimo", 5:"Longo Curso"}
nav = (
    atrac[col_nav].map(MAP_NAV)
    .value_counts().reset_index()
)
nav.columns = ["Tipo", "N"]
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=nav, x="N", y="Tipo", ax=ax, orient="h")
ax.set_title("Atracações por Tipo de Navegação (2023–2025)")
ax.set_xlabel("Atracações")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
plt.tight_layout()
plt.savefig(FIG / "03_tipo_navegacao.png")
plt.close()

# ── GRÁFICO 4 — Shipping Lines: escalas por porto ───────────
print("  >Gráfico 4: Shipping lines — escalas por linha")
sl_count = base_sl["SHIPPING LINE"].value_counts().reset_index()
sl_count.columns = ["Shipping Line", "Escalas"]

fig, ax = plt.subplots(figsize=(9, 5))
colors = sns.color_palette("tab10", len(sl_count))
bars = ax.barh(sl_count["Shipping Line"], sl_count["Escalas"], color=colors)
ax.set_title("Escalas nos Portos Brasileiros por Shipping Line (2025)", fontsize=13)
ax.set_xlabel("Número de Escalas")
ax.set_ylabel("")
for bar, val in zip(bars, sl_count["Escalas"]):
    ax.text(val + 2, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=10)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(FIG / "04_shipping_lines_escalas.png")
plt.close()

# ── GRÁFICO 5 — T1/T2/T3/T4 por Shipping Line ──────────────
print("  >Gráfico 5: Decomposição de tempos T1–T4 por shipping line")
tempos_sl = base_sl[["SHIPPING LINE", "TEsperaAtracacao", "TEsperaInicioOp", "TOperacao", "TEsperaDesatracacao"]].copy()
tempos_sl.columns = ["Shipping Line", "T1 Espera Fundeio", "T2 Espera Início Op", "T3 Operação", "T4 Espera Desatracação"]

medias = tempos_sl.groupby("Shipping Line").median().reset_index()
medias_long = medias.melt(id_vars="Shipping Line", var_name="Fase", value_name="Horas (mediana)")

# Ordem das fases
ordem_fases = ["T1 Espera Fundeio", "T2 Espera Início Op", "T3 Operação", "T4 Espera Desatracação"]
medias_long["Fase"] = pd.Categorical(medias_long["Fase"], categories=ordem_fases, ordered=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=medias_long,
    x="Horas (mediana)", y="Shipping Line",
    hue="Fase", ax=ax, orient="h"
)
ax.set_title("Decomposição do Tempo de Escala por Shipping Line (2025)\nMediana em horas", fontsize=12)
ax.set_xlabel("Horas (mediana)")
ax.set_ylabel("")
ax.legend(title="Fase", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.tight_layout()
plt.savefig(FIG / "05_tempos_T1T2T3T4_shipping_lines.png", bbox_inches="tight")
plt.close()

# ── GRÁFICO 6 — Tempo Total de Estadia (TE) por Linha ───────
print("  >Gráfico 6: Tempo total de estadia por shipping line")
te_sl = (
    base_sl.groupby("SHIPPING LINE")["TEstadia"]
    .agg(["median", "mean", "std", "count"])
    .reset_index()
    .sort_values("median", ascending=False)
)
te_sl.columns = ["Shipping Line", "Mediana (h)", "Média (h)", "Desvio (h)", "N"]

fig, ax = plt.subplots(figsize=(9, 5))
bars = sns.barplot(
    data=te_sl, x="Mediana (h)", y="Shipping Line",
    ax=ax, orient="h", palette="RdYlGn_r"
)
ax.set_title("Tempo Total de Estadia (TE) por Shipping Line (2025)\nMediana em horas — menor é melhor", fontsize=11)
ax.set_xlabel("Horas")
ax.set_ylabel("")
for i, row in te_sl.iterrows():
    ax.text(row["Mediana (h)"] + 0.3, list(te_sl["Shipping Line"]).index(row["Shipping Line"]),
            f"n={int(row['N'])}", va="center", fontsize=9, color="gray")
plt.tight_layout()
plt.savefig(FIG / "06_tempo_estadia_por_linha.png")
plt.close()

# ── GRÁFICO 7 — Portos mais usados por Shipping Line ────────
print("  >Gráfico 7: Portos mais visitados por shipping line")
top_sl_porto = (
    base_sl.groupby(["SHIPPING LINE", col_porto])
    .size().reset_index(name="Escalas")
    .sort_values(["SHIPPING LINE", "Escalas"], ascending=[True, False])
)
# Top 4 portos por linha
top4 = top_sl_porto.groupby("SHIPPING LINE").head(4)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=top4, x="Escalas", y=col_porto,
    hue="SHIPPING LINE", ax=ax, orient="h"
)
ax.set_title("Top 4 Portos por Shipping Line — Número de Escalas (2025)", fontsize=12)
ax.set_xlabel("Escalas")
ax.set_ylabel("")
ax.legend(title="Shipping Line", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.tight_layout()
plt.savefig(FIG / "07_portos_por_shipping_line.png", bbox_inches="tight")
plt.close()

# ── GRÁFICO 8 — T1 por Porto (top 10 com mais espera) ───────
print("  >Gráfico 8: Tempo de espera T1 por porto")
t1_porto = (
    base_sl.groupby(col_porto)["TEsperaAtracacao"]
    .agg(["median", "count"])
    .reset_index()
)
t1_porto.columns = ["Porto", "T1_mediana_h", "N"]
t1_porto = t1_porto[t1_porto["N"] >= 5].sort_values("T1_mediana_h", ascending=False).head(15)

fig, ax = plt.subplots(figsize=(10, 6))
colors_t1 = ["#d73027" if v > 10 else "#fc8d59" if v > 5 else "#91cf60" for v in t1_porto["T1_mediana_h"]]
ax.barh(t1_porto["Porto"], t1_porto["T1_mediana_h"], color=colors_t1)
ax.axvline(5, color="orange", linestyle="--", linewidth=1, label="5h")
ax.axvline(10, color="red", linestyle="--", linewidth=1, label="10h")
ax.set_title("Tempo de Espera para Atracação (T1) por Porto\nNavios de Grandes Shipping Lines — 2025", fontsize=11)
ax.set_xlabel("Horas (mediana)")
ax.set_ylabel("")
ax.invert_yaxis()
ax.legend()
plt.tight_layout()
plt.savefig(FIG / "08_T1_espera_por_porto.png")
plt.close()

# ── GRÁFICO 9 — Sazonalidade das Escalas ────────────────────
print("  >Gráfico 9: Sazonalidade mensal das escalas")
col_mes = "Mes"
MESES = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
# converter mês de nome para número se necessário
atrac["Mes_n"] = pd.to_datetime(atrac["Data Atracação"] if "Data Atracação" in atrac.columns else atrac.iloc[:,9], dayfirst=True, errors="coerce").dt.month
sazon = atrac.groupby(["Ano_Arquivo", "Mes_n"]).size().reset_index(name="N")
sazon = sazon.dropna(subset=["Mes_n"])
sazon["Mes_n"] = sazon["Mes_n"].astype(int)

fig, ax = plt.subplots(figsize=(13, 5))
for ano in [2023, 2024, 2025]:
    d = sazon[sazon["Ano_Arquivo"] == ano].sort_values("Mes_n")
    ax.plot(d["Mes_n"], d["N"], marker="o", label=str(ano))
ax.set_title("Sazonalidade Mensal das Atracações (2023–2025)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels([MESES[i] for i in range(1, 13)])
ax.set_ylabel("Atracações")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
ax.legend(title="Ano")
plt.tight_layout()
plt.savefig(FIG / "09_sazonalidade_mensal.png")
plt.close()

print("\n" + "=" * 60)
print(f"  ✓ 9 gráficos salvos em outputs/figures/")
print("=" * 60)
