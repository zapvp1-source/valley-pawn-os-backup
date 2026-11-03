import json,sys,collections
s=sys.argv[1]; G=collections.Counter(); N=0
for l in open(f'dets/{s}/2026-11-02.jsonl'):
    t,f=json.loads(l); N+=1
    for x,y in f: G[(min(19,max(0,int(x*20))),min(9,max(0,int(y*10))))]+=1
mx=max(G.values()); ch=' .:-=+*#%@'
print(s,'frames',N,'max cell',mx, 'cols x=0..1 by .05, rows y by .1')
for r in range(10): print(f'{r/10:.1f} |'+''.join(ch[min(9,int(9*(G[(c,r)]/mx)**0.4))] for c in range(20))+'|')
print(json.dumps({k:v for k,v in __import__('counter').CFG[s].items() if k not in('hours','camera')}) if False else '')
