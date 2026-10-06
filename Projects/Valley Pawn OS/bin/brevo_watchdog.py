#!/usr/bin/env python3
"""brevo_watchdog.py [--dry-run] — native brevo-preflight-watchdog (daily 07:00, 2026-10-05).
The scan below is the SKILL's own script verbatim (enforce mode: suspends any about-to-send campaign missing
Master-11 Call/Text/UTM instrumentation, auto-adds list 10 Internal Seeds). Reporting follows the SKILL exactly:
exceptions -> #email-campiagns, routine all-clear -> Joshua DM with the marker text "Email watchdog:"."""
import sys as _sys
DRY = "--dry-run" in _sys.argv
import os, sys, json, datetime, urllib.request, urllib.error

STORES=["culpeper","waynesboro","harrisonburg","lexington","roanoke"]
SEEDS_LIST_ID=10
K=open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()

def api(url,method="GET",body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,method=method,
        headers={"api-key":K,"accept":"application/json","content-type":"application/json"})
    try:
        r=urllib.request.urlopen(req); raw=r.read().decode()
        return r.status,(json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code,{"error":e.read().decode()}

def check(h):
    ca=[s for s in STORES if f"/c/{s}" in h]; tx=[s for s in STORES if f"/t/{s}" in h]
    u=h.count("utm_content"); p=[]
    if len(ca)<5:p.append(f"Call buttons {len(ca)}/5")
    if len(tx)<5:p.append(f"Text buttons {len(tx)}/5")
    if u<10:p.append(f"utm_content {u} (<10)")
    if "Full Circle" in h:p.append("legal-name leak")
    return p,len(ca),len(tx),u

now=datetime.datetime.now(datetime.timezone.utc); seen={}
for status in ["queued","inProcess","draft"]:
    st,d=api(f"https://api.brevo.com/v3/emailCampaigns?status={status}&limit=100&sort=desc")
    for c in d.get("campaigns",[]):
        sched=c.get("scheduledAt"); fut=False
        if sched:
            try: fut=datetime.datetime.fromisoformat(sched.replace("Z","+00:00"))>now
            except: fut=True
        if status in ("queued","inProcess") or fut: seen[c["id"]]=c

res=[]
for cid,c in seen.items():
    st,full=api(f"https://api.brevo.com/v3/emailCampaigns/{cid}")
    h=full.get("htmlContent") or ""; p,ca,tx,u=check(h)

    lists=[l["id"] if isinstance(l,dict) else l for l in (full.get("recipients",{}).get("lists") or [])]
    seeds_ok = SEEDS_LIST_ID in lists
    seeds_fixed=False
    seeds_fix_failed=False
    if not seeds_ok and not DRY:
        new_lists=list(dict.fromkeys(lists+[SEEDS_LIST_ID]))
        sc,_=api(f"https://api.brevo.com/v3/emailCampaigns/{cid}","PUT",{"recipients":{"listIds":new_lists}})
        if sc in (200,201,204):
            seeds_fixed=True; seeds_ok=True
        else:
            seeds_fix_failed=True

    r={"id":cid,"name":c.get("name"),"status":c.get("status"),"scheduledAt":c.get("scheduledAt"),
       "pass":not p,"problems":p,"c":ca,"t":tx,"utm":u,"suspended":False,
       "seeds_ok":seeds_ok,"seeds_fixed":seeds_fixed,"seeds_fix_failed":seeds_fix_failed}

    if p and not DRY:
        sc,_=api(f"https://api.brevo.com/v3/emailCampaigns/{cid}/status","PUT",{"status":"suspended"})
        r["suspended"]=(sc in (200,204))

    res.append(r)

fails=[r for r in res if not r["pass"]]
seed_fixes=[r for r in res if r["seeds_fixed"]]
seed_hard_fails=[r for r in res if r["seeds_fix_failed"]]
RESULT={
    "checked":len(res),"failed":len(fails),
    "seed_fixes":len(seed_fixes),"seed_hard_fails":len(seed_hard_fails),
    "results":res}
print("RESULT_JSON:"+json.dumps(RESULT))

import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import vp_slack
_os.environ["VP_TASK"] = "brevo-preflight-watchdog"
CH, JOSHUA = "C0APR5WUL2Z", "U03BB52MDSA"
if not DRY:
    if fails:
        vp_slack.post(CH, ":rotating_light: *Blind-send blocked — %d campaign(s) SUSPENDED*\n" % len(fails) + "\n".join(
            '• #%s "%s" (scheduled %s) — %s; SUSPENDED so it can\'t send blind.' % (r["id"], r["name"], r["scheduledAt"], ", ".join(r["problems"])) for r in fails)
            + "\nFix: rebuild from VP Master Template (ID 11) — it carries all 5 stores' Call/Text buttons + utm_content. Then reschedule.")
    if seed_hard_fails:
        vp_slack.post(CH, ":rotating_light: *Standing recipient rule could not be applied to %d campaign(s)* — list 10 (Internal Seeds: you, Preston, all 5 stores) is missing and adding it failed. Campaign(s): %s. Fix manually in Brevo before it sends." % (
            len(seed_hard_fails), ", ".join("#%s %s" % (r["id"], r["name"]) for r in seed_hard_fails)))
    elif seed_fixes:
        vp_slack.post(CH, ":heavy_check_mark: Standing recipient rule: auto-added list 10 (Internal Seeds) to %d campaign(s) that were missing it: %s." % (
            len(seed_fixes), ", ".join("#%s %s" % (r["id"], r["name"]) for r in seed_fixes)))
    if not fails and not seed_fixes and not seed_hard_fails and res:
        vp_slack.post(JOSHUA, ":white_check_mark: Email watchdog: %d upcoming send(s) checked, all carry full Call/Text + UTM instrumentation and the standing recipient list." % len(res))
