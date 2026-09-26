#!/usr/bin/env python3
"""eaw_probe.py — read-only reconnaissance for the native email-analytics-weekly: helper signatures,
the master sheet's header row + last 3 rows, and the newest 3 sent Brevo campaigns. Writes nothing."""
import sys, inspect, json
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
import brevo_helper, sheets_helper
for mod in (brevo_helper, sheets_helper):
    print("==", mod.__name__)
    for n, o in inspect.getmembers(mod, inspect.isclass):
        if o.__module__ != mod.__name__: continue
        for mn, mo in inspect.getmembers(o, inspect.isfunction):
            if mn.startswith("_") and mn != "__init__": continue
            try: print("  %s.%s%s" % (n, mn, inspect.signature(mo)))
            except Exception: print("  %s.%s(?)" % (n, mn))
SHEET="1EPj22S1zzbSm4B_mRZ4y8TEXXpiCj6YM_75TmVV4d2o"
s = sheets_helper.SheetsClient()
rows = s.read_as_dicts(SHEET, 'Email Campaign Performance')
print("== sheet rows:", len(rows)); print("headers:", list(rows[0].keys()) if rows else "none")
for r in rows[-3:]: print(json.dumps(r)[:600])
b = brevo_helper.BrevoClient()
sent = b.list_email_campaigns(status='sent')
print("== brevo sent campaigns:", len(sent) if hasattr(sent,'__len__') else type(sent))
lst = sent if isinstance(sent, list) else sent.get("campaigns", sent)
for c in sorted(lst, key=lambda c: c.get("sentDate",""), reverse=True)[:3]:
    print(json.dumps({k: c.get(k) for k in ("id","name","sentDate","subject")}))
    cid = c["id"]
    full = b.get_email_campaign(cid)
    st = (full.get("statistics") or {}).get("campaignStats") or [{}]
    print("   stats:", json.dumps(st[0])[:400])
    print("   buckets:", json.dumps(b.utm_content_bucketed_clicks(cid))[:400])
