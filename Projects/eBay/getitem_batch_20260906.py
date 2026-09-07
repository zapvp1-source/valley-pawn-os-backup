#!/usr/bin/env python3
import subprocess, sys

ITEMS = [
    ('398162170503','Culpeper'),
    ('800335233860','Waynesboro'),
    ('385626892405','Harrisonburg'),
    ('800112196687','Harrisonburg'),
    ('800616885259','Harrisonburg'),
    ('800123750148','Harrisonburg'),
    ('157975512781','Lexington'),
    ('157840648182','Lexington'),
    ('157921257295','Lexington'),
    ('157488036886','Lexington'),
    ('158260878900','Lexington'),
    ('298312214008','Roanoke'),
    ('307077672852','Roanoke'),
    ('306413806292','Roanoke'),
    ('307104894147','Roanoke'),
    ('306861872975','Roanoke'),
    ('307164619925','Roanoke'),
    ('307000372642','Roanoke'),
]

for iid, store in ITEMS:
    print(f'=== {store} {iid} ===')
    r = subprocess.run(['/usr/bin/python3', 'getitem_detail.py', iid, store], capture_output=True, text=True, cwd='/Users/joshuadavis/Documents/Claude/Projects/eBay')
    print(r.stdout.strip())
    if r.returncode != 0:
        print('ERR:', r.stderr.strip()[:300])
