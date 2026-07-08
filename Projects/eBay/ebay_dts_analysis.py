#!/usr/bin/env python3
"""Days-to-sell + sell-through-by-age analysis across all 5 Valley Pawn eBay stores.
Outputs JSON: days-to-sell distribution for recent sales, cumulative % sold by age,
active-listing age distribution, and cohort sell-through by listing-age band."""
import json, os, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID, DEV_ID, CERT_ID  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=["/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py", os.path.expanduser("~/ebay_weekly_rankings.py")]
NS="urn:ebay:apis:eBLBaseComponents"; URL="https://api.ebay.com/ws/api.dll"

def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={}; exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")

def post(token,call,inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><{call}Request xmlns="urn:ebay:apis:eBLBaseComponents">'
          f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>{inner}</{call}Request>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":call,
       "X-EBAY-API-APP-NAME":APP_ID,"X-EBAY-API-DEV-NAME":DEV_ID,"X-EBAY-API-CERT-NAME":CERT_ID,
       "X-EBAY-API-IAF-TOKEN":token,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=120).read().decode())

def pdt(s):
    for f in ("%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.strptime(s,f).replace(tzinfo=timezone.utc)
        except: pass
    return None

def iso(d): return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def sold_events(token,frm,to):
    ev=[]; page=1
    while True:
        r=post(token,"GetOrders",f"<CreateTimeFrom>{iso(frm)}</CreateTimeFrom><CreateTimeTo>{iso(to)}</CreateTimeTo><OrderStatus>Completed</OrderStatus><Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for o in r.findall(f".//{{{NS}}}Order"):
            paid=pdt(o.findtext(f".//{{{NS}}}PaidTime") or "") or pdt(o.findtext(f".//{{{NS}}}CreatedTime") or "")
            for t in o.findall(f".//{{{NS}}}TransactionArray/{{{NS}}}Transaction"):
                iid=t.findtext(f".//{{{NS}}}Item/{{{NS}}}ItemID"); sa=pdt(t.findtext(f"{{{NS}}}CreatedDate") or "") or paid
                if iid and sa: ev.append((iid,sa))
        if r.findtext(f".//{{{NS}}}HasMoreOrders","false").strip().lower()=="true": page+=1
        else: break
    return ev

def start_map(token,frm,to):
    m={}; page=1
    while True:
        r=post(token,"GetSellerList",f"<StartTimeFrom>{iso(frm)}</StartTimeFrom><StartTimeTo>{iso(to)}</StartTimeTo><GranularityLevel>Coarse</GranularityLevel><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ItemArray/{{{NS}}}Item"):
            iid=it.findtext(f"{{{NS}}}ItemID"); st=pdt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime") or "")
            if iid and st: m[iid]=st
        tp=r.findtext(f".//{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return m

def active_ages(token,now):
    ages=[]; page=1
    while True:
        r=post(token,"GetMyeBaySelling",f"<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            st=pdt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime") or "")
            if st: ages.append((now-st).days)
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return ages

import sys
now=datetime.now(timezone.utc)
target=sys.argv[1] if len(sys.argv)>1 else None
if target:  # per-store mode: write a part file and exit
    s=[x for x in stores() if x["name"].lower()==target.lower()][0]
    tok=s["token"]; d_list=[]; ages=[]
    sm={}
    for a,b in [(0,100),(100,200),(200,300)]:  # stack 100-day windows (GetSellerList caps at 120d)
        sm.update(start_map(tok, now-timedelta(days=b), now-timedelta(days=a)))
    for iid,sa in sold_events(tok, now-timedelta(days=90), now):  # GetOrders caps at 90d
        st=sm.get(iid)
        if st:
            dd=(sa-st).days
            if dd>=0: d_list.append(dd)
    ages=active_ages(tok, now)
    json.dump({"dts":d_list,"ages":ages}, open(f"/sessions/fervent-admiring-noether/mnt/outputs/part_{s['name']}.json","w"))
    print(f"{s['name']}: {len(d_list)} sold-with-date, {len(ages)} active")
    sys.exit()
dts=[]            # days-to-sell for recent sales
active=[]         # ages of currently active listings
import glob
for pf in glob.glob("/sessions/fervent-admiring-noether/mnt/outputs/part_*.json"):
    p=json.load(open(pf)); dts+=p["dts"]; active+=p["ages"]

def buckets(vals,edges):
    out=[];
    for i in range(len(edges)-1):
        lo,hi=edges[i],edges[i+1]; out.append(sum(1 for v in vals if lo<=v<hi))
    out.append(sum(1 for v in vals if v>=edges[-1]))
    return out

edges=[0,4,8,15,31,61,91,181]
dts_b=buckets(dts,edges); act_b=buckets(active,edges)
n=len(dts) or 1
cum=[]; run=0
labels=["0-3","4-7","8-14","15-30","31-60","61-90","91-180","180+"]
for i,c in enumerate(dts_b):
    run+=c; cum.append(round(100*run/n,1))
res={
 "sold_n":len(dts),"active_n":len(active),
 "dts_median": sorted(dts)[len(dts)//2] if dts else None,
 "labels":labels,
 "days_to_sell_counts":dts_b,
 "days_to_sell_cum_pct":cum,
 "active_age_counts":act_b,
 "pct_sales_within_7": round(100*sum(dts_b[:2])/n,1),
 "pct_sales_within_14": round(100*sum(dts_b[:3])/n,1),
 "pct_sales_within_30": round(100*sum(dts_b[:4])/n,1),
 "pct_sales_within_60": round(100*sum(dts_b[:5])/n,1),
 "pct_sales_after_90": round(100*sum(dts_b[6:])/n,1),
 "active_pct_over_90": round(100*sum(act_b[6:])/(len(active) or 1),1),
}
json.dump(res, open("/sessions/fervent-admiring-noether/mnt/outputs/dts_analysis.json","w"), indent=2)
print("DONE", json.dumps(res))
