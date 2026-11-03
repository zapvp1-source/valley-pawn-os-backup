import sys,types,json,collections,math
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import counter as C
s=sys.argv[1]; cfg=C.CFG[s]; trk=C.Tracker(0.12,4,0.3); T=[]
for l in open(f'dets/{s}/2026-11-02.jsonl'):
    now,f=json.loads(l); trk.update([tuple(p) for p in f],now); T+=trk.expire(now)
T+=trk.expire(now,force=True)
L=[t for t in T if t['n']>=3 and math.dist(t['p0'],t['p'])>0.2]
print(s,'tracks',len(T),'long-travel',len(L))
for name,key in (('STARTS','p0'),('ENDS','p')):
    G=collections.Counter((min(19,max(0,int(t[key][0]*20))),min(9,max(0,int(t[key][1]*10)))) for t in L)
    print(name); 
    for r in range(10): print(f'{r/10:.1f} |'+''.join((str(min(9,G[(c,r)])) if G[(c,r)] else ' ') for c in range(20))+'|')
