"""Grade research/STALE_LINE_V2_SBR_PREREG_2026-11-06.md (pushed ebe0d60 before this ran). Run once.
v1 = live stale-line BLEND-C (const, M2, M8, MKTL, opener), |e| >= 0.5; v2 = v1 + 8 lineup/travel + 4 roster features, |e| >= 0.62 fixed.
Model code identical to stale_line_layers_grade.py (expanding window); rows and prices: SBR opener/close, 2014-2021 (2013 separate).
  python ncaab/stale_line_v2_sbr_grade.py WORKDIR -> research/stale_line_v2_sbr_output.txt (via tee), research/stale_line_v2_sbr_bets.csv"""
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
        if s in (2014, 2021): print(f"  season {s}: trained on {int(tr.sum())} rows; coefficients ({X.shape[1]} terms):", np.round(b, 3).tolist())
    return pd.Series(pred, index=P.index)
print("v1 (S0, live BLEND-C):"); p0 = stack(X0); print("v2 (S1, BLEND-C + layers):"); p1 = stack(X1)
e0, e1 = p0 - opener, p1 - opener
oppo = (np.sign(so) != np.sign(sc)) & (so.abs() >= 3) & (sc.abs() >= 3)   # prereg guard: opposite signs with both |x| >= 3
base = pd.Series(ok & sbr_ok, index=P.index) & ~oppo & res.notna() & p0.notna() & p1.notna()
T1, T2 = 0.5, 0.62
TEST = list(range(2014, 2022))
def grade(k, e):
    sg = np.sign(e[k]); clv = sg * (close[k] - opener[k]); r = sg * (res[k] - opener[k]); u = np.where(r > 0, 100 / 110, np.where(r < 0, -1.0, 0.0))
    return clv.values, u, sg.values
def line(nm, k, e):
    clv, u, _ = grade(k, e); w, l = (u > 0).sum(), (u < 0).sum()
    print(f"  {nm:34s} {int(k.sum()):5d} bets {w / max(w + l, 1):.1%} {u.sum():+8.1f}u CLV {clv.mean() if len(clv) else float('nan'):+.3f}")
    return clv, u
rows = base & P.season.isin(TEST)
rm = lambda a: np.sqrt(np.mean(np.square(a)))
print(f"\nTest rows 2014-2021: {int(rows.sum())} games {P.season[rows].value_counts().sort_index().to_dict()}")
print(f"RMSE of predicted SBR close: opener {rm((close - opener)[rows]):.4f}, v1 {rm((close - p0)[rows]):.4f}, v2 {rm((close - p1)[rows]):.4f}")
k0, k1 = rows & (e0.abs() >= T1), rows & (e1.abs() >= T2)
print("\n[POOLED 2014-2021]")
c0, u0 = line("v1 |e|>=0.5 (live)", k0, e0); c1, u1 = line("v2 |e|>=0.62 (paper)", k1, e1)
print(f"  overlap: {int((k0 & k1).sum())} games in both; same side in {int((k0 & k1 & (np.sign(e0) == np.sign(e1))).sum())}")
print("\n[PER SEASON]")
wins = 0; per = []
for s in TEST:
    ks0, ks1 = k0 & (P.season == s), k1 & (P.season == s)
    print(f" season {s}: games {int((rows & (P.season == s)).sum())}")
    a0, b0 = line("v1", ks0, e0); a1, b1 = line("v2", ks1, e1)
    better = a1.mean() > a0.mean(); wins += int(better); per.append((s, a1.mean() - a0.mean(), b1.sum() - b0.sum()))
print("  CLV(v2) - CLV(v1) by season:", {s: round(d, 3) for s, d, _ in per}); print("  units(v2) - units(v1) by season:", {s: round(d, 1) for s, _, d in per})
D = c1.mean() - c0.mean(); DU = u1.sum() - u0.sum()
rng = np.random.default_rng(7); seas = P.season.values; idx = {s: np.where(rows.values & (seas == s))[0] for s in TEST}
cl_all, op_all, rs_all = close.values, opener.values, res.values; E0, E1 = e0.values, e1.values; Ds, DUs = [], []
def uu(sg, r):
    x = sg * (rs_all[r] - op_all[r]); return np.where(x > 0, 100 / 110, np.where(x < 0, -1.0, 0.0)).sum()
for _ in range(5000):
    r = np.concatenate([ix[rng.integers(0, len(ix), len(ix))] for ix in idx.values()])
    m0 = np.abs(E0[r]) >= T1; m1 = np.abs(E1[r]) >= T2; r0, r1 = r[m0], r[m1]
    s0, s1 = np.sign(E0[r0]), np.sign(E1[r1])
    Ds.append((s1 * (cl_all[r1] - op_all[r1])).mean() - (s0 * (cl_all[r0] - op_all[r0])).mean()); DUs.append(uu(s1, r1) - uu(s0, r0))
lo, hi = np.percentile(Ds, [5, 95]); ulo, uhi = np.percentile(DUs, [5, 95])
p1_ = D > 0 and lo > 0; p2_ = u1.sum() >= u0.sum(); p3_ = wins >= 5
print(f"\nP1 D = CLV(v2) - CLV(v1) = {D:+.3f} [90% {lo:+.3f}, {hi:+.3f}] -> {p1_}")
print(f"P2 units v2 {u1.sum():+.1f} >= v1 {u0.sum():+.1f} (difference {DU:+.1f}, 90% [{ulo:+.1f}, {uhi:+.1f}]) -> {p2_}")
print(f"P3 v2 CLV higher in {wins} of 8 seasons (need 5) -> {p3_}")
print("VERDICT:", "PASS" if (p1_ and p2_ and p3_) else "FAIL")
b2b = (P.h_rest_days <= 1) | (P.a_rest_days <= 1)
print("\n[DIAGNOSTICS, decide nothing]")
line("v1 back-to-back games", k0 & b2b, e0); line("v2 back-to-back games", k1 & b2b, e1)
line("v1 non-back-to-back", k0 & ~b2b, e0); line("v2 non-back-to-back", k1 & ~b2b, e1)
n0_ = int(k0.sum()); a = np.sort(e1[rows].abs().values)[::-1]; cut = a[n0_ - 1]
line(f"v2 matched to v1 count (cut {cut:.3f})", rows & (e1.abs() >= cut), e1)
r13 = base & (P.season == 2013)
print(f"\n[2012-13 separately, decides nothing] games {int(r13.sum())}")
line("v1 |e|>=0.5", r13 & (e0.abs() >= T1), e0); line("v2 |e|>=0.62", r13 & (e1.abs() >= T2), e1)
out = []
for nm, k, e in (("v1", k0 | (r13 & (e0.abs() >= T1)), e0), ("v2", k1 | (r13 & (e1.abs() >= T2)), e1)):
    clv, u, sg = grade(k, e)
    out.append(pd.DataFrame(dict(arm=nm, espn_id=P.espn_id[k].values, season=P.season[k].values, date=P.date[k].dt.date.values, home=P.home_name[k].values,
                                 away=P.away_name[k].values, opener_margin=opener[k].values, close_margin=close[k].values, margin=res[k].values,
                                 edge=e[k].round(3).values, side=sg, back_to_back=b2b[k].values, clv=clv, units=u.round(4))))
pd.concat(out).to_csv(os.path.join(W, "ncaab", "research", "stale_line_v2_sbr_bets.csv"), index=False)
