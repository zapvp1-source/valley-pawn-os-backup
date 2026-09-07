#!/usr/bin/env python3
"""ga4_pull.py — headless GA4 pull for thevalleypawn.com (property 353209303).

Replaces the Chrome scraping of the GA4 UI that four separate tasks do every week
(weekly-analytics-summary, vp-website-trend-daily-refresh, vp-ai-visibility-metrics Part B,
plus the Jetpack numbers in vp-website-shop-weekly-report). One pull, one JSON, many readers.

    python3 ga4_pull.py --check                 # verify access; prints scope status, exits 0/1
    python3 ga4_pull.py --week                  # last full Mon–Sun + prior; writes week.json for
                                                #   format_weekly_website.py and data/ga4/<end>.json
    python3 ga4_pull.py --start A --end B       # any window (ISO dates)
    python3 ga4_pull.py --windows               # 7/28/90/365-day rollups for the trend artifact

The important thing it pulls that no current report shows: LEAD EVENTS BY STORE.
`phone_click`, `sms_click`, `directions_click` (shipped in the sticky contact bar 2026-08-23) carry
a store parameter; `email_click` / `form_submit` are included when present. Sessions are vanity;
these are the calls, texts and doors the site exists to produce.

Exit codes: 0 ok · 1 no access yet (run google_grant.py) · 2 pull failed.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "ga4"
DATA.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
from google_auth import ANALYTICS_SCOPE, GOOGLE_SETUP_HINT, NeedsGrant, api_post, has_scope  # noqa: E402

PROPERTY = "353209303"
BASE = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}"
STORE_ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
LEAD_EVENTS = ["phone_click", "sms_click", "directions_click", "email_click", "form_submit"]
# Custom event params are exposed as customEvent:<name>; the contact bar sends `store`.
STORE_DIM = "customEvent:store"


def run_report(body: dict) -> dict:
    return api_post(f"{BASE}:runReport", body, ANALYTICS_SCOPE)


def _rng(a, b):
    return [{"startDate": a, "endDate": b}]


def totals(start: str, end: str) -> dict:
    r = run_report({
        "dateRanges": _rng(start, end),
        "metrics": [{"name": m} for m in ["sessions", "totalUsers", "engagedSessions",
                                          "engagementRate", "averageSessionDuration",
                                          "screenPageViews", "eventCount", "keyEvents"]],
    })
    row = (r.get("rows") or [{}])[0].get("metricValues", [])
    v = [x.get("value", 0) for x in row] or [0] * 8
    return {
        "sessions": int(float(v[0])), "users": int(float(v[1])), "engaged_sessions": int(float(v[2])),
        "engagement_rate": round(float(v[3]) * 100, 2), "avg_engagement_seconds": int(float(v[4])),
        "page_views": int(float(v[5])), "event_count": int(float(v[6])), "key_events": int(float(v[7])),
    }


def channels(start: str, end: str) -> list[dict]:
    r = run_report({
        "dateRanges": _rng(start, end),
        "dimensions": [{"name": "sessionDefaultChannelGroup"}],
        "metrics": [{"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
        "limit": 15,
    })
    return [{"name": row["dimensionValues"][0]["value"],
             "sessions": int(float(row["metricValues"][0]["value"]))}
            for row in r.get("rows", [])]


def top_pages(start: str, end: str, limit: int = 12) -> list[dict]:
    r = run_report({
        "dateRanges": _rng(start, end),
        "dimensions": [{"name": "pagePath"}],
        "metrics": [{"name": "screenPageViews"}],
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        "limit": limit,
    })
    return [{"path": row["dimensionValues"][0]["value"],
             "views": int(float(row["metricValues"][0]["value"]))}
            for row in r.get("rows", [])]


def leads(start: str, end: str) -> dict:
    """Lead events, total and per store. Falls back to totals-only if the store param is absent."""
    out: dict = {}
    r = run_report({
        "dateRanges": _rng(start, end),
        "dimensions": [{"name": "eventName"}],
        "metrics": [{"name": "eventCount"}],
        "limit": 200,
    })
    for row in r.get("rows", []):
        name = row["dimensionValues"][0]["value"]
        if name in LEAD_EVENTS:
            out[name] = {"v": int(float(row["metricValues"][0]["value"]))}
    if not out:
        return {}
    try:
        r2 = run_report({
            "dateRanges": _rng(start, end),
            "dimensions": [{"name": "eventName"}, {"name": STORE_DIM}],
            "metrics": [{"name": "eventCount"}],
            "limit": 500,
        })
        per: dict = {}
        for row in r2.get("rows", []):
            ev = row["dimensionValues"][0]["value"]
            store = (row["dimensionValues"][1]["value"] or "").strip().title()
            if ev in out and store in STORE_ORDER:
                per.setdefault(ev, {})[store] = per.setdefault(ev, {}).get(store, 0) + int(float(row["metricValues"][0]["value"]))
        for ev, by in per.items():
            # only attach when it reconciles — the formatter withholds on a mismatch, so never
            # hand it a breakdown that does not sum to the total (e.g. events sent without `store`)
            if abs(sum(by.values()) - out[ev]["v"]) < 0.5:
                out[ev]["by_store"] = by
    except Exception:
        pass
    return out


def snapshot(start: str, end: str) -> dict:
    return {"start": start, "end": end, "kpis": totals(start, end), "channels": channels(start, end),
            "top_pages": top_pages(start, end), "leads": leads(start, end)}


def merge_prior(cur: dict, prev: dict) -> dict:
    """Fold prior-period values into the current snapshot in the formatter's schema."""
    kpis = {k: {"v": v, "prev": prev["kpis"].get(k)} for k, v in cur["kpis"].items()}
    pmap = {c["name"]: c["sessions"] for c in prev["channels"]}
    ch = [{"name": c["name"], "sessions": c["sessions"], "prev": pmap.get(c["name"])} for c in cur["channels"]]
    ppages = {p["path"]: p["views"] for p in prev["top_pages"]}
    pages = [{"path": p["path"], "views": p["views"], "prev": ppages.get(p["path"])} for p in cur["top_pages"]]
    lead = {}
    for k, o in (cur.get("leads") or {}).items():
        item = dict(o)
        item["prev"] = (prev.get("leads") or {}).get(k, {}).get("v")
        lead[k] = item
    return {"period": {"start": cur["start"], "end": cur["end"]},
            "prior": {"start": prev["start"], "end": prev["end"]},
            "kpis": kpis, "channels": ch, "top_pages": pages, "leads": lead}


def last_full_week(today: dt.date) -> tuple[dt.date, dt.date]:
    end = today - dt.timedelta(days=today.weekday() + 1)   # most recent Sunday
    return end - dt.timedelta(days=6), end


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--week", action="store_true")
    ap.add_argument("--windows", action="store_true")
    ap.add_argument("--start"), ap.add_argument("--end")
    ap.add_argument("--out")
    a = ap.parse_args()

    if not has_scope(ANALYTICS_SCOPE):
        print("NO ACCESS — " + GOOGLE_SETUP_HINT, file=sys.stderr)
        return 1
    if a.check:
        try:
            t = totals(str(dt.date.today() - dt.timedelta(days=7)), str(dt.date.today() - dt.timedelta(days=1)))
            print(f"OK — GA4 reachable. Last 7 days: {t['sessions']} sessions, {t['key_events']} key events.")
            ld = leads(str(dt.date.today() - dt.timedelta(days=7)), str(dt.date.today() - dt.timedelta(days=1)))
            print("Lead events seen:", ", ".join(f"{k}={v['v']}" for k, v in ld.items()) or "NONE "
                  "(check that the contact-bar events are firing)")
            return 0
        except NeedsGrant as e:
            print(f"NO ACCESS — {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"PULL FAILED — {type(e).__name__}: {e}", file=sys.stderr)
            return 2

    try:
        if a.windows:
            today = dt.date.today()
            out = {}
            for label, days in [("d7", 7), ("d28", 28), ("d90", 90), ("d365", 365)]:
                end = today - dt.timedelta(days=1)
                start = end - dt.timedelta(days=days - 1)
                pend = start - dt.timedelta(days=1)
                out[label] = merge_prior(snapshot(str(start), str(end)),
                                         snapshot(str(pend - dt.timedelta(days=days - 1)), str(pend)))
            path = Path(a.out) if a.out else DATA / f"windows_{dt.date.today()}.json"
            path.write_text(json.dumps(out, indent=2))
            print(f"WROTE {path}")
            return 0

        if a.week or not (a.start and a.end):
            s, e = last_full_week(dt.date.today())
        else:
            s, e = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
        ps, pe = s - dt.timedelta(days=7), e - dt.timedelta(days=7)
        week = merge_prior(snapshot(str(s), str(e)), snapshot(str(ps), str(pe)))
        path = Path(a.out) if a.out else DATA / f"week_{e}.json"
        path.write_text(json.dumps(week, indent=2))
        (DATA / "week_latest.json").write_text(json.dumps(week, indent=2))
        print(f"WROTE {path}")
        return 0
    except NeedsGrant as e:
        print(f"NO ACCESS — {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"PULL FAILED — {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
