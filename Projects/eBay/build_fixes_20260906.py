#!/usr/bin/env python3
import json

base = '/Users/joshuadavis/Documents/Claude/Projects/eBay'
files = {
    'Harrisonburg': f'{base}/Harrisonburg_photos.json',
    'Lexington': f'{base}/Lexington_photos.json',
    'Roanoke': f'{base}/roanoke_photos.json',
}
byid = {}
for store, jf in files.items():
    for x in json.load(open(jf)):
        byid[x['id']] = (store, x['title'])

NEW = {
    '800616885259': 'SONY PS4 - PRO - SYSTEM w/ Controller - CUH-7015B - 1TB (VA5020375)',
    '800123750148': 'Novation Launchpad Pro USB Midi Controller for Ableton 64 Pads w/Case TESTED!',
    '157975512781': "BULOVA Lady's Wristwatch 98R234 Marine Star w/ Box",
    '157488036886': "Philip Stein Extreme Active Men's SS Watch Model 34-bor w/ Box & Papers",
    '158260878900': 'Samsung Galaxy Tab S9+ 5G 256GB SM-X818U 12.4" Graphite w/ S Pen – Verizon',
    '307077672852': 'Buck 498 Ergo Hunter Pro Fixed Blade Hunting Knife w/ Sheath & Gut Hook',
    '306413806292': 'Uncle Henry Schrade 897UH Premium Stockman 3-Blade Knife w/ Bonus Care Kit',
    '800112196687': 'Playground Plug & Play Retro Video Game Console 80+ Built-In Games',
}

fixes = {}
for iid, new in NEW.items():
    store, old = byid[iid]
    fixes[iid] = {'store': store, 'old': old, 'new': new}
    print(iid, store, len(new), 'chars ->', new)

json.dump(fixes, open(f'{base}/audit_fixes_20260906.json', 'w'), indent=2)
print('wrote audit_fixes_20260906.json')
