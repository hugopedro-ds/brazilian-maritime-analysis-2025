# LinkedIn Post — versão revista (pós-auditoria)

**Data:** 2026-04-22
**Estado:** Pronto para publicar APÓS push do repo actualizado para GitHub
**Alterações vs versão anterior:**
- Finding #1: acrescentado disclaimer "order-of-magnitude" na comparação UNCTAD
- Finding #2: reescrito para "within Feeder Max segment", elimina ambiguidade de "quasi-monopólio no Brasil"
- Finding #4: correlação reformulada para incluir CI bootstrap [0,23; 1,00] e contra-exemplo Suape
- PT: substituído "TEstadia" por "estadia portuária" em prosa (mantém TEstadia em contexto técnico)
- Tom geral: mais conservador nas afirmações causais, mais forte na honestidade metodológica

---

## EN

I analysed 22,746 deep sea vessel calls in Brazil (2025).

**84 hours median port stay. 23 happen before the vessel even berths.**

The primary driver looks like coordination — vessel arrival vs berth window — not terminal handling. Brazil runs at roughly 2.1× the UNCTAD benchmark (10.9h, developing countries, RMT 2025). Order-of-magnitude comparison: UNCTAD uses AIS, ANTAQ uses administrative timestamps. Direction is clear.

Three supporting findings:

→ Within the Feeder Max segment (1k–3k TEU), CMA CGM holds 68.9% of deployed capacity (HHI = 5,480 — intra-segment, not Brazil-wide). CMA CGM is also the most efficient operator in that segment: 75h vs 104h for the rest.

→ No carrier allocates more than 12% of its registered fleet to Brazil. Evergreen tops at 12.0%; the majors sit at 6–8%. Structural under-deployment signal.

→ Berth occupancy correlates with port stay (Spearman ρ = 0.82, n = 9). Bootstrap 95% CI wide at [0.23, 1.00] due to small sample — disclosed transparently. Paranaguá at 77% / 98h is the saturation case; Suape at 65.7% / 54h is the efficient counter-example. Occupancy isn't the full story.

Full analysis, code, operational definitions, robustness tests:
https://github.com/hugopedro-ds/brazilian-maritime-analysis-2025

#shipping #containerlogistics #portoperations #datascience #maritimetransport #ANTAQ

---

## PT

Analisei 22.746 escalas de navios em Longo Curso no Brasil (2025).

**84h de estadia portuária mediana. 23h passam-se antes do navio sequer atracar.**

O driver principal parece ser coordenação — chegada do navio vs janela de berço — não o handling do terminal. O Brasil opera a cerca de 2,1× o benchmark UNCTAD (10,9h em países em desenvolvimento, RMT 2025). Comparação de ordem de grandeza: UNCTAD usa AIS, ANTAQ usa timestamps administrativos. A direcção é inequívoca.

Três achados de suporte:

→ Dentro do segmento Feeder Max (1k–3k TEU), a CMA CGM detém 68,9% da capacidade TEU (HHI = 5.480 — intra-segmento, não mercado total). É também o carrier mais eficiente dentro do segmento: 75h vs 104h dos restantes.

→ Nenhum carrier aloca mais de 12% da sua frota registada ao Brasil. Evergreen lidera com 12,0%; os majors ficam nos 6–8%. Sinal de sub-deployment estrutural.

→ Ocupação de berço correlaciona com estadia (Spearman ρ = 0,82, n = 9). IC 95% bootstrap largo em [0,23; 1,00] pela amostra pequena — reportado com transparência. Paranaguá a 77% / 98h é o caso de saturação; Suape a 65,7% / 54h é o contra-exemplo eficiente. Ocupação não conta a história toda.

Análise completa, código, definições operacionais, testes de robustez:
https://github.com/hugopedro-ds/brazilian-maritime-analysis-2025

#shipping #containerlogistics #portoperations #datascience #maritimetransport #ANTAQ

---

## Checklist obrigatório antes de publicar

1. [ ] Repo actualizado no GitHub (`git push`) com: `README.md` novo, `docs/definitions.md`, `outputs/figures/nb15_03_bootstrap_loo.png`, CSVs de robustez
2. [ ] Confirmar que o link do post aponta para o repo correcto e o branch `main` está actualizado
3. [ ] Testar o link numa janela privada (logout do GitHub) para confirmar que carrega
4. [ ] Ler o post em voz alta — confirma fluxo natural
5. [ ] Confirmar que todos os números do post aparecem exactamente iguais no README principal do repo
6. [ ] Verificar contagem de caracteres LinkedIn (limite 3000; versão actual ~1400 EN + 1400 PT, dentro do limite mesmo combinado)
7. [ ] Considerar separar EN e PT em dois posts distintos se quiseres audiências separadas nas métricas de engagement

## Notas de tom

- Troquei "The problem is not the terminals" por "The primary driver looks like coordination" — menos categórico, mais defensável. A afirmação anterior era uma inferência apresentada como facto.
- Finding #4 agora termina em "Occupancy isn't the full story" — subtil, mas mostra que tu próprio questionas a força da correlação. Um analista técnico que leia isto passa a ver-te como sério, não como content marketer.
- Evitei a palavra "quasi-monopólio" que estava implicada no original. HHI = 5.480 é altamente concentrado pela definição DOJ/FTC, mas "quasi-monopólio" é leitura jornalística, não técnica.
