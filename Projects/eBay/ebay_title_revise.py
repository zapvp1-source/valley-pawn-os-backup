#!/usr/bin/env python3
"""Generic reversible eBay title revise. Input {id:{store,old,new}}.
State ~/ebay_toolfix_state.json {id:{store,old}} (shared w/ toolfix for unified revert).
Usage: ebay_title_revise.py <fixes.json> [--apply|--revert]"""
import os,sys,json,xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request,urlopen
ns={}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(),'x','exec'),ns)
TOK={s['name']:s['token'] for s in ns['STORES']}
sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
STATE=os.path.expanduser('~/ebay_toolfix_state.json')
def revise(tok,iid,title):
    b=(f'<?xml version="1.0" encoding="utf-8"?><ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><Item><ItemID>{iid}</ItemID><Title>{escape(title)}</Title></Item></ReviseFixedPriceItemRequest>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"ReviseFixedPriceItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    r=ET.fromstring(urlopen(Request(URL,data=b,headers=h),timeout=60).read().decode())
    ack=r.findtext(f"{{{NS}}}Ack","");return ack in ("Success","Warning"),(r.findtext(f".//{{{NS}}}ShortMessage") or ack)
fixes=json.load(open(sys.argv[1])); apply="--apply" in sys.argv
state=json.load(open(STATE)) if os.path.exists(STATE) else {}
if "--revert" in sys.argv:
    for iid,rec in state.items():
        if apply: ok,m=revise(TOK[rec['store']],iid,rec['old']); print(('OK ' if ok else 'FAIL ')+iid,m)
    sys.exit()
# Model-number guard, added 2026-09-17 (Joshua, store feedback): a rewritten title may
# never silently drop a parenthesised code that was in the old title. Our own stock number
# (VAP/VP/VA/CUL/ROA/WAY/HAR/LEX + 5+ digits) is allowed to go — everything else in parens
# is a manufacturer model number and is the highest-value search term on the listing.
import re as _re
_OURS = _re.compile(r"^(?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,}$")
_PAREN = _re.compile(r"\(([^)]{1,24})\)")
def _dropped_model_numbers(old, new):
    lost = []
    for c in _PAREN.findall(old or ""):
        c = c.strip()
        if _OURS.match(c.upper()):      # our stock number — fine to remove
            continue
        if not _re.search(r"\d", c):    # words like (Tested), (Read), (Open Box)
            continue
        # a real model number: it must survive somewhere in the new title
        if c.lower() not in (new or "").lower():
            lost.append(c)
    return lost

for iid,v in fixes.items():
    if len(v['new'])>80: print("TOO LONG",iid); continue
    _lost = _dropped_model_numbers(v.get('old'), v.get('new'))
    if _lost:
        print("REFUSED",iid,"— new title drops model number(s):", ", ".join(_lost),
              "| keep them in the title (Joshua 2026-09-17)")
        continue
    if not apply: print("DRY",v['store'],iid,'->',v['new']); continue
    ok,m=revise(TOK[v['store']],iid,v['new'])
    if ok: state[iid]={"store":v['store'],"old":v['old']}; print("OK  ",v['store'],iid,v['new'])
    else: print("FAIL",iid,m)
if apply: json.dump(state,open(STATE,'w'),indent=2)
