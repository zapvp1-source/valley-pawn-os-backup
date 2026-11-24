import pickle,re,collections,datetime as dt,bisect
exec(open('age.py').read().split("out=[]")[0])
cur=pickle.load(open('cur.pkl','rb'))
def created(st,num):
    pref,nums,env,thr=cur[st]
    m=re.match(r'([A-Z]+)(\d+)$',num)
    if not m or m.group(1)!=pref: return None,'nopref'
    n=int(m.group(2))
    if n<thr: return None,'old'
    i=bisect.bisect_left(nums,n)
    return (env[min(i,len(env)-1)],'ok')
J=[]
for r in R:
    c=cls(r['cat'])
    if not c or c=='watch': continue
    cd,flag=created(r['st'],r['num'])
    r['cls']=c; r['flag']=flag; r['age']=(r['sd']-cd).days if cd else None; r['k'],r['dwt']=kdwt(r['desc'])
    J.append(r)
pickle.dump(J,open('J.pkl','wb'))
W0,W1=dt.date(2026,8,12),dt.date(2026,11,22)
def b(r):
    if r['flag']=='old': return '>=12.6mo(pre-Jul25)'
    if r['flag']!='ok': return 'unk'
    a=r['age']
    return '<6mo' if a<183 else '6-12mo' if a<365 else '12-18mo' if a<548 else '18mo+'
for grp in [('gold','stone/other','other'),('silver',)]:
    print('#####',grp)
    T=collections.defaultdict(lambda:[0,0.0,0.0])
    for r in J:
        if r['cls'] in grp and W0<=r['sd']<=W1:
            for key in [(r['st'],b(r)),('ALL',b(r))]:
                t=T[key]; t[0]+=1;t[1]+=r['cost'];t[2]+=r['sold']
    for k in sorted(T): print(k,T[k][0],round(T[k][1]),round(T[k][2]), round(T[k][2]/T[k][1],2) if T[k][1] else '')
