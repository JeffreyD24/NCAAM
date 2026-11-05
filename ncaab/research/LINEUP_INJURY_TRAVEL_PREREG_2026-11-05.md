# NCAAM lineups / inferred injuries / travel layer on the market base model. Pre-registration (Nov 5, 2026)

Written and pushed **before any feature is built or graded** (git history is the proof). Jeffrey, Nov 5, 2026: build the lineups, inferred-injuries
and travel layer on top of the market base model, pre-registered before it is graded.
Playbook (betting-goals `MODEL_PLAYBOOK.md`) steps covered: **2 (lineups and minutes; injuries inferred from minutes; travel and rest)** and
**3 (beat-the-close slope, RMSE vs the close)**. Not covered here: sharp money, CLV from a bettable DraftKings/FanDuel opener (see "Out of scope").
Serves the sportsbook system (graded against the book's own close).

## Data
- `ncaab/data/all_games.csv` (games, closing spread `close_sp` = home spread, negative = home favored; closing total `close_tot`; results).
- `ncaab/data/three_targets_preds.csv` (walk-forward `M2_m`, `M8_m`, `MKT_m`, `M2_t`, `M8_t`, `MKT_t`; each uses only games before its date).
- `ncaab/data/box/players_{season}.csv.gz` (starter, minutes, points per player per game), `teams_{season}.csv.gz` (venue city and state).
- Season label = year the season ends (2008 = 2007-08). Margin = home_pts - away_pts. Close-implied margin = -close_sp.
- Venue coordinates: city/state matched to the `zipcodes` package (mean of the place's ZIPs); a hand table for the ~40 places it misses
  (Moon Township PA, Storrs CT, Maui, Nassau, San Juan, ...), labeled approximate (tens of miles, irrelevant at this scale).
  Games with a blank venue city: home team's base if it was a home game; otherwise travel features are missing and the game is dropped from the
  travel groups only.

## Games and seasons
- **Headline test seasons (17):** 2008-2011 and 2014-2026. **Weak seasons, reported separately, never in the headline or in training:**
  2012 (2011-12: player box 89%) and 2013 (2012-13: player box 87%, only 922 closes). **2027 (current season) is NOT used** (RULE 2).
- Game filter: a close exists; if an opener exists, |close_sp - open_sp| < 6 (bad-quote guard, same as MKT-T); both teams have >= 5 earlier games
  that season with player box scores; base model prediction exists. Neutral sites kept.
- Every feature uses only games with a strictly earlier date than the game (same-day games excluded).

## Base model (the market base)
B_m = leave-one-season-out least-squares blend of `M2_m`, `M8_m`, `MKT_m` fitted to the actual margin on the other headline seasons (intercept + 3 weights);
B_t the same for totals. The close-implied margin/total C is the benchmark: excess = actual - C.
Reference model **A**: excess ~ a + b * (B - C). That is "base model vs the close" with no new information.

## Features (all pre-game; computed per team, then home minus away for spreads, home plus away for totals)
Rotation reference for a team = its last 10 games that season (all of them if fewer than 10, minimum 5). A **regular** = top 8 by average minutes in
that window AND >= 15 minutes per game AND played in >= 6 of the 10.
1. **A lost_min_share:** share of the regulars' average minutes belonging to regulars who recorded 0 minutes (or no row) in the team's most recent game.
   (Minutes vanishing: the only injury signal in college. Known before tip.)
2. **B lost_pts_share:** same with average points.
3. **C new_starters:** number of starters in the team's most recent game who were not among the 5 most frequent starters over the 10 games before it (0-5).
4. **D travel_miles:** log(1 + great-circle miles) from the team's previous game's venue (its home base, the modal home-game venue that season, for its first game) to this venue.
5. **E tz_shift:** absolute difference in round(-longitude/15) between the previous venue and this venue.
6. **F rest_days:** days since the team's previous game, capped at 7. **G back_to_back:** 1 if rest_days <= 1. **H games_last_7:** team games in the 7 days before.

Feature groups: **LINEUP/INJURY** = A, B, C; **TRAVEL/REST** = D, E, F, G, H; **ALL** = both.

## Fitting (no tuning)
Ridge, penalty fixed at lambda = 10 on features standardized with the training seasons' mean and sd, intercept unpenalized. Model **B**:
excess ~ a + b * (B - C) + gamma . features. Spreads and totals separately. Nothing is tuned on any test season; lambda and every definition above are fixed now.
- **Primary design: leave-one-season-out (LOSO).** For each of the 17 headline seasons, fit on the other 16, predict the held-out season.
- **Secondary design: forward.** Fit on all earlier headline seasons, predict season s, for s = 2016-2026. Reported, decides nothing alone.

## Measures (held-out predictions only)
1. **Beat-the-close slope (primary):** regress actual excess on the layer's held-out predicted excess (gamma . features part, plus b*(B-C) part for the full model);
   slope > 0 means the model knows something the close doesn't. Pooled over the 17 seasons, standard error clustered by season. Also the slope per season.
2. **Incremental value:** held-out MSE of model B vs model A, pooled; paired difference with season-clustered t.
3. RMSE of C, A and B vs the actual result (diagnostic). Hit rate and units at the CLOSE when betting the sign of the predicted excess where |predicted excess| >= 1
   point (diagnostic only; minus vig this is expected to be negative; not a pass criterion).
4. Weak seasons 2012 and 2013 predicted with the model fit on the headline seasons; shown beside the headline, not pooled with it.
5. **Oracle (diagnostic, NOT tradable, never a pass criterion):** the same features using the game's OWN box score (who actually played) to size how much
   an absence is worth if known; shown only to make clear how much of the signal is available before tip.

## PASS rules (written now; spreads and totals judged separately, ALL feature set)
**PASS** needs all of: (P1) pooled held-out slope > 0 with t > 2; (P2) the slope is positive in at least 12 of the 17 headline seasons;
(P3) model B beats model A in pooled held-out MSE with t > 2. Failing any one = **FAIL**; a fail is a recorded negative result, not re-run with new definitions.
Group-level claims (LINEUP/INJURY alone, TRAVEL/REST alone; 4 extra tests per market) need t > 2.5 for the same P1/P3 (multiple-test guard);
group results are labeled `[LEAD]` at best.
Any definition changed after seeing a result starts a new, separately numbered pre-registration; this one stays as written.

## Out of scope (stated, not skipped)
- No bets are placed or recommended from this test. A PASS means the layer is a PROVISIONAL candidate only after a second pre-registration that grades
  CLV against DraftKings' / FanDuel's own opener (exists only 2023-24 and 2025-26 for DraftKings) and a Fable review.
- Sharp-money features (playbook step 2, last bullet) are a separate build.
- Closes before 2023 are SBR / book closes; their bettability is not claimed.
