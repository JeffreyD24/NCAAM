# NCAAM player props v1 — pre-registration (written Nov 5, 2026, ~21:00 ET, BEFORE any prop line was looked at or graded; the backfill workflow had started on GitHub, nothing from it was opened)

Built the same way as the NBA props (nba-mixed-model `research/props/PROPS_V1_PREREG`, `PROPS_V1B_OPENER_CLEAN_PREREG`), with the lessons
from the NBA results applied up front. Only line *coverage* has been looked at (`research/probes/bp_ncaab_probe.md`), no outcome or edge.

## MODEL_PLAYBOOK steps covered
- Step 1 (base model including the market): player model (minutes × per-minute rate × opponent × pace) blended with the opener's own
  no-vig probability; pace comes from the game's opening total and blowout minutes from the opening spread (market numbers as inputs).
- Step 2 (information the market may lack): **v1s** uses the opening spread to cut starters' minutes in expected blowouts, which is much
  bigger in college (spreads of 20-40) than in the NBA. Inferred absences (minutes vanishing; college has no injury reports) are NOT in v1;
  they are the v2 step, pre-registered separately.
- Step 3 (scoreboard): result vs model / opener / close (log loss), model-beyond-the-opener information test, closing-line EV (lean-adjusted),
  units at the opener. System served: sportsbooks (DraftKings / FanDuel). Polymarket has no college player props.

## What the NBA taught (applied here, not re-tested)
1. The money was at the **opener**, not the close (NBA v1b: +5.1% at openers on unseen seasons, ≈0 at the close). So the bet is the opener.
2. Closes lean to overs (~1-1.6 pts of probability every NBA season); closing-line EV is reported lean-adjusted (leave-one-season-out).
3. Cross-book "edges" from last-update data are stale prices: each bet is judged against its **own** book, nothing book-vs-book.
4. The single-dispersion negative binomial mis-sizes points: use the mean-dependent variance (v1b) from the start.

## Data
- Lines: BettingPros NCAAB markets 269 (points) and 270 (second stat), `ncaab/data/props_history/bettingpros/` (`ncaab/props/bettingpros.py`),
  Dec 2021 – Apr 2026: opening line + price + book + time, and each book's last pre-game line (the close).
  **Market 270's stat** is identified before grading by which of reb / ast / fg3m has the smallest mean |line − model mean| on matched rows
  (no outcomes used); the identification is printed first.
- Results and features: ESPN player box scores (`ncaab/data/box/players_full_*.csv.gz`), features `derived/ncaam_props_features.csv.gz`
  (`ncaab/props/features.py`): every feature uses games before the game date only.
- Matching: BettingPros date + normalized player name to ESPN (same date). A name that matches two ESPN players that day is dropped.

## Models (all settings fixed now)
**v1 (NBA v1b port).** Minutes: exponentially weighted mean of this season's minutes (half-life 5 games), last season's minutes per game as a
5-game prior (league minutes per appearance if no last season). Per-minute rate per stat: (recency-weighted stat + 150 × prior rate) /
(recency-weighted minutes + 150), half-life 20 games; prior = last season's rate if 300+ minutes, else the league rate. Opponent factor:
stat allowed per game this season vs last season's league per game, shrunk k = 15 games. Pace (pts, ast, fg3m): the game's opening total
(DraftKings via ESPN, else the archive opener) ÷ the season's mean opening total over earlier games. μ = minutes × rate × opponent × pace.
Distribution: negative binomial with variance = a·μ + b·μ² per stat (Poisson if that is ≤ μ); **a, b fit on 2020-21 + 2021-22 + 2022-23
box scores only** (players with 3+ prior games), no prop lines.
**v1s (v1 + blowout minutes).** x = max(|team opening spread| − 8, 0) / 10, s = projected minutes / 30. Minutes × (1 + β0·x + β1·x·s),
clipped to [0.5, 1.2]; β0, β1 by least squares of (actual ÷ projected minutes − 1), weighted by projected minutes, on **2021-22 + 2022-23 box
scores only** (players with 3+ prior games, games with an opening spread). Everything else = v1.
Both need the player's 3+ games this season.

## Bet rule
- Market at the opener = the opener's own two prices, de-vigged. p = w·p_model + (1 − w)·p_open; **w fit per model on 2021-22 + 2022-23
  openers** (log loss).
- Bet the side with EV = p × decimal opening price − 1 ≥ 5%, one bet per player-stat-game, at the opener's book and price, 1 unit.
  Lines < 0.5 dropped. DNP = void.
- **Timing guard (as NBA):** the player's previous game must be on an earlier ET day than the opener's posting time, and the opener posted 1h+
  before the scheduled tip.
- **Which openers count:** real sportsbooks only (DraftKings, FanDuel, BetMGM, Caesars, theScore/ESPN BET, Hard Rock, Fanatics, BetRivers,
  bet365, PartyCasino/BetMGM network). DFS pick'em apps (Underdog, PrizePicks, Sleeper), the consensus and unknown book ids are excluded.
  *Why not DraftKings/FanDuel only, as in the NBA:* the probe shows DK/FD openers are rare after 2023-24 (books pulled college props
  in many states), so a DK/FD-only test would have almost no bets in two of three test seasons. The **DK/FD slice is reported separately**,
  and anything that passes goes live only at DK/FD, which carry NCAAM props in Connecticut now (seen in our own odds feed).
- **Seasons:** FIT 2021-22 + 2022-23 (w, β, a/b). **TEST 2023-24, 2024-25, 2025-26** (unseen). 2026-27 is not a test season (RULE 2).

## Pass (all needed; per model)
1. **Information:** logistic regression of the over outcome on logit(p_open) and (logit(p_model) − logit(p_open)) with an intercept, pooled test
   seasons, standard errors clustered by date: coefficient on the model term > 0 with a 90% CI above 0.
2. **Unseen seasons:** units > 0 in every test season with 100+ bets (seasons with fewer are reported, not counted), and pooled test ROI with a
   90% bootstrap CI (by date) above 0.
3. **Closing line, lean-adjusted:** closing-line EV = same book's close no-vig (moved to our line with a normal shift) × our opening price − 1,
   adjusted by the close's over-lean measured on the OTHER seasons (leave-one-season-out). Pooled test mean ≥ 0.
4. **Beats the simple versions** on the same opener rows: (a) the same rule with w = 0, (b) every under at those openers.
If both models pass, the one with the higher lean-adjusted closing-line EV goes forward (units as the tie-break check).
A pass goes to a Fable review, then Jeffrey decides on a PROVISIONAL live record at DK/FD. A fail is logged with its numbers.

## Reported, no pass/fail
By stat, side, opening book, DK/FD slice, season, month (March/tournament separately: neutral sites, short rest), opener lead time,
thresholds 3/8/12%, spread bucket (v1s vs v1 in blowouts), log loss of model / opener / close / blend, line movement opener → close in our direction.

## Amendment 1 (Nov 6, 2026, ~01:30 ET) — written and pushed BEFORE any test-season outcome was looked at
The first run stopped on a code bug before grading anything. What it printed (no outcomes): coverage, the box-only variance fit, and a
blowout-minutes fit of exactly 0, because **2021-22 and 2022-23 have no opening game lines in our data** (`all_games.csv` open_sp/open_tot are
empty for those two seasons; only closing lines exist). So in the FIT seasons pace was always 1 and v1s could not be fit.
Change, applied to every season the same way: for the pace total and the blowout spread, use the opening number when it exists, else the
**closing** number from the archive (`close_tot`, `close_sp`). In 2023-24 to 2025-26 the opener exists for ~90% of games, so the test seasons are
essentially unchanged; in the FIT seasons the close stands in (approximate input, labeled; it carries a little hindsight into the fit of
w and β only, never into a test-season bet). Code fixes in the same commit: `np.clip` instead of the pandas-style `.clip(lower=)` on arrays.
The market-270 identification printed in that run: **270 = rebounds** (mean |line − model mean|: reb 0.69, ast 3.10, threes 3.73).
Nothing else changes.
