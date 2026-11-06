# Fable live-code review: NCAAM stale-line v2 (Nov 5, 2026)

Reviewed: nba-mixed-model branch `ncaam-stale-line-v2` (layer_features.py, box_daily.py, live_features.py, live_blendc_v2_fit.py, live_alert.py, live_grade.py,
ncaab.yml, alert_loop.sh). Independent Fable agent, read-only. Its check script: `../../stale_line_v2_fixed_threshold_check.py`, output `../stale_line_v2_fixed_threshold_check_output.txt`.

## Verdict: BLOCK as the live decider; APPROVE the same code with roles swapped (v1 live, v2 paper), plus fixes
1. The pre-registration says FAIL -> the live rule stays; the graded result was FAIL (P1 90% low -0.008). Switching overrides that.
2. **The deployed rule (one fixed threshold 0.62) was never graded.** The matched comparison used each season's own cut-off (0.633 in 2023-24, 0.607 in 2025-26),
   which can't be used live. At 0.62: **625 bets, 57.4%, +58.8u (2024 +33.9, 2026 +24.9), CLV +1.42** vs v1 642 bets, 57.8%, +65.5u, CLV +1.29. Better line value,
   fewer units; the units claim (P2) does not hold for the deployable rule. Alert text quoted the matched numbers.
3. v2 puts 133 of 625 bets (21%) on back-to-back games (v1: 67), where CLV is lower (+1.15 vs +1.50) and live lineup features are one game staler than the backtest
   (simulated: 621 of 625 bets unchanged, +55.9u).
Consistency checks passed: feature/coefficient order, home/away and neutral swaps, missing -> 0, string ids (lookups don't silently miss), module identical to research.
Must-fix if v2 goes live anyway: correct the quoted backtest; [DECISION] entry for overriding the FAIL; live_features.py must not write features if all_games.csv is
older than yesterday. Should-fix: tolerate a malformed features file; skip features older than 1 day; stop file must not stop paper logging; empty roster/lineup
results on the first days of a season; catch layer_diffs errors.
