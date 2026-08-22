#!/usr/bin/env python3
"""
quota_watchdog.py — per-account weekly post-count check against Publer.

Hardened, self-contained runner for the vp-content-batch-quota-watchdog scheduled
task (added 2026-08-21 after a run stalled on Cowork folder-mount access; the
task file's job logic now lives HERE so every run just executes this script via
`python3 quota_watchdog.py` — locally on the Mac, no mounts, no inline rebuild).

What it does (mirrors the task spec exactly):
  1. Trailing-7-day window (today-7 .. today), YYYY-MM-DD.
  2. GET /posts for BOTH state=scheduled and state=published with explicit
     from/to (NEVER omitted — endpoint silently caps at ~15 without it) and
     limit=100, paginated. Combine + dedupe by (post id, account id).
  3. Group counts per account via publer_accounts.json store keys.
  4. Flag accounts under 4/week. (BrandTikTok/BrandBlog excluded — not targets.)
  5. Compare to the MOST RECENT prior quota_watchdog_result.json (any earlier
     dated folder). Two consecutive flagged weeks => alert-worthy.
  6. Write today's full counts to
     Valley Pawn Studios/output/{today}/quota_watchdog_result.json.
  7. Print a JSON summary to stdout — the calling task reads this and decides
     whether to DM (DM logic stays in the task, not here; this script is
     read-only against Publer and write-only to its own result file).

Exit codes: 0 = ran clean; 1 = hard failure (message on stderr).
"""
from __future__ import annotations
import json
import sys
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from publer_client import PublerClient, PublerError  # noqa: E402

OUTPUT_ROOT = Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output")

TARGETS = {
    "Brand": 7, "BrandIG": 7, "BrandTwitter": 7,
    "Culpeper": 7, "Waynesboro": 7, "Harrisonburg": 7, "Lexington": 7, "Roanoke": 7,
    "GBP_Culpeper": 7, "GBP_Waynesboro": 7, "GBP_Harrisonburg": 7,
    "GBP_Lexington": 7, "GBP_Roanoke": 7,
}
FLAG_UNDER = 4  # under 4/week = flagged


def fetch_posts(p: PublerClient, state: str, date_from: str, date_to: str) -> list[dict]:
    """Paginated GET /posts with explicit from/to. Retries each page 3x (transient 500s)."""
    out: list[dict] = []
    for page in range(1, 11):  # hard cap 10 pages / 1000 posts
        params = {"state": state, "from": date_from, "to": date_to,
                  "limit": "100", "page": str(page)}
        last_err = None
        for attempt in range(3):
            try:
                data = p.get("/posts", params=params)
                break
            except PublerError as e:
                last_err = e
                import time as _t
                _t.sleep(3 * (attempt + 1))
        else:
            raise last_err
        posts = data.get("posts", []) if isinstance(data, dict) else (data or [])
        out.extend(posts)
        if len(posts) < 100:
            break
    return out


def account_id_of(post: dict) -> str | None:
    """Publer post objects vary; try the known shapes."""
    for key in ("account_id", "accountId"):
        if post.get(key):
            return str(post[key])
    acc = post.get("account")
    if isinstance(acc, dict) and acc.get("id"):
        return str(acc["id"])
    if isinstance(acc, str):
        return acc
    return None


def find_prior_result(today: str) -> tuple[str, dict] | None:
    """Most recent quota_watchdog_result.json from a date folder before today."""
    if not OUTPUT_ROOT.exists():
        return None
    candidates = sorted(
        (d for d in OUTPUT_ROOT.iterdir()
         if d.is_dir() and d.name < today and (d / "quota_watchdog_result.json").exists()),
        key=lambda d: d.name, reverse=True)
    if not candidates:
        return None
    d = candidates[0]
    try:
        return d.name, json.loads((d / "quota_watchdog_result.json").read_text())
    except Exception:
        return None


def main() -> int:
    today = dt.date.today()
    date_to = today.isoformat()
    date_from = (today - dt.timedelta(days=7)).isoformat()

    p = PublerClient()
    id_to_key = {v["publer_id"]: k for k, v in p.accounts.items()}

    seen: set[tuple[str, str]] = set()
    counts: dict[str, int] = {k: 0 for k in TARGETS}
    unmapped = 0
    for state in ("scheduled", "published"):
        for post in fetch_posts(p, state, date_from, date_to):
            pid = str(post.get("id") or post.get("_id") or "")
            aid = account_id_of(post)
            if not pid or not aid:
                unmapped += 1
                continue
            if (pid, aid) in seen:
                continue
            seen.add((pid, aid))
            key = id_to_key.get(aid)
            if key in counts:
                counts[key] += 1

    flagged = sorted(k for k, c in counts.items() if c < FLAG_UNDER)

    prior = find_prior_result(date_to)
    prior_date, prior_counts, prior_flagged = None, {}, []
    if prior:
        prior_date = prior[0]
        prior_counts = prior[1].get("counts", {})
        prior_flagged = prior[1].get("flagged", [])
    two_week = sorted(set(flagged) & set(prior_flagged))

    result = {
        "run_date": date_to, "window": {"from": date_from, "to": date_to},
        "targets": TARGETS, "counts": counts, "flagged": flagged,
        "prior_run_date": prior_date,
        "two_week_shortfalls": [
            {"account": a, "this_week": counts.get(a), "last_week": prior_counts.get(a)}
            for a in two_week],
        "unmapped_posts_skipped": unmapped,
        "total_unique_post_account_pairs": len(seen),
    }

    outdir = OUTPUT_ROOT / date_to
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "quota_watchdog_result.json").write_text(json.dumps(result, indent=2))

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"WATCHDOG-FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
