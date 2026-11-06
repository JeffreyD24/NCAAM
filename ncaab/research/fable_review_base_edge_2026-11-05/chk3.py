import numpy as np, pandas as pd, sys
W="/home/claude/ncaam"
src=open(f"{W}/ncaab/lineup_travel_opener_grade.py").read().split("# ---------- choose k")[0]
ns={"__name__":"v2"}; sys.argv=["x",W]; exec(src,ns)
T,E,fit,predict,bets=(ns[k] for k in ("T","E","fit","predict","bets"))
M=fit(T); E["predA"],_=predict(M,E,"A"); E["gap"]=M["gap"](E)
H=E[(E.book=="DraftKings")&E.season.isin([2024,2026])&~E.b2b].copy()
print("H gap mean",H.gap.mean().round(3),"sd",H.gap.std().round(3)," train gap mean",M["gap"](T).mean().round(3))
H["clv_home"]=H.op-H.close_sp
print("all H: mean home-direction move (op-close)",H.clv_home.mean().round(3), " bet-home-always CLV", H.clv_home.mean().round(3))
for k in (1,1.5,2,2.5,2.8,3.0,3.5,4):
    b=bets(H,H.predA.values,k); hb=b[b.side>0]; ab=b[b.side<0]
    print(f"k {k}: n {len(b)} CLV {b.clv.mean():+.3f} units {b.res.sum():+.1f} hit {(b.res[b.res!=0]>0).mean():.3f} | home n {len(hb)} CLV {hb.clv.mean():+.2f} u {hb.res.sum():+.1f} | away n {len(ab)} CLV {ab.clv.mean() if len(ab) else float('nan'):+.2f} u {ab.res.sum():+.1f}")
b=bets(H,H.predA.values,2.8); print("k2.8 by season",b.groupby("season").agg(n=("clv","size"),clv=("clv","mean"),u=("res","sum")).round(2).to_dict())
b["absop"]=pd.cut(b.op.abs(),[-1,5,10,20,50])
print(b.groupby("absop",observed=True).agg(n=("clv","size"),clv=("clv","mean"),u=("res","sum")).round(2))
b["mon"]=b.date.astype(str).str[5:7]
print(b.groupby("mon").agg(n=("clv","size"),clv=("clv","mean"),u=("res","sum")).round(2).T)
# in-sample vs the same rule applied to ESPN BET 2025 and the SBR train seasons at k=2.8
S2=E[(E.book=="ESPN BET")&(E.season==2025)&~E.b2b]; b2=bets(S2,S2.predA.values,2.8); print("ESPN BET 2025 k2.8:",len(b2),b2.clv.mean().round(3),b2.res.sum().round(1))
# what fraction of H gets the b2b filter and what the bets would look like without it (live rule has no b2b filter)
Hb=E[(E.book=="DraftKings")&E.season.isin([2024,2026])]; bb=bets(Hb,Hb.predA.values,2.8); print("no b2b filter k2.8:",len(bb),bb.clv.mean().round(3),bb.res.sum().round(1))
# is the CLV mostly "line moves toward the favorite / toward home"? compare with naive: bet home when |op| large
for lo,hi in ((0,5),(5,10),(10,20),(20,60)):
    s=H[(H.op.abs()>=lo)&(H.op.abs()<hi)]; fav=np.sign(-s.op); print(f"|op| {lo}-{hi}: n {len(s)} mean move toward home {s.clv_home.mean():+.3f}, toward favorite {(fav*(s.op-s.close_sp)).mean():+.3f}")
