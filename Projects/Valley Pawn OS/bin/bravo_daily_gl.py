#!/usr/bin/env python3
"""bravo_daily_gl.py — DAILY Bravo -> QuickBooks posting (Joshua 2026-10-21: "We should be auto posting daily from
Bravo. This keeps revenue and cogs up to date daily along with the expenses."). Native agent
com.valleypawn.bravo-daily-gl (00:45 + 03:15 catch-up). Live by design (net-new, no cloud copy).

WHAT A RUN DOES (self-catch-up: every day from START through yesterday that is not done yet, oldest first)
  1 post-to-accounting-post-v2, all 5 stores, end = the newest pending day (locks the days in Bravo; Joshua
    pre-authorized day posting 2026-07-06). One trigger through bin/bravo_pull.sh (health gate + contention wait).
  2 per pending day: post-to-accounting-gl for that ONE day, the stores open that day (vp_lib open_stores
    calendar). Any month-end GL file already in output/ for that date is stashed first and restored after, and
    the daily file is MOVED to output/daily_gl/<date>_<ST>.csv, so the monthly export/sales-tax agents never see
    a one-day file under their monthly name.
  3 per store-day: the same mapping as every monthly BRAVO-<ST> entry (Quickbooks Set UP/gl_to_je.classify),
    clearing residual = Bravo POS Clearing, Bravo's own per-store imbalance (inter-store moves) carried in
    Bravo POS Clearing. One journal entry  BRAVO-<ST>-YYYYMMDD  dated that day, store Class on every line.
  4 double-post guard: the state file (written the moment QBO returns) + a QBO query of that day's JEs by
    DocNumber. Read back and verified after posting.
  5 month proof (from the 2nd): the month's Consolidated GL (eom-bravo-gl-export's file) must equal the sum of
    the month's daily entries, per store, per account, to the cent. A store that does not tie has every day of
    the month re-pulled; any day whose GL changed is replaced (logged delete + repost). Never a plug.
FAILURES: retried every run; a store-day failing 3 runs, or a month that will not prove, = ONE ledger row.
No Slack, no DM (Rule 16). Status: fleet/state/bravo_daily_gl/STATUS.md; state.json; QBO-API-WRITELOG.jsonl.

usage: bravo_daily_gl.py [--until HH:MM] [--render] [--day YYYY-MM-DD] [--no-pull] [--prove YYYY-MM]
  --render   build and print, never write to QuickBooks (pulls Bravo unless --no-pull)
  --day      only this day (still skips one that is done)
  --until    stop starting new days after this local time (scheduled default 03:50)
"""
import calendar
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.path.join(PROJ, "Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
DAILY = os.path.join(OUT, "daily_gl")
QBO_DIR = os.path.join(PROJ, "Quickbooks Set UP")
STATE_DIR = os.path.join(OS_DIR, "fleet", "state", "bravo_daily_gl")
STATE_F = os.path.join(STATE_DIR, "state.json")
STATUS_F = os.path.join(STATE_DIR, "STATUS.md")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
sys.path.insert(0, QBO_DIR)
import qbo_api as q                                   # noqa: E402
from gl_to_je import money, classify, read_rows        # noqa: E402

AGENT = "bravo-daily-gl"
ET = ZoneInfo("America/New_York")
START = dt.date(2026, 10, 1)          # Jan-Sep 2026 carry the monthly BRAVO-<ST>-YYYY-MM entries
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAME = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
ORDER = ["Cost of Goods Sold", "Inventory Asset", "Pawn Service Charges", "Layaway",
         "Loans Receivable", "Retail Sales", "Gold Revenue", "Sales tax to pay"]
MAX_TRIES = 3
ARGS = sys.argv[1:]
RENDER = "--render" in ARGS
NO_PULL = "--no-pull" in ARGS


def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS and ARGS.index(name) + 1 < len(ARGS) else default


def now():
    return dt.datetime.now(ET)


def log(msg):
    print("%s %s" % (now().strftime("%Y-%m-%d %H:%M:%S"), msg), flush=True)


def ledger(sentence, human="no"):
    if RENDER:
        log("RENDER would ledger: " + sentence); return
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, human))
    except OSError:
        pass


def load_state():
    try:
        return json.load(open(STATE_F))
    except (OSError, ValueError):
        return {"days": {}, "proven": {}}


def save_state(st):
    if RENDER:
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_F + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1, sort_keys=True)
    os.replace(tmp, STATE_F)


def open_stores(d):
    """Same calendar as vp_lib.sh open_stores(). Sunday none; Wednesday CUL (+ROA from 9/30, +WAY from 10/14)."""
    w = d.isoweekday()
    if w == 7:
        return []
    if w == 3:
        s = ["CUL"]
        if d >= dt.date(2026, 9, 30): s.append("ROA")
        if d >= dt.date(2026, 10, 14): s.append("WAY")
        return s
    return list(STORES)


# ---------------------------------------------------------------- Bravo
def bravo_pull(report, date_arg, stores, tag):
    tid = "dailygl-%s-%s-%s" % (tag, "".join(s[0] for s in stores), now().strftime("%Y%m%dT%H%M%S"))
    log("bravo %s %s %s -> %s" % (report, date_arg, ",".join(stores), tid))
    global _GATED
    if not _GATED:
        # first trigger of the run: the full bravo_pull.sh path (contention wait + Bravo health gate)
        cmd = ["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), report, date_arg, ",".join(stores), tid]
    else:
        # Bravo was proven healthy by this run's previous trigger: drop the trigger straight through bravo_run
        # (bravo_pull.sh would wait out its "result written in the last 3 min" busy check on our OWN last result
        # and re-run the health gate — ~6 min per store instead of ~2.5)
        rep = json.dumps({"name": report, "stores": stores, "date": date_arg})
        cmd = ["/bin/bash", "-c", '. "$1"; bravo_run "$2" "$3" 2400', "x", os.path.join(HERE, "vp_lib.sh"), tid, rep]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, AGENT=AGENT))
    t0, requeues = time.time(), 0
    while proc.poll() is None and time.time() - t0 < 7500:
        time.sleep(15)
        if requeue_if_orphaned(tid):
            requeues += 1; log("re-queued %s after a watcher restart orphaned it (%d)" % (tid, requeues))
    if proc.poll() is None:
        proc.kill(); log("bravo pull %s timed out" % tid)
    try:
        r = json.load(open(os.path.join(BRAVO, "results", tid + ".result.json"), encoding="utf-8-sig"))
    except (OSError, ValueError):
        r = {}
    if r.get("status") in ("success", "partial"):
        _GATED = True
    return {c.get("store"): c for c in r.get("cells", [])}


def requeue_if_orphaned(tid):
    """2026-10-21: another caller's watcher restart (seen 11:51, 12:03, 12:19, 12:53) leaves an in-flight trigger in
    triggers/claimed, where it is never re-run, and bravo_pull.sh then waits out its whole cap. If our trigger is
    claimed, its log has been silent 6+ min and the watcher started AFTER that last write, put it back in the queue
    (the same move bravo_run's own one-shot re-queue makes)."""
    cl = os.path.join(BRAVO, "triggers", "claimed", tid + ".json")
    lg = os.path.join(BRAVO, "logs", tid + ".log")
    ws = os.path.join(BRAVO, "logs", "watcher.last_started.txt")
    if not os.path.exists(cl) or os.path.exists(os.path.join(BRAVO, "results", tid + ".result.json")):
        return False
    last = os.path.getmtime(lg) if os.path.exists(lg) else os.path.getmtime(cl)
    if time.time() - last < 360 or not os.path.exists(ws) or os.path.getmtime(ws) <= last:
        return False
    body = open(cl).read()
    open(os.path.join(BRAVO, "triggers", tid + ".json"), "w").write(body)
    dest = os.path.join(BRAVO, "triggers", "claimed", "aborted-stale-2026-10-05")
    os.makedirs(dest, exist_ok=True)
    os.replace(cl, os.path.join(dest, tid + ".json"))
    return True


def gl_out(d, s):
    return os.path.join(OUT, "%s_%s_post-to-accounting-gl.csv" % (d.isoformat(), s))


def daily_file(d, s):
    return os.path.join(DAILY, "%s_%s.csv" % (d.isoformat(), s))


def pull_day(d, stores):
    """GL for day d; a store that fails inside the multi-store trigger gets ONE immediate retry on its own
    (Bravo's GL store combo is occasionally not clickable — seen HAR 2026-10-21 10:41)."""
    # one store per trigger (~2.5 min): a short trigger never makes another caller's queued trigger look stale to the
    # Windows watchdog (its >20-min pending rule restarted the watcher under our 5-store triggers 2026-10-21)
    res = {}
    for s in stores:
        res.update(_pull_day(d, [s]))
        if res[s]:
            res.update(_pull_day(d, [s]))
    return res


def _pull_day(d, stores):
    """One GL trigger for day d; returns {store: error-or-None}. Month-end files are stashed and restored."""
    os.makedirs(DAILY, exist_ok=True)
    stash = {}
    for s in stores:
        p = gl_out(d, s)
        if os.path.exists(p):
            stash[s] = p + ".stash-dailygl"
            os.replace(p, stash[s])
    try:
        cells = bravo_pull("post-to-accounting-gl", d.isoformat(), stores, "gl-" + d.strftime("%Y%m%d"))
        res = {}
        for s in stores:
            c = cells.get(s, {})
            p = gl_out(d, s)
            if c.get("status") == "success" and os.path.exists(p):
                os.replace(p, daily_file(d, s)); res[s] = None
            else:
                res[s] = (c.get("error") or "no result") [:200]
                if os.path.exists(p):
                    os.remove(p)
        return res
    finally:
        for s, sp in stash.items():
            os.replace(sp, gl_out(d, s))


# ---------------------------------------------------------------- mapping
def build(path, s, d0, d1):
    rows = read_rows(path)
    hdr = " ".join(c for r in rows[:5] for c in r)
    want = "%d/%d/%d - %d/%d/%d" % (d0.month, d0.day, d0.year, d1.month, d1.day, d1.year)
    if want not in hdr or s not in hdr:
        raise ValueError("%s: header %r does not match %s %s" % (os.path.basename(path), hdr[:160], want, s))
    nets, clearing = defaultdict(float), 0.0
    for row in rows:
        if len(row) < 4:
            continue
        acct = (row[0] or "").strip(); al = acct.lower()
        if not acct or al.startswith(("account number", "report printed", "consolidated", "reporting dates")) or al in ("store", "store:"):
            continue
        dr, cr = money(row[2]), money(row[3])
        if dr == 0 and cr == 0:
            continue
        a, desc = classify(acct)
        if a is None:
            clearing += dr - cr
        else:
            nets[(a, desc)] += dr - cr
    residual = -sum(nets.values())
    delta = round(residual - clearing, 2)
    lines = []
    for (a, desc), net in sorted(nets.items(), key=lambda kv: (ORDER.index(kv[0][0]) if kv[0][0] in ORDER else 99, kv[0][1])):
        if abs(net) < 0.005:
            continue
        lines.append({"account": a, "desc": "%s - %s" % (desc, NAME[s]), **({"debit": round(net, 2)} if net > 0 else {"credit": round(-net, 2)})})
    if lines and abs(residual) >= 0.005:
        lines.append({"account": "Bravo POS Clearing", "desc": "POS Clearing - %s" % NAME[s],
                      **({"debit": round(residual, 2)} if residual > 0 else {"credit": round(-residual, 2)})})
    return lines, delta


def by_account(lines):
    t = defaultdict(float)
    for l in lines:
        t[l["account"]] += l.get("debit", 0) - l.get("credit", 0)
    return {k: round(v, 2) for k, v in t.items()}


# ---------------------------------------------------------------- QuickBooks
_ACC, _CLS = {}, {}
_GATED = False


def acct(name):
    if not _ACC:
        for a in q.accounts(active_only=True):
            _ACC.setdefault(a.get("Name"), []).append(a)
            _ACC.setdefault("FQN:" + a.get("FullyQualifiedName", ""), []).append(a)
    hit = _ACC.get("FQN:" + name) or _ACC.get(name) or []
    if len(hit) != 1:
        raise RuntimeError("account %r matched %d" % (name, len(hit)))
    return hit[0]


def store_class(s):
    if not _CLS:
        for c in q.query("SELECT * FROM Class"):
            _CLS[c.get("Name", "").lower()] = c
    for k, c in _CLS.items():
        if NAME[s].lower() in k:
            return c
    return None


def existing_doc(d, doc):
    return [j for j in q.query("SELECT * FROM JournalEntry WHERE TxnDate = '%s'" % d.isoformat())
            if (j.get("DocNumber") or "").strip() == doc]


def je_post(d, s, doc, lines, memo):
    cls = store_class(s)
    body_lines, dr, cr = [], 0.0, 0.0
    for i, ln in enumerate(lines):
        a = acct(ln["account"])
        amt = float(ln.get("debit") or ln.get("credit"))
        pt = "Debit" if ln.get("debit") else "Credit"
        dr += amt if pt == "Debit" else 0; cr += amt if pt == "Credit" else 0
        det = {"PostingType": pt, "AccountRef": {"value": a["Id"], "name": a["Name"]}}
        if cls:
            det["ClassRef"] = {"value": cls["Id"], "name": cls["Name"]}
        body_lines.append({"Id": str(i), "Description": ln["desc"], "Amount": round(amt, 2),
                           "DetailType": "JournalEntryLineDetail", "JournalEntryLineDetail": det})
    if round(dr - cr, 2) != 0:
        raise RuntimeError("%s does not balance: DR %.2f CR %.2f" % (doc, dr, cr))
    j, tid = q._req("POST", "journalentry", body={"TxnDate": d.isoformat(), "DocNumber": doc, "PrivateNote": memo[:4000], "Line": body_lines})
    je = j["JournalEntry"]
    q._writelog({"op": "je-create", "id": je["Id"], "docnum": doc, "date": d.isoformat(), "lines": lines, "tid": tid, "agent": AGENT})
    return je, round(dr, 2)


def je_delete(jid, reason):
    je = q.je_get(jid)
    j, tid = q._req("POST", "journalentry", params={"operation": "delete"}, body={"Id": je["Id"], "SyncToken": je["SyncToken"]})
    q._writelog({"op": "je-delete", "id": je["Id"], "docnum": je.get("DocNumber"), "date": je.get("TxnDate"),
                 "pre_delete_lines": je.get("Line"), "reason": reason, "tid": tid, "agent": AGENT})


def verify(jid, want_total, n):
    je = q.je_get(jid)
    tot = round(sum(l["Amount"] for l in je["Line"] if l["JournalEntryLineDetail"]["PostingType"] == "Debit"), 2)
    return tot == want_total and len(je["Line"]) == n


def post_store_day(st, d, s, replace=False):
    """Map daily_file(d, s) and post it. Returns status string."""
    key, rec = d.isoformat(), st["days"].setdefault(d.isoformat(), {}).setdefault(s, {})
    doc = "BRAVO-%s-%s" % (s, d.strftime("%Y%m%d"))
    lines, delta = build(daily_file(d, s), s, d, d)
    rec.update({"delta": delta, "file": os.path.basename(daily_file(d, s))})
    if not lines:
        rec.update({"status": "no-activity", "lines": []}); return "no-activity"
    if RENDER:
        log("RENDER %s %s DR %.2f, %d lines, delta %+.2f" % (doc, key, sum(l.get("debit", 0) for l in lines), len(lines), delta))
        for l in lines:
            log("    %-22s %12.2f %12.2f  %s" % (l["account"], l.get("debit", 0), l.get("credit", 0), l["desc"]))
        return "render"
    prior = existing_doc(d, doc)
    if prior and not replace:
        rec.update({"status": "posted", "je_id": prior[0]["Id"], "lines": rec.get("lines") or lines, "note": "found in QBO"})
        return "already"
    if prior and replace:
        if by_account(rec.get("lines", [])) == by_account(lines):
            return "unchanged"
        for p in prior:
            je_delete(p["Id"], "Bravo GL for %s %s changed after posting (month proof); replaced from re-pulled file" % (s, key))
    memo = ("Bravo Post-to-Accounting Consolidated GL %s %d/%d/%d (one day), source Bravo Data Extraction/output/daily_gl/%s. "
            "Daily posting per Joshua 2026-10-21; same mapping as the monthly BRAVO-%s entries. Revenue is NET of sales tax."
            % (NAME[s], d.month, d.day, d.year, os.path.basename(daily_file(d, s)), s))
    if delta:
        memo += " Bravo's own %s GL is out of balance by %+.2f this day (inter-store item movement); carried in Bravo POS Clearing, no P&L effect." % (s, delta)
    je, tot = je_post(d, s, doc, lines, memo)
    rec.update({"status": "posted", "je_id": je["Id"], "lines": lines, "total": tot, "posted_at": now().isoformat(timespec="seconds")})
    save_state(st)
    rec["verified"] = verify(je["Id"], tot, len(lines))
    if not rec["verified"]:
        ledger("The daily Bravo entry %s did not read back from QuickBooks as posted; check it before the month proof." % doc)
    return "replaced" if prior else "posted"


# ---------------------------------------------------------------- month proof
def prove(st, ym):
    y, m = map(int, ym.split("-"))
    d0, d1 = dt.date(y, m, 1), dt.date(y, m, calendar.monthrange(y, m)[1])
    if any(not os.path.exists(gl_out(d1, s)) or dt.datetime.fromtimestamp(os.path.getmtime(gl_out(d1, s))).date() <= d1 for s in STORES):
        if now().date() >= d1 + dt.timedelta(days=3) and not NO_PULL:
            bravo_pull("post-to-accounting-gl", "%s..%s" % (d0, d1), STORES, "month-" + ym)
        if any(not os.path.exists(gl_out(d1, s)) for s in STORES):
            log("prove %s: month GL files not on disk yet" % ym); return None
    bad = []
    for s in STORES:
        mlines, _ = build(gl_out(d1, s), s, d0, d1)
        want = by_account(mlines)
        got = defaultdict(float)
        for k, v in st["days"].items():
            if k.startswith(ym) and v.get(s, {}).get("status") == "posted":
                for a, amt in by_account(v[s]["lines"]).items():
                    got[a] += amt
        got = {a: round(v, 2) for a, v in got.items()}
        diff = {a: round(want.get(a, 0) - got.get(a, 0), 2) for a in set(want) | set(got) if abs(want.get(a, 0) - got.get(a, 0)) >= 0.01}
        log("prove %s %s: %s" % (ym, s, "TIES" if not diff else "DIFF %s" % diff))
        if diff:
            bad.append((s, diff))
    return bad


def reprove(st, ym, bad):
    y, m = map(int, ym.split("-"))
    days = [dt.date(y, m, i) for i in range(1, calendar.monthrange(y, m)[1] + 1)]
    for s, _ in bad:
        for d in days:
            if pull_day(d, [s])[s] is None:
                r = post_store_day(st, d, s, replace=True)
                log("reprove %s %s: %s" % (s, d, r)); save_state(st)


# ---------------------------------------------------------------- main
def main():
    st = load_state()
    if "--mark-posted-through" in ARGS:        # used by dailygl_restart.sh after a verified post-v2 result
        st["posted_through"] = arg("--mark-posted-through"); save_state(st); print("posted_through", st["posted_through"]); return
    if "--check" in ARGS:                      # cross-check: one Bravo range GL vs the sum of posted dailies
        a0, a1 = [dt.date.fromisoformat(x) for x in arg("--check").split("..")]
        chk = os.path.join(DAILY, "_check"); os.makedirs(chk, exist_ok=True)
        if not NO_PULL:
            stash = {s: gl_out(a1, s) + ".stash-dailygl" for s in STORES if os.path.exists(gl_out(a1, s))}
            for s, sp in stash.items(): os.replace(gl_out(a1, s), sp)
            for s in STORES:
                bravo_pull("post-to-accounting-gl", "%s..%s" % (a0, a1), [s], "check-" + s)
                if os.path.exists(gl_out(a1, s)):
                    os.replace(gl_out(a1, s), os.path.join(chk, "%s..%s_%s.csv" % (a0, a1, s)))
            for s, sp in stash.items(): os.replace(sp, gl_out(a1, s))
        allok = True
        for s in STORES:
            want = by_account(build(os.path.join(chk, "%s..%s_%s.csv" % (a0, a1, s)), s, a0, a1)[0])
            got = defaultdict(float)
            for k, v in st["days"].items():
                if a0.isoformat() <= k <= a1.isoformat() and v.get(s, {}).get("status") == "posted":
                    for a, amt in by_account(v[s]["lines"]).items(): got[a] += amt
            diff = {a: round(want.get(a, 0) - got.get(a, 0), 2) for a in set(want) | set(got) if abs(want.get(a, 0) - got.get(a, 0)) >= 0.01}
            allok &= not diff
            print("CHECK %s %s..%s: %s" % (s, a0, a1, "TIES to the cent" if not diff else "DIFF %s" % diff))
        print("CHECK RESULT", "ALL TIE" if allok else "DIFFERENCES"); return
    if "--probe" in ARGS:                      # read-only: QBO identity, store classes, mapped accounts
        print("company:", q.whoami() if hasattr(q, "whoami") else "?")
        for s in STORES:
            c = store_class(s); print("class", s, c and (c["Id"], c["Name"]))
        for a in ORDER + ["Bravo POS Clearing"]:
            try:
                x = acct(a); print("account", a, x["Id"], x.get("FullyQualifiedName"))
            except Exception as e:             # noqa: BLE001
                print("account", a, "ERROR", e)
        return
    if "--prove" in ARGS:
        ym = arg("--prove"); bad = prove(st, ym)
        if bad and not RENDER:
            reprove(st, ym, bad); bad = prove(st, ym)
        if bad == []:
            st["proven"][ym] = now().isoformat(timespec="seconds"); save_state(st)
        print("PROVE", ym, "OK" if bad == [] else bad); return
    t = now()
    if t.day == 1 and dt.time(5, 45) <= t.time() <= dt.time(7, 30):
        log("1st-of-month 05:45-07:30 belongs to eom-bravo-gl-export — exit"); return
    until = arg("--until") or ("03:50" if t.hour < 4 else "19:45")   # daytime catch-up stops before the 20:30 jewelry pull
    stop = dt.datetime.combine(t.date(), dt.time(*map(int, until.split(":"))), ET) if until else None
    yday = t.date() - dt.timedelta(days=1)
    only = arg("--day")
    days = [dt.date.fromisoformat(only)] if only else [START + dt.timedelta(days=i) for i in range((yday - START).days + 1)]
    pending = []
    for d in days:
        rec = st["days"].get(d.isoformat(), {})
        todo = [s for s in open_stores(d) if rec.get(s, {}).get("status") not in ("posted", "no-activity")
                and rec.get(s, {}).get("tries", 0) < MAX_TRIES + 6]
        if todo:
            pending.append((d, todo))
    log("pending days: %s" % ", ".join("%s(%s)" % (d, ",".join(s)) for d, s in pending) if pending else "nothing pending")
    retrying = any(st["days"].get(d.isoformat(), {}).get(s, {}).get("tries", 0) for d, todo in pending for s in todo)
    if pending and not NO_PULL and (retrying or st.get("posted_through", "") < pending[-1][0].isoformat()):
        pstores = [s for s in STORES if any(s in todo for _, todo in pending)]
        cells = bravo_pull("post-to-accounting-post-v2", "%s..%s" % (pending[0][0], pending[-1][0]), pstores, "post")
        ok = True
        for s in pstores:
            c = cells.get(s, {})
            if c.get("status") != "success":
                ok = False
                log("post-v2 %s: %s %s" % (s, c.get("status"), c.get("error", "")[:160]))
        if ok and not RENDER:
            st["posted_through"] = pending[-1][0].isoformat(); save_state(st)
    summary = []
    for d, todo in pending:
        if stop and now() >= stop:
            log("deadline %s reached — remaining days next run" % until); break
        res = {s: None for s in todo} if NO_PULL else pull_day(d, todo)
        for s in todo:
            rec = st["days"].setdefault(d.isoformat(), {}).setdefault(s, {})
            err = res.get(s)
            if err is None and os.path.exists(daily_file(d, s)):
                try:
                    r = post_store_day(st, d, s)
                    summary.append("%s %s %s" % (d, s, r))
                except Exception as e:                       # noqa: BLE001
                    err = "post: %s" % str(e)[:200]
                    if "401" in err or "invalid_grant" in err:
                        ledger("QuickBooks refused the connection while posting the daily Bravo entries; it needs to be re-authorized once.", "yes, re-authorize QuickBooks for the API app")
            elif err is None:
                err = "daily file missing"
            if err and "Could not select store" in err:
                # Bravo's GL store list only offers stores with GL activity in the date range; two failed selects on a
                # one-day pull = no activity that day (proven 2026-10-21: HAR/LEX 10/20 failed this way and the 10/1-10/20
                # range GL tied to the sum of the dailies to the cent). The month proof re-pulls if this was ever wrong.
                rec.update({"status": "no-activity", "lines": [], "note": "store not offered by Bravo GL for this day"})
                summary.append("%s %s no-activity (not offered by Bravo GL)" % (d, s)); err = None
            if err:
                rec["tries"] = rec.get("tries", 0) + 1; rec["last_error"] = err
                summary.append("%s %s ERROR %s" % (d, s, err))
                if rec["tries"] == MAX_TRIES:
                    ledger("Daily Bravo posting for %s %s has failed %d runs in a row (%s); it keeps retrying each night." % (NAME[s], d, MAX_TRIES, err[:120]))
            save_state(st)
    # month proof for any closed month since START not yet proven
    m = START.replace(day=1)
    while (m.year, m.month) < (t.year, t.month):
        ym = "%04d-%02d" % (m.year, m.month)
        if ym not in st.get("proven", {}) and t.date() >= dt.date(t.year, t.month, 2) and not only:
            bad = prove(st, ym)
            if bad and not RENDER:
                reprove(st, ym, bad); bad = prove(st, ym)
            if bad == []:
                st.setdefault("proven", {})[ym] = now().isoformat(timespec="seconds"); save_state(st)
            elif bad:
                st.setdefault("prove_fail", {})[ym] = st.get("prove_fail", {}).get(ym, 0) + 1; save_state(st)
                if st["prove_fail"][ym] == 3:
                    ledger("The %s daily Bravo entries do not add up to Bravo's monthly ledger for %s after re-pulling; nothing was forced." % (ym, ", ".join(NAME[s] for s, _ in bad)))
        m = (m.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    write_status(st, summary)


def write_status(st, summary):
    if RENDER:
        for x in summary: log(x)
        return
    posted = sum(1 for v in st["days"].values() for r in v.values() if r.get("status") == "posted")
    last = max((k for k, v in st["days"].items() if any(r.get("status") in ("posted", "no-activity") for r in v.values())), default="none")
    errs = ["%s %s: %s (tries %d)" % (k, s, r.get("last_error"), r.get("tries", 0)) for k, v in sorted(st["days"].items())
            for s, r in v.items() if r.get("status") not in ("posted", "no-activity")]
    txt = ["# Daily Bravo -> QuickBooks — status", "", "Updated %s" % now().strftime("%Y-%m-%d %H:%M ET"),
           "", "- Store-day entries posted: %d (from %s)" % (posted, START), "- Newest day posted: %s" % last,
           "- Months proven against Bravo's monthly ledger: %s" % (", ".join(sorted(st.get("proven", {}))) or "none yet"),
           "", "## Last run", ""] + ["- " + x for x in summary or ["nothing to do"]] + ["", "## Open", ""] + (["- " + e for e in errs] or ["- none"])
    os.makedirs(STATE_DIR, exist_ok=True)
    open(STATUS_F, "w").write("\n".join(txt) + "\n")


if __name__ == "__main__":
    main()
