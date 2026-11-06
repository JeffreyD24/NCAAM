# Fable review: NCAAM candidate rule "base edge >= 2.8 at DraftKings' opener" (Nov 5, 2026)

Reviewer: an independent Claude Fable agent (read-only; given the code, data and outputs, not the main session's conclusions). Rule reviewed:
`../BASE_EDGE_DK_CANDIDATE_PREREG_2026-11-05.md` (c22d58d). Reviewer's own check scripts: `chk1.py`, `chk2.py`, `chk3.py` in this folder.

## Verdict: APPROVE WITH CHANGES

## Findings
1. **Leakage: none found.** `run_season` refits on dates strictly before the game day; MKT is fitted only on past games' closes (`three_targets_preds.py`
   lines 13-16); blend weights from SBR 2008-21 only; 0 of 9,915 DK games touch the OTHER mapping. Residual timing: day-d ratings include day d-1 results, which an
   evening-before opener did not have. The tests excluded back-to-backs; the pre-registration omitted that. Including them: 90 bets, CLV +1.81, +10.3u (harmless).
   20 of 85 bets had a close from a non-DK source; with DK's own feed close where present, CLV +1.90 (n 77). Not an artifact.
2. **Constants reproduce exactly:** weights [-0.7038, 0.4941, 0.2131, 0.3858]; edge = 0.02263 + 0.43256 x gap; cut-offs +6.421 / -6.525.
3. **Evidence:** CLV rises steadily with k on the DK seasons (k 1 +0.55; 1.5 +0.75; 2 +0.96; 2.5 +1.41; 2.8 +1.81; 3.5 +2.50), so it does not hinge on picking 2.8;
   k 3.0 (fixed before grading) is the cleanest line: 60 bets, CLV +1.85 [+1.39, +2.33]. Without the top 10 CLV bets: +1.17. 78 of 85 DK openers within 1 pt of the
   Action Network open (no stale/flipped artifact). Break-even 0.67 is right (about 2.4-3.6% win probability per point at sd 11.2). Caveats:
   (a) units are not robust (k 1: -20u on 2,483 bets; 2025-26 at 2.8: -1.0u on 43);
   (b) realized beat-the-opener slope 0.40 (t 3.1): a 2.8-pt edge is worth about 1.1 pts of result, **about +3-4% ROI, not the +13% shown**; model A's RMSE vs the result
   (11.237) is worse than DK's opener (11.224);
   (c) the only season-by-season out-of-sample design (SBR LOSO) gives CLV +0.47 < 0.67;
   (d) 75% of bets are on the home side (home CLV +2.02, away +1.17);
   (e) 62 of 84 bets are in Nov-Dec; 35 have |opener| > 10 (CLV about 2.5 there, low limits).
   **Credible for CLV, weak for profit.**
4. **Required changes** (all adopted in the amendment to the pre-registration):
   1. Gap from DK's line at alert time (current line, not the opener); bet only if edge >= 2.8 there; log opener, line taken, price, time, gap, M2/M8/MKT.
   2. State back-to-back handling. 3. CLV against DK's own close from the feed; flag any fallback close. 4. Price guard: skip or record separately if worse than -115.
   5. Stop: at 50 bets if CLV's 90% upper end < 0.67; at 100 bets if CLV < 0.67; any time at units <= -15. 6. Define 1 unit against DK's NCAAM limit; note account risk.
   7. Write the realistic expectation (+3-4% ROI, flat units likely) into the record. 8. Home/away CLV split at each 50-bet review.
