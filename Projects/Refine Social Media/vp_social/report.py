"""
Deterministic Slack formatters. Same pattern as Bravo Data Extraction/bin/format_aged_inventory.py:
on success print the exact Slack body on stdout and exit 0; on ANY gap print nothing on
stdout, the reason on stderr, and exit 2 (Rule 18 — withhold, don't caveat).

Every number here comes from the ledger, which is synced from Publer through reader.py
with explicit from/to. Nothing is hand-rendered by a model.
"""
from __future__ import annotations
import datetime as dt
import sys
from collections import Counter, defaultdict

from . import config, ledger, reader

ORDER = ["Brand", "BrandIG", "BrandTikTok", "BrandTwitter", "BrandBlog",
         "Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke",
         "GBP_Culpeper", "GBP_Waynesboro", "GBP_Harrisonburg", "GBP_Lexington", "GBP_Roanoke"]
LABEL = {"facebook": "Facebook", "instagram": "Instagram", "tiktok": "TikTok", "twitter": "X",
         "google_business": "Google Business Profile", "gmb": "Google Business Profile",
         "wordpress_oauth": "Blog", "wordpress": "Blog"}


class Withhold(Exception):
    pass


def _fresh_or_sync(max_age_hours: float = 6.0) -> None:
    """Make sure the ledger reflects Publer now. Sync inline if stale (cheap: ~10 s)."""
    last = ledger.last_sync_at()
    if last:
        age = dt.datetime.now(config.TZ) - dt.datetime.fromisoformat(last)
        if age.total_seconds() < max_age_hours * 3600:
            return
    try:
        ledger.sync(days_back=21, days_forward=30)
    except Exception as e:  # noqa: BLE001
        raise Withhold(f"Publer sync failed: {e}")


def _fmt_date(d: str) -> str:
    return dt.date.fromisoformat(d).strftime("%b %-d")


# --- Weekly Social Recap (Mon, #social-media) ------------------------------------

def recap(days: int = 7, end: dt.date | None = None) -> str:
    _fresh_or_sync()
    end = end or dt.datetime.now(config.TZ).date()
    start = end - dt.timedelta(days=days - 1)
    rows = ledger.posts_between(start.isoformat(), end.isoformat(), states=("published",))
    if not rows:
        raise Withhold(f"0 published posts {start}..{end} — either Publer was dark or the read failed; not posting a zero")
    unmapped = [r for r in rows if r["account_key"] == "UNMAPPED"]
    if unmapped:
        raise Withhold(f"{len(unmapped)} posts on unmapped accounts — update publer_accounts.json first")
    by_acct = Counter(r["account_key"] for r in rows)
    by_plat = Counter(LABEL.get(r["provider"], r["provider"]) for r in rows)
    by_kind = Counter(("video" if (r["type"] or "").lower() in ("video", "reel") else
                       "photo" if (r["type"] or "").lower() == "photo" else "text/other") for r in rows)
    outside = sum(1 for r in rows if r["source"] == "sync" and r["provider"] != "wordpress_oauth")
    blank = sum(1 for r in rows if not (r["text"] or "").strip() and r["provider"] != "wordpress_oauth")

    lines = [f"*Weekly Social Recap — {_fmt_date(start.isoformat())} to {_fmt_date(end.isoformat())}*",
             f"{len(rows)} posts published across all Valley Pawn channels "
             f"({by_kind['photo']} photo · {by_kind['video']} video · {by_kind['text/other']} text/other).", "",
             "*By platform:*"]
    lines += [f"• {k}: {v}" for k, v in sorted(by_plat.items(), key=lambda kv: -kv[1])]
    lines += ["", "*By page:*"]
    lines += [f"• {k}: {by_acct[k]}" for k in ORDER if by_acct.get(k)]
    lines += [f"• {k}: {v}" for k, v in by_acct.items() if k not in ORDER]
    notes = []
    if outside:
        notes.append(f"{outside} posted directly on the platform (not through Publer)")
    if blank:
        notes.append(f"{blank} went out with an empty caption")
    if notes:
        lines += ["", "_" + "; ".join(notes) + "._"]
    return "\n".join(lines)


# --- Quota (Tue, silent unless shortfall) ----------------------------------------

def quota(target: int = 7, flag_under: int = 4) -> dict:
    _fresh_or_sync()
    d_from, d_to = reader.date_range(6)
    rows = ledger.posts_between(d_from, d_to, states=("scheduled", "published"))
    counts = Counter(r["account_key"] for r in rows)
    result = {"window": {"from": d_from, "to": d_to}, "target": target, "accounts": {}, "flagged": []}
    for k in ORDER:
        if k in config.EXCLUDED_FROM_QUOTA:
            continue
        n = counts.get(k, 0)
        result["accounts"][k] = n
        if n < flag_under:
            result["flagged"].append(k)
    return result


# --- Postflight (after a publish run) ----------------------------------------------

def postflight(plan_id: str) -> str:
    """Verify every planned slot in a plan against Publer. Withholds if anything is unresolved."""
    ledger.sync(days_back=7, days_forward=21)
    with ledger.connect() as con:
        rows = con.execute("SELECT * FROM planned WHERE plan_id=?", (plan_id,)).fetchall()
    if not rows:
        raise Withhold(f"no planned rows for {plan_id}")
    st = Counter(r["status"] for r in rows)
    missing = [r for r in rows if r["status"] in ("planned", "failed")]
    lanes = defaultdict(Counter)
    for r in rows:
        lanes[r["lane"]][r["status"]] += 1
    lines = [f"*Postflight — {plan_id}*",
             f"{st['scheduled'] + st['published']} of {len(rows)} placements live in Publer"
             + (f", {st['skipped']} skipped by rule" if st.get("skipped") else "") + "."]
    for lane, c in lanes.items():
        lines.append(f"• {lane}: {c['scheduled'] + c['published']} live" + (f", {c['skipped']} skipped" if c.get("skipped") else ""))
    if missing:
        raise Withhold(f"{len(missing)} placements not live: " +
                       "; ".join(f"{r['lane']}/{r['item_key']}/{r['account_key']} ({r['reason'] or r['status']})" for r in missing[:12]))
    return "\n".join(lines)


# --- Month in review (1st, #social-media) --------------------------------------------

def month(yyyy_mm: str) -> str:
    ledger.sync(days_back=45, days_forward=5)
    y, m = map(int, yyyy_mm.split("-"))
    start = dt.date(y, m, 1)
    end = (dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1))
    rows = ledger.posts_between(start.isoformat(), end.isoformat(), states=("published",))
    if not rows:
        raise Withhold(f"0 published posts in {yyyy_mm}")
    by_acct = Counter(r["account_key"] for r in rows)
    by_week = Counter(dt.date.fromisoformat(r["scheduled_date"]).isocalendar()[1] for r in rows)
    videos = sum(1 for r in rows if (r["type"] or "").lower() in ("video", "reel"))
    zero_days = [d for d in (start + dt.timedelta(days=i) for i in range((end - start).days + 1))
                 if not any(r["scheduled_date"] == d.isoformat() for r in rows)]
    lines = [f"*Social — {start.strftime('%B %Y')} in review*",
             f"{len(rows)} posts published ({videos} videos) across {len(by_acct)} pages; "
             f"weekly counts {' · '.join(str(by_week[w]) for w in sorted(by_week))}.",
             "", "*By page:*"]
    lines += [f"• {k}: {by_acct[k]}" for k in ORDER if by_acct.get(k)]
    if zero_days:
        lines += ["", f"_Days with nothing published: {', '.join(d.strftime('%b %-d') for d in zero_days)}._"]
    return "\n".join(lines)


# --- Friday digest (counts from ledger + engagement from Publer insights) ---------------

def digest(days: int = 7) -> str:
    _fresh_or_sync()
    d_from, d_to = reader.date_range(days - 1)
    rows = ledger.posts_between(d_from, d_to, states=("published",))
    if not rows:
        raise Withhold("0 published posts in the window")
    p = reader._client()
    idx = {v["publer_id"]: k for k, v in config.load_accounts().items() if v.get("publer_id")}
    scored = []
    failures = []
    for pid, key in idx.items():
        if key == "BrandBlog":
            continue
        try:
            for it in p.post_insights(pid, since=d_from, until=d_to, limit=100):
                eng = it.get("engagement") or (it.get("likes", 0) + it.get("comments", 0) + it.get("shares", 0) + it.get("saves", 0))
                scored.append({"key": key, "text": (it.get("text") or it.get("caption") or "")[:90].replace("\n", " "),
                               "reach": it.get("reach") or 0, "eng": eng or 0, "type": it.get("type") or it.get("postType")})
        except Exception as e:  # noqa: BLE001
            failures.append(f"{key}: {e}")
    if failures and len(failures) > 3:
        raise Withhold("Publer analytics unavailable for " + "; ".join(failures))
    total_reach = sum(s["reach"] for s in scored)
    total_eng = sum(s["eng"] for s in scored)
    top = sorted(scored, key=lambda s: -s["eng"])[:5]
    lines = [f"*Weekly Social Digest — {_fmt_date(d_from)} to {_fmt_date(d_to)}*",
             f"{len(rows)} posts published · {total_reach:,} reach · {total_eng:,} engagements "
             f"({len(scored)} posts with analytics available).", ""]
    if top:
        lines.append("*Top posts by engagement:*")
        lines += [f"• {s['key']} — {s['eng']} eng / {s['reach']} reach — \"{s['text']}\"" for s in top]
    by_acct = Counter(r["account_key"] for r in rows)
    lines += ["", "*Volume by page:* " + " · ".join(f"{k} {by_acct[k]}" for k in ORDER if by_acct.get(k))]
    if failures:
        lines += ["", "_Analytics not returned for: " + ", ".join(f.split(":")[0] for f in failures) + "._"]
    return "\n".join(lines)


def emit(fn, *a, **kw) -> int:
    """CLI helper: stdout on success (exit 0), nothing on stdout + stderr on withhold (exit 2)."""
    try:
        out = fn(*a, **kw)
    except Withhold as w:
        print(f"WITHHOLD: {w}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if isinstance(out, dict):
        import json
        print(json.dumps(out, indent=1))
    else:
        print(out)
    return 0
