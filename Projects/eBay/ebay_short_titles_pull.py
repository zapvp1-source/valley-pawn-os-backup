#!/usr/bin/env python3
"""Refresh ~/ebay_short_titles.json with current active eBay titles under 50 chars, all 5 stores."""
import os,json,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
for p in PATHS:
    if os.path.exists(p):
        ns={};exec(compile(open(p).read(),p,"exec"),ns);STORES=ns["STORES"];break
def call(tok,inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>{inner}</GetMyeBaySellingRequest>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"GetMyeBaySelling","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=60).read().decode())
short=[]
for s in STORES:
    page=1
    while True:
        r=call(s["token"],f"<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            t=it.findtext(f"{{{NS}}}Title") or ""
            if len(t)<50:
                short.append({"store":s["name"],"id":it.findtext(f"{{{NS}}}ItemID"),"title":t,"len":len(t),"price":it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice")})
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:tp=int(tp)
        except:tp=page
        if page>=tp:break
        page+=1
json.dump(short,open(os.path.expanduser("~/ebay_short_titles.json"),"w"),indent=2)
print(len(short),"short titles written")
