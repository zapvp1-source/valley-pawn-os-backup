import csv,glob,re,pickle,bisect,datetime as dt,collections
cur=pickle.load(open('cur.pkl','rb'))
L='/'.join(__import__('os').path.expanduser('~/mnt/Projects/Bravo Data Extraction/logs-scrap').split('/'))
def kd(desc):
    u=desc.upper()
    k=re.search(r'(\d{1,2})\s*K',u); w=re.search(r'(\d+(?:\.\d+)?)\s*(DWT|DW|G\b|GR)',u)
    return (int(k.group(1)) if k else None,(float(w.group(1))*(0.643 if w.group(2) in('G','GR') else 1)) if w else None)
def created(st,num):
    pref,nums,env,thr=cur[st]
    m=re.match(r'([A-Z]+)(\d+)$',num)
    if not m or m.group(1)!=pref: return None
    n=int(m.group(2)); i=bisect.bisect_left(nums,n)
    if n<thr: return 'old'
    return env[min(i,len(env)-1)]
agg=collections.defaultdict(lambda:[0,0.0,0.0]); fine={'gold':0.0,'stones':0.0}; cost={'gold':0,'stones':0}
for f in glob.glob(L+'/scrap-2026-10-cost_*_items.csv'):
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        st=r['Store']; typ='stones' if 'STONES' in r['Bucket'] else 'gold'
        k,w=kd(r['Description']); c=float(r['Cost'] or 0)
        if k and w and k<=24: fine[typ]+=w*k/24/20
        cost[typ]+=c
        cd=created(st,r['Number'])
        ref=dt.date(2026,10,31)
        b='pre-Jul25' if cd=='old' else 'unk' if cd is None else ('<1mo' if (ref-cd).days<31 else '1-6mo' if (ref-cd).days<183 else '6-12mo' if (ref-cd).days<365 else '12-18mo' if (ref-cd).days<548 else '18+')
        a=agg[(r['Category'][:25],b)]; a[0]+=1; a[1]+=c
        a=agg[('ALL',b)]; a[0]+=1; a[1]+=c
print('fine ozt',fine,'cost',cost)
spot=4032.4
print('gold lot payout factor on Bravo-described fine gold:',round(28509.15/(fine['gold']*spot),3))
print('stones lot $/fine-oz-equiv factor:',round(31996.87/(fine['stones']*3906.3),3))
for k in sorted(agg): 
    if agg[k][1]>300 or k[0]=='ALL': print(k,agg[k][0],round(agg[k][1]))

print('---- case items scrapped in Oct (non-Scrap category), melt vs cost')
tot=collections.defaultdict(lambda:[0,0.0,0.0,0])
for f in glob.glob(L+'/scrap-2026-10-cost_*_items.csv'):
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        if 'scrap' in r['Category'].lower(): grp='scrap-cat'
        else: grp='case-item'
        cd=created(r['Store'],r['Number'])
        age='old' if cd=='old' else 'new' 
        k,w=kd(r['Description']); c=float(r['Cost'] or 0)
        typ='stones' if 'STONES' in r['Bucket'] else 'gold'
        if not(k and w and k<=24): tot[(grp,age,typ,'nomelt')][0]+=1; tot[(grp,age,typ,'nomelt')][1]+=c; continue
        m=w*k/24/20*4032.4*0.826
        t=tot[(grp,age,typ,'melt')]; t[0]+=1;t[1]+=c;t[2]+=m
for k in sorted(tot): t=tot[k]; print(k,t[0],round(t[1]),round(t[2]), round(t[2]/t[1],2) if t[1] and t[2] else '')
