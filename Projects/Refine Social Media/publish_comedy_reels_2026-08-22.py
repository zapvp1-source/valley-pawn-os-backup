#!/usr/bin/env python3
"""
publish_comedy_reels_2026-08-22.py — Lane B3 (vp-comedy-reel-weekly) publish run.

Three videos rendered by vp_comedy_reel.py, all guardrail-PASSed:
  1. hum_object_pov  — POV: the pool robot           (humor, 1/wk ceiling)
  2. vid_walked_in   — What walked in this week      (story, no cap)
  3. vid_one_object  — One object: the Yamaha P-125A (story, no cap)

Routing per the lane spec: Brand FB Reel + Brand IG Reel + BrandTikTok on every bit,
plus ONE rotating store FB per week — Harrisonburg this week, because the 2026-08-22
audit found Harrisonburg at 13 posts/90d vs Culpeper's 111 and directed that it be
weighted first until parity. It also happens to be the store the P-125A came through.

Captions: every account gets its own text (the audit found 76% of captioned posts
reused a caption verbatim, several 3-4x on the SAME page) and every caption ends on a
question so the bit has somewhere to go in the comments (18 comments / 0 replies in 90d
is the baseline being attacked).

Timing: Saturday evening, inside the lane's Thursday-Saturday window. All three ship
in the current window rather than borrowing next week's slots from the Wed 8/26 run.

Publer gotchas honoured: Bearer-API + browser UA (handled in PublerClient), explicit
from/to on every GET /posts (it silently caps at ~15 otherwise), and NO Meta Graph API
anywhere -- every Page token died 2026-08-21.

Idempotent: media uploads and scheduled posts are both cached to the results JSON, and
a live Publer duplicate check runs before anything is scheduled.
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
RESULTS = ROOT / "manifests" / "comedy_reels_2026-08-22_results.json"

VIDEOS = {
    "poolrobot": REELS / "humobjectpov20260822poolrobot.mp4",
    "walkedin": REELS / "vidwalkedin20260822.mp4",
    "p125a": REELS / "vidoneobject20260822p125a.mp4",
}

POSTS = [
    # ---- BIT 1 — hum_object_pov — the pool robot (Maytronics Dolphin Explorer E25, Roanoke)
    {
        "id": "poolrobot-brandfb",
        "video": "poolrobot",
        "account": "Brand",
        "scheduled_at": "2026-08-22T18:50:00-04:00",
        "text": (
            "It has never seen the sun. It has never met the family. It works the deep "
            "end alone and it has never once complained about it.\n\n"
            "A Maytronics Dolphin Explorer E25 — a robot whose entire life is cleaning "
            "somebody else's pool — came across our counter in Roanoke. Half of what "
            "ends up on our floor arrives with a story like that attached.\n\n"
            "What's the oddest thing you've ever owned that did a job better than you did?"
        ),
    },
    {
        "id": "poolrobot-brandig",
        "video": "poolrobot",
        "account": "BrandIG",
        "scheduled_at": "2026-08-22T18:53:00-04:00",
        "text": (
            "Full-time job: the deep end. No days off, no sunlight, no small talk.\n\n"
            "This Dolphin Explorer E25 pool robot came through our Roanoke store, and "
            "it is easily the most single-minded thing we've had on the floor all month.\n\n"
            "What's the strangest thing you've ever seen in a pawn shop?"
        ),
    },
    {
        "id": "poolrobot-tiktok",
        "video": "poolrobot",
        "account": "BrandTikTok",
        "scheduled_at": "2026-08-22T18:56:00-04:00",
        "text": (
            "The pool robot has opinions about the deep end. It's simply not going to "
            "share them. Real item, real counter — Valley Pawn, Roanoke, Virginia.\n\n"
            "If one appliance in your house could talk, which one would you least want to hear from?"
        ),
    },
    # ---- BIT 2 — vid_walked_in — this week's real submissions (8/17)
    {
        "id": "walkedin-brandfb",
        "video": "walkedin",
        "account": "Brand",
        "scheduled_at": "2026-08-22T19:55:00-04:00",
        "text": (
            "Three things that walked through the door this week with nothing whatsoever "
            "to do with each other: a Husqvarna 585 chainsaw in Culpeper, a 12,000-watt "
            "dual fuel generator in Lexington, and a 3,300 PSI pressure washer with a "
            "Honda engine on it in Roanoke.\n\n"
            "Nobody coordinated that. Nobody ever does. That's the whole job.\n\n"
            "Which one are you grabbing first?"
        ),
    },
    {
        "id": "walkedin-brandig",
        "video": "walkedin",
        "account": "BrandIG",
        "scheduled_at": "2026-08-22T19:58:00-04:00",
        "text": (
            "Chainsaw. Generator. Pressure washer. Three towns, one week, zero "
            "coordination between any of them.\n\n"
            "This is what the counter actually looks like — you find out what's coming "
            "when it gets here.\n\n"
            "Which of the three would you take home?"
        ),
    },
    {
        "id": "walkedin-tiktok",
        "video": "walkedin",
        "account": "BrandTikTok",
        "scheduled_at": "2026-08-22T20:01:00-04:00",
        "text": (
            "Nobody plans a pawn shop. A Husqvarna 585, a 12,000-watt dual fuel "
            "generator and a Honda-powered pressure washer all turned up in the same "
            "week across three different Virginia towns.\n\n"
            "Which one are you calling dibs on?"
        ),
    },
    # ---- BIT 3 — vid_one_object — Yamaha P-125A (Harrisonburg)
    {
        "id": "p125a-brandfb",
        "video": "p125a",
        "account": "Brand",
        "scheduled_at": "2026-08-22T21:00:00-04:00",
        "text": (
            "Eighty-eight weighted keys.\n\n"
            "Somebody learned on this one. Somebody sat down and played the same eight "
            "bars over and over until they finally came out right, then came back the "
            "next day and did it again. None of that shows up on a price tag.\n\n"
            "This Yamaha P-125A came through our Harrisonburg store.\n\n"
            "What did you learn to play on?"
        ),
    },
    {
        "id": "p125a-brandig",
        "video": "p125a",
        "account": "BrandIG",
        "scheduled_at": "2026-08-22T21:03:00-04:00",
        "text": (
            "Every second-hand instrument shows up with somebody's practice hours "
            "already in it.\n\n"
            "This Yamaha P-125A — 88 fully weighted keys — came through Harrisonburg. "
            "Whoever had it before put the work in. We just look after it until the "
            "next set of hands.\n\n"
            "What was the first song you ever learned all the way through?"
        ),
    },
    {
        "id": "p125a-tiktok",
        "video": "p125a",
        "account": "BrandTikTok",
        "scheduled_at": "2026-08-22T21:06:00-04:00",
        "text": (
            "88 weighted keys with somebody's practice hours already baked in. Yamaha "
            "P-125A, Harrisonburg, Virginia. Every used instrument is somebody's old "
            "routine passed along.\n\n"
            "What did you learn to play on?"
        ),
    },
    {
        "id": "p125a-harrisonburgfb",
        "video": "p125a",
        "account": "Harrisonburg",
        "scheduled_at": "2026-08-22T21:09:00-04:00",
        "text": (
            "This Yamaha P-125A came through our Harrisonburg store — 88 fully weighted "
            "keys, and it has been played. Somebody worked the same eight bars on it "
            "until they got them right.\n\n"
            "That's what a good used instrument is: the hours are already in it.\n\n"
            "We're at 1790 E Market St STE 22 — come put your hands on it. "
            "Harrisonburg, what did you learn to play on?"
        ),
    },
]


def _video_body(p: PublerClient, item: dict, media: dict) -> dict:
    """Build the ONE video body shape Publer actually accepts.

    Proven by _diag_video_payload.py on 2026-08-22 against the live API:
      A  {"type":"video","media":[{"type":"video","id": MID}]}   -> post created, 0 failures
      C  {"type":"video","media":[<full /media object>]}          -> post created, 0 failures
      B  {"type":"reel", ...}                                     -> "Post type is not valid"
      D  {"type":"video","media":[{"type":"video","url": PATH}]}  -> Mongoid nil-find error
    D is exactly what PublerClient.schedule_post(video_url=...) sends, which is why the
    first attempt produced jobs that reported success and created nothing. Use the media
    ID. A vertical 1080x1920 video surfaces as a Reel on FB/IG on its own; asking for
    type "reel" explicitly is rejected.
    """
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
    """Local wait loop. PublerClient.wait_for_job() only accepts "completed"; Publer
    actually returns "complete", so the shared helper reports a false timeout on every
    video job. Also surfaces payload.failures, which is where a rejected post hides -
    job status is "complete" even when every account in it failed."""
    deadline = time.time() + max_seconds
    last: dict = {}
    while time.time() < deadline:
        last = p.job_status(job_id) or {}
        if last.get("status") in ("complete", "completed", "failed"):
            return last
        time.sleep(5)
    return last or {"status": "timeout"}


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


def _flush(state: dict) -> None:
    RESULTS.parent.mkdir(exist_ok=True)
    state["ran_at"] = dt.datetime.now().isoformat()
    RESULTS.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    sys.exit(main())
