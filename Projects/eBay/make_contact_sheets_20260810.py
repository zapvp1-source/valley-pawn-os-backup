#!/usr/bin/env python3
import json, os
from PIL import Image
base = os.path.expanduser('~/Documents/Claude/Projects/eBay')
rows = json.load(open(f'{base}/analysis_report.json'))
imgdir = f'{base}/primaries_20260810'
outdir = f'{base}/contact_sheets_20260810'
os.makedirs(outdir, exist_ok=True)
THUMB=220
COLS=5
items=[]
for r in rows:
    fn = f"{imgdir}/{r['store']}_{r['id']}.jpg"
    if os.path.exists(fn):
        items.append((r['store'], r['id'], fn))
# split into sheets of 20 (4 rows x 5 cols)
PER=20
for si in range(0, len(items), PER):
    chunk = items[si:si+PER]
    rows_n = (len(chunk)+COLS-1)//COLS
    sheet = Image.new('RGB', (COLS*THUMB, rows_n*(THUMB+22)), 'white')
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i,(store,iid,fn) in enumerate(chunk):
        try:
            im = Image.open(fn).convert('RGB')
            im.thumbnail((THUMB-10, THUMB-10))
            x = (i%COLS)*THUMB
            y = (i//COLS)*(THUMB+22)
            sheet.paste(im, (x+5, y+5))
            d.text((x+5, y+THUMB-2), f'{store[:4]} {iid}', fill='black')
        except Exception as e:
            print('skip', iid, e)
    outpath = f'{outdir}/sheet_{si//PER+1}.png'
    sheet.save(outpath)
    print('wrote', outpath)
