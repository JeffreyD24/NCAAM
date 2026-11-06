"""Overlap of the base-edge candidate (BASE_EDGE_DK_CANDIDATE_PREREG_2026-11-05.md) with the live PROVISIONAL stale-line rule
(nba-mixed-model ncaab/research/MODEL3_RESULTS_2026-11-05.md; BLEND-C with live_blendc.json coefficients, |edge| >= 0.5), DK 2023-24 + 2025-26.
Before the stale-line rule's other filters (3+ games, conference id, price, CT). Quick check, Nov 5, 2026.
  python ncaab/base_edge_vs_stale_overlap.py NBA_REPO NCAAM_REPO"""
import sys, json, numpy as np, pandas as pd
NB, NC = sys.argv[1], sys.argv[2]
P = pd.read_csv(f"{NB}/ncaab/data/model3_preds.csv", low_memory=False); c = json.load(open(f"{NB}/ncaab/data/live_blendc.json"))["coef"]
P = P[P.book_sp.notna() & P.season.isin([2024, 2026]) & (P.book == "DraftKings")].copy(); op = -P.book_sp
P["e_stale"] = c[0] + c[1] * P.M2_m + c[2] * P.M8_m + c[3] * P.MKTL_m + c[4] * op - op
V = pd.read_csv(f"{NC}/ncaab/research/lineup_travel_v3_bets.csv")
for q, lab in ((0.01, "candidate top 1% (~edge 2.8)"),):
    m = V[(V.model == "A") & (V.q == q)].merge(P[["espn_id", "e_stale"]], on="espn_id", how="left")
    both = (m.e_stale.abs() >= 0.5) & (np.sign(m.e_stale) == m.side)
    for nm, g in (("also a stale-line bet (same side)", m[both]), ("candidate only", m[~both])):
        d = g[g.res != 0]
        print(f"{lab} | {nm}: {len(g)} bets, hit {(d.res > 0).mean():.3f}, units {g.res.sum():+.1f}, CLV {g.clv.mean():+.2f}, by season {g.groupby('season').res.sum().round(1).to_dict()}")
print("stale-line candidate rows |edge| >= 0.5 before other filters:", int((P.e_stale.abs() >= 0.5).sum()))
