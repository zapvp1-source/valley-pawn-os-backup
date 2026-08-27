#!/usr/bin/env python3
"""
publish_comedy_reels_2026-08-26.py — Lane B3 (vp-comedy-reel-weekly) publish run.

Two videos rendered by vp_comedy_reel.py, both guardrail-PASSed:
  1. hum_seasonal_arrival — "It is that season again" (humor, 1/wk ceiling)
  2. vid_case_walk        — "Walk the case: Roanoke"  (story, no cap)

Both formats were chosen by creative_drift.py select (exploration picks, 40% cold-start
budget, 0 prior posts each) — not hand-picked. The third drift pick,
vid_sixty_second_repair, needs a before/after PHOTO PAIR that does not exist in the
asset library, so it was not rendered rather than faked. Logged, not silently dropped.

Both bits are built from real Bravo intake/jewelry-count data pulled 2026-08-26:
  * seasonal_arrival — the real week of 8/20-8/25 across all 5 stores: 10 chainsaws,
    5 string trimmers, 4 leaf blowers, 3 mowers, and 10 laptops. Nothing invented.
  * case_walk — 2026-08-25_ROA_jewelry-case-counts.csv, verbatim.

Routing per the lane spec: Brand FB Reel + Brand IG Reel + BrandTikTok on every bit,
plus ONE rotating store FB per week — Roanoke this week (Harrisonburg had it 8/22),
which is also the store the case-walk counts belong to.

Captions: every account gets its own text and every caption ends on a question.
Timing: Thursday and Friday evening, inside the lane's Thursday-Saturday window.

Publer gotchas honoured: Bearer-API + browser UA (handled in PublerClient), explicit
from/to on every GET /posts (silently caps at ~15 otherwise), media-ID video body shape
(shape A, proven 2026-08-22), and NO Meta Graph API — every Page token died 2026-08-21.

Idempotent: media uploads and scheduled posts are cached to the results JSON, and a
live Publer duplicate check runs before anything is scheduled.
"""
import json
import sys
import time
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient, PublerError  # noqa: E402

REELS = ROOT / "reels"
RESULTS = ROOT / "manifests" / "comedy_reels_2026-08-26_results.json"

VIDEOS = {
    "seasonal": REELS / "humseasonalarrival20260826endofyar.mp4",
    "casewalk": REELS / "vidcasewalk20260826roanoke.mp4",
}

POSTS = [
    # ---- BIT 1 — vid_case_walk — Roanoke jewelry case, Thursday evening
    {
        "id": "casewalk-brandfb",
        "video": "casewalk",
        "account": "Brand",
        "scheduled_at": "2026-08-27T18:45:00-04:00",
        "text": (
            "We counted the Roanoke jewelry case this week. 564 rings. 97 chains. "
            "89 pairs of earrings. 67 necklaces. 59 charms.\n\n"
            "And two brooches.\n\n"
            "Nobody buys a brooch by accident. Somebody wore each of those to something "
            "that mattered to them, and then life moved and it ended up here. That's "
            "most of what's in a pawn shop case, if you stand there long enough.\n\n"
            "What's the one piece of jewelry in your family nobody's allowed to sell?"
        ),
    },
    {
        "id": "casewalk-brandig",
        "video": "casewalk",
        "account": "BrandIG",
        "scheduled_at": "2026-08-27T18:48:00-04:00",
        "text": (
            "One case. Eleven hundred pieces. Every single one belonged to somebody "
            "before it belonged to a display tray.\n\n"
            "Counted this week at our Roanoke store: 564 rings, 97 chains, 89 pairs of "
            "earrings — and exactly two brooches, which is the detail we can't stop "
            "thinking about.\n\n"
            "Do you still have a piece that was handed down to you?"
        ),
    },
    {
        "id": "casewalk-tiktok",
        "video": "casewalk",
        "account": "BrandTikTok",
        "scheduled_at": "2026-08-27T18:51:00-04:00",
        "text": (
            "Real count, real case, Roanoke Virginia: 564 rings, 97 chains, 67 "
            "necklaces, 59 charms — and two brooches somebody definitely wore to "
            "something important.\n\n"
            "What's the oldest piece of jewelry you own?"
        ),
    },
    {
        "id": "casewalk-roanokefb",
        "video": "casewalk",
        "account": "Roanoke",
        "scheduled_at": "2026-08-27T18:54:00-04:00",
        "text": (
            "This is our case. Counted this week: 564 rings, 129 bracelets, 97 chains, "
            "94 pendants, 89 pairs of earrings, 67 necklaces, 59 charms — and two "
            "brooches.\n\n"
            "Estate gold, class rings, chains somebody wore every day for twenty years. "
            "It's worth taking your time over.\n\n"
            "We're at 2362 Peters Creek Road, Suite C. Come look at the whole case.\n\n"
            "Roanoke — what are you actually hunting for in there?"
        ),
    },
    # ---- BIT 2 — hum_seasonal_arrival — end of the yard season, Friday evening
    {
        "id": "seasonal-brandfb",
        "video": "seasonal",
        "account": "Brand",
        "scheduled_at": "2026-08-28T19:00:00-04:00",
        "text": (
            "Last week of August across our five stores: ten chainsaws, five string "
            "trimmers, four leaf blowers and three mowers came through the door.\n\n"
            "Also ten laptops.\n\n"
            "You can read the calendar off a pawn counter better than off a calendar. "
            "The yard is over. School is not. Every single year, right on schedule.\n\n"
            "Be honest — is your mower done for the season or are you still pretending?"
        ),
    },
    {
        "id": "seasonal-brandig",
        "video": "seasonal",
        "account": "BrandIG",
        "scheduled_at": "2026-08-28T19:03:00-04:00",
        "text": (
            "The counter always knows what month it is.\n\n"
            "This week in the Valley: 10 chainsaws, 5 string trimmers, 4 leaf blowers, "
            "3 mowers — and 10 laptops, right on cue. Late August does this every year "
            "and it has never once surprised us.\n\n"
            "What's the first thing you do when yard season ends?"
        ),
    },
    {
        "id": "seasonal-tiktok",
        "video": "seasonal",
        "account": "BrandTikTok",
        "scheduled_at": "2026-08-28T19:06:00-04:00",
        "text": (
            "Late August in Virginia is ten chainsaws, five trimmers, four leaf blowers, "
            "three mowers — and ten laptops in the same seven days. The season turns and "
            "the counter fills up accordingly.\n\n"
            "What season are you already dreading?"
        ),
    },
]


def _video_body(p: PublerClient, item: dict, media: dict) -> dict:
    """Body shape A — proven against the live API 2026-08-22 (media ID, type "video").
    Do NOT use type "reel" (rejected) or media[].url (Mongoid nil-find). A vertical
    1080x1920 video surfaces as a Reel on FB/IG on its own."""
    meta = p.accounts[item["account"]]
    network = {"facebook": "facebook", "instagram": "instagram",
               "tiktok": "tiktok"}.get(meta["provider"], meta["provider"])
    return {
        "bulk": {
            "state": "scheduled",
            "posts": [{
                "networks": {network: {
                    "type": "video",
                    "text": item["text"],
                    "media": [{"type": "video", "id": media["id"]}],
                }},
                "accounts": [{"id": meta["publer_id"],
                              "scheduled_at": item["scheduled_at"]}],
            }],
        }
    }


def _wait(p: PublerClient, job_id: str, max_seconds: int = 75) -> dict:
    """Publer returns "complete", not "completed" — the shared helper reports a false
    timeout on every video job. Also surfaces payload.failures, where a rejected post
    hides: job status is "complete" even when every account in it failed."""
    deadline = time.time() + max_seconds
    last: dict = {}
    while time.time() < deadline:
        last = p.job_status(job_id) or {}
        if last.get("status") in ("complete", "completed", "failed"):
            return last
        time.sleep(5)
    return last or {"status": "timeout"}


def _flush(state: dict) -> None:
    RESULTS.parent.mkdir(exist_ok=True)
    state["ran_at"] = dt.datetime.now().isoformat()
    RESULTS.write_text(json.dumps(state, indent=2))


def main() -> int:
    p = PublerClient()

    state = {"media": {}, "results": {}}
    if RESULTS.exists():
        try:
            state = json.loads(RESULTS.read_text())
            state.setdefault("media", {})
            state.setdefault("results", {})
        except Exception:
            pass

    # --- live duplicate guard (explicit from/to: GET /posts caps at ~15 without it)
    today = dt.date.today().isoformat()
    week_out = (dt.date.today() + dt.timedelta(days=8)).isoformat()
    live_texts = set()
    try:
        live = p.get("/posts", params={"state": "scheduled", "from": today,
                                       "to": week_out, "limit": "100"})
        live_posts = live.get("posts", live) if isinstance(live, dict) else (live or [])
        for post in live_posts:
            t = (post.get("text") or "")[:60]
            if t:
                live_texts.add(t)
        print(f"duplicate guard: {len(live_posts)} posts already scheduled {today}..{week_out}")
    except PublerError as e:
        print(f"WARN duplicate guard unavailable ({str(e)[:120]}) — relying on results cache")

    # --- upload each video once
    for key, path in VIDEOS.items():
        if key in state["media"]:
            print(f"media cached: {key} -> {state['media'][key]['id']}")
            continue
        if not path.exists():
            print(f"MISSING VIDEO: {path}")
            continue
        try:
            m = p.upload_media(str(path))
            state["media"][key] = {"id": m["id"], "path": m.get("path", "")}
            print(f"uploaded: {key} -> {m['id']}")
            time.sleep(5)
        except PublerError as e:
            print(f"UPLOAD ERROR {key}: {str(e)[:200]}")

    _flush(state)

    # --- schedule
    for item in POSTS:
        rid = item["id"]
        if state["results"].get(rid, {}).get("status") == "SCHEDULED":
            print(f"SKIP (cached): {rid}")
            continue
        if item["text"][:60] in live_texts:
            state["results"][rid] = {"status": "SCHEDULED", "note": "already live on Publer"}
            print(f"SKIP (live on Publer): {rid}")
            continue
        media = state["media"].get(item["video"])
        if not media or not media.get("path"):
            state["results"][rid] = {"status": "NO_MEDIA"}
            print(f"NO_MEDIA: {rid}")
            continue

        time.sleep(10)  # stay well under Publer's rate limit between scheduling calls
        try:
            job = p.post("/posts/schedule", json=_video_body(p, item, media))
            jid = job.get("job_id", "")
            status = _wait(p, jid) if jid else {}
            ok = (status.get("status") in ("complete", "completed")
                  and not (status.get("payload") or {}).get("failures"))
            state["results"][rid] = {
                "status": "SCHEDULED" if ok else f"JOB_{status.get('status', '?')}",
                "account": item["account"],
                "scheduled_at": item["scheduled_at"],
                "video": item["video"],
                "media_id": media["id"],
                "job_id": jid,
                "failures": (status.get("payload") or {}).get("failures") or {},
            }
            print(f"{'SCHEDULED' if ok else 'JOB ' + str(status.get('status'))}: {rid}")
        except PublerError as e:
            state["results"][rid] = {"status": "ERROR", "error": str(e)[:300]}
            print(f"ERROR: {rid}: {str(e)[:200]}")
        _flush(state)

    print("\n=== SUMMARY ===")
    for rid, r in state["results"].items():
        print(f"  {r.get('status'):<14} {rid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
