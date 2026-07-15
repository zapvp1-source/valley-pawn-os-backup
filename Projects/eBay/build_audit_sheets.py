#!/usr/bin/env python3
"""Build title-vs-photo audit sheets for ONE store.
Each listing = one horizontal strip: [id + title] then its photos left-to-right.
6 listings per sheet. Usage: build_audit_sheets.py <Store>"""
import json,os,sys,urllib.request
from PIL import Image,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor
store=sys.argv[1]
base=f"audit/{store}"; os.makedirs(base+"/thumbs",exist_ok=True)
d=json.load(open(f"{store}_photos.json"))
try:
    F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",15)
    Fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",13)
except: F=Fs=ImageFont.load_default()
def dl(a):
    li,pi,u=a
    try: open(f"{base}/thumbs/{li}_{pi}.jpg","wb").write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read())
    except: pass
jobs=[]
for li,x in enumerate(d):
    for pi,u in enumerate(x['pics'][:6]): jobs.append((li,pi,u))
list(ThreadPoolExecutor(max_workers=16).map(dl,jobs))
TH=150; LBL=22; PERSHEET=6; COLS=6
STRIP_W=COLS*(TH+4)+8; STRIP_H=TH+LBL+6
def strip(li,x):
    s=Image.new("RGB",(STRIP_W,STRIP_H),(255,255,255)); dr=ImageDraw.Draw(s)
    dr.text((4,3),f"#{li}  id={x['id']}  n={x['n']}  |  {x['title'][:88]}",fill=(0,0,0),font=Fs)
    for pi in range(min(len(x['pics']),6)):
        try:
            im=Image.open(f"{base}/thumbs/{li}_{pi}.jpg").convert("RGB"); im.thumbnail((TH,TH))
            s.paste(im,(pi*(TH+4)+4+(TH-im.width)//2, LBL+(TH-im.height)//2))
        except: pass
    dr.line([(0,STRIP_H-1),(STRIP_W,STRIP_H-1)],fill=(210,210,210))
    return s
nsheets=(len(d)+PERSHEET-1)//PERSHEET
for sh in range(nsheets):
    sheet=Image.new("RGB",(STRIP_W,STRIP_H*PERSHEET),(255,255,255))
    for j in range(PERSHEET):
        li=sh*PERSHEET+j
        if li>=len(d): break
        sheet.paste(strip(li,d[li]),(0,j*STRIP_H))
    sheet.save(f"{base}_sheet_{sh+1:02d}.png")
print(store,len(d),"listings,",nsheets,"sheets")
