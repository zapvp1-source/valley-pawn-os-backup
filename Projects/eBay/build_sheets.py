import json,urllib.request,os,sys
from PIL import Image,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor
store=sys.argv[1]
d=json.load(open(f"{store}_photos.json"))
base=f"photorev/{store}"; os.makedirs(base+"/thumbs",exist_ok=True)
try: F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",15); Fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
except: F=ImageFont.load_default(); Fs=F
def grab(ix):
    i,x=ix
    if not x['pics']: return
    try:
        req=urllib.request.Request(x['pics'][0],headers={'User-Agent':'Mozilla/5.0'})
        open(f"{base}/thumbs/{i:03d}.jpg","wb").write(urllib.request.urlopen(req,timeout=30).read())
    except: pass
list(ThreadPoolExecutor(max_workers=12).map(grab,list(enumerate(d))))
TH=210;PADX=12;LBL=34;CW=TH+PADX;CH=TH+LBL+20;COLS=6;ROWS=4;PER=COLS*ROWS
def cell(i,x):
    c=Image.new("RGB",(CW,CH),(255,255,255));dr=ImageDraw.Draw(c)
    try:
        im=Image.open(f"{base}/thumbs/{i:03d}.jpg").convert("RGB");im.thumbnail((TH,TH))
        c.paste(im,((TH-im.width)//2+PADX//2,(TH-im.height)//2+LBL))
    except: dr.text((10,LBL+80),"no img",fill=(200,0,0),font=F)
    dr.rectangle([0,0,54,26],fill=(20,20,20));dr.text((6,4),f"#{i}",fill=(255,255,255),font=F)
    dr.text((60,6),f"n={x['n']}",fill=(90,90,90),font=Fs)
    dr.text((4,TH+LBL+2),(x['title'] or '')[:38],fill=(0,0,0),font=Fs)
    return c
sheets=(len(d)+PER-1)//PER
for s in range(sheets):
    sh=Image.new("RGB",(CW*COLS,CH*ROWS),(245,245,245))
    for j in range(PER):
        idx=s*PER+j
        if idx>=len(d):break
        sh.paste(cell(idx,d[idx]),((j%COLS)*CW,(j//COLS)*CH))
    sh.save(f"{base}_sheet_{s+1}.png")
print(store,len(d),"items,",sheets,"sheets")
