# NCAAM layer v3: base + layer vs base only at MATCHED bet counts, DraftKings' own opener. Pre-registration (Nov 5, 2026)

Written and pushed **before grading**. Jeffrey, Nov 5, 2026 (18:40): run the fairer v3 comparison, then explore bet timing.
v2 (`LINEUP_INJURY_TRAVEL_OPENER_RESULTS_2026-11-05.md`) failed only Q4: B's mean CLV (+1.49 on 151 bets) was below A's (+1.85 on 60), but the two models
bet different numbers of games, so the averages were not comparable. v3 compares them on the **same number of bets**.

## Honest status of the evidence (stated before grading)
- The DraftKings TEST seasons (2023-24, 2025-26) have now been seen twice (v1 against the close, v2 at the opener). The v2 bets and their CLV are known, including
  that B's bet set at k = 3 captured more total CLV (224.5 vs 111.0 points). **Total CLV at the v2 rule is therefore NOT a v3 criterion** (already seen).
- A v3 PASS is weaker evidence than a first-look pass and is labeled so in every write-up. It can make the layer a candidate for a Fable review, nothing more.

## Unchanged from v2 (no new choices)
Same code path as `ncaab/lineup_travel_opener_grade.py`: features `derived/lineup_travel_features.csv.gz`; models A (base gap) and B (base gap + 8 features) fitted
once on SBR 2008-11 and 2014-21 (ridge 10); the same TEST rows: DraftKings' own openers 2024 + 2026, flipped quotes dropped, back-to-back games excluded, -110,
CLV = DK close vs DK opener in the bet's direction, break-even 0.67. Spreads only. ESPN BET 2025 secondary (decides nothing).

## Matched bet sets (new in v3; fractions fixed now, not tuned)
In each TEST season separately, each model bets its **top q share of games** ranked by |predicted opener excess|, on the side it favors.
**q in {1%, 2%, 5%, 10%}**; **q = 2% is primary** (about 83 bets per season, 167 in all). Ties at the cut-off: keep all tied games.

## Measures per q (both models)
CLV mean and 90% bootstrap interval (5,000 draws, seed 7, game level); units at the DK opener (-110), by season; hit rate.
**Difference D = CLV(B) - CLV(A)** with a 90% interval from a joint bootstrap (resample the TEST games, rebuild both top-q sets, recompute D; 5,000 draws, seed 7).
Diagnostics (decide nothing): overlap of the two bet sets; mean CLV of B-only vs A-only bets; total CLV points.

## PASS (all needed)
- **R1** at q = 2%: D > 0 and D's 90% interval low end > 0 (the layer's picks get more line value per bet, beyond noise).
- **R2** D > 0 at at least 3 of the 4 fractions (not a one-cut result).
- **R3** model B at q = 2% meets v2's Q1 and Q2: CLV >= 0.67 with its 90% low end > 0; units > 0 and no DK season below -5u.
(v2's Q3, the layer's beat-the-opener slope t +3.89, uses identical features and fit and is not re-tested.)
**PASS -> candidate for a Fable review, labeled weaker evidence (third look at these seasons). FAIL -> recorded; the layer is not pursued as a stand-alone bet signal.**
