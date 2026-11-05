"""Grade research/CLOSE_MODEL_LAYER_PREREG_2026-11-05.md (pushed eb84784 before this ran): C3 vs C3 + layer for predicting the close from the opener.
  python ncaab/close_model_layer_grade.py WORKDIR -> research/close_model_layer_output.txt"""
import os, sys
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1])
FEATS = ["lost_min_share", "lost_pts_share", "new_starters", "travel_miles", "tz_shift", "rest_days", "back_to_back", "games_last_7"]
SBR = [2008, 2009, 2010, 2011, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
P = pd.read_csv(os.path.join(W, "ncaab", "data", "three_targets_preds.csv"), low_memory=False)
F = pd.read_csv(os.path.join(W, "derived", "lineup_travel_features.csv.gz"), low_memory=False).drop(columns=["season", "date"])
D = P.merge(F, on="espn_id", how="inner"); assert len(D) == len(P)
ok = (D.h_n_box >= 5) & (D.a_n_box >= 5) & D[["M2_m", "M8_m", "MKT_m", "M2_t", "M8_t", "MKT_t"]].notna().all(axis=1)
ok &= D[["h_" + f for f in FEATS] + ["a_" + f for f in FEATS]].notna().all(axis=1)
D = D[ok].copy()

def rows(mk, src):
    """src 'sbr': SBR open/close; 'book': book's own opener vs DK close."""
    d = D.copy()
    if mk == "s":
        o = d.open_sp if src == "sbr" else d.book_sp; c = d.close_sp
        g = o.notna() & c.notna()
        if src == "sbr": g &= ((o - c).abs() < 6) & ~((np.sign(o) != np.sign(c)) & (o.abs() >= 3) & (c.abs() >= 3))
        else: g &= ~((np.sign(o) != np.sign(c)) & (np.sign(o) != np.sign(d.open_sp)) & (o.abs() >= 1)) & ((o - c).abs() <= 10)
        d = d[g].copy(); d["op"] = -o[g]; d["cl"] = -c[g]; sfx = "m"
        for f in FEATS: d["x_" + f] = d["h_" + f] - d["a_" + f]
    else:
        o = d.open_tot if src == "sbr" else d.book_tot; c = d.close_tot
        g = o.notna() & c.notna() & ((o - c).abs() < 10)
        d = d[g].copy(); d["op"] = o[g]; d["cl"] = c[g]; sfx = "t"
        for f in FEATS: d["x_" + f] = d["h_" + f] + d["a_" + f]
    for e in ("M2", "M8", "MKT"): d["g_" + e] = d[f"{e}_{sfx}"] - d.op
    d["y"] = d.cl - d.op
    return d
COLS = {"C3": ["g_M2", "g_MKT", "g_M8"], "C3L": ["g_M2", "g_MKT", "g_M8"] + ["x_" + f for f in FEATS]}
def X(d, n): return np.c_[np.ones(len(d)), d[COLS[n]].values]
def fitpred(tr, te, n): b = np.linalg.lstsq(X(tr, n), tr.y.values, rcond=None)[0]; return X(te, n) @ b, b
rm = lambda e: np.sqrt(np.mean(e ** 2))
for mk, name in (("s", "SPREADS"), ("t", "TOTALS")):
    print(f"\n==================== {name} ====================")
    S = rows(mk, "sbr"); S = S[S.season.isin(SBR)]
    print("SBR rows", len(S), S.groupby("season").size().to_dict())
    out = []
    for s in SBR:
        tr, te = S[S.season != s], S[S.season == s]
        p3, _ = fitpred(tr, te, "C3"); pl, _ = fitpred(tr, te, "C3L"); out.append(te.assign(p3=p3, pl=pl))
    R = pd.concat(out); e0, e3, el = R.y.values, R.y - R.p3, R.y - R.pl
    dg = e3 ** 2 - el ** 2; gs = pd.Series(dg - dg.mean()).groupby(R.season.values).sum().values; G = len(gs)
    se = np.sqrt(G / (G - 1) * (gs ** 2).sum()) / len(dg); t = dg.mean() / se
    per = R.assign(d=dg).groupby("season").d.mean(); nimp = int((per > 0).sum())
    print(f"LOSO RMSE vs close: C0 {rm(e0):.4f} | C3 {rm(e3):.4f} (corr {np.corrcoef(R.p3, R.y)[0,1]:+.3f}) | C3L {rm(el):.4f} (corr {np.corrcoef(R.pl, R.y)[0,1]:+.3f})")
    print(f"MSE gain C3 - C3L {dg.mean():+.5f} (season-clustered t {t:+.2f}); seasons with a gain {nimp}/12")
    print("per-season MSE gain:", per.round(4).to_dict())
    _, bl = fitpred(S, S.iloc[:2], "C3L"); print("C3L coefficients fit on all 12 SBR seasons (const, gaps M2/MKT/M8, " + ", ".join(FEATS) + "):", np.round(bl, 3).tolist())
    B = rows(mk, "book"); FIT = B[(B.book == "DraftKings") & (B.season == 2024)]
    res3 = {}
    for lab, te in (("DK 2025-26", B[(B.book == "DraftKings") & (B.season == 2026)]), ("ESPN BET 2024-25 (decides nothing)", B[(B.book == "ESPN BET") & (B.season == 2025)])):
        p3, _ = fitpred(FIT, te, "C3"); pl, _ = fitpred(FIT, te, "C3L")
        r = (rm(te.y.values), rm(te.y - p3), rm(te.y - pl)); res3[lab] = r
        print(f"{lab}: n {len(te)} (fit DK 2023-24 n {len(FIT)}) | RMSE C0 {r[0]:.4f} C3 {r[1]:.4f} (corr {np.corrcoef(p3, te.y)[0,1]:+.3f}) C3L {r[2]:.4f} (corr {np.corrcoef(pl, te.y)[0,1]:+.3f})")
    p1, p2, p3_ = dg.mean() > 0 and t > 2, nimp >= 9, res3["DK 2025-26"][2] < res3["DK 2025-26"][1]
    print(f"P1 {p1} | P2 {p2} ({nimp}/12) | P3 {p3_} -> {name} {'PASS' if p1 and p2 and p3_ else 'FAIL'}")
