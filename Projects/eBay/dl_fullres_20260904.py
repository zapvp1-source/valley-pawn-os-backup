import json, os, urllib.request

candidates = {
 'Culpeper': ['398147130076','398155101901','398023637276','398250198969'],
 'Waynesboro': ['800471578856','800335233860','800508952161','800548737480'],
 'Harrisonburg': ['800145552197','800167632660','385626892405','800396466895','800396469929'],
 'Lexington': ['158230414385','157975837256'],
 'Roanoke': ['297718886438','306998407053'],
}

base = '/Users/joshuadavis/Documents/Claude/Projects/eBay'
outdir = f'{base}/audit/fullres'
os.makedirs(outdir, exist_ok=True)

for store, ids in candidates.items():
    data = json.load(open(f'{base}/{store}_photos.json'))
    byid = {d['id']: d for d in data}
    for iid in ids:
        d = byid.get(iid)
        if not d:
            print(f'MISSING {store} {iid}')
            continue
        for i, url in enumerate(d['pics']):
            fn = f'{outdir}/{store}_{iid}_{i}.jpg'
            try:
                req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
                data_bytes = urllib.request.urlopen(req, timeout=20).read()
                open(fn, 'wb').write(data_bytes)
            except Exception as e:
                print(f'FAIL {store} {iid} {i}: {e}')
        print(f'done {store} {iid} ({len(d["pics"])} pics) title={d["title"]}')
