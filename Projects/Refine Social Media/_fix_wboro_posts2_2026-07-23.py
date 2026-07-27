#!/usr/bin/env python3
"""Coordinated fix 2026-07-23:
1. Delete the 3 announcement posts containing the bad acute-accent character; recreate clean at 4:02 PM ET.
2. Hiring-campaign posts targeting Waynesboro that say "closed Wednesdays": if still scheduled, delete
   and recreate with the Wednesday claim removed (Waynesboro opens Wednesdays effective 7/29).
3. Report anything already published that contains the stale claim (for a follow-up edit).
"""
import json, re, time
from publer_client import PublerClient

c = PublerClient()
posts = c.list_posts(state="scheduled", limit=100)
print("scheduled count:", len(posts))

id_to_key = {v["publer_id"]: k for k, v in c.accounts.items()}

def post_accounts(p):
    """Return list of publer account ids attached to a post record."""
    ids = []
    for k in ("account", "accounts"):
        v = p.get(k)
        if isinstance(v, dict) and v.get("id"):
            ids.append(v["id"])
        elif isinstance(v, list):
            for a in v:
                if isinstance(a, dict) and a.get("id"):
                    ids.append(a["id"])
                elif isinstance(a, str):
                    ids.append(a)
    if not ids and p.get("account_id"):
        ids.append(p["account_id"])
    return ids

bad_apostrophe, stale_wed = [], []
for p in posts:
    txt = p.get("text") or ""
    accs = post_accounts(p)
    keys = [id_to_key.get(a, a) for a in accs]
    if "´" in txt:
        bad_apostrophe.append((p, keys))
    elif re.search(r"closed Wednesdays?", txt) and any("Waynesboro" in str(k) or "waynesboro" in str(k).lower() for k in keys):
        stale_wed.append((p, keys))
    elif re.search(r"closed Wednesdays?", txt) and "Waynesboro" in txt and "West Broad" in txt:
        stale_wed.append((p, keys))

print("bad-apostrophe posts:", [(p["id"], k, p.get("scheduled_at")) for p, k in bad_apostrophe])
print("stale-Wed Waynesboro posts:", [(p["id"], k, p.get("scheduled_at")) for p, k in stale_wed])

# --- 1. delete bad announcement posts
for p, keys in bad_apostrophe:
    c.delete_post(p["id"])
    print("deleted announcement", p["id"], keys)

# --- 2. fix stale hiring posts (still scheduled)
for p, keys in stale_wed:
    txt = p.get("text") or ""
    new_txt = re.sub(r",?\s*closed Wednesdays?( too)?,?\s*", ", ", txt)
    new_txt = re.sub(r",\s*,", ",", new_txt).replace(" ,", ",")
    accs = post_accounts(p)
    when = p.get("scheduled_at")
    c.delete_post(p["id"])
    print("deleted stale hiring", p["id"], keys, when)
    # push recreate 20 min later than original to clear the slot and stay in the future
    r = c.schedule_post(new_txt, account_ids=accs, scheduled_at="2026-07-23T14:45:00-04:00")
    print("recreated hiring ->", r)
    print("new text:", new_txt[:220])

time.sleep(2)

# --- 3. recreate the clean announcement posts
fb_text = ("Big news, Waynesboro! \U0001F389 Starting Wednesday, July 29, 2026, our Waynesboro store is open six days a week — Monday through Saturday, 10 AM–6 PM. "
           "One more day to shop, make a loan payment, sell your gold and silver, or browse the showroom. Same fair, friendly service — now with Wednesdays. "
           "\U0001F4CD 1321 West Broad Street, Waynesboro · (540) 221-6346 — call or text. What’s Right Is Right.")
gbp_text = ("Starting Wednesday, July 29, 2026, our Waynesboro store is open six days a week — Monday through Saturday, 10am to 6pm. "
            "That’s one more day to shop, make a loan payment, or get a free evaluation. Stop by and see us at 1321 West Broad Street — we’d love to help. What’s Right Is Right.")
r1 = c.schedule_post(fb_text, store_keys=["Waynesboro", "Brand"], scheduled_at="2026-07-23T16:02:00-04:00")
print("FB announce job:", r1)
r2 = c.schedule_post(gbp_text, store_keys=["GBP_Waynesboro"], scheduled_at="2026-07-23T16:02:00-04:00")
print("GBP announce job:", r2)
time.sleep(4)
for label, r in [("FB", r1), ("GBP", r2)]:
    jid = r.get("job_id")
    if jid:
        s = c.job_status(jid)
        print(label, "status:", s.get("status"), "failures:", (s.get("payload") or {}).get("failures"))

# --- 4. published-today posts still carrying the stale claim (need Graph edit follow-up)
pub = c.list_posts(state="published", limit=30)
for p in pub:
    txt = p.get("text") or ""
    if re.search(r"closed Wednesdays?", txt) and ("Waynesboro" in txt or any("Waynesboro" in str(id_to_key.get(a, "")) for a in post_accounts(p))):
        print("PUBLISHED-STALE:", p.get("id"), post_accounts(p), (p.get("scheduled_at") or "")[:19], "|", txt[:160])
print("DONE")
