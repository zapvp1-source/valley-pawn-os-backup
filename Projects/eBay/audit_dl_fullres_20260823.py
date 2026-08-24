#!/usr/bin/env python3
import json, os, urllib.request, time

BASE = '/Users/joshuadavis/Documents/Claude/Projects/eBay'
OUT = f'{BASE}/audit/fullres2'
os.makedirs(OUT, exist_ok=True)

candidates = {
  'Culpeper': ['397528400544','395614189847','397531548727','398106381642','398235942443','398136410699','398140133321','397469858498','395523114047','397292871304','398204785291'],
  'Waynesboro': ['800287909011','800471578856','800321499390','800335233860','800548737480'],
  'Harrisonburg': ['800232060996','800406845611','389431352189','800112196687','389708768130','800493301543','385626892405','800384051061','800055373631'],
  'Lexington': ['157840648182','157921257295','158029621799','158030380480'],
  'Roanoke': ['306413806292','306861872975','298565157505','306926372024','307000372642','298235812990','307077675069'],
}

total=0; done=0
for store, ids in candidates.items():
    data = json.load(open(f'{BASE}/{store}_photos.json'))
    by_id = {d['id']: d for d in data}
    for iid in ids:
        rec = by_id.get(iid)
        if not rec:
            print(f'MISSING {store} {iid}')
            continue
        for pi, url in enumerate(rec.get('pics', [])[:10]):
            total += 1
            dest = f'{OUT}/{store}_{iid}_{pi}.jpg'
            if os.path.exists(dest):
                done += 1; continue
            try:
                req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
                d = urllib.request.urlopen(req, timeout=30).read()
                open(dest,'wb').write(d)
                done += 1
            except Exception as e:
                print(f'ERR {store} {iid} p{pi}: {e}')
            time.sleep(0.05)
print(f'done {done}/{total} into {OUT}')
