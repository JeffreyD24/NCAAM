"""Grade research/ROSTER_CONTINUITY_PREREG_2026-11-05.md (pushed 8054b0a before features were built). Run once.
  python ncaab/roster_grade.py WORKDIR -> research/roster_grade_output.txt, research/roster_dk_bets.csv"""
import os, sys
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1]); LAM = 10.0; BE = 0.67
HEAD = [2009, 2010, 2011] + list(range(2014, 2027)); TRAIN = [2009, 2010, 2011] + list(range(2014, 2022))
P = pd.read_csv(os.path.join(W, "ncaab", "data", "three_targets_preds.csv"), low_memory=False)
F = pd.read_csv(os.path.join(W, "derived", "roster_features.csv.gz")).drop(columns=["season"])
D = P.merge(F, on="espn_id", how="inner"); assert len(D) == len(P)
D["margin"] = D.home_pts - D.away_pts
RC = ["R1", "R2", "R3", "R4"]
for c in RC: D["s_" + c] = D["h_" + c] - D["a_" + c]
XC = ["s_" + c for c in RC]
ok = D.margin.notna() & D[XC].notna().all(axis=1) & D[["M2_m", "M8_m", "MKT_m"]].notna().all(axis=1)
ok &= D.h_n.between(1, 14) & D.a_n.between(1, 14)
D = D[ok].copy()
def ridge_fit(X, y):
    m, s = X.mean(0), X.std(0); s[s == 0] = 1; Z = (X - m) / s
    c = np.linalg.solve(Z.T @ Z + LAM * np.eye(Z.shape[1]), Z.T @ (y - y.mean())); return m, s, c, y.mean()
def blend_w(tr): return np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[["M2_m", "M8_m", "MKT_m"]].values], tr.margin.values, rcond=None)[0]
def fit_pred(tr, te, ref):
    """ref = column holding the market-implied home margin (close or opener). Returns pA, pR, roster part for te."""
    w = blend_w(tr); gap = lambda d: np.c_[np.ones(len(d)), d[["M2_m", "M8_m", "MKT_m"]].values] @ w - d[ref].values
    y = tr.margin.values - tr[ref].values
    mA, sA, cA, yA = ridge_fit(gap(tr)[:, None], y); pA = yA + ((gap(te)[:, None] - mA) / sA) @ cA
    Xtr, Xte = np.c_[gap(tr), tr[XC].values], np.c_[gap(te), te[XC].values]
    m, s, c, ym = ridge_fit(Xtr, y); Z = (Xte - m) / s
    return pA, ym + Z @ c, Z[:, 1:] @ c[1:]
def cl_slope(x, y, g):
    xd = x - x.mean(); yd = y - y.mean(); b = xd @ yd / (xd @ xd); e = yd - b * xd
    gs = pd.Series(xd * e).groupby(g).sum().values; G = len(gs); return b, b / (np.sqrt(G / (G - 1) * (gs ** 2).sum()) / (xd @ xd))
def robust(x, y):
    X = np.c_[np.ones(len(x)), x]; b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b; XtX = np.linalg.inv(X.T @ X)
    V = XtX @ (X.T * e ** 2) @ X @ XtX * len(x) / (len(x) - 2); return b[1], b[1] / np.sqrt(V[1, 1])
print("early-season rows with features:", len(D))

# ================= TEST 1: vs the close, LOSO over 16 seasons =================
C = D[D.close_sp.notna() & D.season.isin(HEAD)].copy()
g = C.open_sp.notna()
bad = g & (((C.open_sp - C.close_sp).abs() >= 6) | ((np.sign(C.open_sp) != np.sign(C.close_sp)) & (C.open_sp.abs() >= 3) & (C.close_sp.abs() >= 3)))
C = C[~bad].copy(); C["cl"] = -C.close_sp
print("\n==== TEST 1: beats the close (LOSO, 16 seasons) ====\nrows", len(C), C.groupby("season").size().to_dict())
out = []
for s in HEAD:
    tr, te = C[C.season != s], C[C.season == s]; pA, pR, rp = fit_pred(tr, te, "cl"); out.append(te.assign(pA=pA, pR=pR, rp=rp))
R = pd.concat(out); y = (R.margin - R.cl).values
b1, t1 = cl_slope(R.rp.values, y, R.season.values)
per = {s: (lambda x, yy: (x - x.mean()) @ (yy - yy.mean()) / ((x - x.mean()) @ (x - x.mean())))(x.rp.values, (x.margin - x.cl).values) for s, x in R.groupby("season")}
dl = (y - R.pA.values) ** 2 - (y - R.pR.values) ** 2; gs = pd.Series(dl - dl.mean()).groupby(R.season.values).sum().values; G = len(gs)
t3 = dl.mean() / (np.sqrt(G / (G - 1) * (gs ** 2).sum()) / len(dl)); npos = sum(v > 0 for v in per.values())
rm = lambda v: np.sqrt(np.mean(np.square(v)))
print(f"roster-part slope {b1:+.3f} (season-clustered t {t1:+.2f}); seasons positive {npos}/16; MSE gain A-R {dl.mean():+.4f} (t {t3:+.2f})")
print(f"RMSE vs result: close {rm(y):.3f} | A {rm(y - R.pA):.3f} | R {rm(y - R.pR):.3f}")
print("per-season slope:", {k: round(v, 2) for k, v in per.items()})
p1 = (b1 > 0 and t1 > 2), npos >= 11, (dl.mean() > 0 and t3 > 2)
print(f"PASS-1: (a) {p1[0]} (b) {p1[1]} (c) {p1[2]} -> {'PASS' if all(p1) else 'FAIL'}")
ws = blend_w(C); Xf = np.c_[np.c_[np.ones(len(C)), C[["M2_m", "M8_m", "MKT_m"]].values] @ ws - C.cl.values, C[XC].values]
m, s_, c, _ = ridge_fit(Xf, (C.margin - C.cl).values); print("standardized coefficients (gap, R1 turnover, R2 incoming, R3 lost strength, R4 imported strength):", np.round(c, 3).tolist())

# ================= TEST 2: DraftKings' own opener =================
print("\n==== TEST 2: DraftKings' own opener (fit SBR 2009-11, 2014-21; test DK 2024 + 2026) ====")
T = D[D.season.isin(TRAIN) & D.open_sp.notna() & D.close_sp.notna()].copy()
T = T[((T.open_sp - T.close_sp).abs() < 6) & ~((np.sign(T.open_sp) != np.sign(T.close_sp)) & (T.open_sp.abs() >= 3) & (T.close_sp.abs() >= 3))]; T["opm"] = -T.open_sp
E = D[(D.book == "DraftKings") & D.season.isin([2024, 2026]) & D.book_sp.notna() & D.close_sp.notna()].copy()
flip = (np.sign(E.book_sp) != np.sign(E.close_sp)) & (np.sign(E.book_sp) != np.sign(E.open_sp)) & (E.book_sp.abs() >= 1)
E = E[~flip & ((E.book_sp - E.close_sp).abs() <= 10)].copy(); E["opm"] = -E.book_sp
print("train rows", len(T), "| DK test rows", len(E), E.groupby("season").size().to_dict())
pA, pR, rp = fit_pred(T, E, "opm"); E["pA"], E["pR"], E["rp"] = pA, pR, rp
ex = (E.margin - E.opm).values; s2, t2 = robust(E.rp.values, ex); sm, tm = robust(E.rp.values, (E.book_sp - E.close_sp).values)
print(f"beat-the-opener slope of roster part {s2:+.3f} (robust t {t2:+.2f}) | roster part vs DK line move {sm:+.3f} (t {tm:+.2f})")
def top(d, col, q):
    keep = np.zeros(len(d), bool)
    for ss in d.season.unique():
        ix = np.where(d.season.values == ss)[0]; a = np.abs(d[col].values[ix]); n = int(np.ceil(q * len(ix))); keep[ix[a >= np.sort(a)[::-1][n - 1]]] = True
    b = d[keep].copy(); sd = np.sign(b[col].values); b["side"] = sd; b["clv"] = sd * (b.book_sp - b.close_sp)
    r = sd * (b.margin.values - b.opm.values); b["res"] = np.where(r > 0, 0.9091, np.where(r < 0, -1.0, 0.0)); return b
res = {}
for n in ("A", "R"):
    b = top(E, "p" + n, 0.05); res[n] = b; dec = b[b.res != 0]
    print(f" top 5% model {n}: {len(b)} bets, hit {(dec.res > 0).mean():.3f}, units {b.res.sum():+.1f} {b.groupby('season').res.sum().round(1).to_dict()}, CLV {b.clv.mean():+.3f}")
p2 = (s2 > 0 and t2 > 2), (res["R"].clv.mean() >= res["A"].clv.mean() and res["R"].clv.mean() >= BE)
print(f"PASS-2: (a) {p2[0]} (b) {p2[1]} -> {'PASS' if all(p2) else 'FAIL'}")
pd.concat([res[n].assign(model=n) for n in res])[["model", "espn_id", "season", "date", "home_name", "away_name", "book_sp", "close_sp", "margin", "side", "clv", "res", "pA", "pR", "rp", "h_n", "a_n"]].to_csv(
    os.path.join(W, "ncaab", "research", "roster_dk_bets.csv"), index=False)
