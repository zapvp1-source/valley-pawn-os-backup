#!/usr/bin/env python3
"""
scrap_rankings.py — canonical gold-scrap history + monthly ranking report.

WHY THIS EXISTS (2026-08-04):
  The scrap-refining-gold CSVs carry a "Month" column that is the QUERY WINDOW,
  not the month the bucket belongs to. 43 of 178 buckets appear under 2-3
  different query months, so summing rows by that column double-counts badly
  (it inflated a 2025 total to 6,773 DWT when the true unique-bucket figure is
  materially different). NEVER sum the Month column.

  Canonical key = (Store, BucketName). Month is resolved in this order:
    1. CreatedOn timestamp  (authoritative; present on newer pulls)
    2. Year+month parsed out of the bucket name ("AUGUST 2025 GOLD", "GOLD 8/25")
    3. Month from the name + year from the earliest source file containing it

Usage:
  python3 scrap_rankings.py build                 # rebuild scrap_history.csv
  python3 scrap_rankings.py validate              # accuracy of name-parse vs CreatedOn
  python3 scrap_rankings.py report 2026-07        # ranking + YoY + YTD for a month
"""
import csv, glob, os, re, sys, json
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output")
HISTORY = os.path.join(OUT, "scrap_history.csv")
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
STORE_NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington",
               "ROA": "Roanoke", "WAY": "Waynesboro"}

MONTHS = {"JANUARY": 1, "JAN": 1, "FEBRUARY": 2, "FEB": 2, "MARCH": 3, "MAR": 3,
          "APRIL": 4, "APR": 4, "MAY": 5, "JUNE": 6, "JUN": 6, "JULY": 7, "JUL": 7,
          "AUGUST": 8, "AUG": 8, "SEPTEMBER": 9, "SEPT": 9, "SEP": 9,
          "OCTOBER": 10, "OCT": 10, "NOVEMBER": 11, "NOV": 11,
          "DECEMBER": 12, "DEC": 12}


def parse_created(s):
    """'6/30/2026 2:15:36 PM -04:00' -> (2026, 6)"""
    m = re.match(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return (int(m.group(3)), int(m.group(1))) if m else None


def parse_name(name):
    """Month/year from a bucket name. Returns (year, month) | (None, month) | None."""
    n = name.upper()
    # explicit numeric date: 6/4/26, 4/28/25, 8/25, 12/25
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", n)
    if m:
        y = int(m.group(3))
        return (2000 + y if y < 100 else y, int(m.group(1)))
    m = re.search(r"\b(\d{1,2})/(\d{2})\b", n)
    if m and 1 <= int(m.group(1)) <= 12:
        return (2000 + int(m.group(2)), int(m.group(1)))
    # month word, optional 4-digit year anywhere in the name
    mon = None
    for word, num in sorted(MONTHS.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + word + r"\b", n):
            mon = num
            break
    if mon is None:
        return None
    y = re.search(r"\b(20\d{2})\b", n)
    return (int(y.group(1)), mon) if y else (None, mon)


def load_raw():
    """(store, bucket, source_file_year) -> dict(created, posted, status, weight, file_years)

    KEYED BY SOURCE FILE YEAR, NOT JUST (store, bucket) -- some stores (confirmed:
    Harrisonburg) reuse bucket names across calendar years with no year in the
    name ("FEBRUARY GOLD W/ STONES" exists in both the 2025 and 2026 raw files).
    Keying by (store, bucket) alone silently merges those two distinct buckets
    into one record -- a blank/unverified weight in one year's file gets
    silently backfilled from the OTHER year's same-named bucket, reproducing
    the exact fabricated-duplicate bug this file was written to catch (2026-08-04
    entry #6), just at the aggregation layer instead of the pull layer. The
    source filename's year prefix ("2025_HAR...", "2026_HAR...") is a reliable,
    already-present signal for which real-world year a row belongs to, so it's
    folded into the key.
    """
    rows = {}
    for f in sorted(glob.glob(os.path.join(OUT, "*scrap-refining-gold*.csv"))):
        if "diagnostic" in f:
            continue
        fy = re.match(r"(\d{4})_", os.path.basename(f))
        fy = int(fy.group(1)) if fy else None
        try:
            data = list(csv.reader(open(f, newline="", encoding="utf-8-sig")))
        except Exception:
            continue
        for r in data:
            if len(r) < 4 or r[0] == "Store" or r[0] not in STORES:
                continue
            bucket = r[2].strip()
            if not bucket or bucket == "NO BUCKET FOUND":
                continue
            created = r[3] if len(r) >= 7 else ""
            status = r[4] if len(r) >= 7 else ""
            posted = r[5] if len(r) >= 7 else ""
            w = r[-1].strip()
            k = (r[0], bucket, fy)
            e = rows.setdefault(k, {"created": "", "posted": "", "status": "",
                                    "weight": "", "file_years": set()})
            if fy:
                e["file_years"].add(fy)
            if created and not e["created"]:
                e["created"] = created
            if posted and not e["posted"]:
                e["posted"] = posted
            if status and not e["status"]:
                e["status"] = status
            if w and not e["weight"]:
                e["weight"] = w
    return rows


def resolve_month(bucket, e):
    """-> (year, month, source) or None

    PERIOD = the month the bucket was POSTED (closed / sent to the refiner).

    Confirmed with Joshua 2026-08-04: buckets are posted the month AFTER the
    gold is collected. Validated in the data -- 72 of 85 year-bearing bucket
    names sit exactly one month before their posted date. So:
        posted month  = reporting period
        collection month = posted month - 1
    Reporting on the POSTED month is what makes a 1st-of-month post possible:
    last month's buckets are all closed by then (stores close between the 13th
    and the 20th), whereas last month's COLLECTION has not been posted yet.

    OPEN buckets are excluded -- still collecting, nothing sent out yet.

    Bucket NAMES are deliberately NOT used as the period. Validated 2026-08-04
    against 119 buckets that carry both: 76 had name == created month, 34 had
    created = name + 1 (named for the gold's month, closed the next month), and
    9 ran the other way -- Waynesboro in 2026 names buckets for the month AHEAD
    ('JULY 26 GOLD SCRAP' created in June). That is three different naming
    conventions across stores and years, so a name is a managerial label, not a
    date. CreatedOn is the only consistent machine-readable period key.

    A name-derived month is emitted ONLY as a flagged low-confidence fallback so
    the gap is visible rather than silently wrong.
    """
    if (e.get("status") or "").upper() == "OPEN":
        return None  # still collecting; not yet sent out
    p = parse_created(e.get("posted", ""))
    if p:
        return p[0], p[1], "posted"
    c = parse_created(e["created"])
    if c:
        return c[0], c[1], "LOW-CONF-created"
    n = parse_name(bucket)
    if n:
        y, mo = n
        # name = collection month; posting is the month after
        if y:
            return (y + 1, 1, "LOW-CONF-name") if mo == 12 else (y, mo + 1, "LOW-CONF-name")
        if e["file_years"]:
            fy = min(e["file_years"])
            return (fy + 1, 1, "LOW-CONF-name+file") if mo == 12 else (fy, mo + 1, "LOW-CONF-name+file")
    return None


def build():
    raw = load_raw()
    out, unresolved = [], []
    for (st, bucket, _fy), e in sorted(raw.items()):
        r = resolve_month(bucket, e)
        if not r:
            unresolved.append((st, bucket))
            continue
        y, mo, src = r
        out.append({"store": st, "year": y, "month": mo, "period": f"{y}-{mo:02d}",
                    "bucket": bucket, "dwt": e["weight"], "date_source": src})
    with open(HISTORY, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["store", "period", "year", "month",
                                           "bucket", "dwt", "date_source"])
        w.writeheader()
        for r in sorted(out, key=lambda x: (x["store"], x["period"], x["bucket"])):
            w.writerow({k: r[k] for k in w.fieldnames})
    missing = [r for r in out if not r["dwt"]]
    print(f"wrote {HISTORY}")
    print(f"  buckets: {len(out)} | unresolved month: {len(unresolved)} | missing weight: {len(missing)}")
    src = defaultdict(int)
    for r in out:
        src[r["date_source"]] += 1
    print(f"  date source: {dict(src)}")
    if missing:
        print("  buckets needing a weight re-pull:")
        for r in missing[:20]:
            print(f"    {r['store']} {r['period']} {r['bucket']}")
    for st, b in unresolved:
        print(f"  UNRESOLVED: {st} {b}")


def validate():
    """Accuracy of the name-parse fallback, measured only where CreatedOn exists."""
    raw = load_raw()
    ok = bad = nomatch = 0
    misses = []
    for (st, bucket, _fy), e in raw.items():
        c = parse_created(e["created"])
        if not c:
            continue
        p = parse_name(bucket)
        if not p:
            nomatch += 1
            misses.append((st, bucket, c, None))
            continue
        y, mo = p
        y = y or (min(e["file_years"]) if e["file_years"] else None)
        if (y, mo) == c:
            ok += 1
        else:
            bad += 1
            misses.append((st, bucket, c, (y, mo)))
    tot = ok + bad + nomatch
    print(f"name-parse validated against CreatedOn on {tot} buckets")
    print(f"  exact match: {ok} ({ok/tot*100:.0f}%) | wrong: {bad} | unparseable: {nomatch}")
    for m in misses[:15]:
        print(f"    {m[0]} {m[1]!r} created={m[2]} name={m[3]}")


def load_history():
    per = defaultdict(lambda: defaultdict(float))
    if not os.path.exists(HISTORY):
        build()
    for r in csv.DictReader(open(HISTORY)):
        if r["dwt"]:
            per[r["period"]][r["store"]] += float(r["dwt"])
    return per


def genesis_period(per):
    """Earliest period with ANY data, across all stores. Every store's tracking
    starts at the same real-world boundary (the source system has nothing
    before it) -- checking coverage back past this point would flag every
    store as 'incomplete' forever, which is a false positive, not a data gap."""
    return min(per.keys()) if per else None


def year_covered(per, store, year, upto_month):
    """True only if `store` has a posted bucket in EVERY month from the data's
    genesis period through `upto_month` of `year` (whichever is later). Every
    active store posts roughly monthly, so any gap in that run means
    missing/unpulled data, not a real zero month. Company-wide YoY/YTD
    comparisons must never quietly average in a store's data hole -- that
    silently overstates growth (the store contributes ~0 to the prior-year
    denominator instead of its real, unknown total)."""
    gp = genesis_period(per)
    gy, gm = (int(gp[:4]), int(gp[5:7])) if gp else (year, 1)
    start_month = gm if gy == year else (1 if gy < year else upto_month + 1)
    return all(store in per.get(f"{year}-{mo:02d}", {}) for mo in range(start_month, upto_month + 1))


def report(period):
    per = load_history()
    y, m = int(period[:4]), int(period[5:7])
    prior = f"{y-1}-{m:02d}"
    cur, pri = per.get(period, {}), per.get(prior, {})
    ytd, ytd_prior = defaultdict(float), defaultdict(float)
    for p, d in per.items():
        py, pm = int(p[:4]), int(p[5:7])
        if pm <= m:
            if py == y:
                for s, v in d.items():
                    ytd[s] += v
            elif py == y - 1:
                for s, v in d.items():
                    ytd_prior[s] += v
    rank = sorted(STORES, key=lambda s: -cur.get(s, 0))

    # Data-completeness gate: company-wide YoY/YTD comparisons are only valid
    # if EVERY store has full prior-year coverage. A store missing months from
    # the prior year contributes an understated (not zero) total, which would
    # inflate the company-wide "% up from last year" figure. Per-store lines
    # are unaffected -- pct() already omits a line when that one store's own
    # prior value is missing.
    incomplete = [s for s in STORES if not year_covered(per, s, y - 1, m)]

    return {"period": period, "prior": prior, "rank": rank, "cur": dict(cur),
            "pri": dict(pri), "ytd": dict(ytd), "ytd_prior": dict(ytd_prior),
            "total": sum(cur.values()), "total_prior": sum(pri.values()),
            "ytd_total": sum(ytd.values()), "ytd_prior_total": sum(ytd_prior.values()),
            "incomplete_prior_stores": incomplete}


def pct(now, then):
    if not then:
        return None
    return (now - then) / then * 100


def slack_post(r):
    """Field-facing text — Field Communication Standard v3."""
    mname = ["", "January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"][int(r["period"][5:7])]
    incomplete = r.get("incomplete_prior_stores") or []
    L = []
    lead = f"*{mname} gold scrap — {r['total']:,.0f} dwt company-wide.*"
    if not incomplete:
        c = pct(r["total"], r["total_prior"])
        if c is not None:
            lead += f" That's {abs(c):.0f}% {'up from' if c >= 0 else 'down from'} {mname} last year."
    L.append(lead)
    L.append("")
    for i, s in enumerate(r["rank"], 1):
        v = r["cur"].get(s, 0)
        if not v:
            continue
        medal = {1: ":first_place_medal:", 2: ":second_place_medal:", 3: ":third_place_medal:"}.get(i, "  ")
        yo = None if s in incomplete else pct(v, r["pri"].get(s, 0))
        yos = f"  ({'+' if yo >= 0 else ''}{yo:.0f}% vs last year)" if yo is not None else ""
        L.append(f"{medal} *{STORE_NAMES[s]}* — {v:,.0f} dwt{yos}")
    L.append("")

    # Year-to-date board. Joshua asked 2026-08-04 for BOTH boards in the
    # monthly post -- the month ranking alone hides who is actually winning
    # the year, which is the number that drives the bonus conversation.
    ytdline = f"*Year to date — {r['ytd_total']:,.0f} dwt"
    if not incomplete:
        yc = pct(r["ytd_total"], r["ytd_prior_total"])
        if yc is not None:
            ytdline += f", {'up' if yc >= 0 else 'down'} {abs(yc):.0f}% over the same stretch last year"
    ytdline += ".*"
    L.append(ytdline)
    L.append("")
    ytd_rank = sorted(STORES, key=lambda s: -r["ytd"].get(s, 0))
    for i, s in enumerate(ytd_rank, 1):
        v = r["ytd"].get(s, 0)
        if not v:
            continue
        medal = {1: ":first_place_medal:", 2: ":second_place_medal:", 3: ":third_place_medal:"}.get(i, "")
        yo = None if s in incomplete else pct(v, r["ytd_prior"].get(s, 0))
        yos = f" ({'+' if yo >= 0 else '−'}{abs(yo):.0f}% vs last year)" if yo is not None else ""
        L.append(f"{medal} *{STORE_NAMES[s]}* — {v:,.0f} dwt{yos}".strip())
    if incomplete:
        names = ", ".join(STORE_NAMES[s] for s in incomplete)
        L.append("")
        L.append(f"(Year-over-year comparison is on hold company-wide until {names}'s history is fully backfilled — showing this year's numbers only for now.)")
    L.append("")
    top, ytd_top = r["rank"][0], ytd_rank[0]
    if top == ytd_top:
        L.append(f"Nice work {STORE_NAMES[top]} — top of both boards.")
    else:
        L.append(f"Nice work {STORE_NAMES[top]} — top of the board this month. {STORE_NAMES[ytd_top]} still leads the year.")
    return "\n".join(L)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "validate":
        validate()
    elif cmd == "report":
        r = report(sys.argv[2])
        print(json.dumps(r, indent=1, default=str))
        print("\n----- SLACK POST -----")
        print(slack_post(r))
    else:
        print(__doc__)
