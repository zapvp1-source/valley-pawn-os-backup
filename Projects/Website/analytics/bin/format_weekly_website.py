#!/usr/bin/env python3
"""format_weekly_website.py — the ONLY thing allowed to render the Monday #website analytics post.

Built 2026-09-05 (Website Analytics plan Phase 2) for the same reason the aged-inventory formatter
was built on 2026-09-05: a post re-rendered by the model every week drifts, loses rows, and can
mis-map a number without anything noticing. Rule 18 = a completeness gate; this is the correctness
gate. Deterministic in, deterministic out.

    python3 format_weekly_website.py week.json        # prints the exact Slack body, exit 0
                                                       # prints NOTHING and exits 2 if invalid

The caller (the `weekly-analytics-summary` Cowork task, or later ga4_pull.py) writes week.json and
posts stdout VERBATIM on exit 0. On exit 2 it posts nothing and DMs Joshua the one plain line.

week.json schema (all counts are integers, all rates are percentages as numbers):
{
  "period":      {"start": "2026-08-24", "end": "2026-08-30"},
  "prior":       {"start": "2026-08-17", "end": "2026-08-23"},
  "kpis":   {"sessions": {"v": 460, "prev": 432}, "users": {...}, "engaged_sessions": {...},
             "engagement_rate": {"v": 61.7, "prev": 70.8}, "avg_engagement_seconds": {"v": 41, "prev": 40},
             "page_views": {...}, "key_events": {...}},
  "leads":  {"phone_click": {"v": 12, "prev": 9, "by_store": {"Culpeper": 4, ...}},
             "sms_click":   {...}, "directions_click": {...},
             "email_click": {...},          # optional
             "form_submit": {...}},         # optional
  "channels":  [{"name": "Organic Search", "sessions": 325, "prev": 280}, ...],
  "top_pages": [{"path": "/", "views": 418, "prev": 433}, ...],
  "search":    {"clicks": {"v": 120, "prev": 111}, "impressions": {...}, "ctr": {...},
                "position": {"v": 12.4, "prev": 13.1},
                "queries": [{"q": "pawn shop near me", "position": 8.1, "prev": 11.2, "clicks": 14}],
                "issues": ["Product snippets: 3 items with errors"]},   # search block optional
  "notes":  ["free-text line", ...]         # optional, appended under Watch
}
Only `period`, `prior`, `kpis` and `channels` are required. `leads` is strongly expected — if it is
absent the post still renders but carries an explicit "lead events not measured this week" line so
nobody reads its absence as zero leads.
"""
from __future__ import annotations
import datetime as dt
import json
import sys

STORE_ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
LEAD_LABELS = [("phone_click", "Calls"), ("sms_click", "Texts"), ("directions_click", "Directions"),
               ("email_click", "Email clicks"), ("form_submit", "Form submits")]
REQUIRED_KPIS = ["sessions", "users", "engaged_sessions", "engagement_rate",
                 "avg_engagement_seconds", "page_views", "key_events"]


class Withhold(Exception):
    pass


def d(v, prev):
    """Delta string. Returns '' when there is no usable prior value."""
    if prev in (None, "", 0) or v is None:
        return ""
    try:
        pct = (float(v) - float(prev)) / float(prev) * 100.0
    except (TypeError, ValueError, ZeroDivisionError):
        return ""
    arrow = "▲" if pct > 0.05 else ("▼" if pct < -0.05 else "▬")
    return f" ({arrow} {abs(pct):.1f}%)"


def n(x):
    return f"{int(round(float(x))):,}"


def fdate(a, b):
    A = dt.date.fromisoformat(a)
    B = dt.date.fromisoformat(b)
    same = A.year == B.year and A.month == B.month
    return f"{A:%b %-d}–{B:%-d}, {B:%Y}" if same else f"{A:%b %-d} – {B:%b %-d}, {B:%Y}"


def val(block, key, required=True):
    o = block.get(key)
    if o is None:
        if required:
            raise Withhold(f"missing metric: {key}")
        return None, None
    if isinstance(o, dict):
        return o.get("v"), o.get("prev")
    return o, None


def validate(w: dict) -> None:
    for k in ("period", "prior", "kpis", "channels"):
        if k not in w:
            raise Withhold(f"missing top-level key: {k}")
    for k in ("start", "end"):
        for blk in ("period", "prior"):
            if not w[blk].get(k):
                raise Withhold(f"{blk}.{k} missing")
    if dt.date.fromisoformat(w["period"]["end"]) < dt.date.fromisoformat(w["period"]["start"]):
        raise Withhold("period end before start")
    if dt.date.fromisoformat(w["period"]["start"]) <= dt.date.fromisoformat(w["prior"]["end"]) - dt.timedelta(days=1):
        # prior must end on/just before period start; overlapping windows produced bogus WoW before
        if dt.date.fromisoformat(w["prior"]["end"]) >= dt.date.fromisoformat(w["period"]["start"]):
            raise Withhold("prior window overlaps the reporting period")
    for k in REQUIRED_KPIS:
        v, _ = val(w["kpis"], k)
        if v is None:
            raise Withhold(f"kpis.{k} is null")
    s, _ = val(w["kpis"], "sessions")
    if float(s) <= 0:
        raise Withhold("sessions is zero — treat as a failed pull, not a real week")
    es, _ = val(w["kpis"], "engaged_sessions")
    if float(es) > float(s):
        raise Withhold("engaged sessions exceed sessions — mis-mapped column")
    er, _ = val(w["kpis"], "engagement_rate")
    if not (0 <= float(er) <= 100):
        raise Withhold("engagement rate outside 0–100")
    if not w["channels"]:
        raise Withhold("no traffic channels")
    ch_total = sum(float(c.get("sessions") or 0) for c in w["channels"])
    if ch_total > float(s) * 1.02 or ch_total < float(s) * 0.80:
        raise Withhold(f"channel sessions {ch_total:.0f} do not reconcile with total sessions {float(s):.0f}")
    for p in w.get("top_pages", []):
        if float(p.get("views") or 0) > float(w["kpis"]["page_views"]["v"]):
            raise Withhold(f"page {p.get('path')} has more views than the site total — mis-mapped column")
    lead = w.get("leads") or {}
    for key, _label in LEAD_LABELS:
        o = lead.get(key)
        if isinstance(o, dict) and o.get("by_store"):
            if abs(sum(float(x) for x in o["by_store"].values()) - float(o.get("v") or 0)) > 0.5:
                raise Withhold(f"leads.{key}: per-store counts do not sum to the total")


def render(w: dict) -> str:
    K = w["kpis"]
    L = w.get("leads") or {}
    period = fdate(w["period"]["start"], w["period"]["end"])
    prior = fdate(w["prior"]["start"], w["prior"]["end"])
    out = [f":bar_chart: *Weekly Website Analytics — thevalleypawn.com*",
           f"_{period} vs. {prior} (previous period, match day of week)_", ""]

    # --- Leads first: the site's job is calls, texts, emails and doors -------------
    out.append("*Leads from the website*")
    if L:
        rows, total, total_prev = [], 0, 0
        for key, label in LEAD_LABELS:
            v, prev = val(L, key, required=False)
            if v is None:
                continue
            total += float(v)
            total_prev += float(prev or 0)
            by = (L[key] or {}).get("by_store") if isinstance(L.get(key), dict) else None
            tail = ""
            if by:
                parts = [f"{s} {int(by[s])}" for s in STORE_ORDER if by.get(s)]
                if parts:
                    tail = "  ·  " + " · ".join(parts)
            rows.append(f"• {label}: *{n(v)}*{d(v, prev)}{tail}")
        sessions, _ = val(K, "sessions")
        rate = (total / float(sessions) * 100.0) if sessions else 0
        rows.append(f"• *Total leads: {n(total)}*{d(total, total_prev) if total_prev else ''} "
                    f"— {rate:.1f} per 100 visits")
        out += rows
    else:
        out.append("• _Lead events (call / text / directions clicks) were not measured this week "
                   "— treat as unknown, not zero._")
    out.append("")

    # --- Traffic ------------------------------------------------------------------
    def kline(label, key, fmt=n, suffix=""):
        v, prev = val(K, key)
        return f"• {label}: *{fmt(v)}{suffix}*{d(v, prev)}"

    er_v, er_prev = val(K, "engagement_rate")
    ae_v, ae_prev = val(K, "avg_engagement_seconds")
    out += ["*Traffic*",
            kline("Sessions", "sessions"),
            kline("Visitors", "users"),
            kline("Engaged sessions", "engaged_sessions") +
            f"  ·  engagement rate *{float(er_v):.1f}%*{d(er_v, er_prev)}",
            f"• Avg time per visit: *{int(round(float(ae_v)))}s*{d(ae_v, ae_prev)}",
            kline("Page views", "page_views"),
            kline("Key events", "key_events"), ""]

    total_ch = sum(float(c.get("sessions") or 0) for c in w["channels"]) or 1
    out.append("*Where visitors came from*")
    for c in sorted(w["channels"], key=lambda x: -float(x.get("sessions") or 0))[:7]:
        sess = float(c.get("sessions") or 0)
        out.append(f"• {c['name']} — *{n(sess)}* ({sess / total_ch * 100:.1f}%)"
                   f"{d(sess, c.get('prev'))}")
    out.append("")

    if w.get("top_pages"):
        out.append("*Top pages*")
        for i, p in enumerate(w["top_pages"][:8], 1):
            out.append(f"{i}. `{p['path']}` — {n(p['views'])}{d(p['views'], p.get('prev'))}")
        out.append("")

    S = w.get("search")
    if S:
        out.append("*Search (Google)*")
        for label, key, fmt, sfx in [("Clicks", "clicks", n, ""), ("Impressions", "impressions", n, ""),
                                     ("CTR", "ctr", lambda x: f"{float(x):.1f}", "%")]:
            v, prev = val(S, key, required=False)
            if v is not None:
                out.append(f"• {label}: *{fmt(v)}{sfx}*{d(v, prev)}")
        pv, pp = val(S, "position", required=False)
        if pv is not None:
            # lower is better for average position — invert the arrow
            arrow = ""
            if pp:
                delta = float(pp) - float(pv)
                arrow = f" ({'▲' if delta > 0.05 else ('▼' if delta < -0.05 else '▬')} {abs(delta):.1f} places)"
            out.append(f"• Average position: *{float(pv):.1f}*{arrow}")
        movers = []
        for q in (S.get("queries") or [])[:6]:
            if q.get("prev") is None:
                continue
            delta = float(q["prev"]) - float(q["position"])
            if abs(delta) >= 0.5:
                movers.append(f"“{q['q']}” {float(q['prev']):.0f} → {float(q['position']):.0f}")
        if movers:
            out.append("• Rank moves: " + " · ".join(movers))
        for issue in (S.get("issues") or [])[:3]:
            out.append(f"• :warning: {issue}")
        out.append("")

    if w.get("notes"):
        out.append("*Watch*")
        out += [f"• {x}" for x in w["notes"][:4]]
        out.append("")

    out.append(f"_Source: GA4 property 353209303, All Users, {period} vs previous period "
               f"(match day of week)._")
    out.append("*Sent using* Claude")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: format_weekly_website.py <week.json>", file=sys.stderr)
        return 2
    try:
        w = json.loads(open(sys.argv[1], encoding="utf-8").read())
        validate(w)
        body = render(w)
    except Withhold as e:
        print(f"WITHHOLD — {e}", file=sys.stderr)
        return 2
    except Exception as e:  # malformed JSON, wrong types, anything
        print(f"WITHHOLD — {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if len(body) < 300 or "Traffic" not in body:
        print("WITHHOLD — rendered body failed its own sanity check", file=sys.stderr)
        return 2
    sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
