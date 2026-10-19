import json, collections as C, datetime as dt, sys
BASE='/sessions/festive-trusting-clarke/mnt/Projects/Call Analysis/week_2026-09-28/'
d=json.load(open(BASE+'call_history.json'))
ext={'802':'HAR','805':'HAR','803':'WAY','806':'WAY','807':'LEX','804':'LEX','808':'CUL','810':'CUL','809':'ROA','812':'ROA','813':'PRE'}
def et(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))-dt.timedelta(hours=4)
def store(r):
    e=r.get('callee_ext_number') if r['direction']=='inbound' else r.get('caller_ext_number')
    return ext.get(str(e),'?')
def other(r): return (r.get('caller_did_number') or r.get('caller_number')) if r['direction']=='inbound' else (r.get('callee_did_number') or r.get('callee_number'))
def hours(s,D):
    w=D.weekday()
    if w==6: return None
    sat5 = (w==5 and D>=dt.date(2026,10,3))
    if s=='CUL': return (10,17 if sat5 else 18)
    if s=='ROA':
        if w==2 and D<dt.date(2026,9,30): return None
        return (10,17 if sat5 else 18)
    if s=='WAY':
        if D>=dt.date(2026,10,14): return (10,17 if w==5 else 18)
        return None if w==2 else (10,18)
    if s in('HAR','LEX'): return None if w==2 else (10,18)
    return (10,18)
MISS={'no_answer','abandoned','voicemail','hang_up'}
for r in d: r['_t']=et(r['start_time']); r['_s']=store(r); r['_o']=other(r)
def open_(r):
    h=hours(r['_s'],r['_t'].date())
    return bool(h) and h[0]<=r['_t'].hour+r['_t'].minute/60<h[1]
def wk(t): return 1 if t.date()<=dt.date(2026,10,4) else 2 if t.date()<=dt.date(2026,10,11) else 3
S=C.defaultdict(C.Counter)
for r in d:
    s=S[(r['_s'],wk(r['_t']))]
    if r['direction']=='outbound': s['out']+=1; continue
    s['in']+=1
    if open_(r):
        s['in_open']+=1
        if r['call_result'] in MISS: s['miss_open']+=1
        else: s['ans']+=1; s['ans_secs']+=r['duration']
    else: s['closed']+=1
res=C.defaultdict(C.Counter); lags=C.defaultdict(list); unres=C.defaultdict(list)
for m in d:
    if m['direction']!='inbound' or m['call_result'] not in MISS or not open_(m): continue
    later=[r for r in d if r['_o']==m['_o'] and r['_t']>m['_t'] and r['_s'] in(m['_s'],'PRE')]
    cb=[r for r in later if r['direction']=='outbound']; ca=[r for r in later if r['direction']=='inbound' and r['call_result'] not in MISS]
    k=(m['_s'],wk(m['_t']))
    if cb: res[k]['cb']+=1; lags[m['_s']].append((min(r['_t'] for r in cb)-m['_t']).total_seconds()/60)
    elif ca: res[k]['again']+=1
    else: res[k]['never']+=1; unres[m['_s']].append(m)
out={}
for s in ['CUL','HAR','WAY','LEX','ROA','PRE']:
    for w in (1,2,3):
        x=S[(s,w)]; r=res[(s,w)]
        if not x: continue
        mo=x['miss_open']; io=x['in_open']
        print(s,w,'in',x['in'],'open',io,'miss',mo,f"{100*mo/io:.0f}%" if io else '','closed',x['closed'],'out',x['out'],'avgsec',round(x['ans_secs']/x['ans']) if x['ans'] else 0,'| cb',r['cb'],'again',r['again'],'never',r['never'])
        out[f'{s}{w}']=dict(x)|{'cb':r['cb'],'again':r['again'],'never':r['never']}
    L=sorted(lags[s])
    if L: print('  ',s,'median cb min',round(L[len(L)//2]),'n',len(L))
    print('  ',s,'never-reached callers',len({m['_o'] for m in unres[s]}))
T=C.Counter()
for k,v in S.items():
    if k[0]!='PRE': T.update(v)
print('TOTAL',dict(T), round(100*T['miss_open']/T['in_open'],1))
D=C.defaultdict(lambda:[0,0])
for r in d:
    if r['direction']=='inbound' and open_(r) and r['_s']!='PRE':
        k=(r['_t'].strftime('%a %m/%d'),r['_s']); D[k][0]+=1; D[k][1]+=r['call_result'] in MISS
print('worst days',sorted(D.items(),key=lambda kv:-kv[1][1])[:8])
json.dump(out,open(BASE+'stats.json','w'),indent=1)
