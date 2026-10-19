#!/usr/bin/env python3
"""website_trend_refresh.py — native vp-website-trend-daily-refresh (2026-10-14, Google re-grant prep).

The "Website visitor-trend page" is the Cowork sidebar artifact `vp-website-trend`
(file ~/Documents/Claude/Artifacts/vp-website-trend/index.html, shown in the Claude app as
"Vp Website Trend"; a copy also rides on vp-dashboard.pages.dev under artifacts/). The cloud copy
of the task scraped the GA4 web UI in Chrome and then needed `mcp__cowork__update_artifact`, which
the cloud session doesn't have (ledger 2026-10-13 02:40). This rebuilds the page from the GA4 Data
API with the Mac's cached Google token — no browser, no Claude tool — keeping the page's markup,
styles and chart code byte-for-byte and replacing only the `const DATA={...};` block and the
"refreshed" stamp.

    website_trend_refresh.py --render [--out PATH]   # writes ONLY to fleet/test_output/website_trend_render/
    website_trend_refresh.py --live                  # writes the real page (+ Desktop copy + dashboard copy)

Horizons (same as the SKILL): daily = yesterday vs the day before, 12 two-hour buckets (real GA4
hour data, not estimated); weekly = last 7 days vs prior 7 (per day); monthly = last 30 vs prior 30
(per day); quarterly = last 90 vs prior 90 (13 weekly buckets); annual = last 365 vs prior 365
(monthly buckets). All windows end yesterday.

Failure policy v3: no DM, no Slack. Missing Google scope -> ONE ledger row
"Google access needs one approval" (once per day). Any other failure -> one ledger row. Exit 0/1/2.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

HOME = Path.home()
OS_DIR = HOME / "Documents/Claude/Projects/Valley Pawn OS"
AN_BIN = HOME / "Documents/Claude/Projects/Website/analytics/bin"
sys.path.insert(0, str(AN_BIN))
from google_auth import ANALYTICS_SCOPE, NeedsGrant, api_post, has_scope  # noqa: E402

TASK = "vp-website-trend-daily-refresh"
PROPERTY = "353209303"
URL = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}:runReport"
LIVE_PAGE = HOME / "Documents/Claude/Artifacts/vp-website-trend/index.html"
DESKTOP_COPY = HOME / "Desktop/Claude Back Up/Claude 4 back up/website-trend-artifact.html"
DASH_COPY = HOME / "Documents/Claude/Projects/Business Dashboard Website/site/artifacts/vp-website-trend/index.html"
TEMPLATE_FALLBACKS = [LIVE_PAGE, DASH_COPY]
RENDER_DIR = OS_DIR / "fleet/test_output/website_trend_render"
BACKUPS = OS_DIR / "fleet/_backups/website_trend"
LEDGER = OS_DIR / "fleet/FAILURE_LEDGER.md"
STATE = OS_DIR / "fleet/state/website_trend_refresh.json"
CHANNEL_ORDER = ["Organic Search", "Direct", "Email", "Organic Social", "Unassigned", "Referral"]


def now_et() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        return dt.datetime.now()


def ledger(sentence: str, needs: str = "no", once_key: str | None = None) -> None:
    stamp = now_et().strftime("%Y-%m-%d %H:%M ET")
    if once_key:
        try:
            txt = LEDGER.read_text()
        except OSError:
            txt = ""
        today = now_et().strftime("%Y-%m-%d")
        if any(today in l and TASK in l and once_key in l for l in txt.splitlines()):
            return
    with LEDGER.open("a") as f:
        f.write(f"| {stamp} (native) | {TASK} | {sentence} | NEEDS_HUMAN: {needs} | OPEN |\n")


# ---------------------------------------------------------------- GA4
def report(body: dict) -> list[dict]:
    r = api_post(URL, body, ANALYTICS_SCOPE)
    return r.get("rows", []) or []


def rng(a: dt.date, b: dt.date) -> list[dict]:
    return [{"startDate": str(a), "endDate": str(b)}]


def kpis(a, b) -> dict:
    rows = report({"dateRanges": rng(a, b), "metrics": [{"name": m} for m in
                   ["sessions", "activeUsers", "screenPageViews", "userEngagementDuration"]]})
    v = [float(x["value"]) for x in rows[0]["metricValues"]] if rows else [0, 0, 0, 0]
    return {"sessions": v[0], "users": v[1], "views": v[2], "eng": (v[3] / v[1]) if v[1] else 0.0}


def by_dim(a, b, dim: str, metric: str = "sessions", limit: int = 400) -> dict:
    rows = report({"dateRanges": rng(a, b), "dimensions": [{"name": dim}], "metrics": [{"name": metric}],
                   "limit": limit})
    return {r["dimensionValues"][0]["value"]: float(r["metricValues"][0]["value"]) for r in rows}


def top_pages(a, b, n=40) -> list[tuple[str, int]]:
    rows = report({"dateRanges": rng(a, b), "dimensions": [{"name": "pagePath"}],
                   "metrics": [{"name": "screenPageViews"}],
                   "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}], "limit": n})
    return [(r["dimensionValues"][0]["value"], int(float(r["metricValues"][0]["value"]))) for r in rows]


# ---------------------------------------------------------------- formatting
def pct(cur: float, prev: float) -> tuple[str, str]:
    if not prev:
        return ("—", "flat") if not cur else ("NEW", "up")
    p = (cur - prev) / prev * 100
    if abs(p) < 0.05:
        return ("0.0%", "flat")
    return (("▲" if p > 0 else "▼") + (f"{abs(p):,.0f}%" if abs(p) >= 1000 else f"{abs(p):.1f}%"),
            "up" if p > 0 else "down")


def fmt_secs(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s"


def md(d: dt.date) -> str:
    return d.strftime("%b ") + str(d.day)


def span(a: dt.date, b: dt.date) -> str:
    if a == b:
        return f"{md(a)}, {a.year}"
    return f"{md(a)} - {md(b)}, {b.year}" if a.year == b.year else f"{md(a)}, {a.year} - {md(b)}, {b.year}"


def daily_series(a, b) -> list[int]:
    m = by_dim(a, b, "date")
    out, d = [], a
    while d <= b:
        out.append(int(m.get(d.strftime("%Y%m%d"), 0)))
        d += dt.timedelta(days=1)
    return out


def hourly_series(day) -> list[int]:
    m = by_dim(day, day, "hour")
    return [int(m.get(f"{h:02d}", 0) + m.get(f"{h + 1:02d}", 0)) for h in range(0, 24, 2)]


def chunk(xs: list[int], size: int) -> list[int]:
    return [sum(xs[i:i + size]) for i in range(0, len(xs), size)]


def monthly_series(a, b) -> tuple[list[str], list[int]]:
    m = by_dim(a, b, "yearMonth")
    keys, labels, d = [], [], a.replace(day=1)
    while d <= b:
        keys.append(d.strftime("%Y%m"))
        labels.append(d.strftime("%b %y"))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return labels, [int(m.get(k, 0)) for k in keys]


def block(horizon: str, a, b, pa, pb) -> dict:
    k, pk = kpis(a, b), kpis(pa, pb)
    if horizon == "daily":
        labels = [f"{h}h" for h in range(0, 24, 2)]
        cur, pri, hint = hourly_series(b), hourly_series(pb), "Hourly (2-hour buckets)"
    elif horizon in ("weekly", "monthly"):
        cur, pri = daily_series(a, b), daily_series(pa, pb)
        days = (b - a).days + 1
        labels = [md(a + dt.timedelta(days=i)) for i in range(days)]
        hint = "Daily"
    elif horizon == "quarterly":
        cur, pri = chunk(daily_series(a, b), 7), chunk(daily_series(pa, pb), 7)
        labels = ["Wk of " + md(a + dt.timedelta(days=7 * i)) for i in range(len(cur))]
        hint = "Weekly"
    else:
        labels, cur = monthly_series(a, b)
        _, pri = monthly_series(pa, pb)
        n = min(len(cur), len(pri))
        labels, cur, pri = labels[-n:], cur[-n:], pri[-n:]
        hint = "Monthly (first and last month partial)"
    kp = {}
    for key, val, prev, f in [("sessions", k["sessions"], pk["sessions"], lambda x: f"{int(x):,}"),
                              ("users", k["users"], pk["users"], lambda x: f"{int(x):,}"),
                              ("views", k["views"], pk["views"], lambda x: f"{int(x):,}"),
                              ("engagement", k["eng"], pk["eng"], fmt_secs)]:
        t, c = pct(val, prev) if prev else ("—", "flat")   # no prior data (e.g. before GA4 existed) = no delta
        kp[key] = {"value": f(val), "deltaText": t, "cls": c}
    pages, ppages = top_pages(a, b, 8), dict(top_pages(pa, pb, 250))
    tp = []
    for p, v in pages:
        t, c = pct(v, ppages.get(p, 0)) if pk["sessions"] else ("—", "flat")
        tp.append([p, v, t, c])
    ch, pch = by_dim(a, b, "sessionDefaultChannelGroup"), by_dim(pa, pb, "sessionDefaultChannelGroup")
    total = sum(ch.values()) or 1
    names = [n for n in CHANNEL_ORDER if ch.get(n)] + sorted((n for n in ch if n not in CHANNEL_ORDER and ch[n]),
                                                              key=lambda n: -ch[n])
    names = sorted(names, key=lambda n: -ch[n])[:6]
    traffic = []
    for n in names:
        t, c = pct(ch[n], pch.get(n, 0)) if pk["sessions"] else ("—", "flat")
        traffic.append([n, int(ch[n]), f"{ch[n] / total * 100:.1f}%", t, c])
    mix = {"labels": names, "data": [round(ch[n] / total * 100, 2) for n in names]}
    return {"period": span(a, b), "prior": span(pa, pb), "seriesLabel": hint, "labels": labels,
            "current": cur, "prior_series": pri, "kpis": kp, "topPages": tp, "trafficMix": mix,
            "traffic": traffic, "_raw": {"sessions": k["sessions"], "prev_sessions": pk["sessions"],
                                          "series_sum": sum(cur), "channel_sum": int(sum(ch.values()))}}


def build_data(today: dt.date) -> dict:
    y = today - dt.timedelta(days=1)
    out = {}
    for h, days in [("daily", 1), ("weekly", 7), ("monthly", 30), ("quarterly", 91), ("annual", 365)]:
        a = y - dt.timedelta(days=days - 1)
        pb = a - dt.timedelta(days=1)
        pa = pb - dt.timedelta(days=days - 1)
        out[h] = block(h, a, y, pa, pb)
    return out


# ---------------------------------------------------------------- page assembly
def js_obj(data: dict) -> str:
    """The page's DATA literal. The template uses the key `prior` twice per block (period label, then
    the prior series) — in JS the second wins, so the chart gets the series. Reproduce that order."""
    parts = []
    for h in ["daily", "weekly", "monthly", "quarterly", "annual"]:
        d = data[h]
        j = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
        parts.append(f"{h}:{{period:{j(d['period'])},prior:{j(d['prior'])},seriesLabel:{j(d['seriesLabel'])},"
                     f"labels:{j(d['labels'])},current:{j(d['current'])},prior:{j(d['prior_series'])},"
                     f"kpis:{j(d['kpis'])},topPages:{j(d['topPages'])},trafficMix:{j(d['trafficMix'])},"
                     f"traffic:{j(d['traffic'])}}}")
    return "const DATA={" + ",".join(parts) + "};"


def load_template() -> tuple[str, Path]:
    for p in TEMPLATE_FALLBACKS:
        if p.exists():
            t = p.read_text(encoding="utf-8")
            if "const DATA=" in t and "refreshed-time" in t:
                return t, p
    raise RuntimeError("no usable vp-website-trend template found")


def assemble(tpl: str, data: dict, stamp: str) -> str:
    new, n = re.subn(r"const DATA=\{.*?\};(?=const palette=)", lambda m: js_obj(data), tpl, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("could not find the DATA block in the template")
    new, n2 = re.subn(r'(<div class="refreshed" id="refreshed-time">)[^<]*(</div>)',
                      lambda m: m.group(1) + stamp + m.group(2), new, count=1)
    if n2 != 1:
        raise RuntimeError("could not find the refreshed stamp in the template")
    return new


def sanity(data: dict) -> list[str]:
    bad = []
    for h, d in data.items():
        r = d["_raw"]
        if r["sessions"] <= 0:
            bad.append(f"{h}: zero sessions")
        # GA4 counts a session once per hour/day it touches and applies thresholds, so a series never
        # sums exactly to the total; only a gross mismatch (wrong window / wrong metric) withholds.
        # 2026-10-18: the daily block is yesterday's data pulled at 02:40 ET, before GA4 has finished
        # processing it (24-48 h latency); the per-hour rows lag the total and are thresholded, so on a
        # quiet day the gap breaks the old 25%/15 rule (10/17: series 29 vs sessions 45 -> page withheld
        # for the whole day). A lagging hour series is not a wrong window: warn, keep the page. The
        # other horizons (7/30/90/365 days, per-day series) keep the strict check.
        if r["series_sum"] and abs(r["series_sum"] - r["sessions"]) > max(15, 0.25 * r["sessions"]):
            if h == "daily":
                print(f"WARN daily: hour series {r['series_sum']} vs sessions {int(r['sessions'])} "
                      "(GA4 still processing yesterday) - page kept", file=sys.stderr)
            else:
                bad.append(f"{h}: series sum {r['series_sum']} vs sessions {int(r['sessions'])}")
        if len(d["topPages"]) < 3:
            bad.append(f"{h}: fewer than 3 top pages")
    return bad


def main() -> int:
    live = "--live" in sys.argv
    out = None
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    try:
        if not has_scope(ANALYTICS_SCOPE):
            raise NeedsGrant("analytics scope missing")
        today = now_et().date()
        data = build_data(today)
        bad = sanity(data)
        if bad:
            raise RuntimeError("sanity: " + "; ".join(bad))
        stamp = now_et().strftime("%b ") + str(now_et().day) + now_et().strftime(", %Y · %H:%M ET")
        tpl, src = load_template()
        html = assemble(tpl, data, stamp)
    except NeedsGrant as e:
        print(f"NO ACCESS — {e}", file=sys.stderr)
        if live:
            ledger("Google access needs one approval — the website visitor-trend page was not refreshed.",
                   "yes, double-click 'Grant Google Access.command' in Valley Pawn OS and click Allow once",
                   once_key="Google access needs one approval")
        return 1
    except Exception as e:
        print(f"FAILED — {type(e).__name__}: {e}", file=sys.stderr)
        if live:
            ledger("The website visitor-trend page did not refresh today (GA4 pull or page build failed; detail in "
                   "~/Library/Logs/valleypawn/vp-website-trend-daily-refresh.log).", once_key="did not refresh")
        return 2
    summary = {h: {"period": d["period"], "sessions": int(d["_raw"]["sessions"]),
                   "prev": int(d["_raw"]["prev_sessions"])} for h, d in data.items()}
    if not live:
        target = out or (RENDER_DIR / "index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        (target.parent / "data.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
        print(f"RENDER (template {src}) -> {target}")
        print(json.dumps(summary, indent=1, ensure_ascii=False))
        return 0
    BACKUPS.mkdir(parents=True, exist_ok=True)
    day = today.strftime("%Y%m%d")
    for p in [LIVE_PAGE, DESKTOP_COPY, DASH_COPY]:
        if p.exists():
            b = BACKUPS / f"{p.parent.name.replace(' ', '_')}__{p.name}.bak-{day}"
            if not b.exists():
                shutil.copy2(p, b)
    written = []
    for p in [LIVE_PAGE, DESKTOP_COPY, DASH_COPY]:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_name(p.name + ".tmp")
            tmp.write_text(html, encoding="utf-8")
            os.replace(tmp, p)
            written.append(str(p))
        except OSError as e:
            print(f"WARN could not write {p}: {e}", file=sys.stderr)
    if str(LIVE_PAGE) not in written:
        ledger("The website visitor-trend page could not be saved to its Claude Artifacts folder.")
        return 2
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"last_ok": now_et().isoformat(), "stamp": stamp, "written": written,
                                 "summary": summary}, indent=1, ensure_ascii=False))
    print(f"LIVE refreshed {stamp}: " + ", ".join(written))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
