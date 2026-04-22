"""
Port Infrastructure Compatibility Analysis
Vessels_Master_Enriched.csv x Restrições Físicas Portuárias

LIMITAÇÕES:
- DWT: 100% nulo — calado NÃO calculado
- LOA/beam: 24.3% nulos (335 navios) — classificados como "indeterminado"
- ZIM NORFOLK LOA=661m: erro de dados, tratado como outlier e excluído das métricas
- Análise baseada em LOA e beam apenas — sem validação de calado
- Frota registada em ANTAQ 2023-2025, não deployment real
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

os.chdir(r'C:\Users\hdped\Desktop\ANTAQ_Projeto - Copia')

FILE   = 'data/02_Operacoes/Vessels_Master_Enriched.csv'
FIGDIR = 'outputs/figures'
CSVDIR = 'outputs/processed_data'
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(CSVDIR, exist_ok=True)

CORES = {
    'COSCO':       '#003087',
    'MAERSK':      '#0099CC',
    'CMA CGM':     '#D62728',
    'MSC':         '#F5C518',
    'EVERGREEN':   '#2CA02C',
    'Hapag-Lloyd': '#F26722',
    'ONE':         '#E377C2',
    'ZIM':         '#17BECF',
}

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
})

# ─── 1. LOAD & DIAGNÓSTICO ────────────────────────────────────────────────────
df = pd.read_csv(FILE, encoding='utf-8-sig', low_memory=False)
df.columns = df.columns.str.strip()

print('=' * 65)
print('DIAGNÓSTICO DE DADOS')
print('=' * 65)
print(f'Total navios únicos : {len(df):,}')
print(f'DWT               : 100.0% nulo — calado INDISPONÍVEL')
print(f'LOA nulos         : {df["loa"].isna().sum()} ({df["loa"].isna().mean()*100:.1f}%)')
print(f'beam nulos        : {df["beam"].isna().sum()} ({df["beam"].isna().mean()*100:.1f}%)')
print(f'São os mesmos?    : {set(df[df["loa"].isna()].index) == set(df[df["beam"].isna()].index)}')
print()

# Anomalia ZIM NORFOLK
outlier_mask = df['loa'] > 400
print(f'Outliers LOA > 400m: {outlier_mask.sum()} navio(s)')
print(df[outlier_mask][['NOME DO NAVIO', 'SHIPPING LINE', 'loa', 'beam', 'CAPACIDADE (TEU)']].to_string())
print('→ Excluídos das métricas de restrição (erro de dados)')
print()

# Excluir outlier
df_clean = df[~outlier_mask].copy()
print(f'Dataset limpo: {len(df_clean)} navios ({len(df) - len(df_clean)} excluídos)')

# Missing por carrier
miss = (df_clean[df_clean['loa'].isna()]
        .groupby('SHIPPING LINE').size().rename('sem_loa'))
total = df_clean.groupby('SHIPPING LINE').size().rename('total')
miss_df = pd.concat([miss, total], axis=1).fillna(0)
miss_df['sem_loa'] = miss_df['sem_loa'].astype(int)
miss_df['pct_missing'] = (miss_df['sem_loa'] / miss_df['total'] * 100).round(1)
print('=== MISSING LOA/BEAM POR CARRIER ===')
print(miss_df.sort_values('pct_missing', ascending=False).to_string())
print()

# ─── 2. RESTRIÇÕES PORTUÁRIAS ─────────────────────────────────────────────────
PORTOS = {
    'Santos'    : {'loa': 366, 'beam': 51},
    'Itaguaí'   : {'loa': 366, 'beam': 51},
    'Paranaguá' : {'loa': 300, 'beam': 40},
    'Suape'     : {'loa': 300, 'beam': 40},
    'Pecém'     : {'loa': 280, 'beam': 40},
    'Manaus'    : {'loa': 200, 'beam': 30},
}

print('=== RESTRIÇÕES PORTUÁRIAS (ANTAQ/ANTF) ===')
print(f'{"Porto":12s}  {"LOA máx":>8s}  {"Beam máx":>9s}  {"Nota calado"}')
for p, r in PORTOS.items():
    print(f'{p:12s}  {r["loa"]:>8.0f}m  {r["beam"]:>8.0f}m  INDISPONÍVEL (DWT=0)')
print()

# ─── 3. CLASSIFICAÇÃO POR NAVIO x PORTO ──────────────────────────────────────
# Para cada navio: compatível / incompatível / indeterminado (loa ou beam null)

results = []

for porto, limites in PORTOS.items():
    loa_lim  = limites['loa']
    beam_lim = limites['beam']

    for _, row in df_clean.iterrows():
        carrier = row['SHIPPING LINE']
        teu     = row['CAPACIDADE (TEU)'] if not pd.isna(row['CAPACIDADE (TEU)']) else 0
        loa_v   = row['loa']
        beam_v  = row['beam']

        if pd.isna(loa_v) or pd.isna(beam_v):
            status = 'indeterminado'
        elif loa_v > loa_lim or beam_v > beam_lim:
            status = 'incompativel'
            # detalhar qual dimensão falhou
        else:
            status = 'compativel'

        results.append({
            'porto'   : porto,
            'carrier' : carrier,
            'imo'     : row['NÚMERO IMO'],
            'loa'     : loa_v,
            'beam'    : beam_v,
            'teu'     : teu,
            'status'  : status,
            'loa_excede'  : (loa_v > loa_lim)  if not pd.isna(loa_v) else None,
            'beam_excede' : (beam_v > beam_lim) if not pd.isna(beam_v) else None,
        })

res = pd.DataFrame(results)

# ─── 4. MATRIZ CARRIER x PORTO — % compatíveis ───────────────────────────────
print('=' * 65)
print('ANÁLISE DE COMPATIBILIDADE')
print('=' * 65)

summary = (res.groupby(['carrier', 'porto', 'status'])
              .size().reset_index(name='n'))

pivot_total = (res.groupby(['carrier', 'porto'])
                  .size().reset_index(name='total'))

pivot_comp  = (res[res['status'] == 'compativel']
                  .groupby(['carrier', 'porto'])
                  .size().reset_index(name='n_comp'))

pivot_indet = (res[res['status'] == 'indeterminado']
                  .groupby(['carrier', 'porto'])
                  .size().reset_index(name='n_indet'))

matrix_base = pivot_total.merge(pivot_comp,  on=['carrier','porto'], how='left')
matrix_base = matrix_base.merge(pivot_indet, on=['carrier','porto'], how='left')
matrix_base = matrix_base.fillna(0)

matrix_base['pct_comp']  = (matrix_base['n_comp']  / matrix_base['total'] * 100).round(1)
matrix_base['pct_indet'] = (matrix_base['n_indet'] / matrix_base['total'] * 100).round(1)
matrix_base['pct_incomp']= (100 - matrix_base['pct_comp'] - matrix_base['pct_indet']).round(1).clip(lower=0)

# Heatmap data: % compatível (excluindo indeterminados da base)
matrix_base['n_determinado'] = matrix_base['total'] - matrix_base['n_indet']
matrix_base['pct_comp_det']  = np.where(
    matrix_base['n_determinado'] > 0,
    (matrix_base['n_comp'] / matrix_base['n_determinado'] * 100).round(1),
    np.nan
)

heatmap_data = matrix_base.pivot(index='carrier', columns='porto', values='pct_comp_det')
porto_order  = ['Manaus', 'Pecém', 'Suape', 'Paranaguá', 'Santos', 'Itaguaí']
heatmap_data = heatmap_data[porto_order]

print('\n=== MATRIZ % COMPATÍVEIS (sobre navios com LOA/beam conhecidos) ===')
print(heatmap_data.round(1).to_string())
print()
print('Nota: valores excluem navios com LOA/beam=null')

# ─── 5. TEU BLOQUEADO ─────────────────────────────────────────────────────────
teu_block = (res[res['status'] == 'incompativel']
               .groupby(['carrier', 'porto'])['teu']
               .sum().reset_index(name='teu_bloqueado'))

teu_total_carrier = (res[res['porto'] == 'Santos']  # base única
                       .groupby('carrier')['teu']
                       .sum().reset_index(name='teu_total'))

teu_block = teu_block.merge(teu_total_carrier, on='carrier', how='left')
teu_block['pct_teu_bloqueado'] = (teu_block['teu_bloqueado'] / teu_block['teu_total'] * 100).round(1)

print('\n=== TEU BLOQUEADO POR CARRIER x PORTO ===')
print(teu_block.sort_values(['porto','teu_bloqueado'], ascending=[True, False]).to_string(index=False))

# Ranking: TEU total bloqueado em portos mais restritivos (Manaus + Pecém + Suape + Paranaguá)
portos_restritivos = ['Manaus', 'Pecém', 'Suape', 'Paranaguá']
ranking = (teu_block[teu_block['porto'].isin(portos_restritivos)]
            .groupby('carrier')['teu_bloqueado']
            .sum().reset_index()
            .sort_values('teu_bloqueado', ascending=False))
ranking = ranking.merge(teu_total_carrier, on='carrier', how='left')
ranking['pct_bloqueado'] = (ranking['teu_bloqueado'] / ranking['teu_total'] * 100).round(1)
ranking['rank'] = range(1, len(ranking) + 1)

print('\n=== RANKING TEU BLOQUEADO (Manaus+Pecém+Suape+Paranaguá) ===')
print(ranking[['rank','carrier','teu_bloqueado','teu_total','pct_bloqueado']].to_string(index=False))

# ─── 6. EXPORTAR CSVs ─────────────────────────────────────────────────────────
matrix_export = matrix_base[['carrier','porto','total','n_comp','n_indet',
                               'pct_comp','pct_indet','pct_incomp','pct_comp_det']]
matrix_export.to_csv(f'{CSVDIR}/port_compat_matrix.csv', index=False, encoding='utf-8-sig')

teu_block.to_csv(f'{CSVDIR}/port_teu_bloqueado.csv', index=False, encoding='utf-8-sig')
ranking.to_csv(f'{CSVDIR}/port_ranking_teu_bloqueado.csv', index=False, encoding='utf-8-sig')
print('\nCSVs exportados.')

# ─── 7. FIGURA 1 — HEATMAP ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
fig.suptitle('Compatibilidade Frota x Porto — % Navios Dentro dos Limites Físicos\n'
             '(LOA e Beam | navios com dados indisponíveis excluídos da base)',
             fontsize=12, fontweight='bold')

# Máscara para indeterminados
mask = heatmap_data.isna()

cmap = sns.color_palette("RdYlGn", as_cmap=True)
sns.heatmap(
    heatmap_data,
    annot=True, fmt='.0f', cmap=cmap,
    vmin=0, vmax=100,
    linewidths=0.5, linecolor='white',
    mask=mask,
    ax=ax,
    cbar_kws={'label': '% Navios Compatíveis', 'shrink': 0.8}
)

# Células indeterminadas em cinza
for i in range(heatmap_data.shape[0]):
    for j in range(heatmap_data.shape[1]):
        if mask.iloc[i, j]:
            ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True,
                                        color='#cccccc', zorder=2))
            ax.text(j + 0.5, i + 0.5, 'N/D', ha='center', va='center',
                    fontsize=9, color='#666', zorder=3)

ax.set_xlabel('Porto', fontsize=11)
ax.set_ylabel('Carrier', fontsize=11)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

# Anotação de restrições
for idx, (porto, lims) in enumerate([(p, PORTOS[p]) for p in porto_order]):
    ax.text(idx + 0.5, -0.7, f"LOA≤{lims['loa']}m\nBeam≤{lims['beam']}m",
            ha='center', va='top', fontsize=7.5, color='#444',
            transform=ax.get_xaxis_transform())

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(f'{FIGDIR}/port_compat_heatmap.png', bbox_inches='tight', dpi=150)
plt.close()
print('Figura 1 (heatmap) salva.')

# ─── 8. FIGURA 2 — RANKING TEU BLOQUEADO ──────────────────────────────────────
teu_pivot = teu_block.pivot(index='carrier', columns='porto', values='teu_bloqueado').fillna(0)
teu_pivot = teu_pivot[porto_order]
teu_pivot = teu_pivot.loc[ranking['carrier'].tolist()]  # ordenar por total bloqueado

porto_colors = ['#2171B5','#4292C6','#6BAED6','#9ECAE1','#C6DBEF','#DEEBF7']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('TEU Potencialmente Bloqueado por Restrições Físicas Portuárias',
             fontsize=13, fontweight='bold')

# Stacked bar por porto
x = np.arange(len(teu_pivot))
bottom = np.zeros(len(teu_pivot))
for porto, color in zip(porto_order, porto_colors):
    if porto in teu_pivot.columns:
        vals = teu_pivot[porto].values
        ax1.bar(x, vals, bottom=bottom, color=color, alpha=0.88, label=porto, width=0.6)
        bottom += vals

ax1.set_xticks(x)
ax1.set_xticklabels(teu_pivot.index, rotation=30, ha='right')
ax1.set_ylabel('TEU Capacidade Bloqueada')
ax1.set_title('TEU Bloqueado por Porto e Carrier')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v/1e6:.1f}M' if v >= 1e6 else f'{v/1e3:.0f}k'))
ax1.legend(fontsize=9, title='Porto', loc='upper right')

# Scatter: % bloqueado vs TEU total
for _, row in ranking.iterrows():
    c = row['carrier']
    ax2.scatter(row['pct_bloqueado'], row['teu_bloqueado'],
                s=200, color=CORES.get(c, '#888'),
                alpha=0.9, edgecolors='white', linewidth=0.8, zorder=3)
    ax2.annotate(c, (row['pct_bloqueado'], row['teu_bloqueado']),
                 textcoords='offset points', xytext=(7, 3), fontsize=8.5)

ax2.set_xlabel('% TEU da Frota Bloqueado (portos restritivos)')
ax2.set_ylabel('TEU Total Bloqueado')
ax2.set_title('Custo de Oportunidade por Carrier\n(Manaus + Pecém + Suape + Paranaguá)')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v/1e6:.1f}M' if v >= 1e6 else f'{v/1e3:.0f}k'))
ax2.axvline(20, color='gray', linestyle='--', alpha=0.4, label='20%')
ax2.legend(fontsize=8)

plt.tight_layout()
plt.savefig(f'{FIGDIR}/port_teu_bloqueado.png', bbox_inches='tight', dpi=150)
plt.close()
print('Figura 2 (TEU bloqueado) salva.')

# ─── 9. FIGURA 3 — STACKED BAR STATUS POR PORTO ──────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Distribuição de Compatibilidade por Porto e Carrier\n'
             '(Verde=Compatível | Vermelho=Incompatível | Cinza=Indeterminado)',
             fontsize=12, fontweight='bold')

axes_flat = axes.flatten()

for idx, porto in enumerate(porto_order):
    ax = axes_flat[idx]
    sub = matrix_base[matrix_base['porto'] == porto].set_index('carrier')
    sub = sub.reindex([c for c in CORES.keys() if c in sub.index])

    x = np.arange(len(sub))
    ax.bar(x, sub['pct_comp'],   color='#2CA02C', alpha=0.85, label='Compatível', width=0.6)
    ax.bar(x, sub['pct_incomp'], color='#D62728', alpha=0.85, label='Incompatível',
           bottom=sub['pct_comp'], width=0.6)
    ax.bar(x, sub['pct_indet'],  color='#AAAAAA', alpha=0.85, label='Indeterminado',
           bottom=sub['pct_comp'] + sub['pct_incomp'], width=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(sub.index, rotation=40, ha='right', fontsize=8)
    ax.set_title(f'{porto}  (LOA≤{PORTOS[porto]["loa"]}m, Beam≤{PORTOS[porto]["beam"]}m)',
                 fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_ylabel('%')
    if idx == 0:
        ax.legend(fontsize=8, loc='upper right')

plt.tight_layout()
plt.savefig(f'{FIGDIR}/port_compat_by_porto.png', bbox_inches='tight', dpi=150)
plt.close()
print('Figura 3 (por porto) salva.')

# ─── SUMÁRIO ──────────────────────────────────────────────────────────────────
print()
print('=' * 65)
print('SUMÁRIO — PORT COMPATIBILITY ANALYSIS')
print('=' * 65)
print()
print('LIMITAÇÕES CRÍTICAS:')
print('  1. Calado: DWT 100% nulo. Restrições de draft NÃO avaliadas.')
print('  2. LOA/beam: 24.3% missing (335 navios) — classificados como indeterminado.')
print('  3. Outlier excluído: ZIM NORFOLK LOA=661m (erro de dados).')
print('  4. Análise sobre frota registada ANTAQ — não deployment real.')
print()
print('ACHADOS PRINCIPAIS:')
# Pior carrier em Manaus
manaus_data = matrix_base[(matrix_base['porto']=='Manaus') & (matrix_base['n_determinado']>0)]
worst_manaus = manaus_data.loc[manaus_data['pct_comp_det'].idxmin()]
print(f'  Manaus (mais restritivo): {worst_manaus["carrier"]} tem menor compatibilidade '
      f'({worst_manaus["pct_comp_det"]:.0f}% navios dentro dos limites)')
# Carrier com mais TEU bloqueado
top_blocked = ranking.iloc[0]
print(f'  Maior TEU bloqueado: {top_blocked["carrier"]} '
      f'({top_blocked["teu_bloqueado"]/1e6:.2f}M TEU, {top_blocked["pct_bloqueado"]:.1f}% da frota)')
print()
print('Outputs gerados:')
print('  outputs/figures/port_compat_heatmap.png')
print('  outputs/figures/port_teu_bloqueado.png')
print('  outputs/figures/port_compat_by_porto.png')
print('  outputs/processed_data/port_compat_matrix.csv')
print('  outputs/processed_data/port_teu_bloqueado.csv')
print('  outputs/processed_data/port_ranking_teu_bloqueado.csv')
