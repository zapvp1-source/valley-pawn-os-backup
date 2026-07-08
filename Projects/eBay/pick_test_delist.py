#!/usr/bin/env python3
import json,os,re
ts=json.load(open(os.path.expanduser('~/ebay_title_state.json')))    # id -> {original, store}
mdp=os.path.expanduser('~/ebay_markdown_state.json')
md=json.load(open(mdp)) if os.path.exists(mdp) else {}
sp=os.path.expanduser('~/ebay_short_titles.json')
short=json.load(open(sp)) if os.path.exists(sp) else []
price={x['id']:x.get('price') for x in short}
code=re.compile(r'\((?:[A-Za-z]{1,4})?\d{3,}[A-Za-z]?\)')
cands=[]
for iid,rec in ts.items():
    if not isinstance(rec,dict): continue
    o=rec.get('original','') or ''
    m=code.search(o)
    if not m: continue
    aged = iid in md
    pr=price.get(iid)
    cands.append({'id':iid,'store':rec.get('store'),'bravo':m.group(0),'aged':aged,'price':pr,'orig':o[:64]})
# prefer: aged, low price, Roanoke
def key(c):
    p=9999
    try: p=float(c['price']) if c['price'] else 9999
    except: pass
    return (not c['aged'], p)
cands.sort(key=key)
for c in cands[:12]:
    print(f"{c['store']:12} {c['id']}  Bravo{c['bravo']:>10}  aged={c['aged']}  ${c['price']}  {c['orig']}")
print('coded total',len(cands),'aged+coded',sum(1 for c in cands if c['aged']))
