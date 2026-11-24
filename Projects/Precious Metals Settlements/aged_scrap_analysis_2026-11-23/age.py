import pickle,re,collections,datetime as dt
exec(open('sold.py').read().split("rows={}")[0])
R=pickle.load(open('sold.pkl','rb'))
def cls(c):
    cl=c.lower()
    if any(k in cl for k in ['coin','bullion','smart watch','watch band','scrap']): return None
    if 'watch' in cl: return 'watch'
    if not any(k in cl for k in ['ring','pendant','chain','necklace','bracelet','earring','charm','brooch','anklet','wedding','bangle','misc.','band','set','jewel']): return None
    if 'silver' in cl: return 'silver'
    if any(k in cl for k in ['gold','diamond','platinum']): return 'gold'
    if 'stone' in cl or 'pearl' in cl: return 'stone/other'
    return 'other'
def kdwt(desc):
    k=re.search(r'(\d{1,2})\s*K',desc.upper()); w=re.search(r'(\d+(?:\.\d+)?)\s*(DWT|DW|D\b|G\b|GR)',desc.upper())
    return (int(k.group(1)) if k else None, (float(w.group(1))*(0.643 if w.group(2) in('G','GR') else 1)) if w else None)
out=[]
for r in R:
    c=cls(r['cat'])
    if not c: continue
    m=re.match(r'([A-Z]+)(\d+)$',r['num'])
    if not m: continue
    a=ndate(r['st'],int(m.group(2)))
    if not a: continue
    r['cls']=c; r['age']=(r['sd']-a).days; r['k'],r['dwt']=kdwt(r['desc']); out.append(r)
pickle.dump(out,open('jew.pkl','wb'))
print('jewelry sold rows',len(out), 'span',min(r['sd'] for r in out),max(r['sd'] for r in out))
B=[(0,180,'<6mo'),(180,365,'6-12mo'),(365,548,'12-18mo'),(548,730,'18-24mo'),(730,99999,'24mo+')]
for c in ['gold','silver','stone/other','watch','other']:
    print('==',c)
    for lo,hi,l in B:
        s=[r for r in out if r['cls']==c and lo<=r['age']<hi]
        if not s: continue
        tc=sum(r['cost'] for r in s); tp=sum(r['sold'] for r in s)
        print(f"{l:8} n={len(s):5} cost={tc:10,.0f} rev={tp:10,.0f} mult={tp/tc if tc else 0:4.2f} neg_age={sum(1 for r in s if r['age']<0)}")
print('negative ages',sum(1 for r in out if r['age']<0))
