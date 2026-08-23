#!/usr/bin/env python3
"""Update W13 (campaign 28) + W14 (29): branded sender, real reply-to, stronger
subject, corrected utm_campaign date. Leaves both as DRAFTS so the hardened
vp-deal-of-week-monday-pick task fills the deal block and schedules them."""
import json, urllib.request, os

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"

def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"api-key": KEY, "Content-Type": "application/json",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

PLAN = {
    28: {
        "subject": "Our Lexington store moved — 125 Walker Street",
        "old_utm": "weekly_lexington_2026-08-06",
        "new_utm": "weekly_lexington_2026-08-27",
    },
    29: {
        "subject": "Every item we sell is covered for 30 days. Every one.",
        "old_utm": "weekly_warranty_2026-08-13",
        "new_utm": "weekly_warranty_2026-09-03",
    },
}

for cid, p in PLAN.items():
    st, cur = req("GET", f"/emailCampaigns/{cid}")
    if st != 200:
        print(cid, "FETCH FAIL", st, cur); continue
    html = cur.get("htmlContent") or ""
    before = html.count(p["old_utm"])
    html = html.replace(p["old_utm"], p["new_utm"])

    payload = {
        "sender": {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"},
        "replyTo": "jdavis@fcfpawn.com",
        "subject": p["subject"],
        "htmlContent": html,
    }
    st2, res = req("PUT", f"/emailCampaigns/{cid}", payload)
    print(f"campaign {cid}: utm rewrites={before} -> PUT {st2} {res if st2>=300 else 'OK'}")

    st3, chk = req("GET", f"/emailCampaigns/{cid}")
    print("   verify:", chk.get("status"), "|", chk.get("sender"), "| replyTo:", chk.get("replyTo"))
    print("   subject:", chk.get("subject"))
    print("   utm now:", p["new_utm"] in (chk.get("htmlContent") or ""),
          "| stale utm gone:", p["old_utm"] not in (chk.get("htmlContent") or ""))
