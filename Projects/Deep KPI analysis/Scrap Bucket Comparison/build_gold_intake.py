import csv, glob, re, os, json, sys
from collections import defaultdict
OUT="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"
# mounted path
import pathlib
OUT=str(pathlib.Path.home()/"mnt/Projects/Bravo Data Extraction/output")
rows=[]; seen=set()
for f in sorted(glob.glob(OUT+"/*_intake-detail.csv")):
    b=os.path.basename(f); m=re.match(r"(\d{4}-\d\d-\d\d)_to_(\d{4}-\d\d-\d\d)_([A-Z]{3})_",b)
    d1,d2,store=m.groups()
    with open(f,newline='',encoding='utf-8',errors='replace') as fh:
        r=csv.DictReader(fh)
        for row in r:
            key=(store,d1,d2,tuple((v or '').strip() for v in row.values()))
            if key in seen: continue
            seen.add(key)
            rows.append(dict(store=store,d1=d1,d2=d2,**{k.strip():(v or '').strip() for k,v in row.items() if k}))
KAR={'24':1.0,'22':0.9167,'18':0.75,'14':0.585,'10':0.417,'9':0.375}
out=[]
for r in rows:
    desc=r.get('Full Description',''); cat=r.get('Category','')
    blob=(cat+' '+desc).upper()
    amt=float(re.sub(r'[^\d.\-]','',r.get('Loan Amount','') or '0') or 0)
    if amt<=0: continue
    m=re.search(r'([\d.]+)\s*DWT',blob); dwt=float(m.group(1)) if m else None
    km=re.search(r'\b(24|22|18|14|10|9)\s*K\b',blob)
    k=km.group(1) if km else None
    is_gold = bool(km) or 'GOLD' in blob
    silver = bool(re.search(r'SILVER|STERLING|925',blob)) and not km
    if not is_gold or silver: continue
    if re.search(r'EAGLE|KRUGERRAND|MAPLE|BULLION|COIN|BAR\b',blob): continue
    stones = bool(re.search(r'STONE|DIAMOND|DIA\b|CTW|SAPPHIRE|RUBY|EMERALD|OPAL|PEARL',blob))
    out.append(dict(store=r['store'],date=r['d2'],month=r['d2'][:7],kind=r.get('Ticket Kind',''),assoc=r.get('Associate',''),
        category=cat,desc=desc,amt=amt,dwt=dwt,karat=k,purity=KAR.get(k),stones=int(stones),
        scrapcat=int('SCRAP' in cat.upper())))
with open(os.path.expanduser('~/scrapwork/gold_intake.csv'),'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(rows),'rows total;',len(out),'gold rows')
