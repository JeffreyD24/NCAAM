# NCAAM stale-line rule + both layers in BLEND-C: results (Nov 5, 2026)

Pre-registration `STALE_LINE_LAYERS_PREREG_2026-11-05.md` (pushed 68dfdd4 before grading). Code `ncaab/stale_line_layers_grade.py`, output
`research/stale_line_layers_output.txt`, every bet `research/stale_line_layers_bets.csv`. Run once. DK 2023-24 + 2025-26 have been graded many times: weaker evidence.

**Sanity check passed:** S0 (the live rule, refit the same way) reproduces the stale-line backtest exactly: 642 bets, 57.8%, +65.5u, CLV +1.29.

## Verdict: FAIL (P1 misses by 0.008)
| DraftKings 2023-24 + 2025-26 (9,156 games) | S0 live rule (abs(e) >= 0.5) | S1 with layers, same count |
|---|---|---|
| Bets / hit | 642 / 57.8% | 642 / 58.2% |
| Units (2024, 2026) | +65.5u (+34.4, +31.2) | **+70.5u** (+33.5, +36.9) |
| CLV | +1.292 | **+1.382** |
| RMSE of predicted DK close (opener alone 1.547) | 1.481 | **1.461** |
| Overlap | 321 of 642 bets in common | |

- **P1** D = CLV(S1) - CLV(S0) = **+0.090, 90% interval [-0.008, +0.216]** -> fail (low end not above 0).
- **P2** units +70.5 >= +65.5 -> pass. **P3** better close prediction -> pass. **P4** non-back-to-backs D +0.097 -> pass (575 bets each: CLV +1.43 vs +1.33; units +51.5 vs +52.4).
- Diagnostic: S1 at its own abs(e) >= 0.5 threshold bets 1,211 games, 55.9%, +79.4u, CLV +1.14 (more bets, lower line value per bet).
- ESPN BET 2024-25 (secondary): same 339 bets count, CLV +1.14 vs +0.88, units equal (+23.7u).

## Read
Every measure moves the right way: better close prediction, more line value per bet, slightly more units, on both DraftKings seasons and at ESPN BET. But the
line-value gain (+0.09 points per bet) is small next to its uncertainty on 642 bets, and the pre-registered bar (90% low end > 0) is not met. The layers swap
about half the bets for different ones of similar or slightly better quality. Consistent, small, unproven.

## Decision
The live stale-line rule stays as it is (pre-registered consequence of a FAIL). No re-run with changed definitions.
Option for Jeffrey (not a test, per RULE 2): log S1's picks next to the live rule's as a paper shadow record in 2026-27 at no stake, so the comparison keeps building.
