"""Grade research/STALE_LINE_LAYERS_PREREG_2026-11-05.md (pushed 68dfdd4 before this ran). Run once.
S0 = live stale-line BLEND-C (const, M2, M8, MKTL, opener); S1 = S0 + 8 lineup/travel + 4 roster features (home - away). Expanding-window fits as model3_grade_mktl.py.
  python ncaab/stale_line_layers_grade.py WORKDIR -> research/stale_line_layers_output.txt, research/stale_line_layers_bets.csv"""
import os, sys
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1])
P = pd.read_csv(os.path.join(W, "ncaab", "data", "model3_preds.csv"), low_memory=False); P["date"] = pd.to_datetime(P.date)
LT = pd.read_csv(os.path.join(W, "derived", "lineup_travel_features.csv.gz")).drop(columns=["season", "date"])
RO = pd.read_csv(os.path.join(W, "derived", "roster_features.csv.gz")).drop(columns=["season"])
n0 = len(P); P = P.merge(LT, on="espn_id", how="left").merge(RO, on="espn_id", how="left"); assert len(P) == n0
long = pd.concat([P[["season", "date", "hk"]].rename(columns={"hk": "k"}), P[["season", "date", "ak"]].rename(columns={"ak": "k"})]).sort_values("date")
long["n"] = long.groupby(["season", "k"]).cumcount(); fg = long.groupby(["season", "k", "date"]).n.min()
P["hn"] = [fg.get((s, k, d), 0) for s, k, d in zip(P.season, P.hk, P.date)]; P["an"] = [fg.get((s, k, d), 0) for s, k, d in zip(P.season, P.ak, P.date)]
ok = ((P.hk != "OTHER") & (P.ak != "OTHER") & (np.minimum(P.hn, P.an) >= 3)).values
sbr = (P.season <= 2021).values
so, sc = -P.open_sp, -P.close_sp
sbr_ok = sbr & so.notna().values & sc.notna().values & ((so - sc).abs() < 6).values
opener = pd.Series(np.where(sbr, so, -P.book_sp), index=P.index); opener[sbr & ~sbr_ok] = np.nan
close = pd.Series(np.where(sbr | (P.season >= 2024).values, sc, np.nan), index=P.index)
res = (P.home_pts - P.away_pts)
LF = ["lost_min_share", "lost_pts_share", "new_starters", "travel_miles", "tz_shift", "rest_days", "back_to_back", "games_last_7"]; RF = ["R1", "R2", "R3", "R4"]
X0 = np.column_stack([np.ones(len(P)), P.M2_m, P.M8_m, P.MKTL_m, opener])
feat = np.column_stack([(P["h_" + f] - P["a_" + f]).fillna(0).values for f in LF + RF])
X1 = np.column_stack([X0, feat])
def stack(X):
    pred = np.full(len(P), np.nan); y = close.values
    for s in range(2012, 2028):
        tr = (P.season < s).values & ok & ~np.isnan(X).any(axis=1) & ~np.isnan(y); te = (P.season == s).values & ~np.isnan(X).any(axis=1)
        if tr.sum() < 2000: continue
        b = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]; pred[te] = X[te] @ b
        if s == 2026: print(f"  coefficients used for 2025-26 ({X.shape[1]} terms):", np.round(b, 3).tolist())
    return pd.Series(pred, index=P.index)
print("S0 (live BLEND-C):"); p0 = stack(X0); print("S1 (BLEND-C + layers):"); p1 = stack(X1)
e0, e1 = p0 - opener, p1 - opener
flip = (np.sign(P.book_sp) != np.sign(P.close_sp)) & (np.sign(P.book_sp) != np.sign(P.open_sp)) & (P.book_sp.abs() >= 1)
base = pd.Series(ok, index=P.index) & opener.notna() & close.notna() & res.notna() & p0.notna() & p1.notna() & ~flip & ((P.book_sp - P.close_sp).abs() <= 10)
b2b = (P.h_rest_days <= 1) | (P.a_rest_days <= 1)
DK = base & (P.book == "DraftKings") & P.season.isin([2024, 2026]); EB = base & (P.book == "ESPN BET") & (P.season == 2025)
rm = lambda a: np.sqrt(np.mean(np.square(a)))
def grade(k, e):
    sg = np.sign(e[k]); clv = sg * (close[k] - opener[k]); r = sg * (res[k] - opener[k]); u = np.where(r > 0, 100 / 110, np.where(r < 0, -1.0, 0.0))
    return clv.values, u, sg.values
def matched(rows, e_ref, e_new, thr=0.5):
    k0 = rows & (e_ref.abs() >= thr); k1 = pd.Series(False, index=P.index)
    for s in P.season[rows].unique():
        rs = rows & (P.season == s); n = int((k0 & (P.season == s)).sum())
        if n == 0: continue
        a = e_new[rs].abs(); cut = np.sort(a.values)[::-1][n - 1]; k1 |= rs & (e_new.abs() >= cut)
    return k0, k1
def report(lab, rows):
    k0, k1 = matched(rows, e0, e1); out = {}
    print(f"\n[{lab}] games {int(rows.sum())} {P.season[rows].value_counts().sort_index().to_dict()} | RMSE of predicted close: opener {rm((close - opener)[rows]):.4f}, "
          f"S0 {rm((close - p0)[rows]):.4f}, S1 {rm((close - p1)[rows]):.4f}")
    for nm, k, e in (("S0 live rule |e|>=0.5", k0, e0), ("S1 matched count", k1, e1), ("S1 own |e|>=0.5 (diagnostic)", rows & (e1.abs() >= 0.5), e1)):
        clv, u, _ = grade(k, e); w, l = (u > 0).sum(), (u < 0).sum()
        per = pd.Series(u, index=P.season[k].values).groupby(level=0).sum().round(1).to_dict()
        print(f"  {nm:30s} {int(k.sum()):4d} bets {w / max(w + l, 1):.1%} {u.sum():+7.1f}u {per} CLV {clv.mean():+.3f}")
        out[nm] = (clv, u, k)
    print(f"  overlap S0/S1 matched: {int((k0 & k1).sum())} of {int(k0.sum())}")
    return k0, k1, out
k0, k1, O = report("DK 2023-24 + 2025-26 (DECIDES)", DK)
c0, u0, _ = O["S0 live rule |e|>=0.5"]; c1, u1, _ = O["S1 matched count"]; D = c1.mean() - c0.mean()
rng = np.random.default_rng(7); seas = P.season.values; idx = {s: np.where(DK.values & (seas == s))[0] for s in (2024, 2026)}
cl_all, op_all = close.values, opener.values; E0, E1 = e0.values, e1.values; Ds = []
for _ in range(5000):
    a0, a1 = [], []
    for s, ix in idx.items():
        r = ix[rng.integers(0, len(ix), len(ix))]; m0 = np.abs(E0[r]) >= 0.5; n = int(m0.sum())
        if n == 0: continue
        a = np.abs(E1[r]); m1 = a >= np.sort(a)[::-1][n - 1]
        a0.append(np.sign(E0[r][m0]) * (cl_all[r][m0] - op_all[r][m0])); a1.append(np.sign(E1[r][m1]) * (cl_all[r][m1] - op_all[r][m1]))
    Ds.append(np.concatenate(a1).mean() - np.concatenate(a0).mean())
lo, hi = np.percentile(Ds, [5, 95])
p1_ = D > 0 and lo > 0; p2_ = u1.sum() >= u0.sum(); p3_ = rm((close - p1)[DK]) < rm((close - p0)[DK])
_, _, Onb = report("DK non-back-to-back games (P4)", DK & ~b2b)
Dnb = Onb["S1 matched count"][0].mean() - Onb["S0 live rule |e|>=0.5"][0].mean(); p4_ = Dnb > 0
print(f"\nP1 D = CLV(S1) - CLV(S0) = {D:+.3f} [90% {lo:+.3f}, {hi:+.3f}] -> {p1_}")
print(f"P2 units S1 {u1.sum():+.1f} >= S0 {u0.sum():+.1f} -> {p2_}")
print(f"P3 RMSE of close S1 < S0 -> {p3_}")
print(f"P4 D on non-back-to-backs {Dnb:+.3f} > 0 -> {p4_}")
print("VERDICT:", "PASS (weaker evidence: seasons seen many times)" if (p1_ and p2_ and p3_ and p4_) else "FAIL")
report("ESPN BET 2024-25 (decides nothing)", EB)
rows = []
for nm, k, e in (("S0", k0, e0), ("S1", k1, e1)):
    clv, u, sg = grade(k, e)
    rows.append(pd.DataFrame(dict(arm=nm, espn_id=P.espn_id[k].values, season=P.season[k].values, date=P.date[k].values, home=P.home_name[k].values, away=P.away_name[k].values,
                                  opener_margin=opener[k].values, close_margin=close[k].values, margin=res[k].values, edge=e[k].values, side=sg, clv=clv, units=u)))
pd.concat(rows).to_csv(os.path.join(W, "ncaab", "research", "stale_line_layers_bets.csv"), index=False)
