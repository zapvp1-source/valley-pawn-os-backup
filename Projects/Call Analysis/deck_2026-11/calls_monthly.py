#!/usr/bin/env python3
"""Deck stats (read-only): inbound store calls by month/store from Call Analysis week_*/call_history.json."""
import json, collections, datetime as dt, sys
from zoneinfo import ZoneInfo
ET=ZoneInfo("America/New_York")
BASE=sys.argv[1] if len(sys.argv)>1 else "."
EXT={'805':'HAR','806':'WAY','812':'ROA','810':'CUL','804':'LEX'}
MISS={"no_answer","abandoned","overflowed","busy","voicemail","ring_timeout","missed","timeout","rejected"}
rows={}
for f in ['week_2026-09-09','week_2026-09-21','week_2026-09-28','week_2026-10-12','week_2026-10-19','week_2026-10-26']:
    for r in json.load(open(f"{BASE}/{f}/call_history.json")): rows[r['id']]=r
R=sorted(rows.values(),key=lambda r:r['start_time'])
def et(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(ET)
def openp(t,s):
    wd=t.weekday()
    days={'CUL':[0,1,2,3,4,5],'ROA':[0,1,2,3,4,5],'WAY':[0,1,3,4,5]+([2] if t.date()>=dt.date(2026,10,14) else []),'HAR':[0,1,3,4,5],'LEX':[0,1,3,4,5]}[s]
    if wd not in days: return False
    close=dt.time(17) if (wd==5 and s in('CUL','ROA','WAY')) else dt.time(18)
    return dt.time(10)<=t.time()<close
first=collections.defaultdict(lambda:None)
inb=[];outb=collections.defaultdict(list); answered_by_num=collections.defaultdict(list)
for r in R:
    t=et(r['start_time'])
    if r['direction']=='inbound' and r.get('connect_type')=='external' and str(r.get('callee_ext_number')) in EXT:
        s=EXT[str(r['callee_ext_number'])]; first[s]=first[s] or t.date()
        n=r.get('caller_did_number'); inb.append((t,s,n,r['call_result']))
        if r['call_result'] not in MISS: answered_by_num[n].append(t)
    elif r['direction']=='outbound' and r.get('connect_type')=='external':
        outb[r.get('callee_did_number')].append(t)
print("first call per queue:",dict(first))
def per(label,flt):
    A=collections.defaultdict(collections.Counter)
    for t,s,n,res in inb:
        if not flt(t): continue
        for k in (s,'ALL'):
            c=A[k]; c['in']+=1; m=res in MISS; c['miss']+=m
            o=openp(t,s); c['in_open']+=o; c['miss_open']+=(m and o)
            if m:
                # reached later: answered inbound from same number or outbound to same number within 24h
                ok=any(t<x<=t+dt.timedelta(hours=24) for x in answered_by_num[n]+outb.get(n,[]))
                c['miss_reached24']+=ok
    days=len({t.date() for t,s,n,res in inb if flt(t)})
    print(f"\n== {label}  (days with calls: {days})")
    for k in ['CUL','HAR','LEX','ROA','WAY','ALL']:
        c=A[k]
        if not c['in']: print(k,'no calls'); continue
        print(f"{k}: inbound {c['in']}, unanswered {c['miss']} ({100*c['miss']/c['in']:.1f}%); open-hrs inbound {c['in_open']}, missed while open {c['miss_open']} ({100*c['miss_open']/max(1,c['in_open']):.1f}%); missed reached within 24h {c['miss_reached24']} ({100*c['miss_reached24']/max(1,c['miss']):.0f}%)")
d=lambda a,b:(lambda t:a<=t.date()<=b)
per("Sep 9-23 (before missed-call text)",d(dt.date(2026,9,9),dt.date(2026,9,23)))
per("Sep 24-30",d(dt.date(2026,9,24),dt.date(2026,9,30)))
per("Sep 9-30",d(dt.date(2026,9,9),dt.date(2026,9,30)))
per("Oct 1-31",d(dt.date(2026,10,1),dt.date(2026,10,31)))
for a,b in [((9,9),(9,15)),((9,16),(9,22)),((9,23),(9,29)),((9,30),(10,6)),((10,7),(10,13)),((10,14),(10,20)),((10,21),(10,27)),((10,28),(10,31))]:
    pass
# weekly ALL
W=collections.defaultdict(collections.Counter)
for t,s,n,res in inb:
    wk=(t.date()-dt.timedelta(days=t.weekday())).isoformat()
    W[wk]['in']+=1; W[wk]['miss']+=res in MISS
    o=openp(t,s); W[wk]['io']+=o; W[wk]['mo']+=(o and res in MISS)
print("\nweekly ALL (Mon start): in, unanswered%, open in, missed-open%")
for k in sorted(W): c=W[k]; print(k,c['in'],f"{100*c['miss']/c['in']:.1f}%",c['io'],f"{100*c['mo']/max(1,c['io']):.1f}%")
