#!/usr/bin/env python3
"""Fix 'Tool Only'-mislabeled titles for items that actually include battery/charger.
Reads new titles from a JSON {id:new_title}; old title+store from ~/tool_only_candidates.json.
Reversible: state ~/ebay_toolfix_state.json {id:{store,old}}.
Usage: ebay_toolfix_apply.py <fixes.json> [--apply|--revert]"""
import os,sys,json,xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request,urlopen
ns={}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(),'x','exec'),ns)
TOK={s['name']:s['token'] for s in ns['STORES']}
sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT

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
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
CAND={c['id']:c for c in json.load(open(os.path.expanduser('~/tool_only_candidates.json')))}
STATE=os.path.expanduser('~/ebay_toolfix_state.json')
def revise(tok,iid,title):
    b=(f'<?xml version="1.0" encoding="utf-8"?><ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><Item><ItemID>{iid}</ItemID><Title>{escape(title)}</Title></Item></ReviseFixedPriceItemRequest>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"ReviseFixedPriceItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    r=ET.fromstring(urlopen(Request(URL,data=b,headers=h),timeout=60).read().decode())
    ack=r.findtext(f"{{{NS}}}Ack","");return ack in ("Success","Warning"),(r.findtext(f".//{{{NS}}}ShortMessage") or ack)
def main():
    fixes=json.load(open(sys.argv[1])); apply="--apply" in sys.argv
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    if "--revert" in sys.argv:
        for iid,rec in state.items():
            if apply: ok,m=revise(TOK[rec['store']],iid,rec['old']); print(('OK ' if ok else 'FAIL ')+iid,m)
        return
    for iid,new in fixes.items():
        c=CAND.get(iid);
        if not c: print("skip (not candidate)",iid); continue
        if len(new)>80: print("TOO LONG(%d)"%len(new),iid,new); continue
        _lost=_dropped_model_numbers(c.get('title'),new)
        if _lost:
            print("REFUSED",iid,"— new title drops model number(s):",", ".join(_lost),
                  "| keep them in the title (Joshua 2026-09-17)")
            continue
        if not apply: print(f"  {c['store']} {iid}\n    {c['title']}\n -> {new}"); continue
        ok,m=revise(TOK[c['store']],iid,new)
        if ok: state[iid]={"store":c['store'],"old":c['title']}; print("OK  ",c['store'],iid,new)
        else: print("FAIL",iid,m)
    if apply: json.dump(state,open(STATE,'w'),indent=2)
if __name__=="__main__": main()
