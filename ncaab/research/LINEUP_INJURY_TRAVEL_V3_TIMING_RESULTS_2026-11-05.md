# NCAAM layer v3 (matched comparison) and bet timing: results (Nov 5, 2026)

Pre-registrations `LINEUP_INJURY_TRAVEL_V3_MATCHED_PREREG_2026-11-05.md` and `LINEUP_INJURY_TRAVEL_TIMING_PREREG_2026-11-05.md` (pushed 6052a78 before grading).
Code `ncaab/lineup_travel_v3_timing_grade.py`, output `research/lineup_travel_v3_timing_output.txt`, bets `research/lineup_travel_v3_bets.csv`, `research/lineup_travel_timing_bets.csv`.
Run once. Same rows and models as v2: DraftKings' own openers 2023-24 + 2025-26 (8,370 games, back-to-backs excluded), fit on SBR 2008-11 and 2014-21.
**Both tests are a third look at these DraftKings seasons**, so they are weaker evidence than a first look.

## v3: base + layer (B) vs base only (A) at the same number of bets: FAIL
| top share of games | A: bets / CLV / units | B: bets / CLV / units | D = CLV(B) - CLV(A) [90%] | overlap |
|---|---|---|---|---|
| 1% | 85 / +1.78 / +13.4 | 85 / +1.69 / +16.3 | -0.08 [-0.39, +0.33] | 53 |
| **2% (primary)** | 169 / +1.41 / +6.7 | 169 / +1.42 / +13.5 | **+0.01 [-0.23, +0.30]** | 94 |
| 5% | 419 / +0.96 / +4.2 | 419 / +1.09 / -1.6 | +0.13 [-0.02, +0.25] | 239 |
| 10% | 838 / +0.79 / +30.2 | 838 / +0.83 / +9.2 | +0.04 [-0.05, +0.14] | 507 |
R1 fails (D at 2% is +0.01, interval spans 0); R2 passes (D > 0 at 3 of 4); R3 passes (B at 2%: CLV +1.42 [90% +1.12], +13.5u, 2024 +10.6, 2026 +2.8). **Verdict FAIL.**
ESPN BET 2024-25 (secondary): at 2%, A 86 bets CLV +1.74 +13.3u; B 86 bets CLV +1.29 +11.4u.

**Read:** at equal bet counts, the layer's picks get the same line value as the base model's picks. The layer does not pick better games at DraftKings' opener.
The base model alone, at its top 1-2% of games, gets about +1.4 to +1.8 points of CLV (well above break-even 0.67) with small positive units. That repeats what the
book-opener test found: real line value at DraftKings' opener, profit not yet shown. Units by cut are noisy (B 2%: +13.5u; B 10%: +9.2u; A 10%: +30.2u).

## Bet timing: PASSES as written, but it barely acts
Base bets = model A with |predicted opener excess| >= 1: **2,483 bets, CLV +0.55 (below break-even 0.67), -20.0u at the opener, -84.6u if always taken at the close.**
Timing rule (t = 0.25, chosen in training): wait for the close when the layer's move model predicts the line moves 0.25+ against us.
- Waited on **11 of 2,483 bets (0.4%)**: +11.0 points gained [90% +4.0, +19.0], +1.0 per waited bet; units -16.2 vs -20.0 always at the opener (+3.8u).
- The base-gap-only move model never waited (0 bets), so T3 passes trivially.
- T1, T2, T3 all pass -> **registered PASS (weaker evidence)**. ESPN BET 2024-25 (secondary): 8 waits, -4.0 points, units unchanged.

**Read:** the base model's picks are the games where the line is expected to move toward us: the median predicted move in the bet's direction is +0.27, and 99.6%
are above -0.25. So "wait" almost never applies. The rule is real on paper (each wait gained about a point) but fires about 5-6 times a season, too rarely to matter.
Waiting in general is costly: the same base bets at the close lose 84.6u instead of 20.0u. **Bet at the opener** is reconfirmed.

## Decision
- Nothing goes live; no bets.
- v3 FAIL: the layer is **not pursued as a stand-alone bet-selection signal** at DraftKings' opener (per the pre-registration).
- Timing PASS makes a "wait" flag a candidate for a Fable review. Claude's recommendation: don't spend the review on it, since it would fire about 5-6 times a season
  for about +2u. Jeffrey decides.
- What the layer did show (v1, v2): its information moves DraftKings' college line between opener and close (t +7.85). Its clearest remaining use is helping predict
  the close itself (the three-target close model), not a bet signal on its own.
