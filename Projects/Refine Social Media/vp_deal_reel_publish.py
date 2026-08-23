#!/usr/bin/env python3
"""
vp_deal_reel_publish.py — the reusable publish leg of Lane B1 (vp-deal-reels-weekly).

Takes a plan JSON, uploads each reel to Publer ONCE, and schedules one post per
target account with that account's OWN caption. Routes every call through
PublerClient — no raw one-off request code (the 2026-08-21 catch-up bypassed the
hardened client and that is the rule this file exists to stop repeating).

WHY PER-ACCOUNT CAPTIONS ARE SEPARATE POSTS
-------------------------------------------
PublerClient.schedule_post() applies one text to every network in the call.
PILLAR_OVERLAY §6 forbids byte-identical captions across accounts, so each
account gets its own schedule_post() call with its own text. That also lets us
stagger each account independently.

TWO SILENT-FAILURE MODES THIS FILE EXISTS TO SURVIVE (found live 2026-08-22)
---------------------------------------------------------------------------
Publer will happily return a job whose status is "complete" and create NO POST.
It does this when (a) media is passed by `url` instead of library `id`, and
(b) `type` is "reel" instead of "video". Twelve posts vanished that way before
anyone checked the live list. So: media by id, type "video", and every run
finishes by diffing the plan against Publer's actual post list (Rule 12) — a
manifest saying "12 scheduled" is not evidence.

IDEMPOTENCE
-----------
Results are written to manifests/<plan-stem>_results.json. A rerun skips anything
already SCHEDULED there, and also re-checks live Publer (explicit from/to params —
GET /posts silently caps at ~15 results without them) so a rerun after a timeout
never double-posts.

PLAN FORMAT
    {
      "week": "2026-08-22",
      "items": [
        {"id": "CUL-husqvarna-585",
         "video": "reels/publish/....mp4",
         "targets": [
            {"account": "Culpeper", "kind": "reel",
             "scheduled_at": "2026-08-22T18:45:00-04:00",
             "caption": "..."},
            {"account": "BrandIG", ...}
         ]}
      ]
    }

USAGE
    python3 vp_deal_reel_publish.py --plan manifests/deal_reels_2026-08-22.json
    python3 vp_deal_reel_publish.py --plan ... --dry-run
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from publer_client import PublerClient, PublerError  # noqa: E402

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


class ReelPublisher(PublerClient):
    """PublerClient + the two Publer gotchas this fleet keeps rediscovering."""

    def _headers(self) -> dict:
        h = super()._headers()
        # Cloudflare returns `error code: 1010` without a browser User-Agent.
        # A 403 here does NOT mean the API key is dead.
        h["User-Agent"] = BROWSER_UA
        return h

    def _request(self, method: str, path: str, **kw):
        # ---- HARD GUARD, added 2026-08-22 after a live incident ----
        # `DELETE /posts` with {"ids": [one_id]} does NOT delete that one post.
        # Publer ignores the ids array and DELETES EVERY SCHEDULED POST IN THE
        # WORKSPACE. It wiped 63 queued posts across three lanes in one call and
        # still returned a cheerful deleted_ids list of unrelated ids.
        # There is no known safe single-post delete on this API version. If a bad
        # post must go, remove it by hand in the Publer UI.
        if method.upper() == "DELETE" and path.rstrip("/").endswith("/posts"):
            raise PublerError(
                "REFUSED: bulk `DELETE /posts` wipes the entire scheduled queue "
                "(live incident 2026-08-22). Delete the post in the Publer UI instead."
            )
        return super()._request(method, path, **kw)

    def wait_for_job(self, job_id: str, max_seconds: int = 60, poll_interval: float = 2.0) -> dict:
        """Publer returns status "complete" — the base client only accepts "completed".

        That one missing letter is why the 2026-08-21 catch-up recorded JOB_timeout
        for two items that had actually succeeded. Accept both spellings here rather
        than editing the hardened client.
        """
        deadline = time.time() + max_seconds
        while time.time() < deadline:
            st = self.job_status(job_id)
            state = st.get("status") if isinstance(st, dict) else None
            if state in ("complete", "completed", "failed", "error"):
                st = dict(st)
                st["status"] = "completed" if state in ("complete", "completed") else "failed"
                return st
            time.sleep(poll_interval)
        return {"status": "timeout", "job_id": job_id}

    def schedule_video(self, *, text: str, account_key: str, media_id: str,
                       scheduled_at: str, kind: str = "video") -> dict:
        """Schedule one video post to ONE account.

        TWO Publer landmines are baked in here, both found live on 2026-08-22:

        1. Media MUST be referenced by library **id**, not by url. Passing
           {"type": "video", "url": <cdn path>} — which is what
           PublerClient.schedule_post(video_url=...) does — returns a job that
           reports "complete" and creates NO POST AT ALL. Twelve posts were lost
           to this silently before anyone looked at the live list (Rule 12).
        2. type "reel" does the same thing: complete job, no post. Use "video";
           Meta renders a 1080x1920 video on a Page/IG account as a Reel anyway.
        """
        meta = self._account_meta(account_key)
        body = {
            "bulk": {
                "state": "scheduled",
                "posts": [{
                    "networks": {
                        meta["network"]: {
                            "type": kind,
                            "text": text,
                            "media": [{"type": "video", "id": media_id}],
                        }
                    },
                    "accounts": [{"id": meta["publer_id"], "scheduled_at": scheduled_at}],
                }],
            }
        }
        return self.post("/posts/schedule", json=body)

    def live_scheduled(self, days_ahead: int = 14) -> list[dict]:
        """Always pass explicit from/to — GET /posts caps at ~15 results without them."""
        frm = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        to = (dt.date.today() + dt.timedelta(days=days_ahead)).isoformat()
        out = []
        for state in ("scheduled", "published"):
            d = self.get("/posts", params={"state": state, "from": frm, "to": to, "limit": "100"})
            posts = d.get("posts", d) if isinstance(d, dict) else (d or [])
            out.extend(posts)
        return out


def _text_of(post: dict) -> str:
    """GET /posts returns caption at TOP LEVEL as `text` — not under `content`.

    Reading content.text made the duplicate guard silently see every post as
    empty, i.e. no guard at all. Found 2026-08-22 on the first live run.
    """
    if post.get("text"):
        return post["text"]
    c = post.get("content") or {}
    return c.get("text") or ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sleep", type=float, default=12.0, help="seconds between Publer calls")
    args = ap.parse_args()

    plan = json.loads(args.plan.read_text())
    results_path = ROOT / "manifests" / f"{args.plan.stem}_results.json"
    results_path.parent.mkdir(exist_ok=True)
    prior: dict[str, dict] = {}
    if results_path.exists():
        prior = {r["key"]: r for r in json.loads(results_path.read_text()).get("results", [])}

    p = ReelPublisher()
    live_texts = []
    if not args.dry_run:
        try:
            live_texts = [_text_of(x)[:60] for x in p.live_scheduled()]
        except PublerError as e:
            print(f"WARN could not read live posts for duplicate guard: {e}")

    results: list[dict] = []
    media_cache: dict[str, dict] = {r["video"]: r for r in prior.values() if r.get("media_id")}

    def flush() -> None:
        """Write the manifest after EVERY target.

        The sandbox this runs in kills background processes between tool calls, so a
        run can be cut off mid-way. Writing only at the end meant a killed run
        recorded nothing and a rerun re-posted everything. Incremental writes plus
        the live-Publer guard make a resume genuinely safe.
        """
        if args.dry_run:
            return
        merged = dict(prior)
        for r in results:
            merged[r["key"]] = r
        results_path.write_text(json.dumps(
            {"plan": args.plan.name, "ran_at": dt.datetime.now().isoformat(),
             "results": list(merged.values())}, indent=2))

    for item in plan["items"]:
        video = ROOT / item["video"]
        if not video.exists():
            for t in item["targets"]:
                results.append({"key": f"{item['id']}::{t['account']}", "status": "NO_VIDEO",
                                "video": item["video"]})
            print(f"NO_VIDEO: {item['id']}")
            continue

        # --- upload once per file
        cached = media_cache.get(item["video"])
        media_id = cached.get("media_id") if cached else None
        video_url = cached.get("video_url") if cached else None
        if not media_id and not args.dry_run:
            try:
                media = p.upload_media(str(video))
                media_id = media.get("id")
                video_url = media.get("path") or media.get("url")
                if not media_id:
                    raise PublerError(f"upload returned no media id: {list(media)[:8]}")
                media_cache[item["video"]] = {"media_id": media_id, "video_url": video_url}
                results.append({"key": f"{item['id']}::_media", "status": "UPLOADED",
                                "video": item["video"], "media_id": media_id,
                                "video_url": video_url})
                flush()
                print(f"UPLOADED {item['id']} -> {video_url.rsplit('/',1)[-1]}")
                time.sleep(args.sleep)
            except Exception as e:
                for t in item["targets"]:
                    results.append({"key": f"{item['id']}::{t['account']}", "status": "UPLOAD_ERROR",
                                    "error": str(e)[:300], "video": item["video"]})
                print(f"UPLOAD_ERROR {item['id']}: {e}")
                continue

        for t in item["targets"]:
            key = f"{item['id']}::{t['account']}"
            if prior.get(key, {}).get("status") == "SCHEDULED":
                results.append(prior[key]); print(f"SKIP (manifest): {key}"); continue
            marker = t["caption"][:60]
            if marker in live_texts:
                results.append({"key": key, "status": "SCHEDULED",
                                "note": "verified live on Publer (duplicate guard)"})
                print(f"SKIP (live): {key}"); continue
            if args.dry_run:
                print(f"DRY  {key} @ {t['scheduled_at']} [{t.get('kind','reel')}] "
                      f"{len(t['caption'])} chars")
                results.append({"key": key, "status": "DRY_RUN"})
                continue

            last_err = None
            for kind in (t.get("kind", "video"), "video"):
                try:
                    job = p.schedule_video(text=t["caption"], account_key=t["account"],
                                           media_id=media_id, scheduled_at=t["scheduled_at"],
                                           kind=kind)
                    st = p.wait_for_job(job.get("job_id", ""), max_seconds=45, poll_interval=5.0)
                    state = st.get("status")
                    fails = (st.get("payload") or {}).get("failures") or {}
                    if state == "completed" and not fails:
                        results.append({"key": key, "status": "SCHEDULED", "kind": kind,
                                        "job_id": job.get("job_id"),
                                        "scheduled_at": t["scheduled_at"],
                                        "video": item["video"], "media_id": media_id,
                                        "video_url": video_url})
                        print(f"SCHEDULED {key} [{kind}] @ {t['scheduled_at']}")
                        last_err = None
                        break
                    if state == "timeout":
                        # Publer video jobs routinely outlive the poll window and then
                        # succeed (the 2026-08-21 catch-up recorded JOB_timeout for two
                        # items that both went live). A blind retry here DOUBLE-POSTS.
                        # Verify against the live post list instead of guessing.
                        time.sleep(20)
                        landed = any(marker in _text_of(x) for x in p.live_scheduled())
                        if landed:
                            results.append({"key": key, "status": "SCHEDULED", "kind": kind,
                                            "job_id": job.get("job_id"),
                                            "scheduled_at": t["scheduled_at"],
                                            "note": "job timed out; verified live on Publer",
                                            "video": item["video"], "media_id": media_id,
                                            "video_url": video_url})
                            print(f"SCHEDULED {key} [{kind}] (verified after job timeout)")
                            last_err = None
                            break
                        last_err = "job timeout and not present in live post list"
                    else:
                        last_err = f"job {state}: {json.dumps(st)[:200]}"
                except Exception as e:
                    last_err = str(e)[:300]
                if kind != "video":
                    print(f"  retry {key} as video (was {kind}): {last_err}")
                    time.sleep(args.sleep)
            if last_err:
                results.append({"key": key, "status": "ERROR", "error": last_err,
                                "scheduled_at": t["scheduled_at"], "video": item["video"]})
                print(f"ERROR {key}: {last_err}")
            flush()
            time.sleep(args.sleep)

    flush()
    ok = sum(1 for r in results if r["status"] == "SCHEDULED")
    print(f"\n== {ok}/{len(results)} targets scheduled ==")
    print(f"manifest: {results_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
