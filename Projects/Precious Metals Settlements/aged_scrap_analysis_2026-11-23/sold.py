exec(open('map.py').read().split("for k,v in sorted(pts.items()):")[0])
exec("import bisect\n"+open('map.py').read().split("import bisect,json")[1].replace("print(st,len","pass #"))
def money(s):
    try: return float(s.replace('$','').replace(',','').strip())
    except: return None
rows={}
files=[f for f in glob.glob(O+'/*_jewelry-margin-sold.csv') if re.search(r'(\d{4}-\d\d)-01_to_\1-\d\d_',f) or '07-28_to_2026-07-28' in f]+glob.glob(O+'/*_sold-discount-detail.csv')
for f in files:
    st=re.search(r'_(CUL|WAY|HAR|LEX|ROA)_',f).group(1)
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        if (r.get('Status') or '').strip()!='SOLD': continue
        sd=d(r.get('Date','')); c=money(r.get('Cost','')); p=money(r.get('Last Sold Price',''))
        if not sd or c is None or p is None: continue
        rows[(st,r['Number'])]=dict(st=st,num=r['Number'],cat=r['Category'],desc=r['Description'],cost=c,tag=money(r.get('Price','')),sold=p,sd=sd)
print(len(rows))
cats=collections.Counter(r['cat'] for r in rows.values())
import pickle; pickle.dump(list(rows.values()),open('sold.pkl','wb'))
for c,n in cats.most_common(400): print(n,c)
