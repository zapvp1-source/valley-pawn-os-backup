#!/usr/bin/env python3
"""Download full-res photos for audit candidates."""
import json, os, urllib.request, re

# Get max-size eBay image URL
def full_res(url):
    # Replace size suffix with largest available (_57 = ~1600px max)
    url = re.sub(r'\$_\d+\.JPG', '$_57.JPG', url)
    url = re.sub(r'\$_\d+\.PNG', '$_57.PNG', url)
    # Strip set_id
    url = re.sub(r'\?set_id=.*', '', url)
    return url

candidates = {
    'Culpeper': ['398154807459'],
    'Waynesboro': ['800041347268'],
    'Harrisonburg': ['800112196687', '800406852492'],
    'Lexington': ['157975456980', '157895971112', '157921257295', '158106446348'],
    'Roanoke': ['306356636151', '297455886815', '306413806292', '307085808658', '298262789130'],
}

base = '/Users/joshuadavis/Documents/Claude/Projects/eBay'
out_dir = '/tmp/verify'
os.makedirs(out_dir, exist_ok=True)

for store, ids in candidates.items():
    fname = os.path.join(base, f'{store}_photos.json')
    if not os.path.exists(fname):
        fname = os.path.join(base, f'{store.lower()}_photos.json')
    data = json.load(open(fname))
    for iid in ids:
        item = next((x for x in data if x['id'] == iid), None)
        if not item:
            print(f'NOT FOUND: {store} {iid}')
            continue
        item_dir = os.path.join(out_dir, f'{store}_{iid}')
        os.makedirs(item_dir, exist_ok=True)
        for i, url in enumerate(item['pics']):
            url_full = full_res(url)
            ext = 'jpg' if '.JPG' in url.upper() else 'png'
            out_path = os.path.join(item_dir, f'pic{i+1:02d}.{ext}')
            try:
                req = urllib.request.Request(url_full, headers={'User-Agent': 'Mozilla/5.0'})
                data_bytes = urllib.request.urlopen(req, timeout=30).read()
                open(out_path, 'wb').write(data_bytes)
                print(f'OK {store} {iid} pic{i+1}')
            except Exception as e:
                print(f'ERR {store} {iid} pic{i+1}: {e}')

print('DONE')
