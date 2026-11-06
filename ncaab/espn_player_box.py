"""Full ESPN player box scores for NCAAM (Nov 5, 2026; props v1 groundwork). The older espn_boxscores.py kept only minutes and points;
player props need rebounds, assists and threes too. One row per player per game, including players listed but not playing (dnp=1,
for inferring absences later): espn_id, team_id, athlete_id, name, starter, dnp, min, pts, reb, oreb, ast, fg3m, fg3a, fgm, fga, ftm, fta, stl, blk, to, pf.
  python ncaab/espn_player_box.py WORKDIR --season 2026 [--threads 8]
  -> ncaab/data/box/players_full_{season}.csv.gz"""
import os, sys, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
W = os.path.abspath(sys.argv[1]); ARG = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SEASON = int(ARG("--season")); OUT = os.path.join(W, "ncaab", "data", "box"); os.makedirs(OUT, exist_ok=True)
U = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event={e}"
COLS = ["espn_id", "team_id", "athlete_id", "name", "starter", "dnp", "min", "pts", "reb", "oreb", "ast", "fg3m", "fg3a", "fgm", "fga",
        "ftm", "fta", "stl", "blk", "to", "pf"]
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(2 + 3 * i)
    return None
def num(x):
    try: return float(x) if x not in (None, "", "--") else None
    except ValueError: return None
def ma(x):
    try: a, b = str(x).split("-"); return float(a), float(b)
    except Exception: return None, None
def one(e):
    d = get(U.format(e=e)); P = []
    if not d: return P, False
    for t in (d.get("boxscore") or {}).get("players", []):
        tid = t["team"]["id"]; st = (t.get("statistics") or [{}])[0]; ix = {l: i for i, l in enumerate(st.get("labels") or [])}
        for a in st.get("athletes", []):
            s = a.get("stats") or []; g = lambda k: s[ix[k]] if k in ix and ix[k] < len(s) else None
            ath = a.get("athlete") or {}
            if not s:
                P.append([e, tid, ath.get("id"), ath.get("displayName"), int(bool(a.get("starter"))), 1] + [None] * 15); continue
            fgm, fga = ma(g("FG")); tpm, tpa = ma(g("3PT")); ftm, fta = ma(g("FT"))
            P.append([e, tid, ath.get("id"), ath.get("displayName"), int(bool(a.get("starter"))), int(bool(a.get("didNotPlay"))),
                      num(g("MIN")), num(g("PTS")), num(g("REB")), num(g("OREB")), num(g("AST")), tpm, tpa, fgm, fga, ftm, fta,
                      num(g("STL")), num(g("BLK")), num(g("TO")), num(g("PF"))])
    return P, True
if __name__ == "__main__":
    M = pd.read_csv(os.path.join(W, "ncaab", "data", "espn_meta.csv"), low_memory=False)
    d = pd.to_datetime(M.date); M["season"] = d.dt.year + (d.dt.month >= 8).astype(int)
    ids = sorted(set(M[M.season == SEASON].espn_id.astype(int)))
    if ARG("--limit"): ids = ids[: int(ARG("--limit"))]
    P, miss = [], 0
    with ThreadPoolExecutor(int(ARG("--threads", 8))) as ex:
        for i, (p, ok) in enumerate(ex.map(one, ids)):
            P += p; miss += (not ok)
            if i % 1000 == 0: print(SEASON, i, len(ids), flush=True)
    pd.DataFrame(P, columns=COLS).to_csv(os.path.join(OUT, f"players_full_{SEASON}.csv.gz"), index=False, compression="gzip")
    print(f"season {SEASON}: {len(ids)} games, {miss} failed fetches, {len(P)} player rows")
