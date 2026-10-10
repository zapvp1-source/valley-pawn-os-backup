#!/usr/bin/env python3
"""chekkit_ai_responder.py — our own AI that answers customer texts sitting unanswered in Chekkit.

WHY (Joshua, 2026-09-30): Chekkit Smart Replies only fire on exact keyword phrases, so real texts
("wondering if you take portable monitors", "have two items, would you be interested") got nothing
but "we're closed". Chekkit's AI add-on is $99/mo. This does it ourselves with Claude.

HOW:
  READ  - Chekkit emails jdavis@fcfpawn.com an "Unanswered Message Alert" when a customer text has
          gone unanswered (customer name, phone, their message, store). Apple Mail already syncs that
          inbox; we read its Envelope Index + .emlx read-only (same method as mail_latest_body.py).
          No Chekkit login, no browser, no Chekkit API.
  THINK - Claude (Anthropic API, key in Keychain "vp-agent-anthropic-key" or ~/.vp_secrets/
          anthropic.json) writes ONE short reply from the store's facts and our approved answers, or
          decides to stay silent. It never quotes prices/offers, never discusses firearm inventory or
          sales, never promises anything, always labels itself "(Automated reply)".
  SEND  - mode "live" only: POST {event: ai_reply, text, caller_phone} to that store's Chekkit
          webhook (same proven path as missed_call_text.py). Chekkit sends it FROM THE STORE NUMBER
          into the customer's existing thread, where staff see it.
  mode "shadow" (default): drafts only, nothing is sent. Drafts go to
          fleet/ai_responder/drafts-YYYY-MM-DD.md for Joshua's review (last-4 of phone only).

  chekkit_ai_responder.py                 normal run (launchd, every 60 s)
  chekkit_ai_responder.py --render        read + draft, print, write no state, send nothing
  chekkit_ai_responder.py --render --hours 8     look further back (render only)
  chekkit_ai_responder.py --selftest      check key present (never prints it), mail readable, config
  chekkit_ai_responder.py --text "msg" --store HAR     draft for an ad-hoc message (prints only)

Rails: skips STOP/START/sign-offs/empty, staff + store numbers, one AI reply per customer per
cooldown, send window, honours the fleet publish guard (fleet/DRY_RUN.json). Customer numbers are
kept only as SHA-256 hashes in local, non-synced state. stdlib only.
"""
import argparse, datetime as dt, email, getpass, glob, hashlib, json, os, re, sqlite3, subprocess, sys
import urllib.error, urllib.request
from email import policy
from zoneinfo import ZoneInfo

AGENT = "chekkit-ai-responder"
OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
CFG_PATH = os.path.join(OS_DIR, "fleet", "chekkit_ai_config.json")
MCT_CFG = os.path.join(OS_DIR, "fleet", "missed_call_text_config.json")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
DRY_FLAG = os.path.join(OS_DIR, "fleet", "DRY_RUN.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
DRAFTS_DIR = os.path.join(OS_DIR, "fleet", "ai_responder")
LOCAL = os.environ.get("VP_LOCAL_DIR") or os.path.expanduser("~/Library/Logs/valleypawn/chekkit_ai_responder")
STATE = os.path.join(LOCAL, "state.json")
LOG = os.path.join(LOCAL, "run.log")
ET = ZoneInfo("America/New_York")
API = "https://api.anthropic.com/v1/messages"
STORE_ALIASES = {"culpeper": "CUL", "harrisonburg": "HAR", "lexington": "LEX", "roanoke": "ROA", "waynesboro": "WAY"}
STORE_ADDR = {"CUL": "571 James Madison Hwy, Culpeper", "HAR": "1790 East Market Street, Suite 22, Harrisonburg",
              "LEX": "125 Walker Street, Lexington (next to Dollar General)", "ROA": "2362 Peters Creek Road, Suite C, Roanoke (next to Domino's)",
              "WAY": "1321 West Broad Street, Waynesboro"}
STORE_PHONE = {"CUL": "(540) 445-5510", "HAR": "(540) 574-4500", "LEX": "(540) 461-8349", "ROA": "(540) 562-0776", "WAY": "(540) 221-6346"}
ENDERS = {"thanks", "thank you", "thank u", "ty", "ok", "okay", "k", "kk", "sounds good", "got it", "bye", "have a good day",
          "appreciate it", "no problem", "will do", "perfect", "cool", "great", "yes", "yep", "yeah", "no", "nope",
          "stop", "start", "unstop", "stop all", "unsubscribe", "cancel", "end", "quit", "👍", "🙏", "❤️"}


OPTOUT_RE = re.compile(r"\b(stop (texting|messaging|sending|contacting)|(don'?t|do not|quit|never) (text|message|contact)|remove me|take me off|unsubscribe|opt ?out|no more (texts|messages)|leave me alone)\b", re.I)
WRONG_RE = re.compile(r"\b(wrong number|who is this|who dis|i didn'?t call|not me)\b", re.I)


def now_et():
    return dt.datetime.now(ET)


def log(msg, render=False):
    line = "%s %s" % (now_et().strftime("%Y-%m-%d %H:%M:%S"), msg)
    if render:
        print(line); return
    os.makedirs(LOCAL, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def load_json(p, d):
    try:
        with open(os.path.expanduser(p)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return d


def save_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    t = p + ".tmp"
    with open(t, "w") as f:
        json.dump(obj, f, indent=1)
    os.chmod(t, 0o600); os.replace(t, p)


def h(num):
    return hashlib.sha256((num or "").encode()).hexdigest()[:24]


def digits(s):
    d = re.sub(r"\D", "", s or "")
    return d[-10:] if len(d) >= 10 else d


def ledger_once(state, key, sentence, needs_human="no"):
    today = dt.date.today().isoformat()
    if state.setdefault("ledgered", {}).get(key) == today:
        return
    state["ledgered"][key] = today
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (now_et().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, needs_human))
    except OSError:
        pass
    log("LEDGER: " + sentence)


def guard_armed():
    d = load_json(DRY_FLAG, {})
    if not d.get("active"):
        return False
    try:
        return dt.datetime.fromisoformat(d["until"].replace("Z", "+00:00")) > dt.datetime.now(dt.timezone.utc)
    except Exception:
        return False


def api_key(cfg):
    f = load_json(cfg.get("secrets_file", "~/.vp_secrets/anthropic.json"), {})
    if f.get("api_key"):
        return f["api_key"]
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", cfg["keychain_service"], "-a", getpass.getuser(), "-w"],
                           capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            return r.stdout.strip()
        r = subprocess.run(["security", "find-generic-password", "-s", cfg["keychain_service"], "-w"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


# ------------------------------------------------------------------ read Chekkit alerts from Apple Mail
def mail_env():
    envs = glob.glob(os.path.expanduser("~/Library/Mail/V*/MailData/Envelope Index"))
    return envs[0] if envs else None


def read_alerts(minutes):
    env = mail_env()
    if not env:
        raise RuntimeError("Apple Mail index not found")
    c = sqlite3.connect("file:%s?mode=ro" % env.replace(" ", "%20"), uri=True)
    cutoff = int((dt.datetime.now() - dt.timedelta(minutes=minutes)).timestamp())
    rows = list(c.execute(
        "select m.ROWID, s.subject, m.date_received, coalesce(m.global_message_id, m.message_id, m.ROWID) "
        "from messages m left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender "
        "where lower(a.address) like '%support@chekkit.io%' and (s.subject like '%Unanswered Message Alert%' or s.subject like '%: message via %') "
        "and m.date_received >= ? order by m.date_received asc", (cutoff,)))
    base = os.path.dirname(os.path.dirname(env))
    seen, out = set(), []
    for rowid, subj, ts, gid in rows:
        if gid in seen:
            continue
        hits = glob.glob(os.path.join(base, "**", "%d.emlx" % rowid), recursive=True) + \
               glob.glob(os.path.join(base, "**", "%d.partial.emlx" % rowid), recursive=True)
        if not hits:
            continue
        seen.add(gid)
        raw = open(hits[0], "rb").read()
        raw = raw[raw.index(b"\n") + 1:]
        msg = email.message_from_bytes(raw, policy=policy.default)
        part = msg.get_body(preferencelist=("plain", "html"))
        txt = part.get_content() if part else ""
        txt = re.sub(r"(?is)<(style|script|head)[^>]*>.*?</\1>", " ", txt)
        txt = re.sub(r"<[^>]+>", " ", txt)
        txt = re.sub(r"[|]", " ", txt)
        txt = re.sub(r"\s+", " ", txt).replace("&#39;", "'").replace("&amp;", "&").replace("&quot;", '"')
        is_new = ": message via " in (subj or "")
        a = parse_new(txt) if is_new else parse_alert(txt)
        if a:
            a["kind"] = "new" if is_new else "unanswered"
            sn = re.sub(r"^.*Unanswered Message Alert:\s*", "", subj or "").strip() if not is_new else re.sub(r":\s*message via .*$", "", subj or "").strip()
            if sn and not re.search(r"\d{3}\D{0,4}\d{3}", sn):
                a["name"] = sn
            a.update({"id": str(gid), "received": dt.datetime.fromtimestamp(ts, ET).isoformat(), "subject": subj or ""})
            out.append(a)
    return out


def read_api(minutes, ongoing_h=3, backup_min=10):
    """2026-10-05: PRIMARY input — the Chekkit API (one token per store, bin/chekkit_api.py).
    The alert/notification emails only arrived for some conversations (e.g. a Harrisonburg customer
    asking about firearm transfers at 1:57 PM got no AI answer and no staff answer for 4+ hours).
    For every conversation with activity in the window: take the customer's trailing message(s) that
    nobody has answered yet (no business message after them). 'ongoing' = a real staff member
    (not an automated text) texted this customer within ongoing_h hours — left to staff."""
    sys.path.insert(0, BIN)
    import chekkit_api as ck
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(minutes=minutes)
    out = []
    for code in ("CUL", "HAR", "LEX", "ROA", "WAY"):
        convs = ck.conversations_since(code, since)
        for phone10, c in convs.items():
            last = c.get("lastMessage") or {}
            if last.get("sender") != "customer":
                continue  # the newest thing in the thread is ours (or an event) — nothing waiting
            msgs = ck.messages(code, c["id"])
            trail = []
            for m in reversed(msgs):
                if m.get("sender") == "customer":
                    trail.append(m)
                elif m.get("sender") == "business":
                    break
            trail.reverse()
            trail = [m for m in trail if (ck.ts(m.get("createdAt")) or now) >= since]
            if not trail:
                continue
            first_t = ck.ts(trail[0].get("createdAt")) or now
            staff_recent = any(m.get("sender") == "business" and not ck.is_automated(m)
                               and first_t - dt.timedelta(hours=ongoing_h) <= (ck.ts(m.get("createdAt")) or first_t) < first_t
                               for m in msgs)
            # parity with the old email path: a mid-conversation text nobody has answered for
            # backup_min minutes is no longer "left to staff" — the AI picks it up (Joshua 9/30: answer texts)
            waited = (now - (ck.ts(trail[-1].get("createdAt")) or now)).total_seconds() / 60
            if staff_recent and waited >= backup_min:
                staff_recent = False
            text = " ".join((m.get("text") or "").strip() for m in trail).strip()
            if not text and any(m.get("media") for m in trail):
                text = "[sent photo(s)]"
            cust = c.get("customer") or {}
            out.append({"id": "api:" + str(trail[-1].get("id")), "kind": "api", "ongoing": staff_recent,
                        "name": (cust.get("name") or "").strip(), "phone": phone10, "text": text, "store": code,
                        "channel": trail[-1].get("channel") or "sms",
                        "received": (ck.ts(trail[-1].get("createdAt")) or now).astimezone(ET).isoformat()})
    out.sort(key=lambda a: a["received"])
    return out


ALERT_RE = re.compile(r"(?:(?P<name>[^,]{1,60}), )?\((?P<a>\d{3})\) (?P<b>\d{3}) - (?P<c>\d{4}) said [^:]{1,40} ago: "
                      r"(?P<msg>.*?) Sent to Valley Pawn ?- ?(?P<store>[A-Za-z]+)", re.S)


NEW_RE = re.compile(r"Message via (?P<chan>[A-Za-z ]+?) (?:(?P<name>[^()]{0,60}?) · )?\((?P<a>\d{3})\) (?P<b>\d{3}) - (?P<c>\d{4}) "
                    r"(?P<msg>.*?) Replying to this email will not respond to your customer\. Sent to Valley Pawn ?- ?(?P<store>[A-Za-z]+)", re.S)


def parse_new(txt):
    """Chekkit per-message email (subject '<name>: message via SMS'), turned on 2026-10-01 for near-instant replies."""
    m = NEW_RE.search(txt)
    if not m:
        return None
    code = STORE_ALIASES.get(m.group("store").lower())
    if not code:
        return None
    return {"name": (m.group("name") or "").strip(), "phone": m.group("a") + m.group("b") + m.group("c"),
            "text": m.group("msg").strip(), "store": code, "channel": m.group("chan").strip()}


def parse_alert(txt):
    ms = list(ALERT_RE.finditer(txt))
    if not ms:
        return None
    m = ms[-1]
    code = STORE_ALIASES.get(m.group("store").lower())
    if not code:
        return None
    name = (m.group("name") or "").strip()
    name = re.sub(r"^.*Unanswered Message From ", "", name).strip()
    if re.search(r"\d{3}\) \d{3}", name):
        name = ""
    return {"name": name, "phone": m.group("a") + m.group("b") + m.group("c"), "text": m.group("msg").strip(), "store": code}


# ------------------------------------------------------------------ decide + draft
def store_open(code, when, mct):
    s = mct["stores"][code]
    if when.weekday() not in s["days"]:
        return False
    # 2026-10-01: optional per-weekday close (CUL/ROA close 17:00 on Saturday) — config close_by_weekday
    close = s.get("close_by_weekday", {}).get(str(when.weekday()), s["close"])
    return s["open"] <= when.strftime("%H:%M") < close


def next_open(code, when, mct):
    s = mct["stores"][code]
    for i in range(0, 8):
        d = when + dt.timedelta(days=i)
        if d.weekday() in s["days"] and (i > 0 or when.strftime("%H:%M") < s["open"]):
            day = "today" if i == 0 else ("tomorrow" if i == 1 else d.strftime("%A"))
            return "%s at 10am" % day
    return "our next open day"


def is_ender(t):
    x = re.sub(r"[^\w\s']", "", (t or "").lower()).strip()
    return (not x and len((t or "").strip()) <= 3) or x in ENDERS or len(x) <= 1


def staff_numbers(mct):
    nums = {digits(n) for n in mct.get("exclude_numbers", [])}
    nums |= {digits(s.get("did")) for s in mct["stores"].values()}
    r = load_json(ROSTER, {})
    for p in (r.get("employees", []) if isinstance(r, dict) else r) or []:
        if isinstance(p, dict) and p.get("phone"):
            nums.add(digits(p["phone"]))
    return {n for n in nums if n}


SYSTEM = """You are the texting assistant for Valley Pawn, a family pawn shop with five stores in Virginia. You are answering a customer text that has gone unanswered. A real team member will also see the conversation.

Write ONE short, friendly, plain text message (1-3 sentences, no emojis, no markdown) OR decide to stay silent.

Hard rules:
- Never quote a price, value, offer, loan amount, interest amount or balance. Staff make every offer. If they ask what we'd pay, ask for photos/details and say the team will text them an offer.
- Never discuss specific firearms in stock, firearm prices or firearm sales by text. For guns: "call the store or stop in". FFL transfer facts are fine.
- Never promise anything, never invent policies, services, hours or facts not given below. If unsure, say a team member will follow up.
- If the store is closed now, say when it opens next (use exactly the phrase given) and that the team will follow up then.
- If they are selling/pawning something we take: ask for a few clear photos, brand/model, condition, what comes with it, sell or pawn, and what they hope to get.
- If it is something we do NOT take, say so kindly.
- If the message is only a reply to an earlier staff conversation you cannot see (e.g. "yes", "ok I will", "what about the other one", a bare number, a photo caption with no question), or is personal, a complaint, legal, a dispute about a specific loan/ticket, spam, or anything you cannot answer safely: stay silent (action "skip").
- If they ask to stop being texted in any wording, or say wrong number / who is this: stay silent (action "skip", reason "opt-out" or "wrong number").
- Answer only what they asked. Do not list things we don't take, or mention firearms, unless their message is about that.
- End the text with " (Automated reply - a team member will follow up.)"
- Keep under %(max)d characters total.

Respond with ONLY a JSON object: {"action": "reply" or "skip", "reason": "<few words>", "text": "<the message, empty if skip>"}"""


def build_user(a, cfg, mct, when):
    code = a["store"]; s = mct["stores"][code]
    op = store_open(code, when, mct)
    facts = "\n".join("- " + f for f in cfg.get("extra_facts", []))
    return ("STORE: Valley Pawn %s, %s. Phone %s. Hours: %s (closed other days).\n"
            "RIGHT NOW: %s, %s. The store is %s.%s\n\nBUSINESS FACTS:\n%s\n\n"
            "CUSTOMER%s TEXTED:\n\"%s\"") % (
        s["name"], STORE_ADDR[code], STORE_PHONE[code], s.get("hours_text", ""),
        when.strftime("%A"), when.strftime("%-I:%M %p"), "OPEN" if op else "CLOSED",
        "" if op else " Next open: %s." % next_open(code, when, mct), facts,
        (" (" + a["name"].split()[0] + ")") if a.get("name") else "", a["text"][:1200])


def ask_claude(key, cfg, a, mct, when):
    body = {"model": cfg["model"], "max_tokens": 2000, "system": SYSTEM % {"max": cfg.get("max_reply_chars", 420)},
            "messages": [{"role": "user", "content": build_user(a, cfg, mct, when)}]}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.load(r)
    out = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    if not out.strip():
        return {"action": "skip", "reason": "no answer from Claude (stop_reason=%s)" % resp.get("stop_reason"), "text": ""}
    m = re.search(r"\{.*\}", out, re.S)
    try:
        d = json.loads(m.group(0), strict=False) if m else None
    except ValueError:
        d = None
    if not isinstance(d, dict):
        am = re.search(r'"action"\s*:\s*"(\w+)"', out); tm = re.search(r'"text"\s*:\s*"(.*)"\s*\}?\s*$', out, re.S)
        rm = re.search(r'"reason"\s*:\s*"([^"]*)"', out)
        d = {"action": am.group(1) if am else "skip", "reason": (rm.group(1) if rm else "unparseable:" + out[:200].replace("\n", " ")),
             "text": tm.group(1).replace('\\"', '"').strip() if tm else ""}
    t = (d.get("text") or "").strip()
    if d.get("action") == "reply":
        if not t or len(t) > cfg.get("max_reply_chars", 420) + 40:
            return {"action": "skip", "reason": "reply empty/too long", "text": t}
        if re.search(r"\$\s?\d", re.sub(r"\$25 per firearm", "", t)):
            return {"action": "skip", "reason": "contained a dollar figure", "text": t}
        if "(Automated reply" not in t:
            t += " (Automated reply - a team member will follow up.)"
        d["text"] = t
    return d


def post_event(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return 200 <= r.status < 300


def write_draft(a, d, sent, when):
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    p = os.path.join(DRAFTS_DIR, "drafts-%s.md" % when.strftime("%Y-%m-%d"))
    new = not os.path.exists(p)
    with open(p, "a") as f:
        if new:
            f.write("# AI text replies — %s\n\n| Time | Store | Customer | They said | AI would reply | Status |\n|---|---|---|---|---|---|\n" % when.strftime("%a %b %-d, %Y"))
        who = (a.get("name") or "").split(" ")[0] + " …" + a["phone"][-4:]
        cell = lambda s: (s or "").replace("|", "/").replace("\n", " ")
        f.write("| %s | %s | %s | %s | %s | %s |\n" % (when.strftime("%-I:%M %p"), a["store"], cell(who), cell(a["text"][:300]),
                cell(d.get("text") if d.get("action") == "reply" else "— (silent: %s)" % d.get("reason", "")), sent))


def write_event(when, a, action, reason, open_now):
    """Metrics feed for bin/texting_scorecard.py — no phone numbers, no names."""
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    with open(os.path.join(DRAFTS_DIR, "events-%s.jsonl" % when.strftime("%Y-%m-%d")), "a") as f:
        f.write(json.dumps({"ts": when.isoformat(timespec="seconds"), "store": a["store"], "open": open_now,
                            "action": action, "reason": reason, "chars": len(a.get("text") or "")}) + "\n")


def heartbeat(when, note):
    save_json(os.path.join(LOCAL, "heartbeat.json"), {"ts": when.isoformat(timespec="seconds"), "note": note})


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true"); ap.add_argument("--hours", type=float)
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--text"); ap.add_argument("--store", default="HAR")
    ap.add_argument("--at", help="pretend time (ISO) for --text")
    ap.add_argument("--send-test", help="with --text: actually send the drafted reply to THIS number (e.g. +18045551212) from --store, to prove the live path")
    args = ap.parse_args()
    cfg = load_json(CFG_PATH, None); mct = load_json(MCT_CFG, None)
    if not cfg or not mct:
        print("config missing"); return 2
    key = api_key(cfg)
    if args.selftest:
        env = mail_env()
        print("config ok, mode=%s model=%s" % (cfg["mode"], cfg["model"]))
        print("anthropic key:", "PRESENT" if key else "MISSING (Keychain %s / %s)" % (cfg["keychain_service"], cfg.get("secrets_file")))
        print("apple mail index:", "found" if env else "NOT FOUND")
        if env:
            try:
                al = read_alerts(24 * 60)
                print("unanswered alerts readable, last 24h:", len(al))
                for a in al[-5:]:
                    print("  ", a["received"][11:16], a["store"], "…" + a["phone"][-4:], "|", a["text"][:70])
            except Exception as e:
                print("mail read error:", type(e).__name__, e)
        if key:
            try:
                d = ask_claude(key, cfg, {"name": "Test", "phone": "0000000000", "text": "are you open today?", "store": "CUL"}, mct, now_et())
                print("claude call ok:", d.get("action"), "|", (d.get("text") or "")[:120])
            except Exception as e:
                print("claude call error:", type(e).__name__, getattr(e, "code", ""))
        return 0
    when = dt.datetime.fromisoformat(args.at).astimezone(ET) if args.at else now_et()
    if args.text:
        if not key:
            print("no API key"); return 1
        d = ask_claude(key, cfg, {"name": "", "phone": "0000000000", "text": args.text, "store": args.store.upper()}, mct, when)
        print(json.dumps(d, indent=1))
        if args.send_test and d.get("action") == "reply":
            s = mct["stores"][args.store.upper()]
            ok = post_event(s["webhook"], {"event": cfg.get("send_event", "ai_reply"), "text": d["text"],
                                           "caller_phone": args.send_test, "store": s["name"]})
            print("TEST SEND", "ok" if ok else "FAILED", "to …" + args.send_test[-4:], "via", s["name"], "event", cfg.get("send_event"))
        return 0

    render = args.render
    state = load_json(STATE, {}) if not render else {}
    state.setdefault("processed", {}); state.setdefault("replied", {})
    lo, hi = cfg.get("send_window", ["07:30", "21:30"])
    if not render and not (lo <= when.strftime("%H:%M") < hi):
        return 0
    if not key:
        if not render:
            ledger_once(state, "key", "The AI text responder has no Claude API key yet, so it is not drafting replies.",
                        "yes — add the Claude API key once")
            save_json(STATE, state)
        else:
            print("no API key — cannot draft")
        return 1
    try:
        look = cfg.get("lookback_minutes", 45)
        # 2026-10-09: send_window is ["00:00","24:00"] since 10/1 (24/7). strptime("24:00") raised ValueError in
        # this overnight catch-up branch during 00:00-00:44 every night (ledger "could not read the Chekkit alert
        # emails (ValueError)" 10/3-10/9). A 24/7 window has no overnight gap to catch up, so skip the branch.
        if not render and hi < "24:00" and when.strftime("%H:%M") < (dt.datetime.strptime(lo, "%H:%M") + dt.timedelta(minutes=45)).strftime("%H:%M"):
            # first 45 min of the day: also catch texts that arrived overnight after the window closed
            prev_close = dt.datetime.combine(when.date() - dt.timedelta(days=1), dt.datetime.strptime(hi, "%H:%M").time(), ET)
            look = max(look, int((when - prev_close).total_seconds() // 60) + 15)
        mins = int((args.hours * 60) if (render and args.hours) else look)
        try:
            alerts = read_api(mins, cfg.get("ongoing_conversation_hours", 3), cfg.get("unanswered_backup_minutes", 10))
            source = "api"
        except Exception as e:  # API down -> old email path, so replies never stop entirely
            log("chekkit api read failed (%s) - falling back to alert emails" % type(e).__name__, render)
            alerts = read_alerts(mins); source = "mail"
        if render:
            print("source:", source, "| items:", len(alerts))
    except Exception as e:
        if not render:
            ledger_once(state, "mail", "The AI text responder could not read the Chekkit alert emails (%s)." % type(e).__name__)
            save_json(STATE, state)
        else:
            print("mail read error", e)
        return 1
    staff = staff_numbers(mct) - {digits(n) for n in cfg.get("test_numbers", [])}
    live = cfg.get("mode") == "live" and not guard_armed() and not render  # 2026-10-05: --render must NEVER send (it did; see CHANGELOG)
    mct_texted = load_json(os.path.expanduser("~/Library/Logs/valleypawn/missed_call_text/state.json"), {}).get("texted", {})
    state.setdefault("inbound", {})
    ongoing_h = cfg.get("ongoing_conversation_hours", 3)
    cutoff = when - dt.timedelta(hours=cfg.get("cooldown_hours", 6))
    for a in alerts:
        if a["id"] in state["processed"]:
            continue
        ph = digits(a["phone"]); hk = h(ph)
        reason = None
        if a.get("kind") == "new":
            # Instant path: only the FIRST text of a conversation (or a reply to our missed-call text).
            # Mid-conversation texts are left to staff; the 10-minute unanswered alert is the backup.
            prev = state["inbound"].get(hk)
            state["inbound"][hk] = a["received"]
            try:
                import hashlib as _hl
                mc = mct_texted.get(_hl.sha256(("+1" + ph).encode()).hexdigest()[:24])
            except Exception:
                mc = None
            recent_mc = bool(mc) and dt.datetime.fromisoformat(mc.replace("Z", "+00:00")) > when - dt.timedelta(hours=6)
            if prev and dt.datetime.fromisoformat(prev) > dt.datetime.fromisoformat(a["received"]) - dt.timedelta(hours=ongoing_h) and not recent_mc:
                reason = "ongoing conversation - left to staff (10-min alert is the backup)"
        if a.get("kind") == "api" and a.get("ongoing"):
            reason = "ongoing conversation - left to staff (10-min alert is the backup)"
        if reason:
            pass  # ongoing conversation, decided above
        elif ph in staff:
            reason = "staff/store number"
        elif is_ender(a["text"]):
            reason = "sign-off/opt-out/empty"
        elif OPTOUT_RE.search(a["text"]):
            reason = "opt-out request - staff must unsubscribe this customer"
        elif WRONG_RE.search(a["text"]) and len(a["text"]) < 80:
            reason = "wrong number / who is this"
        elif hk in state["replied"] and dt.datetime.fromisoformat(state["replied"][hk]) > cutoff:
            reason = "already replied to this customer recently"
        if reason:
            log("skip %s …%s: %s" % (a["store"], ph[-4:], reason), render)
            state["processed"][a["id"]] = when.isoformat()
            if not render:
                write_event(when, a, "skip", reason, store_open(a["store"], when, mct))
                if reason.startswith("opt-out"):
                    write_draft(a, {"action": "skip", "reason": reason}, "OPT-OUT - unsubscribe in Chekkit", when)
            continue
        day = when.strftime("%Y-%m-%d")
        if state.get("calls_day") != day:
            state["calls_day"], state["calls"] = day, 0
        if state["calls"] >= cfg.get("max_ai_calls_per_day", 300):
            if not render:
                ledger_once(state, "cap", "The AI text responder hit its daily limit of %d replies; it paused until tomorrow." % cfg.get("max_ai_calls_per_day", 300))
            break
        state["calls"] = state.get("calls", 0) + 1
        try:
            d = ask_claude(key, cfg, a, mct, when)
        except Exception as e:
            log("claude error %s …%s: %s %s" % (a["store"], ph[-4:], type(e).__name__, getattr(e, "code", "")), render)
            if not render and isinstance(e, urllib.error.HTTPError) and e.code in (401, 403):
                ledger_once(state, "auth", "The Claude API key for the AI text responder was rejected.", "yes — replace the Claude API key")
                save_json(STATE, state)
                return 1
            continue
        status = "draft only"
        if d.get("action") == "reply" and live:
            s = mct["stores"][a["store"]]
            try:
                ok = post_event(s["webhook"], {"event": cfg.get("send_event", "ai_reply"), "text": d["text"],
                                               "caller_phone": "+1" + ph, "store": s["name"]})
            except Exception as e:
                ok = False; log("POST failed %s …%s: %s" % (a["store"], ph[-4:], e), render)
            status = "SENT" if ok else "send failed"
            if ok:
                state["replied"][hk] = when.isoformat()
                try:
                    subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_receipt.py"), "write", AGENT, "--surface", "file",
                                    "--target", "chekkit-webhook:%s" % a["store"]], capture_output=True, timeout=15)
                except Exception:
                    pass
        elif d.get("action") == "reply":
            state["replied"][hk] = when.isoformat()
        log("%s %s …%s: %s | %s" % (status if d.get("action") == "reply" else "silent", a["store"], ph[-4:],
                                     d.get("reason", ""), (d.get("text") or "")[:160]), render)
        if render:
            print("   they said:", a["text"][:200])
        else:
            write_draft(a, d, status if d.get("action") == "reply" else "silent", when)
            write_event(when, a, "reply" if d.get("action") == "reply" else "silent", d.get("reason", ""), store_open(a["store"], when, mct))
            state["processed"][a["id"]] = when.isoformat()
    if not render:
        heartbeat(when, "ok, %d alerts in window" % len(alerts))
        wk = (when - dt.timedelta(days=3)).isoformat()
        state["processed"] = {k: v for k, v in state["processed"].items() if v > wk}
        save_json(STATE, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
