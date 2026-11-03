import sys,types,json
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]; base=dict(C.CFG[s]); Z=json.loads(sys.argv[2])
for z in Z:
    cfg=dict(base); cfg['door_zone']=z[0]; cfg['clear']=z[1]; cfg.pop('line_x',None)
    c=R.replay(s,'2026-11-02',cfg); i=sum(v['in'] for v in c.values()); o=sum(v['out'] for v in c.values())
    print(z,i,o)
