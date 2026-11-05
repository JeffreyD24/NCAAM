"""Pre-game lineup / inferred-injury / travel / rest features per game (Nov 5, 2026).
Definitions are fixed in ncaab/research/LINEUP_INJURY_TRAVEL_PREREG_2026-11-05.md (pushed before this was built).
  python ncaab/lineup_travel_features.py WORKDIR
  -> derived/lineup_travel_features.csv.gz  (one row per game: h_* and a_* features for home and away team, plus oracle_* diagnostics)
Every pre-game feature uses only games with a strictly earlier date. oracle_* use the game's own box score (NOT tradable; diagnostic only).
Interpretation notes (prereg ambiguity, fixed here): a player's 'average minutes' = total minutes in the team's last <=10 box-score games divided by the
number of those games (games missed count as 0); regular = top 8 by that, average >= 15, and minutes > 0 in >= 6 of the window games."""
import os, sys, math
from collections import Counter
import numpy as np, pandas as pd, zipcodes

W = os.path.abspath(sys.argv[1]); D = os.path.join(W, "ncaab", "data"); OUT = os.path.join(W, "derived"); os.makedirs(OUT, exist_ok=True)

G = pd.read_csv(os.path.join(D, "all_games.csv"), low_memory=False,
                usecols=["season", "date", "espn_id", "hk", "ak", "neutral"])
G["date"] = pd.to_datetime(G["date"]); G["espn_id"] = G["espn_id"].astype("int64")
G["neutral"] = G["neutral"].astype(str).str.lower().isin(["true", "1", "1.0"])

# ---------- venues -> coordinates
zd = {}
for z in zipcodes.list_all():
    if z.get("lat") and z.get("long") and z["zip_code_type"] != "MILITARY":
        zd.setdefault((z["city"].lower(), z["state"]), []).append((float(z["lat"]), float(z["long"])))
MANUAL = {  # places the zip table misses; approximate city-center coordinates
    ("moon township", "PA"): (40.52, -80.21), ("homewood", "AL"): (33.48, -86.80), ("riverdale", "NY"): (40.90, -73.91),
    ("lawrenceville", "NJ"): (40.30, -74.73), ("nassau", "Bahamas"): (25.04, -77.35), ("ashwaubenon", "WI"): (44.49, -88.07),
    ("highland heights", "KY"): (39.03, -84.45), ("queens", "NY"): (40.73, -73.79), ("maui", "HI"): (20.80, -156.33),
    ("rosemont", "IL"): (41.99, -87.87), ("storrs", "CT"): (41.81, -72.25), ("saint thomas", "Virgin Islands"): (18.34, -64.93),
    ("cancun", "Mexico"): (21.16, -86.85), ("san juan", "Puerto Rico"): (18.47, -66.11), ("george town", "Cayman Islands"): (19.29, -81.37),
    ("lake buena vista", "FL"): (28.37, -81.52), ("sunrise", "FL"): (26.16, -80.26), ("hot springs", "AR"): (34.50, -93.05),
    ("college park", "GA"): (33.65, -84.45), ("laval", "PQ"): (45.57, -73.69), ("freeport", "Bahamas"): (26.53, -78.70),
    ("bimini", "Bahamas"): (25.73, -79.30), ("bayamon", "Puerto Rico"): (18.40, -66.16), ("montego bay", "Jamaica"): (18.47, -77.92),
}
def place(c, s):
    if not isinstance(c, str) or not isinstance(s, str): return (np.nan, np.nan)
    k = (c.lower().strip(), s.strip())
    for kk in (k, (k[0].replace("saint ", "st. "), k[1]), (k[0].replace("st. ", "saint "), k[1])):
        if kk in MANUAL: return MANUAL[kk]
        if kk in zd: return tuple(np.mean(zd[kk], axis=0))
    return (np.nan, np.nan)

box = os.path.join(D, "box")
seasons = sorted(G.season.unique())
TM = pd.concat([pd.read_csv(os.path.join(box, f"teams_{s}.csv.gz"), usecols=["espn_id", "city", "state"]) for s in seasons]).drop_duplicates("espn_id")
TM["espn_id"] = TM["espn_id"].astype("int64")
pc = {k: place(*k) for k in set(zip(TM.city, TM.state))}
TM["vlat"] = [pc[k][0] for k in zip(TM.city, TM.state)]; TM["vlon"] = [pc[k][1] for k in zip(TM.city, TM.state)]
G = G.merge(TM[["espn_id", "vlat", "vlon"]], on="espn_id", how="left")
print("games", len(G), "venue coords known", round(G.vlat.notna().mean(), 4), flush=True)
unm = TM[TM.vlat.isna() & TM.city.notna()].groupby(["city", "state"]).size().sort_values(ascending=False)
print("non-blank unmatched places:", len(unm), "games", int(unm.sum())); print(unm.head(10).to_string(), flush=True)

# ---------- long team-game table, home bases
L = pd.concat([
    G.assign(team=G.hk, opp=G.ak, is_home=True), G.assign(team=G.ak, opp=G.hk, is_home=False)
], ignore_index=True).sort_values(["team", "season", "date", "espn_id"]).reset_index(drop=True)
def modal(df):
    pts = [(round(a, 2), round(b, 2)) for a, b in zip(df.vlat, df.vlon) if not (np.isnan(a) or np.isnan(b))]
    return Counter(pts).most_common(1)[0][0] if pts else (np.nan, np.nan)
H = L[L.is_home & ~L.neutral]
base_ts = {k: modal(g) for k, g in H.groupby(["team", "season"])}
base_t = {k: modal(g) for k, g in H.groupby("team")}
def base(team, season):
    b = base_ts.get((team, season), (np.nan, np.nan))
    return b if not np.isnan(b[0]) else base_t.get(team, (np.nan, np.nan))
# venue of a game for a team: its coordinates, or (blank city, not neutral) the home team's base
def venue(row_lat, row_lon, is_home, neutral, team, opp, season):
    if not np.isnan(row_lat): return (row_lat, row_lon)
    if neutral: return (np.nan, np.nan)
    return base(team if is_home else opp, season)

def hav(a, b):
    if np.isnan(a[0]) or np.isnan(b[0]): return np.nan
    p1, p2 = math.radians(a[0]), math.radians(b[0]); dl = math.radians(b[1] - a[1]); dp = p2 - p1
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))
tz = lambda v: np.nan if np.isnan(v[0]) else round(-v[1] / 15)

# ---------- player box records: (espn_id, team_id) -> {min, pts, starters}
PB = {}
for s in seasons:
    p = pd.read_csv(os.path.join(box, f"players_{s}.csv.gz"), usecols=["espn_id", "team_id", "athlete_id", "starter", "min", "pts"])
    p["min"] = p["min"].fillna(0.0); p["pts"] = p["pts"].fillna(0.0)
    for (e, t), g in p.groupby(["espn_id", "team_id"]):
        PB[(int(e), int(t))] = (dict(zip(g.athlete_id, g["min"])), dict(zip(g.athlete_id, g.pts)), set(g.athlete_id[g.starter == 1]))
print("player-box team-games", len(PB), flush=True)

def lineup(prior, this=None):
    win = prior[-10:]; n = len(win)
    tm, tp, pl = Counter(), Counter(), Counter()
    for m, p, _ in win:
        for a, v in m.items():
            tm[a] += v; tp[a] += p.get(a, 0.0); pl[a] += v > 0
    avg = {a: tm[a] / n for a in tm}
    reg = [a for a in sorted(avg, key=lambda a: -avg[a])[:8] if avg[a] >= 15 and pl[a] >= 6]
    den = sum(avg[a] for a in reg); pden = sum(tp[a] / n for a in reg)
    def share(lastm):
        lost = [a for a in reg if lastm.get(a, 0.0) <= 0]
        return (sum(avg[a] for a in lost) / den if den > 0 else 0.0, sum(tp[a] / n for a in lost) / pden if pden > 0 else 0.0)
    A, B = share(win[-1][0])
    cnt = Counter(a for _, _, st in prior[-11:-1] for a in st); top5 = {a for a, _ in cnt.most_common(5)}
    C = len(win[-1][2] - top5)
    oA = oB = np.nan
    if this is not None: oA, oB = share(this[0])
    return A, B, C, oA, oB

rows = []
for (team, season), g in L.groupby(["team", "season"], sort=False):
    bs = base(team, season); prior = []; sched = []  # sched: (date, venue)
    for r in g.itertuples(index=False):
        v = venue(r.vlat, r.vlon, r.is_home, r.neutral, team, r.opp, season)
        rec = dict(espn_id=r.espn_id, team=team, is_home=r.is_home, n_box=len(prior))
        if sched:
            pd_, pv = sched[-1]; rest = min((r.date - pd_).days, 7); pv = pv if not np.isnan(pv[0]) else bs
        else:
            rest, pv = 7, bs
        rec["rest_days"] = rest; rec["back_to_back"] = int(rest <= 1)
        rec["games_last_7"] = sum((r.date - d).days <= 7 for d, _ in sched)
        mi = hav(pv, v)
        rec["travel_miles"] = np.log1p(mi) if not np.isnan(mi) else np.nan
        rec["tz_shift"] = abs(tz(pv) - tz(v)) if not (np.isnan(pv[0]) or np.isnan(v[0])) else np.nan
        key = (int(r.espn_id), int(team)); this = PB.get(key)
        if len(prior) >= 5:
            A, B, C, oA, oB = lineup(prior, this)
            rec.update(lost_min_share=A, lost_pts_share=B, new_starters=C, oracle_lost_min=oA, oracle_lost_pts=oB)
        sched.append((r.date, v))
        if this is not None: prior.append(this)
        rows.append(rec)
F = pd.DataFrame(rows)
cols = [c for c in F.columns if c not in ("espn_id", "team", "is_home")]
Hf = F[F.is_home].drop(columns=["team", "is_home"]).rename(columns={c: "h_" + c for c in cols})
Af = F[~F.is_home].drop(columns=["team", "is_home"]).rename(columns={c: "a_" + c for c in cols})
OUTF = G[["espn_id", "season", "date"]].merge(Hf, on="espn_id", how="left").merge(Af, on="espn_id", how="left")
OUTF.to_csv(os.path.join(OUT, "lineup_travel_features.csv.gz"), index=False, compression="gzip")
print("saved", OUTF.shape)
print(OUTF.describe().T[["count", "mean", "std", "min", "max"]].round(3).to_string())
