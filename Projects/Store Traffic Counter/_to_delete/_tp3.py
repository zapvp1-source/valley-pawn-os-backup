import sys,types,copy
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]; out=[]
for mh,pad in [(3,0),(2,0),(2,0.05),(2,0.10)]:
    cfg=copy.deepcopy(C.CFG[s]); cfg['min_hits']=mh
    dz=cfg['door_zone']
    if pad:
        dz['x_min']=dz.get('x_min',-1)-pad; dz['x_max']+=pad; dz['y_min']-=pad; dz['y_max']=dz.get('y_max',1.01)+pad
        if 'line_x' in cfg: dz['x_max']=min(dz['x_max'],cfg['line_x']-0.01)
    c=R.replay(s,'2026-11-02',cfg); out.append(f"mh{mh}+{pad}:{sum(v['in'] for v in c.values())}/{sum(v['out'] for v in c.values())}")
print(s,' '.join(out))
