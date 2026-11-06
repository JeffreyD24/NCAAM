# derived/ manifest (RULE 4: saved builds, never rebuilt)

| file | what it is | built by | inputs | commit |
|---|---|---|---|---|
| `lineup_travel_features.csv.gz` | One row per game (111,435; 2007-08 to 2026-27): pre-game lineup / inferred-injury / travel / rest features for the home (`h_*`) and away (`a_*`) team, plus `oracle_*` (game's own box score; NOT tradable, diagnostic). Definitions: `ncaab/research/LINEUP_INJURY_TRAVEL_PREREG_2026-11-05.md`. | `ncaab/lineup_travel_features.py` (about 70 s) | `ncaab/data/all_games.csv`, `ncaab/data/box/{players,teams}_*.csv.gz` | see git log for this file |

Not saved here (already tracked elsewhere in this repo): walk-forward predictions `ncaab/data/three_targets_preds.csv` (M1/M2/M8/MKT), `model2_preds.csv`, `model3_preds.csv`.
`derived.py` (the restore/save helper in nhl-mixed-model) has not been copied into this repo yet; files here are plain tracked gzips.
| `roster_features.csv.gz` | One row per game (111,435): early-season roster features for home (`h_*`) and away (`a_*`): games before this one (n), returning share of last season's points (ret), incoming transfers' points share (inc), last-season strength (str, strin), R1-R4 (early-weighted, games 1-14). Definitions: `ncaab/research/ROSTER_CONTINUITY_PREREG_2026-11-05.md`. | `ncaab/roster_features.py` (about 75 s) | `ncaab/data/all_games.csv`, `ncaab/data/box/players_*.csv.gz` | see git log for this file |
| `ncaam_props_features.csv.gz` | One row per player-game (572,495; 2021-22 to 2026-27, players with projected minutes ≥ 10): box-only player-prop features (projected minutes, per-minute rates, opponent allowed factors, pace from the opening total, team-perspective opening spread, mu_<stat> for pts/reb/ast/fg3m, actual stats). No prop lines used. Rounded to 4 dp. | `ncaab/props/features.py` (about 60 s) | `ncaab/data/box/players_full_*.csv.gz`, `ncaab/data/espn_meta.csv`, `ncaab/data/espn_openers.csv`, `ncaab/data/all_games.csv` | see git log for this file |
