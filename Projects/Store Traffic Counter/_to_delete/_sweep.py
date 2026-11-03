import sys,types,json,itertools
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]; base=dict(C.CFG[s])
def tot(c): i=sum(v['in'] for v in c.values()); o=sum(v['out'] for v in c.values()); return i,o
print(s,'base',tot(R.replay(s,'2026-11-02',base)))
for md,sp,ma in itertools.product([0.08,0.12,0.18],[0.15,0.3,0.6],[2,4,8]):
    cfg=dict(base,max_dist=md,speed=sp,max_age=ma); print(md,sp,ma,tot(R.replay(s,'2026-11-02',cfg)))
