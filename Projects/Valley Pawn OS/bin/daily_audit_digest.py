#!/usr/bin/env python3
"""daily_audit_digest.py [YYYY-MM-DD] [--root <Projects dir>] [--out <dir>]

Daily Store Audit digest (built 2026-09-30, reminder "Create daily audit pushed to Preston daily.
Cash count, intake and sales."). READ-ONLY roll-up of what the existing automations already produced
for ONE business day. It never touches Bravo, never triggers a pull, never re-runs a compile, and
never posts anything — it writes files; the `daily-store-audit-digest` scheduled task posts them.

Sources (all written by other automations; this script only reads them):
  CASH    Daily Funds Verification/<date> Funds Verification.md      (bin/funds_verification.py, 18:30)
          Bravo Data Extraction/output/<date>_<S>_safe-register-journal.csv  (drawer cash at close)
          Valley Pawn OS/fleet/eod_photos/<date>/index.json          (#end-of-day count-sheet photos, 20:15)
          Valley Pawn OS/hr/ROSTER.json                              (who posted -> which store)
  INTAKE  Pawn Walks/daily/<date>_intake_margin_summary.json (+ .xlsx) (daily-report-pawn 07:15)
  SALES   Sold Margin Review/daily/<date>_sold_review_summary.json (+ .xlsx) (daily-report-sold 07:45)
          Discount Outlier Review/daily/<date>_discount_review_summary.json (daily-report-discount 08:25)

Date: default = the most recent business day before today (ET): skips Sunday (all closed);
Wednesday = Culpeper + Roanoke from 2026-09-30, Culpeper only before (matches vp_lib.sh open_stores); any other store with real activity
that day is added automatically (2026-10-01).

Outputs (in --out, default Valley Pawn OS/daily-audit/):
  <date>.slack.txt   the exact message to post via the Slack connector (standard markdown: **bold**;
                     plain business language, Rule 16)
  <date>.mrkdwn.txt  same message in Slack-native formatting (*bold*) for the ops-bot outbox send
  <date>.md          same content, for the record
  <date>.json        machine summary incl. `complete` and `unavailable` list
Exit 0 always when it could write; exit 2 if the date has no open stores; exit 1 on a crash.
Completeness rule (Rule 18): a section is shown for a store only when its source file exists AND
contains that store. Anything missing is named plainly as "not available" — never shown as zero.
"""
import csv
import datetime as dt
import glob
import json
import os
import re
import sys

try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except Exception:  # pragma: no cover
    ET = None

STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
NAME = dict(STORES)
TARGET = 0.50            # intake + sold margin target used by the source reports
DISC_FLAG_PCT = None     # discount store-level status is taken from the source's own flag counts


def find_root(arg):
    cands = [arg, os.environ.get("VP_PROJECTS"), os.path.expanduser("~/Documents/Claude/Projects")]
    cands += sorted(glob.glob("/sessions/*/mnt/Projects"))
    for c in cands:
        if c and os.path.isdir(os.path.join(c, "Valley Pawn OS")):
            return c
    raise SystemExit("Projects folder not found")


def open_stores(day):
    dow = day.isoweekday()
    if dow == 7:
        return []
    if dow == 3:
        # Roanoke open Wednesdays from 2026-09-30 (Joshua 2026-10-01); earlier Wednesdays CUL only.
        return ["CUL", "ROA"] if day >= dt.date(2026, 9, 30) else ["CUL"]
    return [s for s, _ in STORES]


def prior_business_day(today):
    d = today - dt.timedelta(days=1)
    while not open_stores(d):
        d -= dt.timedelta(days=1)
    return d


def usd(x, cents=False):
    return ("${:,.2f}" if cents else "${:,.0f}").format(x)


def pct(x):
    return "—" if x is None else "%d%%" % round(x * 100)


def money(s):
    s = (s or "").strip()
    if not s:
        return None
    neg = s.startswith("(") or s.startswith("-")
    s = re.sub(r"[^0-9.]", "", s)
    if not s:
        return None
    v = float(s)
    return -v if neg else v


def load_json(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return None


# ---------------------------------------------------------------- CASH -------------------------------
def read_funds(root, day):
    """Parse the native funds-verification table. Returns {store: {...}} only for rows that parse."""
    p = os.path.join(root, "Daily Funds Verification", "%s Funds Verification.md" % day.isoformat())
    if not os.path.exists(p):
        return None, p
    out = {}
    for line in open(p, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        code = next((s for s, n in STORES if cells[0].startswith(n) or cells[0].startswith(s + " ")), None)
        if not code:
            continue
        status = cells[4]
        if "Matched" in status:
            st = "matched"
        elif "Discrepancy" in status:
            st = "discrepancy"
        elif "Check" in status:
            st = "check"
        else:
            st = "unverified"
        out[code] = {"expected": money(cells[2]), "in_bravo": money(cells[3]), "status": st, "status_text": status}
    return (out or None), p


def read_drawer_cash(root, day, code):
    """Sum of Cash on TILL CLOSE-BALANCE rows in the Safe Register Journal (data is offset one column
    right of the header: type=col3, till=col4, tender=col8, amount=col10)."""
    p = os.path.join(root, "Bravo Data Extraction", "output", "%s_%s_safe-register-journal.csv" % (day.isoformat(), code))
    if not os.path.exists(p):
        return None
    rows = list(csv.reader(open(p, encoding="utf-8-sig", errors="replace")))
    # business date sanity check
    bd = next((r for r in rows[:5] if any("Business Date" in c for c in r)), None)
    if bd:
        want = "%d/%d/%d" % (day.month, day.day, day.year)
        if want not in ",".join(bd):
            return None
    cur, tills, total = None, [], 0.0
    safe_closed = False
    for r in rows:
        r = r + [""] * (11 - len(r))
        if r[7].strip() == "Tender Totals":
            break
        if r[3].strip():
            cur = r[3].strip().upper()
            if cur == "SAFE CLOSE-BALANCE":
                safe_closed = True
        if cur == "TILL CLOSE-BALANCE" and r[8].strip().lower() == "cash" and (r[3].strip() or not r[4].strip()):
            v = money(r[10])
            if v is not None:
                tills.append((r[4].strip() or "till", v))
                total += v
    # The safe close is the last step of a store's night. Until it is in the journal, some tills may
    # not be closed yet, so a drawer total would be partial -> report nothing rather than a wrong number.
    # (The evening Bravo read runs ~18:30, before several stores finish closing — see STATUS gap note.)
    if not safe_closed:
        return {"closed": False, "total": None, "tills": []}
    return {"closed": True, "total": round(total, 2), "tills": tills}


def read_count_sheets(root, day):
    idx = load_json(os.path.join(root, "Valley Pawn OS", "fleet", "eod_photos", day.isoformat(), "index.json"))
    if idx is None:
        return None
    roster = load_json(os.path.join(root, "Valley Pawn OS", "hr", "ROSTER.json")) or {}
    by_id = {e.get("slack_id"): e for e in roster.get("employees", []) if e.get("slack_id")}
    rev = {n: s for s, n in STORES}
    per = {}
    unknown = []
    for m in idx:
        e = by_id.get(m.get("poster_id"))
        store = rev.get((e or {}).get("department"))
        who = (e or {}).get("preferred") or m.get("poster", "?")
        t = m.get("ts", "")[11:16]
        if store:
            d = per.setdefault(store, {"photos": 0, "by": set(), "time": t})
            d["photos"] += 1
            d["by"].add(who)
        else:
            unknown.append(who)
    for d in per.values():
        d["by"] = sorted(d["by"])
    return {"per_store": per, "unattributed": sorted(set(unknown))}


# ---------------------------------------------------------------- INTAKE / SALES --------------------
def xlsx_sheet(path, sheet, header_row_contains):
    try:
        import openpyxl
    except Exception:
        return None
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[sheet]
        rows = list(ws.iter_rows(values_only=True))
    except Exception:
        return None
    hi = next((i for i, r in enumerate(rows) if r and header_row_contains in [str(c) for c in r]), None)
    if hi is None:
        return None
    hdr = [str(c) if c is not None else "" for c in rows[hi]]
    return [dict(zip(hdr, r)) for r in rows[hi + 1:] if r and r[0]]


def read_intake(root, day):
    p = os.path.join(root, "Pawn Walks", "daily", "%s_intake_margin_summary.json" % day.isoformat())
    d = load_json(p)
    if d is None:
        return None
    stores = d.get("stores") or {}
    items = xlsx_sheet(os.path.join(root, "Pawn Walks", "daily", "%s_intake_margin.xlsx" % day.isoformat()), "Items", "Cost Paid")
    paid = None
    flags_detail = {}
    if items is not None:
        paid = {}
        for r in items:
            s = r.get("Store")
            try:
                paid[s] = paid.get(s, 0.0) + float(r.get("Cost Paid") or 0)
            except Exception:
                pass
        # cross-check against the summary's own category totals; drop $ if they disagree
        g = sum((v or {}).get("cost_paid", 0) or 0 for v in (d.get("groups") or {}).values())
        if g and abs(sum(paid.values()) - g) > 1:
            paid = None
    fl = xlsx_sheet(os.path.join(root, "Pawn Walks", "daily", "%s_intake_margin.xlsx" % day.isoformat()), "Flags", "Cost Paid")
    if fl:
        for r in fl:
            flags_detail.setdefault(r.get("Store"), []).append(r)
    return {"stores": stores, "paid": paid, "flags_detail": flags_detail, "info": d.get("info"),
            "company": {"items": d.get("items"), "avg": d.get("avg_margin"), "flags": d.get("flags")}}


def read_sold(root, day):
    p = os.path.join(root, "Sold Margin Review", "daily", "%s_sold_review_summary.json" % day.isoformat())
    d = load_json(p)
    if d is None:
        return None
    rev = None
    items = xlsx_sheet(os.path.join(root, "Sold Margin Review", "daily", "%s_sold_review.xlsx" % day.isoformat()), "Items", "Sale Price")
    msg_rev = re.search(r"Revenue \$([\d,]+)", d.get("slack_message") or "")
    if items is not None and msg_rev:
        rev = {}
        for r in items:
            try:
                rev[r.get("Store")] = rev.get(r.get("Store"), 0.0) + float(r.get("Sale Price") or 0)
            except Exception:
                pass
        if abs(sum(rev.values()) - float(msg_rev.group(1).replace(",", ""))) > 1.5:
            rev = None   # cannot reconcile to the published company figure -> do not show per-store $
    return {"stores": d.get("stores") or {}, "missing": d.get("missing_stores") or [], "revenue": rev,
            "company_revenue": float(msg_rev.group(1).replace(",", "")) if msg_rev else None}


def read_discount(root, day):
    d = load_json(os.path.join(root, "Discount Outlier Review", "daily", "%s_discount_review_summary.json" % day.isoformat()))
    if d is None:
        return None
    return {"stores": d.get("stores") or {}, "missing": d.get("missing_stores") or []}


# ---------------------------------------------------------------- BUILD -------------------------------
def build(root, day):
    opened = open_stores(day)
    funds, _ = read_funds(root, day)
    intake = read_intake(root, day)
    sold = read_sold(root, day)
    disc = read_discount(root, day)
    counts = read_count_sheets(root, day)
    # 2026-10-01: a normally-closed store that actually did business that day (Roanoke on
    # Wed 9/30 took in 9 items, sold 8 and posted a count sheet) is added to the day's stores
    # when the source reports show activity for it. Additive; scheduled open stores unchanged.
    active = set()
    for src in (intake, sold, disc):
        for k, v in ((src or {}).get("stores") or {}).items():
            if isinstance(v, dict) and (v.get("items") or v.get("total_items") or v.get("count") or v.get("n")):
                active.add(k)
            elif v and not isinstance(v, dict):
                active.add(k)
    active |= set(((counts or {}).get("per_store") or {}).keys())
    opened = list(opened) + [s for s, _ in STORES if s in active and s not in opened]
    unavailable = []   # (store, section)
    exceptions = []
    per = {}
    for s in opened:
        n = NAME[s]
        rec = {}
        # cash
        f = (funds or {}).get(s)
        rec["funds"] = f
        if f is None:
            unavailable.append((s, "funds check"))
        elif f["status"] == "discrepancy":
            exceptions.append("%s: cash sent was %s but Bravo shows %s entered into the safe" % (n, usd(f["expected"] or 0, True), usd(f["in_bravo"] or 0, True)))
        elif f["status"] == "check":
            exceptions.append("%s: a cash send needs a look (a cancel or an unclear amount in the funds channel)" % n)
        elif f["status"] == "unverified":
            unavailable.append((s, "funds check"))
        # Drawer cash at close is informational only (shown when the store's full close was already in
        # Bravo when it was read); it is never shown partially and never counted as missing data.
        rec["drawer"] = read_drawer_cash(root, day, s)
        if counts is None:
            rec["count"] = None
            unavailable.append((s, "count sheet"))
        else:
            c = counts["per_store"].get(s)
            rec["count"] = c or {"photos": 0}
            if not c:
                exceptions.append("%s: no end-of-day count sheet posted" % n)
        # intake
        if intake is None or s not in intake["stores"]:
            if intake is not None and intake.get("info") and not intake["stores"]:
                rec["intake"] = {"total_items": 0, "avg_margin": None, "flags": 0}
            else:
                rec["intake"] = None
                unavailable.append((s, "intake"))
        else:
            rec["intake"] = dict(intake["stores"][s])
            if intake["paid"] is not None:
                rec["intake"]["paid"] = intake["paid"].get(s, 0.0)
            im = rec["intake"]
            if im.get("flags"):
                top = sorted(intake["flags_detail"].get(s, []), key=lambda r: (r.get("Margin") if isinstance(r.get("Margin"), (int, float)) else 9))
                eg = ""
                if top:
                    r0 = top[0]
                    eg = " — worst: %s on %s" % (usd(float(r0.get("Cost Paid") or 0)), str(r0.get("Description") or "")[:40].strip().rstrip(",;- "))
                exceptions.append("%s: %d intake item%s paid/loaned too high — under 30%% margin%s" % (n, im["flags"], "" if im["flags"] == 1 else "s", eg))
            if im.get("avg_margin") is not None and im["avg_margin"] < TARGET and im.get("total_items", 0) >= 3:
                exceptions.append("%s: intake averaged %s margin vs the 50%% target" % (n, pct(im["avg_margin"])))
        # sales
        if sold is None or s not in sold["stores"]:
            rec["sold"] = None
            unavailable.append((s, "sales"))
        else:
            rec["sold"] = dict(sold["stores"][s])
            if sold["revenue"] is not None:
                rec["sold"]["revenue"] = sold["revenue"].get(s, 0.0)
            sm = rec["sold"]
            if sm.get("critical"):
                exceptions.append("%s: %d item%s sold below cost" % (n, sm["critical"], "" if sm["critical"] == 1 else "s"))
            if sm.get("flags"):
                exceptions.append("%s: %d item%s sold too cheap (under 25%% margin)" % (n, sm["flags"], "" if sm["flags"] == 1 else "s"))
        if disc is None or s not in disc["stores"]:
            rec["disc"] = None
            unavailable.append((s, "discounts"))
        else:
            rec["disc"] = disc["stores"][s]
            if rec["disc"].get("flags"):
                exceptions.append("%s: %d discount%s bigger than the item's age allows (%s off ticket prices that day, all sales)" % (
                    n, rec["disc"]["flags"], "" if rec["disc"]["flags"] == 1 else "s", usd(rec["disc"].get("total_discount_dollars") or 0)))
        per[s] = rec
    if counts and counts.get("unattributed"):
        exceptions.append("Count-sheet photos posted by someone not on a store roster: %s" % ", ".join(counts["unattributed"]))
    return opened, per, exceptions, unavailable, sold


def render(day, opened, per, exceptions, unavailable, sold):
    L = []
    title = "Daily Store Audit — %s" % day.strftime("%a %-m/%-d/%Y")
    L.append("**%s**" % title)
    L.append("Stores open that day: %s" % (", ".join(NAME[s] for s in opened) if len(opened) < 5 else "all 5"))
    if unavailable:
        by = {}
        for s, sec in unavailable:
            by.setdefault(sec, []).append(NAME[s])
        L.append("")
        L.append("**Not available yet (not included below):**")
        for sec, ss in by.items():
            L.append("• %s — %s" % (sec[0].upper() + sec[1:], "all open stores" if len(ss) == len(opened) and len(opened) > 1 else ", ".join(ss)))
    L.append("")
    L.append("**Needs attention**")
    if exceptions:
        for e in exceptions:
            L.append("• " + e)
    else:
        L.append("• Nothing flagged.")
    for s in opened:
        r = per[s]
        L.append("")
        L.append("**%s**" % NAME[s])
        # cash
        parts = []
        f = r["funds"]
        if f and f["status"] in ("matched", "discrepancy", "check"):
            if (f["expected"] or 0) == 0 and (f["in_bravo"] or 0) == 0:
                parts.append("no cash sent")
            else:
                mark = {"matched": "✅ in the safe", "discrepancy": "⚠️ does not match Bravo", "check": "⚠️ needs a look"}[f["status"]]
                parts.append("cash sent %s %s" % (usd(f["expected"] or 0), mark))
        dc = r["drawer"]
        if dc and dc["closed"]:
            parts.append("drawer cash at close %s" % usd(dc["total"], True))
        c = r["count"]
        if c is not None:
            parts.append("count sheet posted ✅" if c.get("photos") else "count sheet ⚠️ not posted")
        L.append("• Cash: " + ("; ".join(parts) if parts else "not available"))
        im = r["intake"]
        if im is not None:
            if not im.get("total_items"):
                L.append("• Intake: no buys or loans")
            else:
                paid = (" · %s paid/loaned" % usd(im["paid"])) if im.get("paid") is not None else ""
                fl = im.get("flags", 0)
                L.append("• Intake: %d items%s · avg margin %s %s · %s" % (
                    im["total_items"], paid, pct(im.get("avg_margin")),
                    "✅" if (im.get("avg_margin") or 0) >= TARGET else "⚠️",
                    "no overpay flags" if not fl else "%d overpay flag%s" % (fl, "" if fl == 1 else "s")))
        sm = r["sold"]
        if sm is not None:
            if not sm.get("items"):
                L.append("• Sales: no sales")
            else:
                rv = (" · %s" % usd(sm["revenue"])) if sm.get("revenue") is not None else ""
                fl = sm.get("flags", 0)
                L.append("• Sales: %d items%s · avg margin %s %s · %s" % (
                    sm["items"], rv, pct(sm.get("avg_margin")), "✅" if (sm.get("avg_margin") or 0) >= TARGET else "⚠️",
                    "none sold too cheap" if not fl else "%d sold too cheap" % fl))
        dd = r["disc"]
        if dd is not None and dd.get("items"):
            fl = dd.get("flags", 0)
            L.append("• Discounts: %s off ticket · avg %s · %s" % (
                usd(dd.get("total_discount_dollars") or 0), pct(dd.get("wtd_avg_discount_pct")),
                "all within the age rules" if not fl else "%d over the age rule" % fl))
    # company line
    tot_int = [per[s]["intake"] for s in opened if per[s]["intake"] is not None]
    tot_sold = [per[s]["sold"] for s in opened if per[s]["sold"] is not None]
    L.append("")
    comp = []
    if tot_int and len(tot_int) == len(opened):
        comp.append("%d intake items" % sum(x.get("total_items", 0) for x in tot_int))
        if all(x.get("paid") is not None for x in tot_int if x.get("total_items")):
            comp[-1] += " (%s)" % usd(sum(x.get("paid", 0) or 0 for x in tot_int))
    if tot_sold and len(tot_sold) == len(opened):
        comp.append("%d items sold" % sum(x.get("items", 0) for x in tot_sold))
        if sold and sold.get("company_revenue") is not None and sold.get("revenue") is not None:
            comp[-1] += " (%s)" % usd(sold["company_revenue"])
    if comp:
        L.append("**Company:** " + " · ".join(comp))
    L.append("_Full item lists are in the #pawn-walks, #sold-review, #discount-review and #daily-funds-reconcilation reports._")
    return "\n".join(L), title


def main():
    args = sys.argv[1:]
    root = None
    out = None
    if "--root" in args:
        i = args.index("--root"); root = args[i + 1]; del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    root = find_root(root)
    now = dt.datetime.now(ET) if ET else dt.datetime.now()
    day = dt.date.fromisoformat(args[0]) if args else prior_business_day(now.date())
    if not open_stores(day):
        print("NO_OPEN_STORES %s" % day)
        return 2
    opened, per, exceptions, unavailable, sold = build(root, day)
    text, title = render(day, opened, per, exceptions, unavailable, sold)
    out = out or os.path.join(root, "Valley Pawn OS", "daily-audit")
    os.makedirs(out, exist_ok=True)
    base = os.path.join(out, day.isoformat())
    open(base + ".slack.txt", "w").write(text + "\n")
    # Same message in Slack's native formatting (*bold*), for the ops-bot outbox path, which posts the
    # file as-is via chat.postMessage (standard **bold** would show literal asterisks there).
    open(base + ".mrkdwn.txt", "w").write(text.replace("**", "*") + "\n")
    open(base + ".md", "w").write("# %s\n\n%s\n" % (title, text))
    summary = {"date": day.isoformat(), "title": title, "open_stores": opened,
               "complete": not unavailable, "unavailable": ["%s: %s" % (NAME[s], sec) for s, sec in unavailable],
               "exceptions": exceptions, "generated_at": now.isoformat(), "slack_file": base + ".slack.txt",
               "mrkdwn_file": base + ".mrkdwn.txt"}
    json.dump(summary, open(base + ".json", "w"), indent=1, default=list)
    print("DATE=%s COMPLETE=%s UNAVAILABLE=%d EXCEPTIONS=%d FILE=%s" % (day, summary["complete"], len(unavailable), len(exceptions), base + ".slack.txt"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # never a stack trace into anything that might be posted
        print("CRASH %s: %s" % (type(e).__name__, e))
        sys.exit(1)
