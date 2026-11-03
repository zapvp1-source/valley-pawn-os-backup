import asyncio,json,sys,os,cv2,numpy as np,collections
import nest_stream as ns
s=sys.argv[1]; C=json.load(open('config.json'))[s]
out=os.path.expanduser(f'~/ov_{s}.jpg')
async def main():
    p=await ns.snapshot(C.get('store',s),C['camera'],out,15,40)
asyncio.run(main())
im=cv2.imread(out); im=cv2.resize(im,(640,360)); H,W=im.shape[:2]
G=collections.Counter()
for l in open(f'dets/{s}/2026-11-02.jsonl'):
    t,f=json.loads(l)
    for x,y in f: G[(int(x*64),int(y*36))]+=1
for (x,y),n in G.items():
    if n>=3: cv2.circle(im,(x*10+5,y*10+5),2,(0,255,0) if n<200 else (0,0,255),-1)
dz=C.get('door_zone')
if dz: cv2.rectangle(im,(int(max(dz.get('x_min',0),0)*W),int(dz['y_min']*H)),(int(min(dz['x_max'],1)*W),int(min(dz.get('y_max',1),1)*H)),(255,0,255),2)
for gx in range(1,10): cv2.putText(im,f'{gx/10:.1f}',(int(gx*W/10),12),0,0.35,(255,255,0),1); cv2.putText(im,f'{gx/10:.1f}',(2,int(gx*H/10)),0,0.35,(255,255,0),1)
cv2.imwrite(out,im,[cv2.IMWRITE_JPEG_QUALITY,45]); print(os.path.getsize(out))
