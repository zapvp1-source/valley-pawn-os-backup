#!/usr/bin/env python3
"""
Brevo send preflight — instrumentation guardrail.
Refuses to green-light any Valley Pawn campaign that isn't built on VP Master
Template 11's tracking. Run this against a campaign ID BEFORE scheduling/sending.

Usage:  python3 brevo_preflight.py <campaign_id>
Exit 0 = PASS (safe to send). Exit 1 = FAIL (do not send).

Key is read from ~/.config/valley-pawn/brevo_api_key (bridge from Mac if empty).
"""
import os, sys, json, urllib.request

STORES = ["culpeper","waynesboro","harrisonburg","lexington","roanoke"]

def key():
    p=os.path.expanduser("~/.config/valley-pawn/brevo_api_key")
    k=open(p).read().strip() if os.path.exists(p) else ""
    if not k: sys.exit("FAIL: Brevo API key missing — bridge it from the Mac first.")
    return k

def get(url,k):
    req=urllib.request.Request(url,headers={"api-key":k,"accept":"application/json"})
    return json.load(urllib.request.urlopen(req))

def check(cid):
    k=key()
    c=get(f"https://api.brevo.com/v3/emailCampaigns/{cid}",k)
    h=c.get("htmlContent") or ""
    name=c.get("name",""); status=c.get("status","")
    calls=[s for s in STORES if f"/c/{s}" in h]
    texts=[s for s in STORES if f"/t/{s}" in h]
    utm=h.count("utm_content")
    problems=[]
    if len(calls)<5: problems.append(f"missing Call buttons for: {set(STORES)-set(calls) or 'none'} ({len(calls)}/5)")
    if len(texts)<5: problems.append(f"missing Text buttons for: {set(STORES)-set(texts) or 'none'} ({len(texts)}/5)")
    if utm<10:       problems.append(f"only {utm} utm_content tags (need >=10 — north-star tracking)")
    if "Full Circle" in h: problems.append("legal entity name 'Full Circle Finance Inc' leaked into a customer email — DBA only")
    print(f"Campaign #{cid} [{status}] {name}")
    print(f"  Call buttons: {len(calls)}/5   Text buttons: {len(texts)}/5   utm_content: {utm}")
    if problems:
        print("  RESULT: ❌ FAIL — DO NOT SEND")
        for p in problems: print("   - "+p)
        print("  Fix: rebuild from VP Master Template (ID 11) — see brevo-context skill.")
        return 1
    print("  RESULT: ✅ PASS — instrumentation intact, safe to schedule.")
    return 0

if __name__=="__main__":
    if len(sys.argv)!=2: sys.exit("Usage: python3 brevo_preflight.py <campaign_id>")
    sys.exit(check(sys.argv[1]))
