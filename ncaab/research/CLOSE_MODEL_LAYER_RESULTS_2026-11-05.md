# NCAAM: layer added to the close model: results (Nov 5, 2026)

Pre-registration `CLOSE_MODEL_LAYER_PREREG_2026-11-05.md` (pushed eb84784 before grading). Code `ncaab/close_model_layer_grade.py`, output
`research/close_model_layer_output.txt`. Run once. Predicting close - opener: C0 (no move), C3 (three-target close model), C3L (C3 + the 8 layer features).

## Verdict: PASS for spreads and totals -> C3L replaces C3 as the research close model
| | Spreads | Totals |
|---|---|---|
| SBR leave-one-season-out, 12 seasons: RMSE C0 / C3 / C3L | 1.223 / 1.206 / **1.197** | 2.303 / 2.110 / **2.096** |
| Correlation with the actual move: C3 / C3L | +0.161 / **+0.204** | +0.398 / **+0.412** |
| MSE gain, season-clustered t (P1) | +0.023, **t +5.21** | +0.058, **t +3.39** |
| Seasons with a gain (P2, need 9) | **12 / 12** | **10 / 12** (2008, 2021 worse) |
| DraftKings 2025-26 (fit DK 2023-24): RMSE C0 / C3 / C3L (P3) | 1.544 / 1.502 / **1.482** (corr +0.25 -> +0.30) | 2.583 / 2.414 / **2.399** (corr +0.36 -> +0.38) |
| ESPN BET 2024-25 (decides nothing) | 1.485 / 1.460 / 1.439 | 1.997 / 2.008 / 2.000 |

Strongest terms (fit on all 12 SBR seasons): back-to-back (spreads -0.82, totals -0.54 points of move) and the lost-minutes / lost-points pair (large, opposite
signs because the two are collinear; read together, not separately).

## Read
- Out of sample on 12 seasons the layer was never graded on for this question, and it holds on DraftKings' own lines. The layer's information (absences, rotation
  changes, travel, rest) reaches the close and is mostly missing from the opener. Solid [CORRELATION] about how the market moves; the effect is modest
  (spreads: correlation with the move +0.16 -> +0.20 on SBR, +0.25 -> +0.30 at DraftKings).
- This is a better forecast of where DraftKings' line will close, not a bet signal (v3: the layer doesn't pick better bets at the opener).

## Decision
C3L is now the research close model for later tests (CLV forecasts, timing). Nothing live, no bets. Decided by the pre-registration (Jeffrey asked for the test).
