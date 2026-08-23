#!/usr/bin/env python3
"""
restore_publer_queue_2026-08-22.py — incident recovery.

WHAT HAPPENED
-------------
2026-08-22 ~17:00 ET, during the first live vp-deal-reels-weekly publish, a call to
`DELETE /posts` with {"ids": [one_post_id]} — an attempt to remove a single diagnostic
test post — caused Publer to delete EVERY SCHEDULED POST IN THE WORKSPACE. It ignored
the ids array, returned a `deleted_ids` list of unrelated ids, and wiped the queue:

  * 13 deal-reel posts (this task's own — already re-published and verified)
  * ~40 Lane C community posts for 8/23, 8/25, 8/27, 8/29 (5 store FB + 5 GBP)
  * ~10 Lane B3 comedy/story video posts for the evening of 8/22

Published history was NOT affected. Both other lanes wrote their manifests to disk
before publishing, so the queue is fully reconstructible — which is why this script
exists instead of a "sorry, they're gone" note. Fix-forward: overcome the failure.

WHAT IT DOES
------------
Re-schedules the Lane C and Lane B3 items from their own on-disk manifests, skipping
anything already live on Publer (checked with explicit from/to). Video posts go by
media **id**, never url — passing a url returns a "complete" job and creates no post.

    python3 restore_publer_queue_2026-08-22.py [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from publer_client import PublerError  # noqa: E402
from vp_deal_reel_publish import ReelPublisher, _text_of  # noqa: E402

LANE_C = ROOT / "_lane_c" / "manifest_2026-08-22.json"
COMEDY = ROOT / "publish_comedy_reels_2026-08-22.py"
RESULTS = ROOT / "manifests" / "restore_queue_2026-08-22_results.json"


def load_comedy_posts():
    spec = importlib.util.spec_from_file_location("_comedy", COMEDY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.POSTS, {k: Path(v) for k, v in mod.VIDEOS.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sleep", type=float, default=1.5)
    args = ap.parse_args()

    p = ReelPublisher()
    id2k = {v["publer_id"]: k for k, v in p.accounts.items()}

    def live_index() -> set[tuple[str, str]]:
        d = p.get("/posts", params={"state": "scheduled", "from": "2026-08-22",
                                    "to": "2026-09-05", "limit": "300"})
        posts = d.get("posts", d) if isinstance(d, dict) else (d or [])
        return {(id2k.get(str(x.get("account_id"))) or "?", _text_of(x)[:60]) for x in posts}

    live = live_index()
    prior = {}
    if RESULTS.exists():
        prior = {r["key"]: r for r in json.loads(RESULTS.read_text()).get("results", [])}
    results: list[dict] = []

    def flush():
        if args.dry_run:
            return
        merged = dict(prior)
        for r in results:
            merged[r["key"]] = r
        RESULTS.write_text(json.dumps(
            {"ran_at": dt.datetime.now().isoformat(), "results": list(merged.values())}, indent=2))

    # ---------------- Lane C: text-only community posts ----------------
    lane_c = json.loads(LANE_C.read_text())["items"]
    for it in lane_c:
        for acct in it["store_keys"]:
            key = f"C::{it['id']}::{acct}"
            if prior.get(key, {}).get("status") == "SCHEDULED":
                results.append(prior[key]); continue
            if (acct, it["caption"][:60]) in live:
                results.append({"key": key, "status": "SCHEDULED", "note": "already live"})
                continue
            if args.dry_run:
                print(f"DRY  C {acct:18s} {it['scheduled_at']} {it['caption'][:40]}")
                results.append({"key": key, "status": "DRY_RUN"}); continue
            try:
                job = p.schedule_post(text=it["caption"], store_keys=[acct],
                                      scheduled_at=it["scheduled_at"])
                st = p.wait_for_job(job.get("job_id", ""), max_seconds=40, poll_interval=4.0)
                fails = (st.get("payload") or {}).get("failures") or {}
                ok = st.get("status") == "completed" and not fails
                results.append({"key": key, "status": "SCHEDULED" if ok else "ERROR",
                                "account": acct, "scheduled_at": it["scheduled_at"],
                                "error": None if ok else json.dumps(st)[:200]})
                print(f"{'RESTORED' if ok else 'ERROR   '} C {acct:18s} {it['scheduled_at']}")
            except Exception as e:
                results.append({"key": key, "status": "ERROR", "error": str(e)[:250]})
                print(f"ERROR    C {acct}: {str(e)[:120]}")
            flush()
            time.sleep(args.sleep)

    # ---------------- Lane B3: comedy / story videos ----------------
    posts, videos = load_comedy_posts()
    media: dict[str, str] = {r["key"].split("::")[-1]: r["media_id"]
                             for r in prior.values() if r.get("media_id")}
    for post in posts:
        key = f"B3::{post['id']}"
        if prior.get(key, {}).get("status") == "SCHEDULED":
            results.append(prior[key]); continue
        if (post["account"], post["text"][:60]) in live:
            results.append({"key": key, "status": "SCHEDULED", "note": "already live"}); continue
        vpath = videos[post["video"]]
        if not vpath.exists():
            results.append({"key": key, "status": "NO_VIDEO", "video": str(vpath)})
            print(f"NO_VIDEO B3 {post['id']}"); continue
        if args.dry_run:
            print(f"DRY  B3 {post['account']:14s} {post['scheduled_at']} {post['text'][:40]}")
            results.append({"key": key, "status": "DRY_RUN"}); continue
        try:
            mid = media.get(post["video"])
            if not mid:
                mid = p.upload_media(str(vpath))["id"]
                media[post["video"]] = mid
                results.append({"key": f"B3::_media::{post['video']}", "status": "UPLOADED",
                                "media_id": mid})
                flush()
            job = p.schedule_video(text=post["text"], account_key=post["account"],
                                   media_id=mid, scheduled_at=post["scheduled_at"],
                                   kind="video")
            st = p.wait_for_job(job.get("job_id", ""), max_seconds=45, poll_interval=5.0)
            fails = (st.get("payload") or {}).get("failures") or {}
            ok = st.get("status") == "completed" and not fails
            results.append({"key": key, "status": "SCHEDULED" if ok else "ERROR",
                            "account": post["account"], "scheduled_at": post["scheduled_at"],
                            "media_id": mid, "error": None if ok else json.dumps(st)[:200]})
            print(f"{'RESTORED' if ok else 'ERROR   '} B3 {post['account']:14s} {post['scheduled_at']}")
        except Exception as e:
            results.append({"key": key, "status": "ERROR", "error": str(e)[:250]})
            print(f"ERROR    B3 {post['id']}: {str(e)[:120]}")
        flush()
        time.sleep(args.sleep)

    flush()
    ok = sum(1 for r in results if r["status"] == "SCHEDULED")
    print(f"\n== restored/confirmed {ok} of {len(results)} queue items ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
