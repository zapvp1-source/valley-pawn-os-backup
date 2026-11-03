#!/usr/bin/env python3
"""Deck stats (read-only): why customers call — intents from graded calls, Sep 21–Oct 31 2026, deduped by zoom_id."""
import json,glob,collections,sys
B=sys.argv[1] if len(sys.argv)>1 else "."
order=[('week_2026-10-26','review_native.json'),('week_2026-10-19','review_native.json'),('week_2026-10-12_regrade_rules20261025','review_native.json'),
       ('week_2026-10-12','review_native.json'),('week_2026-09-28','review_*.json'),('week_2026-09-21','review_batch*.json')]
seen={}
for w,pat in order:
    for f in sorted(glob.glob(f"{B}/{w}/{pat}")):
        for r in json.load(open(f)):
            k=r.get('zoom_id') or (w,r.get('call'))
            if k not in seen: seen[k]=r
R=list(seen.values())
def mmdd(r):
    t=r.get('time','');  # 'Mon 10/26 09:51 AM'
    p=t.split()
    return p[1] if len(p)>1 else ''
R=[r for r in R if mmdd(r) and mmdd(r)<'11/01' and mmdd(r)>='09/21']
print('graded rows',len(R)); print(collections.Counter(r.get('type') for r in R).most_common())
C=[r for r in R if r.get('type')=='customer' and r.get('dir')=='inbound']
print('inbound customer conversations',len(C))
I=collections.Counter(r.get('intent') for r in C)
for k,v in I.most_common(): print(f"{k:32s} {v:5d} {100*v/len(C):5.1f}%")
print('\nby month'); 
for m in ['09','10']:
    cm=[r for r in C if mmdd(r).startswith(m)]; ic=collections.Counter(r['intent'] for r in cm)
    print(m,len(cm),[(k,round(100*v/len(cm),1)) for k,v in ic.most_common(8)])
print('\nitem_availability categories'); A=[r for r in C if r['intent']=='item_availability_or_price']
print(collections.Counter(r.get('category') for r in A).most_common(15))
print('\nfirearm outcomes', collections.Counter(r.get('outcome') for r in C if r['intent']=='firearm').most_common(8))
print('\noutcomes all', collections.Counter(r.get('outcome') for r in C).most_common(15))
print('\nother summaries sample'); 
for r in [r for r in C if r['intent']=='other'][:25]: print('-',r['summary'][:140])
