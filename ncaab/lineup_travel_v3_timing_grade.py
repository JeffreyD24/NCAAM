"""Grade two pre-registrations (pushed 6052a78 before this ran), reusing v2's exact data prep and models from ncaab/lineup_travel_opener_grade.py:
  research/LINEUP_INJURY_TRAVEL_V3_MATCHED_PREREG_2026-11-05.md  (model B vs A at matched bet counts, DK opener)
  research/LINEUP_INJURY_TRAVEL_TIMING_PREREG_2026-11-05.md      (bet base picks at the opener or wait for the close, by the layer's predicted move)
  python ncaab/lineup_travel_v3_timing_grade.py WORKDIR  -> research/lineup_travel_v3_timing_output.txt, research/lineup_travel_v3_bets.csv, research/lineup_travel_timing_bets.csv"""
import os, sys
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1])
src = open(os.path.join(W, "ncaab", "lineup_travel_opener_grade.py")).read().split("# ---------- choose k")[0]
ns = {"__name__": "v2"}; sys.argv = ["x", W]; exec(src, ns)
T, E, fit, predict, bets, XC, TRAIN, LAM, BE = (ns[k] for k in ("T", "E", "fit", "predict", "bets", "XC", "TRAIN", "LAM", "BE"))
M = fit(T)
for n in ("A", "B"): E["pred" + n], _ = predict(M, E, n)
H = E[(E.book == "DraftKings") & E.season.isin([2024, 2026]) & ~E.b2b].reset_index(drop=True)
S2 = E[(E.book == "ESPN BET") & (E.season == 2025) & ~E.b2b].reset_index(drop=True)
rng = np.random.default_rng(7)
def grade(d, side):  # returns clv, result units per bet at the opener
    clv = side * (d.op.values - d.close_sp.values); r = side * (d.margin.values + d.op.values)
    return clv, np.where(r > 0, 0.9091, np.where(r < 0, -1.0, 0.0))
def topq(d, col, q):
    keep = np.zeros(len(d), bool)
    for s in d.season.unique():
        ix = np.where(d.season.values == s)[0]; a = np.abs(d[col].values[ix]); n = int(np.ceil(q * len(ix)))
        thr = np.sort(a)[::-1][n - 1]; keep[ix[a >= thr]] = True
    return keep
def boot(x):
    x = np.asarray(x); i = rng.integers(0, len(x), (5000, len(x))); m = x[i].mean(1); return np.percentile(m, 5), np.percentile(m, 95)

# =================== v3 ===================
print("\n==================== v3: matched bet counts (DK 2024 + 2026, timing-guarded) ====================")
print("games", len(H), H.groupby("season").size().to_dict())
R = {}; allbets = []
for q in (0.01, 0.02, 0.05, 0.10):
    row = {}
    for n in ("A", "B"):
        k = topq(H, "pred" + n, q); d = H[k]; side = np.sign(d["pred" + n].values); c, u = grade(d, side); lo, hi = boot(c)
        dec = u != 0; per = pd.Series(u, index=d.season.values).groupby(level=0).sum().round(1).to_dict()
        row[n] = dict(set=set(d.espn_id), clv=c.mean(), lo=lo, hi=hi, units=u.sum(), per=per, n=len(d), hit=(u[dec] > 0).mean(), tot=c.sum())
        allbets.append(d.assign(model=n, q=q, side=side, clv=c, res=u))
        print(f" q {q:.0%} model {n}: {len(d)} bets, hit {row[n]['hit']:.3f}, units {u.sum():+.1f} {per}, CLV {c.mean():+.3f} [90% {lo:+.3f}, {hi:+.3f}], total CLV {c.sum():.1f}")
    # joint bootstrap of D (resample games within season, rebuild both top-q sets)
    Ds = []; seas = H.season.values; idx_by = {s: np.where(seas == s)[0] for s in np.unique(seas)}
    pa, pb = H.predA.values, H.predB.values; clvA = np.sign(pa) * (H.op.values - H.close_sp.values); clvB = np.sign(pb) * (H.op.values - H.close_sp.values)
    for _ in range(5000):
        sa, sb = [], []
        for s, ix in idx_by.items():
            r = ix[rng.integers(0, len(ix), len(ix))]; n = int(np.ceil(q * len(r)))
            for p, cl, out in ((pa, clvA, sa), (pb, clvB, sb)):
                a = np.abs(p[r]); thr = np.sort(a)[::-1][n - 1]; out.append(cl[r][a >= thr])
        Ds.append(np.concatenate(sb).mean() - np.concatenate(sa).mean())
    D = row["B"]["clv"] - row["A"]["clv"]; dlo, dhi = np.percentile(Ds, 5), np.percentile(Ds, 95)
    ov = row["A"]["set"] & row["B"]["set"]
    print(f"   D = CLV(B) - CLV(A) = {D:+.3f} [90% {dlo:+.3f}, {dhi:+.3f}] | overlap {len(ov)} of A {row['A']['n']} / B {row['B']['n']}")
    R[q] = dict(D=D, dlo=dlo, **{n: row[n] for n in ("A", "B")})
b2 = R[0.02]["B"]
r1 = R[0.02]["D"] > 0 and R[0.02]["dlo"] > 0
r2 = sum(R[q]["D"] > 0 for q in R) >= 3
r3 = b2["clv"] >= BE and b2["lo"] > 0 and b2["units"] > 0 and min(b2["per"].values()) >= -5
print(f"\nR1 (q 2%: D > 0 and 90% low > 0): {r1} (D {R[0.02]['D']:+.3f}, low {R[0.02]['dlo']:+.3f})")
print(f"R2 (D > 0 at >= 3 of 4 fractions): {r2} ({[round(R[q]['D'], 3) for q in R]})")
print(f"R3 (B at q 2%: CLV >= {BE}, low > 0, units > 0, no season < -5u): {r3} (CLV {b2['clv']:+.3f}, low {b2['lo']:+.3f}, units {b2['units']:+.1f} {b2['per']})")
print("v3 VERDICT:", "PASS (weaker evidence: third look at these seasons)" if (r1 and r2 and r3) else "FAIL")
print("\n v3 secondary, ESPN BET 2025 (decides nothing):")
for q in (0.02,):
    for n in ("A", "B"):
        d = S2[topq(S2, "pred" + n, q)]; c, u = grade(d, np.sign(d["pred" + n].values)); print(f"  q {q:.0%} model {n}: {len(d)} bets, CLV {c.mean():+.3f}, units {u.sum():+.1f}")
pd.concat(allbets)[["model", "q", "espn_id", "season", "date", "home_name", "away_name", "op", "close_sp", "margin", "side", "clv", "res", "predA", "predB"]].to_csv(
    os.path.join(W, "ncaab", "research", "lineup_travel_v3_bets.csv"), index=False)

# =================== timing ===================
print("\n==================== Bet timing: opener or wait for the close ====================")
def move_fit(tr, Mf, cols):
    g = Mf["gap"](tr); X = np.c_[g, tr[cols].values] if cols else g[:, None]; y = (tr.op - tr.close_sp).values
    m, s = X.mean(0), X.std(0); s[s == 0] = 1; Z = (X - m) / s
    c = np.linalg.solve(Z.T @ Z + LAM * np.eye(Z.shape[1]), Z.T @ (y - y.mean()))
    def pr(d):
        gg = Mf["gap"](d); XX = np.c_[gg, d[cols].values] if cols else gg[:, None]; return y.mean() + ((XX - m) / s) @ c
    return pr
TS = (0, 0.25, 0.5, 0.75)
def timing(d, predA, mv, t):
    k = np.abs(predA) >= 1; dd = d[k]; side = np.sign(predA[k]); m = side * mv[k]; wait = m <= -t
    gain = side * (dd.close_sp.values - dd.op.values)                      # line at close minus line at opener, bet direction
    ro = side * (dd.margin.values + dd.op.values); rc = side * (dd.margin.values + dd.close_sp.values)
    u = lambda r: np.where(r > 0, 0.9091, np.where(r < 0, -1.0, 0.0))
    uo, uc = u(ro), u(rc); ut = np.where(wait, uc, uo)
    return dict(n=len(dd), nw=int(wait.sum()), gain=gain[wait], uo=uo.sum(), uc=uc.sum(), ut=ut.sum(), dd=dd.assign(side=side, m=m, wait=wait, gain=gain, res_open=uo, res_close=uc, res_timing=ut))
# choose t in training, leave one season out (layer move model)
pooled = {t: 0.0 for t in TS}
for s in TRAIN:
    tr, te = T[T.season != s], T[T.season == s]; Mf = fit(tr); pa, _ = predict(Mf, te, "A"); pm = move_fit(tr, Mf, XC)(te)
    for t in TS: pooled[t] += timing(te, pa, pm, t)["gain"].sum()
print("training LOSO points gained by t:", {t: round(v, 1) for t, v in pooled.items()})
best = max(pooled.values()); tstar = max(t for t in TS if pooled[t] == best); print("chosen t =", tstar)
mvL = move_fit(T, M, XC); mvB = move_fit(T, M, [])
res = {}
for tag, pr in (("layer move model", mvL), ("base-gap-only move model", mvB)):
    o = timing(H, H.predA.values, pr(H), tstar); lo, hi = boot(o["gain"]) if o["nw"] else (np.nan, np.nan)
    tot = o["gain"].sum(); tlo, thi = (lo * o["nw"], hi * o["nw"])
    per = o["dd"].groupby("season").apply(lambda x: pd.Series({"bets": len(x), "waited": int(x.wait.sum()), "gain": x.gain[x.wait].sum(),
          "u_open": x.res_open.sum(), "u_timing": x.res_timing.sum(), "u_close": x.res_close.sum()})).round(1)
    print(f" [{tag}] base bets {o['n']}, waited {o['nw']} ({o['nw']/o['n']:.1%}); points gained total {tot:+.1f} [90% {tlo:+.1f}, {thi:+.1f}], "
          f"mean per waited bet {o['gain'].mean() if o['nw'] else float('nan'):+.3f} | units: always opener {o['uo']:+.1f}, timing {o['ut']:+.1f}, always close {o['uc']:+.1f}")
    print(per.to_string())
    res[tag] = dict(tot=tot, tlo=tlo, o=o)
L, B0 = res["layer move model"], res["base-gap-only move model"]
t1 = L["tot"] > 0 and L["tlo"] > 0; t2 = L["o"]["ut"] >= L["o"]["uo"]; t3 = L["tot"] > B0["tot"]
print(f"\nT1 points gained > 0, 90% low > 0: {t1} ({L['tot']:+.1f}, low {L['tlo']:+.1f})")
print(f"T2 units timing >= always opener: {t2} ({L['o']['ut']:+.1f} vs {L['o']['uo']:+.1f})")
print(f"T3 layer gains more than base-gap-only: {t3} ({L['tot']:+.1f} vs {B0['tot']:+.1f})")
print("TIMING VERDICT:", "PASS (weaker evidence: seen seasons)" if (t1 and t2 and t3) else "FAIL")
o2 = timing(S2, S2.predA.values, mvL(S2), tstar)
print(f"\n timing secondary, ESPN BET 2025 (decides nothing): base bets {o2['n']}, waited {o2['nw']}, gained {o2['gain'].sum():+.1f}, units opener {o2['uo']:+.1f} timing {o2['ut']:+.1f}")
L["o"]["dd"][["espn_id", "season", "date", "home_name", "away_name", "op", "close_sp", "margin", "predA", "side", "m", "wait", "gain", "res_open", "res_timing", "res_close"]].to_csv(
    os.path.join(W, "ncaab", "research", "lineup_travel_timing_bets.csv"), index=False)
