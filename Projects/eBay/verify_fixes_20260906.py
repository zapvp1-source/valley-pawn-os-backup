#!/usr/bin/env python3
import subprocess

ITEMS = [
    ('800616885259','Harrisonburg'),
    ('800123750148','Harrisonburg'),
    ('157975512781','Lexington'),
    ('157488036886','Lexington'),
    ('158260878900','Lexington'),
    ('307077672852','Roanoke'),
    ('306413806292','Roanoke'),
    ('800112196687','Harrisonburg'),
]
for iid, store in ITEMS:
    r = subprocess.run(['/usr/bin/python3', 'getitem_detail.py', iid, store], capture_output=True, text=True, cwd='/Users/joshuadavis/Documents/Claude/Projects/eBay')
    title_line = [l for l in r.stdout.splitlines() if l.startswith('Title:')]
    print(iid, store, '->', title_line[0] if title_line else 'NO TITLE FOUND', r.stderr[:200] if r.returncode else '')
