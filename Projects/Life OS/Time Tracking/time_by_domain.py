#!/usr/bin/env python3
"""Work-share by domain (Valley Pawn / Real Estate / Personal) from dated work records.
Sources: Life OS/OPEN_ITEMS_REGISTER.md + OPEN_ITEMS_ARCHIVE.md (every session logs a row, Rule 14)
and the Real Estate claude.ai project docs (re_project_docs.txt, dated filenames).
Re-run any time: python3 time_by_domain.py  -> writes report.md + items.csv beside this script."""
import re, csv, os, collections, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); LIFE=os.path.dirname(HERE)
START=dt.date(2026,8,7)
VP,RE,PE,SH,CL='Valley Pawn','Real Estate','Personal','Shared / all-domain','Client sites (side work)'
def classify(dom,item):
    d=dom.lower().strip(); t=(dom+' '+item).lower()
    if 'cypress' in d: return PE                      # primary residence = personal
    if re.match(r'^(all|1/2/3|1 & 2|1\+2|domain 1 ?[+/&] ?2|domain 1 \+ 2)',d) or 'all domain' in d or 'all 3' in d: return SH
    if re.match(r'^4\b',d) or 'client site' in d or 'solaterra' in t: return CL
    if 'pawn' in d or re.match(r'^(d?1\b|domain 1|vp\b|valley)',d): return VP
    if re.match(r'^(d?2\b|domain 2|real estate)',d) or any(k in d for k in('bald rock','richmond','woods walk','hardinberry')): return RE
    if re.match(r'^(d?3\b|domain 3|personal)',d): return PE
    if 'cypress' in t and not re.match(r'^(d?[12]\b|domain [12]|valley|real estate)',d): return PE
    for k,v in (('compass.com',RE),('bald rock',RE),('airbnb',RE),('woods walk',RE),('hardinberry',RE),('817 richmond',RE),
                ('health',PE),('hillary',PE),('1040',PE),('bravo',VP),('store',VP),('gusto',VP),('preston',VP),('ffl',VP),('ebay',VP)):
        if k in t: return v
    return VP if ('insurance' not in t and 'reminder' not in t) else SH
rows={}
for fn in('OPEN_ITEMS_REGISTER.md','OPEN_ITEMS_ARCHIVE.md'):
    for l in open(os.path.join(LIFE,fn),encoding='utf-8',errors='ignore'):
        if not l.startswith('|'): continue
        c=[x.strip() for x in l.split('|')]
        if len(c)<4: continue
        m=re.match(r'(\d{4}-\d{2}-\d{2})',c[1])
        if not m: continue
        d=dt.date.fromisoformat(m.group(1))
        if d<START or d>dt.date.today(): continue
        key=(d,re.sub(r'\W+','',c[3].lower())[:80])
        rows.setdefault(key,(d,classify(c[2],c[3]),'register',c[2][:60],re.sub(r'\s+',' ',c[3])[:160]))
for n in open(os.path.join(HERE,'re_project_docs.txt')):
    n=n.strip(); m=re.search(r'(\d{4}-\d{2}-\d{2})',n)
    if not m: continue
    d=dt.date.fromisoformat(m.group(1))
    if d<START: continue
    rows[(d,n)]=(d,PE if 'CYPRESS' in n or 'HALLCO' in n else RE,'RE project doc','Real Estate project',n)
items=sorted(rows.values())
with open(os.path.join(HERE,'items.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['date','domain','source','domain_tag','item']); w.writerows(items)
order=[VP,RE,PE,SH,CL]
cnt=collections.Counter(i[1] for i in items)
days={k:len({i[0] for i in items if i[1]==k}) for k in order}
tot=sum(cnt[k] for k in order)
core=sum(cnt[k] for k in (VP,RE,PE))
def wk(d): return d-dt.timedelta(days=d.weekday())
weeks=sorted({wk(i[0]) for i in items})
wc=collections.defaultdict(collections.Counter)
for i in items: wc[wk(i[0])][i[1]]+=1
L=[f"# Work by Domain — {START:%b %-d} to {dt.date.today():%b %-d, %Y}\n",
   f"Generated {dt.datetime.now():%Y-%m-%d %H:%M}. Unit = logged work items (one per thing drafted, sent, built or decided).\n",
   "| Domain | Work items | Share of all | Share of the 3 businesses | Active days |","|---|---:|---:|---:|---:|"]
for k in order:
    L.append(f"| {k} | {cnt[k]} | {cnt[k]/tot:.0%} | {(cnt[k]/core if k in(VP,RE,PE) else 0):.0%}{'' if k in(VP,RE,PE) else ' (n/a)'} | {days[k]} |")
L.append(f"| **Total** | **{tot}** | 100% | | |\n")
L+=["## By week (Mon start)","","| Week of | Valley Pawn | Real Estate | Personal | Shared | Client |","|---|---:|---:|---:|---:|---:|"]
for w in weeks: L.append(f"| {w:%b %-d} | "+" | ".join(str(wc[w][k]) for k in order)+" |")
open(os.path.join(HERE,'report.md'),'w').write('\n'.join(L)+'\n')
print('\n'.join(L))
