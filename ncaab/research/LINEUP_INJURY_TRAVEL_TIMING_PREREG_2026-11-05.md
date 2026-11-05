# NCAAM bet timing: bet the base model's picks at the opener, or wait for the close, decided by the layer's predicted line move. Pre-registration (Nov 5, 2026)

Written and pushed **before grading**, together with the v3 pre-registration. Jeffrey, Nov 5, 2026 (18:40): explore the bet-timing option.
Lead from v2: the layer predicts DraftKings' opener-to-close move (slope +0.221, t +7.85 on the DK TEST games). **That relation was seen on these seasons**, so this test
is not a first look; a pass is labeled weaker evidence. Playbook steps covered: 2 (lineups, injuries, travel) used for step 3 (CLV from a line we can actually bet).

## Question
Among bets the base model already wants at DraftKings' opener, does waiting for the close when the layer predicts the line will move AGAINST us get a better number,
and does that timing rule beat "always bet at the opener"?

## Data and rows (same as v2)
Training: SBR opener + close seasons 2008-11 and 2014-21 (v2 guards). TEST: DraftKings' own openers 2024 + 2026, flipped quotes dropped, back-to-backs excluded.
ESPN BET 2025 secondary. Only two prices exist per game (opener, close); "wait" means taking the close. Spreads only. -110 at either price.

## The base bets (fixed now)
Model A (v2: base gap only, fit on training) bets its side when |predicted opener excess| >= **1 point** (k = 1, fixed now: v2's k = 3 left only 60 TEST bets).
The timing rule never changes which side or which games are bet; it only changes WHEN (and so at which number).

## Line-move model (fit on training only)
Target: line move toward home = opener spread - close spread (home spread; positive = moved toward home). Ridge (lambda 10, standardized), regressors:
the base gap and the 8 layer features (home - away), as in v2. Predicted move in the bet's direction m = side x predicted move.

## Timing rule
Bet at the opener if m > -t; **wait for the close** if m <= -t. t is chosen in the training seasons from {0, 0.25, 0.5, 0.75}: leave-one-season-out
(fit the move model and model A on 11 training seasons, apply to the 12th), pooled points gained (below); the t with the most points gained; ties -> the larger t.

## Measures (TEST)
- **Points gained** = over the waited bets, the line obtained at the close minus the line at the opener, in the bet's direction (= minus that bet's opener CLV);
  report total, mean per waited bet, and the 90% bootstrap interval of the total (5,000 draws, seed 7). Also as a share of all base bets.
- **Units**: timing rule (each bet graded at the price actually taken) vs always-at-opener vs always-at-close, same games, -110.
- Diagnostics: same with the move predicted by the base gap alone (no layer), to show what the layer adds; by season.

## PASS (all needed)
- **T1** total points gained > 0 with its 90% interval low end > 0.
- **T2** units(timing rule) >= units(always at opener).
- **T3** the layer matters: points gained with the layer move model > points gained with the base-gap-only move model (same t).
**PASS -> a candidate timing aid for alerts ("wait" flag), after a Fable review; weaker evidence (seen seasons). FAIL -> recorded.**
