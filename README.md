# NCAAM: college basketball models, data and research

Everything about men's college basketball that was built in `nba-mixed-model`, copied here on Nov 5, 2026 so it can be found in one place.
**This is a snapshot copy.** The files are at the same relative paths as in `nba-mixed-model`, so the scripts run unchanged from this repo's root
(`python ncaab/daily.py .`). The original files in `nba-mixed-model` were NOT deleted or changed.

## Where things are
| Path | What it is |
|---|---|
| `ncaab/` | All code (`model.py`, `model2_*.py`, `model3*.py`, tournament, daily and live jobs), data, research and state. Start with `ncaab/README.md` and `ncaab/CLAUDE.md`. |
| `ncaab/research/` | Every pre-registration (`*_PREREG_*`) and result (`*_RESULTS_*`) plus raw outputs. Nine studies: Model 1, Model 2, Model 3, team groups, conference totals, book openers, tournament, three targets. |
| `ncaab/data/` | Game tables (`games.csv`, `all_games.csv`, `sbr_games.csv`), ESPN openers and meta, model predictions, and ESPN box scores for 2007-08 to 2026-27 (`box/`). |
| `ncaab/state/` | Test records, PROVISIONAL stale-line alerts (`live_*`), DraftKings line captures (`dk_lines.csv`). |
| `data/external/sbr_ncaab/` | SportsbookReview college basketball odds archive, 2007-08 to 2020-21 (`.xlsx`). Cleaned by `ncaab/clean_sbr.py`. |
| `sharp/data/ncaab_splits.csv.gz`, `sharp/live/ncaab/` | College basketball betting-splits history and live captures from the shared sharp-money system. |
| `docs/project_docs/` | The plain-language result summaries from the Sports Mixed Models project (seven NCAAM / college docs). |
| `reference_from_nba_mixed_model/` | Pieces of shared files that mention college basketball: the FINDINGS.md master-log entries (extract), the threshold and bet-version rows, and the three GitHub Actions workflows (**inactive copies**). |
| `CLAUDE.md` | The same standing rules as the other model repos (record everything, past seasons are the test, derived files, etc.). |

## What still runs from `nba-mixed-model` (not moved)
These live jobs write into `nba-mixed-model/ncaab/`, so that copy keeps updating and this one does not:
the 9:17 AM ET daily workflow (`ncaab.yml`), the M2 totals TEST record, the live stale-line alert (`ncaab/live_alert.py` through `alert_loop.sh`),
the health check, and the sharp-money capture. The workflow files here are in `reference_from_nba_mixed_model/workflows_INACTIVE/` on purpose:
putting them in `.github/workflows/` would start a second copy of each job. Moving the live jobs here is a separate change (needs the workflow
secrets and the alert loop re-pointed).

## Where the college results stand (Nov 5, 2026)
No college basketball model has a confirmed edge at a bettable line. Model 1 and its variants fail at DraftKings' own opener and close;
the one spreads pass at ESPN BET openers was caused by sign-flipped quotes and fails once removed; conference totals, team groups and
elite-coach edges existed in 2008-2023 and are gone. Open items are the M2 totals TEST record at DraftKings' opener (Fable re-review at about 300 bets), the
CLV-forecast tool (predicting the DraftKings close from its opener), and the stale-line PROVISIONAL spread alerts. Details: `docs/project_docs/`.
