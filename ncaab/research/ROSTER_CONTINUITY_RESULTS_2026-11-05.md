# NCAAM early-season roster layer: results (Nov 5, 2026)

Pre-registration `ROSTER_CONTINUITY_PREREG_2026-11-05.md` (pushed 8054b0a before building). Features `ncaab/roster_features.py` -> `derived/roster_features.csv.gz`;
grading `ncaab/roster_grade.py` -> `research/roster_grade_output.txt`, DK bets `research/roster_dk_bets.csv`. Run once. Early-season games only (both teams' games 2-15).

## Verdict: FAIL (Test 1, the primary test, misses one condition)
| Test 1: vs the close, leave-one-season-out, 16 seasons (25,488 games) | Result | Rule |
|---|---|---|
| (a) roster-part slope on (actual - close) | +0.341, season-clustered t **+2.37** | pass |
| (b) seasons with a positive slope | **12 / 16** (need 11) | pass |
| (c) MSE gain over the base-gap model | +0.103, t **+1.80** (need > 2) | **fail** |
| RMSE vs result: close / base gap / + roster | 11.358 / 11.350 / 11.346 | |
Coefficients (standardized): gap +0.565, **R1 turnover -0.406** (teams that lost more of last season's scoring do worse than the close expects), **R2 incoming
transfers +0.252** (teams that brought in more production do better), R3 -0.076, R4 -0.004.

| Test 2: DraftKings' own opener 2023-24 + 2025-26 (fit SBR 2009-11, 2014-21; 3,293 early DK games) | Result | Rule |
|---|---|---|
| (a) beat-the-opener slope of the roster part | +0.539, robust t **+2.29** | pass |
| (b) top 5% of games: CLV with roster vs base only | **+1.67 vs +1.31** (166 bets each; break-even 0.67) | pass |
| units at the opener (diagnostic) | roster -0.7u (2024 +3.3, 2026 -4.0); base only +9.7u | |
| roster part vs DraftKings' line move (close - opener) | +0.334, t **+8.25** | |

## Read
- Same pattern as the lineup/injury/travel layer: roster turnover and incoming transfers are **mostly missing from DraftKings' college opener and largely priced
  into the close** (predicts the opener-to-close move, t +8.25). Against the close, a small effect remains (slope t +2.37, 12/16 seasons) but not enough to pass.
- Signs are sensible: losing last season's scorers hurts more than the market's carry-over expects; adding transfers helps.
- At DraftKings' opener the roster terms add line value (CLV +1.67 vs +1.31 at matched counts) but not units on 166 bets (noise: about +/-12u).
- By the pre-registered consequences, FAIL-1 is a recorded negative for the roster layer as a stand-alone edge vs the close. Test 2's pass is a [LEAD], not a candidate.

## Where this points (Claude)
Both new layers forecast DraftKings' line move from opener to close (travel/lineups t +7.85, roster t +8.25). The live **stale-line rule** bets exactly that move
(DK's opener vs its predicted close, BLEND-C). The best use of both layers is to add them to BLEND-C and test whether the stale-line rule improves at DK's opener.
Pre-register that next (Jeffrey's call): fit on SBR seasons, grade on DK 2023-24 + 2025-26 against the current stale-line rule at matched bet counts.
