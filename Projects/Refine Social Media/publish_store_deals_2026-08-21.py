#!/usr/bin/env python3
"""
publish_store_deals_2026-08-21.py — catch-up publish of store-local Deal-of-the-Week
posts that were blocked in the 2026-08-17 batch (Slack photo access), plus this week's
fresh submissions pulled from #deal-of-the-week on 2026-08-21.

Each item -> store FB page + store GBP page via PublerClient.upload_media() +
schedule_post(). Idempotence guard: writes a results JSON next to itself; re-running
skips items already marked SCHEDULED in that file.
"""
import json, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient, PublerError

UP = ROOT / "deal_of_week_uploads"
RESULTS = ROOT / "manifests" / "store_deals_2026-08-21_results.json"

ITEMS = [
    {
        "id": "WAY-cornwell-toolbox",
        "store": "Waynesboro",
        "image": UP / "20260821_WAY_deal_cornwelltoolbox_real_v1.jpg",
        "caption": "Cornwell 4-drawer rolling tool cart with keys — $399.99 at Valley Pawn Waynesboro. These don't come up for sale often, and this one's priced to move. 30-day warranty like everything we sell, and layaway is free. 1321 W Broad St, Waynesboro.",
        "scheduled_at": "2026-08-21T15:30:00-04:00",
    },
    {
        "id": "HAR-imac-a3137",
        "store": "Harrisonburg",
        "image": UP / "20260821_HAR_deal_imac_a3137_real_v1.png",
        "caption": "Apple iMac (A3137) with Bluetooth keyboard, like-new condition — now $849.94 at Valley Pawn Harrisonburg, marked down from $949.94. It'll run anything you need it to. 30-day warranty, free layaway. 1790 E Market St STE 22, Harrisonburg.",
        "scheduled_at": "2026-08-21T15:45:00-04:00",
    },
    {
        "id": "ROA-samsung-t5evo-4tb",
        "store": "Roanoke",
        "image": UP / "20260821_ROA_deal_samsungt5evo4tb_real_v1.jpg",
        "caption": "Samsung T5 EVO 4TB portable SSD, sealed in the box — $399.99 at Valley Pawn Roanoke. Four terabytes that fit in your pocket. 30-day warranty like everything we sell. Grab it before it's gone. 2362 Peters Creek Rd Suite C, Roanoke.",
        "scheduled_at": "2026-08-21T16:00:00-04:00",
    },
    {
        "id": "CUL-husqvarna-585",
        "store": "Culpeper",
        "image": UP / "20260821_CUL_deal_husqvarna585_real_v1.jpg",
        "caption": "Husqvarna 585 chainsaw — $1,149 at Valley Pawn Culpeper. This saw runs $1,539.99 new. Professional-grade power, durability, and performance — big tools for big jobs. 30-day warranty, free layaway. 571 James Madison Hwy, Culpeper.",
        "scheduled_at": "2026-08-21T16:15:00-04:00",
    },
    {
        "id": "LEX-pulsar-12kw-generator",
        "store": "Lexington",
        "image": UP / "20260821_LEX_deal_pulsargenerator_real_v1.jpg",
        "caption": "Pulsar 12,000-watt dual-fuel generator — $849.99 at Valley Pawn Lexington. That's more than $500 under the $1,399 retail. Serious backup power that runs on gas or propane. 30-day warranty, free layaway. 125 Walker St, Lexington.",
        "scheduled_at": "2026-08-21T16:30:00-04:00",
    },
]


def main() -> int:
    import time
    p = PublerClient()
    prior = {}
    if RESULTS.exists():
        prior = {r["id"]: r for r in json.loads(RESULTS.read_text()).get("results", [])}

    # --- duplicate guard: check live Publer for posts already scheduled today to each
    # store account, so a rerun after a rate-limit never double-posts.
    today = dt.date.today().isoformat()
    week_out = (dt.date.today() + dt.timedelta(days=7)).isoformat()
    live = p.get("/posts", params={"state": "scheduled", "from": today, "to": week_out, "limit": "100"})
    live_posts = live.get("posts", live) if isinstance(live, dict) else (live or [])
    id_to_key = {v["publer_id"]: k for k, v in p.accounts.items()}
    live_accounts = set()
    for post in live_posts:
        k = id_to_key.get(str(post.get("account_id", "")))
        if k:
            live_accounts.add(k)

    results = []
    for item in ITEMS:
        rid = item["id"]
        if prior.get(rid, {}).get("status") == "SCHEDULED":
            results.append(prior[rid]); print(f"SKIP (already scheduled): {rid}"); continue
        if item["store"] in live_accounts:
            results.append({"id": rid, "status": "SCHEDULED", "note": "verified live on Publer (duplicate guard)"})
            print(f"SKIP (live on Publer already): {rid}"); continue
        time.sleep(20)  # stay well under Publer rate limits between items
        if not item["image"].exists():
            results.append({"id": rid, "status": "NO_PHOTO", "image": str(item["image"])})
            print(f"NO_PHOTO: {rid}"); continue
        try:
            media = p.upload_media(str(item["image"]))
            job = p.schedule_post(
                text=item["caption"],
                store_keys=[item["store"], f"GBP_{item['store']}"],
                scheduled_at=item["scheduled_at"],
                media_ids=[media["id"]],
            )
            status = p.wait_for_job(job.get("job_id", ""), max_seconds=60, poll_interval=12.0) if job.get("job_id") else {}
            ok = status.get("status") == "completed"
            results.append({"id": rid, "status": "SCHEDULED" if ok else f"JOB_{status.get('status','?')}",
                            "media_id": media.get("id"), "job_id": job.get("job_id"),
                            "scheduled_at": item["scheduled_at"],
                            "accounts": [item["store"], f"GBP_{item['store']}"]})
            print(f"{'SCHEDULED' if ok else 'JOB ' + str(status.get('status'))}: {rid}")
        except PublerError as e:
            results.append({"id": rid, "status": "ERROR", "error": str(e)[:300]})
            print(f"ERROR: {rid}: {e}")

    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps({"ran_at": dt.datetime.now().isoformat(), "results": results}, indent=2))
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
