import json,sys
for f in sys.argv[1:]:
    d=json.load(open(f)); print('#####',f, d['id'], d['title'])
    for k in ('floor_check','objectives'): print(k.upper()+':',d.get(k))
    for i,s in enumerate(d['slides']):
        print('S%d H: %s'%(i,s['heading']))
        for j,b in enumerate(s['bullets']): print('  b%d %s'%(j,b))
        print('  SAY:',s['say'])
        for k in s:
            if k not in('heading','bullets','say'): print('  ',k,':',s[k])
    print('CLIP:',json.dumps(d.get('call_clip'),ensure_ascii=False))
    for i,k in enumerate(d['key_points']): print('K%d %s'%(i,k))
    q=d['quiz']; print('QUIZ',{k:v for k,v in q.items() if k!='questions'})
    for i,x in enumerate(q['questions']):
        print('Q%d [%s]%s %s'%(i,x['type'],' G' if x.get('goldilocks') else '',x['prompt']))
        for j,o in enumerate(x['options']): print('  %s%d %s || %s'%('*' if o['correct'] else ' ',j,o['text'],o['why']))
    print('OTHERKEYS',[k for k in d if k not in('id','level','order','title','minutes','gate','floor_check','sources','objectives','video','slides','call_clip','key_points','quiz')])
