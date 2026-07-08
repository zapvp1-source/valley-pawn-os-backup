#!/usr/bin/env python3
"""Valley Pawn — strip internal intake codes (e.g. (VA1056309)) from eBay titles. Reversible.
State: ~/ebay_title_state.json { ItemID: {"original": title, "store": name} }
Usage: python3 ebay_title_stripper.py <Store> [--apply|--revert]"""
import json, os, re, sys, xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request, urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=["/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py", os.path.expanduser("~/ebay_weekly_rankings.py")]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
STATE=os.path.expanduser("~/ebay_title_state.json")
CODE=re.compile(r"\s*\((?:[A-Za-z]{1,4})?\d{3,}[A-Za-z]?\)\s*")
def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")
def call(tok,name,inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="urn:ebay:apis:eBLBaseComponents">'
     f'<RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>{inner}</{name}Request>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,"X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=60).read().decode())
def active(tok):
    out=[];page=1
    while True:
        r=call(tok,"GetMyeBaySelling",f"<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            out.append((it.findtext(f"{{{NS}}}ItemID"), it.findtext(f"{{{NS}}}Title") or ""))
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return out
def clean(t): return re.sub(r"\s{2,}"," ",CODE.sub(" ",t)).strip(" -")
def set_title(tok,iid,title):
    r=call(tok,"ReviseFixedPriceItem",f"<Item><ItemID>{iid}</ItemID><Title>{escape(title)}</Title></Item>")
    ack=r.findtext(f"{{{NS}}}Ack","")
    if ack in ("Success","Warning"): return True,None
    return False,(r.findtext(f".//{{{NS}}}ShortMessage") or "err")
def main():
    store=sys.argv[1]; apply="--apply" in sys.argv; revert="--revert" in sys.argv
    tok=[s for s in stores() if s["name"].lower()==store.lower()][0]["token"]
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    if revert:
        n=0
        for iid,rec in list(state.items()):
            if rec.get("store","").lower()!=store.lower(): continue
            ok,err=set_title(tok,iid,rec["original"]) if apply else (True,None)
            print(f"REVERT {iid}" + ("" if ok else f" ERR {err}")); n+=1
        print(f"{store}: reverted {n}" + ("" if apply else " (dry)")); return
    todo=[(iid,t,clean(t)) for iid,t in active(tok) if CODE.search(t) and clean(t) and clean(t)!=t and len(clean(t))<=80]
    print(f"{store}: {len(todo)} titles with intake codes to strip")
    for iid,old,new in todo[:5]: print(f"  {old}  ->  {new}")
    if apply:
        done=fail=0
        for iid,old,new in todo:
            ok,err=set_title(tok,iid,new)
            if ok: state[iid]={"original":old,"store":store}; done+=1
            else: fail+=1; print(f"  FAIL {iid}: {err}")
        json.dump(state,open(STATE,"w"),indent=2)
        print(f"{store}: APPLIED {done}, failed {fail}")
    else:
        print(f"{store}: dry run. Add --apply.")
if __name__=="__main__": main()
