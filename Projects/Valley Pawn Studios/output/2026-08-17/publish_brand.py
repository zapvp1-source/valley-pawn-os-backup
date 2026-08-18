#!/usr/bin/env python3
import sys, json, datetime
sys.path.insert(0, "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media")
from publer_client import PublerClient
from vp_social_publisher import qa_check_caption

BA = "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/brand_assets"

# Brand-tier message posts. Real, verified facts (valley-pawn-context).
# Fresh wording (NOT verbatim last week). No hashtags (FB-safe), <260 chars (X-safe).
items = [
    {
        "id": "brand-warranty-2026-08-18",
        "pillar": "warranty",
        "caption": "Buy something from Valley Pawn and it's covered by a 30-day warranty — every item, every one of our five Shenandoah Valley stores. If it doesn't work right, bring it back. Family-owned, and we stand behind what we sell. What's Right Is Right.",
        "image": BA + "/valley_pawn_landscape.png",
        "scheduled_at": "2026-08-18T10:00:00-04:00",
    },
    {
        "id": "brand-layaway-2026-08-20",
        "pillar": "layaway",
        "caption": "Layaway is free at Valley Pawn. Found something you want but can't grab it all at once? Put a little down, pay it off on your own schedule, and take it home when it's yours. No holding fees, five stores across the Valley.",
        "image": BA + "/valley_pawn_landscape_tight.png",
        "scheduled_at": "2026-08-20T13:00:00-04:00",
    },
    {
        "id": "brand-gold-2026-08-22",
        "pillar": "gold",
        "caption": "We buy gold and silver at all five Valley Pawn stores — rings, coins, bars, sterling, even broken chains. Bring it in for a fair, no-pressure evaluation from people who actually know the metal, and walk out paid the same day.",
        "image": BA + "/valley_pawn_profile_1080.png",
        "scheduled_at": "2026-08-22T11:00:00-04:00",
    },
]

STORE_KEYS = ["Brand", "BrandIG", "BrandTwitter"]

OUT = "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/2026-08-17/brand_publish_results.json"

def flush(results):
    json.dump({"ran_at": datetime.datetime.now().isoformat(), "results": results},
              open(OUT, "w"), indent=2)

p = PublerClient()
results = []
# Skip items already scheduled in a prior (timed-out) run
import os
done_ids = set()
if os.path.exists(OUT):
    try:
        prev = json.load(open(OUT)).get("results", [])
        done_ids = {x["id"] for x in prev if x.get("status") == "SCHEDULED"}
        results = [x for x in prev if x.get("status") == "SCHEDULED"]
    except Exception:
        pass
for it in items:
    if it["id"] in done_ids:
        continue
    r = {"id": it["id"], "pillar": it["pillar"], "routing": STORE_KEYS,
         "scheduled_at": it["scheduled_at"], "char_len": len(it["caption"])}
    problems = qa_check_caption(it["caption"], STORE_KEYS)
    r["qa_problems"] = problems
    if problems:
        r["status"] = "SKIPPED_QA"
        results.append(r); flush(results); continue
    try:
        media = p.upload_media(it["image"], in_library=True, direct_upload=True)
        mid = media.get("id") if isinstance(media, dict) else None
        r["media_id"] = mid
        r["image_method"] = "upload_media"
        if not mid:
            r["status"] = "NO_MEDIA_ID"; r["media_raw"] = str(media)[:200]
            results.append(r); continue
        resp = p.schedule_post(text=it["caption"], store_keys=STORE_KEYS,
                               scheduled_at=it["scheduled_at"], media_ids=[mid])
        r["job_id"] = resp.get("job_id") if isinstance(resp, dict) else None
        r["status"] = "SCHEDULED"
    except Exception as e:
        r["status"] = "ERROR"; r["error"] = repr(e)[:300]
    results.append(r); flush(results)

print(json.dumps(results, indent=2))
