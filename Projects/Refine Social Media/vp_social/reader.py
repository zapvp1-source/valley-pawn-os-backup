"""
THE ONLY reader of Publer. Every report, watchdog and planner reads through here.

Why this exists (2026-09-05): weekly_social_recap.py called /posts with no from/to and
Publer silently returned a default window -> Slack said "15 posts" when 88 had gone out.
publer_weekly_digest.py undercounted the same way. This module always sends from/to,
always paginates, retries transient 5xx, and normalizes every post to one flat record.
"""
from __future__ import annotations
import hashlib
import sys
import time
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from publer_client import PublerClient, PublerError  # noqa: E402
from . import config

STATES = ("scheduled", "published", "failed", "draft")


class ReadIncomplete(Exception):
    """Raised when Publer could not be read completely. Rule 18: callers withhold."""


def _client() -> PublerClient:
    return PublerClient()


def _get_page(p: PublerClient, params: dict) -> dict:
    last = None
    for attempt in range(4):
        try:
            data = p.get("/posts", params=params)
            return data if isinstance(data, dict) else {"posts": data or []}
        except PublerError as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise ReadIncomplete(f"/posts {params} failed after retries: {last}")


def fetch_posts(state: str, date_from: str, date_to: str, p: PublerClient | None = None) -> list[dict]:
    """All posts in [date_from, date_to] (YYYY-MM-DD, inclusive) for one state. Paginated."""
    # Verified 2026-09-05: Publer ignores limit/page for /posts and returns the whole
    # window in one response (545 posts for a 90-day window). We still walk pages
    # defensively but stop the moment a page repeats ids or comes back short.
    p = p or _client()
    out: list[dict] = []
    seen: set = set()
    for page in range(1, 21):
        data = _get_page(p, {"state": state, "from": date_from, "to": date_to,
                             "limit": "100", "page": str(page)})
        posts = data.get("posts", [])
        new = [x for x in posts if (str(x.get("id")), str(x.get("account_id"))) not in seen]
        for x in new:
            seen.add((str(x.get("id")), str(x.get("account_id"))))
        out.extend(new)
        total = data.get("total")
        if not new or len(posts) < 100 or (isinstance(total, int) and len(out) >= total):
            break
    return out


def fetch_window(date_from: str, date_to: str, states=STATES) -> list[dict]:
    """Every post across the given states, normalized and de-duplicated by (id, account)."""
    p = _client()
    seen: dict[tuple, dict] = {}
    for st in states:
        for raw in fetch_posts(st, date_from, date_to, p):
            rec = normalize(raw)
            seen[(rec["publer_id"], rec["account_id"])] = rec
    return sorted(seen.values(), key=lambda r: r["scheduled_at"] or "")


def caption_hash(text: str | None) -> str:
    return hashlib.sha1((text or "").strip().lower().encode()).hexdigest()[:16]


def _parse_ts(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    try:
        d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(config.TZ)


_IDX: dict | None = None


def normalize(raw: dict) -> dict:
    global _IDX
    if _IDX is None:
        _IDX = config.account_index()
    idx = _IDX
    acct = idx.get(str(raw.get("account_id")), {})
    ts = _parse_ts(raw.get("scheduled_at"))
    media = raw.get("media") or []
    if isinstance(media, dict):
        media = [media]
    media_ids = []
    for m in media:
        if isinstance(m, dict):
            media_ids.append(str(m.get("id") or m.get("path") or ""))
    text = raw.get("text") or ""
    return {
        "publer_id": str(raw.get("id")),
        "account_id": str(raw.get("account_id")),
        "account_key": acct.get("key", "UNMAPPED"),
        "provider": acct.get("provider") or raw.get("account_type") or "?",
        "state": raw.get("state"),
        "type": raw.get("type"),
        "source": raw.get("source"),                 # 'schedule' (via Publer) | 'sync' (posted elsewhere)
        "scheduled_at": ts.isoformat() if ts else None,
        "scheduled_date": ts.date().isoformat() if ts else None,
        "text": text,
        "title": raw.get("title"),
        "text_hash": caption_hash(text),
        "media_ids": ",".join(media_ids),
        "post_link": raw.get("post_link"),
        "error": (raw.get("error") or None) if isinstance(raw.get("error"), str) else None,
        "updated_at": raw.get("updated_at"),
    }


def date_range(days_back: int, days_forward: int = 0, today: dt.date | None = None) -> tuple[str, str]:
    today = today or dt.datetime.now(config.TZ).date()
    return ((today - dt.timedelta(days=days_back)).isoformat(),
            (today + dt.timedelta(days=days_forward)).isoformat())


def list_accounts() -> list[dict]:
    return _client().list_accounts()
