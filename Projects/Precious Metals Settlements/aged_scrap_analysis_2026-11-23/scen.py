import json,pickle,datetime as dt
res=json.load(open('res.json'))
J=pickle.load(open('J.pkl','rb'))
SPOT=3619.95;F=0.826
W0,W1=dt.date(2026,8,12),dt.date(2026,11,22)
A=[r for r in J if W0<=r['sd']<=W1 and (r['flag']=='old' or (r['flag']=='ok' and r['age']>=365)) and r['cls']!='silver' and r.get('k') and r.get('dwt') and r['k']<=24]
ratios=sorted(r['sold']/(r['dwt']*r['k']/24/20*SPOT*F) for r in A)
n=len(ratios); 
for t in [1.0,1.2,1.5]: print('share sold at < %.1fx melt: %.0f%%'%(t,100*sum(1 for x in ratios if x<t)/n))
print('median sold/melt',round(ratios[n//2],2),'n',n)
# tag/melt for those
tr=[r['tag']/(r['dwt']*r['k']/24/20*SPOT*F) for r in A if r.get('tag')]
tr.sort(); print('median tag/melt',round(tr[len(tr)//2],2))
def impact(st,s,R,M,rate):
    d=res[st]; inv=d['inv_avg']
    flow=inv*12/(6*(1-s/2))
    lost=s*(R-M)               # retail premium given up per $ cost
    carry=M*rate*0.5*(1-s/2)   # financing saved per $ cost
    return flow, flow*(carry-lost)
print()
base=dict(M=1.9,rate=0.10)
for st in ['CUL','HAR','ROA','WAY','LEX','ALL']:
    d=res[st]; R=d['mult'] if d['mult'] else 2.98
    if st=='LEX': R=2.21
    f,mid=impact(st,d['sell6_mid'],R,**base)
    _,lo=impact(st,d['sell6_hi'],R,**base)
    _,hi=impact(st,d['sell6_lo'],R,**base)
    be=base['M']*base['rate']*0.5/(R-base['M'])
    print(f"{st}: bucket now ${d['now']:,} avg ${d['inv_avg']:,} flow/yr ${f:,.0f} sell6 {d['sell6_lo']:.0%}-{d['sell6_hi']:.0%} (mid {d['sell6_mid']:.0%}) R={R} | switch-to-12 annual effect mid ${mid:,.0f} range ${lo:,.0f}..${hi:,.0f} | breakeven sell6 {be:.1%}")
print('\nSTRESS (ALL):')
d=res['ALL']
for lab,kw in [('base',dict(s=d['sell6_mid'],R=2.98,M=1.9,rate=.10)),('carry 25%',dict(s=d['sell6_mid'],R=2.98,M=1.9,rate=.25)),('gold +20% (M 2.28)',dict(s=d['sell6_mid'],R=2.98,M=2.28,rate=.10)),('gold -20% (M 1.52)',dict(s=d['sell6_mid'],R=2.98,M=1.52,rate=.10)),('retail -20% (R 2.38)',dict(s=d['sell6_mid'],R=2.38,M=1.9,rate=.10)),('low sell-through 12%',dict(s=d['sell6_lo'],R=2.98,M=1.9,rate=.10)),('worst combo',dict(s=d['sell6_lo'],R=2.38,M=2.28,rate=.25))]:
    f,v=impact('ALL',**kw); print(f"  {lab:24} switch-to-12 effect ${v:,.0f}/yr  breakeven sell6 {kw['M']*kw['rate']*0.5/(kw['R']-kw['M']):.1%}")
