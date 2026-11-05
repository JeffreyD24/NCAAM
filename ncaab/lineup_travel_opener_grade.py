"""Grade v2 of the lineup/injury/travel layer at DraftKings' own opener, exactly as pre-registered in
ncaab/research/LINEUP_INJURY_TRAVEL_OPENER_PREREG_2026-11-05.md (pushed 438412a before this ran). Spreads only.
  python ncaab/lineup_travel_opener_grade.py WORKDIR   -> prints everything; output saved as research/lineup_travel_opener_grade_output.txt
Every bet is also written to research/lineup_travel_opener_bets.csv."""
import os, sys
import numpy as np, pandas as pd

W = os.path.abspath(sys.argv[1]); LAM = 10.0; BE = 0.67; KS = (0.5, 1, 1.5, 2, 3)
TRAIN = [2008, 2009, 2010, 2011, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
FEATS = ["lost_min_share", "lost_pts_share", "new_starters", "travel_miles", "tz_shift", "rest_days", "back_to_back", "games_last_7"]
P = pd.read_csv(os.path.join(W, "ncaab", "data", "three_targets_preds.csv"), low_memory=False)
F = pd.read_csv(os.path.join(W, "derived", "lineup_travel_features.csv.gz"), low_memory=False).drop(columns=["season", "date"])
D = P.merge(F, on="espn_id", how="inner"); assert len(D) == len(P)
D["margin"] = D.home_pts - D.away_pts
for c in FEATS: D["s_" + c] = D["h_" + c] - D["a_" + c]
XC = ["s_" + c for c in FEATS]
ok = D.margin.notna() & (D.h_n_box >= 5) & (D.a_n_box >= 5) & D[["M2_m", "M8_m", "MKT_m"]].notna().all(axis=1) & D[XC].notna().all(axis=1) & D.close_sp.notna()
D = D[ok].copy()

# ---------- training rows (SBR opener seasons)
T = D[D.season.isin(TRAIN) & D.open_sp.notna()].copy()
T = T[((T.open_sp - T.close_sp).abs() < 6) & ~((np.sign(T.open_sp) != np.sign(T.close_sp)) & (T.open_sp.abs() >= 3) & (T.close_sp.abs() >= 3))]
T["op"] = T.open_sp

# ---------- test rows (book's own opener)
E = D[D.season.isin([2024, 2025, 2026]) & D.book_sp.notna()].copy()
n0 = len(E)
flip = (np.sign(E.book_sp) != np.sign(E.close_sp)) & (np.sign(E.book_sp) != np.sign(E.open_sp)) & (E.book_sp.abs() >= 1)
far = (E.book_sp - E.close_sp).abs() > 10
E = E[~flip & ~far].copy(); E["op"] = E.book_sp
E["b2b"] = (E.h_rest_days <= 1) | (E.a_rest_days <= 1)
print(f"training rows {len(T)} ({T.season.min()}-{T.season.max()}, {T.season.nunique()} seasons) | test rows with a book opener {n0}, "
      f"flipped dropped {int(flip.sum())}, |open-close|>10 dropped {int(far.sum())}, kept {len(E)}")
print(E.groupby(["book", "season", "b2b"]).size().to_string())

def fit(tr):
    w = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[["M2_m", "M8_m", "MKT_m"]].values], tr.margin.values, rcond=None)[0]
    def gap(d): return np.c_[np.ones(len(d)), d[["M2_m", "M8_m", "MKT_m"]].values] @ w + d.op.values   # blend - (-opener)
    y = tr.margin.values + tr.op.values; g = gap(tr); out = {"w": w, "ym": y.mean()}
    for name, cols in (("A", []), ("B", XC)):
        X = np.c_[g, tr[cols].values] if cols else g[:, None]
        m, s = X.mean(0), X.std(0); s[s == 0] = 1
        Z = (X - m) / s; c = np.linalg.solve(Z.T @ Z + LAM * np.eye(Z.shape[1]), Z.T @ (y - y.mean()))
        out[name] = (cols, m, s, c)
    out["gap"] = gap; return out
def predict(M, d, name):
    cols, m, s, c = M[name]; g = M["gap"](d)
    X = np.c_[g, d[cols].values] if cols else g[:, None]; Z = (X - m) / s
    return M["ym"] + Z @ c, (Z[:, 1:] @ c[1:] if cols else np.zeros(len(d)))

def bets(d, pred, k):
    b = d[np.abs(pred) >= k].copy(); side = np.sign(pred[np.abs(pred) >= k]); b["side"] = side   # +1 home, -1 away
    b["clv"] = side * (b.op - b.close_sp)
    res = side * (b.margin + b.op); b["res"] = np.where(res > 0, 0.9091, np.where(res < 0, -1.0, 0.0)); return b

# ---------- choose k inside the training seasons (leave-one-season-out CLV)
K = {}
for name in ("A", "B"):
    loso = {k: [] for k in KS}
    for s in TRAIN:
        M = fit(T[T.season != s]); te = T[T.season == s]; pr, _ = predict(M, te, name)
        for k in KS: loso[k].append(bets(te, pr, k))
    line = []
    for k in KS:
        bb = pd.concat(loso[k]); line.append(f"k {k}: {len(bb)} bets CLV {bb.clv.mean():+.3f} units {bb.res.sum():+.1f}")
    K[name] = next((k for k in KS if pd.concat(loso[k]).clv.mean() >= BE), 3)
    print(f"[train LOSO, model {name}] " + " | ".join(line) + f"  -> k = {K[name]}")

M = fit(T)
print("blend weights (1, M2, M8, MKT):", np.round(M["w"], 3))
print("model B standardized coefficients (gap, " + ", ".join(FEATS) + "):", np.round(M["B"][3], 3))
for name in ("A", "B"): E["pred" + name], E["ly" + name] = predict(M, E, name)

rng = np.random.default_rng(7)
def boot_lo(x):
    x = np.asarray(x); idx = rng.integers(0, len(x), (5000, len(x))); mm = x[idx].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
def robust(x, y):
    X = np.c_[np.ones(len(x)), x]; b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    XtX = np.linalg.inv(X.T @ X); V = XtX @ (X.T * e ** 2) @ X @ XtX * len(x) / (len(x) - 2); return b[1], b[1] / np.sqrt(V[1, 1])
def summary(d, name, tag):
    b = bets(d, d["pred" + name].values, K[name])
    if len(b) == 0: print(f"  [{tag}] model {name}: no bets"); return None
    lo, hi = boot_lo(b.clv); dec = b[b.res != 0]; hit = (dec.res > 0).mean() if len(dec) else np.nan
    per = b.groupby("season").res.sum().round(1).to_dict(); perc = b.groupby("season").clv.mean().round(2).to_dict()
    print(f"  [{tag}] model {name} k {K[name]}: {len(b)} bets, hit {hit:.3f}, units {b.res.sum():+.1f} (ROI {b.res.sum()/len(b):+.3f}), "
          f"CLV {b.clv.mean():+.3f} [90% {lo:+.3f}, {hi:+.3f}] | units by season {per} | CLV by season {perc}")
    return dict(n=len(b), clv=b.clv.mean(), lo=lo, units=b.res.sum(), per=per, bets=b)

print("\n==== TEST: DraftKings openers, 2024 + 2026, timing-guarded (headline) ====")
H = E[(E.book == "DraftKings") & E.season.isin([2024, 2026]) & ~E.b2b]
print("games", len(H), H.groupby("season").size().to_dict())
R = {n: summary(H, n, "DK headline") for n in ("A", "B")}
ex_o = (H.margin + H.op).values; mv = (H.op - H.close_sp).values   # home-perspective opener excess and line move toward home
s3, t3 = robust(H.lyB.values, ex_o); s3c, t3c = robust(H.lyB.values, mv)
sA, tA = robust((H.predA - H.predA.mean()).values, ex_o); sB, tB = robust((H.predB - H.predB.mean()).values, ex_o)
print(f"  beat-the-opener slope: layer part {s3:+.3f} (t {t3:+.2f}) | layer part vs line move (close-opener) {s3c:+.3f} (t {t3c:+.2f}) | "
      f"full A {sA:+.3f} (t {tA:+.2f}) | full B {sB:+.3f} (t {tB:+.2f})")
rm = lambda v: np.sqrt(np.mean(np.square(v)))
print(f"  RMSE vs result: DK opener {rm(ex_o):.3f} | DK close {rm(H.margin + H.close_sp):.3f} | model A {rm(ex_o - H.predA):.3f} | model B {rm(ex_o - H.predB):.3f}")

print("\n==== PASS / FAIL (model B) ====")
b = R["B"]; a = R["A"]
q1 = b is not None and b["clv"] >= BE and b["lo"] > 0
q2 = b is not None and b["units"] > 0 and min(b["per"].values()) >= -5
q3 = s3 > 0 and t3 > 2
q4 = b is not None and a is not None and b["clv"] >= a["clv"]
if b is not None:
    print(f"Q1 CLV >= {BE} and 90% low > 0: {q1} (CLV {b['clv']:+.3f}, low {b['lo']:+.3f})")
    print(f"Q2 units > 0 and no season < -5u: {q2} (units {b['units']:+.1f}, by season {b['per']})")
print(f"Q3 layer beat-the-opener slope > 0, t > 2: {q3} (slope {s3:+.3f}, t {t3:+.2f})")
if a is not None and b is not None: print(f"Q4 CLV B >= CLV A: {q4} (B {b['clv']:+.3f} vs A {a['clv']:+.3f})")
print("VERDICT:", "PASS" if (q1 and q2 and q3 and q4) else "FAIL")

print("\n==== Diagnostic: units at the recorded DraftKings opening price (home-side bets only; ESPN's feed records only the home price) ====")
O = pd.read_csv(os.path.join(W, "ncaab", "data", "espn_openers.csv"), low_memory=False)
px = O[O.provider == "DraftKings"].drop_duplicates("espn_id").set_index("espn_id").open_spread_px
if b is not None:
    hb = b["bets"][b["bets"].side > 0].copy(); hb["px"] = hb.espn_id.map(px); hb = hb[hb.px.notna() & (hb.res != 0)]
    pay = np.where(hb.px < 0, 100 / -hb.px, hb.px / 100); u = np.where(hb.res > 0, pay, -1.0)
    print(f"  model B home-side bets with a price: {len(hb)}, units at recorded price {u.sum():+.1f} vs at -110 {hb.res.sum():+.1f}, mean price {hb.px.mean():.1f}")

print("\n==== Secondary (decide nothing) ====")
for tag, sub in (("ESPN BET 2025 (not in CT)", E[(E.book == "ESPN BET") & (E.season == 2025) & ~E.b2b]),
                 ("DK back-to-back games (timing unsafe)", E[(E.book == "DraftKings") & E.season.isin([2024, 2026]) & E.b2b]),
                 ("ESPN BET gaps in 2024/2026", E[(E.book == "ESPN BET") & E.season.isin([2024, 2026]) & ~E.b2b])):
    print(f" {tag}: games {len(sub)}")
    for n in ("A", "B"): summary(sub, n, tag)
    if len(sub) > 50:
        s_, t_ = robust(sub.lyB.values, (sub.margin + sub.op).values); print(f"   layer beat-the-opener slope {s_:+.3f} (t {t_:+.2f})")

out = pd.concat([R[n]["bets"].assign(model=n) for n in ("A", "B") if R[n] is not None])
out[["model", "espn_id", "season", "date", "home_name", "away_name", "book", "op", "close_sp", "margin", "side", "clv", "res", "predA", "predB", "lyB"]].to_csv(
    os.path.join(W, "ncaab", "research", "lineup_travel_opener_bets.csv"), index=False)
print("\nbets saved:", len(out))
