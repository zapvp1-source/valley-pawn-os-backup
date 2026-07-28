#!/usr/bin/env python3
"""Extract photo URLs for audit candidates."""
import json, os

candidates = [
    ('Culpeper', '398154807459'),
    ('Waynesboro', '800041347268'),
    ('Harrisonburg', '800112196687'),
    ('Harrisonburg', '800406852492'),
    ('Lexington', '157975456980'),
    ('Lexington', '157895971112'),
    ('Lexington', '157921257295'),
    ('Lexington', '158106446348'),
    ('Roanoke', '306356636151'),
    ('Roanoke', '297455886815'),
    ('Roanoke', '306413806292'),
    ('Roanoke', '307085808658'),
    ('Roanoke', '298262789130'),
]

base = '/Users/joshuadavis/Documents/Claude/Projects/eBay'
for store, iid in candidates:
    fname = os.path.join(base, f'{store}_photos.json')
    if not os.path.exists(fname):
        fname = os.path.join(base, f'{store.lower()}_photos.json')
    data = json.load(open(fname))
    item = next((x for x in data if x['id'] == iid), None)
    if item:
        print(f'=== {store} {iid} ===')
        print(f'TITLE: {item["title"]}')
        for i, url in enumerate(item['pics']):
            print(f'  PIC{i+1}: {url}')
    else:
        print(f'=== {store} {iid} NOT FOUND ===')
