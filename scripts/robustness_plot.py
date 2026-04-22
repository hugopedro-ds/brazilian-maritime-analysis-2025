"""Figura: bootstrap distribution + leave-one-out sensitivity."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

CSV_DIR = '/sessions/vigilant-relaxed-sagan/mnt/ANTAQ_Projeto - Copia/outputs/processed_data/'
FIG_DIR = '/sessions/vigilant-relaxed-sagan/mnt/ANTAQ_Projeto - Copia/outputs/figures/'

# Load
npz = np.load(CSV_DIR + 'robustez_bootstrap_dist.npz')
rhos_A, rhos_B, rhos_C = npz['rhos_A'], npz['rhos_B'], npz['rhos_C']
loo_A = pd.read_csv(CSV_DIR + 'robustez_leave_one_out_cenarioA.csv', encoding='utf-8-sig')
loo_B = pd.read_csv(CSV_DIR + 'robustez_leave_one_out_cenarioB.csv', encoding='utf-8-sig')

plt.rcParams.update({'figure.dpi': 150, 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# ── Painel A: distribuição bootstrap ─────────────────────────────────────
ax = axes[0]
colors = {'A': '#4878CF', 'B': '#D65F5F', 'C': '#6ACC65'}
labels = {'A': f'A — Todos (n=10)\nρ=0.855  CI95=[0.40, 1.00]',
          'B': f'B — Sem SFS (n=9)\nρ=0.817  CI95=[0.23, 1.00]',
          'C': f'C — Sem SFS+PNG (n=8)\nρ=0.738  CI95=[-0.06, 1.00]'}

for key, rhos in [('A', rhos_A), ('B', rhos_B), ('C', rhos_C)]:
    ax.hist(rhos, bins=60, alpha=0.55, color=colors[key], label=labels[key], density=True)

ax.axvline(0.70, color='#27AE60', ls='--', lw=1.2, alpha=0.7, label='Limiar "robusta" (0.70)')
ax.axvline(0.50, color='#E8A838', ls=':', lw=1.2, alpha=0.7, label='Limiar "moderada" (0.50)')
ax.axvline(0, color='gray', ls='-', lw=0.8, alpha=0.4)

ax.set_xlabel('ρ bootstrap (Spearman)', fontsize=11)
ax.set_ylabel('Densidade', fontsize=11)
ax.set_title('Distribuição bootstrap da correlação ρ\n10.000 reamostragens com reposição', fontsize=12)
ax.legend(fontsize=8, loc='upper left')
ax.set_xlim(-0.3, 1.05)

# ── Painel B: leave-one-out ──────────────────────────────────────────────
ax = axes[1]
# Cenário A
loo_A_sorted = loo_A.sort_values('rho').reset_index(drop=True)
y_pos_A = np.arange(len(loo_A_sorted))
ax.barh(y_pos_A - 0.2, loo_A_sorted['rho'], height=0.4,
        color='#4878CF', alpha=0.8, label='Cenário A (base n=10)')
# Cenário B (ordenar pela mesma ordem de portos removidos onde possível)
portos_A = loo_A_sorted['Porto_Removido'].tolist()
loo_B_reindexed = loo_B.set_index('Porto_Removido').reindex([p for p in portos_A if p in loo_B['Porto_Removido'].values])
y_pos_B = [portos_A.index(p) for p in loo_B_reindexed.index]
ax.barh(np.array(y_pos_B) + 0.2, loo_B_reindexed['rho'], height=0.4,
        color='#D65F5F', alpha=0.8, label='Cenário B (base n=9)')

ax.set_yticks(y_pos_A)
ax.set_yticklabels(loo_A_sorted['Porto_Removido'], fontsize=9)
ax.axvline(0.855, color='#4878CF', ls=':', lw=1, alpha=0.6)
ax.axvline(0.817, color='#D65F5F', ls=':', lw=1, alpha=0.6)
ax.axvline(0.70, color='#27AE60', ls='--', lw=1, alpha=0.6, label='Limiar 0.70')
ax.set_xlabel('ρ Spearman após remover o porto', fontsize=11)
ax.set_title('Leave-One-Out: sensibilidade a cada porto', fontsize=12)
ax.set_xlim(0, 1.05)
ax.legend(fontsize=8, loc='lower right')

for i, rho in enumerate(loo_A_sorted['rho']):
    ax.text(rho + 0.01, i - 0.2, f'{rho:.3f}', va='center', fontsize=8, color='#4878CF')

plt.tight_layout()
out_path = FIG_DIR + 'nb15_03_bootstrap_loo.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Salvo: {out_path}')
