# NCAAM: does the lineup / injury / travel layer improve the model that predicts DraftKings' close? Pre-registration (Nov 5, 2026)

Written and pushed **before grading**. Jeffrey, Nov 5, 2026 (18:52): try adding the layer to the close model.
Why: the layer predicts the opener-to-close line move (t +7.85, v2) but does not pick better bets (v3). The three-target close model C3
(`ncaab/three_targets_grade.py`; close - opener on the gaps M2 - opener, MKT - opener, M8 - opener) is the place where that information should help.
Playbook step 2 (lineups, injuries, travel) feeding step 3 (predicting the close). No bets are made or graded here.

## Models (OLS, as in the three-target test; no tuning)
- **C0** close = opener. **C3** close - opener ~ 1 + (M2 - opener) + (MKT - opener) + (M8 - opener).
- **C3L** = C3 + the 8 layer features from `derived/lineup_travel_features.csv.gz` (unchanged): spreads home - away, totals home + away.
- Spreads in margin units (opener-implied margin = -spread); totals in points. Spreads and totals judged separately.

## Primary design: leave-one-season-out on SBR seasons (opener and close from SportsbookReview)
Seasons 2008-2011 and 2014-2021 (12). The opener-to-close relation was never graded on these seasons (v2 and the timing test only used them for fitting).
Rows: both teams >= 5 earlier box-score games; M2/M8/MKT and all features present; opener and close present.
Guards: spreads |open - close| < 6 and drop opposite signs with both |x| >= 3; totals |open - close| < 10.
For each season: fit C3 and C3L on the other 11, predict the held-out season.

## Secondary (decides only P3; the move relation was seen on these seasons in v2)
Same as the three-target test: fit on DraftKings rows 2023-24 (book's own opener vs DK close), test on DraftKings 2025-26; back-to-back games kept
(this is about predicting the close, not betting). Flipped book quotes dropped (v2 rule). ESPN BET 2024-25 reported, decides nothing.

## Measures
RMSE vs the close (C0, C3, C3L); MSE gain = MSE(C3) - MSE(C3L), pooled over held-out rows, t clustered by season; number of seasons with a gain;
correlation of predicted and actual move (C3, C3L).

## PASS per market (all needed)
- **P1** pooled LOSO MSE gain > 0 with season-clustered t > 2.
- **P2** gain in at least 9 of the 12 seasons.
- **P3** DraftKings 2025-26: RMSE(C3L) < RMSE(C3).
**PASS -> C3L replaces C3 as the research close model** (used for timing and CLV forecasts in later tests; nothing live). **FAIL -> recorded; C3 stays.**
