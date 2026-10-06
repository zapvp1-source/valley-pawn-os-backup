#!/usr/bin/env python3
"""markdown_verification.py — native weekly aged-inventory markdown verification (2026-10-05).

Native counterpart of the Cowork pair `weekly-markdown-verification-pull` (Sun 19:00) and
`weekly-markdown-verification-review` (Mon 09:35). Same trigger, same math, same post.

  markdown_verification.py pull   [--render]
      Drops the 5-store markdown-verification trigger, writes logs/_last_markdown_verification_trigger.txt,
      DMs Joshua "Markdown-verification pull dispatched — <date>." (the Fleet Guardian marker). Does not poll.
  markdown_verification.py review [--render] [--date YYYY-MM-DD] [--today YYYY-MM-DD] [--no-retry]
      Reads the newest per-store markdown-verification CSVs, re-pulls any store that is missing/errored
      (one retry trigger, polls up to 20 min), computes aged-1yr+ items with no sale price, split
      Jewelry / General merch (SKILL classifier verbatim), posts to #items-to-markdown, DMs Joshua the
      trend line, appends the history CSV. All 5 stores or nothing: a missing store = withhold + one
      FAILURE_LEDGER row (Joshua's all-or-nothing rule; the data-first override in the SKILL).
  --render prints what would be posted and writes nothing (no trigger, no post, no history row).
"""
import csv, datetime as dt, glob, json, os, re, sys, time
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

ET = ZoneInfo("America/New_York")
BRAVO = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
OUT, TRIG, RES, LOGS = (os.path.join(BRAVO, d) for d in ("output", "triggers", "results", "logs"))
MARKER = os.path.join(LOGS, "_last_markdown_verification_trigger.txt")
HIST = os.path.join(LOGS, "_markdown_verification_history.csv")
LEDGER = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
CHANNEL = "C0BQX7CF13J"          # #items-to-markdown
JOSHUA = "U03BB52MDSA"
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
JEWEL = ["gold", "silver", "platinum", "diamond", "gent's", "lady's", "unisex", "wristwatch", "pocket watch",
         "necklace", "pendant", "bracelet", "earring", "brooch", "charm", "ring", "chain"]
FORCE_GEN = ["smart watch", "fashion accessory", "men's accessory", "accessories"]


def now():
    return dt.datetime.now(ET)


def ledger(task, sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (now().strftime("%Y-%m-%d %H:%M ET"), task, sentence))


def drop_trigger(tid, stores, date):
    body = {"id": tid, "requested_at": now().strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + now().strftime("%z")[-2:],
            "reports": [{"name": "markdown-verification", "stores": stores, "date": date}]}
    tmp = os.path.join(TRIG, "." + tid + ".tmp")
    with open(tmp, "w") as f:
        json.dump(body, f, indent=2)
    os.rename(tmp, os.path.join(TRIG, tid + ".json"))


def money(s):
    s = (s or "").replace("$", "").replace(",", "").strip()
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def is_jewelry(cat):
    c = (cat or "").lower()
    if any(k in c for k in FORCE_GEN):
        return False
    if re.fullmatch(r"\s*coins?\s*", c):
        return False
    return any(k in c for k in JEWEL)


def newest_csv(code, date=None):
    fs = glob.glob(os.path.join(OUT, "%s*_%s_markdown-verification.csv" % (date or "", code)))
    if not fs:
        return None
    # name = <date>_to_<date>_<STORE>_markdown-verification.csv — newest by data date, then mtime
    return max(fs, key=lambda p: (os.path.basename(p)[:10], os.path.getmtime(p)))


def compute(path, today):
    r = dict(n=0, d=0.0, jn=0, jd=0.0, gn=0, gd=0.0)
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.DictReader(f):
            if (row.get("Status") or "").strip().upper() != "INVENTORY":
                continue
            try:
                d = dt.datetime.strptime((row.get("Date") or "").strip(), "%m/%d/%Y").date()
            except ValueError:
                continue
            if (today - d).days < 365:
                continue
            if money(row.get("Sale Price")) != 0.0:
                continue
            p = money(row.get("Price"))
            r["n"] += 1; r["d"] += p
            if is_jewelry(row.get("Category")):
                r["jn"] += 1; r["jd"] += p
            else:
                r["gn"] += 1; r["gd"] += p
    return r


def usd(x):
    return "${:,.0f}".format(x)


def fmt_date(d):
    return d.strftime("%b ") + str(d.day)


def build_post(data_date, per):
    tot = {k: sum(per[c][k] for c, _ in STORES) for k in ("n", "d", "jn", "jd", "gn", "gd")}
    lines = [":label: Markdown check — %s" % fmt_date(data_date),
             "%d items sitting over a year still haven't been marked down — %s worth." % (tot["n"], usd(tot["d"])),
             "", "Jewelry: %d items, %s" % (tot["jn"], usd(tot["jd"])),
             "General merch: %d items, %s" % (tot["gn"], usd(tot["gd"])), "", "By store:"]
    for c, name in STORES:
        lines.append("• %s: %d (%s)" % (name, per[c]["n"], usd(per[c]["d"])))
    # Optional driver line — SKILL: only when one store is clearly disproportionate. Made mechanical:
    # a single store carrying >= 45% of the company dollars. (10/4: biggest share 36.5% -> omitted, as posted.)
    if tot["d"] > 0:
        c, name = max(STORES, key=lambda s: per[s[0]]["d"])
        share = per[c]["d"] / tot["d"]
        if share >= 0.45:
            lines.append("%s alone is about %d%% of the total — worth a look first." % (name, round(share * 100)))
    return "\n".join(lines), tot


def prior_totals(before):
    if not os.path.exists(HIST):
        return None
    rows = list(csv.reader(open(HIST)))
    dates = sorted({r[0] for r in rows if r and r[0][:2] == "20" and r[0] < before})
    if not dates:
        return None
    last = dates[-1]
    rr = [r for r in rows if r and r[0] == last]
    if len(rr) < 5:
        return None
    f = lambda i: sum(float(r[i]) for r in rr)
    return last, int(f(2)), f(3), f(5), f(7)


def build_dm(data_date, tot):
    pr = prior_totals(data_date.isoformat())
    was = ("was %d items / %s last week (jewelry %s / general merch %s)" % (pr[1], usd(pr[2]),
           usd(pr[3]), usd(pr[4]))) if pr else "first run with the jewelry split, no prior week to compare yet"
    return ("Markdown check %s: company-wide %d items / %s still not marked down (jewelry %s / general merch %s) — %s. "
            "Note: the report doesn't currently record WHEN an item was last marked down, only whether it currently has a "
            "reduced price — so this can't yet show whether markdowns are actively continuing vs. static. Ask Preston "
            "whether a last-price-change date can be added to the report if you want that."
            % (fmt_date(data_date), tot["n"], usd(tot["d"]), usd(tot["jd"]), usd(tot["gd"]), was))


def store_status(date=None):
    """Per store: (path, data_date) or None; plus set of stores the latest result JSON says failed."""
    failed = set()
    try:
        tid = open(MARKER).read().strip()
        res = json.load(open(os.path.join(RES, tid + ".result.json"), encoding="utf-8-sig"))
        failed = {c["store"] for c in res.get("cells", []) if c.get("status") != "success"}
    except Exception:
        pass
    out = {}
    for c, _ in STORES:
        p = newest_csv(c, date)
        out[c] = (p, dt.date.fromisoformat(os.path.basename(p)[:10])) if p else None
    return out, failed


def review(render, want_date, today, retry):
    task = "weekly-markdown-verification-review"
    st, failed = store_status(want_date)
    newest = max((v[1] for v in st.values() if v), default=None)
    target = dt.date.fromisoformat(want_date) if want_date else newest
    if target is None:
        if not render:
            ledger(task, "Weekly markdown check did not post: no markdown-verification data on disk for any store.")
        print("WITHHELD: no data"); return 2
    # data older than 8 days = the Sunday pull did not run this week
    if not want_date and (today - target).days > 8:
        target = None
    missing = [c for c, _ in STORES if not st[c] or (target and st[c][1] != target) or (c in failed and not want_date)]
    if missing and retry and not render:
        tid = "markdown-verification-retry-" + dt.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        drop_trigger(tid, missing, today.isoformat())
        print("retry trigger", tid, missing)
        t0 = time.time()
        while time.time() - t0 < 20 * 60 and not os.path.exists(os.path.join(RES, tid + ".result.json")):
            time.sleep(15)
        time.sleep(5)
        st, _ = store_status()
        target = max((v[1] for v in st.values() if v), default=None)
        missing = [c for c, _ in STORES if not st[c] or st[c][1] != target]
    if missing or target is None:
        names = ", ".join(n for c, n in STORES if c in missing) or "all stores"
        if not render:
            ledger(task, "Weekly markdown check withheld: no current markdown data for %s after one re-pull." % names)
        print("WITHHELD: missing", names); return 2
    per = {c: compute(st[c][0], today) for c, _ in STORES}
    post, tot = build_post(target, per)
    dm = build_dm(target, tot)
    header = post.splitlines()[0]
    if render:
        print("=== #items-to-markdown (%s) ===\n%s\n\n=== DM Joshua ===\n%s" % (CHANNEL, post, dm))
        for c, n in STORES:
            print("%s files: %s" % (c, os.path.basename(st[c][0])))
        return 0
    if vp_slack.has(CHANNEL, header, 30):
        print("DUPLICATE: already posted", header); return 4
    vp_slack.post(CHANNEL, post)
    vp_slack.post(vp_slack.dm_channel(JOSHUA), dm)
    with open(HIST, "a") as f:
        for c, _ in STORES:
            p = per[c]
            f.write("%s,%s,%d,%.2f,%d,%.2f,%d,%.2f\n" % (target.isoformat(), c, p["n"], p["d"], p["jn"], p["jd"], p["gn"], p["gd"]))
    print("posted", header); return 0


def pull(render):
    n = now()
    tid = "markdown-verification-" + dt.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    msg = "Markdown-verification pull dispatched — %s." % n.date().isoformat()
    if render:
        print("would drop trigger %s (5 stores, date %s)\nwould DM Joshua: %s" % (tid, n.date().isoformat(), msg)); return 0
    try:
        drop_trigger(tid, [c for c, _ in STORES], n.date().isoformat())
        open(MARKER, "w").write(tid + "\n")
    except Exception as e:
        open(MARKER, "w").write("ERROR: %s\n" % e)
        msg = "Markdown-verification pull dispatched — %s — FAILED to write trigger, see log." % n.date().isoformat()
    vp_slack.post(vp_slack.dm_channel(JOSHUA), msg)
    print(tid); return 0


def main():
    a = sys.argv[1:]
    render = "--render" in a
    val = lambda k: a[a.index(k) + 1] if k in a else None
    if a and a[0] == "pull":
        os.environ.setdefault("VP_TASK", "weekly-markdown-verification-pull")
        sys.exit(pull(render))
    if a and a[0] == "review":
        os.environ.setdefault("VP_TASK", "weekly-markdown-verification-review")
        today = dt.date.fromisoformat(val("--today")) if val("--today") else now().date()
        sys.exit(review(render, val("--date"), today, "--no-retry" not in a))
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
