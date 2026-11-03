import sys,types
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]
for md,sp,ma,mh in [(0.12,0.3,3,3),(0.12,0,1.0,3),(0.12,0,1.5,2),(0.08,0,1.0,2),(0.12,0.3,3,2),(0.15,0.5,2,2)]:
    cfg=dict(C.CFG[s],max_dist=md,speed=sp,max_age=ma,min_hits=mh); c=R.replay(s,'2026-11-02',cfg)
    print(s,md,sp,ma,mh,sum(v['in'] for v in c.values()),sum(v['out'] for v in c.values()))
