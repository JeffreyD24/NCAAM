# NCAAM lineups / inferred injuries / travel layer: results and audit (Nov 5, 2026)

Pre-registration `LINEUP_INJURY_TRAVEL_PREREG_2026-11-05.md` (pushed 97a3c55, before any feature was built). Features `ncaab/lineup_travel_features.py`
(saved `derived/lineup_travel_features.csv.gz`), grading `ncaab/lineup_travel_grade.py` -> `lineup_travel_grade_output.txt`, audit
`ncaab/lineup_travel_audit.py` -> `lineup_travel_audit_output.txt`. Walk-forward base predictions timing checked: `model.py` refits on `dates < d` only.

## Registered verdict (17 headline seasons, 2008-11 and 2014-26; leave-one-season-out; ridge 10)
| | spreads (n 60,252) | totals (n 60,252) |
|---|---|---|
| P1 layer beat-the-close slope (t, season-clustered) | +0.717 (**+8.64**) pass | +0.654 (+4.42) pass |
| P2 seasons with slope > 0 | 16 / 17 pass (2008: -0.29) | 16 / 17 pass |
| P3 MSE gain of model B over model A (t) | +0.230 (**+3.81**) pass | +0.149 (+1.93) **fail** |
| **Verdict** | **PASS** | **FAIL** |
| RMSE vs result: close / A (base gap only) / B (full) | 11.014 / 10.999 / 10.988 | 16.932 / 16.909 / 16.905 |

Groups (need t > 2.5): spreads LINEUP/INJURY P1 +5.95, P3 +3.27 (both clear); spreads TRAVEL/REST P1 +5.18 clears, P3 +2.42 does not;
totals LINEUP P1 +2.22 and P3 +0.94 (neither); totals TRAVEL P1 +4.24 clears, P3 +1.67 does not. Group results are `[LEAD]` at most.
Forward design (train on earlier seasons only, 2016-26): spreads layer slope +0.825 (t +8.77), 11/11 seasons positive, MSE gain +0.295 (t +5.11);
totals slope +0.430 (t +3.70), 10/11, MSE gain +0.033 (t +0.27).
Weak seasons (fit on headline seasons, not pooled, one season so no clustered t): 2012 spreads slope +0.753 (n 2,660), 2013 +1.303 (n 704);
totals 2012 -1.017, 2013 +0.510.

## What the audit says (read before believing the PASS)
1. **The layer's signal is not a pipeline artifact.** Shuffling each season's feature rows across games: layer slope +0.09 / +0.33 / +0.16 (t +0.28 / +1.30 / +0.71),
   MSE gain negative. The real features carry a small, consistent link to (actual margin - close).
2. **But it is small.** Single-feature correlations with the excess are -0.027 (lost minutes share), -0.029 (lost points share), -0.014 (new starters),
   -0.013 (back-to-back), -0.007 to -0.009 (travel, time zones, rest); the layer's added RMSE gain over the base-gap model is about 0.011 points.
3. **It is not lineup-specific.** The oracle (who actually played in that game, not tradable) gives the same spread slope (+0.742, t +7.70) as the
   pre-game lineup features (+0.736), and travel/rest alone gives +0.695. So the mechanism is not shown to be "the market misses absences".
   (Oracle does help totals: slope +0.881, P3 t +3.78, vs +0.671 / +0.94 pre-game.) Status: `[CORRELATION]`, not `[CAUSAL]`.
4. **The 54.1% hit / +374u when betting the full model at the close is mostly the base gap, not the layer.** In the placebo (no real layer) the same bets
   still hit 53.5-53.8% for +150 to +191u. Base-gap-only bets (|pred| >= 0.9): 8,824 bets, 53.5% (SBR closes 53.7%, DraftKings closes 2024-26 53.0% on 2,514,
   consensus 2022-23 53.7%), break-even 52.4%. The blend of M2/M8/MKT minus the close predicts the excess with slope +0.27 (corr +0.065; DK-close seasons +0.035).
   This conflicts with the standing finding that models only make money at the opener, so it is a `[LEAD]` that needs its own pre-registration and a bettable
   price. SBR closes before 2023 are not claimed bettable.
5. **Data:** closes are well calibrated (mean excess +0.04, sd 11.01). Strong sign disagreement between the close and our model (|close| >= 7 and |M2| >= 7, opposite
   signs): 118 games, **87 of them in season 2020** (mean excess +10.8): probable bad quotes; a flipped-sign guard belongs in any v2 pre-registration (the
   registered |open - close| < 6 guard does not catch them).

## Decision
Nothing goes live and no bet is placed or recommended. Per the pre-registration a spread PASS makes the layer a PROVISIONAL *candidate* only after a second
pre-registration that grades CLV against DraftKings' / FanDuel's own opener and a Fable review. Claude made no other decision; Jeffrey to approve the next step.

## Notes on how it was run (no registered definition changed)
- Code bugs fixed, definitions untouched: (1) per-season slope asked for a clustered SE with one cluster (crashed before any result printed); (2) the weak-season
  block hit the same crash after the primary results printed, fixed and re-run to completion (numbers unchanged, deterministic). Audit script fixes: column-name clash.
- Prereg ambiguities fixed in code: "average minutes" = total minutes over the last <= 10 box games / number of those games (misses count 0); P1 judged on the
  layer part (gamma . features) of the held-out prediction (full-model slope also shown: spreads +0.884, t +3.82; totals +0.799, t +3.13); the gap term is
  penalized like the other regressors in the ridge.
- Venue coordinates known for 97.4% of games (rest are blank-city games with a neutral site, or foreign venues, travel missing there).
