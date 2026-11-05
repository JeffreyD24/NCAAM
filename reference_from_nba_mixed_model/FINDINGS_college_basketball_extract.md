# College basketball entries from nba-mixed-model/analysis/FINDINGS.md (master log), extracted Nov 5, 2026

Entries about NCAAM are copied whole. Entries about all sports that mention college basketball are cut down to the lines that mention it; the full entry is in the master log.

## 2026-11-05: NCAAM box score backfill complete, 2007-08 to 2026-27 (NCAAM) [TEST]
- Question: did the ESPN box score backfill (ncaab-box.yml, run 42100153853) land every season, so lineup, inferred-injury and travel models can be built?
- Data / method: `ncaab/espn_boxscores.py` output in `ncaab/data/box/` (players: starter, minutes, points; teams: shooting/turnover totals, city, state, venue, attendance), compared with `ncaab/data/all_games.csv`.
- Result: all 20 seasons present (20/20 jobs succeeded). Player box on 99-100% of games every season except 2011-12 (89%) and 2012-13 (87%); team box (with venue city/state for travel) on 100%. Minutes filled on 100% of player rows. Per-season counts in `ncaab/box_coverage_output.txt`.
- Read: inputs are in place for the playbook step 2 models (lineups/minutes, injuries inferred from minutes dropping to 0, travel from venue location and rest). 2012-13 also has few closing lines (922), so it is a weak test season.
- Decision: nothing changes; next build is the lineup / inferred-injury / travel model on top of the market base model, pre-registered first.
- Files: ncaab/data/box/, ncaab/box_coverage_output.txt.

## 2026-11-05: Polymarket and Kalshi history: where it is and what we can get (all sports) [TEST] [LEAD] [DECISION]
*(excerpt: only the lines that mention college basketball)*
- Result: Polymarket data-api v2 `/v2/trades?condition=<id>&taker_only=false` returns every fill with wallet, side, size, price, time (both sides of each fill), paged by `pagination.next_cursor`; market-scoped history reaches back about 3 years (2022 college tournament markets return 0 fills). Listings: NBA 2025-26 = series 10345, NHL 10346, NCAAM 10470, NFL 2025 = 10187 (separate "nfl-2025" listing; 12185 is NFL 2026 from preseason), CFB 12756. One NFL game is about 5,000 fills. Kalshi: settled markets before a moving cutoff move to `/historical/*`; candles, trades with sizes (no identities) are free. Free bulk sets: Hugging Face SII-WANGZJ/Polymarket_data (every Polymarket fill with wallets Nov 2022-Oct 4 2026, 37 GB, query remotely) and jon-becker/prediction-market-analysis (Kalshi trades, 36 GB). Old Polymarket subgraphs are unreliable since the Apr 28, 2026 contract change; data-api v1 retired Oct 24, 2026.
- Read: wallet-level Polymarket history for the full 2025-26 NBA/NHL/NCAAM seasons and the 2025 NFL season is available for free, enough for an honest rank-then-follow test. Kalshi's Developer Agreement (sec. 3.1) only allows storing data for your own Kalshi trading and bars sharing it, so Kalshi data must not sit in a public repo.

## 2026-11-05: Sweep of tracked-but-not-bet ideas for PROVISIONAL promotion (all sports) [TEST] [LEAD] [CORRELATION]
*(excerpt: only the lines that mention college basketball)*
- Data / method: inventory of all three repos + ncaab; NHL rest check recomputed from nhl-mixed-model research/stats_catalog/nhl_games.csv

## 2026-11-05: Kalshi and Polymarket history: how far back, with sizes and wallets (all sports) [TEST] [DECISION]
*(excerpt: only the lines that mention college basketball)*
  NHL 1,847 (Apr 19, 2025), NFL 502 (Aug 7, 2025), NCAAM 5,445 (Dec 1, 2025), college football 2,095 (Aug 23, 2025), NBA spreads 1,512 and
  markets from Oct 2025 for NBA (series 10345), NHL (10346), NCAAM (10470); an older NCAA series (39) has March Madness games from 2022;

## 2026-11-05: Paid Pinnacle feed stopped (credits ran out); Pinnacle API status; what Kalshi / Polymarket history holds (all sports) [OBSERVATION] [TEST] [LEAD]
*(excerpt: only the lines that mention college basketball)*
  reached back to Sep 2026 (NHL), Oct 2026 (college football), Nov 2026 (NCAAM); older history not yet found (may need its historical endpoint).

## 2026-11-05: Free replacements for the paid Pinnacle feed; Polymarket wallet data confirmed (all sports) [TEST] [DECISION] [IDEA]
*(excerpt: only the lines that mention college basketball)*
  books; no Pinnacle or Circa anywhere on Action Network. (2) Kalshi public API (no key): game markets for NBA, NHL, NFL, NCAAM, NCAAF and NBA

## 2026-11-05: Sharp money: where it goes, does it beat the close, and does it disagree with our models (all sports) [TEST] [CORRELATION] [LEAD] [DECISION]
*(excerpt: only the lines that mention college basketball)*
  49.7%, -9.8u (vs 55.8-57.1% otherwise); NCAAM spreads ENS with sharps agreeing 89 bets 60.5%.

## 2026-11-05: Can a results-only model ever beat the closing line's accuracy? (NCAAM, all sports) [OBSERVATION] [DECISION]
- Question (Jeffrey): if we keep building models with new weights, will we get more accurate than DraftKings at the close?
- Evidence: 10+ NCAAM model variants (Model 1, M2, M4, M8, M10, MKT, ENS, stacks) across 2007-26: the closing line is the most accurate
  predictor in every season. TEST 2025-26 spread RMSE: best model ENS 11.47, DK opener 11.27, DK close 11.22 (totals 17.24 / 17.18 / 16.96).
- Read: a model built only from past scores uses a subset of the information already in the close (scores, form) and lacks the rest
  (injury and lineup news, sharp money). Better weights approach the close, never pass it. Both errors are mostly irreducible game noise
  (~11 pts on a college spread), so the real gap is small and the target is the "excess error" above that noise.
- Decision (Jeffrey + Claude): (1) build the best possible base model, which must include the market (our ratings blended with opener /
  Pinnacle / line movement); (2) add information the close lacks or gets late: player lineups and minutes (from ESPN box scores), inferred
  injuries (college has no official reports: absences show in minutes), travel and rest; (3) measure every step on accuracy vs the close
  and the beat-the-close slope. Box score backfill 2007-27 started (`ncaab/espn_boxscores.py`, workflow `ncaab-box.yml`).
- [IDEA] Inferred injuries: a player whose minutes drop to 0 without news is information books react to late; test once the box data lands.
