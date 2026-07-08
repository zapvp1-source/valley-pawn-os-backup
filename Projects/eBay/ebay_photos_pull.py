#!/usr/bin/env python3
"""Pull active listings for ONE store with ALL picture URLs + count.
Usage: python3 ebay_photos_pull.py <StoreName> <outpath.json>
Writes [{id,title,cat_name,n,pics:[url,...],url}] """
import os,sys,json,time,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
for p in PATHS:
    if os.path.exists(p):
        ns={};exec(compile(open(p).read(),p,"exec"),ns);STORES=ns["STORES"];break
store=sys.argv[1]; out=sys.argv[2]
tok=[s["token"] for s in STORES if s["name"]==store][0]
def hdr(name): return {"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,"X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
# 1) active item ids
ids=[];page=1
while True:
    body=(f'<?xml version="1.0" encoding="utf-8"?><GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList></GetMyeBaySellingRequest>').encode()
    r=ET.fromstring(urlopen(Request(URL,data=body,headers=hdr("GetMyeBaySelling")),timeout=60).read().decode())
    for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
        ids.append(it.findtext(f"{{{NS}}}ItemID"))
    tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
    try:tp=int(tp)
    except:tp=page
    if page>=tp:break
    page+=1
print(len(ids),"active items",flush=True)
# 2) per item pictures
data=[]
for i,iid in enumerate(ids):
    body=(f'<?xml version="1.0" encoding="utf-8"?><GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ItemID>{iid}</ItemID><DetailLevel>ItemReturnAttributes</DetailLevel></GetItemRequest>').encode()
    try:
        r=ET.fromstring(urlopen(Request(URL,data=body,headers=hdr("GetItem")),timeout=60).read().decode())
    except Exception as e:
        print("err",iid,e,flush=True);continue
    it=r.find(f".//{{{NS}}}Item")
    if it is None: continue
    pics=[p.text for p in it.findall(f".//{{{NS}}}PictureDetails/{{{NS}}}PictureURL")]
    data.append({"id":iid,"title":it.findtext(f"{{{NS}}}Title") or "",
                 "cat_name":it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryName"),
                 "n":len(pics),"pics":pics,
                 "url":it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}ViewItemURL") or ""})
    if (i+1)%25==0: print(i+1,"/",len(ids),flush=True)
    time.sleep(0.15)
json.dump(data,open(out,"w"),indent=2)
print("wrote",len(data),"to",out)
