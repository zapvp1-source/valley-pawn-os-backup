#!/usr/bin/env python3
"""Valley Pawn — eBay listing quality audit (title + category) for one store.
Flags weak titles and category mismatches. Writes JSON. Photos handled separately (vision)."""
import json, os, sys, re, xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=["/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py", os.path.expanduser("~/ebay_weekly_rankings.py")]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")
def call(token,name,inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="urn:ebay:apis:eBLBaseComponents">'
          f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>{inner}</{name}Request>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,"X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":token,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=60).read().decode())
def active(token):
    out=[];page=1
    while True:
        r=call(token,"GetMyeBaySelling",f"<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            out.append({"id":it.findtext(f"{{{NS}}}ItemID"),"title":it.findtext(f"{{{NS}}}Title") or "",
                        "cat_id":it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryID"),
                        "cat_name":it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryName"),
                        "price":it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice")})
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return out
def suggest_cat(token,title):
    q=re.sub(r"[<>&]"," ",title)[:350]
    r=call(token,"GetSuggestedCategories",f"<Query>{q}</Query>")
    s=r.find(f".//{{{NS}}}SuggestedCategoryArray/{{{NS}}}SuggestedCategory")
    if s is None: return None,None
    return s.findtext(f".//{{{NS}}}CategoryID"), s.findtext(f".//{{{NS}}}CategoryName")
def title_flags(t):
    f=[]
    n=len(t)
    if n<40: f.append(f"short({n}/80)")
    if re.search(r"\([A-Z]{2,4}\d{3,}\)", t): f.append("has_intake_code")   # e.g. (ROA008189) — internal, wastes chars
    if t.isupper(): f.append("all_caps")
    if not re.search(r"\d", t) and n<55: f.append("no_specs")
    return f
def main():
    store=sys.argv[1]
    tok=[s for s in stores() if s["name"].lower()==store.lower()][0]["token"]
    items=active(tok)
    rows=[]
    for it in items:
        sid,sname=suggest_cat(tok,it["title"])
        mism = (sid and it["cat_id"] and sid!=it["cat_id"])
        rows.append({**it,"sug_cat_id":sid,"sug_cat_name":sname,"cat_mismatch":bool(mism),"title_flags":title_flags(it["title"]),"title_len":len(it["title"])})
    weak=[r for r in rows if r["title_flags"]]; mis=[r for r in rows if r["cat_mismatch"]]
    print(f"{store}: {len(rows)} listings | {len(weak)} weak titles | {len(mis)} category mismatches")
    json.dump(rows,open(f"/sessions/fervent-admiring-noether/mnt/outputs/audit_{store}.json","w"),indent=2)
if __name__=="__main__": main()
