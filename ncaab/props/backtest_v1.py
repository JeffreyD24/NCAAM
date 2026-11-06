"""NCAAM player props v1 / v1s at the OPENING line on past seasons — as pre-registered in ncaab/research/props/PROPS_V1_PREREG_2026-11-05.md.
  python ncaab/props/backtest_v1.py WORKDIR  -> ncaab/props/backtest_v1_output.txt, ncaab/props/backtest_v1_bets.csv.gz
Needs ncaab/data/props_history/bettingpros/*.csv.gz and derived/ncaam_props_features.csv.gz (or _tmp/ncaam_props_features.csv.gz)."""
import os, sys, re, glob, unicodedata
import numpy as np, pandas as pd
from scipy import stats, optimize
W = os.path.abspath(sys.argv[1]); HERE = os.path.join(W, "ncaab", "props")
out = []
def say(*a): out.append(" ".join(str(x) for x in a)); print(*a, flush=True)
rng = np.random.default_rng(1105)
FIT, TEST = [2022, 2023], [2024, 2025, 2026]
SPORTSBOOKS = ["draftkings", "fanduel", "betmgm", "caesars", "thescore", "hardrock", "fanatics", "betrivers", "bet365", "partycasino", "sugarhouse"]
ST = ["pts", "reb", "ast", "fg3m"]


def norm(n):
    n = unicodedata.normalize("NFKD", str(n)).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"[.'`]", "", n).replace("-", " "); n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


def dec(a): a = np.asarray(a, float); return np.where(a > 0, 1 + a / 100, 1 + 100 / np.abs(a))


# ---------------------------------------------------------------- data
fs = [f for f in sorted(glob.glob(os.path.join(W, "ncaab", "data", "props_history", "bettingpros", "*.csv.gz"))) if os.path.getsize(f) > 200]
D = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
D = D[D.line.notna() & D.price.notna()].copy()
D["name_n"] = D.player.map(norm); d = pd.to_datetime(D.date); D["season"] = d.dt.year + (d.dt.month >= 8)
D["tip"] = pd.to_datetime(D.scheduled); D["upd"] = pd.to_datetime(D.updated); D["hours_before"] = (D.tip - D.upd).dt.total_seconds() / 3600
say(f"BettingPros NCAAM lines: {len(D)} rows, {D.date.nunique()} dates, seasons {D.season.value_counts().sort_index().to_dict()}")
ff = os.path.join(W, "_tmp", "ncaam_props_features.csv.gz")
F = pd.read_csv(ff if os.path.exists(ff) else os.path.join(W, "derived", "ncaam_props_features.csv.gz"), dtype={"athlete_id": str})
F = F.sort_values(["athlete_id", "date"]); F["prev_date"] = F.groupby("athlete_id").date.shift()
dup = F.groupby(["date", "name_n"]).athlete_id.transform("nunique") > 1
say(f"features: {len(F)} player-games; ambiguous same-day names dropped: {dup.sum()}"); F = F[~dup]

# ---------------------------------------------------------------- variance (a, b) and blowout minutes (beta), box only, FIT seasons
Fb = F[F.season.isin([2022, 2023]) & (F.n_prev >= 3)]   # 2020-21 has no features (it is only the prior); noted in the output
var_ab = {}
for s in ST:
    mu = Fb[f"mu_{s}"].clip(lower=0.05).values; e2 = (Fb[s].values - mu) ** 2
    var_ab[s] = [float(v) for v in np.linalg.lstsq(np.column_stack([mu, mu ** 2]), e2, rcond=None)[0]]
say("var_ab (2021-22 + 2022-23 box; 2020-21 has no features since it is the prior season): " + ", ".join(f"{k} a {v[0]:.2f} b {v[1]:.4f}" for k, v in var_ab.items()))
Fs = Fb[Fb.open_sp_team.notna() & (Fb.min_proj > 0)]
x = (Fs.open_sp_team.abs() - 8).clip(lower=0) / 10; sv = Fs.min_proj / 30; y = Fs["min"] / Fs.min_proj - 1; wt = Fs.min_proj
Xm = np.column_stack([x, x * sv]); sw = np.sqrt(wt.values)
beta = np.linalg.lstsq(Xm * sw[:, None], y.values * sw, rcond=None)[0]
say(f"blowout minutes (v1s): beta0 {beta[0]:+.4f}, beta1 {beta[1]:+.4f}  (e.g. starter 30 min, 25-pt spread: x {1.7:.1f} -> x {1+beta[0]*1.7+beta[1]*1.7:.3f})")
F["min_fac_s"] = (1 + beta[0] * ((F.open_sp_team.abs() - 8).clip(lower=0) / 10).fillna(0) + beta[1] * ((F.open_sp_team.abs() - 8).clip(lower=0) / 10).fillna(0) * F.min_proj / 30).clip(0.5, 1.2)

# ---------------------------------------------------------------- identify market 270 (no outcomes used)
key = ["date", "name_n", "market_id"]
O = D.drop_duplicates(key + ["side"])[key + ["season", "side", "open_line", "open_price", "open_book", "open_time", "scheduled", "event_id"]]
O = O.pivot_table(index=key + ["season", "open_book", "open_time", "scheduled", "event_id"], columns="side", values=["open_line", "open_price"], aggfunc="first")
O.columns = [f"{a}_{b}" for a, b in O.columns]; O = O.reset_index()
O = O[(O.open_line_over == O.open_line_under) & O.open_price_over.notna() & O.open_price_under.notna()]
for c in ("open_price_over", "open_price_under"): O = O[(O[c].abs() >= 100) & (O[c].abs() <= 1000)]
O = O.rename(columns={"open_line_over": "line"})
M0 = O[O.market_id == 270].merge(F[["date", "name_n"] + [f"mu_{s}" for s in ST]], on=["date", "name_n"])
gap = {s: float((M0.line - M0[f"mu_{s}"]).abs().mean()) for s in ["reb", "ast", "fg3m"]}
s270 = min(gap, key=gap.get)
say(f"market 270 identification (mean |line - model mean|): {', '.join(f'{k} {v:.2f}' for k, v in gap.items())} -> 270 = {s270}")
O["stat"] = O.market_id.map({269: "pts", 270: s270})

O["open_t"] = pd.to_datetime(O.open_time); O["tip"] = pd.to_datetime(O.scheduled); O["lead_h"] = (O.tip - O.open_t).dt.total_seconds() / 3600
O["open_date_et"] = O.open_t.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
qo, qu = 1 / dec(O.open_price_over), 1 / dec(O.open_price_under); O["p_open"] = qo / (qo + qu)
say(f"openers: {len(O)}; by book {O.open_book.value_counts().head(12).to_dict()}")
# close at the opener's book
C = D[D.hours_before.between(-0.25, 6)].copy(); C["stat"] = C.market_id.map({269: "pts", 270: s270})
C = C.pivot_table(index=["date", "name_n", "stat", "book"], columns="side", values=["line", "price"], aggfunc="first")
C.columns = [f"{a}_{b}" for a, b in C.columns]; C = C.reset_index()
C = C[C.line_over == C.line_under].rename(columns={"line_over": "c_line", "book": "open_book"})
for c in ("price_over", "price_under"): C = C[(C[c].abs() >= 100) & (C[c].abs() <= 1000)]
qo, qu = 1 / dec(C.price_over), 1 / dec(C.price_under); C["c_fair"] = qo / (qo + qu)

FL = pd.concat([F[["date", "name_n", "season", "n_prev", "min_proj", "min_fac_s", "prev_date", "open_sp_team", s, f"mu_{s}"]]
                .rename(columns={s: "actual", f"mu_{s}": "mu"}).assign(stat=s) for s in ST], ignore_index=True)
X = O.drop(columns="season").merge(FL, on=["date", "name_n", "stat"], how="inner")
say(f"openers matched to a played game: {len(X)} of {len(O)}")
X = X[(X.n_prev >= 3) & (X.lead_h >= 1) & (X.prev_date.isna() | (X.prev_date < X.open_date_et)) & (X.line >= 0.5)].copy()
say(f"after timing guard (prev game on an earlier ET day; opener 1h+ before tip; 3+ games; line >= 0.5): {len(X)}")
X = X[X.open_book.isin(SPORTSBOOKS)].copy()
say(f"sportsbook openers (DFS apps / consensus / unknown excluded): {len(X)}; by season {X.season.value_counts().sort_index().to_dict()}; by book {X.open_book.value_counts().to_dict()}")


def pmodel(mu, stat):
    p = np.full(len(mu), np.nan); sd = np.full(len(mu), np.nan)
    for s in ST:
        m = (stat == s).values
        if not m.any(): continue
        a, b = var_ab[s]; u = mu[m].clip(lower=0.05); ex = (a - 1) * u + b * u ** 2
        r = np.where(ex > 1e-6, u ** 2 / np.clip(ex, 1e-6, None), 1e6)
        p[m] = 1 - stats.nbinom.cdf(np.floor(X.line.values[m]), r, r / (r + u)); sd[m] = np.sqrt(u + u ** 2 / r)
    return p, sd


X["p_v1"], X["sd"] = pmodel(X.mu.values, X.stat)
X["p_v1s"], _ = pmodel((X.mu * X.min_fac_s).values, X.stat)
X["y"] = np.where(X.actual > X.line, 1.0, np.where(X.actual < X.line, 0.0, np.nan))
X = X.merge(C[["date", "name_n", "stat", "open_book", "c_line", "c_fair"]], on=["date", "name_n", "stat", "open_book"], how="left")
mc = X.c_line + X.sd * stats.norm.ppf(X.c_fair.clip(0.01, 0.99))
X["c_over_here"] = np.where(X.c_line == X.line, X.c_fair, 1 - stats.norm.cdf((X.line - mc) / X.sd))
Cl = X[X.c_fair.notna() & (X.actual != X.c_line)]
lean = (Cl.groupby("season").c_fair.mean() - (Cl.actual > Cl.c_line).groupby(Cl.season).mean()).to_dict()
loso = {s: np.mean([v for k, v in lean.items() if k != s]) for s in lean}
say("close over-lean by season (no-vig over minus actual, matched rows): " + ", ".join(f"{k} {v*100:+.2f}" for k, v in sorted(lean.items())))


def ll(p, y): p = np.clip(p, 1e-6, 1 - 1e-6); return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))


def bets(X, pcol, w, ev_min=0.05):
    p = w * X[pcol] + (1 - w) * X.p_open; rows = []
    for side in ("over", "under"):
        ps = p if side == "over" else 1 - p
        rows.append(X.assign(side=side, price=X[f"open_price_{side}"], p_side=ps, ev=ps * dec(X[f"open_price_{side}"]) - 1))
    B = pd.concat(rows).sort_values("ev", ascending=False).drop_duplicates(["date", "name_n", "stat"])
    B = B[B.ev >= ev_min].copy()
    won = np.where(B.side == "over", B.actual > B.line, B.actual < B.line)
    B["u"] = np.where(B.actual == B.line, 0.0, np.where(won, dec(B.price) - 1, -1.0))
    cs = np.where(B.side == "over", B.c_over_here, 1 - B.c_over_here)
    adj = B.season.map(loso).fillna(np.mean(list(lean.values())) if lean else 0.0)
    B["clev"] = cs * dec(B.price) - 1
    B["clev_adj"] = (cs + np.where(B.side == "under", adj, -adj)) * dec(B.price) - 1
    B["move"] = np.where(B.side == "under", B.line - B.c_line, B.c_line - B.line)
    return B


def boot(df, col, n=3000):
    g = df.groupby("date")[col].agg(["sum", "count"]).values
    if len(g) < 5: return np.nan, np.nan
    idx = rng.integers(0, len(g), (n, len(g))); m = g[idx, 0].sum(1) / g[idx, 1].sum(1)
    return np.percentile(m, 5), np.percentile(m, 95)


def line_(B):
    if not len(B): return "0 bets"
    lo, hi = boot(B, "u"); c = B[B.clev.notna()]
    return (f"{len(B):5d} bets | win {(B.u > 0).sum() / max((B.u != 0).sum(), 1)*100:5.1f}% | {B.u.sum():+7.1f}u ROI {B.u.mean()*100:+.1f}% [{lo*100:+.1f}, {hi*100:+.1f}] | "
            f"close-EV raw {c.clev.mean()*100:+.2f}% lean-adj {c.clev_adj.mean()*100:+.2f}% (n {len(c)}) | line move our way {c.move.mean():+.2f}")


def info_test(T, pcol):
    """logit(y) ~ 1 + logit(p_open) + (logit(p_model) - logit(p_open)); date-clustered sandwich SE"""
    T = T[T.y.notna()]; lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))
    Z = np.column_stack([np.ones(len(T)), lg(T.p_open.values), lg(T[pcol].values) - lg(T.p_open.values)]); yv = T.y.values
    bta = np.zeros(3)
    for _ in range(50):
        pr = 1 / (1 + np.exp(-Z @ bta)); H = (Z * (pr * (1 - pr))[:, None]).T @ Z; g = Z.T @ (yv - pr)
        step = np.linalg.solve(H, g); bta += step
        if np.abs(step).max() < 1e-9: break
    pr = 1 / (1 + np.exp(-Z @ bta)); Hi = np.linalg.inv((Z * (pr * (1 - pr))[:, None]).T @ Z)
    sc = pd.DataFrame(Z * (yv - pr)[:, None]).groupby(T.date.values).sum().values
    V = Hi @ (sc.T @ sc) @ Hi; se = np.sqrt(np.diag(V))
    return bta[2], se[2], len(T)


res = {}
for name, pcol in (("v1", "p_v1"), ("v1s", "p_v1s")):
    say(f"\n================ {name} ================")
    Fi = X[X.season.isin(FIT) & X.y.notna()]
    f = lambda w: ll(w * Fi[pcol] + (1 - w) * Fi.p_open, Fi.y)
    w = float(optimize.minimize_scalar(f, bounds=(0, 1), method="bounded").x)
    say(f"FIT 2021-22 + 2022-23: w = {w:.3f} (log loss opener {f(0):.4f}, model {f(1):.4f}, blend {f(w):.4f}, n {len(Fi)})")
    Te = X[X.season.isin(TEST) & X.y.notna()]; tc = Te[Te.c_fair.notna()]
    say(f"TEST log loss: opener {ll(Te.p_open, Te.y):.4f}, model {ll(Te[pcol], Te.y):.4f}, blend {ll(w*Te[pcol]+(1-w)*Te.p_open, Te.y):.4f} (n {len(Te)}); "
        f"close {ll(tc.c_over_here, tc.y):.4f} vs blend {ll(w*tc[pcol]+(1-w)*tc.p_open, tc.y):.4f} on the {len(tc)} rows with a close")
    coef, se, n = info_test(X[X.season.isin(TEST)], pcol)
    say(f"information test (model beyond the opener, test seasons, date-clustered): coef {coef:+.3f} se {se:.3f} 90% CI [{coef-1.645*se:+.3f}, {coef+1.645*se:+.3f}] n {n}")
    for s_ in TEST:
        c_, s2, n2 = info_test(X[X.season == s_], pcol); say(f"   {s_}: coef {c_:+.3f} se {s2:.3f} n {n2}")
    Bm = bets(X, pcol, w); B0 = bets(X, pcol, 0.0)
    U = X.assign(side="under", price=X.open_price_under); U["u"] = np.where(U.actual == U.line, 0.0, np.where(U.actual < U.line, dec(U.price) - 1, -1.0))
    say("Rule (EV >= 5% at the opening price, sportsbook openers) by season:")
    for s_ in sorted(Bm.season.unique()):
        tag = " TEST" if s_ in TEST else (" fit" if s_ in FIT else " (descr.)"); say(f"  {s_}{tag}: {line_(Bm[Bm.season == s_])}")
    T = Bm[Bm.season.isin(TEST)]; T0 = B0[B0.season.isin(TEST)]; TU = U[U.season.isin(TEST)]
    lo, hi = boot(T, "u") if len(T) else (np.nan, np.nan)
    counted = [s_ for s_ in TEST if (Bm.season == s_).sum() >= 100]
    c1 = coef - 1.645 * se > 0
    c2 = len(counted) > 0 and all(Bm[Bm.season == s_].u.sum() > 0 for s_ in counted) and lo > 0
    c3 = len(T) > 0 and T[T.clev.notna()].clev_adj.mean() >= 0
    c4 = len(T) > 0 and T.u.sum() > T0.u.sum() and T.u.sum() > TU.u.sum()
    say(f"TEST pooled: {line_(T)}")
    say(f"simple (a) no model (w=0): {line_(T0)}")
    say(f"simple (b) every under at these openers: {len(TU)} bets, {TU.u.sum():+.1f}u ROI {TU.u.mean()*100:+.2f}%")
    say(f"seasons counted (100+ bets): {counted}")
    say(f"checks: 1 information {'PASS' if c1 else 'fail'} | 2 unseen seasons {'PASS' if c2 else 'fail'} | 3 lean-adj close-EV >= 0 {'PASS' if c3 else 'fail'} | "
        f"4 beats simple {'PASS' if c4 else 'fail'} -> {'ALL PASS' if all([c1, c2, c3, c4]) else 'does not qualify'}")
    res[name] = dict(all_pass=all([c1, c2, c3, c4]), clev=T[T.clev.notna()].clev_adj.mean() if len(T) else np.nan, units=T.u.sum() if len(T) else 0)
    say("Descriptive (test seasons):")
    dk = T[T.open_book.isin(["draftkings", "fanduel"])]; say(f"  DK/FD openers only: {line_(dk)}")
    for s_ in TEST: say(f"     {s_}: {line_(dk[dk.season == s_])}")
    for thr in (0.03, 0.08, 0.12):
        b = bets(X, pcol, w, thr); say(f"  EV >= {int(thr*100)}%: {line_(b[b.season.isin(TEST)])}")
    for col in ("stat", "side", "open_book"):
        for k, g in T.groupby(col): say(f"  {col}={k}: {line_(g)}")
    T = T.assign(month=pd.to_datetime(T.date).dt.month, spb=pd.cut(T.open_sp_team.abs(), [-0.1, 5, 10, 20, 60]), lead=pd.cut(T.lead_h, [1, 4, 12, 24, 72]))
    for k, g in T.groupby("month"): say(f"  month {k}: {line_(g)}")
    for k, g in T.groupby("spb", observed=True): say(f"  |spread| {k}: {line_(g)}")
    for k, g in T.groupby("lead", observed=True): say(f"  opener {k} h before tip: {line_(g)}")
    if len(T[T.clev_adj.notna()]) > 5:
        lo2, hi2 = boot(T[T.clev_adj.notna()], "clev_adj"); say(f"  lean-adjusted close-EV 90% CI: [{lo2*100:+.2f}, {hi2*100:+.2f}]")
    pd.concat([Bm.assign(rule=name), B0.assign(rule=f"{name}_no_model")]).to_csv(os.path.join(HERE, f"backtest_{name}_bets.csv.gz"), index=False)
say("\nSummary: " + "; ".join(f"{k}: {'ALL PASS' if v['all_pass'] else 'does not qualify'} (lean-adj close-EV {v['clev']*100:+.2f}%, {v['units']:+.1f}u)" for k, v in res.items()))
open(os.path.join(HERE, "backtest_v1_output.txt"), "w").write("\n".join(out) + "\n")
