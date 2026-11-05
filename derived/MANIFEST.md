# derived/ manifest (RULE 4: saved builds, never rebuilt)

| file | what it is | built by | inputs | commit |
|---|---|---|---|---|
| `lineup_travel_features.csv.gz` | One row per game (111,435; 2007-08 to 2026-27): pre-game lineup / inferred-injury / travel / rest features for the home (`h_*`) and away (`a_*`) team, plus `oracle_*` (game's own box score; NOT tradable, diagnostic). Definitions: `ncaab/research/LINEUP_INJURY_TRAVEL_PREREG_2026-11-05.md`. | `ncaab/lineup_travel_features.py` (about 70 s) | `ncaab/data/all_games.csv`, `ncaab/data/box/{players,teams}_*.csv.gz` | see git log for this file |

Not saved here (already tracked elsewhere in this repo): walk-forward predictions `ncaab/data/three_targets_preds.csv` (M1/M2/M8/MKT), `model2_preds.csv`, `model3_preds.csv`.
`derived.py` (the restore/save helper in nhl-mixed-model) has not been copied into this repo yet; files here are plain tracked gzips.
