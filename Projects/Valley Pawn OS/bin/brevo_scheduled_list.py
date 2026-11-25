#!/usr/bin/env python3
"""brevo_scheduled_list.py -- READ-ONLY (GET only), 2026-11-24. Lists Brevo email campaigns that are queued/scheduled
or drafts with a future send time: id, name, status, scheduledAt, recipient lists. -> fleet/state/brevo_scheduled.json"""
import os, json, urllib.request, urllib.error
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
def get(url):
    req = urllib.request.Request(url, headers={"api-key": K, "accept": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return {"error": e.code}
out = []
for status in ("queued", "inProcess", "draft", "suspended"):
    d = get("https://api.brevo.com/v3/emailCampaigns?status=%s&limit=100&sort=desc" % status)
    for c in d.get("campaigns") or []:
        if c.get("scheduledAt") or status in ("queued", "inProcess"):
            out.append({"id": c["id"], "name": c.get("name"), "status": c.get("status"), "scheduledAt": c.get("scheduledAt"),
                        "lists": ((c.get("recipients") or {}).get("lists")), "subject": c.get("subject")})
out.sort(key=lambda x: x["scheduledAt"] or "")
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "brevo_scheduled.json")
json.dump(out, open(p, "w"), indent=1)
for c in out: print(c["scheduledAt"], c["status"], "#%s" % c["id"], c["name"])
