#!/usr/bin/env python3
"""brevo_audit_export.py — READ-ONLY full-channel export for the email channel audit (2026-10-20).

Writes ONE JSON file:  Email Refinement/_audit/brevo_export_<date>.json
Never prints or writes the API key. Never PUT/POST/DELETE. Stdlib only. Host only (key in ~/.config).

Pulls: account, senders, domains, lists (with counts), folders, smtp templates (meta only),
all email campaigns (sent / queued / draft / suspended) with per-campaign globalStats + linksStats,
transactional aggregate stats (welcome flow), contact totals, blacklist counts.
"""
import functools, json, os, sys, time, urllib.error, urllib.parse, urllib.request, datetime
print = functools.partial(print, flush=True)
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects")
OUT_DIR = os.path.join(OS_DIR, "Email Refinement", "_audit")
os.makedirs(OUT_DIR, exist_ok=True)
TODAY = datetime.date.today().isoformat()
OUT = os.path.join(OUT_DIR, f"brevo_export_{TODAY}.json")
BASE = "https://api.brevo.com/v3"

def api(path, params=None):
    url = BASE + path + (("?" + urllib.parse.urlencode(params)) if params else "")
    req = urllib.request.Request(url, headers={"api-key": K, "accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(2 + attempt * 3); continue
            return e.code, {"error": body}
        except Exception as e:  # network
            time.sleep(2 + attempt * 3); last = repr(e)
    return 0, {"error": last}

def paged(path, key, limit=50, extra=None):
    out, offset = [], 0
    while True:
        st, d = api(path, dict(limit=limit, offset=offset, **(extra or {})))
        if st != 200: out.append({"_error": st, "_body": d}); break
        items = d.get(key) or []
        out.extend(items)
        if len(items) < limit: break
        offset += limit
    return out

export = {"exported_at": datetime.datetime.now().isoformat(), "errors": []}

def grab(name, fn):
    try:
        export[name] = fn(); print("ok", name)
    except Exception as e:
        export["errors"].append({name: repr(e)}); print("ERR", name, repr(e))

grab("account", lambda: api("/account")[1])
grab("senders", lambda: api("/senders")[1])
grab("domains", lambda: api("/senders/domains")[1])
grab("lists", lambda: paged("/contacts/lists", "lists"))
grab("folders", lambda: paged("/contacts/folders", "folders"))
grab("contacts_total", lambda: api("/contacts", {"limit": 1})[1].get("count"))
grab("blacklisted_total", lambda: api("/contacts", {"limit": 1, "filter": "equals(emailBlacklisted,true)"})[1])
grab("attributes", lambda: api("/contacts/attributes")[1])
grab("segments", lambda: api("/contacts/segments", {"limit": 50})[1])
grab("smtp_templates", lambda: [{k: t.get(k) for k in ("id", "name", "subject", "isActive", "createdAt", "modifiedAt", "sender")}
                                for t in paged("/smtp/templates", "templates")])
grab("transactional_agg_90d", lambda: api("/smtp/statistics/aggregatedReport",
                                          {"startDate": (datetime.date.today() - datetime.timedelta(days=90)).isoformat(),
                                           "endDate": TODAY})[1])
grab("transactional_events_welcome", lambda: api("/smtp/statistics/events", {"limit": 100, "templateId": 72, "days": 30})[1])

# campaigns — every status, then detail per campaign
camps = []
for status in ("sent", "queued", "draft", "suspended", "archive", "inProcess"):
    st, d = api("/emailCampaigns", {"status": status, "limit": 100, "sort": "desc"})
    if st == 200:
        for c in d.get("campaigns", []):
            c["_status_bucket"] = status; camps.append(c)
    else:
        export["errors"].append({"campaigns_" + status: [st, d]})
seen = set(); detail = []
for c in camps:
    cid = c["id"]
    if cid in seen: continue
    seen.add(cid)
    st, full = api(f"/emailCampaigns/{cid}", {"statistics": "globalStats"})
    row = {k: c.get(k) for k in ("id", "name", "subject", "status", "scheduledAt", "sentDate", "createdAt", "modifiedAt", "tag", "sender", "replyTo", "abTesting", "subjectA", "subjectB", "_status_bucket")}
    if st == 200:
        row["recipients"] = full.get("recipients")
        stats = full.get("statistics") or {}
        row["globalStats"] = stats.get("globalStats")
        row["campaignStats"] = stats.get("campaignStats")
        row["linksStats"] = stats.get("linksStats")
        row["statsByDomain"] = stats.get("statsByDomain")
        row["statsByDevice"] = stats.get("statsByDevice")
        row["statsByBrowser"] = stats.get("statsByBrowser")
        row["mirrorActive"] = full.get("mirrorActive")
        row["header"] = full.get("header"); row["footer"] = full.get("footer")
        row["htmlLength"] = len(full.get("htmlContent") or "")
        row["previewText"] = full.get("previewText")
        row["utmCampaign"] = full.get("utmCampaign")
        row["sendAtBestTime"] = full.get("sendAtBestTime")
        row["inlineImageActivation"] = full.get("inlineImageActivation")
        # keep html only for the last 12 sent + all queued/draft (for creative review)
        row["_html"] = full.get("htmlContent") if (c.get("status") != "sent" or len(detail) < 12) else None
    else:
        row["_error"] = [st, full]
    detail.append(row); time.sleep(0.25)
export["campaigns"] = detail
print("campaigns:", len(detail))

with open(OUT, "w") as f: json.dump(export, f, indent=1, default=str)
print("WROTE", OUT, os.path.getsize(OUT), "bytes")
