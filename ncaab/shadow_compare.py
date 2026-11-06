"""NCAAM live move: daily shadow-vs-live comparison (Nov 6, 2026). Rule: ncaab/research/LIVE_MOVE_SHADOW_PASS_RULE_2026-11-06.md.
Live = nba-mixed-model/ncaab/state (read from GitHub), shadow = this repo's ncaab/state.
Grades every completed ET game day after the copy cutoff that is not yet in the log, appends to ncaab/state/shadow_compare.md and
ncaab/state/shadow_compare_log.csv, and prints the running streak.
  python ncaab/shadow_compare.py WORKDIR [--live-dir PATH] [--today YYYY-MM-DD]
  (--live-dir: a local nba-mixed-model checkout instead of GitHub; --today: grade as if run that day, for testing)"""
import os, sys, io, json, urllib.request
import pandas as pd
W = os.path.abspath(sys.argv[1]); ST = os.path.join(W, "ncaab", "state")
LIVE_DIR = sys.argv[sys.argv.index("--live-dir") + 1] if "--live-dir" in sys.argv else None
RAW = "https://raw.githubusercontent.com/JeffreyD24/nba-mixed-model/main/ncaab/state/"
CUTOFF = "2026-11-06 01:00"          # last nba evaluation in the copied state (pass rule)
TOL_MIN, TOL_NUM = 10, 0.01
TODAY = pd.Timestamp(sys.argv[sys.argv.index("--today") + 1]) if "--today" in sys.argv else pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()   # --today: testing only

def live_text(name):
    if LIVE_DIR:
        p = os.path.join(LIVE_DIR, "ncaab", "state", name); return open(p).read() if os.path.exists(p) else None
    try:
        with urllib.request.urlopen(RAW + name, timeout=30) as r: return r.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 404: return None
        raise
def csv(text):
    return pd.read_csv(io.StringIO(text)) if text else pd.DataFrame()
def shadow(name):
    p = os.path.join(ST, name); return open(p).read() if os.path.exists(p) else None
def after_cut(df):
    if not len(df): return df
    df = df[df.at_et > CUTOFF].copy(); df["day"] = df.at_et.str[:10]; df["t"] = pd.to_datetime(df.at_et); return df

LE, SE = after_cut(csv(live_text("live_evals.csv"))), after_cut(csv(shadow("live_evals.csv")))
LB, SB = after_cut(csv(live_text("live_bets.csv"))), after_cut(csv(shadow("live_bets.csv")))
LR, SR = json.loads(live_text("live_ratings.json") or "null"), json.loads(shadow("live_ratings.json") or "null")

def match_bets(A, B):
    """rows of A with no row in B: same an_id, side, line, at_et within TOL_MIN"""
    miss = []
    for _, a in A.iterrows():
        c = B[(B.an_id == a.an_id) & (B.side == a.side) & (B.line.astype(float) == float(a.line))] if len(B) else B
        if not len(c) or (abs(c.t - a.t) > pd.Timedelta(minutes=TOL_MIN)).all(): miss.append(f"{a.an_id} {a.team} {float(a.line):+g} at {a.at_et}")
    return miss

def ratings_check():
    if LR is None or SR is None: return False, "a ratings file is missing"
    if LR.get("played_through") != SR.get("played_through"):
        return False, f"not comparable: played_through live {LR.get('played_through')} vs shadow {SR.get('played_through')}"
    worst, where = 0.0, ""
    for m in LR["models"]:
        for k in ("hca", "o", "d", "co", "cd"):
            a, b = LR["models"][m].get(k), SR["models"].get(m, {}).get(k)
            if isinstance(a, dict):
                if set(a) != set(b or {}): return False, f"{m}.{k}: different teams"
                for t in a:
                    d = abs(float(a[t]) - float(b[t]))
                    if d > worst: worst, where = d, f"{m}.{k}[{t}]"
            else:
                d = abs(float(a) - float(b))
                if d > worst: worst, where = d, f"{m}.{k}"
    for i, (a, b) in enumerate(zip(LR["blend_c"], SR["blend_c"])):
        if abs(a - b) > worst: worst, where = abs(a - b), f"blend_c[{i}]"
    if set(LR["games"]) != set(SR["games"]) or set(LR["conf"]) != set(SR["conf"]): return False, "games/conf keys differ"
    return worst <= TOL_NUM, f"max diff {worst:.4f} ({where or 'none'}), played_through {LR.get('played_through')}"

LOGP, MDP = os.path.join(ST, "shadow_compare_log.csv"), os.path.join(ST, "shadow_compare.md")
log = pd.read_csv(LOGP) if os.path.exists(LOGP) else pd.DataFrame(columns=["day", "game_day", "passed", "a_missed", "b_extra", "c_ratings", "d_decisions",
                                                                          "live_evals", "shadow_evals", "both", "only_live", "only_shadow", "live_bets", "shadow_bets", "note"])
done = set(log.day.astype(str))
days = sorted(set(LE.get("day", pd.Series(dtype=str))) | set(SE.get("day", pd.Series(dtype=str))))
days = [d for d in days if d < str(TODAY.date()) and d not in done]
rat_ok, rat_note = ratings_check()            # today's refit (both daily jobs ran this morning on the same data)
rows, md = [], []
for d in days:
    le, se = (LE[LE.day == d] if len(LE) else LE), (SE[SE.day == d] if len(SE) else SE)
    lb, sb = (LB[LB.day == d] if len(LB) else LB), (SB[SB.day == d] if len(SB) else SB)
    game_day = len(le) > 0
    a_miss, b_extra = match_bets(lb, SB), match_bets(sb, LB)
    li, si = set(le.an_id) if len(le) else set(), set(se.an_id) if len(se) else set()
    both = li & si; bad = []
    for g in sorted(both):
        x, y = le[le.an_id == g].iloc[0], se[se.an_id == g].iloc[0]
        ex, ey = x.get("edge"), y.get("edge")
        edge_bad = (pd.isna(ex) != pd.isna(ey)) or (not pd.isna(ex) and abs(float(ex) - float(ey)) > TOL_NUM)
        if x.verdict != y.verdict or str(x.reason) != str(y.reason) or edge_bad:
            bad.append(f"{g}: live {x.verdict}/{x.reason}/{ex} vs shadow {y.verdict}/{y.reason}/{ey}")
    passed = game_day and not a_miss and not b_extra and rat_ok and not bad
    rows.append(dict(day=d, game_day=game_day, passed=passed if game_day else None, a_missed=len(a_miss), b_extra=len(b_extra), c_ratings=rat_ok,
                     d_decisions=len(bad), live_evals=len(li), shadow_evals=len(si), both=len(both), only_live=len(li - si), only_shadow=len(si - li),
                     live_bets=len(lb), shadow_bets=len(sb), note=rat_note))
    md.append(f"\n## {d} ({'PASS' if passed else 'FAIL' if game_day else 'no games, skipped'})  [checked {pd.Timestamp.now(tz='America/New_York'):%Y-%m-%d %H:%M} ET]\n"
              f"- (a) missed alerts: {len(a_miss)} {a_miss[:5]}\n- (b) extra alerts: {len(b_extra)} {b_extra[:5]}\n"
              f"- (c) ratings: {'ok' if rat_ok else 'FAIL'}, {rat_note}\n- (d) decision mismatches: {len(bad)} of {len(both)} evaluated by both {bad[:5]}\n"
              f"- evaluations: live {len(li)}, shadow {len(si)}, only live {sorted(li - si)[:10]}, only shadow {sorted(si - li)[:10]}; "
              f"BET alerts: live {len(lb)}, shadow {len(sb)}\n")
if rows:
    log = pd.concat([log, pd.DataFrame(rows)], ignore_index=True); log.to_csv(LOGP, index=False)
    head = "" if os.path.exists(MDP) else "# NCAAM live move: shadow vs live, one section per game day (rule: ncaab/research/LIVE_MOVE_SHADOW_PASS_RULE_2026-11-06.md)\n"
    open(MDP, "a").write(head + "".join(md))
# running streak: consecutive passing game days at the end of the log, and live BET alerts inside it
g = log[log.game_day.astype(str) == "True"]
streak, bets = 0, 0
for _, r in g[::-1].iterrows():
    if str(r.passed) != "True": break
    streak += 1; bets += int(r.live_bets)
print("".join(md) if md else "No new completed game day to grade.")
print(f"STREAK: {streak} consecutive passing game day(s), {bets} live BET alert(s) inside -> "
      f"{'OVERALL PASS: ready for cutover (Jeffrey present)' if streak >= 3 and bets >= 1 else 'not yet'}")
