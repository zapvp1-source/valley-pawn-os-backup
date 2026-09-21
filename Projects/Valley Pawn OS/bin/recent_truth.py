#!/usr/bin/env python3
"""recent_truth.py — for every channel-publishing Tier-1 task, list which of the last N days it
actually posted on.

WHY (Joshua, 2026-09-20: "cloud cover works fine, find the stuff that doesnt"): he was right and the
audit's framing was wrong. A 60-day lifetime rate is dominated by two multi-day outages and by dates
before a task was converted to its current form. It answers "how has this task done since July",
which is history. The question that decides where to spend a day of work is "is it working NOW".
This answers only that, day by day, read with the posting app's own token.
"""
import datetime as dt, json, os, sys
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
sys.path.insert(0, os.path.join(OS_DIR, "bin"))
import vp_slack
DAYS = int(sys.argv[sys.argv.index("--days")+1]) if "--days" in sys.argv else 14
ents = [e for e in json.load(open(os.path.join(OS_DIR,"fleet/expected_outputs.json")))["entries"]
        if e.get("channel_id") and e.get("marker") and not str(e.get("cadence","")).startswith(("monthly","retired"))]
tier1 = {t for g in json.load(open(os.path.join(OS_DIR,"fleet/tier1_tasks.json")))["tier1"].values() for t in g}
ents = [e for e in ents if e["task"] in tier1]
now = dt.datetime.now()
cache = {}
print("# Recent reality — last %d days (posting app's own view)\n" % DAYS)
print("A dot is a day the report landed. A dash is a day it did not. Weekend/Sunday gaps are normal")
print("for weekday cadences; Wednesdays are Culpeper-only.\n")
print("| Task | " + " ".join((now - dt.timedelta(days=DAYS-1-i)).strftime("%d") for i in range(DAYS)) + " | posted |")
print("|---|" + "---|"*DAYS + "---:|")
rows=[]
for e in sorted(ents, key=lambda x: x["task"]):
    ch, mk = e["channel_id"], e["marker"]
    ci = e.get("marker_ci")
    if ch not in cache:
        try:
            oldest = str((now - dt.timedelta(days=DAYS)).timestamp())
            msgs, cur = [], None
            for _ in range(6):
                p = {"channel": ch, "oldest": oldest, "limit": 200}
                if cur: p["cursor"] = cur
                r = vp_slack.call("conversations.history", params=p)
                if not r.get("ok"): break
                msgs += r.get("messages", [])
                cur = (r.get("response_metadata") or {}).get("next_cursor")
                if not cur: break
            cache[ch] = msgs
        except Exception:
            cache[ch] = []
    days=[]
    for i in range(DAYS):
        d = (now - dt.timedelta(days=DAYS-1-i)).date()
        hit=False
        for m in cache[ch]:
            try: t = dt.datetime.fromtimestamp(float(m["ts"])).date()
            except Exception: continue
            if t != d: continue
            txt = m.get("text") or ""
            if (mk.lower() in txt.lower()) if ci else (mk in txt): hit=True; break
        days.append(hit)
    n=sum(days)
    rows.append((n, e["task"], days))
    print("| %s | %s | %d/%d |" % (e["task"], " ".join(" ●" if x else " –" for x in days), n, DAYS))
print("\n## Nothing at all in %d days — these are the real problems\n" % DAYS)
dead=[t for n,t,_ in rows if n==0]
for t in dead: print("- **%s**" % t)
print("\n## Posting most days — working\n")
for n,t,_ in sorted(rows, reverse=True):
    if n >= DAYS*0.5: print("- %s (%d/%d)" % (t,n,DAYS))
print("\nSUMMARY dead=%d working=%d partial=%d" % (len(dead), sum(1 for n,_,_ in rows if n>=DAYS*0.5),
      sum(1 for n,_,_ in rows if 0<n<DAYS*0.5)))
