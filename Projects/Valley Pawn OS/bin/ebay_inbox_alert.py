#!/usr/bin/env python3
"""ebay_inbox_alert.py — eBay Inbox Alert (native, no Claude). Built 2026-10-22 on Joshua's ask:
"how can we automate the messaging? or get visibility on it" — 232 unread eBay messages across the 5
accounts on 10/21, incl. 18 return/refund + 6 case messages; unanswered cases are what put Harrisonburg
Below Standard.

READ-ONLY against eBay: the only calls are GetMyMessages (headers + bodies for the few that are shown).
It never replies to a buyer, never marks anything read, never touches a listing/order/case.

WHAT IT DOES, per store account, last 14 days of the eBay inbox:
  WAITING  — a buyer/member wrote to us and nobody has replied yet (Replied=false). Repeats every run
             until answered: that is the point. Oldest first, with how long they have waited.
  ACTION   — eBay's own notices that need someone in Seller Hub: return requests, cases/disputes,
             cancellation requests, item-not-received / not-as-described. Shown once (new since the
             last alert), so nobody gets nagged twice about the same notice.
  Everything else eBay sends (marketing, fee notices, listing confirmations) is ignored.

WHO GETS WHAT (same store-team map and roster check as ebay_ship_alert.py / loan_layaway_dms.py)
  --slot am (10:15 Mon–Sat) and --slot pm (15:15 Mon–Sat): each OPEN store's team gets ONE DM if it has
  anything WAITING or a new ACTION notice. Nothing to report = nothing sent.
  Joshua: ONE plain DM on the am slot, only if any buyer has waited 24 h+ or a case/dispute notice is new.
  Failures: one row in fleet/FAILURE_LEDGER.md, nothing to Slack (Failure policy v3 / Rule 16).

  ebay_inbox_alert.py --slot am|pm            send (launchd wrapper; gated by vp_live.sh)
  ebay_inbox_alert.py --slot am|pm --render   print every DM, send nothing, state untouched
  ebay_inbox_alert.py --probe                 print a per-store sample of raw message headers (no Slack)
"""
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from zoneinfo import ZoneInfo
    ET_TZ = ZoneInfo("America/New_York")
except Exception:  # pragma: no cover
    ET_TZ = dt.timezone(dt.timedelta(hours=-4))

AGENT = "ebay-inbox-alert"
OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
sys.path.insert(0, BIN)
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.expanduser("~/Library/Logs/valleypawn/ebay-inbox-alert.state.json")
JOSHUA = "U03BB52MDSA"
NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
READ_CALLS = {"GetMyMessages"}
LOOKBACK_DAYS = 14
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
TEAM = {  # identical to ebay_ship_alert.py TEAM; filtered against hr/ROSTER.json at send time
    "CUL": ["U04C5DL5EKH"],
    "HAR": ["U09UTFT4P7X", "U03BFDJH31B"],
    "LEX": ["U09H9ES2LKA", "U05TV57FH0B"],
    "ROA": ["U0631AECK4K", "U063E87TM70"],
    "WAY": ["U04U136MF6V"],
}
EBAY_SENDERS = {"ebay", "ebay@ebay.com", "ebay customer service"}
CASE_RE = re.compile(r"\bcase\b|dispute|claim|item not received|not as described|money back guarantee|escalat", re.I)
RETURN_RE = re.compile(r"return request|requested a return|wants to return|return (was )?(opened|started)|return.*(waiting|respond|action)", re.I)
CANCEL_RE = re.compile(r"cancel", re.I)
# eBay notices that are informational even though they mention a keyword
OFFER_RE = re.compile(r"[$£€]\s?\d|\boffer|\bpay\b|\btake \d|\baccept|\bdeal\b|\bbuy it\b|best price|lowest|acept|meet me|middle|how about \d|\bi'?ll give|\b\d{2,5}(\.\d{2})?\s*\?", re.I)
THANKS_RE = re.compile(r"^(ok(ay)?|k|thanks?( you)?( so much| again)?|thx|ty|great|perfect|super|awesome|got it|will do|sounds good|no problem|appreciate it)[\s,.!:)]*((thanks?|thank you)( so much| again)?)?[\s.!]*$", re.I)
NOISE_RE = re.compile(r"has been refunded|processing your refund|refund (has been |was )?(issued|sent)|you('ve| have) (sent|issued) a refund|return (closed|completed)|case (closed|resolved)"
                      r"|payout|invoice|fee credit|promot|newsletter|tips|webinar|survey", re.I)


# ---------------------------------------------------------------- store calendar (same as ebay_ship_alert.py)
def open_codes(day):
    wd = day.isoweekday()
    if wd == 7:
        return set()
    if wd == 3:
        if day >= dt.date(2026, 10, 14):
            return {"CUL", "ROA", "WAY"}
        return {"CUL", "ROA"} if day >= dt.date(2026, 9, 30) else {"CUL"}
    return {c for c, _ in STORES}


# ---------------------------------------------------------------- eBay (read only)
def load_tokens():
    sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
    from ebay_store_tokens import STORES as TOK, APP_ID, DEV_ID, CERT_ID  # never hardcode
    return {s["name"].lower(): s["token"] for s in TOK}, (APP_ID, DEV_ID, CERT_ID)


def ebay_call(tok, keys, name, inner, retries=3):
    if name not in READ_CALLS:
        raise RuntimeError("refusing non-read eBay call %s" % name)
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="%s">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            % (name, NS, tok, inner, name)).encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
         "X-EBAY-API-CALL-NAME": name, "X-EBAY-API-APP-NAME": keys[0],
         "X-EBAY-API-DEV-NAME": keys[1], "X-EBAY-API-CERT-NAME": keys[2],
         "X-EBAY-API-IAF-TOKEN": tok, "Content-Type": "text/xml"}
    last = None
    for i in range(retries):
        try:
            r = ET.fromstring(urlopen(Request(URL, data=body, headers=h), timeout=90).read().decode("utf-8"))
            ack = r.findtext("{%s}Ack" % NS)
            if ack == "Failure":
                msg = " ".join(e.text or "" for e in r.iter("{%s}LongMessage" % NS))
                raise RuntimeError("%s Ack=Failure: %s" % (name, msg[:200]))
            return r
        except (URLError, HTTPError, ET.ParseError, OSError) as e:
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError("%s failed after %d tries: %s" % (name, retries, last))


def T(el, tag, d=None):
    x = el.find("{%s}%s" % (NS, tag))
    return x.text.strip() if x is not None and x.text else d


def pts(s):
    try:
        return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def get_headers(tok, keys, now_utc):
    win = "<StartTime>%s</StartTime><EndTime>%s</EndTime>" % (
        (now_utc - dt.timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        now_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    out, page, pages = [], 1, 1
    while page <= min(pages, 5):  # cap 1,000 headers per store
        r = ebay_call(tok, keys, "GetMyMessages", win + "<DetailLevel>ReturnHeaders</DetailLevel><Pagination>"
                      "<EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>" % page)
        for m in r.iter("{%s}Message" % NS):
            folder = m.find("{%s}Folder" % NS)
            out.append({
                "id": T(m, "MessageID"), "sender": T(m, "Sender") or "", "subject": T(m, "Subject") or "",
                "received": T(m, "ReceiveDate"), "read": (T(m, "Read") or "").lower() == "true",
                "replied": (T(m, "Replied") or "").lower() == "true", "type": T(m, "MessageType") or "",
                "item_id": T(m, "ItemID"), "item_title": T(m, "ItemTitle"),
                "folder": T(folder, "FolderID") if folder is not None else None,
                "response_enabled": (T(m.find("{%s}ResponseDetails" % NS), "ResponseEnabled") or "").lower() == "true"
                if m.find("{%s}ResponseDetails" % NS) is not None else None,
            })
        pr = r.find("{%s}PaginationResult" % NS)
        pages = int(T(pr, "TotalNumberOfPages", "1") or 1) if pr is not None else 1
        page += 1
    return out


def get_snippets(tok, keys, ids):
    """Body text for the messages we show (10 ids per call). Best effort — a failure just drops the snippet."""
    snip = {}
    for i in range(0, len(ids), 10):
        chunk = ids[i:i + 10]
        try:
            r = ebay_call(tok, keys, "GetMyMessages", "<DetailLevel>ReturnMessages</DetailLevel><MessageIDs>%s</MessageIDs>"
                          % "".join("<MessageID>%s</MessageID>" % x for x in chunk), retries=2)
            for m in r.iter("{%s}Message" % NS):
                txt = T(m, "Text") or ""
                txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
                txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
                txt = re.sub(r"\s+", " ", txt).strip()
                # eBay's body = preview, then "New message from: <user> (<score>) <the buyer's words> --> Reply ..."
                mm = re.search(r"New message from:\s*\S+\s*\(\s*[\d,]+\s*\)\s*(.+?)(?:\s*-->|\s+Reply\s|$)", txt, re.I)
                if mm:
                    txt = mm.group(1)
                snip[T(m, "MessageID")] = txt[:300]
        except Exception as e:
            print("snippet fetch failed: %s" % str(e)[:120])
    return snip


# ---------------------------------------------------------------- classification
def is_ebay(m):
    s = (m["sender"] or "").strip().lower()
    return s in EBAY_SENDERS or s.startswith("ebay")


def classify(m):
    subj = m["subject"]
    if not is_ebay(m):
        if m["folder"] not in (None, "0"):          # sent / archive folders are never "waiting"
            return None
        return "WAITING" if not m["replied"] else None
    if NOISE_RE.search(subj):
        return None
    if CASE_RE.search(subj):
        return "CASE"
    if RETURN_RE.search(subj):
        return "RETURN"
    if CANCEL_RE.search(subj) and "request" in subj.lower():
        return "CANCEL"
    return None


def age_txt(hours):
    if hours < 1:
        return "under 1 hr"
    if hours < 48:
        return "%d hr" % hours
    return "%d days" % (hours // 24)


def title_short(t, n=48):
    t = (t or "").strip()
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def store_message(name, waiting, actions, snips, now_utc):
    if not waiting and not actions:
        return None
    parts = ["📬 *eBay messages — %s*" % name]
    if waiting:
        rows = []
        for m in waiting[:10]:
            since = pts(m.get("waiting_since") or m["received"])
            h = int((now_utc - since).total_seconds() // 3600) if since else 0
            flag = " ⚠️" if h >= 24 else ""
            s = snips.get(m["id"]) or re.sub(r"\s*#\d+$", "", m["subject"])
            money = " 💰" if OFFER_RE.search(s) else ""
            extra = " (+%d earlier)" % (m["n_unanswered"] - 1) if m.get("n_unanswered", 1) > 1 else ""
            rows.append("• %s%s%s — %s: \"%s\"%s — %s" % (age_txt(h), flag, money, m["sender"], title_short(s, 110), extra,
                                                          title_short(m["item_title"] or "no item", 50)))
        more = "\n…and %d more older conversations." % (len(waiting) - 10) if len(waiting) > 10 else ""
        parts.append("*Buyers waiting for a reply* (newest first · ⚠️ = over 24 hr · 💰 = wants to buy / making an offer):\n" + "\n".join(rows) + more)
    if actions:
        lab = {"CASE": "Case", "RETURN": "Return", "CANCEL": "Cancel request"}
        rows = ["• %s — %s" % (lab[k], title_short(m["subject"], 110)) for k, m in actions[:12]]
        parts.append("*New return / case notices — handle in Seller Hub today:*\n" + "\n".join(rows))
    parts.append("Reply in eBay → Messages. A case left without a response counts against our seller rating. Thank you!")
    return "\n\n".join(parts)


# ---------------------------------------------------------------- plumbing
def ledger(sentence):
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (
                dt.datetime.now(ET_TZ).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def send(user, text):
    env = dict(os.environ, VP_TASK=AGENT)
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", user, text],
                       capture_output=True, text=True, timeout=60, env=env)
    return p.returncode == 0, (p.stderr or p.stdout).strip()[:160]


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"slots": {}, "seen_actions": {}}


def save_state(s):
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        cutoff = (dt.date.today() - dt.timedelta(days=45)).isoformat()
        s["slots"] = {k: v for k, v in s.get("slots", {}).items() if k[:10] >= cutoff}
        s["seen_actions"] = {k: v for k, v in s.get("seen_actions", {}).items() if v >= cutoff}
        tmp = STATE + ".tmp"
        json.dump(s, open(tmp, "w"), indent=1)
        os.replace(tmp, STATE)
    except OSError:
        pass


def main():
    args = sys.argv[1:]
    render, probe = "--render" in args, "--probe" in args
    slot = args[args.index("--slot") + 1] if "--slot" in args else None
    if not probe and slot not in ("am", "pm"):
        print("usage: ebay_inbox_alert.py --slot am|pm [--render] | --probe")
        return 2
    now_utc = dt.datetime.now(dt.timezone.utc)
    today = now_utc.astimezone(ET_TZ).date()
    open_today = open_codes(today)
    if not probe and not render and not open_today:
        print("no store open today — nothing to do")
        return 0
    state = load_state()
    slot_key = "%s-%s" % (today.isoformat(), slot)
    if not probe and not render and state["slots"].get(slot_key):
        print("slot %s already sent — exit" % slot_key)
        return 0
    try:
        toks, keys = load_tokens()
    except Exception as e:
        print("eBay credentials unreadable:", e)
        if not (render or probe):
            ledger("The eBay message reminders did not go out — the eBay store credentials could not be read.")
        return 1

    results, failed = {}, []
    for code, name in STORES:
        tok = toks.get(name.lower())
        if not tok:
            failed.append(name)
            continue
        try:
            hdrs = get_headers(tok, keys, now_utc)
        except Exception as e:
            print("%s: %s" % (name, e))
            failed.append(name)
            continue
        if probe:
            from collections import Counter
            print("\n===== %s: %d headers in %dd" % (name, len(hdrs), LOOKBACK_DAYS))
            print("types:", dict(Counter(h["type"] for h in hdrs)))
            print("folders:", dict(Counter(h["folder"] for h in hdrs)), " replied:", dict(Counter(h["replied"] for h in hdrs)))
            print("senders(top):", Counter("eBay" if is_ebay(h) else "member" for h in hdrs))
            for h in hdrs[:25]:
                print("  %s | %-22s | %-18s | rd=%s rp=%s f=%s | %s | %s" % (
                    (h["received"] or "")[:16], (h["sender"] or "")[:22], h["type"][:18], int(h["read"]), int(h["replied"]),
                    h["folder"], classify(h), (h["subject"] or "")[:90]))
            continue
        # one line per conversation (buyer + item): waiting only if the buyer's LATEST message has no reply
        convs = {}
        for h in hdrs:
            if is_ebay(h) or h["folder"] not in (None, "0"):
                continue
            key = ((h["sender"] or "").lower(), h["item_id"] or re.sub(r"^re:\s*", "", h["subject"] or "", flags=re.I))
            convs.setdefault(key, []).append(h)
        waiting = []
        for key, ms in convs.items():
            ms.sort(key=lambda h: h["received"] or "")
            last = ms[-1]
            if last["replied"]:
                continue
            unanswered = [m for m in ms if not m["replied"]]
            first_unans = next((m for m in ms if not m["replied"] and all(not x["replied"] for x in ms[ms.index(m):])), last)
            waiting.append(dict(last, n_unanswered=len(unanswered), waiting_since=first_unans["received"]))
        actions = []
        for h in sorted(hdrs, key=lambda h: h["received"] or ""):
            k = classify(h)
            if k in ("CASE", "RETURN", "CANCEL") and h["id"] not in state["seen_actions"]:
                actions.append((k, h))
        snips = get_snippets(tok, keys, [h["id"] for h in waiting if h["id"]][:40])
        # a last message that only says thanks / ok needs no answer — drop it
        waiting = [h for h in waiting if not THANKS_RE.match((snips.get(h["id"]) or "").strip())]
        waiting.sort(key=lambda h: h["received"] or "", reverse=True)  # freshest first: those buyers are still shopping
        results[code] = (waiting, actions, snips)
        print("%s: %d headers — waiting %d (24h+ %d), new return/case notices %d" % (
            name, len(hdrs), len(waiting),
            sum(1 for h in waiting if pts(h.get("waiting_since") or h["received"]) and now_utc - pts(h.get("waiting_since") or h["received"]) >= dt.timedelta(hours=24)),
            len(actions)))
    if probe:
        return 0
    if failed and not render:
        ledger("eBay message reminders could not check %s this run (eBay did not answer or the store sign-in has expired)."
               % ", ".join(failed))

    try:
        import vp_people
        active = {e.get("slack_id") for e in json.load(open(ROSTER))["employees"]
                  if e.get("slack_id") and not vp_people.is_davis(e.get("name")) and not vp_people.is_davis(e.get("email"))}
    except Exception as e:
        print("roster unreadable (%s) — refusing to guess who is employed" % e)
        if not render:
            ledger("The eBay message reminders were not sent — the staff roster could not be read.")
        return 1

    outbox = []
    for code, name in STORES:
        if code not in results or (code not in open_today and not render):
            continue
        waiting, actions, snips = results[code]
        text = store_message(name, waiting, actions, snips, now_utc)
        if not text:
            continue
        for uid in TEAM.get(code, []):
            if uid in active:
                outbox.append((uid, code, text))
            else:
                print("skip %s (%s): not on the active roster" % (uid, code))

    if slot == "am":
        rows = []
        for code, name in STORES:
            if code not in results:
                continue
            waiting, actions, _ = results[code]
            old = sum(1 for h in waiting if pts(h.get("waiting_since") or h["received"]) and now_utc - pts(h.get("waiting_since") or h["received"]) >= dt.timedelta(hours=24))
            cases = sum(1 for k, _ in actions if k == "CASE")
            bits = []
            if old:
                bits.append("%d buyer%s waiting 24 hr+" % (old, "" if old == 1 else "s"))
            if cases:
                bits.append("%d new case notice%s" % (cases, "" if cases == 1 else "s"))
            if bits:
                rows.append("• %s: %s" % (name, ", ".join(bits)))
        if rows:
            outbox.append((JOSHUA, "JOSHUA", "📬 eBay messages — needs attention this morning:\n" + "\n".join(rows)
                           + "\n\nEach store has been sent its list."))

    if render:
        print("=== RENDER ONLY (%s slot, %s) — %d DM(s) ===" % (slot, today, len(outbox)))
        for uid, code, text in outbox:
            print("\n--- to %s (%s) ---\n%s" % (uid, code, text))
        return 0

    sent, bad = 0, []
    for uid, code, text in outbox:
        ok, err = send(uid, text)
        if ok:
            sent += 1
        else:
            bad.append("%s/%s" % (code, uid))
            print("send failed %s: %s" % (uid, err))
    for code, (waiting, actions, _) in results.items():
        if code in open_today:
            for k, h in actions:
                state["seen_actions"][h["id"]] = today.isoformat()
    if bad:
        ledger("eBay message reminders went to %d of %d people; these did not go through: %s." % (sent, len(outbox), ", ".join(bad)))
    state["slots"][slot_key] = {"sent": sent, "at": dt.datetime.now().isoformat(timespec="seconds")}
    save_state(state)
    print("sent %d/%d" % (sent, len(outbox)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
