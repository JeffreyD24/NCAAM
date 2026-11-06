# NCAAM open leads and ideas (checkbox list; every item also has a one-line entry in betting-goals/FINDINGS.md)

Opened Nov 5, 2026 (first entries from the lineup/injury/travel layer). Test on past seasons, never "wait for this season" (RULE 2).

- [x] **Layer vs a bettable price (second pre-registration): DONE Nov 5, FAIL on Q4** (`research/LINEUP_INJURY_TRAVEL_OPENER_RESULTS_2026-11-05.md`):
      151 bets at DK opener, CLV +1.49 [90% +1.17], +9.5u, layer beat-the-opener t +3.89, but mean CLV below the base-only model (1.85 on 60 bets).
- [x] **Layer as a bet-timing tool: DONE Nov 5, registered PASS but immaterial** (`research/LINEUP_INJURY_TRAVEL_V3_TIMING_RESULTS_2026-11-05.md`): waited on
      11 of 2,483 base bets (+11 points, +3.8u). Fable review of a "wait" flag only if Jeffrey wants it (Claude: not worth it).
- [x] **v3 matched B-vs-A comparison: DONE Nov 5, FAIL** (same file): at equal bet counts B's CLV = A's (D +0.01 at 2%). Layer dropped as a stand-alone bet signal.
- [x] **Layer in the close model: DONE Nov 5, PASS spreads and totals** (`research/CLOSE_MODEL_LAYER_RESULTS_2026-11-05.md`); C3L is the research close model.
- [x] **Base edge >= 2.8 at DK's opener: pre-registered, Fable APPROVE WITH CHANGES, NOT started** (Nov 5, 19:45): 54 of its 85 bets duplicate the live stale-line
      rule; its 31 own bets -0.5u. Status note in `research/BASE_EDGE_DK_CANDIDATE_PREREG_2026-11-05.md`. Jeffrey decides.
- [x] **Early-season roster layer: DONE Nov 5, FAIL** (`research/ROSTER_CONTINUITY_RESULTS_2026-11-05.md`): vs the close slope t +2.37, 12/16 seasons, but MSE gain
      t +1.80 (< 2). At DK's opener CLV +1.67 vs +1.31 (base) at matched counts; predicts DK's line move t +8.25.
- [x] **Both layers in the stale-line rule's BLEND-C: DONE Nov 5, FAIL by a hair** (`research/STALE_LINE_LAYERS_RESULTS_2026-11-05.md`): same 642 bets, CLV +1.38 vs
      +1.29 (D +0.09, 90% [-0.008, +0.216]), +70.5u vs +65.5u, better close RMSE. Live rule unchanged.
- [x] **Stale-line v1 vs v2 on SBR 2014-2021 (never used for this comparison): DONE Nov 6, PASS** (`research/STALE_LINE_V2_SBR_RESULTS_2026-11-06.md`):
      v2 at 0.62: 1,520 bets +251.1u CLV +0.640 vs v1 1,596 bets +189.6u CLV +0.559; D +0.082 [90% +0.022, +0.141]; v2 CLV higher 6 of 8 seasons. SBR openers not bettable.
- [ ] **[LEAD] v2 replaces v1 live?** Candidate after the SBR PASS. Next: Fable review of the swap + Jeffrey's go. Paper record keeps running either way.
- [~] **Paper shadow of stale-line v2 (S1)**: Jeffrey Nov 6, 10:18: v1 live, v2 paper (`live_paper_v2.csv`, nba-mixed-model branch `ncaam-stale-line-v2`).
- [ ] **[LEAD] Stake more when the base edge and the stale-line rule agree** (54 overlap bets: 66.0%, +13.8u, CLV +2.26; candidate-only 31 bets -0.5u). Stake-sizing
      pre-registration; in-sample so far.
- [ ] **[IDEA] College sharp money** (playbook step 2, last bullet): `sharp/data/ncaab_splits.csv.gz` already has Action Network ticket % vs money % for about
      5,000-5,600 games a season 2019-20 to 2025-26 (DK lines alongside 2024-26). Test: does money % minus ticket % predict DK's opener-to-close move and the result
      beyond C3L and the base gap? Check first when the splits were captured (a near-close snapshot can't be used at the opener).
- [ ] (history) **[LEAD] Base model alone at DK's opener, |pred| >= ~2.8 (top 1%):** DK 2023-24 + 2025-26: 85 bets, 60.7%, +13.4u (2024 +14.4, 2026 -1.0), CLV +1.78;
      ESPN BET 2024-25 top 2%: 86 bets +13.3u, CLV +1.74; SBR 2008-21 leave-one-season-out at k 3: 362 bets, +56.5u, CLV +0.47 (SBR openers, not bettable).
      Units alone are within luck (z 1.5, luck sd 8.7u); CLV is the strong part. Jeffrey asked (Nov 5, 18:52) why not use it. Next step if he wants it: pre-register
      it as a fixed rule (threshold in points, written now), Fable review, then a PROVISIONAL record of its own.
- [ ] **[LEAD] Base gap beats the close.** Blend(M2, M8, MKT) minus the close predicts actual - close (slope +0.27, corr +0.065; DK closes 2024-26 +0.035);
      gap-only bets at the close hit 53.5% (break-even 52.4%). Contradicts "only the opener makes money". Pre-register a forward test (fit on earlier seasons)
      with CLV vs the bettable opener; check what the gap is (line shading? stale SBR snapshot time?).
- [ ] **[IDEA] Why is the layer not lineup-specific?** Oracle absences = pre-game absences on spreads; travel/rest alone nearly as strong. Test a single
      "disruption" score, refit with one of the collinear lost-minutes / lost-points features, and check coefficients by season.
- [ ] **[LEAD] Totals: travel/rest slope t +4.24 but no MSE gain (t +1.67)**; oracle absences help totals (t +3.78). Possible follow-up: oracle-like
      pre-game signals (starters announced, minutes ramp) for totals.
- [ ] **[IDEA] Bad-quote screen for 2020 (87 strong close-vs-model sign disagreements)**: list them, compare to the opener and ESPN, fix or drop.
- [ ] **[IDEA] Box-score gaps 2011-12 (89%) and 2012-13 (87%)**: re-pull the missing events; 2012-13 also has only 922 closes, so low value.
- [ ] **[IDEA] derived.py**: copy the restore/save helper from nhl-mixed-model into this repo (derived/MANIFEST.md exists, plain tracked gzips for now).
