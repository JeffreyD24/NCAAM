# NCAAM player props v1 / v1s — results (graded Nov 6, 2026, ~01:35 ET)

Pre-registration: `PROPS_V1_PREREG_2026-11-05.md` (+ Amendment 1, pushed before grading). Script `ncaab/props/backtest_v1.py`,
full output `ncaab/props/backtest_v1_output.txt`, every bet `ncaab/props/backtest_v1_bets.csv.gz` / `backtest_v1s_bets.csv.gz`.
Data: BettingPros NCAAB points (269) and rebounds (270) props, 716 dates Nov 2021 – Apr 2026; 69,996 sportsbook openers after the timing guard.

## Verdict: both pass all four pre-registered checks as written, BUT the Fable review found the closing-line check is fragile, and a corrected run fails it. Not live. Status: LEAD (Jeffrey decides on a PROVISIONAL record).

Short version: the model makes money on three unseen seasons (+280-300u, ROI ~+14-15%), but the closing line never moves toward the bets.
Check 3 passes only when the 2025-26 closing lean feeds the adjustment for earlier seasons. With a walk-forward lean (prior seasons only)
plus the matching fixes, closing-line EV is −0.07% and check 3 fails.

| | v1 (NBA v1b port) | v1s (+ blowout minutes) |
|---|---|---|
| FIT w (model weight) | 0.204 | 0.203 |
| Information test (model beyond the opener), test seasons | +0.217, 90% CI [+0.187, +0.247] | +0.212 [+0.183, +0.242] |
| 2023-24 TEST | 663 bets, +88.8u, ROI +13.4% | 633, +91.0u, +14.4% |
| 2024-25 TEST | 518 bets, +79.2u, +15.3% | 498, +80.9u, +16.2% |
| 2025-26 TEST | 808 bets, +126.1u, +15.6% | 770, +129.2u, +16.8% |
| Pooled TEST | 1,989 bets, +294.1u, ROI +14.8% [+11.7, +18.0] | 1,901, +301.1u, +15.8% [+12.6, +18.9] |
| Closing-line EV raw / lean-adjusted | −4.24% / **+0.64%** [+0.20, +1.10] | −4.21% / +0.63% [+0.20, +1.11] |
| Every under at the same openers | −584u, ROI −1.0% (57,311 bets) | same |
| Checks 1-4 | ALL PASS | ALL PASS |

Tie-break (pre-registered: higher lean-adjusted closing-line EV): v1 +0.64% vs v1s +0.63%, so **v1**. The difference is noise: the fitted
blowout effect was tiny (β0 −0.040, β1 +0.053: a 30-minute starter at a 25-point spread loses ~0 minutes), so v1s is v1 in practice.

## What the bets look like
- **97% unders** (1,936 of 1,989; overs 53 bets, −4.8u). The model is not "bet every under" (that loses 1%); it picks unders where the line is
  well above the player's projection (median line − model mean +3.3).
- Rebounds earned more than points: reb 811 bets +193u (ROI +23.8%), pts 1,178 bets +101u (+8.6%). Rebounds were positive every season.
- Every month positive; openers posted 12-24 h before tip did best (+18.8%).
- Price: median −102.

## Takeaways (Claude)
1. **This is the strongest prop result we have**: three unseen seasons all clearly positive, and the information test is far from zero in each season.
   Even so, +15% ROI is large enough that a hidden leak has to be ruled out before anyone trusts it. That is what the Fable review is for (below).
2. **The market does not move our way.** Raw closing-line EV is −4.2%: closing lines move further toward overs, not toward our unders. Closing
   lines in NCAAM props lean to overs by +1.6 to +5.4 points of probability every season (2025-26: +5.4), much more than the NBA (~1-1.6). Only after that lean
   is removed is closing-line EV slightly positive (+0.6%). So the edge looks like **books and bettors pricing college props too high**
   (an over bias), not information the sharp market later agrees with. It can still be real money, but the closing line won't confirm it bet by bet.
3. **Where Jeffrey can bet it:** DK/FD openers alone: 753 bets +90.5u (+12.0%), but 95% of DK/FD bets come from 2023-24; DK/FD posted few college
   props in 2024-25 (86 bets) and 2025-26 (35). Our own feed shows DK and FD are posting NCAAM props in Connecticut this season, but
   **DraftKings only offers "X+" milestone ladders**, which are over-only. An under-heavy model can't bet DK milestones; FanDuel's O/U lines are the usable market.
4. **Known weakness found while checking (not a leak):** the minutes projection never lets the prior fade (the exponential weights cap the
   season's effective games at ~7.7 against a 5-game prior), so heavy-minute players are projected ~2 minutes low (~7%) and the model
   leans to unders. That bias is in every season of the test, so the results already include it; fixing it is a v2 candidate, not a reason to distrust v1.
5. Next: v2 (fixed minutes prior + inferred absences), pre-registered on the same seasons; live shadow logging at FanDuel O/U openers.

## Fable review (Nov 6, 2026, ~02:00 ET): CONCERNS
Fable ran its own code on the repo data. Found clean: no same-game or later information in the features (recomputed min_proj and rates on 47k / 35k rows:
0 mismatches); dates line up (BP date = ET, ESPN = ET); 270 = rebounds in every season and book; pushes and DNP voids handled correctly;
openers have both sides from the same book and time, 1h+ before tip.
Issues:
1. **Check 3 rests on the current season's number.** The 2025-26 close over-lean (+5.39) goes into the leave-one-season-out adjustment for
   2023-24 and 2024-25. Drop it, or use a walk-forward lean, and lean-adjusted closing-line EV goes to about −0.05%: **fail**. Raw closing-line EV is −4.2%.
2. **The edge is unders against an over-shaded market**, not something the closing line confirms. Overs hit 47.6% across all 57k sportsbook openers
   (2025-26: 44.7%). The model's ranking is real (over rate falls 53% → 41% across deciles of (line − mu)/sd while the opener moves only 0.52 → 0.48),
   but it is a regression-to-the-mean bet on players it under-projects. If books stop shading openers to the over, the edge goes with it.
3. **Live access:** 49% of bets are BetMGM openers; the DK/FD slice (753 bets) is 84% 2023-24, with 35 bets in 2025-26.
4. **Wrong-player matches lean to unders:** 14 bets +12.6u (13 of 14 won), including FGCU team totals graded as a player named "George Washington".
5. **Reproducibility:** the run read the full `_tmp/` features (624k rows), not the committed `derived/` copy (572k), which shifts a few fits and bets.

## Correction run (Nov 6, NOT pre-registered, labeled; `backtest_v1.py --fixes`, output `backtest_v1_fixes_output.txt`)
Committed `derived/` features only; matches dropped when the ESPN game is not the BettingPros event's game (21 rows); closing lean walk-forward.
| | v1 | v1s |
|---|---|---|
| Information test | +0.212 [+0.182, +0.243] | +0.202 [+0.171, +0.232] |
| 2023-24 / 2024-25 / 2025-26 | +77.5u / +73.3u / +128.5u | +66.8u / +65.9u / +127.2u |
| Pooled TEST | 1,989 bets, +279.3u, ROI +14.0% [+11.1, +17.2] | 1,813 bets, +259.9u, +14.3% |
| Lean-adjusted closing-line EV | **−0.07%** [−0.46, +0.34] | −0.10% |
| DK/FD openers only | 755 bets, +83.0u, +11.0% | 682, +74.8u, +11.0% |
| Checks | 1 PASS, 2 PASS, **3 fail**, 4 PASS | same |

## Decision (Claude, Nov 6)
Nothing goes live on its own: Fable did not pass it, and the corrected closing-line check fails. Status: **LEAD**. The money result is strong
and holds after the fixes, so the choice is Jeffrey's: start a **PROVISIONAL** record at **FanDuel O/U openers** (the only Connecticut book
with NCAAM under props; DK has only over-only "X+" ladders), or keep logging the live bets on paper first. Before either goes live:
the live job needs the matching fixes, and Fable has to review the live code.
Next model work: v2 with a minutes prior that fades (fixes the under-projection) plus inferred absences, pre-registered on the same seasons
with the walk-forward lean written in from the start.
