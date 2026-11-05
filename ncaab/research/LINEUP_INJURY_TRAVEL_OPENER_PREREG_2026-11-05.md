# NCAAM lineup / injury / travel layer at DraftKings' own opener: pre-registration v2 (Nov 5, 2026)

Written and pushed **before grading** (git history is the proof). Jeffrey, Nov 5, 2026: go ahead with the second pre-registration that v1 requires.
v1 (`LINEUP_INJURY_TRAVEL_PREREG_2026-11-05.md`, results `LINEUP_INJURY_TRAVEL_RESULTS_2026-11-05.md`): spreads PASSED against the close, totals FAILED.
This test asks the bettable question: **does the layer find bets at DraftKings' own opening spread that beat DraftKings' close and win money?**
Playbook steps covered: 2 (lineups, inferred injuries, travel/rest) and 3 (CLV from a line we can actually bet, units at the opener). System: sportsbooks (DraftKings).

## Scope
- **Spreads only.** Totals failed v1 and are not graded here (a fail is not re-run).
- **Features unchanged:** `derived/lineup_travel_features.csv.gz` exactly as built for v1 (definitions in the v1 pre-registration). No new features, no tuning of them.
- No FanDuel openers exist in our data (ESPN's feed has none for NCAAM); FanDuel is not tested.

## Prices
- **Bettable opener** = `book_sp` in `ncaab/data/all_games.csv` (the book's own first line from ESPN's feed; home spread). **Close** = `close_sp` (DraftKings' close for every row with a book opener).
- **TEST (headline): DraftKings openers, seasons 2024 (2023-24) and 2026 (2025-26)**. **Secondary: ESPN BET openers, 2025 (2024-25)**, reported, decides nothing
  (not offered in Connecticut). 2027 (current season) is not used (RULE 2).
- Stake 1 unit at -110 (headline). Diagnostic: units at the recorded opening price (`open_spread_px` from `espn_openers.csv`) where present.
- Note, stated up front: 2024-26 are not untouched. v1 graded the layer against the close on these seasons (in its leave-one-season-out design); nothing in
  this test is chosen on them.

## Guards (written now)
- **Flipped quotes:** drop if sign(book opener) differs from sign(DK close) AND from sign(Action Network Open), with |book opener| >= 1 (the Nov 5 book-opener correction rule).
  Drop if |book opener - DK close| > 10.
- **Timing:** openers have no timestamps. A team on a back-to-back (rest_days <= 1) probably had its opener posted before its previous game's box score existed, so its
  lineup features may not have been known. **Headline excludes games where either team has rest_days <= 1**; those games are reported separately.
- Same game filters as v1: both teams >= 5 earlier box-score games that season; base predictions (M2_m, M8_m, MKT_m) present; all 8 features present.

## Model (fit ONLY on the training seasons; nothing fitted on 2024-26)
Training seasons = SBR opener seasons **2008-2011 and 2014-2021** (not 2012-13: weak; 2022-23: no opener). Training rows: SBR opener and close present,
|open - close| < 6, and drop if sign(open) != sign(close) with both |x| >= 3.
- Target: **opener excess** = actual margin - opener-implied margin (= margin + opener spread).
- Base blend: least squares of margin on (1, M2_m, M8_m, MKT_m) fitted on the training seasons. Gap = blend - opener-implied margin.
- **Model A (base only):** ridge (lambda 10, standardized) of opener excess on the gap. **Model B (layer):** the same plus the 8 spread features (home - away), as in v1.
- One fit on all training seasons; the fitted means/sds, blend weights and ridge coefficients are then applied unchanged to 2024, 2025, 2026.

## Bet rule
Bet the side the model favors at the opener when |predicted opener excess| >= k. **k** = the smallest of {0.5, 1, 1.5, 2, 3} whose pooled
leave-one-season-out CLV inside the training seasons (fit on 11 training seasons, predict the 12th; CLV = SBR close vs SBR open in the bet's direction)
is >= 0.67. If none qualifies, k = 3. Chosen separately for A and B. Bets that land exactly on a key half-point are not special-cased.

## Measures (TEST = DraftKings 2024 + 2026, timing-guarded)
1. **CLV** = (DK close - DK opener) in the bet's direction, points. Break-even 0.67 (from the book-opener test). Mean, and 90% interval (game-level bootstrap, 5,000 draws, seed 7).
2. **Units at the DK opener** (-110), and per season.
3. **Beat-the-opener slope of the layer:** regress (actual margin - opener-implied margin) on model B's layer part (gamma . features) over all TEST games
   (not only bets); heteroskedasticity-robust t (game level; only two seasons, so no season clustering). Same against (DK close - DK opener) as a diagnostic.
4. The same for model A (base only) and B side by side; ESPN BET 2025 and the back-to-back games reported separately.

## PASS (all needed; model B, DraftKings TEST rows)
- **Q1** CLV >= 0.67 **and** the 90% interval's low end > 0.
- **Q2** units at the DK opener > 0, and **no DK season below -5u**.
- **Q3** the layer adds information at the opener: beat-the-opener slope of the layer part > 0 with t > 2.
- **Q4** the layer is not worse than the base: model B's CLV >= model A's CLV.
**PASS -> PROVISIONAL candidate only after a Fable review and Jeffrey's approval** (nothing goes live from this file). **FAIL** on any one -> recorded negative result;
not re-run with new definitions; any change is a new numbered pre-registration.

## Expected power (stated before looking)
About 9,000 DraftKings games after filters; a few hundred to a few thousand bets depending on k. With ~1,000 bets, luck alone moves ROI by about +/-3%, so Q2 is
noisy; Q1 and Q3 carry most of the evidence.
