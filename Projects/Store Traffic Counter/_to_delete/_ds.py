import sys,types,json,random,os
for m in ('cv2','nest_stream','detector'):
    try: __import__(m)
    except Exception: sys.modules[m]=types.ModuleType(m)
import retrack as R, counter as C
s=sys.argv[1]; src=f'dets/{s}/2026-11-03.jsonl'; L=open(src).read().splitlines()
os.makedirs(f'dets/_ds{s}',exist_ok=True); o=[]
for keep in [1.0,0.8,0.65,0.5]:
    random.seed(1); open(f'dets/_ds{s}/k.jsonl','w').write('\n'.join(l for l in L if random.random()<keep))
    c=R.replay(f'_ds{s}','k',C.CFG[s]); o.append(f"keep{keep}:{sum(v['in'] for v in c.values())}/{sum(v['out'] for v in c.values())}")
print(s,' '.join(o))
