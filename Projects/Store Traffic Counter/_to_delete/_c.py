import sys,types
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s,d=sys.argv[1],sys.argv[2]; o=[]
for kv in [{}, {'cap':2.0}, {'min_hits':2}, {'max_age':5}]:
    c=R.replay(s,d,dict(C.CFG[s],**kv)); o.append(f"{kv}:{sum(v['in'] for v in c.values())}/{sum(v['out'] for v in c.values())}")
print(s,d,' '.join(o))
