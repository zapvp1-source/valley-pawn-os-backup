import csv,glob,re,os,datetime as dt,collections
O=os.path.expanduser('~/mnt/Projects/Bravo Data Extraction/output')
def d(s):
    try: return dt.datetime.strptime(s.strip(),'%m/%d/%Y').date()
    except: return None
pts=collections.defaultdict(list)
for f in glob.glob(O+'/*_items-to-price.csv'):
    st=re.search(r'_(CUL|WAY|HAR|LEX|ROA)_',f).group(1)
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        m=re.match(r'BT-([A-Z]+)(\d+)',r.get('Number') or '')
        if m and d(r['Date']): pts[(st,'BT',m.group(1))].append((int(m.group(2)),d(r['Date'])))
for f in glob.glob(O+'/*pm-loan-growth*.csv')+glob.glob(O+'/*loan-reminders.csv')+glob.glob(O+'/*forfeiture-winback*.csv'):
    mm=re.search(r'_(CUL|WAY|HAR|LEX|ROA)_',f)
    if not mm: continue
    st=mm.group(1)
    try:
      for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        m=re.match(r'[LF]T-([A-Z]+)(\d+)',r.get('Ticket Number',''))
        dd=d(r.get('Due Date',''))
        if m and dd: pts[(st,'LT',m.group(1))].append((int(m.group(2)),dd-dt.timedelta(days=30)))
    except Exception as e: pass
for k,v in sorted(pts.items()):
    v=sorted(set(v)); 
    if len(v)<20: continue
    print(k,len(v),v[0],v[len(v)//4],v[len(v)//2],v[-1])

import bisect,json
curves={}
for st in ['CUL','WAY','HAR','LEX','ROA']:
    allp=[]
    for (s,t,p),v in pts.items():
        if s==st and p in ('VP','VA','VAP','ROA'): allp+=v
    allp=sorted(set(allp))
    nums=[n for n,_ in allp]; ds=[x for _,x in allp]
    # lower envelope from right
    env=ds[:]
    for i in range(len(env)-2,-1,-1): env[i]=min(env[i],env[i+1])
    curves[st]=(nums,env)
    print(st,len(nums),nums[0],env[0],nums[-1],env[-1])
def ndate(st,num):
    nums,env=curves[st]
    i=bisect.bisect_left(nums,num)
    if i>=len(nums): return env[-1]
    if i==0: return None if num<nums[0]-50 else env[0]
    return env[i]
