# NCAAM stale-line v1 vs v2 on SBR seasons 2013-14 to 2020-21: results (Nov 6, 2026)

Pre-registration: `STALE_LINE_V2_SBR_PREREG_2026-11-06.md` (pushed ebe0d60 before the run). Script `ncaab/stale_line_v2_sbr_grade.py`, run once.
Output `stale_line_v2_sbr_output.txt`, every bet `stale_line_v2_sbr_bets.csv`.

## Verdict: PASS (all three criteria)
| | v1 (live, \|e\| >= 0.5) | v2 (paper, \|e\| >= 0.62) |
|---|---|---|
| Bets 2014-2021 | 1,596 | 1,520 |
| Hit rate | 58.7% | 61.2% |
| Units (-110 at SBR opener) | +189.6 | +251.1 |
| CLV vs SBR close | +0.559 | +0.640 |

- **P1** D = CLV(v2) - CLV(v1) = **+0.082**, 90% [+0.022, +0.141] -> PASS.
- **P2** units +251.1 vs +189.6 (difference +61.5, 90% [+3.5, +120.3]) -> PASS.
- **P3** v2's CLV higher in **6 of 8** seasons (lower in 2014 and 2019) -> PASS.
- Predicted-close RMSE (SBR close): opener 1.296, v1 1.271, v2 1.264.

Per season (units v1 / v2; CLV difference): 2014 -1.5 / -4.2 (-0.21); 2015 -6.2 / +16.5 (+0.26); 2016 +14.7 / +10.7 (+0.17); 2017 +28.7 / +18.5 (+0.21);
2018 -7.5 / +25.4 (+0.02); 2019 +19.9 / +32.5 (-0.22); 2020 +139.0 / +136.5 (+0.06); 2021 +2.5 / +15.2 (+0.25).
Overlap: 836 games bet by both, always on the same side.

## Diagnostics (decide nothing)
- Back-to-back games: v1 159 bets CLV +0.311, v2 274 bets CLV +0.650; non-back-to-back v1 +0.586, v2 +0.638. v2 again bets far more back-to-backs (18% vs 10%),
  and here they are its best part. (Live, lineup features for back-to-backs are one game staler than in this backtest; see the Fable review's check C.)
- v2 matched to v1's bet count (cut 0.611): 1,596 bets, +261.1u, CLV +0.630. So the result does not depend on 0.62.
- 2012-13 (separate): v1 75 bets -7.2u CLV +0.087; v2 43 bets +4.8u CLV +0.209.
- Without 2020 (not a criterion): units v1 +50.6, v2 +114.6; v2's CLV higher in 5 of 7.

## Read
- First test of v1 vs v2 for betting on seasons never used for that comparison, at the exact live thresholds. v2 wins on line value (CLV) with an interval above 0,
  on units, and in most seasons. Strongest honest evidence for v2 so far, and consistent with DraftKings (CLV +1.42 vs +1.29, inside noise there).
- Limits: SBR openers were not bettable at scale; hit rates of 58-61% (71% in 2020 for both arms) say SBR openers were softer than any real opener, so the units
  are a model comparison, not profit. The CLV gap (+0.08 points) is small in absolute terms; the DK gap was +0.13. These seasons were used to show the layers
  predict the close (CLOSE_MODEL_LAYER test), so P1 was partly expected; P2 and P3 were not tested anywhere before.
- 2020's 71% hit rate for both arms points again at bad SBR quotes in 2020 (open idea: bad-quote screen for 2020). It inflates both arms about equally.

## Decision
Per the pre-registration: **v2 becomes a candidate to replace v1 live.** Nothing changes live now: it needs a Fable review and Jeffrey's go. v1 stays live and
v2's paper record (nba-mixed-model `ncaab/state/live_paper_v2.csv`, Task 1 of the same handoff) runs either way.
