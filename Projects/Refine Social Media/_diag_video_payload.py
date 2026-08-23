#!/usr/bin/env python3
"""
Diagnostic: find the payload shape Publer actually accepts for a VIDEO post.

Why: schedule_post(video_url=...) returned a job that Publer reported as "complete"
but which produced NO post. Two separate findings so far:
  (1) PublerClient.wait_for_job() waits for status "completed"; Publer returns
      "complete" — so every video job self-reports a false JOB_timeout.
  (2) "complete" still produced no post, so the media-by-URL body is being dropped.

This probes four candidate bodies against the Brand FB page at distinct far-future
timestamps, then reports which ones actually materialise as posts. Test posts are
deleted at the end.
"""
import json, sys, time, datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient, PublerError  # noqa: E402

p = PublerClient()
BRAND = p.accounts["Brand"]["publer_id"]
MEDIA = json.loads((ROOT / "manifests" / "_probe_media_20260822.json").read_text())
MID, PATH = MEDIA["id"], MEDIA["path"]

VARIANTS = {
    "A_video_id": {"type": "video", "media": [{"type": "video", "id": MID}]},
    "B_reel_id_path": {"type": "reel", "media": [{"type": "video", "id": MID, "path": PATH}]},
    "C_video_fullobj": {"type": "video", "media": [MEDIA]},
    "D_video_path": {"type": "video", "media": [{"type": "video", "path": PATH}]},
}

jobs = {}
for i, (name, net) in enumerate(VARIANTS.items()):
    when = f"2026-08-24T0{3 + i}:00:00-04:00"
    body = {
        "bulk": {
            "state": "scheduled",
            "posts": [{
                "networks": {"facebook": dict(net, text=f"DIAGNOSTIC {name} — delete me")},
                "accounts": [{"id": BRAND, "scheduled_at": when}],
            }],
        }
    }
    try:
        r = p.post("/posts/schedule", json=body)
        jobs[name] = {"job_id": r.get("job_id"), "when": when}
        print(f"{name}: job {r.get('job_id')} at {when}")
    except PublerError as e:
        jobs[name] = {"error": str(e)[:250]}
        print(f"{name}: ERROR {str(e)[:250]}")
    time.sleep(6)

print("\nwaiting 45s for jobs to settle...")
time.sleep(45)
for name, j in jobs.items():
    if j.get("job_id"):
        try:
            print(f"{name}: job_status={p.job_status(j['job_id'])}")
        except PublerError as e:
            print(f"{name}: job_status ERROR {str(e)[:150]}")

print("\n--- what actually exists on Publer 8/24 ---")
data = p.get("/posts", params={"state": "scheduled", "from": "2026-08-24",
                               "to": "2026-08-25", "limit": "100"})
posts = data.get("posts", data) if isinstance(data, dict) else (data or [])
found = []
for post in posts:
    txt = (post.get("text") or "")
    if "DIAGNOSTIC" in txt:
        found.append(post)
        print(f"  FOUND {txt[:45]:<48} type={post.get('type')} id={post.get('id')}")
if not found:
    print("  (none of the four variants produced a post)")

print("\n--- cleaning up test posts ---")
for post in found:
    try:
        p.delete_post(post["id"])
        print(f"  deleted {post['id']}")
    except PublerError as e:
        print(f"  delete failed {post['id']}: {str(e)[:120]}")

(ROOT / "manifests" / "_diag_video_payload_result.json").write_text(
    json.dumps({"jobs": jobs, "found": [f.get("text", "")[:60] for f in found]}, indent=2))
