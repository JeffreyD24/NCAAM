"""Early-season roster features (returning production, incoming transfers) per game. Definitions fixed in
ncaab/research/ROSTER_CONTINUITY_PREREG_2026-11-05.md (pushed 8054b0a before this was built).
  python ncaab/roster_features.py WORKDIR -> derived/roster_features.csv.gz (one row per game: h_/a_ n, ret, inc, str, strin, R1-R4)
A team's known roster for game g = players with minutes for that team in its games on dates strictly before g's date this season."""
import os, sys
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1]); D = os.path.join(W, "ncaab", "data"); OUT = os.path.join(W, "derived")
G = pd.read_csv(os.path.join(D, "all_games.csv"), low_memory=False, usecols=["season", "date", "espn_id", "hk", "ak", "home_pts", "away_pts"])
G["date"] = pd.to_datetime(G.date); G["espn_id"] = G.espn_id.astype("int64")
G["hk"] = G.hk.astype(str); G["ak"] = G.ak.astype(str)
date_of = dict(zip(G.espn_id, G.date))
# team strength by season = mean actual margin per game
L = pd.concat([G.assign(t=G.hk, mg=G.home_pts - G.away_pts), G.assign(t=G.ak, mg=G.away_pts - G.home_pts)])
STR = L.groupby(["season", "t"]).mg.mean().to_dict()
seasons = sorted(G.season.unique()); PB = {}
for s in seasons:
    p = pd.read_csv(os.path.join(D, "box", f"players_{s}.csv.gz"), usecols=["espn_id", "team_id", "athlete_id", "min", "pts"])
    p["team_id"] = p.team_id.astype(str); p["min"] = p["min"].fillna(0); p["pts"] = p["pts"].fillna(0); p["date"] = p.espn_id.map(date_of); PB[s] = p
rows = []
for s in seasons:
    if s - 1 not in PB: continue
    q = PB[s - 1]; pa = q.groupby(["athlete_id", "team_id"]).agg(mn=("min", "sum"), pt=("pts", "sum")).reset_index()
    main = pa.sort_values("mn").drop_duplicates("athlete_id", keep="last").set_index("athlete_id").team_id.to_dict()
    apts = pa.groupby("athlete_id").pt.sum().to_dict(); tpts = q.groupby("team_id").pts.sum().to_dict()
    cur = PB[s][PB[s]["min"] > 0]; app = cur.groupby(["team_id", "date"]).athlete_id.apply(set).to_dict()
    Gs = G[G.season == s]
    for team, g in pd.concat([Gs.assign(t=Gs.hk), Gs.assign(t=Gs.ak)]).groupby("t"):
        dts = sorted(g.date.unique()); known = set(); n = 0; tp = tpts.get(team, 0.0); st = STR.get((s - 1, team), np.nan)
        for d in dts:
            ids = g[g.date == d].espn_id.values
            if tp > 0 and known:
                rp = sum(apts.get(a, 0) for a in known if main.get(a) == team)
                inc_ids = [a for a in known if a in main and main[a] != team]
                ip = sum(apts.get(a, 0) for a in inc_ids)
                sw = [(apts.get(a, 0), STR.get((s - 1, main[a]), np.nan)) for a in inc_ids]
                sw = [(w, v) for w, v in sw if w > 0 and np.isfinite(v)]
                strin = sum(w * v for w, v in sw) / sum(w for w, _ in sw) if sw else 0.0
                ret, inc = min(rp / tp, 1.0), min(ip / tp, 2.0)
            else:
                ret = inc = strin = np.nan
            for e in ids: rows.append(dict(espn_id=e, team=team, n=n, ret=ret, inc=inc, str=st, strin=strin))
            for e in ids: known |= app.get((team, d), set())
            n += len(ids)
    print("season", s, "done", flush=True)
F = pd.DataFrame(rows)
early = ((15 - F.n) / 15).where((F.n >= 1) & (F.n <= 14))
F["R1"] = early * (1 - F.ret); F["R2"] = early * F.inc; F["R3"] = early * (1 - F.ret) * F["str"]; F["R4"] = early * F.inc * F.strin
G2 = G[["espn_id", "season", "hk", "ak"]]
H = G2.merge(F.rename(columns={"team": "hk"}), on=["espn_id", "hk"], how="left")
A = G2.merge(F.rename(columns={"team": "ak"}), on=["espn_id", "ak"], how="left")
cols = ["n", "ret", "inc", "str", "strin", "R1", "R2", "R3", "R4"]
OUTF = G2[["espn_id", "season"]].copy()
for c in cols: OUTF["h_" + c] = H[c].values; OUTF["a_" + c] = A[c].values
OUTF.to_csv(os.path.join(OUT, "roster_features.csv.gz"), index=False, compression="gzip")
print("saved", OUTF.shape)
E2 = OUTF[OUTF[["h_R1", "a_R1"]].notna().all(axis=1)]
print("early rows with both teams' features:", len(E2)); print(E2[[c for c in OUTF.columns if c.startswith(("h_", "a_"))]].describe().T[["count", "mean", "std", "min", "max"]].round(3).to_string())
print("by season:", E2.groupby("season").size().to_dict())
