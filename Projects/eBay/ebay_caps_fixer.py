#!/usr/bin/env python3
"""Valley Pawn — convert ALL-CAPS eBay titles to proper Title Case (keeps model numbers/units). Reversible.
State: ~/ebay_caps_state.json { ItemID: {"before": title, "store": name} }
Usage: python3 ebay_caps_fixer.py <Store> [--apply|--revert]"""
import json, os, re, sys, xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request, urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=["/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py", os.path.expanduser("~/ebay_weekly_rankings.py")]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
STATE=os.path.expanduser("~/ebay_caps_state.json")
KEEP={"14K","18K","10K","925","1TB","2TB","500GB","256GB","128GB","USB","LED","LCD","HD","4K","OBD2","V1","V2"}
def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")
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
            out.append((it.findtext(f"{{{NS}}}ItemID"), it.findtext(f"{{{NS}}}Title") or ""))
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return out
def is_caps(t):
    letters=[c for c in t if c.isalpha()]
    return len(letters)>=4 and all(c.isupper() for c in letters) and len(t.split())>=2
def tc(t):
    out=[]
    for w in t.split():
        if w.upper() in KEEP or any(ch.isdigit() for ch in w) or "/" in w:
            out.append(w)
        else:
            out.append(w[:1].upper()+w[1:].lower())
    return " ".join(out)
def set_title(tok,iid,title):
    r=call(tok,"ReviseFixedPriceItem",f"<Item><ItemID>{iid}</ItemID><Title>{escape(title)}</Title></Item>")
    return r.findtext(f"{{{NS}}}Ack","") in ("Success","Warning"), (r.findtext(f".//{{{NS}}}ShortMessage") or "err")
def main():
    store=sys.argv[1];apply="--apply" in sys.argv;revert="--revert" in sys.argv
    tok=[s for s in stores() if s["name"].lower()==store.lower()][0]["token"]
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    if revert:
        n=0
        for iid,rec in list(state.items()):
            if rec.get("store","").lower()!=store.lower(): continue
            if apply: set_title(tok,iid,rec["before"])
            n+=1
        print(f"{store}: reverted {n}"+("" if apply else " (dry)"));return
    todo=[(iid,t,tc(t)) for iid,t in active(tok) if is_caps(t) and tc(t)!=t]
    print(f"{store}: {len(todo)} ALL-CAPS titles to fix")
    for iid,o,n in todo[:4]: print(f"  {o}  ->  {n}")
    if apply:
        done=fail=0
        for iid,o,n in todo:
            ok,err=set_title(tok,iid,n)
            if ok: state[iid]={"before":o,"store":store};done+=1
            else: fail+=1
        json.dump(state,open(STATE,"w"),indent=2)
        print(f"{store}: APPLIED {done}, failed {fail}")
    else: print(f"{store}: dry run.")
if __name__=="__main__": main()
