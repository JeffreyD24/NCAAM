# NCAAM open leads and ideas (checkbox list; every item also has a one-line entry in betting-goals/FINDINGS.md)

Opened Nov 5, 2026 (first entries from the lineup/injury/travel layer). Test on past seasons, never "wait for this season" (RULE 2).

- [ ] **[LEAD] Layer vs a bettable price (second pre-registration).** The spread layer PASSED the registered close test
      (`research/LINEUP_INJURY_TRAVEL_RESULTS_2026-11-05.md`). Grade CLV and units at DraftKings' / FanDuel's own opener (DK openers exist 2023-24 and
      2025-26; ESPN BET 2024-25 secondary), flipped-sign guard added, features unchanged. Needs Fable review before anything goes PROVISIONAL.
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
