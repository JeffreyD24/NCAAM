# Fable live-code review check (Nov 5, 2026), copied from the reviewer's scratch script: stale-line v2 at the single live threshold 0.62 vs the matched-count grading, back-to-back split, stale lineup features. W is hard-coded to the NCAAM clone.
import os, sys
import numpy as np, pandas as pd
W = "/home/claude/ncaam"
P = pd.read_csv(os.path.join(W, "ncaab", "data", "model3_preds.csv"), low_memory=False); P["date"] = pd.to_datetime(P.date)
LT = pd.read_csv(os.path.join(W, "derived", "lineup_travel_features.csv.gz")).drop(columns=["season", "date"])
RO = pd.read_csv(os.path.join(W, "derived", "roster_features.csv.gz")).drop(columns=["season"])
P = P.merge(LT, on="espn_id", how="left").merge(RO, on="espn_id", how="left")
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
    return pd.Series(pred, index=P.index)
p0 = stack(X0); p1 = stack(X1); e0, e1 = p0 - opener, p1 - opener
flip = (np.sign(P.book_sp) != np.sign(P.close_sp)) & (np.sign(P.book_sp) != np.sign(P.open_sp)) & (P.book_sp.abs() >= 1)
base = pd.Series(ok, index=P.index) & opener.notna() & close.notna() & res.notna() & p0.notna() & p1.notna() & ~flip & ((P.book_sp - P.close_sp).abs() <= 10)
b2b = (P.h_rest_days <= 1) | (P.a_rest_days <= 1)
DK = base & (P.book == "DraftKings") & P.season.isin([2024, 2026])
def grade(k, e):
    sg = np.sign(e[k]); clv = sg * (close[k] - opener[k]); r = sg * (res[k] - opener[k]); u = np.where(r > 0, 100 / 110, np.where(r < 0, -1.0, 0.0))
    return clv.values, u
def show(nm, k, e):
    clv, u = grade(k, e); w, l = (u > 0).sum(), (u < 0).sum()
    per = pd.Series(u, index=P.season[k].values).groupby(level=0).sum().round(1).to_dict()
    print(f"  {nm:45s} {int(k.sum()):4d} bets {w / max(w + l, 1):.1%} {u.sum():+7.1f}u {per} CLV {clv.mean():+.3f}")
print("A) fixed live threshold 0.62 vs matched cuts, DK 2024+2026")
show("S0 |e0|>=0.5", DK & (e0.abs() >= 0.5), e0)
show("S1 fixed |e1|>=0.62 (LIVE rule)", DK & (e1.abs() >= 0.62), e1)
for s, c in ((2024, 0.6330), (2026, 0.6070)):
    show(f"S1 season {s} matched cut {c}", DK & (P.season == s) & (e1.abs() >= c), e1)
print("B) back-to-back split (either team rest_days<=1): where live lineup features would be one game staler than the backtest")
k1 = DK & (e1.abs() >= 0.62); k0 = DK & (e0.abs() >= 0.5)
show("S1 0.62, b2b games", k1 & b2b, e1); show("S1 0.62, non-b2b", k1 & ~b2b, e1)
show("S0 0.5, b2b games", k0 & b2b, e0); show("S0 0.5, non-b2b", k0 & ~b2b, e0)
# C) stale-lineup simulation: for b2b teams zero out the lineup features (lost_min, lost_pts, new_starters) as the live job cannot have them
Xs = X1.copy()
for i, f in enumerate(LF[:3]):
    hz = (P.h_rest_days <= 1).values; az = (P.a_rest_days <= 1).values
    col = 5 + i
    # if home team is b2b its lineup feature is unknown live -> treat as missing: diff uses only away side (missing->0 for that side)
    hv = P["h_" + f].where(~hz, np.nan); av = P["a_" + f].where(~az, np.nan)
    Xs[:, col] = (hv - av).fillna(0).values
def stack_pred(Xfit, Xapply):
    pred = np.full(len(P), np.nan); y = close.values
    for s in (2024, 2026):
        tr = (P.season < s).values & ok & ~np.isnan(Xfit).any(axis=1) & ~np.isnan(y)
        b = np.linalg.lstsq(Xfit[tr], y[tr], rcond=None)[0]; te = (P.season == s).values; pred[te] = Xapply[te] @ b
    return pd.Series(pred, index=P.index)
ps = stack_pred(X1, Xs); es = ps - opener
print("C) S1 coefficients applied with b2b teams' lineup features treated as unknown (live situation)")
show("S1-stale 0.62 all", DK & (es.abs() >= 0.62), es); show("S1-stale 0.62 b2b", DK & (es.abs() >= 0.62) & b2b, es)
print("   S1 vs S1-stale bet-set overlap:", int((k1 & (es.abs() >= 0.62)).sum()), "of", int(k1.sum()))
print("D) share of S1 bets whose layer diffs are all zero (no features) and early-season share")
z = (np.abs(feat).sum(axis=1) == 0)
print("   S1 0.62 bets with all-zero layer diffs:", int((k1 & z).sum()), "of", int(k1.sum()))
print("   S1 0.62 bets by month:", P.date[k1].dt.month.value_counts().sort_index().to_dict())
print("E) distribution of |e1-e0| on DK rows:", np.round(np.percentile((e1 - e0)[DK].abs(), [50, 90, 99]), 3))
