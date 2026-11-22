import json,sys
for f in sys.argv[1:]:
    d=json.load(open(f))
    print('=====',f,'|',d['title'],'| floor:',d.get('floor_check'),'| gate:',d.get('gate'))
    print('OBJ:',d.get('objectives'))
    print('CLIP:',json.dumps(d.get('call_clip'),ensure_ascii=False))
    for i,s in enumerate(d['slides']):
        print('S%d H: %s'%(i,s['heading']))
        for j,b in enumerate(s['bullets']): print('  b%d: %s'%(j,b))
        print('  SAY:',s['say'])
    for i,k in enumerate(d['key_points']): print('K%d: %s'%(i,k))
    for i,q in enumerate(d['quiz']['questions']):
        print('Q%d [%s] %s'%(i,q['type'],q['prompt']))
        for j,o in enumerate(q['options']): print('   o%d %s %s || %s'%(j,'*' if o['correct'] else '-',o['text'],o['why']))
