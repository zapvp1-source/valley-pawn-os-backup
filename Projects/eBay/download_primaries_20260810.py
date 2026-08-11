#!/usr/bin/env python3
import json, os, urllib.request
os.makedirs(os.path.expanduser('~/Documents/Claude/Projects/eBay/primaries_20260810'), exist_ok=True)
rows = json.load(open(os.path.expanduser('~/Documents/Claude/Projects/eBay/analysis_report.json')))
ok=0; fail=0
for r in rows:
    url = r.get('first_pic')
    if not url: continue
    fn = os.path.expanduser(f"~/Documents/Claude/Projects/eBay/primaries_20260810/{r['store']}_{r['id']}.jpg")
    try:
        urllib.request.urlretrieve(url, fn)
        ok+=1
    except Exception as e:
        fail+=1
        print('FAIL', r['id'], e)
print(f'downloaded {ok}, failed {fail}')
