import pickle,json,collections,datetime as dt,re,csv,glob,os,bisect
J=pickle.load(open('J.pkl','rb'))
agedj=json.load(open('/tmp/agedjew.json'))
SPOT=3619.95; F=0.826
def melt(r,spot=SPOT):
    k,w=r.get('k'),r.get('dwt')
    if not k or not w or k>24: return None
    return w*k/24/20*spot*F
W0,W1=dt.date(2026,8,12),dt.date(2026,11,22); days=(W1-W0).days+1
res={}
for st in ['CUL','WAY','HAR','LEX','ROA','ALL']:
    S=[r for r in J if (st=='ALL' or r['st']==st) and W0<=r['sd']<=W1 and r['cls'] in('gold','stone/other','other','silver')]
    known=[r for r in S if r['flag']=='ok' and 365<=r['age']<548]
    old=[r for r in S if r['flag']=='old']
    inv=[ (sum(agedj[d][s][5] for s in agedj[d]) if st=='ALL' else agedj[d][st][5]) for d in sorted(agedj) if '2026-08-12'<=d<='2026-11-23' and (st=='ALL' and len(agedj[d])==5 or st in agedj[d])]
    avg=sum(inv)/len(inv)
    kc=sum(r['cost'] for r in known); oc=sum(r['cost'] for r in old)
    kr=sum(r['sold'] for r in known); orv=sum(r['sold'] for r in old)
    lo=kc/days*30.44/avg; hi=(kc+oc)/days*30.44/avg; mid=(kc+oc/2)/days*30.44/avg
    p6=lambda h:1-(1-h)**6
    res[st]=dict(inv_avg=round(avg),now=round(agedj['2026-11-23'][st][5]) if st!='ALL' else round(sum(agedj['2026-11-23'][s][5] for s in agedj['2026-11-23'])),
        sales_cost_known=round(kc),sales_cost_old=round(oc),rev_known=round(kr),rev_old=round(orv),
        n_known=len(known),n_old=len(old),hazard_lo=round(lo,4),hazard_mid=round(mid,4),hazard_hi=round(hi,4),
        sell6_lo=round(p6(lo),3),sell6_mid=round(p6(mid),3),sell6_hi=round(p6(hi),3),
        mult=round((kr+orv)/(kc+oc),2) if kc+oc else None)
    print(st,res[st])
# melt vs cost vs revenue on aged sold items (>=12mo)
A=[r for r in J if W0<=r['sd']<=W1 and (r['flag']=='old' or (r['flag']=='ok' and r['age']>=365)) and r['cls']!='silver']
mm=[(r,melt(r)) for r in A]; mm=[(r,m) for r,m in mm if m]
print('aged gold sold items w/ parsable melt',len(mm),'of',len(A))
c=sum(r['cost'] for r,m in mm); s=sum(r['sold'] for r,m in mm); M=sum(m for r,m in mm)
print('cost',round(c),'sold',round(s),'melt@today',round(M),'sold/melt',round(s/M,2),'melt/cost',round(M/c,2))
json.dump(res,open('res.json','w'))
