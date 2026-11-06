# NCAAM live move: shadow-run pass rule (written and pushed BEFORE the shadow run, Nov 6, 2026)

Plan: `betting-goals/plans/2026-11-06_NCAAM_LIVE_MOVE.md` (Jeffrey approved). This file is Phase 0 step 3. Git history is the proof it was
pushed before `ncaab-alerts.yml` (shadow) started.

## What is compared
- **Live (sends alerts):** `nba-mixed-model/ncaab/state/` written by nba `alert_loop.sh` (line 43) and nba `ncaab.yml`.
- **Shadow (sends nothing):** `NCAAM/ncaab/state/` written by NCAAM `ncaab-alerts.yml` (`ncaab/alert_loop.sh`, `NCAAM_SHADOW=1`,
  no `NTFY_TOPIC`) and NCAAM `ncaab.yml`. Same code: `ncaab/*.py` copied byte-for-byte from nba at this commit.
- Start point: NCAAM's state was copied from nba at this commit (last nba evaluation in the copy: `2026-11-06 01:00` ET). Only rows
  with `at_et` after `2026-11-06 01:00` are compared.
- Script: `ncaab/shadow_compare.py`, run daily by `ncaab-shadow-compare.yml` after both daily jobs; result appended to
  `ncaab/state/shadow_compare.md` and `ncaab/state/shadow_compare_log.csv` (committed).

## A game day passes when ALL of these hold (ET date of `at_et`)
- **(a) No missed alert:** every row in nba `live_bets.csv` that day has a row in NCAAM `live_bets.csv` with the same `an_id`, `side` and
  `line`, and `at_et` within 10 minutes (one 5-minute poll plus scheduler slack).
- **(b) No extra alert:** no NCAAM `live_bets.csv` row that day lacks such a match in nba.
- **(c) Ratings match:** NCAAM `live_ratings.json` vs nba's, when both have the same `played_through`: every number (`models.*.hca/o/d/co/cd`,
  `blend_c`) within 0.01, and the same `games` and `conf` keys. If `played_through` differs on the compare day, (c) is "not comparable" for that
  day, which counts as a FAIL (the two daily jobs must refit on the same data).
- **(d) Same decisions (added to the plan's a-c because no BET alert has fired yet this season):** for every `an_id` evaluated by both
  (`live_evals.csv`), the same `verdict`, the same `reason`, and `edge` within 0.01. Games evaluated by only one side are listed and counted,
  and are a FAIL only if the other side's row is a BET (that is already (a)/(b)).
- A **game day** = a date with at least 1 nba evaluation. Days with none are skipped (neither pass nor reset).

## Overall pass (allows Phase 2 cutover)
- 3 consecutive passing game days, **and** at least 1 nba BET alert inside the passing window (so the alert path itself was tested).
  If teams are still under 3 games and no BET fires, the window simply extends.
- Any FAIL: the cause is found and fixed (FINDINGS `[OBSERVATION]` entry), and the 3-day count restarts at 0.
- Cutover itself (Phase 2) needs Jeffrey present. Note: `NTFY_TOPIC` is already set in NCAAM (ops/ntfy_test_result.txt, Nov 6 10:10 ET, ntfy HTTP 200),
  so the shadow loop unsets it explicitly while `NCAAM_SHADOW=1`; cutover = set `NCAAM_SHADOW: "0"` and pass the secret.
