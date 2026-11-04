import sys,types
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s,day=sys.argv[1],sys.argv[2]; out=[]
for cap in [2.0,0.35,0.25,0.18,0.12]:
    c=R.replay(s,day,dict(C.CFG[s],cap=cap)); out.append(f"cap{cap}:{sum(v['in'] for v in c.values())}/{sum(v['out'] for v in c.values())}")
print(s,day,' '.join(out))
