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

## What has to exist before the first alert (implementation, after review)
The live NCAAM jobs (`nba-mixed-model/ncaab/`) produce Model 1 and M2 daily; **M8 and MKT live ratings do not exist yet.** They must be built from the same code
(`model2_tournament.py` walk with the M8 settings; MKT on past closes) and checked against `three_targets_preds.csv` on 2025-26 (same numbers to 0.01) before
the record starts. Alerts follow RULE 5 (sent at any hour).
