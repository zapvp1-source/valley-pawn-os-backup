import json,glob,re,sys
pat=re.compile(sys.argv[1],re.I)
only=sys.argv[2] if len(sys.argv)>2 else ''
def walk(o,p):
    if isinstance(o,dict):
        for k,v in o.items(): yield from walk(v,p+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from walk(v,p+'[%d]'%i)
    elif isinstance(o,str): yield p,o
for f in sorted(glob.glob('lessons/*/*.json')):
    if only and not re.search(only,f): continue
    d=json.load(open(f))
    for p,s in walk(d,''):
        if p.startswith('.sources') or p.startswith('.production_notes'): continue
        if pat.search(s): print(f[8:],p,'::',s)
