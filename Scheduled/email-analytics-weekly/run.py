"""email-analytics-weekly — v2
Permanent driver for the Friday cron. Improvements over v1:
  1. Lives at ~/Documents/Claude/Scheduled/email-analytics-weekly/run.py
  2. Lead-movement headline requires a volume floor (abs change >= 10 clicks OR
     baseline >= 0.10%); tiny-base swings can't dominate.
  3. Trailing window uses MEDIAN, not mean, with an outlier flag emitted when
     max(window) > 3x median.
  4. Campaigns whose clicks are mostly _unlabeled (>= 60% of total tracked
     clicks) get a "no_utm" notes tag so we know to fix the template.
  5. classify_name handles 3+-part names (W1 -- Kickoff -- June 4, 2026).

Output:
  JSON blob to stdout. The orchestrating agent reads .summary and posts the
  5-line summary to #email-campiagns (C0APR5WUL2Z). The agent is responsible
  for the Slack post -- this script does NOT post.
"""
from __future__ import annotations
import sys, json, re, warnings, statistics
warnings.filterwarnings("ignore")
from datetime import datetime, timezone, timedelta, date

sys.path.insert(0, "/Users/joshuadavis/Documents/Claude/Scheduled/_shared")
from brevo_helper import BrevoClient
from sheets_helper import SheetsClient

SHEET_ID = "1EPj22S1zzbSm4B_mRZ4y8TEXXpiCj6YM_75TmVV4d2o"
TAB = "Email Campaign Performance"

NOW_UTC = datetime.now(timezone.utc)
NOW_ISO = NOW_UTC.strftime("%Y-%m-%dT%H:%M:%SZ")
STALE_CUTOFF = NOW_UTC - timedelta(days=14)
RECENT_CUTOFF = NOW_UTC - timedelta(days=90)
SHEETS_EPOCH = date(1899, 12, 30)

# Volume floors for the lead-movement picker
MIN_ABS_DELTA_CLICKS = 10      # absolute click change required to headline
MIN_BASELINE_PCT = 0.10        # OR baseline metric >= this %

# UTM tracking quality threshold
UNLABELED_TAG_THRESHOLD = 0.60 # >=60% of clicks unlabeled -> flag "no_utm"


# ----- helpers -----
def serial_to_iso(serial):
    try:
        return (SHEETS_EPOCH + timedelta(days=int(float(serial)))).isoformat()
    except Exception:
        return ""

def parse_brevo_date(s):
    if not s:
        return None
    s = s.replace("T", " ")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})", s)
    if not m:
        return None
    y, mo, d, h, mi, se = map(int, m.groups())
    return datetime(y, mo, d, h, mi, se, tzinfo=timezone.utc)

def to_sheets_serial(dt):
    return (dt.date() - SHEETS_EPOCH).days

def classify_name(name):
    """category, theme from any of:
      'Weekly -- Education -- 2026-05-21'
      'W1 -- Kickoff -- June 4, 2026'
      'Valley Pawn -- We Buy Gold & Silver (June 2026)'
      'Memorial Day 2026 -- 15% Off In-Store'
    """
    if not name:
        return ("", "")
    parts = [p.strip() for p in re.split(r"\s+[—\-]\s+", name) if p.strip()]
    if len(parts) >= 2:
        return (parts[0], parts[1])
    return (name, "")

def dow(dt):
    return ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][dt.weekday()]

def merge_notes(existing, *new_tags):
    """Merge bracketed [tag] markers without duplicating; preserve any free-text notes."""
    existing = (existing or "").strip()
    tag_re = re.compile(r"\[([a-zA-Z0-9_:.\-]+)\]")
    have = set(tag_re.findall(existing))
    free = tag_re.sub("", existing).strip()
    for t in new_tags:
        if t:
            have.add(t)
    tags = "".join(f"[{t}]" for t in sorted(have))
    return (tags + (" " + free if free else "")).strip()


def main():
    out = {"steps": [], "errors": [], "summary": {}}
    b = BrevoClient()
    s = SheetsClient()

    # ----- read existing sheet -----
    existing_rows = s.read(SHEET_ID, f"{TAB}!A:Z")
    if not existing_rows:
        out["errors"].append("sheet read returned no rows")
        print(json.dumps(out, indent=2, default=str)); return
    header = existing_rows[0]
    existing_dicts = [
        {header[i]: (r[i] if i < len(r) else "") for i in range(len(header))}
        for r in existing_rows[1:]
    ]
    existing_by_id = {
        str(r["campaign_id"]): r
        for r in existing_dicts
        if r.get("campaign_id") not in ("", None)
    }
    out["steps"].append(f"existing_rows={len(existing_dicts)}")

    # ----- pull Brevo sent campaigns -----
    sent = b.list_email_campaigns(status="sent")
    out["steps"].append(f"brevo_sent_total={len(sent)}")

    candidates = []
    for c in sent:
        sd = parse_brevo_date(c.get("sentDate") or "")
        if sd and sd > RECENT_CUTOFF:
            candidates.append((c, sd))
    candidates.sort(key=lambda x: x[1], reverse=True)
    out["steps"].append(f"brevo_recent_90d={len(candidates)}")

    # ----- classify NEW vs STALE vs FROZEN -----
    new_or_stale = []
    for c, sd in candidates:
        cid = str(c["id"])
        if cid not in existing_by_id:
            new_or_stale.append(("NEW", c, sd))
        elif sd > STALE_CUTOFF:
            new_or_stale.append(("STALE", c, sd))
    out["steps"].append(f"to_process={len(new_or_stale)}")
    out["to_process_ids"] = [
        (t, str(c["id"]), sd.isoformat(), c.get("name",""))
        for t, c, sd in new_or_stale
    ]

    # ----- per-campaign: pull stats + bucket + build row -----
    rows_to_write = []
    for tag, c, sd in new_or_stale:
        cid = c["id"]
        try:
            full = b.get_email_campaign(cid, with_stats=True)
            stats = (full.get("statistics") or {}).get("campaignStats") or [{}]
            agg = stats[0] if stats else {}
            recipients = int(agg.get("sent") or 0)
            uniq_opens = int(agg.get("uniqueViews") or 0)
            uniq_clicks= int(agg.get("uniqueClicks") or 0)
            unsubs     = int(agg.get("unsubscriptions") or 0)

            buckets = b.utm_content_bucketed_clicks(cid)
            total_bucketed = sum(buckets.values()) or 1
            unlabeled = buckets.get("_unlabeled", 0)
            unlabeled_share = unlabeled / total_bucketed

            directions_clicks = sum(v for k, v in buckets.items() if k.endswith("_map"))
            calls_clicks      = sum(v for k, v in buckets.items() if k.endswith("_call"))
            texts_clicks      = sum(v for k, v in buckets.items() if k.endswith("_text"))
            primary_cta       = buckets.get("primary_cta", 0)

            open_pct  = round(uniq_opens  / recipients * 100, 2) if recipients else 0
            click_pct = round(uniq_clicks / recipients * 100, 2) if recipients else 0
            unsub_pct = round(unsubs      / recipients * 100, 2) if recipients else 0
            clicks_per_1k   = round(uniq_clicks / recipients * 1000, 2) if recipients else 0
            calls_texts_1k  = round((calls_clicks + texts_clicks) / recipients * 1000, 2) if recipients else 0

            cat, theme = classify_name(c.get("name") or "")

            # Notes: preserve any human note, manage [tags] in-place
            prior_notes = existing_by_id.get(str(cid), {}).get("notes", "")
            new_tags = []
            if unlabeled_share >= UNLABELED_TAG_THRESHOLD:
                new_tags.append("no_utm")
            notes = merge_notes(prior_notes, *new_tags)

            row = {
                "campaign_id": cid,
                "send_date":   to_sheets_serial(sd),
                "send_dow":    dow(sd),
                "send_time":   sd.strftime("%H:%M"),
                "campaign_name": c.get("name",""),
                "category":    cat,
                "theme":       theme,
                "recipients":  recipients,
                "opens":       uniq_opens,
                "open_pct":    open_pct,
                "clicks":      uniq_clicks,
                "click_pct":   click_pct,
                "unsubs":      unsubs,
                "unsub_pct":   unsub_pct,
                "clicks_per_1k": clicks_per_1k,
                "calls_clicks": calls_clicks,
                "texts_clicks": texts_clicks,
                "directions_clicks": directions_clicks,
                "primary_cta_clicks": primary_cta,
                "calls_texts_per_1k": calls_texts_1k,
                "last_synced_at": NOW_ISO,
                "notes":        notes,
            }
            rows_to_write.append(row)
            out["steps"].append(
                f"  {tag} {cid} unlabeled={unlabeled}/{total_bucketed} "
                f"buckets={dict(sorted(buckets.items()))}"
            )
        except Exception as e:
            out["errors"].append(f"campaign {cid}: {e}")

    # ----- upsert -----
    result = {"updated": 0, "appended": 0}
    if rows_to_write:
        result = s.upsert_by_key(SHEET_ID, TAB, "campaign_id", rows_to_write)
    out["upsert_result"] = result
    out["steps"].append(f"upsert updated={result['updated']} appended={result['appended']}")

    # ----- refresh and compute trends -----
    refreshed_rows = s.read(SHEET_ID, f"{TAB}!A:Z")
    rhdr = refreshed_rows[0]
    rdicts = [
        {rhdr[i]: (r[i] if i < len(r) else "") for i in range(len(rhdr))}
        for r in refreshed_rows[1:]
    ]

    def coerce(d):
        try:    d["send_date_serial"] = int(float(d["send_date"]))
        except: d["send_date_serial"] = -1
        for k in ["recipients","opens","clicks","unsubs","directions_clicks",
                  "calls_clicks","texts_clicks","primary_cta_clicks"]:
            try: d[k] = int(float(d[k] or 0))
            except: d[k] = 0
        for k in ["open_pct","click_pct","unsub_pct","clicks_per_1k","calls_texts_per_1k"]:
            try: d[k] = float(d[k] or 0)
            except: d[k] = 0.0
        return d

    rdicts = [coerce(d) for d in rdicts]
    rdicts.sort(key=lambda d: d["send_date_serial"], reverse=True)

    if not rdicts:
        out["errors"].append("no rows in sheet after upsert")
        print(json.dumps(out, indent=2, default=str)); return

    def directions_per_1k(d):
        return (d["directions_clicks"] / d["recipients"] * 1000) if d["recipients"] else 0.0
    def primary_cta_pct(d):
        return (d["primary_cta_clicks"] / d["recipients"] * 100) if d["recipients"] else 0.0

    this_week = rdicts[0]
    prev_4 = rdicts[1:5]

    # Median (not mean) for the trailing window
    def median(xs):
        xs = [x for x in xs if x is not None]
        return float(statistics.median(xs)) if xs else 0.0
    def maxv(xs):
        xs = [x for x in xs if x is not None]
        return float(max(xs)) if xs else 0.0

    metrics_def = [
        ("directions_per_1k", True,  directions_per_1k),
        ("primary_cta_pct",   True,  primary_cta_pct),
        ("unsub_pct",         False, lambda d: d["unsub_pct"]),
        ("open_pct",          True,  lambda d: d["open_pct"]),
        ("clicks_per_1k",     True,  lambda d: d["clicks_per_1k"]),
    ]

    tw = {}
    trailing_median = {}
    trailing_max = {}
    outlier_flag = {}
    for key, _hb, fn in metrics_def:
        tw[key] = fn(this_week)
        vals = [fn(d) for d in prev_4]
        trailing_median[key] = median(vals)
        trailing_max[key] = maxv(vals)
        # outlier if max > 3x median and median > 0
        outlier_flag[key] = (
            trailing_median[key] > 0 and
            trailing_max[key] > 3 * trailing_median[key]
        )

    def delta_pct(now, baseline):
        if baseline == 0: return None
        return (now - baseline) / baseline * 100

    deltas_pct = {k: delta_pct(tw[k], trailing_median[k]) for k in tw}

    # Absolute click counts for volume floor
    tw_abs_clicks = {
        "directions_per_1k":  this_week["directions_clicks"],
        "primary_cta_pct":    this_week["primary_cta_clicks"],
        "clicks_per_1k":      this_week["clicks"],
        "unsub_pct":          this_week["unsubs"],
        "open_pct":           this_week["opens"],
    }
    baseline_clicks = {
        "directions_per_1k": median([d["directions_clicks"] for d in prev_4]),
        "primary_cta_pct":   median([d["primary_cta_clicks"] for d in prev_4]),
        "clicks_per_1k":     median([d["clicks"] for d in prev_4]),
        "unsub_pct":         median([d["unsubs"] for d in prev_4]),
        "open_pct":          median([d["opens"] for d in prev_4]),
    }

    # ----- lead-movement picker with volume floor -----
    # Rank candidates by |delta_pct|, then drop those that fail BOTH volume gates
    candidates_lead = []
    for key, higher_better, _fn in metrics_def:
        d = deltas_pct.get(key)
        if d is None:
            continue
        abs_delta_clicks = abs(tw_abs_clicks[key] - baseline_clicks[key])
        baseline_value = trailing_median[key]
        passes_volume = (
            abs_delta_clicks >= MIN_ABS_DELTA_CLICKS
            or baseline_value >= MIN_BASELINE_PCT
        )
        favorable = (d > 0) if higher_better else (d < 0)
        candidates_lead.append({
            "metric": key,
            "delta_pct": d,
            "magnitude": abs(d),
            "favorable": favorable,
            "higher_better": higher_better,
            "passes_volume": passes_volume,
            "abs_delta_clicks": abs_delta_clicks,
            "outlier_baseline": outlier_flag[key],
            "this_week_value": tw[key],
            "median_baseline": trailing_median[key],
            "max_baseline":   trailing_max[key],
        })
    # Lead = biggest magnitude that passes volume floor; fall back to biggest overall
    passing = [c for c in candidates_lead if c["passes_volume"]]
    passing.sort(key=lambda c: c["magnitude"], reverse=True)
    if passing:
        lead = passing[0]
    else:
        candidates_lead.sort(key=lambda c: c["magnitude"], reverse=True)
        lead = candidates_lead[0] if candidates_lead else None

    summary = {
        "this_week_campaign": this_week.get("campaign_name",""),
        "this_week_id":       this_week.get("campaign_id"),
        "send_date":          serial_to_iso(this_week.get("send_date", "")),
        "this_week_row":      this_week,
        "tw": tw,
        "trailing_median":    trailing_median,
        "trailing_max":       trailing_max,
        "outlier_flag":       outlier_flag,
        "deltas_pct":         deltas_pct,
        "lead":               lead,
        "lead_candidates":    candidates_lead,
        "rdicts_count":       len(rdicts),
        "recent_5": [
            {"id": d["campaign_id"], "name": d.get("campaign_name",""),
             "send_date": serial_to_iso(d.get("send_date","")),
             "category": d.get("category",""), "theme": d.get("theme",""),
             "recipients": d["recipients"],
             "open_pct": d["open_pct"], "click_pct": d["click_pct"],
             "unsub_pct": d["unsub_pct"],
             "directions_clicks": d["directions_clicks"],
             "primary_cta_clicks": d["primary_cta_clicks"],
             "directions_per_1k": round(directions_per_1k(d), 2),
             "primary_cta_pct":  round(primary_cta_pct(d), 2),
             "notes": d.get("notes","")}
            for d in rdicts[:5]
        ],
    }
    out["summary"] = summary
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
