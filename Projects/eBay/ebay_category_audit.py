#!/usr/bin/env python3
"""Valley Pawn — full eBay category audit (all 5 stores). Flags listings whose current category
doesn't match eBay's Taxonomy suggestion. Writes mismatches to ~/ebay_category_mismatches.json."""
import base64,json,os,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, CERT_ID as CERT, DEV_ID as DEV  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")
def app_token():
    a=base64.b64encode(f"{APP}:{CERT}".encode()).decode()
    d=urllib.parse.urlencode({"grant_type":"client_credentials","scope":"https://api.ebay.com/oauth/api_scope"}).encode()
    return json.load(urlopen(Request("https://api.ebay.com/identity/v1/oauth2/token",data=d,headers={"Authorization":f"Basic {a}","Content-Type":"application/x-www-form-urlencoded"}),timeout=30))["access_token"]
def call(tok,name,inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>{inner}</{name}Request>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,"X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=60).read().decode())
def active(tok):
    out=[];page=1
    while True:
        r=call(tok,"GetMyeBaySelling",f"<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            out.append({"id":it.findtext(f"{{{NS}}}ItemID"),"title":it.findtext(f"{{{NS}}}Title") or "",
                        "cat_id":it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryID"),
                        "cat_name":it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryName"),
                        "url":it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}ViewItemURL") or ""})
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return out
def suggest(app_tok,q):
    url="https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions?"+urllib.parse.urlencode({"q":q[:300]})
    try:
        j=json.load(urlopen(Request(url,headers={"Authorization":f"Bearer {app_tok}"}),timeout=20))
        s=j["categorySuggestions"][0];cat=s["category"]
        path=" > ".join(a["categoryName"] for a in s.get("categoryTreeNodeAncestors",[])[::-1])
        return cat["categoryId"],cat["categoryName"],path
    except: return None,None,None
def main():
    at=app_token();mism=[];counts={}
    for s in stores():
        n=0;items=active(s["token"])
        for it in items:
            if not it["title"] or not it["cat_id"]: continue
            sid,sname,path=suggest(at,it["title"])
            if sid and sid!=it["cat_id"]:
                mism.append({"store":s["name"],**it,"sug_id":sid,"sug_name":sname,"sug_path":path});n+=1
        counts[s["name"]]=(len(items),n);print(f"{s['name']}: {len(items)} listings, {n} category mismatches",flush=True)
    json.dump(mism,open(os.path.expanduser("~/ebay_category_mismatches.json"),"w"),indent=2)
    print(f"TOTAL mismatches: {len(mism)}")
if __name__=="__main__": main()
