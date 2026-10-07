#!/usr/bin/env python3
"""missed_call_report.py [--render] [--week YYYY-MM-DD] — native replacement for Cowork `missed-call-text-report`
(2026-10-06). Weekly DM to Joshua (Mondays, prior Mon-Sun): how many missed callers were texted, how many
replied, how fast the store answered, outcomes. Same format the Cowork task posted.

Why native: the Cowork task matched each text to its Chekkit conversation BY HAND in the website and ran
out of time (9/28-10/4 report never posted). The Chekkit API (read-only GETs, chekkit_api.py tokens) does
the matching in minutes.

Matching, per text (receipt line in fleet/receipts/missed-call-text.jsonl, target chekkit-webhook:<STORE>):
  1. pair the receipt with the agent's local log line "SENT <STORE> ...<last4>" (same store, within 2 min)
  2. list the store's conversations with activity since the period start (paginated, complete or abort)
  3. candidate = conversation whose customer phone ends in that last-4; the match is the automated
     "Hi, this is Valley Pawn in ..." message created within 3 min of the receipt (each message used once)
  4. no last-4 (or no hit): scan every conversation active after the text for that automated message
  A text whose automated message exists in NO conversation after a complete read is reported the way the
  Cowork task reported it ("sent but didn't create a conversation"). Any API read that fails or cannot be
  completed = nothing posted, one FAILURE_LEDGER row (all-or-nothing; SKILL step 3).

Metrics: replied = a customer message after our text (before the next missed-call text in that thread);
reply_min = our text -> first customer message; store_reply_min = first customer message -> first staff
(non-automated business) message, employee = its sentBy; STOP/unsubscribe = opt-out.
CSV fleet/missed_call_text_results.csv: rows appended, never a duplicate of date+store+text_time (counted
as a multiset, so two texts in the same minute stay two rows). --render writes nothing and sends nothing.
Logs: no customer names or phone numbers beyond last-4. READ-ONLY toward Chekkit (GET only).
"""
import argparse, csv, datetime as dt, json, os, re, sys, threading, time
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chekkit_api as ck  # noqa: E402

TASK = "missed-call-text-report"
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
FLEET = os.path.join(OS_DIR, "fleet")
RECEIPTS = os.path.join(FLEET, "receipts", "missed-call-text.jsonl")
CSV_PATH = os.path.join(FLEET, "missed_call_text_results.csv")
LEDGER = os.path.join(FLEET, "FAILURE_LEDGER.md")
RUNLOG = os.path.expanduser("~/Library/Logs/valleypawn/missed_call_text/run.log")
STATE = os.path.expanduser("~/Library/Logs/valleypawn/missed_call_report_state.json")
JOSHUA = "U03BB52MDSA"
HEADER = ["date", "store", "text_time", "replied", "reply_min", "store_reply_min", "employee", "outcome", "opt_out"]
ORDER = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
LIVE_SINCE = dt.date(2026, 9, 24)
OPENER = "hi, this is valley pawn in"
MATCH_SEC = 180
MAX_PAGES = 200
REPLY_WINDOW_H = 24          # a customer text more than a day after ours is not counted as a reply to it


class Incomplete(Exception):
    pass


def ledger(sentence, needs="no"):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence, needs))


def md(d):
    return "%d/%d" % (d.month, d.day)


def mins(a, b):
    return int(round((b - a).total_seconds() / 60.0))


# ------------------------------------------------------------------ inputs
def load_texts(start, end):
    """Receipts in [start, end) ET -> list of dicts (sorted), plus failed count by store."""
    texts, failed = [], Counter()
    for line in open(RECEIPTS):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        tgt = r.get("target") or ""
        if not tgt.startswith("chekkit-webhook:"):
            continue
        t = ck.ts(r.get("ts"))
        if not t:
            continue
        t = t.astimezone(ET)
        if not (start <= t < end):
            continue
        code = tgt.split(":", 1)[1]
        if r.get("ok") is False:
            failed[code] += 1
            continue
        texts.append({"store": code, "t": t})
    texts.sort(key=lambda x: x["t"])
    return texts, failed


def attach_last4(texts):
    """Pair each receipt with a 'SENT <STORE> ...<last4>' run.log line (same store, within 120 s)."""
    sent = []
    rx = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) SENT ([A-Z]{3}) \.*(\d{4})\b")
    try:
        for line in open(RUNLOG, errors="replace"):
            m = rx.match(line)
            if m:
                t = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET)
                sent.append({"t": t, "store": m.group(2), "l4": m.group(3), "used": False})
    except FileNotFoundError:
        pass
    for x in texts:
        best = None
        for s in sent:
            if s["used"] or s["store"] != x["store"]:
                continue
            d = abs((s["t"] - x["t"]).total_seconds())
            if d <= 120 and (best is None or d < best[0]):
                best = (d, s)
        x["l4"] = None
        if best:
            best[1]["used"] = True
            x["l4"] = best[1]["l4"]
    return texts


# ------------------------------------------------------------------ Chekkit reads (GET only)
class Store:
    def __init__(self, code):
        self.code = code
        self.lock = threading.Lock()
        self.last_call = 0.0
        self.convs = []
        self.msg_cache = {}

    def get(self, path):
        with self.lock:
            wait = 1.05 - (time.time() - self.last_call)
            if wait > 0:
                time.sleep(wait)
            self.last_call = time.time()
        return ck.get(self.code, path, retries=3)

    def list_since(self, since_utc):
        before, pages, out, seen = None, 0, [], set()
        while True:
            pages += 1
            if pages > MAX_PAGES:
                raise Incomplete("%s: conversation list did not reach the period start in %d pages" % (self.code, MAX_PAGES))
            b = self.get("/v1/conversations" + ("?before=" + before if before else ""))
            convs = b.get("conversations") or []
            reached = False
            for c in convs:
                last = ck.ts(c.get("lastMessageAt"))
                if last and last < since_utc:
                    reached = True
                    continue
                if c.get("id") in seen:
                    continue
                seen.add(c.get("id"))
                out.append(c)
            nb = b.get("nextBefore")
            if reached or not convs or not nb:
                break
            if nb == before:
                raise Incomplete("%s: conversation list paging stalled" % self.code)
            before = nb
        self.convs = out
        return out

    def messages(self, cid):
        if cid not in self.msg_cache:
            b = self.get("/v1/conversations/%s/messages" % cid) or {}
            ms = b.get("messages")
            if ms is None:
                raise Incomplete("%s: a conversation's messages could not be read" % self.code)
            ms = sorted(ms, key=lambda m: ck.ts(m.get("createdAt")) or dt.datetime.min.replace(tzinfo=UTC))
            self.msg_cache[cid] = ms
        return self.msg_cache[cid]


def is_opener(m):
    return m.get("sender") == "business" and (m.get("text") or "").strip().lower().startswith(OPENER)


def phone_l4(c):
    cust = c.get("customer") or {}
    d = "".join(ch for ch in str(cust.get("phone") or "") if ch.isdigit())
    return d[-4:] if len(d) >= 4 else None


def match_store(st, texts, since_utc):
    st.list_since(since_utc)
    used = set()

    def find(x, convs):
        best = None
        for c in convs:
            last = ck.ts(c.get("lastMessageAt"))
            if last and last < x["t"].astimezone(UTC) - dt.timedelta(minutes=5):
                continue
            for m in st.messages(c["id"]):
                if not is_opener(m) or (c["id"], m.get("id")) in used:
                    continue
                mt = ck.ts(m.get("createdAt"))
                if not mt:
                    continue
                d = abs((mt - x["t"]).total_seconds())
                if d <= MATCH_SEC and (best is None or d < best[0]):
                    best = (d, c, m)
        return best

    for x in texts:
        best = None
        if x.get("l4"):
            best = find(x, [c for c in st.convs if phone_l4(c) == x["l4"]])
        if not best:
            best = find(x, st.convs)
        if best:
            used.add((best[1]["id"], best[2].get("id")))
            x["conv"], x["opener"] = best[1], best[2]
        else:
            x["conv"] = x["opener"] = None
    for x in texts:
        if x["conv"]:
            x.update(analyse(st.messages(x["conv"]["id"]), x["opener"]))
        else:
            x.update({"replied": False, "status": "noconv"})


def later(msgs, c1t, opener):
    """Messages after the customer's first reply up to the next missed-call text (staff may answer after
    the 24 h reply window; that answer still belongs to this conversation)."""
    out = []
    for m in msgs:
        mt = ck.ts(m.get("createdAt"))
        if not mt or mt < c1t or m is opener:
            continue
        if is_opener(m):
            break
        out.append((mt, m))
    return out


TOPICS = [  # first match wins; deliberately coarse and non-identifying (no customer words are quoted)
    (r"\b(stop|unsubscribe)\b", None),
    (r"\b(pay(ment)?|interest|extend|extension|ticket|late|pick(ing)? up|redeem|loan|pawned)\b", "asked about a loan or payment"),
    (r"\b(gold|silver|jewel\w*|ring|chain|necklace|bracelet|scrap)\b", "asked about gold or jewelry"),
    (r"\b(gun|firearm|rifle|pistol|shotgun|ammo|transfer|muzzle)\b", "asked about firearms"),
    (r"\b(sell|selling|buy|buying|trade|price|worth|how much|offer|interested|do you (all |y'?all )?(have|take|buy|carry)|looking for)\b", "asked about buying or selling an item"),
    (r"\b(open|close|closed|hours|what time)\b", "asked about store hours"),
    (r"\b(call|calling|phone)\b", "asked for a call back"),
]


def topic(cmsgs):
    txt = " ".join((m.get("text") or "") for m in cmsgs).lower()
    for rx, label in TOPICS:
        if re.search(rx, txt):
            if label:
                return label
    if any(m.get("media") for m in cmsgs) and not txt.strip():
        return "sent photos"
    return "replied"


STOP_RX = re.compile(r"^\s*(stop|stop all|unsubscribe|end|quit|cancel|optout|opt out|stopall)\W*$", re.I)


def analyse(msgs, opener):
    t0 = ck.ts(opener.get("createdAt"))
    after = []
    for m in msgs:
        mt = ck.ts(m.get("createdAt"))
        if not mt or mt <= t0 or m is opener:
            continue
        if is_opener(m) or mt > t0 + dt.timedelta(hours=REPLY_WINDOW_H):
            break                         # the next missed-call text (or a day later) ends this episode
        after.append((mt, m))
    cust = [(mt, m) for mt, m in after if m.get("sender") == "customer" and ((m.get("text") or "").strip() or m.get("media"))]
    out = {"undelivered": (opener.get("status") or "").lower() in ("undelivered", "failed", "error") or bool(opener.get("errorCode"))}
    if not cust:
        out.update({"replied": False, "status": "undelivered" if out["undelivered"] else "noreply"})
        return out
    c1t, c1 = cust[0]
    out.update({"replied": True, "reply_min": max(0, mins(t0, c1t)), "c1t": c1t})
    out["opt_out"] = any(STOP_RX.match(m.get("text") or "") for _, m in cust)
    out["topic"] = topic([m for _, m in cust[:6]])
    staff = [(mt, m) for mt, m in later(msgs, c1t, opener) if mt >= c1t and m.get("sender") == "business" and not ck.is_automated(m)
             and not is_opener(m)]
    if staff:
        st_t, sm = staff[0]
        out.update({"store_min": max(0, mins(c1t, st_t)), "employee": (sm.get("sentBy") or "").strip(),
                    "next_morning": st_t.astimezone(ET).date() > c1t.astimezone(ET).date()})
    out["status"] = "optout" if out["opt_out"] else ("answered" if staff else "waiting")
    return out


# ------------------------------------------------------------------ results file
def csv_rows():
    if not os.path.isfile(CSV_PATH):
        return []
    return list(csv.DictReader(open(CSV_PATH, newline="")))


def to_row(x):
    o = {"date": x["t"].strftime("%Y-%m-%d"), "store": x["store"], "text_time": x["t"].strftime("%H:%M"),
         "replied": "yes" if x["replied"] else "no", "reply_min": "", "store_reply_min": "", "employee": "",
         "outcome": "", "opt_out": "no"}
    s = x["status"]
    if s == "noconv":
        o["outcome"] = "no Chekkit conversation found (send likely failed silently)"
    elif s == "undelivered":
        o["outcome"] = "undelivered"
    elif s == "noreply":
        o["outcome"] = "no reply"
    else:
        o["reply_min"] = str(x["reply_min"])
        if x.get("store_min") is not None:
            o["store_reply_min"] = str(x["store_min"])
            o["employee"] = x.get("employee", "")
        if s == "optout":
            o["outcome"], o["opt_out"] = "opted out (STOP)", "yes"
        elif s == "answered":
            o["outcome"] = "replied - store answered" + (" next morning" if x.get("next_morning") else "")
        else:
            o["outcome"] = "replied - awaiting store reply"
    return o


def new_rows(texts, existing):
    have = Counter((r["date"], r["store"], r["text_time"]) for r in existing)
    out = []
    for x in texts:
        r = to_row(x)
        k = (r["date"], r["store"], r["text_time"])
        if have[k] > 0:
            have[k] -= 1
            continue
        out.append(r)
    return out


def append_rows(rows):
    exists = os.path.isfile(CSV_PATH) and os.path.getsize(CSV_PATH) > 0
    with open(CSV_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def totals(rows, d0, d1):
    sel = [r for r in rows if d0.isoformat() <= r["date"] <= d1.isoformat()]
    return len(sel), sum(1 for r in sel if r["replied"] == "yes"), sum(1 for r in sel if r["opt_out"] == "yes")


# ------------------------------------------------------------------ message
def pct(a, b):
    return "%d%%" % round(100.0 * a / b) if b else "0%"


def dur(m):
    if m < 1:
        return "under 1 min"
    if m < 120:
        return "%d min" % m
    return "about %d hours" % round(m / 60.0)


def answer_text(x):
    if x.get("next_morning"):
        days = (x["c1t"] + dt.timedelta(minutes=x["store_min"])).astimezone(ET).date() - x["c1t"].astimezone(ET).date()
        return "the next morning" if days.days == 1 else "%d days later" % days.days
    return dur(x["store_min"])


def build_dm(start, texts, failed, rows_all):
    end_d = (start + dt.timedelta(days=6)).date()
    label = "Mon %s–Sun %s" % (md(start), md(end_d))
    n = len(texts)
    if n == 0 and not sum(failed.values()):
        return ("**Missed-call texts — %s: 0 texted.** No missed-call texts went out this week — expected only when "
                "stores are closed (Sunday all stores; Wednesday all but Culpeper and Roanoke)." % label)
    rep = [x for x in texts if x["replied"]]
    L = ["**Missed-call texts — %s: %d texted, %d replied (%s).**" % (label, n, len(rep), pct(len(rep), n))]
    none = []
    for code in ORDER:
        tx = [x for x in texts if x["store"] == code]
        if not tx:
            none.append(NAMES[code]); continue
        r = [x for x in tx if x["replied"]]
        line = "• %s — %d texted / %d replied" % (NAMES[code], len(tx), len(r))
        ans = [answer_text(x) for x in r if x.get("store_min") is not None]
        ans = [("next morning" if a == "the next morning" else a) for a in ans]
        wait = sum(1 for x in r if x["status"] == "waiting")
        if ans:
            shown = ans if len(ans) <= 6 else ans[:6] + ["+%d more" % (len(ans) - 6)]
            line += " / store answered in " + ", ".join(shown)
            if wait:
                line += "; %d still waiting" % wait
        elif wait:
            line += " / store hasn't answered yet"
        L.append(line)
    if none:
        L.append("• %s — none" % ", ".join(none))
    L.append("")
    conv = [x for x in rep]
    rank = {"waiting": 0, "answered": 1, "optout": 2}
    conv.sort(key=lambda x: (rank.get(x["status"], 3), -(x.get("store_min") or 0), x["t"]))
    if not conv:
        L.append("**Conversations** — none, nobody replied.")
    else:
        L.append("**Conversations**")
        for x in conv[:5]:
            if x["status"] == "optout":
                L.append("• %s — customer replied STOP, opted out" % NAMES[x["store"]])
                continue
            what = x.get("topic") or "replied"
            what = "customer " + what if what != "replied" else "customer replied"
            if x["status"] == "answered":
                at = answer_text(x)
                L.append("• %s — %s — store answered %s%s (%s)" % (NAMES[x["store"]], what, "" if x.get("next_morning") else "in ", at, x.get("employee") or "staff"))
            else:
                L.append("• %s — %s — still waiting on a store reply" % (NAMES[x["store"]], what))
        if len(conv) > 5:
            L.append("• …and %d more replies" % (len(conv) - 5))
    slow = [x for x in rep if x.get("store_min") is not None and (x["store_min"] > 15 or x.get("next_morning"))]
    if slow:
        L.append("")
        L.append('**Slow replies (text promises "within a few minutes")**')
        for x in sorted(slow, key=lambda x: -x["store_min"]):
            took = ("%s (%s)" % (answer_text(x), dur(x["store_min"]))) if x.get("next_morning") else (
                "%d minutes" % x["store_min"] if x["store_min"] < 120 else dur(x["store_min"]))
            L.append("• %s — %s (%s)" % (NAMES[x["store"]], took, x.get("employee") or "staff"))
    # running totals since 9/24 + change vs the prior week (from the results file)
    L.append("")
    t_n, t_r, t_o = totals(rows_all, LIVE_SINCE, end_d)
    p0 = (start - dt.timedelta(days=7)).date()
    p_n, p_r, _ = totals(rows_all, max(p0, LIVE_SINCE), p0 + dt.timedelta(days=6))
    plabel = ("%s–%s" % (md(max(p0, LIVE_SINCE)), md(p0 + dt.timedelta(days=6))))
    L.append("**Since 9/24:** %d texted, %d replied (%s), %d opt-out%s." % (t_n, t_r, pct(t_r, t_n), t_o, "" if t_o == 1 else "s"))
    if p_n:
        L.append("**vs prior week (%s):** %d texted vs %d, reply rate %s vs %s." % (plabel, n, p_n, pct(len(rep), n), pct(p_r, p_n)))
    L.append("")
    # last line: opt-outs and failed texts
    oo = Counter(NAMES[x["store"]] for x in texts if x["status"] == "optout")
    und = sum(1 for x in texts if x.get("undelivered"))
    noc = sum(1 for x in texts if x["status"] == "noconv")
    fl = sum(failed.values())
    parts = []
    if oo:
        k = sum(oo.values())
        parts.append("%d opt-out%s (%s)." % (k, "" if k == 1 else "s", ", ".join("%s %d" % (s, c) if c > 1 else s for s, c in oo.items())))
    else:
        parts.append("No opt-outs.")
    if und:
        parts.append("%d text%s showed as undelivered in the system." % (und, "" if und == 1 else "s"))
    if noc:
        parts.append("%d text%s sent but didn't create a conversation in Chekkit (%d of %d matched), so %s may not have reached the customer either."
                     % (noc, "" if noc == 1 else "s", len(texts) - noc, len(texts), "it" if noc == 1 else "they"))
    parts.append("%d failed text%s." % (fl, "" if fl == 1 else "s") if fl else "No failed texts.")
    if not oo and not und and not noc and not fl:
        parts = ["No opt-outs, no failed texts."]
    L.append(" ".join(parts))
    return "\n".join(L)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true", help="print the DM and match table; write and send nothing")
    ap.add_argument("--week", help="Monday (YYYY-MM-DD) that starts the period; default = last week")
    ap.add_argument("--force-day", action="store_true", help="run even if today is not Monday")
    a = ap.parse_args()
    now = dt.datetime.now(ET)
    if a.week:
        d0 = dt.date.fromisoformat(a.week)
    else:
        if now.weekday() != 0 and not (a.render or a.force_day):
            print("not Monday — nothing to do"); return 0
        d0 = now.date() - dt.timedelta(days=now.weekday() + 7)
    if d0.weekday() != 0:
        sys.exit("--week must be a Monday")
    start = dt.datetime.combine(d0, dt.time(0), ET)
    end = start + dt.timedelta(days=7)
    if end > now:
        sys.exit("period %s.. has not finished yet" % d0)
    label = "Mon %s–Sun %s" % (md(start), md(end - dt.timedelta(days=1)))
    marker = "Missed-call texts — " + label

    state = {}
    try:
        state = json.load(open(STATE))
    except Exception:
        pass
    if not a.render and d0.isoformat() in state.get("sent", {}):
        print("already sent for %s — nothing to do" % label); return 0

    texts, failed = load_texts(start, end)
    attach_last4(texts)
    by = defaultdict(list)
    for x in texts:
        by[x["store"]].append(x)
    errors = {}

    def work(code):
        try:
            match_store(Store(code), by[code], start.astimezone(UTC) - dt.timedelta(hours=1))
        except Exception as e:
            errors[code] = "%s: %s" % (type(e).__name__, str(e)[:160])

    th = [threading.Thread(target=work, args=(c,)) for c in by]
    for t in th:
        t.start()
    for t in th:
        t.join()

    print("period %s  texts=%d failed=%d  last4-paired=%d" % (label, len(texts), sum(failed.values()),
                                                              sum(1 for x in texts if x.get("l4"))))
    if errors:
        msg = ("Weekly missed-call texts report for %s not sent: the Chekkit read did not complete for %s (%s). "
               "Nothing posted; the next run retries." % (label, ", ".join(sorted(errors)), "; ".join(errors[k] for k in sorted(errors))))
        print("WITHHELD: " + msg)
        if not a.render:
            ledger(msg)
        return 2

    for x in texts:
        print("  %s %s %s ...%s  %-11s reply=%s store=%s %s" % (
            x["t"].strftime("%m-%d %H:%M"), x["store"], "matched" if x["conv"] else "NO-CONV ",
            x.get("l4") or "????", x["status"], x.get("reply_min", ""), x.get("store_min", ""), x.get("employee", "")))

    existing = csv_rows()
    add = new_rows(texts, existing)
    # how the API result compares with rows already in the file (hand-matched) for the same keys
    api_by = Counter((r["date"], r["store"], r["text_time"], r["replied"]) for r in map(to_row, texts))
    file_by = Counter((r["date"], r["store"], r["text_time"], r["replied"]) for r in existing
                      if start.date().isoformat() <= r["date"] <= (end.date() - dt.timedelta(days=1)).isoformat())
    diff = [(k, file_by[k], api_by[k]) for k in sorted(set(file_by) | set(api_by)) if file_by[k] and file_by[k] != api_by[k]]
    print("rows already in file for the period: %d; new rows to append: %d; file-vs-API replied disagreements: %d"
          % (sum(file_by.values()), len(add), len(diff)))
    for k, f, p in diff:
        print("   differs %s %s %s replied=%s  file=%d api=%d" % (k[0], k[1], k[2], k[3], f, p))

    # totals: this period from the API (source of record), earlier weeks from the results file
    p0, p1 = start.date().isoformat(), (end.date() - dt.timedelta(days=1)).isoformat()
    text = build_dm(start, texts, failed, [r for r in existing if not (p0 <= r["date"] <= p1)] + [to_row(x) for x in texts])
    print("\n----- DM -----\n" + text + "\n--------------")
    if a.render:
        return 0

    os.environ["VP_TASK"] = TASK
    import vp_slack
    ch = vp_slack.dm_channel(JOSHUA)
    try:   # the ops bot may lack im:history (missing_scope seen 2026-10-06) -> the local state file is the guard
        dup = vp_slack.has(ch, marker, 24 * 21)
    except SystemExit as e:
        print("duplicate guard: Slack history not readable (%s); relying on the local sent-state file" % e)
        dup = False
    if dup:
        print("duplicate guard: a report for %s is already in Joshua's DM" % label)
        if add:
            append_rows(add)
        state.setdefault("sent", {})[d0.isoformat()] = "found-existing"
        json.dump(state, open(STATE, "w"))
        return 0
    if add:
        append_rows(add)
    try:
        vp_slack.post(ch, text)
    except SystemExit as e:
        ledger("Weekly missed-call texts report for %s was built but the Slack DM did not go through (%s)." % (label, e))
        return 3
    state.setdefault("sent", {})[d0.isoformat()] = now.isoformat()
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(state, open(STATE, "w"))
    print("sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
