import sys,types
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]; out=[]
for md,sp,ma in [(0.12,0.3,3),(0.12,0.5,4),(0.15,0.6,5),(0.2,0.8,6),(0.2,1.0,8)]:
    cfg=dict(C.CFG[s],max_dist=md,speed=sp,max_age=ma); c=R.replay(s,'2026-11-02',cfg)
    out.append(f"{md}/{sp}/{ma}:{sum(v['in'] for v in c.values())}/{sum(v['out'] for v in c.values())}")
print(s,' '.join(out))
