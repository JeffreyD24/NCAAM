"""Probe (Nov 5, 2026): does BettingPros' public web API have past NCAAM player props, which markets, books and seasons?
Coverage only: no outcome or edge is looked at. Runs on GitHub Actions (the sandbox can't reach api.bettingpros.com).
  python tools/probe_bp_ncaab.py WORKDIR  -> research/probes/bp_ncaab_probe.md"""
import os, sys, json, time, random, urllib.request, urllib.parse, urllib.error, collections
W = os.path.abspath(sys.argv[1])
KEY = "CHi8Hy5CEE4khd46XNYL23dCFX96oUdw6qOt1Dnh"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36", "Accept": "application/json",
       "x-api-key": KEY, "Origin": "https://www.bettingpros.com", "Referer": "https://www.bettingpros.com/"}
OUT = []
def p(*a): s = " ".join(str(x) for x in a); print(s, flush=True); OUT.append(s)
def get(path, params):
    url = f"https://api.bettingpros.com/v3/{path}?" + urllib.parse.urlencode(params)
    for i in range(3):
        time.sleep(1.2 + random.random() * 0.6)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=40) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            p(f"  HTTP {e.code} on {path} {params}")
            if e.code in (429, 500, 502, 503): time.sleep(15); continue
            return {}
        except Exception as e:
            p(f"  error {e}"); time.sleep(5)
    return {}
SPORTS = ["NCAAB", "NCAAMB", "CBB"]
DATES = ["2021-12-11", "2022-02-12", "2022-03-17", "2023-01-14", "2023-02-11", "2023-03-16", "2024-01-13", "2024-02-10",
         "2024-03-21", "2025-01-11", "2025-02-08", "2025-03-20", "2026-01-10", "2026-02-07", "2026-03-19", "2026-11-04", "2026-11-05"]
p("# BettingPros NCAAM player-props probe (Nov 5, 2026)\n")
p("Coverage only (no outcomes or edges). Script: tools/probe_bp_ncaab.py\n")
sport = None
for s in SPORTS:
    ev = get("events", dict(sport=s, date="2026-02-07")).get("events", [])
    p(f"- sport={s}: {len(ev)} events on 2026-02-07")
    if ev and not sport: sport = s
if not sport: p("\nNo college sport key worked."); 
else:
    mk = get("markets", dict(sport=sport, limit=200))
    ms = mk.get("markets", []) if isinstance(mk, dict) else []
    p(f"\n## Markets listed for {sport}: {len(ms)}")
    for m in ms[:120]:
        p(f"- {m.get('id')}: {m.get('name') or m.get('title')} {m.get('category') or ''}")
    p("\n## v2 (Nov 5): player-prop markets 269/270 over ALL events of each date\n")
    sample = {}
    for d in DATES:
        ev = get("events", dict(sport=sport, date=d)).get("events", [])
        if not ev: p(f"- {d}: 0 events"); continue
        n = 0; mcnt = collections.Counter(); bcnt = collections.Counter(); opens = collections.Counter(); evp = set(); players = set()
        for k in range(0, len(ev), 10):
            ids = ":".join(str(e["id"]) for e in ev[k:k + 10]); page = 1
            while True:
                o = get("offers", dict(sport=sport, market_id="269:270", event_id=ids, location="ALL", limit=50, page=page))
                for of in o.get("offers", []):
                    n += 1; mcnt[of.get("market_id")] += 1; evp.add(of.get("event_id")); players.add(of.get("player_id"))
                    sample.setdefault(of.get("market_id"), of)
                    for sel in of.get("selections", []):
                        op = sel.get("opening_line") or {}
                        if op: opens[op.get("book_id")] += 1
                        for b in sel.get("books", []): bcnt[b.get("id")] += 1
                if page >= ((o.get("_pagination") or {}).get("total_pages") or 1): break
                page += 1
        p(f"- {d}: {len(ev)} events, {len(evp)} with props, {len(players)} players, {n} offers; markets {dict(mcnt)}; books {dict(bcnt.most_common(12))}; opening-line books {dict(opens.most_common(6))}")
    for m, of in sample.items(): p(f"\nsample offer market {m}: " + json.dumps(of)[:2500])
os.makedirs(os.path.join(W, "research", "probes"), exist_ok=True)
open(os.path.join(W, "research", "probes", "bp_ncaab_probe.md"), "w").write("\n".join(OUT) + "\n")
