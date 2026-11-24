import pickle,re,collections,datetime as dt,bisect
exec(open('age.py').read().split("out=[]")[0])
cur={}
for st in ['CUL','WAY','HAR','LEX','ROA']:
    p=collections.defaultdict(lambda:dt.date(2099,1,1))
    for r in R:
        if r['st']!=st: continue
        m=re.match(r'([A-Z]+)(\d+)$',r['num'])
        if not m: continue
        n=int(m.group(2)); p[(m.group(1),n)]=min(p[(m.group(1),n)],r['sd'])
    # main prefix
    pref=collections.Counter(k[0] for k in p).most_common(1)[0][0]
    pts=sorted((n,d0) for (pf,n),d0 in p.items() if pf==pref)
    nums=[n for n,_ in pts]; env=[d0 for _,d0 in pts]
    import heapq
    K=5; h=[]; e2=env[:]
    for i in range(len(env)-1,-1,-1):
        heapq.heappush(h,-env[i].toordinal())
        if len(h)>K: heapq.heappop(h)
        e2[i]=dt.date.fromordinal(-h[0]) if len(h)==K else env[i]
    env=e2
    cur[st]=(pref,nums,env)
    # find number boundary where env first exceeds 2025-07-20 (reliable from here)
    j=next(i for i,x in enumerate(env) if x>dt.date(2025,7,20))
    print(st,pref,len(nums),'reliable from num',nums[j],env[j])
    for q in [0.1,0.3,0.5,0.7,0.9]: i=int(q*len(nums)); print('   ',nums[i],env[i])
    cur[st]=(pref,nums,env,nums[j])
pickle.dump(cur,open('cur.pkl','wb'))
