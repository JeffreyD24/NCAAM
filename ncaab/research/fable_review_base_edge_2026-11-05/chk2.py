import numpy as np, pandas as pd
W="/home/claude/ncaam"
B=pd.read_csv(f"{W}/ncaab/research/lineup_travel_v3_bets.csv")
A=B[(B.model=="A")&(B.q==0.01)].copy()
G=pd.read_csv(f"{W}/ncaab/data/three_targets_preds.csv",low_memory=False)
A=A.merge(G[["espn_id","open_sp","neutral","tournament","conf_game","M2_m","M8_m","MKT_m","home_pts","away_pts"]],on="espn_id")
print("n",len(A),"CLV mean",A.clv.mean(),"median",A.clv.median(),"sd",A.clv.std())
print("CLV quantiles",A.clv.quantile([0,.05,.1,.25,.5,.75,.9,.95,1]).round(2).to_dict())
print("share clv>0",(A.clv>0).mean(),"==0",(A.clv==0).mean(),"<0",(A.clv<0).mean())
print("side counts",A.side.value_counts().to_dict())
print("|op| quantiles",A.op.abs().quantile([0,.25,.5,.75,.9,1]).round(1).to_dict())
print("op vs AN open diff (op - open_sp) quantiles",(A.op-A.open_sp).quantile([0,.05,.25,.5,.75,.95,1]).round(2).to_dict())
print("|op-open_sp|>=3:",((A.op-A.open_sp).abs()>=3).sum(), " missing AN open:",A.open_sp.isna().sum())
# CLV when DK opener close to AN open vs not
near=(A.op-A.open_sp).abs()<=1
print("CLV near AN open (<=1):",A.clv[near].mean(),near.sum()," far:",A.clv[~near].mean(),(~near).sum())
# leave out top 5 CLV
s=A.sort_values("clv",ascending=False)
print("CLV without top5:",s.clv.iloc[5:].mean()," without top10:",s.clv.iloc[10:].mean())
print("top CLV bets:"); print(s[["season","date","home_name","away_name","op","close_sp","open_sp","side","clv","res","predA"]].head(12).to_string())
print("worst:"); print(s[["season","date","home_name","away_name","op","close_sp","open_sp","side","clv","res","predA"]].tail(5).to_string())
print("date spread: by month", A.date.str[:7].value_counts().sort_index().to_dict())
print("neutral",A.neutral.mean(),"tournament",A.tournament.value_counts().to_dict(),"conf_game",A.conf_game.mean())
print("units by month", A.groupby(A.date.str[:7]).res.sum().round(1).to_dict())
# does the AN-open-based rule also give CLV? (i.e., is CLV simply DK opener being a stale/soft opener relative to AN?)
# CLV vs AN open
A["clv_an"]=A.side*(A.open_sp-A.close_sp)
print("CLV measured from AN open instead:",A.clv_an.mean())
print("sign of (op-open_sp) vs side: DK softer than AN in bet direction",(A.side*(A.op-A.open_sp)).mean())
# repeated teams
tm=pd.concat([A.home_name,A.away_name]).value_counts(); print(tm.head(10).to_dict())
