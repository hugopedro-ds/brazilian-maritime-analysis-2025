"""
Teste de robustez da correlação ocupação × TEstadia — Brasil 2025
Bootstrap (n=10.000) + Leave-One-Out sistemático.

Spearman implementado via Pearson sobre ranks (sem scipy).
Autor: Hugo P.
"""
import pandas as pd
import numpy as np
import os

SEED = 42
N_BOOTSTRAP = 10_000
CSV_DIR = '/sessions/vigilant-relaxed-sagan/mnt/ANTAQ_Projeto - Copia/outputs/processed_data/'
OUT_CSV_DIR = CSV_DIR
FIG_DIR = '/sessions/vigilant-relaxed-sagan/mnt/ANTAQ_Projeto - Copia/outputs/figures/'

rng = np.random.default_rng(SEED)


def spearman_rho(x, y):
    """Correlação de Spearman via Pearson sobre ranks. Retorna (rho, p_approx)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if n < 3:
        return np.nan, np.nan
    # Ranking com média em empates
    rx = pd.Series(x).rank(method='average').values
    ry = pd.Series(y).rank(method='average').values
    # Pearson sobre ranks
    rho = np.corrcoef(rx, ry)[0, 1]
    # p-value aproximado via t-stat (para n pequeno é aproximação)
    if abs(rho) >= 1.0 or n <= 2:
        p = 0.0 if abs(rho) >= 1.0 else np.nan
    else:
        t = rho * np.sqrt((n - 2) / (1 - rho**2))
        # CDF t-student via relação com normal (aproximação)
        # Para n pequeno isto é apenas indicativo; usamos bootstrap como método primário
        from math import erf, sqrt
        # aproximação Wilson-Hilferty para t -> normal
        z = t * (1 - 1/(4*(n-2))) / np.sqrt(1 + t**2 / (2*(n-2)))
        p = 2 * (1 - 0.5 * (1 + erf(abs(z)/sqrt(2))))
    return rho, p


def load_data():
    df = pd.read_csv(CSV_DIR + 'ocupacao_testadia_porto_2025.csv', encoding='utf-8-sig')
    df = df.dropna(subset=['Taxa_Media_Pct', 'TEstadia_Med']).copy()
    df = df.sort_values('TEstadia_Med', ascending=False).reset_index(drop=True)
    return df


def bootstrap_ci(x, y, n_boot=N_BOOTSTRAP, conf=0.95):
    """Bootstrap com reamostragem com reposição dos pares (x,y)."""
    n = len(x)
    rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xi, yi = x[idx], y[idx]
        # Se bootstrap produz amostra constante, rho é NaN
        if len(np.unique(xi)) < 2 or len(np.unique(yi)) < 2:
            rhos[i] = np.nan
            continue
        rho, _ = spearman_rho(xi, yi)
        rhos[i] = rho
    rhos = rhos[~np.isnan(rhos)]
    lo = np.percentile(rhos, (1 - conf) / 2 * 100)
    hi = np.percentile(rhos, (1 + conf) / 2 * 100)
    return rhos, lo, hi


def leave_one_out(df, x_col='Taxa_Media_Pct', y_col='TEstadia_Med'):
    rows = []
    for i in range(len(df)):
        sub = df.drop(df.index[i])
        rho, p = spearman_rho(sub[x_col].values, sub[y_col].values)
        rows.append({
            'Porto_Removido': df.iloc[i]['Porto_Canon'],
            'n': len(sub),
            'rho': round(rho, 4),
            'p_aprox': round(p, 4),
        })
    return pd.DataFrame(rows).sort_values('rho').reset_index(drop=True)


def main():
    df = load_data()
    print(f'Portos no dataset: {len(df)}')
    print(df[['Porto_Canon', 'Taxa_Media_Pct', 'TEstadia_Med']].to_string(index=False))
    print()

    # ── Cenário A: todos os portos ──────────────────────────────────────
    x_A = df['Taxa_Media_Pct'].values
    y_A = df['TEstadia_Med'].values
    rho_A, p_A = spearman_rho(x_A, y_A)
    rhos_A, lo_A, hi_A = bootstrap_ci(x_A, y_A)
    print(f'=== CENÁRIO A: todos os {len(df)} portos ===')
    print(f'ρ pontual     = {rho_A:.4f}')
    print(f'p aproximado  = {p_A:.4f}')
    print(f'Bootstrap 95% = [{lo_A:.4f}, {hi_A:.4f}]  (n={N_BOOTSTRAP})')
    print(f'Bootstrap mediana = {np.median(rhos_A):.4f}')
    print()

    # ── Cenário B: sem São Francisco do Sul ──────────────────────────────
    df_B = df[df['Porto_Canon'] != 'São Francisco do Sul'].copy().reset_index(drop=True)
    x_B = df_B['Taxa_Media_Pct'].values
    y_B = df_B['TEstadia_Med'].values
    rho_B, p_B = spearman_rho(x_B, y_B)
    rhos_B, lo_B, hi_B = bootstrap_ci(x_B, y_B)
    print(f'=== CENÁRIO B: sem São Francisco do Sul (n={len(df_B)}) ===')
    print(f'ρ pontual     = {rho_B:.4f}')
    print(f'p aproximado  = {p_B:.4f}')
    print(f'Bootstrap 95% = [{lo_B:.4f}, {hi_B:.4f}]')
    print(f'Bootstrap mediana = {np.median(rhos_B):.4f}')
    print()

    # ── Cenário C: sem SFS e Paranaguá ──────────────────────────────────
    df_C = df[~df['Porto_Canon'].isin(['São Francisco do Sul', 'Paranaguá'])].copy().reset_index(drop=True)
    x_C = df_C['Taxa_Media_Pct'].values
    y_C = df_C['TEstadia_Med'].values
    rho_C, p_C = spearman_rho(x_C, y_C)
    rhos_C, lo_C, hi_C = bootstrap_ci(x_C, y_C)
    print(f'=== CENÁRIO C: sem SFS e Paranaguá (n={len(df_C)}) ===')
    print(f'ρ pontual     = {rho_C:.4f}')
    print(f'p aproximado  = {p_C:.4f}')
    print(f'Bootstrap 95% = [{lo_C:.4f}, {hi_C:.4f}]')
    print()

    # ── Leave-one-out no cenário A (todos) ──────────────────────────────
    print(f'=== LEAVE-ONE-OUT (base: cenário A, n=10) ===')
    loo_A = leave_one_out(df)
    print(loo_A.to_string(index=False))
    print()
    print(f'ρ mínimo LOO (A): {loo_A["rho"].min():.4f} (removido: {loo_A.iloc[0]["Porto_Removido"]})')
    print(f'ρ máximo LOO (A): {loo_A["rho"].max():.4f} (removido: {loo_A.iloc[-1]["Porto_Removido"]})')
    print(f'Range LOO (A): {loo_A["rho"].max() - loo_A["rho"].min():.4f}')
    print()

    # ── Leave-one-out no cenário B (sem SFS) ────────────────────────────
    print(f'=== LEAVE-ONE-OUT (base: cenário B, n=9) ===')
    loo_B = leave_one_out(df_B)
    print(loo_B.to_string(index=False))
    print()
    print(f'ρ mínimo LOO (B): {loo_B["rho"].min():.4f} (removido: {loo_B.iloc[0]["Porto_Removido"]})')
    print(f'ρ máximo LOO (B): {loo_B["rho"].max():.4f} (removido: {loo_B.iloc[-1]["Porto_Removido"]})')
    print(f'Range LOO (B): {loo_B["rho"].max() - loo_B["rho"].min():.4f}')
    print()

    # ── Salvar resultados ───────────────────────────────────────────────
    resultado = pd.DataFrame([
        {'Cenário': 'A — Todos', 'n': len(df), 'rho_pontual': round(rho_A, 4),
         'p_aprox': round(p_A, 4), 'CI95_lo': round(lo_A, 4), 'CI95_hi': round(hi_A, 4)},
        {'Cenário': 'B — Sem SFS', 'n': len(df_B), 'rho_pontual': round(rho_B, 4),
         'p_aprox': round(p_B, 4), 'CI95_lo': round(lo_B, 4), 'CI95_hi': round(hi_B, 4)},
        {'Cenário': 'C — Sem SFS e Paranaguá', 'n': len(df_C), 'rho_pontual': round(rho_C, 4),
         'p_aprox': round(p_C, 4), 'CI95_lo': round(lo_C, 4), 'CI95_hi': round(hi_C, 4)},
    ])
    resultado.to_csv(OUT_CSV_DIR + 'robustez_bootstrap_ic.csv', index=False, encoding='utf-8-sig')
    loo_A.to_csv(OUT_CSV_DIR + 'robustez_leave_one_out_cenarioA.csv', index=False, encoding='utf-8-sig')
    loo_B.to_csv(OUT_CSV_DIR + 'robustez_leave_one_out_cenarioB.csv', index=False, encoding='utf-8-sig')

    print('=== OUTPUTS SALVOS ===')
    print('  outputs/processed_data/robustez_bootstrap_ic.csv')
    print('  outputs/processed_data/robustez_leave_one_out_cenarioA.csv')
    print('  outputs/processed_data/robustez_leave_one_out_cenarioB.csv')

    # Salvar distribuição bootstrap para plot posterior
    np.savez(OUT_CSV_DIR + 'robustez_bootstrap_dist.npz',
             rhos_A=rhos_A, rhos_B=rhos_B, rhos_C=rhos_C)
    print('  outputs/processed_data/robustez_bootstrap_dist.npz')

    return resultado, loo_A, loo_B, (rhos_A, rhos_B, rhos_C)


if __name__ == '__main__':
    main()
