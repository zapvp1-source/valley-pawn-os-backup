#!/usr/bin/env python3
"""knowledge_harvest_monthly.py [--render] [--asof YYYY-MM-DD] [--days 30] [--skip-texts] [--skip-mail] [--skip-slack]

Native `vp-knowledge-harvest-monthly` (day 22, 06:30 ET — before the 25th Policy Day cutoff and the 26th preview).
Built 2026-10-22 (Joshua: "glean what we can from all our communications and content to improve policy, procedure,
training and our knowledge base, especially Ask Goldilocks — monthly, from every platform").

WHAT IT IS: the one monthly loop that turns everything the business SAID in the last 30 days into proposed
improvements. It re-pulls nothing that another agent already pulls; it reads their outputs:

  C  calls      Call Analysis/week_*/grades/*.json + review_*.json (the weekly Phone & Text Review's graded rows —
                customer AND employee-internal calls: intents, flags, turned-away reasons, summaries, quotes)
  T  texts      Chekkit API (GET only, bin/chekkit_api.py): customer question -> human staff answer pairs
  A  ai-texts   fleet/ai_reply_audit/<date>.json (what the automated text responder said, and anything graded wrong)
  E  email      Apple Mail Envelope Index (read-only): customer emails to the five store mailboxes
  S  slack      staff questions in the deal/ops channels (what the floor did not know)
  K  kb         Preston Knowledge Base/_raw_harvest/capture_<date>.md (rules Preston/managers stated in Slack + calls)
  Q  goldilocks Ask Valley Pawn/QUESTION_LOG.md (every #ask-goldilocks question and outcome)
  M  marketing  marketing copy files written in the window (emails, SMS packs, posts, blog/page copy)
  reference     current P&P + Handbook (Ask_Handbook/SOURCES_CURRENT.md), Academy lesson list, store facts,
                POLICY_QUEUE.md (so nothing already queued is proposed twice)

WHAT IT WRITES (proposals only — nothing reaches staff or customers from here):
  Knowledge Harvest/<YYYY-MM>/HARVEST_<YYYY-MM>.md + harvest_<YYYY-MM>.json + evidence_<YYYY-MM>.json
  Human Resources/policy_bundles/POLICY_QUEUE.md   — one "Harvest candidates" block for next month's Policy Day
                                                    (status `candidate`; Joshua decides at the preview; backup first)
  Training Program/academy/HARVEST_EDITS_<YYYY-MM>.md — lesson fixes mapped to lesson ids
  Ask Valley Pawn/harvest/GAPS_<YYYY-MM>.md          — questions Goldilocks cannot answer yet + fact conflicts
  Ask Valley Pawn/answer_bank/CANDIDATES_<YYYY-MM>.md — "how we answer customers" bank (Layer 5) — pending approval,
                                                    NOT in the corpus
  ONE DM to Joshua (business summary). Failures: ledger row only (Rule 16).

GROUNDING: every proposal must cite evidence ids that exist in the evidence pack; anything citing none is dropped
in code. Customer identifiers (names, phones, emails) never leave this script: phones/emails are scrubbed before the
model sees text, and outputs are scrubbed again, including every rostered staff name except Preston's.
--render: same reads + model call; files go under Knowledge Harvest/_render/, queue untouched, DM to test_output.
"""
import collections
import datetime as dt
import glob
import json
import os
import re
import shutil
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "vp-knowledge-harvest-monthly"
PROJ = L.PROJ
OS_DIR = L.OS_DIR
OUT_ROOT = os.path.join(PROJ, "Knowledge Harvest")
CALLS = os.path.join(PROJ, "Call Analysis")
KB_RAW = os.path.join(PROJ, "Preston Knowledge Base", "_raw_harvest")
ASKVP = os.path.join(PROJ, "Ask Valley Pawn")
QLOG = os.path.join(ASKVP, "QUESTION_LOG.md")
FACTS = os.path.join(ASKVP, "facts", "store_facts.md")
SOURCES = os.path.join(PROJ, "Human Resources", "Ask_Handbook", "SOURCES_CURRENT.md")
QUEUE = os.path.join(PROJ, "Human Resources", "policy_bundles", "POLICY_QUEUE.md")
ACADEMY = os.path.join(PROJ, "Training Program", "academy")
MANIFEST = os.path.join(ACADEMY, "dist", "manifest_index.json")
AIAUDIT = os.path.join(OS_DIR, "fleet", "ai_reply_audit")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
BACKUPS = os.path.join(OS_DIR, "fleet", "_backups")
STORE_MAIL = {"culpeper@fcfpawn.com": "CUL", "waynesboro@fcfpawn.com": "WAY", "harrisonburg@fcfpawn.com": "HAR",
              "lexington@fcfpawn.com": "LEX", "roanoke@fcfpawn.com": "ROA"}
PERSONAL_DOMAINS = ("gmail.com", "yahoo.com", "aol.com", "hotmail.com", "outlook.com", "icloud.com", "me.com", "mac.com",
                    "comcast.net", "verizon.net", "att.net", "live.com", "msn.com", "ntelos.net", "shentel.net", "cox.net",
                    "charter.net", "protonmail.com", "proton.me", "ymail.com", "sbcglobal.net", "bellsouth.net", "lumos.net")
SLACK_CH = {"C03BWGT5F5X": "#deal-questions", "C03BETSS669": "#general", "C0C809Q2JDS": "#ask-goldilocks",
            "C063K8E02TW": "#roanoke-funds", "C03BLLRN64U": "#boro-funds", "C03B3K5DL6T": "#lex-funds",
            "C03BWRKEDUZ": "#harrisonburg-funds", "C04NGH4FF35": "#aged-inventory-review"}
MKT_DIRS = ["eBay Customer Campaign", "Valley Pawn Studios", "Gold and Silver Markeitng", "Refine Social Media",
            "Ai Optimized Marketing", "Website", "Email Refinement", "Community Involvment", "Loan Rule Change Outreach"]
MKT_NAME_OK = re.compile(r"(post|caption|email|sms|text|copy|blog|campaign|ad[s_-]|script|page|pack|content|launch)", re.I)
MKT_NAME_SKIP = re.compile(r"(status|plan|changelog|readme|audit|strategy|log|findings|\.bak|backup|_raw|test)", re.I)
PRESTON = "U03BWMEM9GR"

PHONE = re.compile(r"(\+?1[\s.-]?)?\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
STORE_PHONES = {"5404455510", "5402216346", "5405744500", "5404618349", "5405620776", "5402024200"}


# ----------------------------------------------------------------------------- helpers
def scrub(t, keep_store=True):
    """Drop customer phone numbers/emails (store numbers and @fcfpawn.com stay — they are public business facts)."""
    if not t:
        return ""
    def ph(m):
        d = re.sub(r"\D", "", m.group(0))[-10:]
        return m.group(0) if keep_store and d in STORE_PHONES else "[phone]"
    t = PHONE.sub(ph, t)
    t = EMAIL.sub(lambda m: m.group(0) if m.group(0).lower().endswith("@fcfpawn.com") else "[email]", t)
    return t


def staff_names():
    """Rostered staff names (full + first) except Preston — scrubbed from anything that leaves this script."""
    names = set()
    try:
        for e in json.load(open(ROSTER)).get("employees", []):
            n = (e.get("name") or "").strip()
            if not n or "preston" in n.lower() or "joshua" in n.lower():   # Preston and Joshua may be named
                continue
            names.add(n)
            for p in (e.get("preferred"), n.split()[0]):
                if p and len(p) > 2 and p.lower() not in ("the", "and"):
                    names.add(p.strip())
    except Exception:
        pass
    return sorted(names, key=len, reverse=True)


NAMES = []


def unname(t):
    for n in NAMES:
        t = re.sub(r"\b%s\b" % re.escape(n), "a team member", t)
    return t


def clean_out(t):
    return unname(scrub(t or ""))


def read(p, n=None):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read() if n is None else f.read(n)
    except OSError:
        return ""


def backup(p, tag):
    os.makedirs(BACKUPS, exist_ok=True)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(BACKUPS, "%s.bak-pre-%s-%s" % (os.path.basename(p), tag, L.now().strftime("%Y%m%d-%H%M"))))


# ----------------------------------------------------------------------------- sources
def src_calls(start, end):
    """Graded call rows whose week folder overlaps the window, deduped by zoom id."""
    rows, seen, weeks = [], set(), []
    for wd in sorted(glob.glob(os.path.join(CALLS, "week_*"))):
        m = re.search(r"week_(\d{4}-\d{2}-\d{2})", wd)
        if not m:
            continue
        ws = dt.date.fromisoformat(m.group(1))
        if ws > end or ws + dt.timedelta(days=21) < start:
            continue
        got = []
        for f in glob.glob(os.path.join(wd, "grades", "*.json")):
            try:
                r = json.load(open(f))
                got.extend(r if isinstance(r, list) else [r])
            except Exception:
                pass
        for f in glob.glob(os.path.join(wd, "review_*.json")):
            try:
                r = json.load(open(f))
                got.extend(r if isinstance(r, list) else [r])
            except Exception:
                pass
        n0 = len(rows)
        for r in got:
            if not isinstance(r, dict):
                continue
            # date from "Mon 10/12 05:10 PM" + the folder year
            d = None
            mm = re.search(r"(\d{1,2})/(\d{1,2})", str(r.get("time") or ""))
            if mm:
                try:
                    d = dt.date(ws.year, int(mm.group(1)), int(mm.group(2)))
                except ValueError:
                    d = None
            if d and not (start <= d <= end):
                continue
            k = r.get("zoom_id") or "%s|%s|%s" % (r.get("store"), r.get("time"), r.get("call"))
            if k in seen:
                continue
            seen.add(k)
            rows.append(r)
        weeks.append("%s (%d)" % (os.path.basename(wd), len(rows) - n0))
    return rows, weeks


def src_texts(start, end):
    """[(store, customer text, staff answer)] — human staff answers only; automated texts excluded."""
    try:
        import chekkit_api as ck
    except Exception as e:
        return [], "unavailable (%s)" % e
    s_utc = dt.datetime.combine(start, dt.time(0), L.ET).astimezone(dt.timezone.utc)
    e_utc = dt.datetime.combine(end + dt.timedelta(days=1), dt.time(0), L.ET).astimezone(dt.timezone.utc)
    pairs, stats, errs = [], collections.Counter(), []
    for code in L.STORES:
        try:
            convs = ck.conversations_since(code, s_utc, max_pages=30)
        except Exception as e:
            errs.append("%s: %s" % (code, str(e)[:80]))
            continue
        items = list(convs.items())
        step = max(1, len(items) // 300)          # a 300-thread sample per store is plenty to find the recurring questions
        stats[code + ":threads_total"] += len(items)
        for _p, c in items[::step][:300]:
            try:
                msgs = ck.messages(code, c.get("id") or c.get("_id") or "")
            except Exception:
                continue
            msgs = sorted(msgs, key=lambda m: m.get("createdAt") or "")
            stats[code + ":threads"] += 1
            for i, m in enumerate(msgs):
                t = ck.ts(m.get("createdAt"))
                if m.get("sender") != "customer" or not t or not (s_utc <= t < e_utc):
                    continue
                q = (m.get("text") or "").strip()
                if len(q) < 12 or q.lower() in ("stop", "ok", "thanks", "thank you"):
                    continue
                ans = ""
                for n in msgs[i + 1:i + 6]:
                    if n.get("sender") == "customer":
                        break
                    if n.get("sender") == "business" and not ck.is_automated(n) and (n.get("text") or "").strip():
                        ans = n["text"].strip()
                        break
                stats[code + ":questions"] += 1
                pairs.append((code, scrub(q)[:400], scrub(ans)[:500]))
            time.sleep(0.2)
    note = "%d customer messages across %d sampled threads (of %d active)" % (
        sum(v for k, v in stats.items() if k.endswith(":questions")), sum(v for k, v in stats.items() if k.endswith(":threads")),
        sum(v for k, v in stats.items() if k.endswith(":threads_total")))
    if errs:
        note += "; unreadable: " + ", ".join(errs)
    return pairs, note


def src_ai(start, end):
    items, wrong = [], 0
    for f in sorted(glob.glob(os.path.join(AIAUDIT, "*.json"))):
        try:
            d = json.load(open(f))
            day = dt.date.fromisoformat(d.get("date", os.path.basename(f)[:10]))
        except Exception:
            continue
        if not (start <= day <= end):
            continue
        wrong += int(d.get("wrong") or 0)
        for it in d.get("items") or []:
            bad = it.get("rule_issues") or it.get("judged") or it.get("issue")
            items.append({"store": it.get("store"), "q": scrub(it.get("customer_before") or "")[:300],
                          "reply": scrub(it.get("reply") or "")[:400], "issue": json.dumps(bad)[:200] if bad else ""})
    return items, wrong


def src_mail(start, end):
    envs = glob.glob(os.path.expanduser("~/Library/Mail/V*/MailData/Envelope Index"))
    if not envs:
        return [], "unavailable (no Apple Mail index on this machine)"
    try:
        c = sqlite3.connect("file:%s?mode=ro" % envs[0].replace(" ", "%20"), uri=True)
        tabs = {r[0] for r in c.execute("select name from sqlite_master where type='table'")}
        mcols = {r[1] for r in c.execute("PRAGMA table_info(messages)")}
        rcols = [r[1] for r in c.execute("PRAGMA table_info(recipients)")] if "recipients" in tabs else []
        if not rcols:
            return [], "unavailable (mail index has no recipients table)"
        rmsg = "message" if "message" in rcols else ("message_id" if "message_id" in rcols else None)
        radr = "address" if "address" in rcols else ("address_id" if "address_id" in rcols else None)
        if not rmsg or not radr:
            return [], "unavailable (unrecognised recipients schema: %s)" % ",".join(rcols)
        summ = ("summaries" in tabs and "summary" in mcols)
        q = ("select distinct m.ROWID, s.subject, a.address, m.date_received, ra.address%s "
             "from messages m left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender "
             "join recipients r on r.%s=m.ROWID join addresses ra on ra.ROWID=r.%s %s"
             "where lower(ra.address) in (%s) and m.date_received >= ? and m.date_received < ?"
             % (", su.summary" if summ else "", rmsg, radr,
                "left join summaries su on su.ROWID=m.summary " if summ else "",
                ",".join("'%s'" % a for a in STORE_MAIL)))
        t0 = int(dt.datetime.combine(start, dt.time(0), L.ET).timestamp())
        t1 = int(dt.datetime.combine(end + dt.timedelta(days=1), dt.time(0), L.ET).timestamp())
        out, seen = [], set()
        for row in c.execute(q, (t0, t1)):
            sender = (row[2] or "").lower()
            if not sender.endswith(PERSONAL_DOMAINS):
                continue
            key = (row[1], sender)
            if key in seen:
                continue
            seen.add(key)
            out.append({"store": STORE_MAIL.get((row[4] or "").lower(), "?"), "subject": scrub(row[1] or "")[:160],
                        "snippet": scrub(row[5] if summ and len(row) > 5 and row[5] else "")[:500]})
        return out, "%d customer emails" % len(out)
    except Exception as e:
        return [], "unavailable (%s)" % str(e)[:120]


def src_slack(start, end):
    """Staff questions (not Preston's, not bots) in the ops channels — what the floor had to ask."""
    out, read_ok, errs = [], 0, []
    oldest, latest = L.ts_of(start), L.ts_of(end, end=True)
    for ch, name in SLACK_CH.items():
        try:
            msgs = L.history(ch, oldest, latest)
        except Exception as e:
            errs.append(name)
            continue
        read_ok += 1
        for m in msgs:
            if m.get("bot_id") or m.get("subtype") or m.get("user") in (PRESTON, L.JOSHUA):
                continue
            t = L.text_of(m).strip()
            if len(t) < 15:
                continue
            if "?" in t or m.get("reply_count"):
                ans = ""
                if m.get("reply_count"):
                    try:
                        reps = L.thread(ch, m["ts"])
                        pr = [r for r in reps if r.get("user") == PRESTON] or [r for r in reps if not r.get("bot_id")]
                        ans = L.text_of(pr[0]) if pr else ""
                    except Exception:
                        pass
                out.append({"ch": name, "q": scrub(t)[:400], "a": scrub(ans)[:400]})
    note = "%d staff questions from %d channels" % (len(out), read_ok)
    if errs:
        note += "; unreadable: " + ", ".join(errs)
    return out, note


def src_kb(start, end):
    out = []
    for f in sorted(glob.glob(os.path.join(KB_RAW, "capture_*.md"))):
        m = re.search(r"capture_(\d{4}-\d{2}-\d{2})", f)
        if not m or not (start <= dt.date.fromisoformat(m.group(1)) <= end):
            continue
        for blk in read(f).split("\n---"):
            d = dict(re.findall(r"^(TOPIC|CLAIM|SOURCE|CONFIDENCE|CONFLICT):\s*(.*)$", blk, re.M))
            if d.get("CLAIM"):
                src = d.get("SOURCE", "")
                kind = "call" if src.startswith("zoom-call") else "slack"
                out.append({"topic": d.get("TOPIC", ""), "claim": d["CLAIM"][:400], "conf": d.get("CONFIDENCE", ""),
                            "kind": kind, "conflict": d.get("CONFLICT", "")[:200], "date": m.group(1)})
    return out


def src_goldilocks(start, end):
    out = []
    for line in read(QLOG).splitlines():
        p = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(p) < 5 or not re.match(r"\d{4}-\d{2}-\d{2}", p[0]):
            continue
        if not (start <= dt.date.fromisoformat(p[0][:10]) <= end):
            continue
        out.append({"store": p[2], "q": scrub(p[3])[:300], "outcome": p[4][:120]})
    return out


def src_marketing(start, end):
    files = []
    t0 = dt.datetime.combine(start, dt.time(0)).timestamp()
    t1 = dt.datetime.combine(end + dt.timedelta(days=1), dt.time(0)).timestamp()
    for d in MKT_DIRS:
        for root, _dirs, fs in os.walk(os.path.join(PROJ, d)):
            if "/_" in root or "backup" in root.lower():
                continue
            for f in fs:
                if not f.lower().endswith((".md", ".txt", ".json", ".html")):
                    continue
                if MKT_NAME_SKIP.search(f) or not MKT_NAME_OK.search(f):
                    continue
                p = os.path.join(root, f)
                try:
                    mt = os.path.getmtime(p)
                except OSError:
                    continue
                if t0 <= mt < t1:
                    files.append((mt, p))
    files.sort(reverse=True)
    out = []
    for _mt, p in files[:45]:
        txt = read(p, 6000)
        if p.endswith(".html"):
            txt = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", txt)
            txt = re.sub(r"<[^>]+>", " ", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) > 80:
            out.append({"file": os.path.relpath(p, PROJ), "text": scrub(txt)[:2500]})
    return out


def ref_policy_index():
    heads = [h.strip("# ").strip() for h in read(SOURCES).splitlines() if re.match(r"^#{2,4} \S", h)]
    return [h for h in heads if not h.lower().startswith(("what", "changelog", "table of contents"))][:400]


def ref_lessons():
    try:
        d = json.load(open(MANIFEST))
        return ["%s %s" % (p.get("id"), p.get("title")) for p in d.get("packages", [])]
    except Exception:
        return []


def ref_queue_titles():
    out = []
    for line in read(QUEUE).splitlines():
        p = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(p) >= 4 and re.match(r"\d{4}-\d{2}-\d{2}", p[0]):
            out.append("%s [%s]" % (p[1][:140], p[3]))
    return out


# ----------------------------------------------------------------------------- evidence pack
def build_pack(srcs):
    ev = {}
    lines = []

    def add(prefix, text):
        k = "%s%d" % (prefix, sum(1 for x in ev if x.startswith(prefix)) + 1)
        ev[k] = text
        lines.append("[%s] %s" % (k, text))

    calls = srcs["calls"]
    cust = [r for r in calls if r.get("type") == "customer"]
    emp = [r for r in calls if r.get("type") != "customer"]
    flags = collections.Counter(f for r in cust for f in (r.get("flags") or []))
    lines.append("## CALLS — %d graded customer calls, %d employee-internal calls" % (len(cust), len(emp)))
    lines.append("Customer intents: " + ", ".join("%s %d" % kv for kv in collections.Counter(r.get("intent") for r in cust).most_common(14)))
    lines.append("Outcomes: " + ", ".join("%s %d" % kv for kv in collections.Counter(r.get("outcome") for r in cust).most_common(10)))
    lines.append("Turned away because: " + ", ".join("%s %d" % kv for kv in collections.Counter(
        (r.get("turned_away_reason") or "").strip().lower() for r in cust if r.get("turned_away_reason")).most_common(15)))
    lines.append("Flags (count, stores):")
    for fl, n in flags.most_common(20):
        st = collections.Counter(r.get("store") for r in cust if fl in (r.get("flags") or []))
        lines.append("- %s: %d (%s)" % (fl, n, ", ".join("%s %d" % kv for kv in st.most_common())))
    for fl, _n in flags.most_common(12):
        ex = [r for r in cust if fl in (r.get("flags") or [])][:6]
        for r in ex:
            add("C", "call %s %s | flag: %s | %s | quote: \"%s\"" % (r.get("store"), r.get("time"), fl,
                                                                     scrub(r.get("summary") or "")[:300], scrub(r.get("quote") or "")[:160]))
    tr = [r for r in cust if r.get("outcome") in ("turned_away_we_dont_take", "unresolved_no_help", "unresolved_callback_promised")]
    for r in tr[:25]:
        add("C", "call %s %s | outcome %s | %s" % (r.get("store"), r.get("time"), r.get("outcome"), scrub(r.get("summary") or "")[:260]))
    lines.append("\n## EMPLOYEE-INTERNAL CALLS (staff calling Preston/each other = what the floor did not know)")
    for r in emp[:70]:
        add("C", "internal call %s %s | %s | %s" % (r.get("store"), r.get("time"), r.get("category") or r.get("intent"),
                                                  scrub(r.get("summary") or "")[:300]))

    lines.append("\n## CUSTOMER TEXTS — customer message -> human staff answer (blank = no human answer). %s" % srcs["texts_note"])
    tx = srcs["texts"]
    step = max(1, len(tx) // 160)
    for code, q, a in tx[::step][:160]:
        add("T", "%s | customer: %s | staff: %s" % (code, q, a or "(none)"))

    lines.append("\n## AUTOMATED TEXT REPLIES (AI responder) — %d graded wrong in window" % srcs["ai_wrong"])
    for it in [i for i in srcs["ai"] if i["issue"]][:25] + [i for i in srcs["ai"] if not i["issue"]][:25]:
        add("A", "%s | customer: %s | auto-reply: %s | issue: %s" % (it["store"], it["q"], it["reply"], it["issue"] or "none"))

    lines.append("\n## CUSTOMER EMAILS to store mailboxes — %s" % srcs["mail_note"])
    for m in srcs["mail"][:80]:
        add("E", "%s | %s | %s" % (m["store"], m["subject"], m["snippet"]))

    lines.append("\n## STAFF QUESTIONS IN SLACK — %s" % srcs["slack_note"])
    for s in srcs["slack"][:120]:
        add("S", "%s | asked: %s | answer: %s" % (s["ch"], s["q"], s["a"] or "(none)"))

    lines.append("\n## NEW RULES STATED BY PRESTON / MANAGERS (nightly capture) — %d" % len(srcs["kb"]))
    for k in srcs["kb"][:150]:
        add("K", "%s (%s, %s, %s)%s | %s" % (k["topic"], k["kind"], k["conf"], k["date"],
                                             " CONFLICT: " + k["conflict"] if k["conflict"] else "", k["claim"]))

    lines.append("\n## ASK GOLDILOCKS QUESTIONS — %d" % len(srcs["gold"]))
    for g in srcs["gold"]:
        add("Q", "%s | %s | %s" % (g["store"], g["q"], g["outcome"]))

    lines.append("\n## MARKETING COPY written in the window — %d files" % len(srcs["mkt"]))
    for m in srcs["mkt"]:
        add("M", "%s | %s" % (m["file"], m["text"][:1800]))
    return "\n".join(lines), ev


SYSTEM = """You are the monthly knowledge analyst for Valley Pawn (Full Circle Finance Inc DBA Valley Pawn), five Virginia
pawn stores. You read one month of what the business actually said — customer calls, texts, emails, staff questions,
the rules Preston (Operations Manager) stated, questions asked of Ask Goldilocks (the staff Q&A bot), automated text
replies, and marketing copy — and you propose concrete improvements to the written policy (P&P Manual / Employee
Handbook), the training (Valley Pawn Academy lessons), the Ask Goldilocks knowledge base, and customer-facing answers.

Hard rules:
- Every item MUST cite evidence ids exactly as given in brackets (e.g. "C12", "T4"). No id = the item is discarded.
- Separate the two problems: (a) the written policy is missing/unclear/wrong -> policy_candidates; (b) the policy
  exists but staff are not following it or do not know it -> training_candidates (enforcement/teaching), and say
  which P&P section already covers it.
- Never invent a policy number, dollar amount, percentage, hold period or legal requirement. If the right rule is
  unknown, set proposed_rule to "Preston/Joshua to decide: <the exact question>".
- Never output a customer's name, phone, email, or item tied to a person. Do not name staff; say "a team member"
  and the store code. Preston and Joshua may be named.
- Do not re-propose anything already in the policy queue list provided (match by meaning). You may reference it.
- Prefer few, high-value items with counts over many thin ones. Rank by how often it happened x risk
  (compliance/legal/firearms/money first, then customer experience, then convenience).
- Output ONLY one JSON object, no prose."""

PROMPT = """WINDOW: {start} to {end}

CURRENT P&P / HANDBOOK SECTION HEADINGS:
{pp}

ACADEMY LESSONS (id title):
{lessons}

STORE FACTS (current, authoritative):
{facts}

ALREADY IN THE POLICY QUEUE (title [status]) — do not duplicate:
{queue}

EVIDENCE PACK:
{pack}

Return JSON with exactly these keys:
{{
 "headline": ["3 plain-English sentences: the most important things this month's communications showed"],
 "policy_candidates": [{{"title": "", "type": "new|clarify|fix", "area": "Loans|Buys|Firearms|Customers & phones|eBay|HR|Pay|Operations|Compliance|Pricing|Training|Marketing", "problem": "", "proposed_rule": "", "pp_section": "existing section number+name it belongs in, or 'new'", "count": 0, "stores": ["CUL"], "priority": "high|medium|low", "evidence": ["C1"]}}],
 "training_candidates": [{{"lesson_id": "id from the list or 'new'", "lesson_title": "", "change": "", "already_in_policy": "section or 'no'", "count": 0, "stores": [], "evidence": []}}],
 "goldilocks_gaps": [{{"question": "a question staff actually asked or clearly needed", "why_missing": "not written down|conflicting|only in someone's head", "answer_owner": "Preston|Joshua|policy", "count": 0, "evidence": []}}],
 "customer_faq": [{{"question": "generic customer question (no identifiers)", "channel": "phone|text|email", "count": 0, "best_answer": "the best real staff answer seen, cleaned up, consistent with policy and store facts — or blank if none was good", "issue": "blank, or what staff/auto-replies got wrong", "evidence": []}}],
 "contradictions": [{{"detail": "two sources that disagree (policy vs practice, Preston vs P&P, auto-reply vs facts, marketing vs facts)", "fix": "", "evidence": []}}],
 "marketing_drift": [{{"file": "", "claim": "", "conflicts_with": "", "fix": "", "evidence": []}}]
}}
Limits: policy_candidates <= 10, training_candidates <= 12, goldilocks_gaps <= 15, customer_faq <= 15, contradictions <= 10, marketing_drift <= 10."""


def grounded(items, ev):
    keep = []
    for it in items or []:
        ids = [e for e in (it.get("evidence") or []) if e in ev]
        if not ids:
            continue
        it["evidence"] = ids
        for k, v in list(it.items()):
            if isinstance(v, str):
                it[k] = clean_out(v)
        keep.append(it)
    return keep


# ----------------------------------------------------------------------------- trend (month over month)
def metrics(srcs):
    cust = [r for r in srcs["calls"] if r.get("type") == "customer"]
    g = srcs["gold"]
    return {"calls": len(cust),
            "flags": dict(collections.Counter(f for r in cust for f in (r.get("flags") or [])).most_common(25)),
            "ai_wrong": srcs["ai_wrong"], "ai_checked": len(srcs["ai"]),
            "goldilocks_questions": len(g),
            "goldilocks_answered": sum(1 for x in g if x["outcome"].upper().startswith("ANSWERED")),
            "goldilocks_not_found": sum(1 for x in g if "NOT-FOUND" in x["outcome"].upper()),
            "staff_slack_questions": len(srcs["slack"]), "kb_rules": len(srcs["kb"])}


def prior_metrics(key):
    y, m = int(key[:4]), int(key[5:])
    pk = "%04d-%02d" % ((y - 1, 12) if m == 1 else (y, m - 1))
    try:
        return pk, json.load(open(os.path.join(OUT_ROOT, pk, "harvest_%s.json" % pk))).get("metrics")
    except Exception:
        return pk, None


def trend_lines(cur, prev):
    if not prev:
        return ["First harvest — this month is the baseline for next month's comparison."]
    out = []
    for k in ("calls", "goldilocks_questions", "goldilocks_not_found", "ai_wrong", "staff_slack_questions", "kb_rules"):
        out.append("%s: %s (last month %s)" % (k.replace("_", " "), cur.get(k), prev.get(k)))
    pc, pp = prev.get("calls") or 0, cur.get("calls") or 0
    for fl, n in sorted(cur["flags"].items(), key=lambda kv: -kv[1])[:10]:
        was = (prev.get("flags") or {}).get(fl, 0)
        rate = n / pp * 100 if pp else 0
        prate = was / pc * 100 if pc else 0
        arrow = "up" if rate > prate * 1.15 + 0.5 else ("down" if rate < prate * 0.85 - 0.5 else "flat")
        out.append("call flag '%s': %d (%.1f%% of calls) vs %d (%.1f%%) — %s" % (fl, n, rate, was, prate, arrow))
    return out


# ----------------------------------------------------------------------------- writers
def write_report(path, label, start, end, cov, res, ev, trend=None):
    L_ = ["# Knowledge Harvest — %s" % label, "",
          "Window %s to %s. Built %s by the monthly knowledge harvest. Proposals only — nothing here has been sent to staff "
          "or customers. Evidence ids point to `evidence_%s.json` next to this file." % (start, end, L.now().strftime("%Y-%m-%d %H:%M"), label_key(end)), "",
          "## What was read", ""]
    for k, v in cov:
        L_.append("- **%s:** %s" % (k, v))
    L_ += ["", "## Headline", ""] + ["- %s" % h for h in res.get("headline") or []]
    L_ += ["", "## Trend vs last month", ""] + ["- %s" % t for t in (trend or [])]

    def sec(title, items, fmt):
        L_.extend(["", "## %s (%d)" % (title, len(items)), ""])
        if not items:
            L_.append("_None this month._")
        for i, it in enumerate(items, 1):
            L_.append("%d. %s" % (i, fmt(it)))
            L_.append("   - evidence: %s" % ", ".join(it["evidence"][:12]))

    sec("Policy candidates → next Policy Day queue", res["policy_candidates"], lambda x: "**%s** (%s, %s priority, seen %s×, %s) — %s **Proposed:** %s _[P&P: %s]_" % (
        x.get("title"), x.get("type"), x.get("priority"), x.get("count"), ", ".join(x.get("stores") or []), x.get("problem"),
        x.get("proposed_rule"), x.get("pp_section")))
    sec("Training / Academy fixes", res["training_candidates"], lambda x: "**%s %s** — %s (seen %s×; already in policy: %s)" % (
        x.get("lesson_id"), x.get("lesson_title"), x.get("change"), x.get("count"), x.get("already_in_policy")))
    sec("Ask Goldilocks gaps (not written down yet)", res["goldilocks_gaps"], lambda x: "%s — %s; owner: %s (seen %s×)" % (
        x.get("question"), x.get("why_missing"), x.get("answer_owner"), x.get("count")))
    sec("Customer FAQ — answer bank candidates", res["customer_faq"], lambda x: "**%s** (%s, %s×) — best answer: %s%s" % (
        x.get("question"), x.get("channel"), x.get("count"), x.get("best_answer") or "_none good yet_",
        (" — issue: " + x["issue"]) if x.get("issue") else ""))
    sec("Contradictions", res["contradictions"], lambda x: "%s — fix: %s" % (x.get("detail"), x.get("fix")))
    sec("Marketing drift", res["marketing_drift"], lambda x: "%s: \"%s\" conflicts with %s — fix: %s" % (
        x.get("file"), x.get("claim"), x.get("conflicts_with"), x.get("fix")))
    with open(path, "w") as f:
        f.write("\n".join(L_) + "\n")


def label_key(end):
    return end.strftime("%Y-%m")


def next_packet(asof):
    y, m = (asof.year + 1, 1) if asof.month == 12 else (asof.year, asof.month + 1)
    return "%04d-%02d" % (y, m)


def write_queue(res, key, asof, render, outdir):
    begin = "<!-- HARVEST:%s:BEGIN -->" % key
    finish = "<!-- HARVEST:%s:END -->" % key
    rows = [begin, "", "## Harvest candidates — %s (from calls, texts, email, Slack, Goldilocks; NOT approved — Joshua decides at the Policy Day preview)" % dt.date(asof.year, asof.month, 1).strftime("%B %Y"), "",
            "| Added | Item | Area | Status | Packet | Notes |", "|---|---|---|---|---|---|"]
    for c in res["policy_candidates"]:
        note = "%s seen %s× (%s); %s. Proposed: %s. P&P: %s. Evidence: Knowledge Harvest/%s (%s)" % (
            c.get("priority", "").upper(), c.get("count"), ", ".join(c.get("stores") or []) or "all", c.get("problem", "").rstrip("."),
            c.get("proposed_rule", "").rstrip("."), c.get("pp_section"), key, ", ".join(c["evidence"][:6]))
        rows.append("| %s | %s | %s | candidate | %s | %s |" % (asof.isoformat(), c.get("title", "").replace("|", "/"), c.get("area", ""),
                                                             next_packet(asof), note.replace("|", "/").replace("\n", " ")))
    rows += ["", finish]
    block = "\n".join(rows)
    if render:
        with open(os.path.join(outdir, "POLICY_QUEUE_block_%s.md" % key), "w") as f:
            f.write(block + "\n")
        return "rendered (queue untouched)"
    txt = read(QUEUE)
    if not txt:
        return "queue file missing — not written"
    backup(QUEUE, "harvest%s" % key.replace("-", ""))
    if begin in txt and finish in txt:
        txt = txt[:txt.index(begin)] + block + txt[txt.index(finish) + len(finish):]
    else:
        txt = txt.rstrip("\n") + "\n\n" + block + "\n"
    with open(QUEUE, "w") as f:
        f.write(txt)
    return "%d candidates in the queue" % len(res["policy_candidates"])


def write_side(path, title, intro, items, fmt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = ["# %s" % title, "", intro, ""]
    if not items:
        out.append("_None this month._")
    for i, it in enumerate(items, 1):
        out.append("%d. %s  _(evidence: %s)_" % (i, fmt(it), ", ".join(it["evidence"][:8])))
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


# ----------------------------------------------------------------------------- main
def main():
    global NAMES
    a = sys.argv
    render = "--render" in a
    asof = dt.date.fromisoformat(a[a.index("--asof") + 1]) if "--asof" in a else L.now().date()
    days = int(a[a.index("--days") + 1]) if "--days" in a else 30
    end = asof - dt.timedelta(days=1)
    start = end - dt.timedelta(days=days - 1)
    key = asof.strftime("%Y-%m")
    label = asof.strftime("%B %Y")
    NAMES = staff_names()
    outdir = os.path.join(OUT_ROOT, "_render" if render else "", key)
    os.makedirs(outdir, exist_ok=True)
    print("window", start, "->", end, "key", key, "render", render)

    cdir = os.path.join(OS_DIR, "fleet", "state", "knowledge_harvest")
    os.makedirs(cdir, exist_ok=True)
    cache = os.path.join(cdir, "sources_%s%s.json" % (key, "_render" if render else ""))
    if "--reuse" in a and os.path.exists(cache):
        c = json.load(open(cache))
        srcs, cov = c["srcs"], [tuple(x) for x in c["cov"]]
        srcs["texts"] = [tuple(x) for x in srcs["texts"]]
        print("reusing", cache)
    else:
        srcs, cov = collect(a, start, end)
        with open(cache, "w") as f:
            json.dump({"srcs": srcs, "cov": cov}, f)
    for k, v in cov:
        print("  %-34s %s" % (k, v))
    rc = analyse(a, render, asof, start, end, key, label, outdir, srcs, cov)
    if rc == 0 and not render:
        try:
            os.remove(cache)      # raw customer wording is not kept once the month is analysed
        except OSError:
            pass
    return rc


def collect(a, start, end):
    srcs, cov = {}, []
    srcs["calls"], weeks = src_calls(start, end)
    cov.append(("Phone calls (graded)", "%d calls from %s" % (len(srcs["calls"]), ", ".join(weeks) or "no review weeks in window")))
    if "--skip-texts" in a:
        srcs["texts"], srcs["texts_note"] = [], "skipped"
    else:
        srcs["texts"], srcs["texts_note"] = src_texts(start, end)
    cov.append(("Customer texts", srcs["texts_note"]))
    srcs["ai"], srcs["ai_wrong"] = src_ai(start, end)
    cov.append(("Automated text replies", "%d read back, %d graded wrong" % (len(srcs["ai"]), srcs["ai_wrong"])))
    if "--skip-mail" in a:
        srcs["mail"], srcs["mail_note"] = [], "skipped"
    else:
        srcs["mail"], srcs["mail_note"] = src_mail(start, end)
    cov.append(("Store email", srcs["mail_note"]))
    if "--skip-slack" in a:
        srcs["slack"], srcs["slack_note"] = [], "skipped"
    else:
        srcs["slack"], srcs["slack_note"] = src_slack(start, end)
    cov.append(("Slack staff questions", srcs["slack_note"]))
    srcs["kb"] = src_kb(start, end)
    cov.append(("Rules stated by Preston/managers", "%d captured (%d from calls)" % (len(srcs["kb"]), sum(k["kind"] == "call" for k in srcs["kb"]))))
    srcs["gold"] = src_goldilocks(start, end)
    cov.append(("Ask Goldilocks questions", "%d" % len(srcs["gold"])))
    srcs["mkt"] = src_marketing(start, end)
    cov.append(("Marketing copy", "%d files" % len(srcs["mkt"])))
    return srcs, cov


ADDENDUM = ("\n\nOUTPUT DISCIPLINE: think briefly, then write the JSON. Keep every string under 45 words. "
            "Valid JSON only: double quotes, no trailing commas, no comments.")


def analyse(a, render, asof, start, end, key, label, outdir, srcs, cov):
    pack, ev = build_pack(srcs)
    with open(os.path.join(outdir, "evidence_%s.json" % key), "w") as f:
        json.dump({k: clean_out(v) for k, v in ev.items()}, f, indent=1)
    if len(ev) < 10:
        if not render:
            L.ledger(TASK, "the monthly knowledge harvest found almost nothing to read (%d items) — sources may be down" % len(ev))
        print("too little evidence:", len(ev))
        return 1

    prompt = PROMPT.format(start=start, end=end, pp="\n".join(ref_policy_index()), lessons="\n".join(ref_lessons()),
                           facts=read(FACTS)[:6000], queue="\n".join(ref_queue_titles()) or "(empty)", pack=pack[:260000])
    raw, err = None, None
    for attempt in range(2):
        try:
            txt, stop, usage = L._raw(prompt + ADDENDUM, SYSTEM, 40000, None)
            print("analysis: stop=%s usage=%s" % (stop, {k: usage.get(k) for k in ("input_tokens", "output_tokens")} if usage else None))
            m = re.search(r"\{.*\}", txt, re.S)
            if not m:
                raise ValueError("no JSON in answer (stop=%s)" % stop)
            raw = json.loads(m.group(0), strict=False)
            break
        except Exception as e:   # truncated / malformed JSON -> one more try
            err = e
            print("analysis attempt %d failed: %s" % (attempt + 1, str(e)[:160]))
    if raw is None:
        if not render:
            L.ledger(TASK, "the monthly knowledge harvest could not get its analysis back (%s)" % str(err)[:80])
        return 1
    res = {k: grounded(raw.get(k), ev) for k in ("policy_candidates", "training_candidates", "goldilocks_gaps",
                                                   "customer_faq", "contradictions", "marketing_drift")}
    res["headline"] = [clean_out(h) for h in (raw.get("headline") or [])][:3]
    pr = {"high": 0, "medium": 1, "low": 2}
    def _n(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
    res["policy_candidates"].sort(key=lambda x: (pr.get(x.get("priority"), 3), -_n(x.get("count"))))
    dropped = sum(len(raw.get(k) or []) for k in res if k != "headline") - sum(len(v) for k, v in res.items() if k != "headline")
    met = metrics(srcs)
    pk, prev = prior_metrics(key)
    trend = trend_lines(met, prev)
    with open(os.path.join(outdir, "harvest_%s.json" % key), "w") as f:
        json.dump({"window": [str(start), str(end)], "coverage": cov, "dropped_ungrounded": dropped, "metrics": met, **res}, f, indent=1)
    report = os.path.join(outdir, "HARVEST_%s.md" % key)
    write_report(report, label, start, end, cov + [("Proposals dropped for citing no evidence", str(dropped))], res, ev, trend)

    side = outdir if render else None
    qnote = write_queue(res, key, asof, render, outdir)
    write_side(os.path.join(side or ACADEMY, "HARVEST_EDITS_%s.md" % key), "Academy edits from the %s knowledge harvest" % label,
               "Proposed lesson changes from what calls, texts and staff questions showed. Apply in the next lesson pass; "
               "re-run the build + validator. Source: Knowledge Harvest/%s." % key, res["training_candidates"],
               lambda x: "**%s %s** — %s (seen %s×; policy: %s)" % (x.get("lesson_id"), x.get("lesson_title"), x.get("change"),
                                                                   x.get("count"), x.get("already_in_policy")))
    gold = res["goldilocks_gaps"] + [{"question": "CONTRADICTION: " + c.get("detail", ""), "why_missing": "conflicting",
                                      "answer_owner": "Joshua", "count": "", "evidence": c["evidence"]} for c in res["contradictions"]]
    write_side(os.path.join(side or os.path.join(ASKVP, "harvest"), "GAPS_%s.md" % key), "Ask Goldilocks gaps — %s" % label,
               "Questions the floor needed answered that are not written down (or conflict). Preston's weekly check and the "
               "Policy Day preview close these; once answered they reach Goldilocks automatically.", gold,
               lambda x: "%s — %s; owner: %s %s" % (x.get("question"), x.get("why_missing"), x.get("answer_owner"),
                                                   ("(seen %s×)" % x["count"]) if x.get("count") else ""))
    write_side(os.path.join(side or os.path.join(ASKVP, "answer_bank"), "CANDIDATES_%s.md" % key),
               "How we answer customers — candidates %s" % label,
               "PENDING APPROVAL — not in Goldilocks' corpus. Approved answers move to answer_bank/APPROVED.md.",
               res["customer_faq"], lambda x: "**%s** (%s, %s×) — %s%s" % (
                   x.get("question"), x.get("channel"), x.get("count"), x.get("best_answer") or "_no good answer seen_",
                   (" — issue: " + x["issue"]) if x.get("issue") else ""))

    pc, tc = res["policy_candidates"], res["training_candidates"]
    lines = ["Monthly knowledge harvest — %s" % label, "",
             "Read: %d calls, %s, %s, %d staff questions in Slack, %d Goldilocks questions, %d new rules from Preston/managers, %d marketing pieces." % (
                 len(srcs["calls"]), srcs["texts_note"].split(";")[0], srcs["mail_note"].split(";")[0], len(srcs["slack"]),
                 len(srcs["gold"]), len(srcs["kb"]), len(srcs["mkt"])), ""]
    for h in res["headline"]:
        lines.append("• " + h)
    lines += ["", "Policy: %d candidates added to the %s update queue for your preview%s" % (
        len(pc), dt.date(int(next_packet(asof)[:4]), int(next_packet(asof)[5:]), 1).strftime("%B"), ":" if pc else ".")]
    for i, c in enumerate(pc[:5], 1):
        lines.append("%d. %s (seen %s×)" % (i, c.get("title"), c.get("count")))
    lines += ["", "Training: %d Academy fixes queued. Goldilocks: %d gaps to fill. Customer answers: %d drafted for approval. "
              "Contradictions: %d. Marketing drift: %d." % (len(tc), len(res["goldilocks_gaps"]), len(res["customer_faq"]),
                                                            len(res["contradictions"]), len(res["marketing_drift"])),
              "", "Full report: Knowledge Harvest/%s/HARVEST_%s.md" % (key, key)]
    text = clean_out("\n".join(lines))
    ok = L.post(TASK, L.JOSHUA, text, render, label="joshua")
    print("queue:", qnote, "| report:", report, "| dm ok:", ok)
    if not render and ok is True:
        with open(os.path.join(OUT_ROOT, "RUN_LOG.md"), "a") as f:
            f.write("- %s — %s: %d policy, %d training, %d goldilocks, %d faq, %d contradictions, %d marketing; dropped %d ungrounded\n" % (
                L.now().strftime("%Y-%m-%d %H:%M"), key, len(pc), len(tc), len(res["goldilocks_gaps"]), len(res["customer_faq"]),
                len(res["contradictions"]), len(res["marketing_drift"]), dropped))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
