# NCAAM early-season roster layer (returning production, incoming transfers). Pre-registration (Nov 5, 2026)

Written and pushed **before any feature is built or graded**. Jeffrey, Nov 5, 2026 (19:36): build the early-season roster-strength layer (Claude's pick from
the idea list). Why: 62 of 84 top-edge base-model bets fall in Nov-Dec, when team ratings still lean on last season (the walk carries 0.8 of last season's
final rating) and rosters turn over heavily (transfers). Playbook step 2: "transfers and returning minutes". System: sportsbooks (DraftKings).

## Data
- Player box scores `ncaab/data/box/players_{season}.csv.gz` (athlete_id, team_id, minutes, points per game), seasons 2008-2027; games `ncaab/data/all_games.csv`;
  base predictions `ncaab/data/three_targets_preds.csv` (M2_m, M8_m, MKT_m, walk-forward).
- ESPN does not keep historical rosters (checked: 2014-15 roster empty), so **a team's known roster for game g = players who recorded minutes for that team in
  its games strictly before g's date this season.** Features therefore exist from a team's 2nd game.

## Features (per team, per game; spreads use home - away)
Last season (s-1) per player: total minutes and points, and his main team (most minutes). Per team: s-1 total points; s-1 strength = mean actual margin per game.
For team T in game g of season s, with n = T's games before g this season (1 <= n <= 14) and early = (15 - n) / 15:
- **R1 turnover** = early x (1 - ret), ret = s-1 points of known players whose main s-1 team was T / T's s-1 total points (capped at 1).
- **R2 incoming** = early x inc, inc = s-1 points of known players whose main s-1 team was another D-I team / T's s-1 total points (capped at 2).
- **R3 lost strength** = early x (1 - ret) x str(T), str = T's s-1 mean margin (a good team that lost its scorers is overrated by the carry-over).
- **R4 imported strength** = early x inc x strin, strin = points-weighted mean s-1 margin of the incoming players' old teams.
Rows with no s-1 data for either team (new D-I programs, missing box seasons) are dropped.

## Rows
**Early-season games only:** both teams 1 <= n <= 14. Close present; spread guards as before (|open - close| < 6 and the flipped-sign guard where an opener exists).
Base predictions present. Seasons: s-1 box data is needed, so 2009-2011 and 2014-2026 (2012-13 weak/missing box seasons excluded as season s; 2014 uses
2012-13 (87% box) as s-1: kept, noted). 2027 (current) not used.

## Test 1 (primary): beats the close, leave-one-season-out over the 16 seasons
Target: actual margin - close-implied margin. Model A: ridge (lambda 10, standardized) on the base gap (LOSO blend of M2/M8/MKT minus the close). Model R: A + R1-R4.
Held-out predictions for each season from fits on the other 15.
**PASS-1 (all):** (a) slope of the excess on the held-out roster part > 0 with season-clustered t > 2; (b) slope > 0 in at least 11 of 16 seasons;
(c) MSE(A) - MSE(R) > 0 with season-clustered t > 2.

## Test 2: bettable, DraftKings' own opener (2023-24 + 2025-26; these seasons have been looked at before for other layers, not for these features)
Fit on SBR opener seasons 2009-2011 and 2014-2021, target actual - opener-implied margin, models A and R as above (opener in place of the close).
Predict DraftKings' own openers 2024 + 2026 (flipped quotes dropped; back-to-backs kept: these features use only earlier games and last season).
**PASS-2 (all):** (a) beat-the-opener slope of the roster part > 0 with robust t > 2; (b) at the top 5% of early-season DK games by |prediction| (per season),
CLV(R) >= CLV(A) and CLV(R) >= 0.67.

## Consequences
PASS-1 and PASS-2 -> the roster terms are added to the base model as a candidate for the stale-line rule's BLEND-C and a Fable review (nothing live directly).
PASS-1 only -> [LEAD]: the close already knows it; useful for predicting the close. FAIL-1 -> recorded negative; not re-run with new definitions.
