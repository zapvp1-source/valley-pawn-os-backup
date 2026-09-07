#!/usr/bin/env python3
"""Download full-res photos for this week's candidate items, keyed by store json."""
import json, os, urllib.request, time

CANDIDATES = {
    'Culpeper': ['398162170503'],
    'Waynesboro': ['800335233860'],
    'Harrisonburg': ['385626892405','800112196687','800616885259','800123750148'],
    'Lexington': ['157975512781','157840648182','157921257295','157488036886','158260878900'],
    'Roanoke': ['298312214008','307077672852','306413806292','307104894147','306861872975','307164619925','307000372642'],
}

base = '/Users/joshuadavis/Documents/Claude/Projects/eBay'
outdir = f'{base}/audit/fullres_20260906'
os.makedirs(outdir, exist_ok=True)

for store, ids in CANDIDATES.items():
    jf = f'{base}/{store}_photos.json' if store != 'Roanoke' else f'{base}/roanoke_photos.json'
    if not os.path.exists(jf):
        jf = f'{base}/{store.lower()}_photos.json'
    data = json.load(open(jf))
    by_id = {x['id']: x for x in data}
    for iid in ids:
        x = by_id.get(iid)
        if not x:
            print(f'NOT FOUND in {store} active listings: {iid}')
            continue
        pics = x.get('pics', [])
        print(f'{store} {iid}: {len(pics)} pics, title={x["title"]!r}')
        for pi, url in enumerate(pics):
            dest = f'{outdir}/{iid}_{pi}.jpg'
            if os.path.exists(dest):
                continue
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                d = urllib.request.urlopen(req, timeout=30).read()
                open(dest, 'wb').write(d)
            except Exception as e:
                print(f'  err p{pi}: {e}')
            time.sleep(0.05)

print('DONE')
