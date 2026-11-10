import sys,types,copy,json,itertools
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]; H='2026-11-09 12:00'; base=C.CFG[s]; res=[]
def run(cfg):
    c=R.replay(s,'2026-11-09',cfg); h=c.get(H,{'in':0,'out':0}); return h['in'],h['out'],sum(v['in'] for v in c.values()),sum(v['out'] for v in c.values())
print('base',run(base))
for pad,mh,cap,clear in itertools.product([0,0.05,0.1,0.15],[2,3],[0.25,0.4],[None,0.05]):
    cfg=copy.deepcopy(base); cfg['min_hits']=mh; cfg['cap']=cap
    if clear is not None and 'clear' in cfg: cfg['clear']=clear
    dz=cfg['door_zone']
    if pad:
        dz['x_min']=dz.get('x_min',-0.01)-pad; dz['x_max']+=pad; dz['y_min']-=pad; dz['y_max']=dz.get('y_max',1.01)+pad
        if 'line_x' in cfg: dz['x_max']=min(dz['x_max'],cfg['line_x']-0.01)
    print(pad,mh,cap,clear,run(cfg),flush=True)
