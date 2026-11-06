"""NCAAM player props — box-score features (no prop lines used). Port of nba-mixed-model analysis/props_v1.py features() (v1b),
with the college changes written in ncaab/research/props/PROPS_V1_PREREG_*.md. Nov 5, 2026.
  python ncaab/props/features.py WORKDIR  -> _tmp/ncaam_props_features.csv.gz (save with derived/; RULE 4)
One row per player-game (players who played), seasons 2021-22 on (2020-21 loaded only as the prior). Every feature uses games before
the current game's date only. Columns: season, date, espn_id, team_id, opp_id, home, athlete_id, name, starter, min, n_prev, min_proj,
pace, open_sp_team (team-perspective DK/consensus opening spread, + = underdog), the four stats, mu_<stat>, rate_<stat>, allow_<stat>."""
import os, sys, re, glob, unicodedata
import numpy as np, pandas as pd
W = os.path.abspath(sys.argv[1])
ST = ["pts", "reb", "ast", "fg3m"]; PACE = {"pts": True, "ast": True, "fg3m": True, "reb": False}
HL_MIN, HL_RATE, PRIOR_GAMES, PRIOR_MIN, K_OPP = 5, 20, 5, 150, 15
SEASONS = [2021, 2022, 2023, 2024, 2025, 2026, 2027]


def norm(n):
    n = unicodedata.normalize("NFKD", str(n)).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"[.'`]", "", n).replace("-", " "); n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


def main():
    M = pd.read_csv(os.path.join(W, "ncaab", "data", "espn_meta.csv"), low_memory=False)[["date", "espn_id", "home_espn_team", "away_espn_team", "neutral"]]
    M = M.drop_duplicates("espn_id"); M["espn_id"] = M.espn_id.astype(int)
    B = []
    for s in SEASONS:
        f = os.path.join(W, "ncaab", "data", "box", f"players_full_{s}.csv.gz")
        if os.path.exists(f): B.append(pd.read_csv(f, dtype={"athlete_id": str}).assign(season=s))
    B = pd.concat(B, ignore_index=True).merge(M, on="espn_id", how="inner")
    B = B[(B.dnp == 0) & (B["min"] > 0)].copy(); B["d"] = pd.to_datetime(B.date)
    B["home"] = (B.team_id == B.home_espn_team).astype(int)
    B["opp_id"] = np.where(B.home == 1, B.away_espn_team, B.home_espn_team)
    B = B.sort_values(["athlete_id", "season", "d"]).reset_index(drop=True)
    # last-season priors (ESPN athlete ids follow transfers)
    agg = B.groupby(["athlete_id", "season"]).agg(g=("min", "size"), m=("min", "sum"), **{s: (s, "sum") for s in ST}).reset_index()
    lg = agg.groupby("season").sum(numeric_only=True)
    league_rate = {(s, st): lg.loc[s, st] / lg.loc[s, "m"] for s in lg.index for st in ST}
    newmpg = B.groupby("season")["min"].mean().to_dict()          # league minutes per appearance: prior for players with no last season
    agg["season"] += 1; agg = agg.set_index(["athlete_id", "season"])
    dm, dr = 0.5 ** (1 / HL_MIN), 0.5 ** (1 / HL_RATE)
    cols = {c: np.full(len(B), np.nan) for c in ["n_prev", "min_proj"] + [f"rate_{s}" for s in ST]}
    for (pid, season), idx in B.groupby(["athlete_id", "season"]).indices.items():
        pr = agg.loc[(pid, season)] if (pid, season) in agg.index else None
        p_mpg = pr.m / pr.g if pr is not None else newmpg.get(season - 1, newmpg[season])
        p_rate = {s: (pr[s] / pr.m if pr is not None and pr.m >= 300 else league_rate.get((season - 1, s), league_rate[(season, s)])) for s in ST}
        Sm = Sw = Srm = 0.0; Sr = {s: 0.0 for s in ST}
        mins = B["min"].values[idx]; vals = {s: B[s].values[idx] for s in ST}
        for k, i in enumerate(idx):
            cols["n_prev"][i] = k
            cols["min_proj"][i] = (Sm + PRIOR_GAMES * p_mpg) / (Sw + PRIOR_GAMES)
            for s in ST: cols[f"rate_{s}"][i] = (Sr[s] + PRIOR_MIN * p_rate[s]) / (Srm + PRIOR_MIN)
            Sm = Sm * dm + mins[k]; Sw = Sw * dm + 1; Srm = Srm * dr + mins[k]
            for s in ST: Sr[s] = Sr[s] * dr + np.nan_to_num(vals[s][k])
    for c, v in cols.items(): B[c] = v
    # opponent factor: stat allowed per game before this date (any opponent, incl. non-D1 games ESPN has), shrunk k=15 toward last season's league per game
    TG = B.groupby(["season", "d", "espn_id", "team_id"])[ST].sum().reset_index()
    opp = TG.merge(TG, on=["season", "d", "espn_id"], suffixes=("", "_o")); opp = opp[opp.team_id != opp.team_id_o].sort_values("d")
    for s in ST:
        lgpg = opp.groupby("season")[f"{s}_o"].mean().to_dict(); g = opp.groupby(["season", "team_id"])
        csum = g[f"{s}_o"].cumsum() - opp[f"{s}_o"]; cnt = g.cumcount()
        base = opp.season.map(lambda x: lgpg.get(x - 1, lgpg[x]))
        opp[f"allow_{s}"] = ((csum + K_OPP * base) / (cnt + K_OPP)) / base
    A = opp[["espn_id", "team_id"] + [f"allow_{s}" for s in ST]].rename(columns={"team_id": "opp_id"})
    B = B.merge(A, on=["espn_id", "opp_id"], how="left")
    # market numbers per game: DraftKings opener from ESPN (provider 100), else the archive opener in all_games.csv
    O = pd.read_csv(os.path.join(W, "ncaab", "data", "espn_openers.csv"))
    O = O[O.provider_id == 100].drop_duplicates("espn_id")[["espn_id", "open_spread", "open_total"]]
    G = pd.read_csv(os.path.join(W, "ncaab", "data", "all_games.csv"), low_memory=False)[["espn_id", "open_sp", "open_tot", "close_tot"]].drop_duplicates("espn_id")
    G = G.merge(O, on="espn_id", how="left")
    G["sp_home"] = G.open_spread.fillna(G.open_sp); G["tot"] = G.open_total.fillna(G.open_tot)
    B = B.merge(G[["espn_id", "sp_home", "tot"]], on="espn_id", how="left")
    B["open_sp_team"] = np.where(B.home == 1, B.sp_home, -B.sp_home)
    # pace = this game's opening total / the season's mean opening total over games before this date
    gt = B.drop_duplicates("espn_id")[["season", "d", "espn_id", "tot"]].dropna().sort_values("d")
    gt["run"] = gt.groupby("season").tot.transform(lambda v: v.shift().expanding().mean())
    gt["run"] = gt.run.fillna(gt.groupby("season").tot.transform("mean"))
    B = B.merge((gt.set_index("espn_id").tot / gt.set_index("espn_id").run).rename("pace"), left_on="espn_id", right_index=True, how="left")
    B["pace"] = B.pace.fillna(1.0)
    for s in ST: B[f"mu_{s}"] = B.min_proj * B[f"rate_{s}"] * B[f"allow_{s}"].fillna(1.0) * (B.pace if PACE[s] else 1.0)
    B["name_n"] = B.name.map(norm)
    keep = ["season", "date", "espn_id", "team_id", "opp_id", "home", "athlete_id", "name", "name_n", "starter", "min", "n_prev", "min_proj",
            "pace", "open_sp_team"] + ST + [f"mu_{s}" for s in ST] + [f"rate_{s}" for s in ST] + [f"allow_{s}" for s in ST]
    B = B[B.season >= 2022]
    os.makedirs(os.path.join(W, "_tmp"), exist_ok=True)
    B[keep].to_csv(os.path.join(W, "_tmp", "ncaam_props_features.csv.gz"), index=False)
    print(f"features: {len(B)} player-games, seasons {B.season.value_counts().sort_index().to_dict()}, pace from a market total {(B.pace != 1).mean():.1%}")
    F = B[(B.season == 2023) & (B.n_prev >= 3)]
    for s in ST: print(f"  2022-23 box check {s}: corr(mu, actual) {np.corrcoef(F[f'mu_{s}'], F[s].fillna(0))[0,1]:.3f}, mean mu {F[f'mu_{s}'].mean():.2f} vs actual {F[s].mean():.2f}")


if __name__ == "__main__":
    main()
