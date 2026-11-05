"""AUDIT of the lineup/injury/travel grading (Nov 5, 2026) - exploratory, NOT part of the pre-registered grading.
Why: the registered spread test PASSED with t=+8.6 and a 54% close-hit rate, and the oracle (in-game absences) added nothing over the pre-game
lineup features. That pattern points at a data problem, not an edge. This script looks for it.   python ncaab/lineup_travel_audit.py WORKDIR"""
import os, sys
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1])
src = open(os.path.join(W, "ncaab", "lineup_travel_grade.py")).read().split('print("\\n==== PRIMARY')[0]
ns = {"__name__": "g"}; sys.argv = ["x", W]; exec(src, ns)
D, run, report, SETS, HEAD, fit_predict, EX = ns["D"], ns["run"], ns["report"], ns["SETS"], ns["HEAD"], ns["fit_predict"], ns["EX"]
D["neu"] = D.neutral.astype(str).str.lower().isin(["true", "1", "1.0"]); ns["D"] = D
H = D[D.season.isin(HEAD)].copy()

print("\n== A. basic shape of the excess (actual margin - close-implied margin) ==")
print("mean excess", round(H.ex_s.mean(), 3), "sd", round(H.ex_s.std(), 3), "| share |excess|>40:", round((H.ex_s.abs() > 40).mean(), 5), "| max", round(H.ex_s.abs().max(), 1))
print("neutral share", round(H.neutral.astype(str).str.lower().isin(["true", "1", "1.0"]).mean(), 3))
H["neu"] = H.neutral.astype(str).str.lower().isin(["true", "1", "1.0"])
print(H.groupby("neu").ex_s.agg(["count", "mean", "std"]).round(3).to_string())
print("line_src counts:", H.line_src.value_counts().to_dict())

print("\n== B. flipped-sign check: close sign vs our walk-forward margin sign, strong disagreements ==")
dis = H[(H.C_s.abs() >= 7) & (H.M2_m.abs() >= 7) & (np.sign(H.C_s) != np.sign(H.M2_m))]
print("games with |close|>=7 and |M2|>=7 but opposite signs:", len(dis), "of", len(H), "| mean excess there", round(dis.ex_s.mean(), 2), "| mean |excess|", round(dis.ex_s.abs().mean(), 2))
print(dis.groupby("neu").size().to_dict(), dis.groupby("season").size().to_dict())

print("\n== C. base-gap alone (blend - close) vs excess ==")
for nm, sub in (("all", H), ("non-neutral", H[~H.neu]), ("neutral", H[H.neu])):
    w = np.linalg.lstsq(np.c_[np.ones(len(sub)), sub[["M2_m", "M8_m", "MKT_m"]].values], sub.margin.values, rcond=None)[0]
    gap = np.c_[np.ones(len(sub)), sub[["M2_m", "M8_m", "MKT_m"]].values] @ w - sub.C_s.values
    b = np.polyfit(gap, sub.ex_s.values, 1)[0]; print(f"{nm}: n={len(sub)} slope of excess on base gap {b:+.3f}, corr {np.corrcoef(gap, sub.ex_s.values)[0, 1]:+.3f}, sd of gap {gap.std():.2f}")

print("\n== D. which features carry the layer (ridge fitted on all headline seasons, spreads, standardized coefficients) ==")
cols = [f"s_{f}" for f in SETS["ALL"]]; Hm = H[H[cols].notna().all(axis=1)]
Z = (Hm[cols] - Hm[cols].mean()) / Hm[cols].std()
c = np.linalg.solve(Z.values.T @ Z.values + 10 * np.eye(len(cols)), Z.values.T @ (Hm.ex_s.values - Hm.ex_s.mean()))
print(pd.Series(c, index=cols).round(3).to_string())
for cname in cols:
    x = Hm[cname]; print(f"  corr(excess, {cname}) = {np.corrcoef(x, Hm.ex_s)[0, 1]:+.4f}")
print("neutral-site split of the layer slope (LOSO ALL spreads):")
R = run("s", "ALL")
for nm, sub in (("non-neutral", R[~R.neu]), ("neutral", R[R.neu])): report(sub, "s", nm)

print("\n== E. placebo: shuffle each season's feature rows across games (breaks any real link, keeps distributions) ==")
rng = np.random.default_rng(7); fc = [c for c in D.columns if c.startswith("s_") or c.startswith("t_")]
for rep in range(3):
    Dp = D.copy()
    for s, idx in Dp.groupby("season").groups.items():
        perm = rng.permutation(len(idx)); Dp.loc[idx, fc] = Dp.loc[idx, fc].values[perm]
    ns["D"] = Dp; Rp = ns["run"]("s", "ALL"); report(Rp, "s", f"PLACEBO {rep}")
ns["D"] = D
print("\n== G. by close source (LOSO ALL spreads): layer slope, base-gap slope, hit rate of the base gap alone at |gap|>=3 ==")
R = run("s", "ALL")
for src_, sub in R.groupby("line_src"):
    yv = sub.ex_s.values; gp = sub.pB.values - sub.ly.values
    print(src_, "n", len(sub), "seasons", sorted(sub.season.unique())[:3], "..", "layer slope", round(np.polyfit(sub.ly.values, yv, 1)[0], 3), "| full slope", round(np.polyfit(sub.pB.values, yv, 1)[0], 3), "| corr(gap part, excess)", round(np.corrcoef(gp, yv)[0, 1], 4))
bg = R[(R.pA - R.pA.mean()).abs() >= 0.9]; wn = np.sign(bg.pA - R.pA.mean()) == np.sign(bg.ex_s); pu = bg.ex_s == 0
print("gap-only (model A) bets |pred|>=0.9: n", len(bg), "hit", round((wn & ~pu).sum() / (~pu).sum(), 4))
for src_, sub in bg.groupby("line_src"):
    w_ = np.sign(sub.pA - R.pA.mean()) == np.sign(sub.ex_s); p_ = sub.ex_s == 0; print("   ", src_, "n", len(sub), "hit", round((w_ & ~p_).sum() / (~p_).sum(), 4))
print("\n== F. layer-only close bets by season (spreads, LOSO ALL, |layer part|>=0.3 pt) ==")
R = run("s", "ALL"); b = R[R.ly.abs() >= 0.3]; win = np.sign(b.ly) == np.sign(b.ex_s); ps = b.ex_s == 0
t = pd.DataFrame({"n": b.groupby("season").size(), "hit": (win & ~ps).groupby(b.season).sum() / (~ps).groupby(b.season).sum()}).round(3); print(t.T.to_string())
