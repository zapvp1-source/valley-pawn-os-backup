#!/usr/bin/env python3
"""
Valley Pawn — Missed Calls & Voicemails trend report generator.

Reads daily_log.csv (one row per store per day: date,store,candidates,resolved,
unresolved,callback_pct) sitting alongside this script, and writes report.html
in the same folder — a single self-contained HTML file (Chart.js via CDN) showing:

  - Summary cards (YTD totals, overall callback %, days tracked)
  - Daily missed calls by store (stacked bar)
  - Missed calls by month, by store (grouped bar)
  - Running year-to-date cumulative total (line)
  - Callback % trend, daily by store + overall (line)
  - Full data table

Additive / idempotent: safe to re-run any number of times, always rewrites report.html
fresh from the current CSV. Run with no arguments; both files are resolved relative to
this script's own directory so it works regardless of the caller's cwd.
"""
import csv
import json
import os
from collections import defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "daily_log.csv")
OUT_PATH = os.path.join(HERE, "report.html")

STORE_COLORS = {
    "Harrisonburg": "#2563eb",
    "Waynesboro": "#dc2626",
    "Lexington": "#059669",
    "Culpeper": "#d97706",
    "Roanoke": "#7c3aed",
}
DEFAULT_COLOR = "#6b7280"


def load_rows():
    rows = []
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            r["candidates"] = int(r["candidates"])
            r["resolved"] = int(r["resolved"])
            r["unresolved"] = int(r["unresolved"])
            r["callback_pct"] = float(r["callback_pct"])
            rows.append(r)
    rows.sort(key=lambda r: (r["date"], r["store"]))
    return rows


def color_for(store):
    return STORE_COLORS.get(store, DEFAULT_COLOR)


def build(rows):
    stores = sorted({r["store"] for r in rows})
    dates = sorted({r["date"] for r in rows})

    # daily by store: date -> store -> candidates
    daily = defaultdict(lambda: defaultdict(int))
    daily_resolved = defaultdict(lambda: defaultdict(int))
    for r in rows:
        daily[r["date"]][r["store"]] += r["candidates"]
        daily_resolved[r["date"]][r["store"]] += r["resolved"]

    # monthly by store
    monthly = defaultdict(lambda: defaultdict(int))
    monthly_resolved = defaultdict(lambda: defaultdict(int))
    for r in rows:
        month = r["date"][:7]
        monthly[month][r["store"]] += r["candidates"]
        monthly_resolved[month][r["store"]] += r["resolved"]
    months = sorted(monthly.keys())

    # running YTD cumulative (all stores combined), per calendar year
    years = sorted({d[:4] for d in dates})
    ytd_series = {}
    for year in years:
        year_dates = sorted(d for d in dates if d.startswith(year))
        running = 0
        series = []
        for d in year_dates:
            day_total = sum(daily[d].values())
            running += day_total
            series.append({"date": d, "cumulative": running})
        ytd_series[year] = series

    # callback % trend: daily overall + per store
    callback_daily_overall = []
    for d in dates:
        cand = sum(daily[d].values())
        res = sum(daily_resolved[d].values())
        pct = round(res / cand * 100, 1) if cand else None
        callback_daily_overall.append({"date": d, "pct": pct})

    callback_daily_by_store = defaultdict(list)
    cand_by_store_date = defaultdict(lambda: defaultdict(int))
    res_by_store_date = defaultdict(lambda: defaultdict(int))
    for r in rows:
        cand_by_store_date[r["store"]][r["date"]] = r["candidates"]
        res_by_store_date[r["store"]][r["date"]] = r["resolved"]
    for store in stores:
        for d in dates:
            cand = cand_by_store_date[store].get(d, 0)
            res = res_by_store_date[store].get(d, 0)
            pct = round(res / cand * 100, 1) if cand else None
            callback_daily_by_store[store].append({"date": d, "pct": pct})

    # summary
    total_candidates = sum(r["candidates"] for r in rows)
    total_resolved = sum(r["resolved"] for r in rows)
    total_unresolved = sum(r["unresolved"] for r in rows)
    overall_pct = round(total_resolved / total_candidates * 100, 1) if total_candidates else 0
    per_store_summary = []
    for store in stores:
        srows = [r for r in rows if r["store"] == store]
        c = sum(r["candidates"] for r in srows)
        res = sum(r["resolved"] for r in srows)
        per_store_summary.append({
            "store": store,
            "candidates": c,
            "resolved": res,
            "unresolved": c - res,
            "pct": round(res / c * 100, 1) if c else 0,
        })

    return {
        "stores": stores,
        "dates": dates,
        "months": months,
        "years": years,
        "daily": daily,
        "monthly": monthly,
        "ytd_series": ytd_series,
        "callback_daily_overall": callback_daily_overall,
        "callback_daily_by_store": callback_daily_by_store,
        "total_candidates": total_candidates,
        "total_resolved": total_resolved,
        "total_unresolved": total_unresolved,
        "overall_pct": overall_pct,
        "per_store_summary": per_store_summary,
        "rows": rows,
    }


def render(data):
    stores = data["stores"]
    dates = data["dates"]
    months = data["months"]

    daily_datasets = [{
        "label": store,
        "backgroundColor": color_for(store),
        "data": [data["daily"][d].get(store, 0) for d in dates],
    } for store in stores]

    monthly_datasets = [{
        "label": store,
        "backgroundColor": color_for(store),
        "data": [data["monthly"][m].get(store, 0) for m in months],
    } for store in stores]

    ytd_datasets = []
    palette = ["#111827", "#2563eb", "#dc2626", "#059669", "#d97706"]
    for i, year in enumerate(data["years"]):
        series = data["ytd_series"][year]
        ytd_datasets.append({
            "label": f"{year} running total",
            "borderColor": palette[i % len(palette)],
            "backgroundColor": "transparent",
            "data": [{"x": p["date"], "y": p["cumulative"]} for p in series],
            "tension": 0.15,
        })

    callback_datasets = [{
        "label": "Overall",
        "borderColor": "#111827",
        "backgroundColor": "transparent",
        "borderWidth": 2.5,
        "data": [p["pct"] for p in data["callback_daily_overall"]],
        "spanGaps": True,
    }]
    for store in stores:
        callback_datasets.append({
            "label": store,
            "borderColor": color_for(store),
            "backgroundColor": "transparent",
            "borderDash": [4, 3],
            "data": [p["pct"] for p in data["callback_daily_by_store"][store]],
            "spanGaps": True,
        })

    cards = "".join(f"""
      <div class="card">
        <div class="card-label">{s['store']}</div>
        <div class="card-value">{s['pct']}%</div>
        <div class="card-sub">{s['resolved']}/{s['candidates']} resolved &middot; {s['unresolved']} outstanding</div>
      </div>""" for s in data["per_store_summary"])

    table_rows = "".join(f"""
        <tr>
          <td>{r['date']}</td>
          <td>{r['store']}</td>
          <td class="num">{r['candidates']}</td>
          <td class="num">{r['resolved']}</td>
          <td class="num">{r['unresolved']}</td>
          <td class="num">{r['callback_pct']}%</td>
        </tr>""" for r in reversed(data["rows"]))

    generated = datetime.now().strftime("%b %d, %Y %I:%M %p")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Valley Pawn — Missed Calls &amp; Voicemails Trend Report</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<style>
  :root {{ --ink:#111827; --sub:#6b7280; --line:#e5e7eb; --bg:#f9fafb; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          margin:0; padding:32px; background:var(--bg); color:var(--ink); }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  .meta {{ color:var(--sub); font-size:13px; margin-bottom:28px; }}
  .cards {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:32px; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:16px 20px; min-width:170px; flex:1; }}
  .card-label {{ font-size:12px; color:var(--sub); text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px; }}
  .card-value {{ font-size:28px; font-weight:600; }}
  .card-sub {{ font-size:12px; color:var(--sub); margin-top:4px; }}
  .card.total .card-value {{ color:#111827; }}
  .panel {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:20px; margin-bottom:24px; }}
  .panel h2 {{ font-size:15px; margin:0 0 16px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }}
  th {{ color:var(--sub); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.03em; }}
  td.num, th.num {{ text-align:right; font-variant-numeric: tabular-nums; }}
  canvas {{ max-height:320px; }}
</style>
</head>
<body>
  <h1>Missed Calls &amp; Voicemails — Trend Report</h1>
  <div class="meta">Full Circle Finance Inc DBA Valley Pawn &middot; generated {generated} &middot; source: Zoom Phone call logs via the daily EOD review</div>

  <div class="cards">
    <div class="card total">
      <div class="card-label">All stores, all time</div>
      <div class="card-value">{data['overall_pct']}%</div>
      <div class="card-sub">{data['total_resolved']}/{data['total_candidates']} resolved &middot; {data['total_unresolved']} outstanding</div>
    </div>{cards}
  </div>

  <div class="panel">
    <h2>Daily missed calls by store</h2>
    <canvas id="dailyChart"></canvas>
  </div>

  <div class="panel">
    <h2>Missed calls by month, by store</h2>
    <canvas id="monthlyChart"></canvas>
  </div>

  <div class="panel">
    <h2>Running year-to-date total</h2>
    <canvas id="ytdChart"></canvas>
  </div>

  <div class="panel">
    <h2>Callback % trend</h2>
    <canvas id="callbackChart"></canvas>
  </div>

  <div class="panel">
    <h2>Daily detail</h2>
    <table>
      <thead><tr><th>Date</th><th>Store</th><th class="num">Candidates</th><th class="num">Resolved</th><th class="num">Unresolved</th><th class="num">Callback %</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>

<script>
const dates = {json.dumps(dates)};
const months = {json.dumps(months)};

new Chart(document.getElementById('dailyChart'), {{
  type: 'bar',
  data: {{ labels: dates, datasets: {json.dumps(daily_datasets)} }},
  options: {{ responsive:true, scales: {{ x: {{ stacked:true }}, y: {{ stacked:true, beginAtZero:true, title:{{display:true,text:'missed calls'}} }} }} }}
}});

new Chart(document.getElementById('monthlyChart'), {{
  type: 'bar',
  data: {{ labels: months, datasets: {json.dumps(monthly_datasets)} }},
  options: {{ responsive:true, scales: {{ x: {{ stacked:false }}, y: {{ beginAtZero:true, title:{{display:true,text:'missed calls'}} }} }} }}
}});

new Chart(document.getElementById('ytdChart'), {{
  type: 'line',
  data: {{ datasets: {json.dumps(ytd_datasets)} }},
  options: {{ responsive:true, parsing:false,
    scales: {{ x: {{ type:'category', labels: dates }}, y: {{ beginAtZero:true, title:{{display:true,text:'cumulative missed calls (YTD)'}} }} }} }}
}});

new Chart(document.getElementById('callbackChart'), {{
  type: 'line',
  data: {{ labels: dates, datasets: {json.dumps(callback_datasets)} }},
  options: {{ responsive:true, scales: {{ y: {{ min:0, max:100, title:{{display:true,text:'callback %'}} }} }} }}
}});
</script>
</body>
</html>
"""
    return html


def main():
    rows = load_rows()
    if not rows:
        raise SystemExit(f"No data in {CSV_PATH}")
    data = build(rows)
    html = render(data)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Wrote {OUT_PATH} ({len(rows)} rows, {len(data['dates'])} days, {len(data['stores'])} stores)")


if __name__ == "__main__":
    main()
