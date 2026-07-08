#!/usr/bin/env python3
"""
Valley Pawn — eBay Auto-Markdown Engine (all 5 stores)
Rule: every listing 90+ days old gets 10% off; then 10% more each subsequent run;
STOP at 30% off the baseline (max 3 cuts). No cost data needed — the 30% cap is the floor.

State: ~/ebay_markdown_state.json  { ItemID: {"baseline": price_at_first_cut, "cuts": n, "last": "YYYY-MM-DD", "store": name} }

Usage:
  python3 ebay_markdown_engine.py <Store>            # DRY RUN (prints proposed changes, no changes made)
  python3 ebay_markdown_engine.py <Store> --apply    # applies via ReviseFixedPriceItem
  python3 ebay_markdown_engine.py <Store> --revert    # restores every touched item to its baseline
"""
import json, os, sys, datetime, xml.etree.ElementTree as ET
from datetime import timezone
from urllib.request import Request, urlopen

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=["/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py", os.path.expanduser("~/ebay_weekly_rankings.py")]
NS="urn:ebay:apis:eBLBaseComponents"; URL="https://api.ebay.com/ws/api.dll"
STATE=os.path.expanduser("~/ebay_markdown_state.json")
AGED_DAYS=90; STEP=0.10; MAX_CUTS=3  # 10% per cut, cap at 30% off baseline

def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")

def call(token, name, inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="urn:ebay:apis:eBLBaseComponents">'
          f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>{inner}</{name}Request>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,
       "X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":token,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=60).read().decode())

def pdt(s):
    for f in ("%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.datetime.strptime(s,f).replace(tzinfo=timezone.utc)
        except: pass
    return None

def active(token):
    out=[]; page=1
    while True:
        r=call(token,"GetMyeBaySelling",f"<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination></ActiveList>")
        if r.findtext(f"{{{NS}}}Ack","")=="Failure": break
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            st=pdt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime") or "")
            pr=it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice") or it.findtext(f".//{{{NS}}}BuyItNowPrice") or it.findtext(f".//{{{NS}}}StartPrice")
            if not st or pr is None: continue
            out.append({"id":it.findtext(f"{{{NS}}}ItemID"),"title":(it.findtext(f"{{{NS}}}Title") or "")[:55],
                        "price":float(pr),"age":(datetime.datetime.now(timezone.utc)-st).days})
        tp=r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp=int(tp)
        except: tp=page
        if page>=tp: break
        page+=1
    return out

def revise(token, item_id, new_price):
    r=call(token,"ReviseFixedPriceItem",f"<Item><ItemID>{item_id}</ItemID><StartPrice>{new_price:.2f}</StartPrice></Item>")
    ack=r.findtext(f"{{{NS}}}Ack","")
    if ack in ("Success","Warning"): return True,None
    msg=r.findtext(f".//{{{NS}}}ShortMessage") or "error"
    return False,msg

def main():
    store=sys.argv[1]; apply="--apply" in sys.argv; revert="--revert" in sys.argv
    tok=[s for s in stores() if s["name"].lower()==store.lower()][0]["token"]
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    today=datetime.date.today().isoformat()

    if revert:
        changed=0
        for iid,rec in list(state.items()):
            if rec.get("store","").lower()!=store.lower() or rec.get("cuts",0)==0: continue
            ok,err=revise(tok,iid,rec["baseline"]) if apply else (True,None)
            print(f"REVERT {iid} -> ${rec['baseline']:.2f}" + ("" if ok else f"  ERR {err}"))
            if apply and ok: rec["cuts"]=0
            changed+=1
        if apply: json.dump(state,open(STATE,"w"),indent=2)
        print(f"{store}: reverted {changed} items" + ("" if apply else "  (dry run)")); return

    items=active(tok)
    proposed=[]
    for it in items:
        if it["age"] < AGED_DAYS: continue
        rec=state.get(it["id"], {"baseline":it["price"],"cuts":0,"store":store})
        if rec["cuts"]>=MAX_CUTS: continue                     # already at 30% off, stop
        baseline=rec["baseline"]; next_cut=rec["cuts"]+1
        new=round(baseline*(1-STEP*next_cut),2)
        if new>=it["price"]-0.01: continue                     # no downward change (safety)
        proposed.append((it,rec,new,next_cut))

    tot_old=sum(it["price"] for it,_,_,_ in proposed); tot_new=sum(n for _,_,n,_ in proposed)
    print(f"{store}: {len(proposed)} items eligible (aged>{AGED_DAYS}d, <{MAX_CUTS} cuts) | ${tot_old:,.0f} -> ${tot_new:,.0f}")
    for it,rec,new,nc in proposed[:8]:
        print(f"  {it['id']} | {it['age']}d | ${it['price']:.2f}->${new:.2f} (cut {nc}/3) | {it['title']}")
    if len(proposed)>8: print(f"  ... +{len(proposed)-8} more")

    if apply:
        done=0; fail=0
        for it,rec,new,nc in proposed:
            ok,err=revise(tok,it["id"],new)
            if ok:
                rec.update({"baseline":rec["baseline"],"cuts":nc,"last":today,"store":store}); state[it["id"]]=rec; done+=1
            else:
                fail+=1; print(f"  FAIL {it['id']}: {err}")
        json.dump(state,open(STATE,"w"),indent=2)
        print(f"{store}: APPLIED {done}, failed {fail}")
    else:
        print(f"{store}: dry run — nothing changed. Add --apply to execute.")

if __name__=="__main__": main()
