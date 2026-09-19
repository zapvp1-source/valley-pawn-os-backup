#!/usr/bin/env python3
"""vp_audit_diag.py — can the vp_ops_engine bot actually SEE the history vp_audit.py counts?
A rate is only meaningful if the denominator's window is visible. Read-only."""
import getpass, json, os, subprocess, sys, time, urllib.parse, urllib.request, datetime as dt
SVC="vp-ops-slack-bot-token"
def token():
    r=subprocess.run(["security","find-generic-password","-s",SVC,"-a",getpass.getuser(),"-w"],capture_output=True,text=True,timeout=10)
    return r.stdout.strip()
TOK=token()
def hist(ch, oldest):
    msgs=[];cur=None
    for _ in range(40):
        p={"channel":ch,"oldest":str(oldest),"limit":200}
        if cur:p["cursor"]=cur
        r=json.load(urllib.request.urlopen(urllib.request.Request(
            "https://slack.com/api/conversations.history?"+urllib.parse.urlencode(p),
            headers={"Authorization":"Bearer "+TOK}),timeout=30))
        if not r.get("ok"):return None,r.get("error")
        msgs+=r.get("messages",[])
        cur=(r.get("response_metadata") or {}).get("next_cursor")
        if not cur:break
        time.sleep(1.2)
    return msgs,None
start=(dt.datetime.now()-dt.timedelta(days=60)).timestamp()
for name,ch,marker in [("#pawn-walks","C0B8WR95N31","Daily Pawn Walk"),
                       ("#general","C03BETSS669","Daily Clock-In Check"),
                       ("#discount-review","C0BQ6JA27MX","Discount Review"),
                       ("#emails-missed","C0BNN60347M","nopened")]:
    m,err=hist(ch,start)
    if err: print("%-18s ERROR %s"%(name,err)); continue
    ts=[float(x["ts"]) for x in m]
    join=[x for x in m if x.get("subtype")=="channel_join" and "VP OPS" in (x.get("text") or "")]
    hits=[float(x["ts"]) for x in m if marker.lower() in (x.get("text") or "").lower()]
    print("%-18s msgs=%-5d oldest=%s  join=%s  marker_hits=%d oldest_hit=%s"%(
        name,len(m),
        dt.datetime.fromtimestamp(min(ts)).strftime("%m/%d") if ts else "-",
        dt.datetime.fromtimestamp(float(join[0]["ts"])).strftime("%m/%d") if join else "NONE",
        len(hits),
        dt.datetime.fromtimestamp(min(hits)).strftime("%m/%d") if hits else "-"))
