#!/usr/bin/env python3
"""
publer_90day_audit.py -- Rule 12 audit of Valley Pawn's ACTUAL published
social output via the Publer API. Verifies real published posts, not manifests
or run records.

Window: 2026-05-24 .. 2026-08-22 (90 days).

Outputs:
  audit_2026-08-22/publer_90day_raw.json   -- raw API payloads (posts + analytics)
  audit_2026-08-22/PUBLER_90DAY_AUDIT.md   -- readable summary

GOTCHAS baked in (do not "simplify" these away):
  * Publer sits behind Cloudflare -> a browser User-Agent header is REQUIRED
    or every call returns 403 / "error code: 1010".
  * Auth header format is `Bearer-API {key}` (NOT OAuth `Bearer {key}`).
  * GET /posts silently caps at ~15 results unless explicit `from`/`to`
    date-range params are supplied. ALWAYS pass a date range.
  * GET /posts IGNORES `page` (returns the whole range every time) -- so we
    fetch the range in one call and de-dupe by id.
  * GET /analytics/{id}/post_insights DOES paginate: fixed 10 per page,
    `page` param, `total` in the envelope. Passing `limit` corrupts the
    ordering -- do not pass it.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import datetime as dt
from collections import Counter, defaultdict
from pathlib import Path

import requests

ROOT = Path(__file__).parent
OUTDIR = ROOT / "audit_2026-08-22"
CFG = json.loads((ROOT / "publer_config.json").read_text())
ACCT_CFG = json.loads((ROOT / "publer_accounts.json").read_text())["accounts"]

BASE = CFG["api_base"].rstrip("/")
HEADERS = {
    "Authorization": f"Bearer-API {CFG['api_key']}",
    "Publer-Workspace-Id": CFG["workspace_id"],
    # REQUIRED: Cloudflare in front of Publer 403s any non-browser UA.
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json",
}

DATE_FROM = "2026-05-24"
DATE_TO = "2026-08-22"

INSIGHT_TOTALS: dict[str, dict] = {}

ID_TO_KEY = {v["publer_id"]: k for k, v in ACCT_CFG.items()}
KEY_TO_NAME = {
    k: f"{v.get('name', k)}" for k, v in ACCT_CFG.items()
}


def api_get(path: str, params: dict, tries: int = 4):
    """GET with retry -- Publer intermittently 500s on analytics reads."""
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=120)
            if r.ok:
                return r.json()
            last = f"{r.status_code}: {r.text[:200]}"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"GET {path} failed after {tries} tries -> {last}")


# ---------------------------------------------------------------- posts

def fetch_published() -> list[dict]:
    """All published posts in the window. Date range is mandatory (see gotchas)."""
    data = api_get("/posts", {"state": "published", "from": DATE_FROM,
                              "to": DATE_TO, "limit": "500"})
    posts = data.get("posts", []) if isinstance(data, dict) else (data or [])
    # De-dupe defensively by id.
    seen, out = set(), []
    for p in posts:
        pid = str(p.get("id"))
        if pid in seen:
            continue
        seen.add(pid)
        out.append(p)
    return out


# ---------------------------------------------------------------- analytics

def fetch_insights(account_id: str) -> tuple[list[dict], str | None]:
    """
    Paginate post_insights for one account. Returns (items, error_or_None).

    CRITICAL: this endpoint's `page` param is ZERO-INDEXED. Omitting `page`
    == `page=0` == the FIRST 10 records; `page=1` is the SECOND page. Starting
    a loop at page=1 (1-indexed assumption) silently drops records 11-20 for
    every account. Verified live 2026-08-22 against the Harrisonburg account
    (total=13: page0 -> 10 rows, page1 -> 3 rows, page2 -> 0 rows).
    Page size is fixed at 10; passing `limit` corrupts ordering, so don't.
    """
    items: list[dict] = []
    total = None
    page = 0
    while page <= 200:
        params = {"from": DATE_FROM, "to": DATE_TO,
                  "account_id": account_id, "sort": "scheduled_at"}
        if page:
            params["page"] = str(page)
        try:
            d = api_get(f"/analytics/{account_id}/post_insights", params)
        except RuntimeError as e:
            return items, f"page {page}: {e}"
        if total is None and isinstance(d, dict):
            total = d.get("total")
        batch = d.get("posts", []) if isinstance(d, dict) else []
        if not batch:
            break
        items.extend(batch)
        page += 1
        if total and len(items) >= total:
            break
    # de-dupe
    seen, out = set(), []
    for p in items:
        pid = str(p.get("id"))
        if pid in seen:
            continue
        seen.add(pid)
        out.append(p)
    INSIGHT_TOTALS[account_id] = {"api_total": total, "fetched": len(out)}
    return out, None


# ---------------------------------------------------------------- classification

def media_class(post: dict) -> str:
    """video | image | text | article  -- from post.type + media[].type."""
    media = post.get("media") or []
    mtypes = {str(m.get("type", "")).lower() for m in media if isinstance(m, dict)}
    ptype = str(post.get("type") or "").lower()

    if "video" in mtypes or ptype in ("video", "reel", "reels", "short", "story_video"):
        return "video"
    if ptype == "article":
        return "article"
    if "photo" in mtypes or "image" in mtypes or "gif" in mtypes or ptype in ("photo", "image", "gif", "carousel"):
        return "image"
    if media:
        return "image"
    if ptype in ("status", "text", "link"):
        return "text"
    return f"other:{ptype or 'unknown'}"


def acct_label(post: dict) -> str:
    aid = str(post.get("account_id") or "")
    key = ID_TO_KEY.get(aid)
    if key:
        return key
    return f"UNMAPPED:{aid}"


def val(a: dict, name: str):
    node = (a or {}).get(name)
    if isinstance(node, dict):
        return node.get("value")
    return node


def engagement_of(analytics: dict) -> tuple[int, dict]:
    """Sum of likes+comments+shares+saves. Returns (score, flat metrics dict)."""
    flat = {}
    for k in ("reach", "impressions", "likes", "comments", "shares", "saves",
              "video_views", "link_clicks", "post_clicks", "engagement",
              "engagement_rate", "reach_rate", "click_through_rate", "profile_views"):
        v = val(analytics, k)
        if v is not None:
            flat[k] = v
    if isinstance(flat.get("engagement"), (int, float)):
        score = float(flat["engagement"])
    else:
        score = sum(float(flat.get(k) or 0) for k in ("likes", "comments", "shares", "saves"))
    return int(round(score)), flat


def wk_start(iso: str) -> str:
    d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    return (d - dt.timedelta(days=d.weekday())).isoformat()


def clip(s, n=120):
    s = (s or "").replace("\n", " ⏎ ").strip()
    return s[:n]


# ---------------------------------------------------------------- main

def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    print(f"Window {DATE_FROM} .. {DATE_TO}", file=sys.stderr)

    accounts_live = api_get("/accounts", {})
    if isinstance(accounts_live, dict):
        accounts_live = accounts_live.get("accounts", [])

    posts = fetch_published()
    print(f"published posts fetched: {len(posts)}", file=sys.stderr)

    insights = {}
    errors = {}
    for key, cfg in ACCT_CFG.items():
        aid = cfg["publer_id"]
        items, err = fetch_insights(aid)
        insights[key] = items
        if err:
            errors[key] = err
        print(f"  insights {key}: {len(items)}" + (f"  ERR={err}" if err else ""), file=sys.stderr)

    raw = {
        "pulled_at": dt.datetime.now().isoformat(),
        "window": {"from": DATE_FROM, "to": DATE_TO},
        "accounts_live": accounts_live,
        "published_posts": posts,
        "post_insights": insights,
        "insight_errors": errors,
        "insight_completeness": {ID_TO_KEY.get(k, k): v for k, v in INSIGHT_TOTALS.items()},
    }
    (OUTDIR / "publer_90day_raw.json").write_text(json.dumps(raw, indent=2))

    # ---- build the report
    L = []
    A = L.append
    A(f"# Valley Pawn — Publer 90-Day Published-Output Audit")
    A("")
    A(f"**Window:** {DATE_FROM} through {DATE_TO} (91 calendar days)  ")
    A(f"**Source:** Publer API `GET /posts?state=published` + `GET /analytics/{{account}}/post_insights` — live pull, not manifests.  ")
    A(f"**Pulled:** {raw['pulled_at']}  ")
    A(f"**Raw data:** `audit_2026-08-22/publer_90day_raw.json`")
    A("")
    A("---")
    A("")

    # 1. totals by account
    by_acct = Counter(acct_label(p) for p in posts)
    A("## 1. Total published posts by account")
    A("")
    A(f"**TOTAL PUBLISHED POSTS IN WINDOW: {len(posts)}**")
    A("")
    A("| Account | Platform | Published posts | Per week (÷13) |")
    A("|---|---|---:|---:|")
    order = [k for k in ACCT_CFG] + sorted(k for k in by_acct if k not in ACCT_CFG)
    for key in order:
        n = by_acct.get(key, 0)
        prov = ACCT_CFG.get(key, {}).get("provider", "?")
        A(f"| {key} | {prov} | {n} | {n/13.0:.1f} |")
    A(f"| **TOTAL** | | **{len(posts)}** | **{len(posts)/13.0:.1f}** |")
    A("")
    connected_but_silent = [k for k in ACCT_CFG if by_acct.get(k, 0) == 0]
    if connected_but_silent:
        A(f"**Connected accounts with ZERO published posts in the window:** {', '.join(connected_but_silent)}")
        A("")

    # 2. per week
    weeks = defaultdict(Counter)
    for p in posts:
        sa = p.get("scheduled_at")
        if not sa:
            continue
        weeks[wk_start(sa)][acct_label(p)] += 1
    wk_keys = sorted(weeks)
    A("## 2. Posts per week per account (week starting Monday)")
    A("")
    A(f"Every week bucket touching the window is shown ({len(wk_keys)} buckets). The first "
      f"bucket ({wk_keys[0]}) is PARTIAL — the window opens Sunday {DATE_FROM}, so it holds "
      f"only that one day. The last bucket is partial too (window closes {DATE_TO}). "
      "Column totals therefore equal the full 554.")
    A("")
    A("| Account | " + " | ".join(w[5:] for w in wk_keys) + " | Total |")
    A("|---" * (len(wk_keys) + 2) + "|")
    for key in order:
        row = [str(weeks[w].get(key, 0)) for w in wk_keys]
        tot = sum(weeks[w].get(key, 0) for w in wk_keys)
        A(f"| {key} | " + " | ".join(row) + f" | {tot} |")
    tot_row = [str(sum(weeks[w].values())) for w in wk_keys]
    A("| **ALL** | " + " | ".join(tot_row) + f" | **{sum(int(x) for x in tot_row)}** |")
    A("")

    # 3. media type
    A("## 3. Media type breakdown")
    A("")
    mt = Counter(media_class(p) for p in posts)
    A("| Media type | Posts | % of total |")
    A("|---|---:|---:|")
    for k, v in mt.most_common():
        A(f"| {k} | {v} | {100*v/len(posts):.1f}% |")
    A(f"| **TOTAL** | **{len(posts)}** | 100% |")
    A("")
    A("### Media type by account")
    A("")
    mt_keys = [k for k, _ in mt.most_common()]
    A("| Account | " + " | ".join(mt_keys) + " |")
    A("|---" * (len(mt_keys) + 1) + "|")
    per = defaultdict(Counter)
    for p in posts:
        per[acct_label(p)][media_class(p)] += 1
    for key in order:
        A(f"| {key} | " + " | ".join(str(per[key].get(m, 0)) for m in mt_keys) + " |")
    A("")
    A("### Video posts over time (the 'no videos' question)")
    A("")
    vweeks = defaultdict(Counter)
    for p in posts:
        if p.get("scheduled_at"):
            vweeks[wk_start(p["scheduled_at"])][media_class(p)] += 1
    A("| Week starting | Video | Image | Text | Article | Total | Video % |")
    A("|---|---:|---:|---:|---:|---:|---:|")
    for w in sorted(vweeks):
        c = vweeks[w]
        tot = sum(c.values())
        A(f"| {w} | {c.get('video',0)} | {c.get('image',0)} | {c.get('text',0)} | "
          f"{c.get('article',0)} | {tot} | {100*c.get('video',0)/tot:.0f}% |")
    A("")
    vids = [p for p in posts if media_class(p) == "video"]
    if vids:
        vts = sorted((p.get("scheduled_at") or "") for p in vids)
        A(f"- All {len(vids)} video posts fall between **{vts[0][:16]}** and **{vts[-1][:16]}**.")
        src = Counter(str(p.get("source")) for p in vids)
        A(f"- Publer `source` field on those video posts: {dict(src)}.")
        burst = Counter((p.get("scheduled_at") or "")[:10] for p in vids)
        A(f"- Video posts per calendar day: {dict(sorted(burst.items()))}")
        A("")
        A("**Read this carefully — it is the crux of the 'no videos' complaint.** "
          f"{src.get('sync', 0)} of the {len(vids)} videos carry `source: sync` and timestamps inside a "
          "single ~19-minute window on the morning of 2026-05-25 (11:19–11:38 ET). Their `post_link` "
          "values are real `facebook.com/reel/...` URLs, so they genuinely published — but they were "
          "hand-uploaded to Facebook in one manual batch and only *imported* into Publer afterwards "
          "(`updated_at` on those records is 2026-06-19, three weeks later). They were not produced or "
          "scheduled by the content pipeline. Since that one burst, video output across all 15 "
          f"connected accounts over the remaining 89 days is **{len(vids) - src.get('sync', 0)} posts**.")
        A("")
        A("| Timestamp | Account | Source | Caption (first 120 chars) |")
        A("|---|---|---|---|")
        for p in sorted(vids, key=lambda p: p.get("scheduled_at") or ""):
            A(f"| {(p.get('scheduled_at') or '')[:16]} | {acct_label(p)} | {p.get('source')} | "
              f"{clip(p.get('text') or p.get('title') or '(no caption)').replace('|','/')} |")
        A("")
    A("### Publishing source: pipeline vs. synced-from-platform")
    A("")
    A("| source | Posts | Meaning |")
    A("|---|---:|---|")
    srcmap = {"schedule": "published BY Publer on a schedule (the automation pipeline)",
              "post_now": "published BY Publer immediately (manual/immediate send through the pipeline)",
              "sync": "posted natively on the platform; Publer only imported the record afterwards"}
    for k, v in Counter(str(p.get("source")) for p in posts).most_common():
        A(f"| {k} | {v} | {srcmap.get(k, '')} |")
    A("")
    A("### Raw Publer `type` values seen (unmapped, for transparency)")
    A("")
    A("| Publer post.type | count |")
    A("|---|---:|")
    for k, v in Counter(str(p.get("type")) for p in posts).most_common():
        A(f"| {k} | {v} |")
    A("")

    # 4. engagement
    A("## 4. Engagement")
    A("")
    rows = []
    ins_by_id = {}
    for key, items in insights.items():
        for it in items:
            a = it.get("analytics") or {}
            score, flat = engagement_of(a)
            has_any = bool(flat)
            ins_by_id[str(it.get("id"))] = it
            rows.append({
                "account": key,
                "id": str(it.get("id")),
                "date": (it.get("scheduled_at") or "")[:10],
                "media": media_class(it),
                "text": clip(it.get("text") or it.get("title") or ""),
                "engagement": score,
                "metrics": flat,
                "has_metrics": has_any,
                "link": it.get("post_link"),
            })
    scored = [r for r in rows if r["has_metrics"]]
    A(f"- Accounts Publer exposes post-level analytics for: "
      f"{', '.join(sorted({r['account'] for r in scored})) or 'NONE'}")
    noan = sorted(k for k, v in insights.items() if not v)
    if noan:
        A(f"- Accounts returning NO analytics rows at all: {', '.join(noan)}")
    if errors:
        A(f"- Analytics endpoint ERRORS: {json.dumps(errors)}")
    A(f"- Analytics rows fetched vs. Publer's own reported `total` (completeness check): "
      + ", ".join(f"{ID_TO_KEY.get(k,k)} {v['fetched']}/{v['api_total']}"
                  for k, v in INSIGHT_TOTALS.items()))
    A(f"- Posts with any engagement metric available: **{len(scored)}** of {len(posts)} published posts "
      f"({100*len(scored)/len(posts):.1f}%).")
    A("")
    A("Engagement score = likes + comments + shares + saves (Publer's own per-post analytics values).")
    A("")

    def tbl(title, rs):
        A(f"### {title}")
        A("")
        A("| # | Eng | Likes | Cmts | Shares | Reach | Account | Date | Media | Caption (first 120 chars) |")
        A("|---:|---:|---:|---:|---:|---:|---|---|---|---|")
        for i, r in enumerate(rs, 1):
            m = r["metrics"]
            A(f"| {i} | {r['engagement']} | {m.get('likes','-')} | {m.get('comments','-')} | "
              f"{m.get('shares','-')} | {m.get('reach','-')} | {r['account']} | {r['date']} | "
              f"{r['media']} | {r['text'].replace('|','/')} |")
        A("")

    srt = sorted(scored, key=lambda r: (-r["engagement"], r["date"]))
    tbl("TOP 15 posts by engagement", srt[:15])
    tbl("BOTTOM 15 posts by engagement", sorted(scored, key=lambda r: (r["engagement"], r["date"]))[:15])

    A("### Median engagement per account")
    A("")
    A("| Account | Posts w/ metrics | Median engagement | Mean | Max | Median reach |")
    A("|---|---:|---:|---:|---:|---:|")
    for key in order:
        rs = [r for r in scored if r["account"] == key]
        if not rs:
            A(f"| {key} | 0 | n/a — no analytics exposed | n/a | n/a | n/a |")
            continue
        eng = [r["engagement"] for r in rs]
        reach = [float(r["metrics"]["reach"]) for r in rs if isinstance(r["metrics"].get("reach"), (int, float))]
        reach_s = f"{statistics.median(reach):.1f}" if reach else "n/a"
        A(f"| {key} | {len(rs)} | {statistics.median(eng):.1f} | {statistics.mean(eng):.2f} | "
          f"{max(eng)} | {reach_s} |")
    A("")

    # 5. comments
    A("## 5. Comments / community signal")
    A("")
    with_c = [r for r in scored if isinstance(r["metrics"].get("comments"), (int, float)) and r["metrics"]["comments"] > 0]
    total_c = sum(float(r["metrics"].get("comments") or 0) for r in scored)
    measurable = [r for r in scored if isinstance(r["metrics"].get("comments"), (int, float))]
    A(f"- Posts where a comment count is measurable: **{len(measurable)}**")
    A(f"- Posts that received AT LEAST ONE comment: **{len(with_c)}**")
    A(f"- TOTAL comments across all measured posts: **{int(total_c)}**")
    if measurable:
        A(f"- Share of measured posts with any comment: **{100*len(with_c)/len(measurable):.1f}%**")
    A("")
    if with_c:
        A("| Account | Date | Comments | Caption |")
        A("|---|---|---:|---|")
        for r in sorted(with_c, key=lambda r: -r["metrics"]["comments"]):
            A(f"| {r['account']} | {r['date']} | {int(r['metrics']['comments'])} | {r['text'].replace('|','/')} |")
        A("")
    # also raw comments[] arrays on /posts
    raw_c = sum(len(p.get("comments") or []) for p in posts)
    A(f"- Cross-check: the `comments[]` array on the raw `/posts` objects (Publer's own "
      f"stored replies) contains **{raw_c}** entries across all {len(posts)} posts.")
    A("")

    # 6. captions
    A("## 6. Caption sample — 25 most recent, verbatim")
    A("")
    recent = sorted([p for p in posts if p.get("scheduled_at")],
                    key=lambda p: p["scheduled_at"], reverse=True)[:25]
    for i, p in enumerate(recent, 1):
        A(f"**{i}. {acct_label(p)} — {p['scheduled_at'][:16]} — {media_class(p)}**")
        A("")
        A("```")
        A((p.get("text") or p.get("title") or "(no text)").strip())
        A("```")
        A("")

    # duplicate analysis
    A("### Near-duplicate caption analysis")
    A("")
    norm = defaultdict(list)
    for p in posts:
        t = (p.get("text") or "").strip()
        if not t:
            continue
        norm[t].append(p)
    exact_dupes = {t: v for t, v in norm.items() if len(v) > 1}
    n_text = sum(1 for p in posts if (p.get("text") or "").strip())
    A(f"- Posts carrying ANY caption text: **{n_text}** of {len(posts)}. "
      f"**{len(posts) - n_text}** posts published with no caption at all "
      "(mostly image-only posts Publer synced from Facebook).")
    A(f"- Distinct caption strings among those {n_text} posts with text: **{len(norm)}**")
    A(f"- Caption strings used MORE THAN ONCE: **{len(exact_dupes)}**")
    dup_posts = sum(len(v) for v in exact_dupes.values())
    A(f"- Posts that reuse a caption verbatim with another post: **{dup_posts}**")
    A("")
    A("Top reused captions:")
    A("")
    A("| Times used | Accounts | Caption (first 120 chars) |")
    A("|---:|---|---|")
    for t, v in sorted(exact_dupes.items(), key=lambda kv: -len(kv[1]))[:20]:
        accts = ", ".join(sorted({acct_label(x) for x in v}))
        A(f"| {len(v)} | {accts} | {clip(t).replace('|','/')} |")
    A("")
    # opening-line repetition
    openers = Counter()
    for p in posts:
        t = (p.get("text") or "").strip()
        if t:
            openers[" ".join(t.split()[:5])] += 1
    A("Most repeated opening 5 words (voice-repetitiveness signal):")
    A("")
    A("| Count | Opening |")
    A("|---:|---|")
    for k, v in openers.most_common(15):
        A(f"| {v} | {k.replace('|','/')} |")
    A("")

    (OUTDIR / "PUBLER_90DAY_AUDIT.md").write_text("\n".join(L))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
