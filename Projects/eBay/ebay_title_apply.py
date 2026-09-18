#!/usr/bin/env python3
"""Apply enriched eBay titles from a batch JSON {ItemID: new_title}. Reversible.
Original titles read from ~/ebay_short_titles.json (store + current title).
State: ~/ebay_title_enrich_state.json { ItemID: {"original": t, "store": s} }
Usage: python3 ebay_title_apply.py <batch.json> [--apply|--revert]"""
import json,os,sys,xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request,urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py

# ── Model-number guard, added 2026-09-17 (Joshua, store feedback) ──────────────
# A rewritten title may never silently drop a parenthesised code that was in the
# old title. Our own stock number (VAP/VP/VA/CUL/ROA/WAY/HAR/LEX + 5+ digits) may
# go; anything else in parens containing a digit is a manufacturer model number
# and is the highest-value search term on the listing.
import re as _re
_OURS = _re.compile(r"^(?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,}$")
_PAREN = _re.compile(r"\(([^)]{1,24})\)")
def _dropped_model_numbers(old, new):
    lost = []
    for c in _PAREN.findall(old or ""):
        c = c.strip()
        if _OURS.match(c.upper()):
            continue
        if not _re.search(r"\d", c):
            continue
        if c.lower() not in (new or "").lower():
            lost.append(c)
    return lost
# ──────────────────────────────────────────────────────────────────────────────
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
SHORT=os.path.expanduser("~/ebay_short_titles.json");STATE=os.path.expanduser("~/ebay_title_enrich_state.json")
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return {s["name"]:s["token"] for s in ns["STORES"]}
    raise SystemExit("no tokens")
def revise(tok,iid,title):
    body=(f'<?xml version="1.0" encoding="utf-8"?><ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><Item><ItemID>{iid}</ItemID><Title>{escape(title)}</Title></Item></ReviseFixedPriceItemRequest>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"ReviseFixedPriceItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    r=ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=60).read().decode())
    ok=r.findtext(f"{{{NS}}}Ack","") in ("Success","Warning")
    return ok,(r.findtext(f".//{{{NS}}}ShortMessage") or "err")
def main():
    batch=json.load(open(sys.argv[1]));apply="--apply" in sys.argv;revert="--revert" in sys.argv
    toks=stores();short={x["id"]:x for x in json.load(open(SHORT))}
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    if revert:
        n=0
        for iid,rec in list(state.items()):
            if apply: revise(toks[rec["store"]],iid,rec["original"])
            n+=1
        print(f"reverted {n}"+("" if apply else " (dry)"));return
    done=fail=0
    for iid,newt in batch.items():
        if iid not in short: print(f"  skip {iid} (not in short list)"); continue
        st=short[iid]["store"];old=short[iid]["title"]
        _lost=_dropped_model_numbers(old,newt)
        if _lost:
            print(f"  REFUSED {iid} ({st}) — new title drops model number(s): {', '.join(_lost)} | keep them (Joshua 2026-09-17)")
            continue
        if not apply: print(f"  {st}: {old}  ->  {newt}"); continue
        ok,err=revise(toks[st],iid,newt)
        if ok: state[iid]={"original":old,"store":st};done+=1
        else: fail+=1;print(f"  FAIL {iid} ({st}): {err}")
    if apply:
        json.dump(state,open(STATE,"w"),indent=2);print(f"APPLIED {done}, failed {fail}")
    else: print(f"dry run: {len(batch)} titles")
if __name__=="__main__": main()
