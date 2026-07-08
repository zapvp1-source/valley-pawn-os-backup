#!/usr/bin/env python3
"""
Brevo preflight WATCHDOG — automatic enforcement across ALL send paths.

Scans every Brevo campaign that is about to go out (status 'queued', 'inProcess',
or a 'draft' with a future scheduledAt) and runs the instrumentation preflight.
Any campaign that FAILS is SUSPENDED (so it physically cannot send blind) and
reported. Covers API-scheduled sends, manually-scheduled UI sends, holiday
one-offs — everything.

  python3 brevo_preflight_watchdog.py            # enforce: suspend failers
  python3 brevo_preflight_watchdog.py --dry-run  # report only, suspend nothing

Prints a machine-readable RESULT block the scheduled task uses to build its
Slack alert. Exit 0 = all upcoming sends clean (or none). Exit 2 = at least one
failed (and was suspended unless --dry-run).
"""
import os, sys, json, datetime, urllib.request, urllib.error

STORES = ["culpeper","waynesboro","harrisonburg","lexington","roanoke"]
DRY = "--dry-run" in sys.argv

def key():
    p=os.path.expanduser("~/.config/valley-pawn/brevo_api_key")
    k=open(p).read().strip() if os.path.exists(p) else ""
    if not k: sys.exit("FAIL: Brevo API key missing — bridge from Mac first.")
    return k
K=key()

def api(url, method="GET", body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url, data=data, method=method,
        headers={"api-key":K,"accept":"application/json","content-type":"application/json"})
    try:
        r=urllib.request.urlopen(req)
        raw=r.read().decode()
        return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()}

def check_html(h):
    calls=[s for s in STORES if f"/c/{s}" in h]
    texts=[s for s in STORES if f"/t/{s}" in h]
    utm=h.count("utm_content")
    problems=[]
    if len(calls)<5: problems.append(f"Call buttons {len(calls)}/5")
    if len(texts)<5: problems.append(f"Text buttons {len(texts)}/5")
    if utm<10:       problems.append(f"utm_content {utm} (<10)")
    if "Full Circle" in h: problems.append("legal-name leak")
    return problems, len(calls), len(texts), utm

def upcoming():
    now=datetime.datetime.now(datetime.timezone.utc)
    out=[]
    for status in ["queued","inProcess","draft"]:
        st,d=api(f"https://api.brevo.com/v3/emailCampaigns?status={status}&limit=100&sort=desc")
        for c in d.get("campaigns",[]):
            sched=c.get("scheduledAt")
            future=False
            if sched:
                try:
                    dt=datetime.datetime.fromisoformat(sched.replace("Z","+00:00"))
                    future = dt>now
                except Exception:
                    future=True
            # queued/inProcess are imminent regardless; drafts only if scheduled to a future time
            if status in ("queued","inProcess") or future:
                out.append(c)
    # de-dupe by id
    seen={}; 
    for c in out: seen[c["id"]]=c
    return list(seen.values())

def main():
    camps=upcoming()
    results=[]
    for c in camps:
        cid=c["id"]
        st,full=api(f"https://api.brevo.com/v3/emailCampaigns/{cid}")
        h=full.get("htmlContent") or ""
        problems,ca,tx,utm=check_html(h)
        rec={"id":cid,"name":c.get("name"),"status":c.get("status"),
             "scheduledAt":c.get("scheduledAt"),"pass":not problems,
             "problems":problems,"c":ca,"t":tx,"utm":utm,"suspended":False}
        if problems and not DRY:
            sc,_=api(f"https://api.brevo.com/v3/emailCampaigns/{cid}/status","PUT",{"status":"suspended"})
            rec["suspended"] = (sc in (200,204))
        results.append(rec)
    fails=[r for r in results if not r["pass"]]
    print("RESULT_JSON:"+json.dumps({"checked":len(results),"failed":len(fails),
        "dry_run":DRY,"results":results}))
    print(f"\nUpcoming sends checked: {len(results)} | failing: {len(fails)}")
    for r in results:
        flag="✅" if r["pass"] else ("❌ SUSPENDED" if r["suspended"] else "❌ FAIL")
        print(f"  {flag}  #{r['id']} [{r['status']}] {r['name']}  (c{r['c']}/t{r['t']}/utm{r['utm']})")
        for p in r["problems"]: print(f"        - {p}")
    return 2 if fails else 0

if __name__=="__main__":
    sys.exit(main())
