#!/usr/bin/env python3
"""call_week_grade.py — the weekly Phone & Text Review, native (no Cowork session, no screen).

WHY (comms review 2026-10-20): the Sep 28–Oct 18 review was the single most actionable thing the business
produced (Joshua posted its findings to #general 10/20), and it still depended on a hand-run session reading
1,790 calls with 41 subagents. "Local scheduled-task creation is now blocked on this Mac" (CHANGELOG 10/18),
so the weekly cadence never started. This agent does the whole job on the Mac every Monday:

  1. PULL      call_week_review.py --since/--until (read-only Zoom S2S: call history, recordings index,
               local whisper transcripts through the existing harvester). Skipped when the week folder is
               already complete.
  2. GRADE     every recorded call's transcript -> the SAME JSON row the hand review used
               (Call Analysis/week_2026-09-28/review_*.json schema), via vp_ai (Claude API, Keychain key),
               8 calls per request, cached per call in week_<since>/grades/<zoom id>.json (re-runs resume).
               Silent / <12-word transcripts are classed without an API call.
  3. STATS     missed-while-open, callbacks, never-reached, by store (store hours from
               fleet/missed_call_text_config.json — the one file that drives every hours decision).
  4. TEXTS     read-only Chekkit API audit per store for the week: conversations, customer messages with no
               staff answer by Sunday night, automated (AI / missed-call) texts, STOPs.
  5. WRITE     numbers table + cross-store themes + per-store bullets (one verbatim quote each) + texts,
               narrative drafted by vp_ai from the graded rows ONLY (it never sees audio and is told so),
               rendered to HTML and PDF (Playwright/Chrome, headless, its own temp profile — never pw-vp).
               Copies the PDF into Drive for Desktop "Call Reviews" when that folder exists.
  6. DELIVER   3–5 plain lines + the PDF path through fleet/outbox (ops bot DM to Joshua). Output is for
               Joshua ONLY — it names staff and customers; never a channel. One CHANGELOG line.

  call_week_grade.py                      last Mon–Sun, full run (DM at the end)
  call_week_grade.py --since 2026-10-12 --until 2026-10-18
  call_week_grade.py --render             everything except the DM/CHANGELOG line
  call_week_grade.py --max-calls 40       grade only the first N calls (smoke test; marks the run partial)
  call_week_grade.py --no-pull            never call Zoom (use what is on disk)
Rule 18: if transcripts are missing for more than 10% of recordings, or any store's grading failed, the
numbers are still written but the DM says plainly what is incomplete; a failed PDF leaves the HTML.
stdlib only + vp_ai + (optional) playwright. Logs never carry customer names or numbers (last-4 only).
"""
import argparse, collections, datetime as dt, glob, json, os, re, shutil, subprocess, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OS_DIR = os.path.dirname(HERE)
PROJECTS = os.path.dirname(OS_DIR)
CA = os.path.join(PROJECTS, "Call Analysis")
PIPE = os.path.join(PROJECTS, "Zoom Call Pipeline")
TX = os.path.join(PIPE, "out", "transcripts")
FLEET = os.path.join(OS_DIR, "fleet")
CONFIG = os.path.join(FLEET, "missed_call_text_config.json")
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
JOSHUA = "U03BB52MDSA"
TASK = "weekly-phone-text-review"
STORES = ["CUL", "HAR", "WAY", "LEX", "ROA"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "WAY": "Waynesboro", "LEX": "Lexington", "ROA": "Roanoke",
         "PRE": "Preston", "UNK": "Preston"}
EXT = {"802": "HAR", "805": "HAR", "803": "WAY", "806": "WAY", "807": "LEX", "804": "LEX",
       "808": "CUL", "810": "CUL", "809": "ROA", "812": "ROA", "813": "PRE"}
MISS = {"no_answer", "abandoned", "voicemail", "hang_up", "overflowed", "busy", "ring_timeout", "missed", "timeout", "rejected"}
BATCH = 8
MODEL = "claude-sonnet-5-5"

SCHEMA = {
    "call": "int (the CALL number in the header)", "type": "customer|employee_internal|vendor_business|voicemail_outbound|spam_robocall|wrong_number|silent_or_unintelligible",
    "intent": "loan_payment_or_extension|loan_payoff_or_redeem|sell_item|pawn_loan_new|buy_item|item_availability_or_price|firearm|gold_silver_jewelry|layaway|follow_up_on_item|hours_location|complaint|other",
    "category": "item category or none", "item": "short item description or empty",
    "outcome": "deal_or_customer_coming_in|payment_or_extension_handled|info_given|unresolved_callback_promised|unresolved_no_help|turned_away_we_dont_take|declined_price_or_condition|not_in_stock|voicemail_left|n/a",
    "turned_away_reason": "why we said no, or empty", "qualifying_questions": "true|false|null (sell/pawn calls only: did staff ask brand/model/condition/what comes with it)",
    "offered_loan_vs_buy": "true|false|null (sell/pawn calls only)", "staff_name": "first name of the employee on the call or empty",
    "service_rating": "1-5 or null (customer calls only)", "flags": "list from the FLAG LIST, empty if none",
    "summary": "one or two plain sentences, name the staff member", "quote": "one short verbatim line from the transcript that best shows the issue or the praise, or empty"}
FLAGS = ["hold/extension past due after Oct 1", "promised callback", "excellent handling worth praising", "odd/weird conversation",
         "unverified caller given loan/account/collateral details", "stolen-property or police matters", "customer complaint or angry customer",
         "wrong or made-up policy/hours", "long hold", "personal call on store line", "low cash / can't fund", "FFL/background-check handling issues",
         "lost sale due to our process", "gossip or inappropriate talk on the line", "firearm details confirmed to unverified caller",
         "staff badmouthing company/coworkers/management", "price quote given by phone without seeing the item", "customer told to use the app instead of being helped"]
POLICY = """Policy context (Full Circle Finance Inc DBA Valley Pawn, 5 Virginia stores):
- Past-due timeline (Every Call Counts deck, 2026-10-23, slide 7): days 1-5 past due = grace period, no late fee (so "five-day grace period" is CORRECT policy, not a flag); late fee from day 6; days 16-75 the loan can be expired and only a manager can work with it; day 76+ expired, no exceptions. Staff may NOT promise a hold on a past-due loan, quote "two months", "60 days", "75 days and you're fine", or any date not read from Bravo; the extension or the payoff only, no partial payments. Payments and extensions BEFORE the due date are normal.
- Account details (balance, items, due dates) only to the verified account holder (name + DOB or ID); never to a spouse, parent, friend or "calling for" someone, never to an unverified "police/ATF" caller — take a number and have a manager verify.
- We do not take cell phones. Handguns 21+, long guns 18+. No firearm returns. 30-day warranty on retail. Layaway: deposit then a payment at least every 30 days.
- Staff should ask qualifying questions on sell/pawn calls (brand, model, condition, what comes with it) and offer a loan as well as a buy. Phone price quotes without seeing the item are discouraged.
- Hours: Culpeper/Roanoke/Waynesboro Mon-Fri 10-6, Sat 10-5; Harrisonburg/Lexington Mon Tue Thu Fri Sat 10-6 (closed Wed); all closed Sunday.
- Payments, due dates and balances can also be handled in the free MobilePawn app (thevalleypawn.com/app)."""


# ---------------------------------------------------------------- helpers
def log(msg):
    print(dt.datetime.now(ET).strftime("%H:%M:%S"), msg, flush=True)


def ledger(sentence, needs="no"):
    with open(os.path.join(FLEET, "FAILURE_LEDGER.md"), "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence, needs))


def last_week(today=None):
    today = today or dt.datetime.now(ET).date()
    mon = today - dt.timedelta(days=today.weekday() + 7)
    return mon, mon + dt.timedelta(days=6)


def et(s):
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ET)
    except Exception:
        return None


def l4(n):
    d = "".join(c for c in str(n or "") if c.isdigit())
    return "…" + d[-4:] if d else "…?"


def cfg():
    return json.load(open(CONFIG))


def during_hours(t, s):
    if t.weekday() not in s.get("days", []):
        return False
    o = dt.time.fromisoformat(s.get("open", "10:00"))
    c = dt.time.fromisoformat(s.get("close_by_weekday", {}).get(str(t.weekday()), s.get("close", "18:00")))
    return o <= t.time() < c


# ---------------------------------------------------------------- 1. pull
def pull(since, until, d, allow_pull):
    st = {}
    try:
        st = json.load(open(os.path.join(d, "status.json")))
    except Exception:
        pass
    have = os.path.exists(os.path.join(d, "call_history.json")) and os.path.exists(os.path.join(d, "recordings_index.json"))
    if have and st.get("phase") == "done" and st.get("until") == until:
        log("pull: week folder complete, skipping Zoom"); return True
    if not allow_pull:
        log("pull: --no-pull and folder incomplete"); return have
    import importlib.util
    spec = importlib.util.spec_from_file_location("cwr", os.path.join(HERE, "call_week_review.py"))
    cwr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cwr)
    log("pull: call_week_review.work %s..%s (transcribes locally, can take ~1h)" % (since, until))
    cwr.work(since, until)
    try:
        st = json.load(open(os.path.join(d, "status.json")))
    except Exception:
        st = {}
    return st.get("phase") == "done"



# ---------------------------------------------------------------- JSON hardening (restart 2026-10-20)
# First smoke (job 20261020-1358-callweek-smoke2): 2 of 4 batches died "Expecting ',' delimiter" — the
# model put a raw double quote inside the verbatim `quote` / `summary` strings. Fix: tell it not to, parse
# tolerantly (escape stray quotes inside strings), fall back to one-object-per-line, keep the raw text
# of anything that still fails under week_<since>/grades/_raw_fail_*.txt for the next person.
def _repair_json(txt):
    """Escape double quotes that sit INSIDE a string value (the model quoting a caller verbatim)."""
    out, ins, esc, i, n = [], False, False, 0, len(txt)
    while i < n:
        c = txt[i]
        if ins:
            if esc:
                out.append(c); esc = False
            elif c == "\\":
                out.append(c); esc = True
            elif c == '"':
                j = i + 1
                while j < n and txt[j] in " \t\r\n":
                    j += 1
                end = j >= n or txt[j] in ":}]"
                if not end and j < n and txt[j] == ",":
                    k = j + 1
                    while k < n and txt[k] in " \t\r\n":
                        k += 1
                    end = k >= n or txt[k] in '"{[-0123456789' or txt.startswith(("true", "false", "null"), k)
                if end:
                    out.append(c); ins = False
                else:
                    out.append('\\"')
            else:
                out.append(c)
        else:
            if c == '"':
                ins = True
            out.append(c)
        i += 1
    return "".join(out)


def ask_rows(prompt, system, d, tag):
    import vp_ai
    raw = vp_ai.ask(prompt, system=system, model=MODEL, max_tokens=8000)
    m = re.search(r"(\[.*\]|\{.*\})", raw, re.S)
    body = m.group(1) if m else raw
    for cand in (body, _repair_json(body)):
        try:
            got = json.loads(cand, strict=False)
            return [got] if isinstance(got, dict) else got
        except Exception:
            pass
    rows = []  # one object per line / per {...} block
    for blk in re.findall(r"\{[^{}]*\}", raw, re.S):
        for cand in (blk, _repair_json(blk)):
            try:
                rows.append(json.loads(cand, strict=False)); break
            except Exception:
                continue
    if rows:
        log("grade: %s parsed %d rows after repair" % (tag, len(rows)))
        return rows
    try:
        gdir = os.path.join(d, "grades"); os.makedirs(gdir, exist_ok=True)
        open(os.path.join(gdir, "_raw_fail_%s_%s.txt" % (tag, dt.datetime.now(ET).strftime("%H%M%S"))), "w").write(raw)
    except Exception:
        pass
    raise ValueError("no parseable JSON rows")


# ---------------------------------------------------------------- 2. grade
def calls_index(d):
    idx = json.load(open(os.path.join(d, "recordings_index.json")))
    for r in idx:
        r["_t"] = et(r.get("date_time")) or dt.datetime.now(ET)
    idx.sort(key=lambda r: r["_t"])
    for n, r in enumerate(idx, 1):
        r["n"] = n
        r["store"] = r.get("store") if r.get("store") in STORES else "PRE"
    return idx


def transcripts(idx):
    files = {}
    for f in glob.glob(os.path.join(TX, "2026-*", "*.json")):
        files[os.path.basename(f)[:-5]] = f
    out, missing = {}, []
    for r in idx:
        f = files.get(r["id"])
        if not f:
            missing.append(r["id"]); continue
        try:
            t = json.load(open(f))
            out[r["id"]] = (t.get("transcript") or "").strip()
        except Exception:
            missing.append(r["id"])
    return out, missing


def header(r):
    return "=== CALL %d | %s | %s | %s | %ds | other %s | zoom id %s" % (
        r["n"], NAMES.get(r["store"], r["store"]), r["_t"].strftime("%a %m/%d %I:%M %p"), r["direction"], r["duration_s"], l4(r.get("other_number")), r["id"])


def silent_row(r):
    return {"call": r["n"], "store": r["store"], "time": r["_t"].strftime("%a %m/%d %I:%M %p"), "dir": r["direction"], "dur": r["duration_s"],
            "zoom_id": r["id"], "type": "silent_or_unintelligible", "intent": "other", "category": "none", "item": "", "outcome": "n/a",
            "turned_away_reason": "", "qualifying_questions": None, "offered_loan_vs_buy": None, "staff_name": "", "service_rating": None,
            "flags": [], "summary": "No usable audio.", "quote": ""}


def grade(idx, tx, d, max_calls=None):
    import vp_ai
    gdir = os.path.join(d, "grades"); os.makedirs(gdir, exist_ok=True)
    todo, rows, failed = [], {}, 0
    sel = idx[:max_calls] if max_calls else idx
    for r in sel:
        p = os.path.join(gdir, r["id"] + ".json")
        if os.path.exists(p):
            try:
                rows[r["id"]] = json.load(open(p)); continue
            except Exception:
                pass
        t = tx.get(r["id"])
        if t is None:
            continue
        if len(t.split()) < 12:
            rows[r["id"]] = silent_row(r); json.dump(rows[r["id"]], open(p, "w")); continue
        todo.append(r)
    log("grade: %d cached/silent, %d to grade" % (len(rows), len(todo)))
    system = ("You are reviewing transcribed phone calls for the owner of Valley Pawn. You only have machine transcripts (no audio). "
              "Be factual and specific; name the staff member when the transcript gives a name; never invent. Return ONLY a JSON list, one object per call, "
              "with exactly these keys: " + json.dumps(SCHEMA) + "\nJSON RULES: valid JSON only, no markdown fence; inside any string value never use a double quote character — use single quotes when quoting what someone said; no trailing commas.\nFLAG LIST: " + json.dumps(FLAGS) + "\n" + POLICY)
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        prompt = "\n\n".join(header(r) + "\n" + tx[r["id"]][:6000] for r in batch)
        got = None
        for attempt in range(3):
            try:
                got = ask_rows("Review these %d calls. Return a JSON list with one object per CALL number, in order.\n\n%s" % (len(batch), prompt),
                               system, d, "b%d-a%d" % (i // BATCH + 1, attempt + 1))
                break
            except Exception as e:
                log("grade: batch %d attempt %d failed %s: %s" % (i // BATCH + 1, attempt + 1, type(e).__name__, str(e)[:120]))
                time.sleep(5 + 10 * attempt)
        by_n = {}
        for g in got or []:
            try:
                by_n[int(g.get("call"))] = g
            except Exception:
                pass
        for r in batch:
            g = by_n.get(r["n"])
            if not g:
                failed += 1; continue
            row = silent_row(r)
            for k in SCHEMA:
                if k in g and k != "call":
                    row[k] = g[k]
            if not isinstance(row.get("flags"), list):
                row["flags"] = []
            try:
                row["service_rating"] = int(row["service_rating"]) if row.get("service_rating") not in (None, "", "null") else None
            except Exception:
                row["service_rating"] = None
            rows[r["id"]] = row
            json.dump(row, open(os.path.join(gdir, r["id"] + ".json"), "w"))
        if (i // BATCH) % 10 == 0:
            log("grade: %d/%d" % (min(i + BATCH, len(todo)), len(todo)))
        time.sleep(0.5)
    out = [rows[r["id"]] for r in sel if r["id"] in rows]
    json.dump(out, open(os.path.join(d, "review_native.json"), "w"), indent=1)
    return out, failed


# ---------------------------------------------------------------- 3. stats
def stats(d, c):
    hist = json.load(open(os.path.join(d, "call_history.json")))
    stores = c["stores"]
    def store(r):
        e = r.get("callee_ext_number") if r.get("direction") == "inbound" else r.get("caller_ext_number")
        return EXT.get(str(e), "?")
    def other(r):
        return (r.get("caller_did_number") or r.get("caller_number")) if r.get("direction") == "inbound" else (r.get("callee_did_number") or r.get("callee_number"))
    for r in hist:
        r["_t"] = et(r.get("start_time")) or dt.datetime.now(ET); r["_s"] = store(r); r["_o"] = other(r)
        r["_open"] = r["_s"] in stores and during_hours(r["_t"], stores[r["_s"]])
    S = collections.defaultdict(collections.Counter)
    for r in hist:
        s = S[r["_s"]]
        if r.get("direction") == "outbound":
            s["out"] += 1; continue
        s["in"] += 1
        if r["_open"]:
            s["in_open"] += 1
            if r.get("call_result") in MISS:
                s["miss_open"] += 1
            else:
                s["ans"] += 1; s["ans_secs"] += int(r.get("duration") or 0)
        else:
            s["closed"] += 1
    never = collections.defaultdict(set); cb = collections.Counter(); again = collections.Counter(); lag = collections.defaultdict(list)
    for m in hist:
        if m.get("direction") != "inbound" or m.get("call_result") not in MISS or not m["_open"]:
            continue
        later = [r for r in hist if r["_o"] and r["_o"] == m["_o"] and r["_t"] > m["_t"] and r["_s"] in (m["_s"], "PRE")]
        c_b = [r for r in later if r.get("direction") == "outbound"]
        c_a = [r for r in later if r.get("direction") == "inbound" and r.get("call_result") not in MISS]
        if c_b:
            cb[m["_s"]] += 1; lag[m["_s"]].append((min(r["_t"] for r in c_b) - m["_t"]).total_seconds() / 60)
        elif c_a:
            again[m["_s"]] += 1
        else:
            never[m["_s"]].add(m["_o"])
    worst = collections.defaultdict(lambda: [0, 0])
    for r in hist:
        if r.get("direction") == "inbound" and r["_open"] and r["_s"] in STORES:
            k = (r["_t"].strftime("%a %m/%d"), r["_s"]); worst[k][0] += 1; worst[k][1] += r.get("call_result") in MISS
    out = {}
    for s in STORES + ["PRE"]:
        x = S[s]
        L = sorted(lag[s])
        out[s] = dict(x) | {"cb": cb[s], "again": again[s], "never": len(never[s]), "median_cb_min": round(L[len(L) // 2]) if L else None}
    out["_worst_days"] = [{"day": k[0], "store": k[1], "in": v[0], "missed": v[1]} for k, v in sorted(worst.items(), key=lambda kv: -kv[1][1])[:6]]
    return out


# ---------------------------------------------------------------- 4. texts (Chekkit API, read-only)
def texts(since, until):
    try:
        import chekkit_api as ck
    except Exception:
        return {}
    start = dt.datetime.combine(since, dt.time(0), ET).astimezone(UTC)
    end = dt.datetime.combine(until + dt.timedelta(days=1), dt.time(0), ET).astimezone(UTC)
    out = {}
    for code in STORES:
        o = {"conversations": 0, "customer_msgs": 0, "unanswered_threads": 0, "automated": 0, "stops": 0, "ai_replies": 0, "error": ""}
        try:
            convs = ck.conversations_since(code, start)
            for p, c in convs.items():
                msgs = ck.messages(code, c.get("id") or c.get("_id") or "")
                wk = [m for m in msgs if start <= (ck.ts(m.get("createdAt")) or start) < end]
                if not wk:
                    continue
                o["conversations"] += 1
                cust = [m for m in wk if m.get("sender") == "customer"]
                o["customer_msgs"] += len(cust)
                o["automated"] += sum(1 for m in wk if m.get("sender") == "business" and ck.is_automated(m))
                o["ai_replies"] += sum(1 for m in wk if m.get("sender") == "business" and ck.is_automated(m) and "hi, this is valley pawn in" not in (m.get("text") or "").lower())
                o["stops"] += sum(1 for m in cust if (m.get("text") or "").strip().lower() in ("stop", "stop texting me", "unsubscribe", "remove me"))
                if cust:
                    last_c = max(ck.ts(m.get("createdAt")) or start for m in cust)
                    staff_after = [m for m in msgs if m.get("sender") == "business" and not ck.is_automated(m) and (ck.ts(m.get("createdAt")) or start) > last_c]
                    if not staff_after and (cust[-1].get("text") or "").strip().lower() not in ("thanks", "thank you", "ok", "okay", "stop"):
                        o["unanswered_threads"] += 1
                time.sleep(0.25)
        except Exception as e:
            o["error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
        out[code] = o
    return out


# ---------------------------------------------------------------- 5. aggregate + narrative
def aggregate(rows):
    agg = {}
    for s in STORES + ["PRE"]:
        rs = [r for r in rows if r.get("store") == s]
        cu = [r for r in rs if r.get("type") == "customer"]
        sl = [r for r in cu if r.get("intent") in ("sell_item", "pawn_loan_new")]
        rt = [r["service_rating"] for r in cu if isinstance(r.get("service_rating"), int)]
        fl = collections.Counter(f for r in rs for f in (r.get("flags") or []))
        agg[s] = {"recorded": len(rs), "customer": len(cu),
                  "deals": sum(r.get("outcome") == "deal_or_customer_coming_in" for r in cu),
                  "callback_promised": sum(r.get("outcome") == "unresolved_callback_promised" for r in cu),
                  "no_help": sum(r.get("outcome") == "unresolved_no_help" for r in cu),
                  "turned_away": sum(r.get("outcome") in ("turned_away_we_dont_take", "declined_price_or_condition") for r in cu),
                  "not_in_stock": sum(r.get("outcome") == "not_in_stock" for r in cu),
                  "sell_calls": len(sl), "qualifying": sum(r.get("qualifying_questions") is True for r in sl),
                  "loan_offered": sum(r.get("offered_loan_vs_buy") is True for r in sl),
                  "rating": round(sum(rt) / len(rt), 2) if rt else None,
                  "intents": collections.Counter(r.get("intent") for r in cu).most_common(6),
                  "flags": fl.most_common(14),
                  "staff": collections.Counter(r.get("staff_name") for r in cu if r.get("staff_name")).most_common(6),
                  "holds_past_due": fl.get("hold/extension past due after Oct 1", 0),
                  "unverified": fl.get("unverified caller given loan/account/collateral details", 0) + fl.get("firearm details confirmed to unverified caller", 0),
                  "turned": [(r.get("item", "")[:30], r.get("turned_away_reason", "")[:40]) for r in cu if r.get("outcome") in ("turned_away_we_dont_take", "declined_price_or_condition")][:20]}
    return agg


def _ask_meta(prompt, system, max_tokens):
    """vp_ai.ask plus the stop reason (restart 2026-10-20: a narrative came back cut off at ~6.5k chars with
    no error — we need to know whether that was max_tokens). Same key, same endpoint, nothing else."""
    import vp_ai, urllib.request
    body = {"model": MODEL, "max_tokens": max_tokens, "system": system, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(vp_ai.API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": vp_ai.key(), "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.load(r)
    txt = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    return txt, resp.get("stop_reason"), (resp.get("usage") or {}).get("output_tokens")


def narrative(since, until, st, agg, rows, tx_stats, partial_note, d_=None):
    import vp_ai
    flagged = {}
    for s in STORES + ["PRE"]:
        fr = [r for r in rows if r.get("store") == s and (r.get("flags") or r.get("outcome") in ("unresolved_no_help", "unresolved_callback_promised"))]
        fr.sort(key=lambda r: (-len(r.get("flags") or []), r.get("call", 0)))
        flagged[s] = [{"call": r.get("call"), "time": r.get("time"), "staff": r.get("staff_name"), "flags": r.get("flags"),
                       "summary": (r.get("summary") or "")[:300], "quote": (r.get("quote") or "")[:200]} for r in fr[:45]]
    for s_ in flagged.values():  # the model copies these verbatim — strip double quotes so its JSON stays valid (restart 2026-10-20)
        for f_ in s_:
            f_["summary"] = (f_["summary"] or "").replace('"', "'"); f_["quote"] = (f_["quote"] or "").replace('"', "'")
    facts = {"week": "%s – %s" % (since.strftime("%b %d"), until.strftime("%b %d, %Y")), "phone_stats": st, "graded": agg, "texts": tx_stats, "flagged_calls": flagged}
    system = ("You write the weekly Phone & Text Review for the owner of Valley Pawn (5 stores). Audience: the owner only. Plain language, "
              "no jargon, no hedging, name staff members as the data names them. Use ONLY the facts given (machine transcripts, no audio); "
              "quotes must be copied from the 'quote' fields verbatim. JSON RULES: valid JSON only, no markdown fence; never put a double quote character inside a string value — use single quotes for quoted speech. Every store section gets 3-6 bullets: the biggest problems first, "
              "one 'Praise:' bullet last when the data supports it. Return ONLY JSON: {\"cross_store\": [{\"head\": str, \"body\": str}] (3-5 items), "
              "\"stores\": {\"CUL\": [{\"head\": str, \"body\": str}], \"HAR\": [...], \"WAY\": [...], \"LEX\": [...], \"ROA\": [...]}, "
              "\"texts\": [{\"head\": str, \"body\": str}] (2-4 items), \"top3\": [str, str, str] (the three things the owner should act on this week, one line each)}. "
              "Keep every body under 70 words; the whole answer must stay under 2,500 words.")
    for attempt in range(3):
        try:
            raw, stop, otok = _ask_meta("Write this week's review from these facts.%s\n\n%s" % ((" NOTE: " + partial_note) if partial_note else "", json.dumps(facts, default=str)[:180000]),
                                        system, 12000)
            log("narrative: stop_reason=%s output_tokens=%s chars=%d" % (stop, otok, len(raw)))
            if stop == "max_tokens":
                raise ValueError("narrative cut off at max_tokens")
            m = re.search(r"(\{.*\})", raw, re.S)
            body = m.group(1) if m else raw
            try:
                return json.loads(body, strict=False)
            except Exception:
                try:
                    return json.loads(_repair_json(body), strict=False)  # stray double quotes inside prose (restart 2026-10-20)
                except Exception:
                    open(os.path.join(d_, "_raw_fail_narrative_%d.txt" % (attempt + 1)), "w").write(raw)
                    raise
        except Exception as e:
            log("narrative attempt %d failed: %s" % (attempt + 1, str(e)[:160])); time.sleep(10)
    return None


# ---------------------------------------------------------------- 6. render
def pct(a, b):
    return "%d (%d%%)" % (a, round(100.0 * a / b)) if b else str(a)


def html_doc(since, until, st, agg, tx, nar, n_rows, partial_note):
    def esc(x):
        return (str(x) if x is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    row = lambda label, vals: "<tr><td class='l'>%s</td>%s</tr>" % (label, "".join("<td>%s</td>" % esc(v) for v in vals))
    T = [row("Calls in while open", [st[s].get("in_open", 0) for s in STORES]),
         row("Missed while open", [pct(st[s].get("miss_open", 0), st[s].get("in_open", 0)) for s in STORES]),
         row("Missed callers never reached by phone", [st[s].get("never", 0) for s in STORES]),
         row("Called back (median minutes)", ["%s (%s)" % (st[s].get("cb", 0), st[s].get("median_cb_min") if st[s].get("median_cb_min") is not None else "–") for s in STORES]),
         row("Calls promising a hold on a past-due loan", [agg[s]["holds_past_due"] for s in STORES]),
         row("Account/firearm details given w/o a real ID check", [agg[s]["unverified"] for s in STORES]),
         row("Sell/pawn calls with qualifying questions", ["%d of %d" % (agg[s]["qualifying"], agg[s]["sell_calls"]) for s in STORES]),
         row("Callbacks promised / customers not helped", ["%d / %d" % (agg[s]["callback_promised"], agg[s]["no_help"]) for s in STORES]),
         row("Average service rating (1-5)", [agg[s]["rating"] if agg[s]["rating"] is not None else "–" for s in STORES])]
    if tx:
        T += [row("Text conversations / customer msgs", ["%d / %d" % (tx[s]["conversations"], tx[s]["customer_msgs"]) if s in tx and not tx[s].get("error") else "–" for s in STORES]),
              row("Text threads a customer left waiting", [tx[s]["unanswered_threads"] if s in tx and not tx[s].get("error") else "–" for s in STORES]),
              row("Automated texts (AI + missed-call) / STOPs", ["%d / %d" % (tx[s]["automated"], tx[s]["stops"]) if s in tx and not tx[s].get("error") else "–" for s in STORES])]
    def bullets(items):
        return "".join("<li><b>%s</b> %s</li>" % (esc(i.get("head", "")), esc(i.get("body", ""))) for i in (items or []))
    nar = nar or {}
    sections = "".join("<h2>%s</h2><ul>%s</ul>" % (NAMES[s].upper(), bullets((nar.get("stores") or {}).get(s))) for s in STORES)
    worst = ", ".join("%s %s %d of %d" % (w["store"], w["day"], w["missed"], w["in"]) for w in st.get("_worst_days", [])[:4])
    return """<html><head><meta charset='utf-8'><style>
body{font-family:Calibri,Helvetica,Arial,sans-serif;font-size:10pt;color:#222;margin:0.55in 0.7in}
h1{color:#2D1A5E;font-size:18pt;margin:0} .brand{color:#0099DD;font-weight:bold;font-size:9pt} .sub{color:#595959;font-size:9.5pt;margin-bottom:6pt}
h2{color:#0099DD;font-size:11.5pt;margin:10pt 0 3pt} table{border-collapse:collapse;width:100%%;margin:4pt 0} td,th{border:1px solid #999;padding:2pt 4pt;font-size:9pt}
th{background:#2D1A5E;color:#fff} td.l{width:36%%} ul{margin:2pt 0 2pt 14pt;padding:0} li{margin:0 0 3pt 0} b{color:#2D1A5E} .foot{color:#595959;font-size:8pt;margin-top:8pt}
.top{background:#F2F0F8;border-left:4px solid #2D1A5E;padding:6pt 8pt;margin:6pt 0}
</style></head><body>
<div class='brand'>VALLEY PAWN</div><h1>Phone &amp; Text Review — by Store</h1>
<div class='sub'>%s – %s &nbsp;·&nbsp; %d recorded calls read, all 5 stores &nbsp;·&nbsp; For Joshua only%s</div>
<div class='top'><b>Three things to act on this week</b><ol>%s</ol></div>
<h2>THE NUMBERS</h2><table><tr><th></th>%s</tr>%s</table>
<div class='foot'>Worst days for missed calls: %s. Store hours come from fleet/missed_call_text_config.json. Text figures are read from the Chekkit API.</div>
<h2>WHAT CUTS ACROSS EVERY STORE</h2><ul>%s</ul>
%s
<h2>TEXTS (Chekkit)</h2><ul>%s</ul>
<div class='foot'>Quotes come from machine transcripts. Play the audio in Zoom (Phone → Recordings) before acting. Every call's row is in review_native.json in the week folder.</div>
</body></html>""" % (since.strftime("%b %d"), until.strftime("%b %d, %Y"), n_rows, (" · " + esc(partial_note)) if partial_note else "",
                     "".join("<li>%s</li>" % esc(t) for t in (nar.get("top3") or [])), "".join("<th>%s</th>" % NAMES[s] for s in STORES), "".join(T),
                     esc(worst), bullets(nar.get("cross_store")), sections, bullets(nar.get("texts")))


def to_pdf(html_path, pdf_path):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        log("pdf: playwright missing (%s)" % e); return False
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome", headless=True)
            pg = b.new_page()
            pg.goto("file://" + html_path)
            pg.pdf(path=pdf_path, format="Letter", print_background=True, margin={"top": "0.3in", "bottom": "0.3in", "left": "0.3in", "right": "0.3in"})
            b.close()
        return os.path.getsize(pdf_path) > 1000
    except Exception as e:
        log("pdf: failed %s: %s" % (type(e).__name__, str(e)[:160])); return False


def drive_copy(pdf_path):
    cloud = os.path.expanduser("~/Library/CloudStorage")
    for root in glob.glob(os.path.join(cloud, "GoogleDrive-*")):
        for base in ("My Drive", "Shared drives"):
            top = os.path.join(root, base)
            if not os.path.isdir(top):
                continue
            for cur, dirs, _f in os.walk(top):
                if cur[len(top):].count(os.sep) >= 4:
                    dirs[:] = []
                if "Call Reviews" in dirs:
                    dst = os.path.join(cur, "Call Reviews", os.path.basename(pdf_path))
                    shutil.copy2(pdf_path, dst); return dst
    # no folder yet: create one under the first My Drive
    for root in glob.glob(os.path.join(cloud, "GoogleDrive-jdavis@fcfpawn.com")) + glob.glob(os.path.join(cloud, "GoogleDrive-*")):
        top = os.path.join(root, "My Drive")
        if os.path.isdir(top):
            os.makedirs(os.path.join(top, "Call Reviews"), exist_ok=True)
            dst = os.path.join(top, "Call Reviews", os.path.basename(pdf_path))
            shutil.copy2(pdf_path, dst); return dst
    return None


def deliver(since, until, nar, pdf, drive_dst, d, partial_note, render):
    lines = ["Phone & Text Review for %s – %s is ready." % (since.strftime("%b %d"), until.strftime("%b %d"))]
    for t in (nar or {}).get("top3", [])[:3]:
        lines.append("• " + str(t))
    if partial_note:
        lines.append("Incomplete: " + partial_note)
    lines.append("PDF: " + (("Google Drive › My Drive › Call Reviews › " + os.path.basename(drive_dst)) if drive_dst else pdf))
    txt = "\n".join(lines)
    stamp = dt.datetime.now(ET).strftime("%Y%m%d-%H%M%S")
    tpath = os.path.join(FLEET, "outbox", "%s-joshua-%s.txt" % (TASK, stamp))
    if render:
        print("=== DM (render only)\n" + txt); return
    os.makedirs(os.path.join(FLEET, "outbox"), exist_ok=True)
    open(tpath, "w").write(txt)
    json.dump({"channel": JOSHUA, "file": tpath}, open(tpath[:-4] + ".json", "w"))
    with open(os.path.join(OS_DIR, "CHANGELOG.md"), "r+") as f:
        body = f.read(); f.seek(0)
        f.write("## %s (weekly phone & text review, native)\n\n- weekly-phone-text-review: %s–%s graded (%s), DM'd to Joshua%s\n\n%s" % (
            dt.datetime.now(ET).strftime("%Y-%m-%d"), since, until, os.path.basename(pdf), (" — " + partial_note) if partial_note else "", body))



# ---------------------------------------------------------------- current staff only, never a Davis (Joshua 2026-10-21)
_NICK = {"JOEY": "JOSEPH", "JOE": "JOSEPH", "SANDY": "SANDI", "CHAD": "CHADD", "BENJI": "BENJIE", "BENJY": "BENJIE", "BEN": "BENJIE"}


def _staff_ok(first, store):
    """A transcript first name (or nickname) is kept only if it is ONE current, non-Davis roster person in that
    store's department (any department for PRE/unknown). Unknown/ambiguous = dropped (bin/vp_people.py rule)."""
    import vp_people
    t = re.sub(r"[^A-Z]", "", (first or "").upper())
    if not t:
        return False
    t = _NICK.get(t, t)
    dept = NAMES.get(store) if store in STORES else None

    def hits(pool):
        h = []
        for e in pool:
            for f in {e["_first"], e["_pref"]}:
                if t == f or (len(t) >= 3 and (f.startswith(t) or (len(f) >= 4 and t.startswith(f[:4])))):
                    h.append(e); break
        return h
    staff = vp_people.current_staff()
    local = hits([e for e in staff if dept and (e.get("department") or "") == dept])
    if len(local) == 1:
        return vp_people.is_reportable(local[0]["name"])
    every = hits(staff)   # e.g. Preston on a store call: must be ONE person fleet-wide, and not a Davis
    return len(every) == 1 and vp_people.is_reportable(every[0]["name"])


def _people_scrub(rows):
    """Drop non-current / Davis staff names from graded rows before anything is aggregated or written: the
    staff_name goes blank and that name is replaced by 'a staff member' in summary/quote. Call counts stay."""
    import vp_people
    dropped = []
    out = []
    fam = sorted({f for e in vp_people.current_staff() if vp_people.is_davis(e["name"]) for f in (e["_first"], e["_pref"])})
    davis_rx = re.compile(r"(?i)\b(?:%s)\s+davis\b" % "|".join(map(re.escape, fam))) if fam else None
    for r in rows:
        r = dict(r)
        for k in ("summary", "quote"):   # Davis FAMILY names only (roster) — a customer named Davis stays
            if r.get(k) and davis_rx and davis_rx.search(r[k]):
                r[k] = davis_rx.sub("a team member", r[k])
        n = (r.get("staff_name") or "").strip()
        if n and not _staff_ok(n, r.get("store")):
            dropped.append((n, "not current staff / Davis / unmatched (%s)" % r.get("store")))
            r["staff_name"] = ""
            for k in ("summary", "quote"):
                if r.get(k):
                    r[k] = re.sub(r"\b%s\b" % re.escape(n), "a staff member", r[k])
        out.append(r)
    vp_people._log("weekly-phone-text-review", dropped)
    return out

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since"); ap.add_argument("--until"); ap.add_argument("--render", action="store_true")
    ap.add_argument("--max-calls", type=int); ap.add_argument("--no-pull", action="store_true"); ap.add_argument("--no-texts", action="store_true")
    a = ap.parse_args()
    if a.since and a.until:
        since, until = dt.date.fromisoformat(a.since), dt.date.fromisoformat(a.until)
    else:
        since, until = last_week()
    d = os.path.join(CA, "week_%s" % since.isoformat()); os.makedirs(d, exist_ok=True)
    log("week %s..%s -> %s" % (since, until, d))
    notes = []
    ok = pull(since.isoformat(), until.isoformat(), d, not a.no_pull)
    if not ok:
        notes.append("Zoom pull/transcription did not finish — numbers below use what was on disk")
    if not os.path.exists(os.path.join(d, "recordings_index.json")):
        ledger("The weekly phone review could not read the week's call list from Zoom, so nothing was produced.")
        print("no recordings index"); return 2
    idx = calls_index(d)
    tx, missing = transcripts(idx)
    log("calls %d, transcripts missing %d" % (len(idx), len(missing)))
    if idx and len(missing) > 0.1 * len(idx):
        notes.append("%d of %d calls have no transcript" % (len(missing), len(idx)))
    rows, failed = grade(idx, tx, d, a.max_calls)
    if failed:
        rows2, failed = grade(idx, tx, d, a.max_calls)   # one retry pass: cached calls are skipped, only the misses re-run
        rows = rows2 or rows
    if failed and failed > 0.02 * max(len(idx), 1):      # Rule 18 only when it changes the picture (>2% of calls)
        notes.append("%d calls could not be graded" % failed)
    if a.max_calls:
        notes.append("smoke test: only the first %d calls graded" % a.max_calls)
    c = cfg()
    st = stats(d, c)
    json.dump(st, open(os.path.join(d, "stats_native.json"), "w"), indent=1, default=str)
    try:
        rows = _people_scrub(rows)
    except Exception as e:   # vp_people.RosterHold -> no DM (Rule 18), one ledger row
        if type(e).__name__ != "RosterHold":
            raise
        ledger("The weekly phone review was not sent: %s." % e)
        print("roster hold: %s" % e); return 2
    agg = aggregate(rows)
    txs = {} if a.no_texts else texts(since, until)
    json.dump(txs, open(os.path.join(d, "texts_native.json"), "w"), indent=1)
    partial = "; ".join(notes)
    nar = narrative(since, until, st, agg, rows, txs, partial, d)
    if nar is None:
        notes.append("narrative could not be written (numbers table only)"); partial = "; ".join(notes)
    tag = "%s_%s" % (since.strftime("%b%d"), until.strftime("%b%d"))
    html_path = os.path.join(d, "Phone_Text_Review_By_Store_%s.html" % tag)
    pdf_path = os.path.join(d, "Phone_Text_Review_By_Store_%s.pdf" % tag)
    open(html_path, "w").write(html_doc(since, until, st, agg, txs, nar, len(rows), partial))
    have_pdf = to_pdf(html_path, pdf_path)
    out = pdf_path if have_pdf else html_path
    drive_dst = None
    if have_pdf and not a.render:
        try:
            drive_dst = drive_copy(pdf_path)
        except Exception as e:
            log("drive copy failed: %s" % e)
    json.dump({"since": since.isoformat(), "until": until.isoformat(), "calls": len(idx), "graded": len(rows), "failed": failed, "pdf": out,
               "drive": drive_dst, "notes": notes, "finished": dt.datetime.now(ET).isoformat(timespec="seconds")},
              open(os.path.join(d, "review_status.json"), "w"), indent=1)
    deliver(since, until, nar, out, drive_dst, d, partial, a.render)
    log("done: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
