#!/usr/bin/env python3
"""Replace the two Waynesboro 6-day announcement posts (bad apostrophes) with corrected copy."""
import time
from publer_client import PublerClient

c = PublerClient()

# 1. Find and delete the two just-scheduled posts containing the bad accent char
posts = c.list_posts(state="scheduled", limit=100)
deleted = 0
for p in posts:
    txt = (p.get("text") or "") + str(p.get("networks") or "")
    if "´" in txt and "six days a week" in txt:
        c.delete_post(p["id"])
        deleted += 1
        print("deleted post", p["id"])
print("deleted:", deleted)

fb_text = ("Big news, Waynesboro! \U0001F389 Starting Wednesday, July 29, 2026, our Waynesboro store is open six days a week — Monday through Saturday, 10 AM–6 PM. "
           "One more day to shop, make a loan payment, sell your gold and silver, or browse the showroom. Same fair, friendly service — now with Wednesdays. "
           "\U0001F4CD 1321 West Broad Street, Waynesboro · (540) 221-6346 — call or text. What’s Right Is Right.")
gbp_text = ("Starting Wednesday, July 29, 2026, our Waynesboro store is open six days a week — Monday through Saturday, 10am to 6pm. "
            "That’s one more day to shop, make a loan payment, or get a free evaluation. Stop by and see us at 1321 West Broad Street — we’d love to help. What’s Right Is Right.")

r1 = c.schedule_post(fb_text, store_keys=["Waynesboro", "Brand"], scheduled_at="2026-07-23T16:00:00-04:00")
print("FB job:", r1)
r2 = c.schedule_post(gbp_text, store_keys=["GBP_Waynesboro"], scheduled_at="2026-07-23T16:00:00-04:00")
print("GBP job:", r2)
time.sleep(4)
for label, r in [("FB", r1), ("GBP", r2)]:
    jid = r.get("job_id")
    if jid:
        s = c.job_status(jid)
        print(label, "status:", s.get("status"), "failures:", (s.get("payload") or {}).get("failures"))

# verify final scheduled set
time.sleep(2)
posts = c.list_posts(state="scheduled", limit=100)
for p in posts:
    txt = str(p.get("text") or "")
    if "six days a week" in txt or "six days" in str(p.get("networks") or ""):
        print("SCHEDULED:", p.get("id"), "|", (p.get("scheduled_at") or p.get("date")), "|", txt[:90])
