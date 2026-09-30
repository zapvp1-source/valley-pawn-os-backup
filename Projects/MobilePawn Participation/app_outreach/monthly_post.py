#!/usr/bin/env python3
"""MobilePawn app-download social post — once a month, all Valley Pawn pages.

Schedules (via the one sanctioned path, Refine Social Media/vp_social_publisher.py) for the
2nd Tuesday of the target month at 11:00 AM ET:
  * Brand FB + Brand IG   — graphics/mobilepawn_brand.png
  * each store FB + GBP   — graphics/mobilepawn_<store>.png (store-named, passes image gate)
Link: thevalleypawn.com/app (smart redirect to App Store / Google Play), UTM-tagged per page.
Idempotent: skips a month already in sent_log.json. Built 2026-09-29 (Joshua: "go").

    python3 monthly_post.py                 # next month
    python3 monthly_post.py --month 2026-10 [--dry-run]
"""
import argparse, calendar, datetime as dt, json, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
SOCIAL = HERE.parent.parent / "Refine Social Media"
sys.path.insert(0, str(SOCIAL))
from publer_client import PublerClient  # noqa: E402

STORES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
STATE = HERE / "media_ids.json"
LOG = HERE / "sent_log.json"
ET = ZoneInfo("America/New_York")

FB = [  # rotate by month; no phone numbers, no weekday/hours claims
    "Pay your loan without making the trip. With the free MobilePawn app you can pay or extend your {who} loan, make layaway payments and check your due dates right from your phone.\n\nDownload it here: {link}\nOpen the app and choose Valley Pawn to connect your account.",
    "Busy week? Skip the drive. The free MobilePawn app lets you pay or extend your loan and make layaway payments from anywhere, anytime.\n\nGet it here: {link}\nPick Valley Pawn in the app to link your account.",
    "Never miss a due date again. MobilePawn shows your {who} loans and layaways, sends reminders and lets you pay from your phone. It's free.\n\nDownload: {link}",
]
GBP = [  # Google: no hashtags, no phone numbers
    "Pay or extend your loan and make layaway payments from your phone with the free MobilePawn app. Download it at {link} and choose Valley Pawn {store}.",
    "Skip the trip. The free MobilePawn app lets you pay loans, make layaway payments and check due dates anytime. Get it at {link}",
    "Never miss a due date. Track your Valley Pawn {store} loans and layaways and pay from your phone with the free MobilePawn app: {link}",
]


def nth_weekday(y, m, wd, n):
    days = [d for d in range(1, calendar.monthrange(y, m)[1] + 1) if dt.date(y, m, d).weekday() == wd]
    return dt.date(y, m, days[n - 1])


def link(content, month):
    return f"https://thevalleypawn.com/app/?utm_source=social&utm_medium={content.split('_')[0]}&utm_campaign=mobilepawn_{month}&utm_content={content}"


def media_ids(p):
    ids = json.loads(STATE.read_text()) if STATE.exists() else {}
    for key in ["brand"] + [s.lower() for s in STORES]:
        if key not in ids:
            r = p.upload_media(str(HERE / "graphics" / f"mobilepawn_{key}.png"))
            ids[key] = r.get("id") or r.get("media", {}).get("id")
            if not ids[key]:
                raise SystemExit(f"upload failed for {key}: {r}")
    STATE.write_text(json.dumps(ids, indent=2))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    today = dt.date.today()
    if a.month:
        y, m = map(int, a.month.split("-"))
    else:
        y, m = (today.year + (today.month == 12), today.month % 12 + 1)
    month = f"{y}-{m:02d}"
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    if month in log and not a.dry_run:
        print(f"{month} already scheduled — nothing to do"); return
    when = dt.datetime.combine(nth_weekday(y, m, 1, 2), dt.time(11, 0), ET)
    if when <= dt.datetime.now(ET) + dt.timedelta(minutes=10):
        raise SystemExit(f"{month}: send time {when} already passed")
    v = (m - 1) % 3
    p = PublerClient()
    ids = {"brand": "DRY", **{s.lower(): "DRY" for s in STORES}} if a.dry_run else media_ids(p)
    iso = when.isoformat()
    items = [{"id": f"mp-{month}-brand", "routing_tier": "brand", "store_keys": ["Brand", "BrandIG"],
              "caption": FB[v].format(who="Valley Pawn", link=link("fb_brand", month)),
              "media_ids": [ids["brand"]], "scheduled_at": iso, "status": "approved"}]
    for s in STORES:
        items.append({"id": f"mp-{month}-{s.lower()}-fb", "routing_tier": "store-local", "store_keys": [s],
                      "caption": FB[v].format(who=f"Valley Pawn {s}", link=link(f"fb_{s.lower()}", month)),
                      "media_ids": [ids[s.lower()]], "scheduled_at": iso, "status": "approved"})
        items.append({"id": f"mp-{month}-{s.lower()}-gbp", "routing_tier": "store-local", "store_keys": [f"GBP_{s}"],
                      "caption": GBP[v].format(store=s, link=link(f"gbp_{s.lower()}", month).replace("https://", "")),
                      "media_ids": [ids[s.lower()]], "scheduled_at": iso, "status": "approved"})
    man = HERE / "manifests" / f"manifest_{month}.json"
    man.parent.mkdir(exist_ok=True)
    man.write_text(json.dumps({"batch_id": f"mobilepawn-{month}", "items": items}, indent=2))
    cmd = [sys.executable, str(SOCIAL / "vp_social_publisher.py"), str(man)] + (["--dry-run"] if a.dry_run else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-1500:])
    res_path = man.with_name(man.stem + "_results.json")
    if a.dry_run:
        return
    # Verify against Publer itself (Rule 12): every item needs a job that completed with no failures.
    res = sorted(man.parent.glob(man.stem + "_publish_results_*.json"))[-1]
    results = json.loads(res.read_text())["results"]
    bad = [x.get("id") for x in results if not x.get("job_id")]
    for x in results:
        if x.get("job_id"):
            js = p.wait_for_job(x["job_id"], max_seconds=90)
            pl = js.get("payload") if isinstance(js.get("payload"), dict) else {}
            if js.get("status") != "complete" or pl.get("failures"):
                bad.append(x.get("id"))
    if r.returncode != 0 or bad or len(results) != len(items):
        raise SystemExit(f"{month}: not all posts scheduled — {bad}")
    log[month] = {"scheduled_for": iso, "items": len(items), "at": dt.datetime.now(ET).isoformat()}
    LOG.write_text(json.dumps(log, indent=2))
    print(f"OK {month}: {len(items)} posts scheduled for {iso}")


if __name__ == "__main__":
    main()
