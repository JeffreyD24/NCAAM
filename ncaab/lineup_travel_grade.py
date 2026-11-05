"""Grade the lineup / inferred-injury / travel layer exactly as pre-registered in
ncaab/research/LINEUP_INJURY_TRAVEL_PREREG_2026-11-05.md.   python ncaab/lineup_travel_grade.py WORKDIR
Reads ncaab/data/three_targets_preds.csv and derived/lineup_travel_features.csv.gz. Prints everything; run once, output saved next to this file."""
import os, sys
import numpy as np, pandas as pd

W = os.path.abspath(sys.argv[1]); LAM = 10.0
HEAD = [s for s in range(2008, 2027) if s not in (2012, 2013)]; WEAK = [2012, 2013]
P = pd.read_csv(os.path.join(W, "ncaab", "data", "three_targets_preds.csv"), low_memory=False)
F = pd.read_csv(os.path.join(W, "derived", "lineup_travel_features.csv.gz"), low_memory=False).drop(columns=["season", "date"])
D = P.merge(F, on="espn_id", how="inner"); assert len(D) == len(P), (len(D), len(P))
D["margin"] = D.home_pts - D.away_pts; D["total"] = D.home_pts + D.away_pts
D["C_s"] = -D.close_sp; D["C_t"] = D.close_tot
D["ex_s"] = D.margin - D.C_s; D["ex_t"] = D.total - D.C_t
print("sign check corr(M2_m, close-implied margin) =", round(D[["M2_m", "C_s"]].corr().iloc[0, 1], 3), "| corr(M2_t, close total) =", round(D[["M2_t", "C_t"]].corr().iloc[0, 1], 3))
ok = D.close_sp.notna() & D.close_tot.notna() & D.margin.notna() & (D.h_n_box >= 5) & (D.a_n_box >= 5)
ok &= ~(D.open_sp.notna() & ((D.open_sp - D.close_sp).abs() >= 6))
ok &= D[["M2_m", "M8_m", "MKT_m", "M2_t", "M8_t", "MKT_t"]].notna().all(axis=1) & D.season.isin(HEAD + WEAK)
D = D[ok].copy(); print("games after filters", len(D)); print(D.groupby("season").size().to_string().replace("\n", "; "))

BASE = {"s": ["M2_m", "M8_m", "MKT_m"], "t": ["M2_t", "M8_t", "MKT_t"]}
BASE_T = {"s": "margin", "t": "total"}; CL = {"s": "C_s", "t": "C_t"}; EX = {"s": "ex_s", "t": "ex_t"}
# feature columns: spreads = home - away, totals = home + away
RAW = {"lost_min_share": "A", "lost_pts_share": "B", "new_starters": "C", "travel_miles": "D", "tz_shift": "E", "rest_days": "F", "back_to_back": "G", "games_last_7": "H"}
for mk in "st":
    for c in RAW: D[f"{mk}_{c}"] = (D["h_" + c] - D["a_" + c]) if mk == "s" else (D["h_" + c] + D["a_" + c])
for mk in "st":
    for c in ("lost_min_share", "lost_pts_share"): D[f"{mk}_oracle_{c.split('_')[1]}"] = (D["h_oracle_lost_" + c.split("_")[1]] - D["a_oracle_lost_" + c.split("_")[1]]) if mk == "s" else (D["h_oracle_lost_" + c.split("_")[1]] + D["a_oracle_lost_" + c.split("_")[1]])
SETS = {"ALL": list(RAW), "LINEUP": ["lost_min_share", "lost_pts_share", "new_starters"], "TRAVEL": ["travel_miles", "tz_shift", "rest_days", "back_to_back", "games_last_7"]}

def ols(X, y):
    X1 = np.c_[np.ones(len(X)), X]; return np.linalg.lstsq(X1, y, rcond=None)[0]
def ridge(Z, y):
    return np.linalg.solve(Z.T @ Z + LAM * np.eye(Z.shape[1]), Z.T @ (y - y.mean()))
def fit_predict(tr, te, mk, feats):
    """returns (predA, predB_full, layer_part) predicted EXCESS (actual - close) for te rows; base blend + ridge fitted on tr only."""
    bc = BASE[mk]; w = ols(tr[bc].values, tr[BASE_T[mk]].values)
    gap_tr = np.c_[np.ones(len(tr)), tr[bc].values] @ w - tr[CL[mk]].values
    gap_te = np.c_[np.ones(len(te)), te[bc].values] @ w - te[CL[mk]].values
    y = tr[EX[mk]].values
    # model A: gap only
    m, s = gap_tr.mean(), gap_tr.std(); s = s or 1.0
    cA = ridge(((gap_tr - m) / s)[:, None], y); pA = y.mean() + (((gap_te - m) / s)[:, None] @ cA)
    cols = [f"{mk}_{f}" for f in feats]
    Xtr = np.c_[gap_tr, tr[cols].values]; Xte = np.c_[gap_te, te[cols].values]
    xm, xs = Xtr.mean(0), Xtr.std(0); xs[xs == 0] = 1.0
    cB = ridge((Xtr - xm) / xs, y); Zte = (Xte - xm) / xs
    pB = y.mean() + Zte @ cB; layer = Zte[:, 1:] @ cB[1:]
    return pA, pB, layer

def cl_slope(x, y, g):
    xd = x - x.mean(); e = (y - y.mean()) - (xd @ (y - y.mean())) / (xd @ xd) * xd; b = (xd @ (y - y.mean())) / (xd @ xd)
    gs = pd.Series(xd * e).groupby(g.values).sum().values; G = len(gs)
    if G < 2: return b, np.nan  # single season (weak-season rows): no clustered SE
    se = np.sqrt(G / (G - 1) * (gs ** 2).sum()) / (xd @ xd); return b, se
def cl_mean(d, g):
    dm = d.mean(); gs = pd.Series(d - dm).groupby(g.values).sum().values; G = len(gs)
    if G < 2: return dm, np.nan
    se = np.sqrt(G / (G - 1) * (gs ** 2).sum()) / len(d); return dm, se

def run(mk, fname, design="loso", sub=None, oracle=False):
    feats = SETS[fname] if not oracle else ["oracle_min", "oracle_pts", "new_starters"]
    cols = [f"{mk}_{f}" for f in feats]
    Dm = D[D[cols].notna().all(axis=1)] if sub is None else D[D[cols].notna().all(axis=1)]
    res = []
    if design == "loso":
        for s in HEAD:
            tr = Dm[Dm.season.isin(HEAD) & (Dm.season != s)]; te = Dm[Dm.season == s]
            if len(te) == 0: continue
            pA, pB, ly = fit_predict(tr, te, mk, feats); res.append(te.assign(pA=pA, pB=pB, ly=ly))
    elif design == "forward":
        for s in [x for x in HEAD if x >= 2016]:
            tr = Dm[Dm.season.isin(HEAD) & (Dm.season < s)]; te = Dm[Dm.season == s]
            pA, pB, ly = fit_predict(tr, te, mk, feats); res.append(te.assign(pA=pA, pB=pB, ly=ly))
    elif design == "weak":
        tr = Dm[Dm.season.isin(HEAD)]
        for s in WEAK:
            te = Dm[Dm.season == s]
            if len(te): pA, pB, ly = fit_predict(tr, te, mk, feats); res.append(te.assign(pA=pA, pB=pB, ly=ly))
    return pd.concat(res)

def report(R, mk, tag):
    y = R[EX[mk]].values; g = R.season; n = len(R)
    b1, s1 = cl_slope(R.ly.values, y, g); b2, s2 = cl_slope(R.pB.values, y, g)
    dA = (y - R.pA.values) ** 2; dB = (y - R.pB.values) ** 2; dm, dse = cl_mean(dA - dB, g)
    def _slope(x_, y_): xd_ = x_ - x_.mean(); return (xd_ @ (y_ - y_.mean())) / (xd_ @ xd_)
    per = {s: _slope(x.ly.values, x[EX[mk]].values) for s, x in R.groupby("season")}
    pos = sum(v > 0 for v in per.values())
    rm = lambda v: np.sqrt(np.mean(v))
    # diagnostic bets at the close: sign of full prediction, |pred| >= 1
    bet = R[np.abs(R.pB) >= 1]; win = np.sign(bet.pB) == np.sign(bet[EX[mk]]); push = bet[EX[mk]] == 0
    units = (win & ~push).sum() * 0.9091 - (~win & ~push).sum(); hit = (win & ~push).sum() / max((~push).sum(), 1)
    print(f"[{tag}] {mk=} n={n} seasons={R.season.nunique()} | layer slope {b1:+.3f} (t {b1/s1:+.2f}); full-model slope {b2:+.3f} (t {b2/s2:+.2f}); "
          f"seasons with layer slope>0: {pos}/{len(per)} | MSE A-B {dm:+.4f} (t {dm/dse:+.2f}) | RMSE close {rm(y**2):.3f} A {rm(dA):.3f} B {rm(dB):.3f} | "
          f"close bets |pred|>=1: n={len(bet)} hit {hit:.3f} units {units:+.1f}")
    return dict(t1=b1 / s1, pos=pos, G=len(per), t3=dm / dse, per=per)

print("\n==== PRIMARY: leave-one-season-out, 17 headline seasons ====")
OUT = {}
for mk in "st":
    for fn in ("ALL", "LINEUP", "TRAVEL"):
        R = run(mk, fn); OUT[(mk, fn)] = report(R, mk, f"LOSO {fn}")
print("\n==== PASS / FAIL (ALL set; P1 layer slope t>2, P2 >=12 of 17 seasons positive, P3 MSE improvement t>2) ====")
for mk in "st":
    o = OUT[(mk, "ALL")]; p1 = o["t1"] > 2; p2 = o["pos"] >= 12; p3 = o["t3"] > 2
    print(f"{'spreads' if mk=='s' else 'totals'}: P1 {p1} (t {o['t1']:+.2f}), P2 {p2} ({o['pos']}/{o['G']}), P3 {p3} (t {o['t3']:+.2f}) -> {'PASS' if p1 and p2 and p3 else 'FAIL'}")
print("group-level (need t>2.5 on P1 and P3):")
for mk in "st":
    for fn in ("LINEUP", "TRAVEL"):
        o = OUT[(mk, fn)]; print(f"  {'spreads' if mk=='s' else 'totals'} {fn}: P1 t {o['t1']:+.2f} ({o['t1']>2.5}), P3 t {o['t3']:+.2f} ({o['t3']>2.5})")
print("\nper-season layer slopes (ALL):")
for mk in "st": print(mk, {s: round(v, 2) for s, v in OUT[(mk, 'ALL')]["per"].items()})
print("\n==== SECONDARY: forward (train on earlier seasons only), 2016-2026 ====")
for mk in "st":
    for fn in ("ALL",): report(run(mk, fn, "forward"), mk, f"FORWARD {fn}")
print("\n==== WEAK SEASONS 2012, 2013 (fit on headline seasons; not pooled) ====")
for mk in "st":
    R = run(mk, "ALL", "weak")
    for s, x in R.groupby("season"): report(x, mk, f"WEAK {s}")
print("\n==== ORACLE (in-game box score; NOT tradable; diagnostic) LINEUP set with oracle absences ====")
for mk in "st": report(run(mk, "LINEUP", oracle=True), mk, "ORACLE")
