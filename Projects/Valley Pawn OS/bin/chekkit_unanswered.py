#!/usr/bin/env python3
"""chekkit_unanswered.py morning|eod [--render] [--send] [--day YYYY-MM-DD]
                         audit FROM TO                    (read-only matcher check, prints last-4 only)

Native replacement (Mac-first wave 1, 2026-10-08) for TWO Cowork tasks that read Chekkit's
"Unanswered Message Alert" emails out of Gmail:
  morning = `chekkit-unanswered-alert`        08:00 Mon-Sat. YESTERDAY's in-hours misses ->
            one DM per store employee (stores with 1+) + ONE summary post in #chekkit-messages-missed.
  eod     = `chekkit-unanswered-eod-followup` 19:00 Mon-Sat. TODAY's in-hours misses -> was each one
            answered later (staff reply / customer self-closed) or still open at close -> ONE post in the
            same channel (C0B1PEW0C30). Never DMs anyone.

Where the misses come from: Chekkit's own "Unanswered Message Alert" emails — the exact list the SKILL
counted — read natively from Apple Mail's Envelope Index + .emlx (read-only, the AI responder's method), not
from Gmail. (An API-only rebuild was tried first, 2026-10-08: over 9/22-10/7 it found ~4x more "10-minute
gaps" than Chekkit ever alerted on, so Chekkit's alert rule is not reproducible from the message log.)
Freshness gate: if Apple Mail has received nothing at all in the last 3 hours (Mail not syncing), the run
stops with a ledger row instead of posting a false all-clear. Then the SKILL's own filters, unchanged:
  * message time = email received - 10 min (ET); skip conversation-enders (fixed list + tapbacks/emoji-only;
    anything short and unclear is asked of Claude once via vp_ai and cached) and empty-body alerts;
    a location that is not one of the five stores is skipped
  * OPEN-HOURS filter: CUL/ROA Mon-Fri 10-18, Sat 10-17; WAY/HAR/LEX Mon, Tue, Thu, Fri, Sat 10-18;
    Wednesday = CUL + ROA only (ROA from 2026-09-30); Sunday = none
  * morning: DM recipients from hr/ROSTER.json (roster_write.py --check must say ok), department == store,
    slack_id set, never Joshua/Preston/Corporate Support/Marketing. Roster not ok = ledger row, no DMs,
    summary still posts.
EOD: each flagged alert is matched to its Chekkit conversation through the API (GET only; same store, a
customer message with the same text 6-16 min before the email) — this replaces the dashboard search.
EOD "answered" = a staff (non-automated) business message after the flagged text, or the customer's own
later messages are all sign-offs (self-closed). Automated texts do NOT count as answered (9/29 run).

Formats are the ones the live posts show (parity_check.py against the channel). The morning post keeps the
look the Slack connector gave it (headers in _italics_); the EOD post keeps the outbox look (*bold*).

--render  prints exactly what would be posted/DM'd (customer names masked to …last4 — logs never carry
          names or numbers) and sends nothing. --send is required to publish. All-or-nothing: any store
          whose read fails = nothing sent, one FAILURE_LEDGER row. Duplicate guard: a state file per date
          plus a channel check for the same header.
"""
import datetime as dt, json, os, re, subprocess, sys, threading, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chekkit_api as ck  # noqa: E402

ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
OS_DIR = os.path.dirname(HERE)
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE_DIR = os.path.join(OS_DIR, "fleet", "state", "chekkit_unanswered")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
CH = "C0B1PEW0C30"
NEVER_DM = {"U03BB52MDSA", "U03BWMEM9GR"}          # Joshua, Preston
ORDER = ["CUL", "WAY", "HAR", "LEX", "ROA"]         # the post's store order
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
MISS_MIN = 10
ENDERS = {"thanks", "thank you", "thank u", "thankyou", "thanks so much", "thank you so much", "thanks again",
          "thank you very much", "ty", "thx", "tysm", "ok", "okay", "k", "kk", "okk", "oki", "okey", "sounds good",
          "got it", "bye", "goodbye", "good bye", "bye bye", "have a good day", "have a great day", "have a nice day",
          "you too", "appreciate it", "i appreciate it", "no problem", "np", "will do", "perfect", "cool", "great",
          "stop", "start", "unstop", "alright", "all right", "ok thanks", "ok thank you", "okay thanks",
          "okay thank you", "ok no problem", "okay no problem", "ok sounds good", "ok cool", "ok great",
          "ok perfect", "ok will do", "thanks bye", "ok bye", "awesome", "awesome thanks", "great thanks",
          "perfect thanks", "cool thanks", "sounds good thanks", "sounds great", "got it thanks", "ok got it"}
TAPBACK = re.compile(r"^(liked|loved|laughed at|emphasized|disliked|questioned|reacted\s+\S+\s+to|\S{1,4}\s+to)\s+[“\"]", re.I)


def ledger(task, sentence, needs="no"):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), task, sentence, needs))


# ------------------------------------------------------------------ store calendar
def hours(code, day):
    """(open, close) local times for that store on that date, or None if closed."""
    wd = day.weekday()  # Mon 0 .. Sun 6
    if wd == 6:
        return None
    if wd == 2:
        if code == "CUL" or (code == "ROA" and day >= dt.date(2026, 9, 30)):
            return (dt.time(10), dt.time(18))
        return None
    if wd == 5 and code in ("CUL", "ROA"):
        return (dt.time(10), dt.time(17))
    return (dt.time(10), dt.time(18))


def in_hours(code, t_et):
    h = hours(code, t_et.date())
    return bool(h) and h[0] <= t_et.time() < h[1]


# ------------------------------------------------------------------ text rules
_cache = None


def cache():
    global _cache
    if _cache is None:
        p = os.path.join(STATE_DIR, "ender_cache.json")
        try:
            _cache = json.load(open(p))
        except Exception:
            _cache = {}
    return _cache


def save_cache():
    if _cache is not None:
        os.makedirs(STATE_DIR, exist_ok=True)
        json.dump(_cache, open(os.path.join(STATE_DIR, "ender_cache.json"), "w"), indent=0)


def norm(t):
    x = re.sub(r"[^\w\s']", " ", (t or "").lower()).replace("'", "")
    return re.sub(r"\s+", " ", x).strip()


def kind(m):
    """'empty' | 'ender' | 'real' for one customer message (the SKILL's skip rules)."""
    t = (m.get("text") or "").strip()
    if not t:
        return "empty"
    if TAPBACK.match(t):
        return "ender"
    x = norm(t)
    if not x or not re.search(r"[a-z0-9]", x):           # emoji / punctuation only
        return "ender"
    if x in ENDERS:
        return "ender"
    words = x.split()
    if len(words) <= 6 and not re.search(r"\?|\d", t):
        c = cache()
        key = x
        if key not in c:
            try:
                import vp_ai
                a = vp_ai.ask("A customer texted a pawn shop: \"%s\"\nIs this ONLY a conversation-ender that needs no reply "
                              "(thanks/ok/bye/sign-off/acknowledgement/emoji), or a genuine question/request/complaint "
                              "that warranted a reply? Answer with exactly one word: ENDER or REAL." % t,
                              max_tokens=5).strip().upper()
                c[key] = "ender" if a.startswith("ENDER") else "real"
            except Exception:
                return "real"                                # unsure = count it, do not cache
        return c[key]
    return "real"


# ------------------------------------------------------------------ Chekkit reads (complete or raise)
class Store:
    def __init__(self, code):
        self.code, self.lock, self.last = code, threading.Lock(), 0.0

    def get(self, path):
        with self.lock:
            w = 1.2 - (time.time() - self.last)          # <= 50/min, leaves room for the AI responder
            if w > 0:
                time.sleep(w)
            self.last = time.time()
        return ck.get(self.code, path, retries=3)

    def threads(self, since_utc, max_pages=200):
        out, before, seen = [], None, set()
        for _ in range(max_pages):
            b = self.get("/v1/conversations" + ("?before=" + before if before else ""))
            convs = b.get("conversations") or []
            reached = False
            for c in convs:
                last = ck.ts(c.get("lastMessageAt"))
                if last and last < since_utc:
                    reached = True; continue
                if c.get("id") not in seen:
                    seen.add(c.get("id")); out.append(c)
            nb = b.get("nextBefore")
            if reached or not convs or not nb:
                break
            if nb == before:
                raise RuntimeError("conversation paging stalled")
            before = nb
        else:
            raise RuntimeError("conversation list did not reach the start")
        res = []
        for c in out:
            b = self.get("/v1/conversations/%s/messages" % c["id"]) or {}
            ms = b.get("messages")
            if ms is None:
                raise RuntimeError("messages unreadable")
            ms = sorted(ms, key=lambda m: ck.ts(m.get("createdAt")) or dt.datetime.min.replace(tzinfo=UTC))
            res.append((c, ms))
        return res


def read_all(since_utc, only=None):
    """{code: [(conv, msgs)]} for every store; raises if any store cannot be read completely."""
    out, errs = {}, {}

    def run(code):
        try:
            out[code] = Store(code).threads(since_utc)
        except Exception as e:  # noqa: BLE001
            errs[code] = "%s: %s" % (type(e).__name__, str(e)[:80])
    th = [threading.Thread(target=run, args=(c,)) for c in (only or ORDER)]
    [t.start() for t in th]
    [t.join() for t in th]
    if errs:
        raise RuntimeError("; ".join("%s %s" % kv for kv in sorted(errs.items())))
    return out


# ------------------------------------------------------------------ the alert emails (Apple Mail, read-only)
STORE_ALIASES = {"culpeper": "CUL", "harrisonburg": "HAR", "lexington": "LEX", "roanoke": "ROA", "waynesboro": "WAY"}
ALERT_RE = re.compile(r"(?:(?P<who>.{1,90}?) )?said (?:\d+|a few|an?) (?:minutes?|hours?|seconds?) ago: ?(?P<msg>.*?) ?Sent to Valley Pawn ?- ?(?P<store>[A-Za-z]+)", re.S)
PHONE_RE = re.compile(r"\((\d{3})\) (\d{3}) - (\d{4})")


def mail_index():
    import glob
    envs = glob.glob(os.path.expanduser("~/Library/Mail/V*/MailData/Envelope Index"))
    if not envs:
        raise RuntimeError("Apple Mail index not found")
    return envs[0]


def mail_fresh(hours=3):
    import sqlite3
    c = sqlite3.connect("file:%s?mode=ro" % mail_index().replace(" ", "%20"), uri=True)
    newest = c.execute("select max(date_received) from messages").fetchone()[0] or 0
    return time.time() - newest < hours * 3600


def mail_bodies(subject_like, start_et, end_et):
    """[(received ET, subject, plain text, gid)] for distinct support@chekkit.io emails whose subject is LIKE
    subject_like, received in [start_et, end_et). Read-only (Envelope Index + one walk for the .emlx files)."""
    import email, html, sqlite3
    from email import policy
    env = mail_index()
    c = sqlite3.connect("file:%s?mode=ro" % env.replace(" ", "%20"), uri=True)
    rows = list(c.execute(
        "select m.ROWID, s.subject, m.date_received, coalesce(m.global_message_id, m.message_id, m.ROWID) "
        "from messages m left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender "
        "where lower(a.address) like '%support@chekkit.io%' and s.subject like ? "
        "and m.date_received >= ? and m.date_received < ? order by m.date_received asc",
        (subject_like, int(start_et.timestamp()), int(end_et.timestamp()))))
    base = os.path.dirname(os.path.dirname(env))
    want = {str(r[0]) for r in rows}
    paths = {}
    if want:
        for root, _dirs, files in os.walk(base):
            for f in files:
                if f.endswith(".emlx") and f.split(".")[0] in want:
                    paths.setdefault(int(f.split(".")[0]), []).append(os.path.join(root, f))
    seen, out = set(), []
    for rowid, subj, ts, gid in rows:
        hits = sorted(paths.get(rowid, []), key=lambda x: ".partial." in x)
        if gid in seen or not hits:
            continue
        seen.add(gid)
        raw = open(hits[0], "rb").read()
        raw = raw[raw.index(b"\n") + 1:]
        msg = email.message_from_bytes(raw, policy=policy.default)
        part = msg.get_body(preferencelist=("plain", "html"))
        txt = part.get_content() if part else ""
        txt = re.sub(r"(?is)<(style|script|head)[^>]*>.*?</\1>", " ", txt)
        txt = re.sub(r"<[^>]+>", " ", txt)
        txt = html.unescape(re.sub(r"\s+", " ", txt.replace("|", " ")))
        out.append((dt.datetime.fromtimestamp(ts, ET), subj or "", txt, str(gid)))
    return out


def alerts(start_et, end_et):
    """Every distinct Unanswered Message Alert email RECEIVED in [start_et, end_et) — as dicts with
    store, t (message time ET = received - 10 min), received, text, name, phone, kind."""
    import email, glob, html, sqlite3
    from email import policy
    env = mail_index()
    c = sqlite3.connect("file:%s?mode=ro" % env.replace(" ", "%20"), uri=True)
    rows = list(c.execute(
        "select m.ROWID, s.subject, m.date_received, coalesce(m.global_message_id, m.message_id, m.ROWID) "
        "from messages m left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender "
        "where lower(a.address) like '%support@chekkit.io%' and s.subject like '%Unanswered Message Alert%' "
        "and m.date_received >= ? and m.date_received < ? order by m.date_received asc",
        (int(start_et.timestamp()), int(end_et.timestamp()))))
    base = os.path.dirname(os.path.dirname(env))
    want = {str(r[0]) for r in rows}
    paths = {}
    if want:                                 # ONE walk of the mail store (a recursive glob per email took minutes each)
        for root, _dirs, files in os.walk(base):
            for f in files:
                if f.endswith(".emlx"):
                    rid = f.split(".")[0]
                    if rid in want:
                        paths.setdefault(int(rid), []).append(os.path.join(root, f))
    seen, out, unread = set(), [], 0
    for rowid, subj, ts, gid in rows:
        if gid in seen:
            continue
        hits = sorted(paths.get(rowid, []), key=lambda x: ".partial." in x)
        if not hits:
            continue                         # another copy of the same email may still have its body
        seen.add(gid)
        raw = open(hits[0], "rb").read()
        raw = raw[raw.index(b"\n") + 1:]
        msg = email.message_from_bytes(raw, policy=policy.default)
        part = msg.get_body(preferencelist=("plain", "html"))
        txt = part.get_content() if part else ""
        txt = re.sub(r"(?is)<(style|script|head)[^>]*>.*?</\1>", " ", txt)
        txt = re.sub(r"<[^>]+>", " ", txt)
        txt = html.unescape(re.sub(r"\s+", " ", txt.replace("|", " ")))
        m = list(ALERT_RE.finditer(txt))
        if not m:
            unread += 1
            continue
        m = m[-1]
        code = STORE_ALIASES.get(m.group("store").lower())
        who = (m.group("who") or "").strip()
        ph = PHONE_RE.search(who)
        name = who[:ph.start()].rstrip(", ").strip() if ph else ("" if who.lower().startswith("a customer") else who)
        sn = re.sub(r"^.*Unanswered Message Alert:?\s*", "", subj or "").strip()
        if not name and sn and not PHONE_RE.search(sn):
            name = sn
        rec = dt.datetime.fromtimestamp(ts, ET)
        out.append({"store": code, "received": rec, "t": rec - dt.timedelta(minutes=MISS_MIN),
                    "text": m.group("msg").strip(), "name": name,
                    "phone": "".join(ph.groups()) if ph else "", "id": str(gid)})
    if unread:
        print("WARN %d alert email(s) could not be parsed" % unread, file=sys.stderr)
    return out


def counted_alerts(al):
    """The SKILL's tally: real (not a sign-off, not empty), in that store's open hours, and ONE per customer
    message — Chekkit sometimes sends two alerts for the same text a minute apart (9/25 LEX: the live post
    counted it once)."""
    rows = []
    for a in al:
        if not a["store"]:
            continue
        key = (a["store"], a["phone"] or a["name"], norm(a["text"]))
        if any((r["store"], r["phone"] or r["name"], norm(r["text"])) == key and
               abs((a["received"] - r["received"]).total_seconds()) <= 900 for r in rows):
            a["kind"], a["in_hours"] = "duplicate", in_hours(a["store"], a["t"])
            continue
        k = kind({"text": a["text"]})
        a["kind"] = k
        a["in_hours"] = in_hours(a["store"], a["t"])
        if k == "real" and a["in_hours"]:
            rows.append(a)
    return rows


def match_thread(a, threads):
    """The (conv, msgs, i) of the customer message an alert is about, or None."""
    want = norm(a["text"])[:60]
    best = None
    for c, ms in threads:
        if a["phone"] and l4(c) != a["phone"][-4:]:
            continue
        for i, m in enumerate(ms):
            if m.get("sender") != "customer":
                continue
            t = ck.ts(m.get("createdAt"))
            if not t:
                continue
            gap = (a["received"] - t.astimezone(ET)).total_seconds() / 60.0
            if 6 <= gap <= 16 and (not want or norm(m.get("text"))[:60] == want):
                if best is None or abs(gap - 10) < best[3]:
                    best = (c, ms, i, abs(gap - 10))
    return best[:3] if best else None



def l4(c):
    d = "".join(ch for ch in str((c.get("customer") or {}).get("phone") or "") if ch.isdigit())
    return d[-4:] if len(d) >= 4 else "????"


def display_name(c):
    cu = c.get("customer") or {}
    n = (cu.get("name") or "").strip()
    if n:
        return n
    d = "".join(ch for ch in str(cu.get("phone") or "") if ch.isdigit())[-10:]
    return "(%s) %s-%s" % (d[:3], d[3:6], d[6:]) if len(d) == 10 else "a customer"


# ------------------------------------------------------------------ messages
def human_date(d):
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def morning_text(day, per):
    hdr = ":bar_chart: _Daily Response Summary — %s_ _(business hours only)_" % human_date(day)
    total = sum(per.values())
    if total == 0:
        return hdr + " — All clear! Every customer message sent during business hours was answered within 10 minutes yesterday. :tada:"
    lines = [hdr, ""] + ["• _%s:_ %d unanswered" % (NAMES[c], per.get(c, 0)) for c in ORDER]
    lines += ["_Total: %d message(s) across all stores yesterday_" % total]     # no blank line (live post)
    return "\n".join(lines)


def dm_text(code, day, n):
    what = "1 customer message" if n == 1 else "%d customer message(s)" % n
    return (":bar_chart: _Response check for %s — %s:_ %s sent during business hours went 10+ minutes without a "
            "response yesterday. Please make sure to check for new messages regularly so customers get fast replies!"
            % (NAMES[code], human_date(day), what))


AUTO_EXTRA = ("thanks for texting valley pawn", "is open monday", "we'll text you back shortly")


def staff_reply(m):
    """A real person answered: a business message with a staff name on it that is not an automated text
    (the 9/29 live run treated the "Thanks for texting ... we'll text you back shortly" greeting as automated)."""
    t = (m.get("text") or "").lower()
    return (m.get("sender") == "business" and bool(m.get("sentBy")) and not ck.is_automated(m)
            and not any(k in t for k in AUTO_EXTRA))


def eod_status(r, cutoff=None):
    """'staff' | 'self' | 'open' | 'unverified' for one flagged alert (r["match"] from match_thread).
    Only messages up to the cutoff (the run time, or 19:00 that day for a replay) count."""
    if not r.get("match"):
        return "unverified"
    c, ms, i = r["match"]
    cut = cutoff or r.get("cutoff")
    later = [m for m in ms[i + 1:] if not cut or (ck.ts(m.get("createdAt")) and ck.ts(m.get("createdAt")) <= cut)]
    if any(staff_reply(m) for m in later):
        return "staff"
    cust = [m for m in later if m.get("sender") == "customer"]
    if cust and all(kind(m) in ("ender", "empty") for m in cust) and any(kind(m) == "ender" for m in cust):
        return "self"
    return "open"


def who(r, mask):
    if mask:
        return "[customer …%s]" % ((r.get("phone") or "")[-4:] or (l4(r["match"][0]) if r.get("match") else "????"))
    if r.get("name"):
        return r["name"]
    if r.get("phone") and len(r["phone"]) == 10:
        p = r["phone"]
        return "(%s) %s-%s" % (p[:3], p[3:6], p[6:])
    return display_name(r["match"][0]) if r.get("match") else "a customer"


def eod_text(day, rows, now_et, mask):
    hdr = ":crescent_moon: *End-of-Day Follow-up — %s*" % human_date(day)
    if not rows:
        return hdr + " — No 10-minute misses were flagged at any store today — nothing to follow up on."
    lines = [hdr + " _(closes the loop on today's 10-minute misses)_", ""]
    still, unver = [], 0
    for c in ORDER:
        mine = [r for r in rows if r["store"] == c]
        st = [eod_status(r) for r in mine]
        z = st.count("open")
        unver += st.count("unverified")
        lines.append("• *%s:* %d flagged → %d answered, %d still unanswered"
                     % (NAMES[c], len(mine), st.count("staff") + st.count("self"), z))
        still += [r for r, x in zip(mine, st) if x == "open"]
    if still:
        lines += ["", ":warning: *Still unanswered at close:*"]
        for r in sorted(still, key=lambda r: r["t"]):
            hrs = max(1, int(round((now_et - r["t"]).total_seconds() / 3600.0)))
            lines.append("• %s — %s — flagged ~%d hr%s ago" % (NAMES[r["store"]], who(r, mask), hrs, "" if hrs == 1 else "s"))
    elif not unver:
        lines += ["", "Every customer message flagged this morning as a 10-minute miss was eventually answered "
                      "(or was a self-closed sign-off) by close. No stragglers today. :tada:"]
    if unver:
        lines += ["", "*%d unable to verify* (name/thread mismatch)" % unver]
    return "\n".join(lines)


# ------------------------------------------------------------------ roster + send
def recipients(code):
    ok = subprocess.run([sys.executable, os.path.join(HERE, "roster_write.py"), "--check"],
                        capture_output=True, text=True).stdout.strip().startswith("ok")
    if not ok:
        return None
    emps = json.load(open(ROSTER)).get("employees") or []
    return [e for e in emps if e.get("department") == NAMES[code] and e.get("slack_id")
            and e["slack_id"] not in NEVER_DM]


def state(name):
    os.makedirs(STATE_DIR, exist_ok=True)
    p = os.path.join(STATE_DIR, name)
    try:
        return p, json.load(open(p))
    except Exception:
        return p, {}


def post(channel, text):
    import vp_slack
    vp_slack.post(channel, text)


def already_posted(marker, hours=30):
    import vp_slack
    try:
        return vp_slack.has(CH, marker, hours)
    except SystemExit:
        return False


# ------------------------------------------------------------------ modes
def run(mode, day, render, send):
    task = "chekkit-unanswered-alert" if mode == "morning" else "chekkit-unanswered-eod-followup"
    start = dt.datetime.combine(day, dt.time(0), ET)
    end = start + dt.timedelta(days=1)
    try:
        if not mail_fresh():
            raise RuntimeError("Apple Mail has received nothing in 3 hours (not syncing)")
        rows = counted_alerts(alerts(start, end))
    except Exception as e:  # noqa: BLE001
        print("ALERT READ FAILED:", e)
        if send:
            ledger(task, "The unanswered-message check for %s could not read the alert emails on the Mac, so nothing was posted." % human_date(day),
                   "yes, open Apple Mail on the Mac so it syncs" if "syncing" in str(e) else "no")
        return 1
    save_cache()
    for r in rows:
        print("MISS %s %s …%s" % (r["store"], r["t"].strftime("%H:%M"), (r["phone"] or "????")[-4:]), file=sys.stderr)
    if mode == "morning":
        per = {c: sum(1 for r in rows if r["store"] == c) for c in ORDER}
        summary = morning_text(day, per)
        dms = []
        roster_ok = True
        for c in ORDER:
            if per[c]:
                rc = recipients(c)
                if rc is None:
                    roster_ok = False; continue
                dms += [(e["slack_id"], e.get("preferred") or e.get("name"), dm_text(c, day, per[c])) for e in rc]
        if render or not send:
            for uid, nm, txt in dms:
                print("=== DM %s (%s)\n%s" % (uid, (nm or "?").split()[0], txt))
            print("=== POST %s\n%s" % (CH, summary))
            if not roster_ok:
                print("NOTE roster check not ok: store DMs would be skipped and a ledger row written")
            return 0
        sp, st = state("%s-%s.json" % (mode, day))
        if not roster_ok:
            ledger(task, "Store message counts for %s were posted, but the staff list was out of date so no store DMs went out." % human_date(day))
        sent = set(st.get("dms", []))
        for uid, nm, txt in dms:
            if uid in sent:
                continue
            post(uid, txt); sent.add(uid); st["dms"] = sorted(sent); json.dump(st, open(sp, "w"))
        if not st.get("posted") and not already_posted("Daily Response Summary — %s" % human_date(day)):
            post(CH, summary)
        st["posted"] = True; json.dump(st, open(sp, "w"))
        print("SENT morning %s dms=%d" % (day, len(sent)))
        return 0
    # eod: match every flagged alert to its conversation (API, GET only), then classify
    ref = min(dt.datetime.now(ET), dt.datetime.combine(day, dt.time(19, 0), ET)) if day < dt.datetime.now(ET).date() else dt.datetime.now(ET)
    for r in rows:
        r["cutoff"] = ref
    if rows:
        try:
            threads = read_all(start.astimezone(UTC) - dt.timedelta(hours=1), only=sorted({r["store"] for r in rows}))
        except Exception as e:  # noqa: BLE001
            print("API READ FAILED:", e)
            if send:
                ledger(task, "The end-of-day follow-up for %s could not read the store conversations, so nothing was posted." % human_date(day))
            return 1
        for r in rows:
            r["match"] = match_thread(r, threads.get(r["store"], []))
            print("FLAG %s %s …%s -> %s" % (r["store"], r["t"].strftime("%H:%M"), (r["phone"] or "????")[-4:], eod_status(r)), file=sys.stderr)
            if "--explain" in sys.argv and r.get("match"):
                c0, ms0, i0 = r["match"]
                for m in ms0[i0 + 1:]:
                    if m.get("sender") == "business":       # our own outgoing texts only (never customer text)
                        t0 = ck.ts(m.get("createdAt"))
                        print("   biz +%dm by=%s auto=%s %r" % ((t0 - r["t"].astimezone(UTC)).total_seconds() // 60 if t0 else -1,
                              (m.get("sentBy") or "-").split()[0], ck.is_automated(m), (m.get("text") or "")[:70]), file=sys.stderr)
        save_cache()
    text = eod_text(day, rows, ref, mask=render or not send)
    if render or not send:
        print("=== POST %s\n%s" % (CH, text))
        return 0
    sp, st = state("%s-%s.json" % (mode, day))
    if st.get("posted") or already_posted("End-of-Day Follow-up — %s" % human_date(day)):
        print("already posted"); return 0
    post(CH, eod_text(day, rows, ref, mask=False))
    st["posted"] = True; json.dump(st, open(sp, "w"))
    print("SENT eod %s flagged=%d" % (day, len(rows)))
    return 0


def audit(frm, to):
    """Per alert email in the range: time, store, last-4, kind, hours; then the per-day counted totals."""
    start = dt.datetime.combine(frm, dt.time(0), ET)
    end = dt.datetime.combine(to + dt.timedelta(days=1), dt.time(0), ET)
    al = alerts(start, end)
    counted_alerts(al)
    save_cache()
    for a in al:
        print("ALERT recv %s msg~%s %s …%s kind=%s hours=%s" % (a["received"].strftime("%m-%d %H:%M"), a["t"].strftime("%H:%M"),
              a["store"], (a["phone"] or "none")[-4:], a.get("kind"), "in" if a.get("in_hours") else "out"))
    d = frm
    while d <= to:
        ds = [a for a in al if a["received"].date() == d and a.get("kind") == "real" and a.get("in_hours")]
        print("DAY %s %s counted=%s" % (d, d.strftime("%a"), {c: sum(1 for a in ds if a["store"] == c) for c in ORDER}))
        d += dt.timedelta(days=1)
    return 0


def main(a):
    if not a or a[0] not in ("morning", "eod", "audit"):
        sys.exit(__doc__)
    if a[0] == "audit":
        return audit(dt.date.fromisoformat(a[1]), dt.date.fromisoformat(a[2]))
    today = dt.datetime.now(ET).date()
    day = dt.date.fromisoformat(a[a.index("--day") + 1]) if "--day" in a else (
        today - dt.timedelta(days=1) if a[0] == "morning" else today)
    return run(a[0], day, "--render" in a, "--send" in a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
