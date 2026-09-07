#!/usr/bin/env python3
"""
Valley Pawn Comms Engine — deterministic render + post layer for team-facing Slack publications.

WHY THIS EXISTS (2026-09-06, Communications Dept review):
  Team-facing Slack posts were re-rendered as free text by the model on every run. Verified
  drift in the channels: dropped header/TOTAL rows, unbalanced code fences, a denominator printed
  in a total column, "4 of 5 stores" partial tables, "pipeline cell failed" notes and system
  names in team channels, item counts silently capped at the 22 rows a grid renders, double
  "Sent using Claude" footers, and every post appearing under Joshua's own account. The
  2026-09-05 aged-inventory formatter proved the fix; this file generalises it and adds the
  sender-identity + dedupe pieces.

CONTRACT (same as format_aged_inventory.py, extended):
  render  -> stdout = exact Slack body, nothing else.  exit 0 = post it verbatim.
             exit 2 = WITHHOLD (stdout empty, reasons on stderr — run record / Joshua DM only).
             exit 1 = usage / unexpected error. Post nothing.
  check   -> exit 0 = no post with this publication's marker today; exit 4 = already posted.
  post    -> renders, dedupes, posts via the VP OPS ENGINE bot (Keychain token).
             exit 0 = posted by the bot.
             exit 3 = could not post as the bot (no token / bot not in channel) — stdout carries
                      the validated body; the calling task must post it VERBATIM via the Slack
                      connector instead. Nothing is lost, only the sender identity.
             exit 4 = duplicate (already in channel today) — nothing posted, stdout empty.
             exit 2 / 1 as above.
  results-json -> writes loan-layaway-results-latest.json for weekly-loan-layaway-manager-dms.

  Never post anything this script did not print. Never "clean up" its output.

Python 3.9 compatible (macOS /usr/bin/python3). stdlib + openpyxl (present on the Mac Studio).
"""

import argparse
import csv
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request

STORES = [
    ("CUL", "Culpeper"),
    ("HAR", "Harrisonburg"),
    ("LEX", "Lexington"),
    ("ROA", "Roanoke"),
    ("WAY", "Waynesboro"),
]
CODE_TO_NAME = dict(STORES)

DEFAULT_OUTPUT_DIR = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"
FPD_ARCHIVE = "/Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv"
RESULTS_JSON = "/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json"
RUN_LOG_DIR = "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/comms-engine/runs"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"
MIN_FILE_BYTES = 40
GRID_ROW_CAP = 22          # rows a Bravo DevExpress grid renders on screen; counts at exactly
                           # this value at 2+ stores are a display cap, not a real count.
LOAN_POLICY_PCT = 5.0
EOM_MAX_AGE_DAYS = 8

# ---------------------------------------------------------------------------
# Publication registry — ONE owner, ONE channel, ONE marker per publication.
# ---------------------------------------------------------------------------
PUBS = {
    "loan-review": {
        "channel": "C0B08RS2BMK",
        "marker": "Weekly Past-Due Loan Review",
    },
    "layaway-review": {
        "channel": "C04N24STDP1",
        "marker": "Weekly Layaway Review",
    },
    "employee-performance": {
        "channel": "C0ATTLPQHR8",
        "marker": "MTD Employee Sales Rankings",
    },
    "first-payment-default": {
        "channel": "C0B17894S2Y",
        "marker": "Weekly First-Payment-Default Ranking",
    },
}

SHADOW_CHANNEL_NAME = "vp-ops-shadow"
SHADOW_CHANNEL_ID = "C0BLQSABGGY"   # private; conversations.list needs groups:read, which the
                                     # bot may not carry — use the id directly, verify by posting.


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def money(raw):
    if raw is None:
        return 0.0
    s = str(raw).strip().replace("$", "").replace(",", "").replace(" ", "")
    if s in ("", "-", "--"):
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]
    v = float(s)
    return -v if neg else v


def usd(v):
    return "$" + format(v, ",.2f")


def pretty_date(iso):
    try:
        return dt.datetime.strptime(iso, "%Y-%m-%d").strftime("%B %-d, %Y")
    except ValueError:
        return iso


def short_date(iso):
    d = dt.datetime.strptime(iso, "%Y-%m-%d")
    return "%d/%d" % (d.month, d.day)


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        return list(csv.reader(fh))


def store_file(output_dir, date, code, suffix):
    return os.path.join(output_dir, "%s_%s_%s.csv" % (date, code, suffix))


class Withhold(Exception):
    pass


def log_run(pub, lines):
    try:
        os.makedirs(RUN_LOG_DIR, exist_ok=True)
        with open(os.path.join(RUN_LOG_DIR, dt.date.today().isoformat() + ".log"), "a") as fh:
            stamp = dt.datetime.now().strftime("%H:%M:%S")
            for ln in lines:
                fh.write("%s %s: %s\n" % (stamp, pub, ln))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Loan balances (denominators) from the freshest complete 5-store EOM xlsx set
# ---------------------------------------------------------------------------
def load_loan_balances(output_dir, post_date):
    """Return (eom_date, {code: balance}) or (None, None). Never scrapes Slack, never hard-codes."""
    try:
        import openpyxl
    except ImportError:
        return None, None
    post = dt.datetime.strptime(post_date, "%Y-%m-%d").date()
    dates = set()
    for p in glob.glob(os.path.join(output_dir, "20??-??-??_*_end-of-month.xlsx")):
        dates.add(os.path.basename(p)[:10])
    for d in sorted(dates, reverse=True):
        try:
            dd = dt.datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            continue
        if (post - dd).days > EOM_MAX_AGE_DAYS or dd > post:
            continue
        bal = {}
        for code, _ in STORES:
            p = os.path.join(output_dir, "%s_%s_end-of-month.xlsx" % (d, code))
            if not os.path.exists(p) or os.path.getsize(p) < 5000:
                break
            try:
                wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
                ws = wb.active
                val = None
                for row in ws.iter_rows(values_only=True):
                    if row and row[0] is not None and str(row[0]).startswith("Ending Loan Base"):
                        nums = [c for c in row[1:] if isinstance(c, (int, float))]
                        if not nums:
                            nums = [money(c) for c in row[1:] if c is not None and re.match(r"^[\d,.$]+$", str(c))]
                        if nums:
                            val = float(nums[-1])
                wb.close()
                if val is None or val <= 0:
                    break
                bal[code] = val
            except Exception:
                break
        if len(bal) == 5:
            return d, bal
    return None, None


# ---------------------------------------------------------------------------
# LOAN REVIEW
# ---------------------------------------------------------------------------
def load_loans(output_dir, pipeline_date):
    data, problems = {}, []
    for code, name in STORES:
        p = store_file(output_dir, pipeline_date, code, "loans-75-days-past-due")
        if not os.path.exists(p):
            problems.append("%s: loans-75 CSV not found" % name)
            continue
        rows = [r for r in read_csv_rows(p) if r]
        if len(rows) < 2 or len(rows[1]) < 4:
            problems.append("%s: loans-75 CSV has no data row" % name)
            continue
        try:
            data[code] = {"count": int(float(rows[1][2])), "dollars": money(rows[1][3])}
        except Exception as exc:
            problems.append("%s: loans-75 parse error (%s)" % (name, exc))
    if problems:
        raise Withhold(problems)
    return data


def render_loan_review(output_dir, pipeline_date, post_date, notes):
    loans = load_loans(output_dir, pipeline_date)
    eom_date, balances = load_loan_balances(output_dir, post_date)

    capped = [c for c, _ in STORES if loans[c]["count"] == GRID_ROW_CAP]
    counts_reliable = len(capped) < 2
    if not counts_reliable:
        notes.append("loan item counts read exactly %d at %d stores — that is the on-screen grid row cap, "
                     "not a real count; counts omitted from the post (dollars come from the report "
                     "summary and are unaffected). Pipeline fix: use the loans75-gridread cell's row count."
                     % (GRID_ROW_CAP, len(capped)))

    total_d = sum(v["dollars"] for v in loans.values())
    total_n = sum(v["count"] for v in loans.values())

    lines = [":clipboard: *Weekly Past-Due Loan Review — %s*" % pretty_date(post_date), "",
             "*PAST DUE LOANS (75-day rule — cap %d%% of loan balance)*" % int(LOAN_POLICY_PCT)]
    over = []
    for code, name in STORES:
        d = loans[code]["dollars"]
        n = loans[code]["count"]
        if balances:
            pct = d / balances[code] * 100.0
            flag = ":white_check_mark:" if pct <= LOAN_POLICY_PCT else ":red_circle:"
            if pct > LOAN_POLICY_PCT:
                over.append((name, pct))
            pct_s = "%.2f%%" % pct
        else:
            flag, pct_s = "", "n/a"
        if counts_reliable:
            lines.append("• *%s* — %d items / %s / %s %s" % (code, n, usd(d), pct_s, flag))
        else:
            lines.append("• *%s* — %s / %s %s" % (code, usd(d), pct_s, flag))
    lines.append("")
    if balances:
        company_bal = sum(balances.values())
        cpct = total_d / company_bal * 100.0
        if counts_reliable:
            lines.append("*Total past 75d:* %d items / %s (%.2f%% of %s company loan balance)"
                         % (total_n, usd(total_d), cpct, usd(company_bal)))
        else:
            lines.append("*Total past 75d:* %s (%.2f%% of %s company loan balance)"
                         % (usd(total_d), cpct, usd(company_bal)))
        if over:
            for name, pct in over:
                lines.append(":red_circle: *%s* is %.2f%% past 75 days — out of the %d%% policy. Needs to be caught up."
                             % (name, pct, int(LOAN_POLICY_PCT)))
        else:
            lines.append("All 5 stores within the %d%% policy — no action items." % int(LOAN_POLICY_PCT))
        lines.append("_Loan balances as of %s._" % eom_date)
        age = (dt.datetime.strptime(post_date, "%Y-%m-%d") - dt.datetime.strptime(eom_date, "%Y-%m-%d")).days
        if age > EOM_MAX_AGE_DAYS:
            notes.append("loan balance is %d days old" % age)
    else:
        if counts_reliable:
            lines.append("*Total past 75d:* %d items / %s" % (total_n, usd(total_d)))
        else:
            lines.append("*Total past 75d:* %s" % usd(total_d))
        lines.append("%d%% policy check pending a current loan balance." % int(LOAN_POLICY_PCT))
        notes.append("no complete 5-store end-of-month set within %d days — percentages omitted" % EOM_MAX_AGE_DAYS)
    return "\n".join(lines), {"loans": loans, "balances": balances, "eom_date": eom_date}


# ---------------------------------------------------------------------------
# LAYAWAY REVIEW
# ---------------------------------------------------------------------------
LAY_COLS = ["overdue", "past_pmt_due", "contacted_no_activity", "no_pmt_30d", "locate"]


def load_layaways(output_dir, pipeline_date):
    data, problems = {}, []
    for code, name in STORES:
        p = store_file(output_dir, pipeline_date, code, "layaways")
        if not os.path.exists(p):
            problems.append("%s: layaways CSV not found" % name)
            continue
        rows = [r for r in read_csv_rows(p) if r]
        if len(rows) < 2:
            problems.append("%s: layaways CSV has no data row" % name)
            continue
        hdr = [h.strip() for h in rows[0]]
        try:
            rec = dict(zip(hdr, rows[1]))
            data[code] = dict((k, int(float(rec[k]))) for k in LAY_COLS)
        except Exception as exc:
            problems.append("%s: layaways parse error (%s)" % (name, exc))
    if problems:
        raise Withhold(problems)
    return data


def render_layaway_review(output_dir, pipeline_date, post_date, notes):
    lay = load_layaways(output_dir, pipeline_date)
    totals = dict((k, sum(lay[c][k] for c, _ in STORES)) for k in LAY_COLS)

    def cell(v, tot):
        pct = int(round(v / tot * 100.0)) if tot else 0
        return "%d (%d%%)" % (v, pct)

    W = [13, 10, 13, 17, 12, 7]
    hdr = ["Store", "Overdue", "Past Pmt Due", "Contacted/No Act", "30d-No-Pmt", "Locate"]
    rule = "".join("-" * (w - 1) + " " for w in W).rstrip()

    def row(cells):
        return " ".join(str(c).ljust(w) for c, w in zip(cells, W)).rstrip()

    tbl = [row(hdr), rule]
    for code, name in STORES:
        d = lay[code]
        tbl.append(row([name, cell(d["overdue"], totals["overdue"]),
                        cell(d["past_pmt_due"], totals["past_pmt_due"]),
                        cell(d["contacted_no_activity"], totals["contacted_no_activity"]),
                        cell(d["no_pmt_30d"], totals["no_pmt_30d"]), d["locate"]]))
    tbl.append(rule)
    loc_total = totals["locate"]
    tbl.append(row(["Company", totals["overdue"], totals["past_pmt_due"],
                    totals["contacted_no_activity"], totals["no_pmt_30d"],
                    ("\U0001F534%d" % loc_total) if loc_total else "0"]))  # unicode renders inside code fences; :emoji: does not

    fence = "```"
    out = [":clipboard: *Weekly Layaway Review — %s*" % pretty_date(post_date),
           "_(% = store's share of the company total for that metric)_",
           fence + "\n" + "\n".join(tbl) + "\n" + fence]
    locs = [(name, lay[c]["locate"]) for c, name in STORES if lay[c]["locate"]]
    if locs:
        for name, n in locs:
            out.append(":red_circle: *%s has %d Locate Layaway%s* — must be physically located and resolved"
                       % (name, n, "" if n == 1 else "s"))
    else:
        out.append("_No Locate layaways this week._")
    msg = "\n".join(out)
    if msg.count(fence) != 2:
        raise Withhold(["code fences unbalanced"])
    return msg, {"layaways": lay}


# ---------------------------------------------------------------------------
# EMPLOYEE PERFORMANCE (MTD)
# ---------------------------------------------------------------------------
def load_employee_activity(output_dir, pipeline_date):
    first = pipeline_date[:8] + "01"
    pdate = dt.datetime.strptime(pipeline_date, "%Y-%m-%d")
    by_name, stores_seen, problems = {}, {}, []
    for code, name in STORES:
        p = store_file(output_dir, first, code, "employee-activity")
        if not os.path.exists(p):
            problems.append("%s: employee-activity CSV for %s not found" % (name, first))
            continue
        mtime = dt.datetime.fromtimestamp(os.path.getmtime(p))
        if mtime.date() < pdate.date():
            problems.append("%s: employee-activity CSV is stale (written %s, pull was %s)"
                            % (name, mtime.date().isoformat(), pipeline_date))
            continue
        rows = read_csv_rows(p)
        hdr_i = None
        for i, r in enumerate(rows):
            if r and r[0].strip() == "Employee":
                hdr_i = i
                break
        if hdr_i is None:
            problems.append("%s: no Employee header row" % name)
            continue
        hdr = [h.strip() for h in rows[hdr_i]]
        if "Retail Sales Excluding Fees" not in hdr:
            problems.append("%s: 'Retail Sales Excluding Fees' column missing" % name)
            continue
        col = hdr.index("Retail Sales Excluding Fees")
        n_emp = 0
        for r in rows[hdr_i + 1:]:
            if not r or not r[0].strip():
                continue
            label = r[0].strip()
            if label.lower().startswith(("total store", "report printed", "system")):
                continue
            emp = label.split(" - ", 1)[1].strip() if " - " in label else label
            if "PRESTON PETERS" in emp.upper():
                continue
            try:
                v = money(r[col]) if col < len(r) else 0.0
            except ValueError:
                continue
            key = emp.upper()
            by_name.setdefault(key, {"total": 0.0, "stores": []})
            by_name[key]["total"] += v
            if v != 0.0 and code not in by_name[key]["stores"]:
                by_name[key]["stores"].append(code)
            n_emp += 1
        if n_emp == 0:
            problems.append("%s: employee-activity CSV has no employee rows" % name)
            continue
        stores_seen[code] = True
    if problems:
        raise Withhold(problems)
    return first, by_name


def title_name(upper):
    return " ".join(w.capitalize() for w in upper.lower().split())


def render_employee_performance(output_dir, pipeline_date, post_date, notes):
    first, by_name = load_employee_activity(output_dir, pipeline_date)
    ranked = [(k, v) for k, v in by_name.items() if v["total"] > 0.0]
    ranked.sort(key=lambda kv: -kv[1]["total"])
    if not ranked:
        raise Withhold(["no employees with sales > $0"])
    medals = {1: ":first_place_medal:", 2: ":second_place_medal:", 3: ":third_place_medal:"}
    lines = ["*MTD Employee Sales Rankings — Retail Sales Excluding Fees*",
             ":bar_chart: Period: %s–%s" % (first, pipeline_date), ""]
    for i, (k, v) in enumerate(ranked, 1):
        rank = medals.get(i, "%dth" % i if i > 3 else "")
        stores = "+".join(sorted(v["stores"], key=lambda c: [s[0] for s in STORES].index(c)))
        lines.append("%s *%s* (%s) — %s" % (rank, title_name(k), stores, usd(v["total"])))
    if any(k.startswith("FREE1") for k, _ in ranked):
        notes.append("the shared FREE1 login appears in the employee ranking — sales rung under the "
                     "shared login are not attributable to a person")
    return "\n".join(lines), {"ranked": ranked}


# ---------------------------------------------------------------------------
# FIRST-PAYMENT-DEFAULT
# ---------------------------------------------------------------------------
def load_fpd(output_dir, pipeline_date):
    per_store, rows_all, problems = {}, [], []
    for code, name in STORES:
        p = store_file(output_dir, pipeline_date, code, "fpd-cohort")
        if not os.path.exists(p):
            problems.append("%s: fpd-cohort CSV not found" % name)
            continue
        rows = read_csv_rows(p)
        if not rows or "Ticket Number" not in [c.strip() for c in rows[0]]:
            problems.append("%s: fpd-cohort CSV has no header" % name)
            continue
        hdr = [c.strip() for c in rows[0]]
        it, ic, id_, ia = (hdr.index("Ticket Number"), hdr.index("Category"),
                           hdr.index("Full Description"), hdr.index("Loan Amount"))
        n, d = 0, 0.0
        for r in rows[1:]:
            if not r or len(r) <= ia or not r[it].strip():
                continue
            amt = money(r[ia])
            n += 1
            d += amt
            rows_all.append({"store": code, "ticket": r[it].strip(), "category": r[ic].strip(),
                             "desc": r[id_].strip(), "amount": amt})
        per_store[code] = {"count": n, "dollars": d}
    if problems:
        raise Withhold(problems)
    return per_store, rows_all


def fpd_archive_rows():
    if not os.path.exists(FPD_ARCHIVE):
        return []
    out = []
    with open(FPD_ARCHIVE, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.append(r)
    return out


def fpd_archive_append(rows_all, first_seen):
    os.makedirs(os.path.dirname(FPD_ARCHIVE), exist_ok=True)
    existing = set(r["ticket_number"] for r in fpd_archive_rows())
    new = [r for r in rows_all if r["ticket"] not in existing]
    write_header = not os.path.exists(FPD_ARCHIVE) or os.path.getsize(FPD_ARCHIVE) == 0
    with open(FPD_ARCHIVE, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if write_header:
            w.writerow(["first_seen_date", "store", "ticket_number", "category", "full_description", "loan_amount"])
        for r in new:
            w.writerow([first_seen, r["store"], r["ticket"], r["category"], r["desc"], "%.1f" % r["amount"]])
    return len(new)


def top_categories(rows, n=3):
    agg = {}
    for r in rows:
        a = agg.setdefault(r["category"], [0, 0.0])
        a[0] += 1
        a[1] += r["amount"]
    return sorted(agg.items(), key=lambda kv: (-kv[1][0], -kv[1][1]))[:n]


def render_fpd(output_dir, pipeline_date, post_date, notes):
    per_store, rows_all = load_fpd(output_dir, pipeline_date)
    ranking = sorted(STORES, key=lambda s: (per_store[s[0]]["count"], per_store[s[0]]["dollars"]))
    tot_n = sum(v["count"] for v in per_store.values())
    tot_d = sum(v["dollars"] for v in per_store.values())
    lines = [":dart: *Weekly First-Payment-Default Ranking — %s*" % pretty_date(post_date),
             "_Loans written 60–90 days ago with no payment yet_", "",
             "*Store ranking — best to worst*"]
    for i, (code, name) in enumerate(ranking, 1):
        v = per_store[code]
        lines.append("%d. *%s* — %d FPD loans • %s exposure" % (i, name, v["count"], usd(v["dollars"])))
    lines.append("*Company:* %d FPD loans • %s total exposure" % (tot_n, usd(tot_d)))
    lines.append("")
    lines.append("*Top default-prone categories (this week)*")
    tc = top_categories(rows_all)
    if tc:
        for i, (cat, (n, d)) in enumerate(tc, 1):
            lines.append("%d. %s — %d loans • %s" % (i, cat, n, usd(d)))
    else:
        lines.append("_None this week._")
    # chronic (12-month) from the archive + this week's rows (archive is appended on post)
    cutoff = (dt.datetime.strptime(post_date, "%Y-%m-%d") - dt.timedelta(days=365)).date().isoformat()
    hist = [{"category": r["category"], "amount": money(r["loan_amount"]), "ticket": r["ticket_number"]}
            for r in fpd_archive_rows() if r.get("first_seen_date", "") >= cutoff]
    seen = set(h["ticket"] for h in hist)
    hist += [{"category": r["category"], "amount": r["amount"], "ticket": r["ticket"]}
             for r in rows_all if r["ticket"] not in seen]
    lines.append("")
    lines.append("*Chronic-risk categories (last 12 months)*")
    for i, (cat, (n, d)) in enumerate(top_categories(hist), 1):
        lines.append("%d. %s — %d total FPD loans • %s" % (i, cat, n, usd(d)))
    return "\n".join(lines), {"per_store": per_store, "rows": rows_all}


RENDERERS = {
    "loan-review": render_loan_review,
    "layaway-review": render_layaway_review,
    "employee-performance": render_employee_performance,
    "first-payment-default": render_fpd,
}


# ---------------------------------------------------------------------------
# Slack (bot identity) — token from Keychain, never from this file.
# ---------------------------------------------------------------------------
def get_bot_token():
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", "joshuadavis"),
             "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, timeout=10)
        tok = out.stdout.strip()
        if out.returncode == 0 and tok.startswith("xox"):
            return tok
    except Exception:
        pass
    tok = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    return tok or None


def slack_call(token, method, payload=None, params=None):
    if payload is not None:
        req = urllib.request.Request(
            "https://slack.com/api/" + method, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json; charset=utf-8"})
    else:
        qs = "&".join("%s=%s" % (k, urllib.request.quote(str(v))) for k, v in (params or {}).items())
        req = urllib.request.Request("https://slack.com/api/%s?%s" % (method, qs),
                                     headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def already_posted(token, channel, marker, post_date):
    """True if a message carrying the marker exists in channel since local midnight of post_date."""
    start = dt.datetime.strptime(post_date, "%Y-%m-%d")
    oldest = start.timestamp()
    res = slack_call(token, "conversations.history", params={"channel": channel, "oldest": oldest, "limit": 100})
    if not res.get("ok"):
        raise RuntimeError("history: " + res.get("error", "?"))
    for m in res.get("messages", []):
        if marker in (m.get("text") or ""):
            return True
    return False


def cmd_retract(args):
    """Remove one of the BOT's OWN messages (Slack refuses anything else with this token).
    Used to pull a post the engine itself made in error, e.g. a shadow test that landed in prod."""
    token = get_bot_token()
    if not token:
        sys.stderr.write("no bot token\n")
        return 3
    res = slack_call(token, "chat.delete", payload={"channel": args.channel, "ts": args.ts})
    if not res.get("ok"):
        sys.stderr.write("retract failed: %s\n" % res.get("error", "?"))
        return 1
    log_run("retract", ["retracted %s ts=%s" % (args.channel, args.ts)])
    sys.stderr.write("retracted %s ts=%s\n" % (args.channel, args.ts))
    return 0


def resolve_shadow_channel(token):
    if SHADOW_CHANNEL_ID:
        return SHADOW_CHANNEL_ID
    cur = None
    while True:
        params = {"types": "public_channel,private_channel", "limit": 200, "exclude_archived": "true"}
        if cur:
            params["cursor"] = cur
        res = slack_call(token, "conversations.list", params=params)
        if not res.get("ok"):
            return None
        for ch in res.get("channels", []):
            if ch.get("name") == SHADOW_CHANNEL_NAME:
                return ch["id"]
        cur = res.get("response_metadata", {}).get("next_cursor")
        if not cur:
            return None


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def do_render(args, notes):
    if args.pub not in RENDERERS:
        sys.stderr.write("unknown publication %r\n" % args.pub)
        return 1, None, None
    try:
        body, extra = RENDERERS[args.pub](args.output_dir, args.pipeline_date, args.post_date, notes)
    except Withhold as w:
        reasons = w.args[0] if isinstance(w.args[0], list) else [str(w.args[0])]
        sys.stderr.write("WITHHOLD — %s not emitted.\n" % args.pub)
        for r in reasons:
            sys.stderr.write("  - %s\n" % r)
        sys.stderr.write("Post NOTHING to the channel this run.\n")
        log_run(args.pub, ["WITHHOLD"] + reasons)
        return 2, None, None
    return 0, body, extra


def cmd_render(args):
    notes = []
    code, body, _ = do_render(args, notes)
    if code:
        return code
    for n in notes:
        sys.stderr.write("NOTE — %s\n" % n)
    log_run(args.pub, ["rendered"] + ["note: " + n for n in notes])
    sys.stdout.write(body + "\n")
    return 0


def cmd_check(args):
    pub = PUBS[args.pub]
    token = get_bot_token()
    if not token:
        sys.stderr.write("no bot token — cannot check; caller must dedupe via the connector\n")
        return 3
    try:
        if already_posted(token, args.channel or pub["channel"], pub["marker"], args.post_date):
            sys.stderr.write("DUPLICATE — %s already posted today\n" % args.pub)
            return 4
    except Exception as exc:
        sys.stderr.write("check failed: %s\n" % exc)
        return 3
    return 0


def cmd_post(args):
    notes = []
    code, body, extra = do_render(args, notes)
    if code:
        return code
    for n in notes:
        sys.stderr.write("NOTE — %s\n" % n)
    pub = PUBS[args.pub]
    channel = args.channel or pub["channel"]
    token = get_bot_token()
    if args.shadow:
        if not token:
            sys.stderr.write("shadow post needs the bot token\n")
            return 3
        shadow = resolve_shadow_channel(token)
        if not shadow:
            # NEVER fall through to production on a shadow run (2026-09-06 lesson).
            sys.stderr.write("shadow channel #%s not found/visible to the bot — nothing posted\n" % SHADOW_CHANNEL_NAME)
            sys.stdout.write(body + "\n")
            return 3
        channel = shadow
    if args.dry_run:
        sys.stderr.write("DRY RUN — would post to %s as the bot (%s)\n" % (channel, "token ok" if token else "NO TOKEN"))
        sys.stdout.write(body + "\n")
        return 0
    if not token:
        sys.stderr.write("NO BOT TOKEN — post the body below VERBATIM via the Slack connector to %s\n" % channel)
        log_run(args.pub, ["no bot token; handed body back to caller"])
        sys.stdout.write(body + "\n")
        return 3
    try:
        if not args.shadow and already_posted(token, channel, pub["marker"], args.post_date):
            sys.stderr.write("DUPLICATE — %s already posted to %s today; nothing sent\n" % (args.pub, channel))
            log_run(args.pub, ["duplicate guard hit; nothing sent"])
            return 4
    except Exception as exc:
        sys.stderr.write("dedupe check failed (%s) — refusing to post blind; caller must dedupe + post via connector\n" % exc)
        sys.stdout.write(body + "\n")
        return 3
    res = slack_call(token, "chat.postMessage", payload={"channel": channel, "text": body, "unfurl_links": False, "unfurl_media": False})
    if not res.get("ok"):
        err = res.get("error", "?")
        sys.stderr.write("BOT POST FAILED (%s) — post the body below VERBATIM via the Slack connector to %s\n" % (err, channel))
        log_run(args.pub, ["bot post failed: " + err])
        sys.stdout.write(body + "\n")
        return 3
    ts = res.get("ts")
    log_run(args.pub, ["POSTED to %s ts=%s as bot" % (channel, ts)] + ["note: " + n for n in notes])
    if args.pub == "first-payment-default" and not args.shadow:
        try:
            added = fpd_archive_append(extra["rows"], args.post_date)
            log_run(args.pub, ["archive +%d tickets" % added])
        except Exception as exc:
            sys.stderr.write("archive append failed: %s\n" % exc)
    sys.stderr.write("POSTED to %s as the bot (ts %s)\n" % (channel, ts))
    return 0


def cmd_results_json(args):
    """Write loan-layaway-results-latest.json (downstream: weekly-loan-layaway-manager-dms)."""
    notes = []
    try:
        loans = load_loans(args.output_dir, args.pipeline_date)
        lay = load_layaways(args.output_dir, args.pipeline_date)
    except Withhold as w:
        sys.stderr.write("results-json not written: %s\n" % w.args[0])
        return 2
    eom_date, balances = load_loan_balances(args.output_dir, args.post_date)
    out = {"date": args.post_date, "pipeline_date": args.pipeline_date,
           "company_loan_balance": sum(balances.values()) if balances else None,
           "loan_balance_as_of": eom_date, "stores": {}}
    for code, _ in STORES:
        pct = (loans[code]["dollars"] / balances[code] * 100.0) if balances else None
        out["stores"][code] = {
            "loan_count": loans[code]["count"], "loan_dollar": loans[code]["dollars"],
            "loan_pct": round(pct, 2) if pct is not None else None,
            "loan_status": ("over" if pct > LOAN_POLICY_PCT else "ok") if pct is not None else "unknown",
            "layaway_overdue": lay[code]["overdue"], "layaway_past_pmt_due": lay[code]["past_pmt_due"],
            "layaway_contacted_no_act": lay[code]["contacted_no_activity"],
            "layaway_no_pmt_30d": lay[code]["no_pmt_30d"], "layaway_locate": lay[code]["locate"],
        }
    path = args.results_path or RESULTS_JSON
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    sys.stderr.write("wrote %s\n" % path)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    def common(p):
        p.add_argument("--pub", required=True, choices=sorted(PUBS.keys()))
        p.add_argument("--pipeline-date", required=True)
        p.add_argument("--post-date", required=True)
        p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
        p.add_argument("--channel", default=None, help="override channel id")

    common(sub.add_parser("render"))
    common(sub.add_parser("check"))
    p = sub.add_parser("post")
    common(p)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--shadow", action="store_true", help="post to #%s instead" % SHADOW_CHANNEL_NAME)
    p = sub.add_parser("results-json")
    p.add_argument("--pipeline-date", required=True)
    p.add_argument("--post-date", required=True)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--results-path", default=None)
    p = sub.add_parser("retract", help="delete one of the bot's own messages (channel + ts)")
    p.add_argument("--channel", required=True)
    p.add_argument("--ts", required=True)
    args = ap.parse_args()
    if args.cmd == "retract":
        return cmd_retract(args)
    if args.cmd == "render":
        return cmd_render(args)
    if args.cmd == "check":
        return cmd_check(args)
    if args.cmd == "post":
        return cmd_post(args)
    if args.cmd == "results-json":
        return cmd_results_json(args)
    ap.print_help()
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write("WITHHOLD — engine error: %s\n" % exc)
        sys.exit(1)
