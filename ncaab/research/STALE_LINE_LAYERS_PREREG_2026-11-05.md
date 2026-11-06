# NCAAM stale-line rule: does adding both layers to its close prediction (BLEND-C) pick better bets? Pre-registration (Nov 5, 2026)

Written and pushed **before grading**. Jeffrey, Nov 5, 2026 (19:47): go ahead.
Why: the lineup/injury/travel layer and the early-season roster layer both predict DraftKings' opener-to-close move (t +7.85, t +8.25) but neither picks better bets
on its own. The live PROVISIONAL stale-line rule (nba-mixed-model `ncaab/research/MODEL3_RESULTS_2026-11-05.md`, `ncaab/live_alert.py`) bets exactly that move:
DraftKings' opener when BLEND-C's predicted close is 0.5+ pts away. Playbook steps 2 (lineups, injuries, travel, roster) and 3 (CLV from a bettable line).
**Seen-data warning:** DK 2023-24 and 2025-26 have been graded many times (stale-line rule itself, layers v1-v3, roster, base edge). A pass here is weaker evidence.

## Two arms, built identically (spreads only)
Data: `ncaab/data/model3_preds.csv` (M2_m, M8_m, MKTL_m = the one-day-lagged market model the live rule uses), features `derived/lineup_travel_features.csv.gz`
and `derived/roster_features.csv.gz` (both unchanged).
- **S0 (current rule):** close margin ~ const + M2 + M8 + MKTL + opener margin (OLS), exactly as `model3_grade_mktl.py`.
- **S1 (with layers):** S0 + the 8 lineup/injury/travel features and the 4 roster features R1-R4, each as home minus away (OLS).
  Missing feature differences are set to 0 (no known absence, no roster adjustment, travel unknown), so S1 is defined wherever S0 is.
- **Fitting, as the live rule:** for each season s, fit on all seasons before s (SBR opener/close <= 2021 with |open - close| < 6; book's own opener and close from 2024;
  2022-23 not used), rows with both teams 3+ games and no "OTHER" team. Predict season s.
- Edge e = predicted close margin - opener margin (book's own opener).

## Test rows
DraftKings' own openers, 2024 (2023-24) and 2026 (2025-26); both teams 3+ games; no "OTHER" team; flipped quotes dropped (opposite sign to DK close and to the
Action Network open with |opener| >= 1); |opener - close| <= 10. Back-to-backs included (as the live rule). ESPN BET 2025 secondary (decides nothing).

## Bets
- S0 bets the live rule: |e0| >= 0.5, side = sign(e0). Let N_s = its bet count in season s.
- S1 bets its top N_s games by |e1| in season s (matched counts; ties kept). Diagnostic only: S1 at its own |e1| >= 0.5.
- -110 stakes; CLV = DK close vs DK opener in the bet's direction (break-even 0.63 per the stale-line rule; 0.67 per the book-opener test; both shown).

## Measures and PASS (all needed)
- **P1** D = CLV(S1) - CLV(S0) > 0 with its 90% interval low end > 0 (joint bootstrap: resample games within season, rebuild both bet sets; 5,000 draws, seed 7).
- **P2** units(S1) >= units(S0) at matched counts.
- **P3** S1 predicts DK's close better than S0 on all test rows (RMSE of predicted close vs actual DK close).
- **P4** D > 0 also on the non-back-to-back games alone (point estimate).
Sanity check (not a criterion): S0 should reproduce the stale-line backtest's DraftKings numbers (MODEL3 output, lagged market model) closely.
**PASS -> S1 is a candidate stale-line v2: new record, Fable review and Jeffrey's go before any live change. FAIL -> recorded; the live rule stays as it is.**
