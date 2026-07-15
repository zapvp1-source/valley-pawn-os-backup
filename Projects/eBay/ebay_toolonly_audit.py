#!/usr/bin/env python3
"""Scan ACTIVE listings across all 5 stores for titles claiming 'Tool Only' / 'Bare' /
'Body Only' / 'No Battery' — the inclusion-mismatch set Preston flagged. READ-ONLY.
Writes ~/tool_only_candidates.json = [{store,id,title,n,pics:[...]}]"""
import os,re,json,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
ns={}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(),'x','exec'),ns)
STORES=ns['STORES']
import sys as _sys
_sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
PAT=re.compile(r'\b(tool only|bare tool|\(bare\)|body only|no battery|tool-only)\b',re.I)
def hdr(tok,name): return {"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,"X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
def active(tok):
    out=[];page=1
    while True:
        body=(f'<?xml version="1.0" encoding="utf-8"?><GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList></GetMyeBaySellingRequest>').encode()
        r=ET.fromstring(urlopen(Request(URL,data=body,headers=hdr(tok,"GetMyeBaySelling")),timeout=60).read().decode())
        if r.findtext(f"{{{NS}}}Ack","")=="Failure":
            print("  FAIL",r.findtext(f".//{{{NS}}}ShortMessage"));break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            out.append((it.findtext(f"{{{NS}}}ItemID"),it.findtext(f"{{{NS}}}Title") or ""))
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:tp=int(tp)
        except:tp=page
        if page>=tp:break
        page+=1
    return out
def pics(tok,iid):
    body=(f'<?xml version="1.0"?><GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ItemID>{iid}</ItemID><DetailLevel>ItemReturnAttributes</DetailLevel></GetItemRequest>').encode()
    r=ET.fromstring(urlopen(Request(URL,data=body,headers=hdr(tok,"GetItem")),timeout=60).read().decode())
    return [p.text for p in r.findall(f".//{{{NS}}}PictureDetails/{{{NS}}}PictureURL")]
cand=[]
for s in STORES:
    items=active(s['token']); hits=[(i,t) for i,t in items if PAT.search(t)]
    print(f"{s['name']}: {len(items)} active, {len(hits)} tool-only/bare")
    for iid,t in hits:
        cand.append({"store":s['name'],"id":iid,"title":t,"pics":pics(s['token'],iid)})
json.dump(cand,open(os.path.expanduser('~/tool_only_candidates.json'),'w'),indent=2)
print("TOTAL candidates:",len(cand))
