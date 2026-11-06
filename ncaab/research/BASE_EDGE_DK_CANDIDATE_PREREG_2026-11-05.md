# NCAAM candidate rule: base model's edge >= 2.8 points at DraftKings' opening spread. Pre-registration (Nov 5, 2026)

Written and pushed **before any live tracking and before the Fable review**. Jeffrey, Nov 5, 2026 (19:25): lock the rule as a fixed threshold, pre-register it,
get a Fable review, and track it on its own PROVISIONAL record. Playbook: step 1 (base model including the market) scored by step 3 (CLV from a line we can
bet, units at the opener). System: sportsbooks (DraftKings).

## The rule (every number frozen here; never re-fitted for this record)
For a D-I NCAAM game with a DraftKings opening spread S (home spread, negative = home favored):
1. Ratings: M2_m, M8_m, MKT_m = predicted home margin from the three walk-forward rating models (`ncaab/three_targets_preds.py` definitions: M2 moving scoring level;
   M8 conference hierarchy, ridge 10/10; MKT the same ridge model fitted to past games' closing lines). Each uses only games finished before the game day.
2. Blend = -0.7038 + 0.4941 x M2_m + 0.2131 x M8_m + 0.3858 x MKT_m (fitted on SBR 2008-11 and 2014-21; v2 model A).
3. Gap = Blend + S (our predicted home margin minus the margin DraftKings' opener implies).
4. Predicted edge = 0.0226 + 0.4326 x Gap (model A's ridge fit, same seasons).
5. **Bet the home side if edge >= +2.8 (Gap >= +6.42); bet the away side if edge <= -2.8 (Gap <= -6.53).** Spread only, at DraftKings' price when the alert fires.
Filters: both teams D-I with >= 5 earlier games this season; no team mapped to "OTHER"; skip a game if DraftKings' opener and its current line have opposite signs
with |opener| >= 1 (flipped-quote guard), or if a rating is missing.

## Where 2.8 came from (stated plainly)
2.8 is about the top 1% of DraftKings games by |edge| in 2023-24 and 2025-26 (cut-off 2.78 and 2.80). It was read off those seasons after they had been looked
at three times (v1-v3), so **the threshold is in-sample**. The training rule in v2 (fixed before those seasons were graded) gave k = 3.0. Both are reported below.

## Evidence so far (none of it a clean holdout)
| Source | Bets | CLV (break-even 0.67) | Units | Note |
|---|---|---|---|---|
| DK 2023-24 + 2025-26, edge top 1% (~2.8) | 85 | +1.78 (2024 +1.64, 2026 +1.91) | +13.4 (2024 +14.4, 2026 -1.0) | threshold chosen here |
| DK 2023-24 + 2025-26, edge >= 3.0 (v2 pre-registered k) | 60 | +1.85 [90% +1.39] | +7.8 | |
| ESPN BET 2024-25, top 2% | 86 | +1.74 | +13.3 | not offered in Connecticut |
| SBR 2008-21, leave-one-season-out, edge >= 3.0 | 362 | +0.47 | +56.5 | SBR openers, not bettable |
Luck alone on 85 bets: sd about 8.7u; hit rate 60.7% is z +1.53 vs 52.4%. Earlier: Model 1 at DK's opener had CLV +1.26 and flat units (348 bets).

## The PROVISIONAL record (after a Fable review and Jeffrey's go)
- Its own record file (`ncaab/state/base_edge_dk_record.md` + `base_edge_dk_bets.csv`): every alert with time, line and price taken, DK close, result, units, CLV.
  Never merged with the Model 1 TEST record or any other rule; this version is never re-graded under a later rule.
- **Stake 1 unit**, at the DraftKings price at alert time. CLV = line taken vs DK's closing spread, in the bet's direction.
- **Review points (decided now):**
  - Every 50 bets: report CLV with its 90% interval, units, hit rate.
  - **Stop** at 100+ bets if CLV < 0.67 with its 90% upper end < 0.67, or at any point if units <= -15.
  - **Keep and consider raising stakes** only at 200+ bets with CLV >= 0.67 (90% low > 0.3) AND units > 0. Any stake change is a new record and a [DECISION] entry.
- Expected volume: about 40-45 bets a season (85 in two seasons), so the 100-bet review is about 2 seasons away; CLV is the measure that can say something sooner.
- The current season's record is a running check of this rule, not a re-test of it (RULE 2); this pre-registration is the test design.

## AMENDMENT after the Fable review (Nov 5, 2026, before any tracking; original text above kept, git history c22d58d)
Review: `fable_review_base_edge_2026-11-05/REVIEW.md`, verdict **APPROVE WITH CHANGES**. All eight changes adopted; they replace the conflicting text above:
1. **Line used:** the gap is computed with DraftKings' line **at alert time** (S = current DK spread, normally the opener). Bet only if edge >= 2.8 at that line.
   Log: DK opener, line taken, price, timestamp, gap, edge, M2_m, M8_m, MKT_m.
2. **Back-to-backs are included** (the tests excluded them; including them on the DK seasons: 90 bets, CLV +1.81, +10.3u). Their bets are flagged in the record.
3. **CLV** is graded against DraftKings' own close from ESPN's feed; any fallback close is flagged and reported separately.
4. **Price guard:** only bet at -115 or better; a qualifying game at a worse price is recorded as a non-bet with its CLV.
5. **Stop rules (replace the ones above):** at 50 bets stop if CLV's 90% upper end < 0.67; at 100 bets stop if CLV < 0.67; stop any time units <= -15.
   Keep rule unchanged: 200+ bets, CLV >= 0.67 (90% low > 0.3) and units > 0 before any stake increase.
6. **Unit:** 1 unit = Jeffrey's flat NCAAM stake, at most DraftKings' NCAAM opener limit. Account risk noted: opener bets on large mismatches look like sharp play
   and may get the account limited; that cost is part of judging the rule.
7. **Expectation written in advance:** a 2.8-pt edge has been worth about 1.1 pts of result (beat-the-opener slope 0.40), about **+3-4% ROI**; over 100 bets that
   is about +3u with luck of about +/-10u. A flat first 100 bets is the expected outcome, not a failure; CLV decides.
8. **Each 50-bet review** also reports CLV split by home/away side, Nov-Dec vs Jan-Mar, and |opener| > 10 vs <= 10.
Threshold note: the review found k 3.0 (fixed before grading) the cleanest; 2.8 stays as Jeffrey chose, and the record also reports how the 3.0+ subset does.

## STATUS Nov 5, 2026 (19:45): NOT started. It overlaps the live stale-line rule (Claude's recommendation; Jeffrey decides)
Before wiring alerts, Claude found that the live PROVISIONAL **stale-line spreads rule** (nba-mixed-model `ncaab/research/MODEL3_RESULTS_2026-11-05.md`,
`ncaab/live_alert.py`; DK 2023-26 backtest 623 bets 57.9% +65.5u CLV +1.27) already bets DraftKings' opener from the same three ratings (M2, M8, lagged market model).
Check `ncaab/base_edge_vs_stale_overlap.py` -> `research/base_edge_vs_stale_overlap_output.txt` (DK 2023-24 + 2025-26, candidate top 1%):
- **54 of 85 candidate bets are also stale-line bets on the same side:** 66.0%, +13.8u, CLV +2.26.
- **The 31 candidate-only bets:** 51.6%, -0.5u, CLV +0.94 (2024 +5.1u, 2026 -5.5u).
So the candidate adds almost nothing on its own; live, it would mostly double the stake on stale-line bets. Not started as a separate record.
[LEAD] "Stake more when the base edge and the stale-line rule agree" (the 54 overlap bets) is a stake-sizing idea that needs its own pre-registration.
Correction: the section below says live M8 and market ratings do not exist; they do (`nba-mixed-model/ncaab/live_ratings.py`: M2, M8 and a one-day-lagged market
model, MKTL, for the stale-line rule). The candidate was tested with the unlagged MKT; a live version would use MKTL.

## What has to exist before the first alert (implementation, after review)
The live NCAAM jobs (`nba-mixed-model/ncaab/`) produce Model 1 and M2 daily; **M8 and MKT live ratings do not exist yet.** They must be built from the same code
(`model2_tournament.py` walk with the M8 settings; MKT on past closes) and checked against `three_targets_preds.csv` on 2025-26 (same numbers to 0.01) before
the record starts. Alerts follow RULE 5 (sent at any hour).
