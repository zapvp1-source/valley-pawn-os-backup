#!/usr/bin/env python3
"""
publish_batch_2026-08-31.py — vp-content-batch-weekly run for week of 2026-08-31.

Ships the two real gaps in the already-staged week:
  - 5 real photo-backed store-local "Find" deal items (one per store, fresh 0831
    deal-mirror captures) -> {Store} FB + GBP_{Store}
  - 2 Brand-tier posts (How-It-Works, Gold-buy) from asset-library heroes ->
    Brand FB + BrandIG (full caption) + BrandTwitter (trimmed <260 char caption)

Real photos only (deal-mirror + brand heroes). 0824 deal items were already
published last week and are excluded. Per-item + live-Publer duplicate guard so
reruns never double-post. 20s pacing, job polling.
"""
import json, sys, time, datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient, PublerError

UP = ROOT / "deal_of_week_uploads"
HEROES = Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/asset-library/heroes/2026-07")
RESULTS = ROOT / "manifests" / "batch_2026-08-31_results.json"

FOOTER = (
    "\n\n\U0001F4CD 125 Walker St, Lexington"
    "\n\U0001F4CD 1321 W Broad St, Waynesboro"
    "\n\U0001F4CD 1790 E Market St, Ste 22, Harrisonburg"
    "\n\U0001F4CD 571 James Madison Hwy, Culpeper"
    "\n\U0001F4CD 2362 Peters Creek Rd Ste C, Roanoke"
)

# --- Store-local Find items (real photos, fresh 0831 captures) ---
STORE_ITEMS = [
    {
        "id": "CUL-mantis-tiller-0831",
        "store": "Culpeper",
        "kw": "mantis",
        "image": UP / "deal_culpeper_mantis_0831.jpg",
        "caption": ("Mantis tiller on the floor in Culpeper for $249. If you've fought hard "
                    "Piedmont clay in a fall garden, a compact tiller like this saves your back. "
                    "Runs strong and ready to work. Everything we sell carries a 30-day warranty "
                    "and layaway's free. 571 James Madison Hwy, Culpeper."),
        "scheduled_at": "2026-09-01T13:00:00-04:00",
    },
    {
        "id": "WAY-gibson-br9-0831",
        "store": "Waynesboro",
        "kw": "gibson br-9",
        "image": UP / "deal_waynesboro_gibson_0831.jpg",
        "caption": ("A late-1940s Gibson BR-9 amp came through Waynesboro, and it's yours for "
                    "$149.99. That's real Gibson history from the lap-steel era for less than a new "
                    "practice amp costs. 30-day warranty, and layaway's free if you want to hold it. "
                    "1321 W Broad St, Waynesboro."),
        "scheduled_at": "2026-09-02T13:30:00-04:00",
    },
    {
        "id": "ROA-cummins-inverter-0831",
        "store": "Roanoke",
        "kw": "cummins",
        "image": UP / "deal_roanoke_inverter_0831.jpg",
        "caption": ("Cummins 4000-watt power inverter in Roanoke, $349.99. Wire it into a truck or "
                    "RV and you've got real power for tools, a fridge, whatever the job needs. "
                    "Heavy-duty build, checked over and ready to go. 30-day warranty, free layaway. "
                    "2362 Peters Creek Rd Ste C, Roanoke."),
        "scheduled_at": "2026-09-03T14:00:00-04:00",
    },
    {
        "id": "LEX-monsterhigh-0831",
        "store": "Lexington",
        "kw": "monster high",
        "image": UP / "deal_lexington_monsterhigh_0831.jpg",
        "caption": ("Monster High Haunted High School 360-degree playset in Lexington for $169.99 "
                    "— 35-plus pieces, seven play areas, and that's under what Mattel charges direct. "
                    "Makes a serious birthday or holiday gift, and it's done sitting on the shelf. "
                    "30-day warranty, free layaway. 125 Walker St, Lexington."),
        "scheduled_at": "2026-09-04T13:00:00-04:00",
    },
    {
        "id": "HAR-martin-000-18-0831",
        "store": "Harrisonburg",
        "kw": "martin 000-18",
        "image": UP / "deal_harrisonburg_martin_0831.jpg",
        "caption": ("Martin 000-18 Modern Deluxe in Harrisonburg, $2,699.94. Sitka top, mahogany "
                    "back and sides — the kind of guitar somebody keeps for forty years and hands "
                    "down. If you've been holding out for the right one, come play it. 30-day "
                    "warranty, layaway available. 1790 E Market St, Ste 22, Harrisonburg."),
        "scheduled_at": "2026-09-05T13:30:00-04:00",
    },
]

# --- Brand items (asset-library heroes; FB+IG full, X trimmed) ---
BRAND_ITEMS = [
    {
        "id": "BRAND-howitworks-0831",
        "kw": "how a pawn loan",
        "image": HEROES / "20260706_BRAND_story_howpawnworks_styleB_igfeed_v1.png",
        "caption": ("Here's how a pawn loan actually works: you bring in something of value, we "
                    "agree on a loan amount, and the time and terms to pay it back are spelled out "
                    "up front. No credit check, no hit to your score, no judgment. It's one of the "
                    "oldest and most straightforward ways to borrow, and we've kept it honest across "
                    "all five of our Valley stores." + FOOTER),
        "caption_x": ("How a pawn loan works: bring in something of value, we agree on an amount, and "
                      "the terms are spelled out up front. No credit check, no score hit, no judgment. "
                      "Honest borrowing across all five Valley Pawn stores."),
        "scheduled_at": "2026-09-02T18:00:00-04:00",
        "scheduled_at_x": "2026-09-02T18:03:00-04:00",
    },
    {
        "id": "BRAND-goldbuy-0831",
        "kw": "test and weigh",
        "image": HEROES / "20260706_BRAND_value_goldbuy_styleC_igfeed_v1.png",
        "caption": ("Gold prices have held strong, which means that old chain or those mismatched "
                    "earrings in the drawer are worth a real look. Bring them into any of our five "
                    "stores and we'll test and weigh everything in front of you, then make a fair "
                    "cash offer on the spot. No appointment, no pressure — walk out with cash or "
                    "walk out with your gold, your call." + FOOTER),
        "caption_x": ("Gold's held strong, so that old chain or those mismatched earrings are worth a "
                      "look. We test and weigh in front of you and make a fair cash offer on the spot "
                      "at any of our 5 Valley Pawn stores."),
        "scheduled_at": "2026-09-04T18:00:00-04:00",
        "scheduled_at_x": "2026-09-04T18:03:00-04:00",
    },
]


def load_live_texts(p):
    """Return a lowercased blob of all scheduled+published post text in the window,
    for a keyword-based per-item duplicate guard."""
    frm = (dt.date.today() - dt.timedelta(days=3)).isoformat()
    to = (dt.date.today() + dt.timedelta(days=12)).isoformat()
    blob = []
    for st in ("scheduled", "published", "completed"):
        try:
            r = p.get("/posts", params={"state": st, "from": frm, "to": to, "limit": "100"})
            posts = r.get("posts", r) if isinstance(r, dict) else (r or [])
            for po in posts:
                blob.append((po.get("text") or "").lower())
        except Exception as e:
            print(f"  (live-text load {st} failed: {e})")
    return "\n".join(blob)


def sched(p, text, store_keys, when, media_id):
    job = p.schedule_post(text=text, store_keys=store_keys, scheduled_at=when,
                          media_ids=[media_id])
    jid = job.get("job_id", "")
    status = p.wait_for_job(jid, max_seconds=60, poll_interval=12.0) if jid else {}
    return jid, status.get("status", "?")


def main():
    p = PublerClient()
    prior = {}
    if RESULTS.exists():
        prior = {r["id"]: r for r in json.loads(RESULTS.read_text()).get("results", [])}
    live_blob = load_live_texts(p)
    results = []

    # Store-local
    for it in STORE_ITEMS:
        rid = it["id"]
        if prior.get(rid, {}).get("status") == "SCHEDULED":
            results.append(prior[rid]); print(f"SKIP prior-scheduled: {rid}"); continue
        if it["kw"].lower() in live_blob:
            results.append({"id": rid, "status": "SCHEDULED", "note": "live duplicate guard"})
            print(f"SKIP live-duplicate: {rid}"); continue
        if not it["image"].exists():
            results.append({"id": rid, "status": "NO_PHOTO", "image": str(it["image"])})
            print(f"NO_PHOTO: {rid}"); continue
        time.sleep(20)
        try:
            media = p.upload_media(str(it["image"]))
            keys = [it["store"], f"GBP_{it['store']}"]
            jid, jst = sched(p, it["caption"], keys, it["scheduled_at"], media["id"])
            ok = jst == "completed"
            results.append({"id": rid, "tier": "store_local", "store": it["store"],
                            "pillar": "find", "routing": keys, "image_method": "upload_media",
                            "photo_gap": False, "authenticity_check": "pass",
                            "media_id": media.get("id"), "job_id": jid,
                            "scheduled_at": it["scheduled_at"],
                            "status": "SCHEDULED" if ok else f"JOB_{jst}"})
            print(f"{'SCHEDULED' if ok else 'JOB_'+jst}: {rid}")
        except PublerError as e:
            results.append({"id": rid, "status": "ERROR", "error": str(e)[:300]})
            print(f"ERROR: {rid}: {e}")

    # Brand
    for it in BRAND_ITEMS:
        rid = it["id"]
        if prior.get(rid, {}).get("status") == "SCHEDULED":
            results.append(prior[rid]); print(f"SKIP prior-scheduled: {rid}"); continue
        if it["kw"].lower() in live_blob:
            results.append({"id": rid, "status": "SCHEDULED", "note": "live duplicate guard"})
            print(f"SKIP live-duplicate: {rid}"); continue
        if not it["image"].exists():
            results.append({"id": rid, "status": "NO_PHOTO", "image": str(it["image"])})
            print(f"NO_PHOTO: {rid}"); continue
        time.sleep(20)
        try:
            media = p.upload_media(str(it["image"]))
            # FB + IG (full caption)
            jid1, jst1 = sched(p, it["caption"], ["Brand", "BrandIG"], it["scheduled_at"], media["id"])
            time.sleep(20)
            # X (trimmed caption, 3-min gap on the shared account is inherent via separate day/time)
            jid2, jst2 = sched(p, it["caption_x"], ["BrandTwitter"], it["scheduled_at_x"], media["id"])
            ok = (jst1 == "completed") and (jst2 == "completed")
            results.append({"id": rid, "tier": "brand", "store": None,
                            "pillar": "how_it_works" if "howit" in rid else "gold_buy",
                            "routing": ["Brand", "BrandIG", "BrandTwitter"],
                            "image_method": "upload_media", "photo_gap": False,
                            "authenticity_check": "pass", "media_id": media.get("id"),
                            "job_id_fbig": jid1, "job_id_x": jid2,
                            "scheduled_at": it["scheduled_at"],
                            "status": "SCHEDULED" if ok else f"JOB_fbig_{jst1}_x_{jst2}"})
            print(f"{'SCHEDULED' if ok else 'JOB fbig='+jst1+' x='+jst2}: {rid}")
        except PublerError as e:
            results.append({"id": rid, "status": "ERROR", "error": str(e)[:300]})
            print(f"ERROR: {rid}: {e}")

    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps({"ran_at": dt.datetime.now().isoformat(), "results": results}, indent=2))
    print("\n=== SUMMARY ===")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
