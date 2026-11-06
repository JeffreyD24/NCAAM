import numpy as np, pandas as pd, os
W="/home/claude/ncaam"
P=pd.read_csv(f"{W}/ncaab/data/three_targets_preds.csv",low_memory=False)
F=pd.read_csv(f"{W}/derived/lineup_travel_features.csv.gz",low_memory=False).drop(columns=["season","date"])
D=P.merge(F,on="espn_id",how="inner"); print(len(D),len(P))
D["margin"]=D.home_pts-D.away_pts
FEATS=["lost_min_share","lost_pts_share","new_starters","travel_miles","tz_shift","rest_days","back_to_back","games_last_7"]
for c in FEATS: D["s_"+c]=D["h_"+c]-D["a_"+c]
XC=["s_"+c for c in FEATS]
ok=D.margin.notna()&(D.h_n_box>=5)&(D.a_n_box>=5)&D[["M2_m","M8_m","MKT_m"]].notna().all(axis=1)&D[XC].notna().all(axis=1)&D.close_sp.notna()
D=D[ok].copy()
TRAIN=[2008,2009,2010,2011,2014,2015,2016,2017,2018,2019,2020,2021]
T=D[D.season.isin(TRAIN)&D.open_sp.notna()].copy()
T=T[((T.open_sp-T.close_sp).abs()<6)&~((np.sign(T.open_sp)!=np.sign(T.close_sp))&(T.open_sp.abs()>=3)&(T.close_sp.abs()>=3))]
T["op"]=T.open_sp
w=np.linalg.lstsq(np.c_[np.ones(len(T)),T[["M2_m","M8_m","MKT_m"]].values],T.margin.values,rcond=None)[0]
print("w",np.round(w,4))
g=np.c_[np.ones(len(T)),T[["M2_m","M8_m","MKT_m"]].values]@w+T.op.values
y=T.margin.values+T.op.values
m,s=g.mean(),g.std(); Z=(g-m)/s; c=(Z@(y-y.mean()))/(Z@Z+10)
# pred = ym + (g-m)/s*c = (ym - m*c/s) + (c/s)*g
print("intercept",y.mean()-m*c/s,"slope",c/s, "ym",y.mean(),"m",m,"s",s,"c",c)
a0,a1=y.mean()-m*c/s,c/s
print("gap cutoffs for edge +/-2.8:",(2.8-a0)/a1,(-2.8-a0)/a1, " for 3.0:",(3.0-a0)/a1,(-3.0-a0)/a1)
# OLS slope for comparison
print("OLS slope",np.polyfit(g,y,1))
