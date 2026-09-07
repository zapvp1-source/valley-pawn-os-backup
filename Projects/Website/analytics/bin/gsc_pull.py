#!/usr/bin/env python3
"""gsc_pull.py — Google Search Console pull for thevalleypawn.com.

Organic search is 64–71% of the site's sessions and nothing in the fleet has ever measured it:
no rank tracking, and Search Console's structured-data emails land in an inbox instead of a report.
This adds the missing half of website analytics.

    python3 gsc_pull.py --check          # verify access
    python3 gsc_pull.py --week           # last full Mon–Sun + prior; writes data/gsc/week_<end>.json
                                         # and a `search` block ready to merge into week.json

Tracked keyword set = the queries the business actually competes for (5 cities × the three intents).
A query the site does not rank for simply doesn't come back — that absence is itself the finding.
Exit codes: 0 ok · 1 no access yet (run google_grant.py) · 2 pull failed.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "gsc"
DATA.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
from google_auth import GOOGLE_SETUP_HINT, NeedsGrant, SEARCH_SCOPE, api_post, has_scope  # noqa: E402

SITE = "https://thevalleypawn.com/"
API = "https://www.googleapis.com/webmasters/v3/sites/" + SITE.replace("/", "%2F").replace(":", "%3A")
CITIES = ["culpeper", "waynesboro", "harrisonburg", "lexington", "roanoke"]
TRACKED = ([f"pawn shop {c} va" for c in CITIES] +
           [f"sell gold {c} va" for c in CITIES] +
           ["pawn shop near me", "pawn loan virginia", "no credit check loan virginia",
            "ffl transfer virginia", "sell jewelry shenandoah valley"])


def query(start: str, end: str, dims: list[str], limit: int = 500) -> list[dict]:
    body = {"startDate": start, "endDate": end, "dimensions": dims, "rowLimit": limit,
            "type": "web", "dataState": "final"}
    j = api_post(f"{API}/searchAnalytics/query", body, SEARCH_SCOPE)
    return j.get("rows", [])


def summarize(start: str, end: str) -> dict:
    tot = query(start, end, [])
    t = tot[0] if tot else {}
    rows = query(start, end, ["query"])
    per = {r["keys"][0].lower(): r for r in rows}
    tracked = []
    for q in TRACKED:
        r = per.get(q)
        if r:
            tracked.append({"q": q, "position": round(r["position"], 1),
                            "clicks": int(r["clicks"]), "impressions": int(r["impressions"])})
    top = [{"q": r["keys"][0], "position": round(r["position"], 1), "clicks": int(r["clicks"]),
            "impressions": int(r["impressions"])}
           for r in sorted(rows, key=lambda x: -x["clicks"])[:15]]
    pages = [{"path": r["keys"][0], "clicks": int(r["clicks"]), "impressions": int(r["impressions"]),
              "position": round(r["position"], 1)}
             for r in sorted(query(start, end, ["page"]), key=lambda x: -x["clicks"])[:15]]
    return {"start": start, "end": end,
            "clicks": int(t.get("clicks", 0)), "impressions": int(t.get("impressions", 0)),
            "ctr": round(t.get("ctr", 0) * 100, 2), "position": round(t.get("position", 0), 1),
            "tracked": tracked, "top_queries": top, "top_pages": pages}


def search_block(cur: dict, prev: dict) -> dict:
    pmap = {q["q"]: q for q in prev["tracked"]}
    queries = []
    for q in cur["tracked"]:
        p = pmap.get(q["q"])
        queries.append({"q": q["q"], "position": q["position"], "clicks": q["clicks"],
                        "prev": p["position"] if p else None})
    queries.sort(key=lambda x: abs((x["prev"] or x["position"]) - x["position"]), reverse=True)
    return {"clicks": {"v": cur["clicks"], "prev": prev["clicks"]},
            "impressions": {"v": cur["impressions"], "prev": prev["impressions"]},
            "ctr": {"v": cur["ctr"], "prev": prev["ctr"]},
            "position": {"v": cur["position"], "prev": prev["position"]},
            "queries": queries, "issues": []}


def last_full_week(today: dt.date) -> tuple[dt.date, dt.date]:
    end = today - dt.timedelta(days=today.weekday() + 1)
    return end - dt.timedelta(days=6), end


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--week", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if not has_scope(SEARCH_SCOPE):
        print("NO ACCESS — " + GOOGLE_SETUP_HINT, file=sys.stderr)
        return 1
    try:
        if a.check:
            end = dt.date.today() - dt.timedelta(days=3)   # GSC data lags ~2–3 days
            s = summarize(str(end - dt.timedelta(days=6)), str(end))
            print(f"OK — Search Console reachable. Last 7 days: {s['clicks']} clicks, "
                  f"{s['impressions']} impressions, avg position {s['position']}.")
            print(f"Tracked queries with data: {len(s['tracked'])} of {len(TRACKED)}")
            return 0
        s, e = last_full_week(dt.date.today())
        cur = summarize(str(s), str(e))
        prev = summarize(str(s - dt.timedelta(days=7)), str(e - dt.timedelta(days=7)))
        out = {"current": cur, "prior": prev, "search": search_block(cur, prev)}
        path = Path(a.out) if a.out else DATA / f"week_{e}.json"
        path.write_text(json.dumps(out, indent=2))
        (DATA / "week_latest.json").write_text(json.dumps(out, indent=2))
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
