"""Past NCAAM player-prop lines from BettingPros' public web API (same calls bettingpros.com makes; free, no account; personal research,
paced ~1 request per 1.5 s). Port of nba-mixed-model/props_bettingpros.py (Nov 5, 2026).
Probe (research/probes/bp_ncaab_probe.md): sport=NCAAB has two player-prop markets, 269 (points) and 270 (second stat, identified
against box scores in the backtest); coverage Dec 2021 (FanDuel only) to now, ~45 games/day with props from 2023-24, books vary by season.
Per row: each book's last line + price before the game (with its update time) = the close, and the opening line + price + book + time.
  python ncaab/props/bettingpros.py WORKDIR [--from 2021-11-01] [--to YYYY-MM-DD] [--max-dates 40] [--newest-first]
  -> ncaab/data/props_history/bettingpros/{date}.csv.gz (dates already saved are skipped; empty dates saved as a 0-row file)"""
import os, sys, json, time, random, urllib.request, urllib.parse, urllib.error
import datetime as dt
import pandas as pd

W = os.path.abspath(sys.argv[1])
ARG = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
OUT = os.path.join(W, "ncaab", "data", "props_history", "bettingpros"); os.makedirs(OUT, exist_ok=True)
KEY = "CHi8Hy5CEE4khd46XNYL23dCFX96oUdw6qOt1Dnh"      # BettingPros' public web-client key (what bettingpros.com itself sends)
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36", "Accept": "application/json",
       "x-api-key": KEY, "Origin": "https://www.bettingpros.com", "Referer": "https://www.bettingpros.com/"}
MARKETS = {269: "m269", 270: "m270"}
BOOKS = {0: "consensus", 12: "draftkings", 10: "fanduel", 19: "betmgm", 13: "caesars", 18: "betrivers", 24: "bet365", 14: "fanatics",
         33: "thescore", 49: "hardrock", 15: "sugarhouse", 27: "partycasino", 2: "pinnacle", 36: "underdog", 37: "prizepicks", 63: "sleeper"}
COLS = ["date", "event_id", "home", "away", "scheduled", "market_id", "bp_player_id", "player", "team", "side", "book", "line", "price",
        "updated", "open_line", "open_price", "open_book", "open_time"]


def get(path, params):
    url = f"https://api.bettingpros.com/v3/{path}?" + urllib.parse.urlencode(params)
    for i in range(5):
        time.sleep(1.2 + random.random() * 0.6)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=40) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504): time.sleep(20 * (i + 1)); continue
            raise
        except Exception:
            time.sleep(10 * (i + 1))
    raise RuntimeError(f"gave up on {path}")


def one_date(day):
    ev = get("events", dict(sport="NCAAB", date=day)).get("events", [])
    if not ev: return pd.DataFrame(columns=COLS), 0
    info = {e["id"]: e for e in ev}; rows = []
    for k in range(0, len(ev), 25):
        ids = ":".join(str(e["id"]) for e in ev[k:k + 25]); page = 1
        while True:
            d = get("offers", dict(sport="NCAAB", market_id=":".join(map(str, MARKETS)), event_id=ids, location="ALL", limit=50, page=page))
            for o in d.get("offers", []):
                e = info.get(o.get("event_id"), {}); p = (o.get("participants") or [{}])[0]
                for s in o.get("selections", []):
                    op = s.get("opening_line") or {}
                    for b in s.get("books", []):
                        for ln in b.get("lines", []):
                            if not ln.get("main", True): continue
                            rows.append(dict(date=day, event_id=o.get("event_id"), home=e.get("home"), away=e.get("visitor"),
                                             scheduled=e.get("scheduled"), market_id=o.get("market_id"), bp_player_id=o.get("player_id"),
                                             player=p.get("name"), team=(p.get("player") or {}).get("team"), side=s.get("selection"),
                                             book=BOOKS.get(b.get("id"), str(b.get("id"))), line=ln.get("line"), price=ln.get("cost"),
                                             updated=ln.get("updated"), open_line=op.get("line"), open_price=op.get("cost"),
                                             open_book=BOOKS.get(op.get("book_id"), str(op.get("book_id"))), open_time=op.get("created")))
            pg = d.get("_pagination") or {}
            if page >= (pg.get("total_pages") or 1): break
            page += 1
    return pd.DataFrame(rows, columns=COLS), len(ev)


def main():
    G = pd.read_csv(os.path.join(W, "ncaab", "data", "all_games.csv"), usecols=["season", "date"])
    dates = sorted(set(G[G.season >= 2022].date))
    y = dt.date.today() - dt.timedelta(days=1)
    lo, hi = ARG("--from", "2021-11-01"), ARG("--to", str(y))
    todo = [d for d in dates if lo <= d <= hi and not os.path.exists(os.path.join(OUT, f"{d}.csv.gz"))]
    if "--newest-first" in sys.argv: todo = todo[::-1]
    todo = todo[: int(ARG("--max-dates", "40"))]
    if not todo: print("all dates already saved"); return
    for d in todo:
        try:
            R, n = one_date(d)
        except Exception as e:
            print(f"{d}: failed ({e}); will retry next run", flush=True); continue
        R.to_csv(os.path.join(OUT, f"{d}.csv.gz"), index=False)
        print(f"{d}: {n} games, {len(R)} rows, {R.bp_player_id.nunique() if len(R) else 0} players, books {sorted(R.book.unique()) if len(R) else []}", flush=True)


if __name__ == "__main__":
    main()
