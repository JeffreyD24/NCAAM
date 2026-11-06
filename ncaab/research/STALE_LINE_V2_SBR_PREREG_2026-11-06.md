# NCAAM stale-line v1 vs v2 on the SportsbookReview seasons 2013-14 to 2020-21: pre-registration (Nov 6, 2026)

Written and pushed **before grading** (git history is the proof). Jeffrey, Nov 6, 2026 (10:18): "do both" (keep v1 live, v2 on paper; test v1 vs v2 on older seasons).
Handoff: betting-goals `handoffs/2026-11-06/1020_ncaam-stale-line-v2-paper-and-sbr-test.md`, Task 2. RULE 2: the DraftKings seasons (2023-24, 2025-26) are used up
(graded many times); 2013-14 to 2020-21 have SBR openers and closes and were never used to compare v1 and v2 for betting.
Playbook steps covered: 2 (lineups, injuries, travel, roster layers) and 3 (CLV against the close).

## Arms (same specification as the live code; refit per season here)
Data: `ncaab/data/model3_preds.csv` (M2_m, M8_m, MKTL_m), `derived/lineup_travel_features.csv.gz`, `derived/roster_features.csv.gz` (all unchanged).
- **v1 (S0, live):** close margin ~ const + M2 + M8 + MKTL + opener margin (OLS).
- **v2 (S1, paper):** v1 + 8 lineup/injury/travel + 4 roster features (R1-R4), each home minus away, missing difference = 0.
- Built exactly as `ncaab/stale_line_layers_grade.py` (same X matrices, same `stack()`): expanding window, each season s fitted on all seasons before s
  (SBR opener/close, |open - close| < 6, both teams 3+ games, no "OTHER" team), minimum 2,000 training rows. The coefficients are refit for every
  test season from earlier seasons only; they are NOT the live `live_blendc_v2.json` numbers (those were fitted on later seasons).
- Edge e = predicted close margin - SBR opener margin.

## Test rows
- Seasons **2014-2021** (2013-14 ... 2020-21; 8 seasons). **2013 (2012-13) reported separately** (only 462 SBR openers that season and weaker box-score coverage;
  decides nothing).
- Prices: SBR opener (`open_sp`) and SBR close (`close_sp`).
- Guards: both present; |open - close| < 6; drop rows where open and close have opposite signs with both |x| >= 3; both teams 3+ games; no "OTHER" team;
  back-to-backs included; final score known; both arms' predictions defined.
- **Data-forced change from the handoff design:** `stale_line_layers_grade.py`'s `flip` and `|book_sp - close_sp| <= 10` guards use DraftKings' `book_sp`, which is
  empty before 2024 (they would drop every SBR row). They are replaced by the SBR guards above, as the handoff specifies. New script:
  `ncaab/stale_line_v2_sbr_grade.py` (same model code, new row filter and grading).

## Bets
- v1: |e1| >= **0.5** (live rule). v2: |e2| >= **0.62 fixed** (the live paper threshold, chosen on DraftKings seasons, not tuned here). Side = sign(edge).
- Units at -110 at the SBR opener (push = 0). CLV = SBR close - SBR opener in the bet's direction.

## Measures (per arm, pooled 2014-2021 and per season)
Bets, hit rate, units, CLV. D = CLV(v2) - CLV(v1) with a 90% bootstrap interval (resample games within season, 5,000 draws, seed 7; both bet sets rebuilt from
the same resampled games); same bootstrap for the units difference.

## PASS (all three needed)
- **P1** D > 0 and its 90% low end > 0.
- **P2** units(v2) >= units(v1), pooled 2014-2021.
- **P3** v2's CLV higher than v1's in at least 5 of the 8 seasons.

**PASS -> v2 becomes a candidate to replace v1 live (Fable review + Jeffrey's go first; the paper record keeps running either way).
FAIL -> v2 stays paper only.** Run once; output `ncaab/research/stale_line_v2_sbr_output.txt`, every bet `ncaab/research/stale_line_v2_sbr_bets.csv`,
write-up `ncaab/research/STALE_LINE_V2_SBR_RESULTS_2026-11-06.md`.

## Caveats (stated now)
- SBR openers were not bettable at scale (posting times and limits unknown): this compares the two models, it does not measure real profit.
- These seasons were used, leave-one-season-out, in the close-model layer test (CLOSE_MODEL_LAYER_PREREG_2026-11-05: predicting the close). That test knew
  the layers help predict the close; it never compared v1 and v2 bets. So P1 (CLV) is partly expected from that result; P2 and P3 are the harder parts.
- v2's 0.62 threshold was chosen to match v1's bet count on DraftKings, where edges are scaled to DK openers; on SBR openers the two arms' bet counts may differ.
  Both are reported; the criteria use each arm at its live threshold.
- Early SBR seasons (2014, 2015) have fewer openers (about 1,400-1,600 games with both lines).
