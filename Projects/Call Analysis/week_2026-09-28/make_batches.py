"""Build reading batches from transcripts. Global call numbers = chronological order over the whole
recordings index (stable regardless of which days are done). Usage: python3 make_batches.py <first_day> <last_day> <tag>"""
import json, glob, os, sys, datetime as dt
B='/sessions/festive-trusting-clarke/mnt/Projects/Call Analysis/week_2026-09-28/'
TX='/sessions/festive-trusting-clarke/mnt/Projects/Zoom Call Pipeline/out/transcripts/'
idx=json.load(open(B+'recordings_index.json'))
def et(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))-dt.timedelta(hours=4)
for r in idx: r['_t']=et(r['date_time'])
idx.sort(key=lambda r:r['_t'])
NAME={'UNK':'PRESTON'}
rows=[]
for n,r in enumerate(idx,1):
    r['n']=n
json.dump([{'n':r['n'],'id':r['id'],'time':r['_t'].strftime('%a %m/%d %I:%M %p'),'store':NAME.get(r['store'],r['store']),'dir':r['direction'],'dur':r['duration_s'],'other':'…'+str(r['other_number'] or '')[-4:]} for r in idx],open(B+'calls_index.json','w'))
a,b,tag=sys.argv[1],sys.argv[2],sys.argv[3]
files={os.path.basename(f)[:-5]:f for f in glob.glob(TX+'2026-*/*.json')}
sel=[r for r in idx if a<=r['date_time'][:10]<=b]
missing=[r['id'] for r in sel if r['id'] not in files]
print('selected',len(sel),'missing transcripts',len(missing))
os.makedirs(B+'batches',exist_ok=True)
size=48; k=0
for i in range(0,len(sel),size):
    k+=1
    with open(B+f'batches/{tag}_{k:02d}.txt','w') as f:
        for r in sel[i:i+size]:
            t=json.load(open(files[r['id']])) if r['id'] in files else {'transcript':'[NO TRANSCRIPT]','kind':'?'}
            f.write(f"=== CALL {r['n']} | {NAME.get(r['store'],r['store'])} | {r['_t'].strftime('%a %m/%d %I:%M %p')} | {r['direction']} | {r['duration_s']}s | {t.get('kind')} | other …{str(r['other_number'] or '')[-4:]} | zoom id {r['id']}\n{(t['transcript'] or '').strip()}\n\n")
print('batches',k)
