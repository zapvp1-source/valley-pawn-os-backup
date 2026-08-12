#!/usr/bin/env python3
"""Rebuild the FFL Transfer monthly trend from the raw Bravo pull CSVs and upsert
every COMPLETE month (all 5 stores present) into the Google Drive trend sheet
IN PLACE, keyed by Month (text). Idempotent — safe to run any time.
Run with /usr/bin/python3 (has the Google libs + cached OAuth via sheets_helper).
"""
import sys, os, csv, re, calendar
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient

SHEET_ID = '1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs'   # Valley Pawn - FFL Transfer Trend (Monthly)
TAB      = 'Monthly'
OUT      = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output'
STORES   = ['WAY', 'CUL', 'HAR', 'LEX', 'ROA']

pat = re.compile(r'^(\d{4})-(\d{2})-01_to_\1-\2-(\d{2})_(WAY|CUL|HAR|LEX|ROA)_nics-transfers\.csv$')
data = {}   # (y,m) -> { store: (count, revenue) }
for fn in os.listdir(OUT):
    mo = pat.match(fn)
    if not mo:
        continue
    y, m, last, s = int(mo.group(1)), int(mo.group(2)), int(mo.group(3)), mo.group(4)
    if last != calendar.monthrange(y, m)[1]:
        continue   # only true full-month files
    rows = list(csv.reader(open(os.path.join(OUT, fn))))[1:]
    cnt = len(rows)
    rev = sum(float(x[8].replace('$', '').replace(',', '')) for x in rows if len(x) > 8 and x[8].strip())
    data.setdefault((y, m), {})[s] = (cnt, rev)

upserts = []
skipped = []
for (y, m) in sorted(data):
    d = data[(y, m)]
    if len(d) < 5:   # only upsert COMPLETE months (all 5 stores pulled)
        skipped.append(f'{y:04d}-{m:02d} (have {sorted(d)})')
        continue
    row = {'Month': f'{y:04d}-{m:02d}'}
    tc = 0; tr = 0.0
    for s in STORES:
        cnt, rev = d[s]
        row[f'{s} Transfers'] = cnt
        row[f'{s} Revenue'] = round(rev, 2)
        tc += cnt; tr += rev
    row['Total Transfers'] = tc
    row['Total Revenue'] = round(tr, 2)
    upserts.append(row)

c = SheetsClient()
res = c.upsert_by_key(SHEET_ID, TAB, 'Month', upserts) if upserts else {'updated': 0, 'appended': 0}
print(f'complete months upserted: {len(upserts)}  -> {res}')
if skipped:
    print('incomplete months skipped: ' + '; '.join(skipped))
