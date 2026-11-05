# NCAAM lineup / injury / travel layer at DraftKings' own opener: results v2 (Nov 5, 2026)

Pre-registration `LINEUP_INJURY_TRAVEL_OPENER_PREREG_2026-11-05.md` (pushed 438412a before grading). Code `ncaab/lineup_travel_opener_grade.py`, output
`research/lineup_travel_opener_grade_output.txt`, every bet `research/lineup_travel_opener_bets.csv`. Run once. Spreads only. Model fit only on SBR 2008-11 and 2014-21;
graded on DraftKings' own openers 2023-24 and 2025-26 (8,370 games, back-to-backs excluded for timing).

## Verdict: FAIL (Q4)
| | Model A (base gap only) | **Model B (base + layer)** | rule |
|---|---|---|---|
| k (chosen in training; no k reached CLV 0.67 on SBR, so the default 3) | 3 | 3 | |
| Bets at DK opener | 60 | **151** | |
| Hit / units (-110) | 59.3% / +7.8u | **55.7% / +9.5u** (2024 +4.3, 2026 +5.2) | Q2 pass |
| CLV vs DK close [90% interval] | +1.85 [+1.39, +2.33] | **+1.49 [+1.17, +1.81]** | Q1 pass (b/e 0.67) |
| Layer beat-the-opener slope | | **+0.748 (t +3.89)** | Q3 pass |
| Mean CLV, B >= A | | 1.49 < 1.85 | **Q4 fail** |

Q1-Q3 pass; Q4 fails, so by the written rule the layer is **not** a PROVISIONAL candidate and no Fable review is triggered.

## What else the run shows
- **The layer forecasts DraftKings' line move:** layer part vs (close - opener) slope +0.221, **t +7.85** over all 8,370 games. The layer's information (absences,
  rotation changes, travel, rest) is mostly NOT in DraftKings' college opener and mostly IS in the close. That fits the earlier finding that DK's opener looks
  like a results-based power rating and the close moves toward the market consensus.
- **Why Q4 failed:** both models use k = 3. The layer flags 2.5x as many games (151 vs 60; 54 of A's 60 are also B bets). The 97 extra bets average CLV +1.23,
  above break-even but below A's most extreme 60, which pulls B's average down. Total CLV captured: B 224.5 points, A 111.0. Comparing averages over bet sets of
  different sizes was a weak choice of rule, but it is the registered rule and the FAIL stands. A fairer comparison needs a new, numbered pre-registration.
- **Not a blowout artifact (post-hoc, decides nothing):** median CLV B +1.00 (A +1.50). 69% of B's bets got a better close, 17% worse. With |opener| <= 15 only: B 116 bets,
  CLV +1.16, +7.2u.
- **Accuracy vs the result:** DK opener RMSE 11.224, model B 11.226, DK close 11.170. The model is not more accurate than the opener across all games. Its value is in
  the few games where it disagrees most.
- **Units are noise at this size:** 151 bets at -110 can swing about +/-12u from luck alone. The +9.5u says little either way. At the recorded DK price
  (home-side bets): +10.7u vs +11.2u at -110.
- **Secondary (decides nothing):** ESPN BET 2024-25 (not in CT): B 59 bets, CLV +1.58, +4.0u; layer slope +0.39 (t +1.45). DK back-to-back games: B 34 bets,
  CLV +1.72, +4.2u. ESPN BET gaps: 13 bets.
- Training: 23 flipped book quotes dropped from the test rows. On SBR training seasons the best LOSO CLV was +0.59 (B, k 3), below 0.67, which is why k defaulted to 3.

## Decision
Nothing goes live and no bets. The layer is not a candidate under v2. Recorded leads:
1. **[LEAD] Line-move forecaster for timing:** the layer predicts DK's move (t +7.85). Use it to decide *when* to bet a game the base model already likes
   (bet early when the layer predicts a move our way). Needs its own pre-registration.
2. **[LEAD] v3 with a fair comparison:** compare B vs A at matched bet counts (each model's top-N games) or by total CLV, chosen in training, graded on the same
   DK seasons. Jeffrey decides whether to run it. These seasons have now been seen twice, so a v3 pass would be weaker evidence than a first look.
3. The base gap at k 3 (model A) cleared Q1-Q2 on 60 bets. It was the reference, not the test. The earlier book-opener test of Model 1 at DK (CLV +1.26, flat units)
   says the same: line value at DK's opener is real, profit is not yet shown.
