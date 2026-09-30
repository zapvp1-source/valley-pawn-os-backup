#!/usr/bin/env python3
"""ebay_ship_alert.py — eBay Ship-By Alert (native, no Claude). Built 2026-09-29 on Joshua's ask:
"a reminder to go out to the team if they have not shipped their eBay packages in the right amount
of time, or if it needs to be done before it's late."

WHAT IT DOES (read-only against eBay — it never changes an order, a listing or anything in eBay):
  For each of the 5 store eBay accounts, GetOrders (Trading API, same per-store tokens every eBay
  script uses) for paid orders from the last 30 days, then sorts each unshipped order into:
    LATE   — ship-by time has already passed
    TODAY  — must ship today, because the ship-by date falls before the store's NEXT open day
             (so a Wednesday ship-by at a store closed Wednesday shows up on Tuesday)
    NEXT   — due on the store's next open day (heads-up, morning only)
  plus NOTRACK — marked shipped in the last 7 days but no tracking number (counts against us).
  Local-pickup orders and cancelled orders are ignored.

WHO GETS WHAT
  * Store team DMs (roster-checked, same recipient map as the weekly loan/layaway DMs):
      --slot am  (09:30 Mon–Sat)  ship today + already late + no tracking + heads-up count
      --slot pm  (14:00 Mon–Sat)  last call: only what is STILL unshipped (today + late)
    Only stores open that day get a DM. Nothing to report = nothing sent (silent by design).
  * Joshua: ONE plain DM on the am slot, only when something is late or missing tracking.
  * Failures (token expired, eBay down): one row in fleet/FAILURE_LEDGER.md, nothing to Slack
    (Failure policy v3 / Rule 16). A store that fails is skipped; the others still go out.

  ebay_ship_alert.py --slot am|pm            send
  ebay_ship_alert.py --slot am|pm --render   print every DM, send nothing (safe test)
  add --debug to print the raw shipping fields of the first order per store
"""
import datetime as dt
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

AGENT = "ebay-ship-alert"
OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.expanduser("~/Library/Logs/valleypawn/ebay-ship-alert.state.json")
JOSHUA = "U03BB52MDSA"

NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
LOOKBACK_DAYS = 30
NOTRACK_DAYS = 7
DEFAULT_HANDLING_DAYS = 1   # only used when eBay gives no ship-by time for an order

STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
# Same store-team map as loan_layaway_dms.py (2026-09-28). Filtered against hr/ROSTER.json at send time.
TEAM = {
    "CUL": ["U04C5DL5EKH"],
    "HAR": ["U09UTFT4P7X", "U03BFDJH31B"],
    "LEX": ["U09H9ES2LKA", "U05TV57FH0B"],
    "ROA": ["U0631AECK4K", "U063E87TM70"],
    "WAY": ["U04U136MF6V"],
}
# Bravo intake code in titles — identical to engine/ebay_common.py CODE_RE (never widen; eBay Rule 3)
CODE_RE = re.compile(r"\(((?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,})\)")
PICKUP_RE = re.compile(r"pickup|pick up|localdelivery|local delivery|instore", re.I)


# ---------------------------------------------------------------- store calendar (vp_lib.sh open_stores)
def open_codes(day):
    wd = day.isoweekday()  # 1=Mon .. 7=Sun
    if wd == 7:
        return set()
    if wd == 3:
        return {"CUL"}
    return {c for c, _ in STORES}


def next_open_day(code, day):
    d = day + dt.timedelta(days=1)
    for _ in range(14):
        if code in open_codes(d):
            return d
        d += dt.timedelta(days=1)
    return day + dt.timedelta(days=1)


def add_business_days(d, n):
    while n > 0:
        d += dt.timedelta(days=1)
        if d.isoweekday() <= 5:
            n -= 1
    return d


# ---------------------------------------------------------------- eBay
def load_tokens():
    sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
    from ebay_store_tokens import STORES as TOK, APP_ID, DEV_ID, CERT_ID  # never hardcode
    return {s["name"].lower(): s["token"] for s in TOK}, (APP_ID, DEV_ID, CERT_ID)


def ebay_call(tok, keys, name, inner, retries=3):
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
            return ET.fromstring(urlopen(Request(URL, data=body, headers=h), timeout=90).read().decode())
        except (URLError, HTTPError, ET.ParseError, OSError) as e:
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError("%s failed after %d tries: %s" % (name, retries, last))


def q(el, tag):
    return "{%s}%s" % (NS, tag)


def ftext(el, tag):
    v = el.find(".//" + q(el, tag))
    return v.text.strip() if v is not None and v.text else None


def all_text(el, tag):
    return [x.text.strip() for x in el.iter(q(el, tag)) if x.text and x.text.strip()]


def parse_ts(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_orders(tok, keys, now_utc, debug=False):
    frm = (now_utc - dt.timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    to = now_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out, page = [], 1
    while page <= 20:
        r = ebay_call(tok, keys, "GetOrders",
                      "<CreateTimeFrom>%s</CreateTimeFrom><CreateTimeTo>%s</CreateTimeTo>"
                      "<OrderRole>Seller</OrderRole><OrderStatus>Completed</OrderStatus><DetailLevel>ReturnAll</DetailLevel>"
                      "<Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                      % (frm, to, page))
        ack = r.findtext(q(r, "Ack"), "")
        if ack not in ("Success", "Warning"):
            msgs = "; ".join(e.findtext(q(e, "LongMessage"), "") for e in r.iter(q(r, "Errors")))
            raise RuntimeError("GetOrders %s: %s" % (ack, msgs[:300]))
        for o in r.iter(q(r, "Order")):
            if debug and not out:
                dbg = {t: all_text(o, t) for t in ("OrderID", "PaidTime", "ShippedTime", "HandleByTime",
                                                    "ShippingService", "ShipmentTrackingNumber",
                                                    "CancelStatus", "DispatchTimeMax", "OrderStatus")}
                print("DEBUG first order fields:", json.dumps(dbg))
            out.append(o)
        more = r.findtext(q(r, "HasMoreOrders"), "false").lower() == "true"
        if not more:
            break
        page += 1
    return out


def classify(o, code, now_utc, today, dispatch_days=None):
    """Return (bucket, record) or (None, None). Buckets: LATE, TODAY, NEXT, NOTRACK."""
    cancel = (ftext(o, "CancelStatus") or "").lower()
    if cancel in ("cancelcomplete", "cancelclosedwithrefund", "cancelclosedforcommitment") or cancel.startswith("cancelcomplete"):
        return None, None
    services = all_text(o, "ShippingService")
    if services and all(PICKUP_RE.search(s) for s in services):
        return None, None
    if (ftext(o, "InStorePickup") or "").lower() == "true":
        return None, None
    paid = parse_ts(ftext(o, "PaidTime"))
    if not paid:
        return None, None  # unpaid — nothing to ship yet
    titles = all_text(o, "Title")
    title = titles[0] if titles else "(item)"
    if len(titles) > 1:
        title += " + %d more" % (len(titles) - 1)
    m = CODE_RE.search(" ".join(titles)) or None
    rec = {
        "order": ftext(o, "OrderID") or "?",
        "title": CODE_RE.sub("", title).strip()[:70],
        "code": m.group(1) if m else None,
        "paid": paid.isoformat(),
    }
    shipped = parse_ts(ftext(o, "ShippedTime"))
    if shipped:
        tracking = all_text(o, "ShipmentTrackingNumber")
        if not tracking and (now_utc - shipped).days < NOTRACK_DAYS:
            rec["shipped"] = shipped.isoformat()
            return "NOTRACK", rec
        return None, None
    hb = [parse_ts(s) for s in all_text(o, "HandleByTime")]
    hb = [x for x in hb if x]
    if hb:
        ship_by = min(hb)
        rec["estimated"] = False
    else:
        # eBay did not return a ship-by time: use the listing's own handling time (GetItem
        # DispatchTimeMax, business days after payment); only if that is unavailable too, assume 1 day.
        n = None
        if dispatch_days:
            vals = [dispatch_days(i) for i in all_text(o, "ItemID")]
            vals = [v for v in vals if v is not None]
            n = min(vals) if vals else None
        rec["estimated"] = n is None
        rec["handling_days"] = n if n is not None else DEFAULT_HANDLING_DAYS
        d = add_business_days(paid.astimezone(ET_TZ).date(), rec["handling_days"])
        ship_by = dt.datetime.combine(d, dt.time(23, 59), ET_TZ)
    rec["ship_by"] = ship_by.isoformat()
    sb_local = ship_by.astimezone(ET_TZ).date()
    if ship_by <= now_utc:
        return "LATE", rec
    nod = next_open_day(code, today)
    if sb_local < nod:
        return "TODAY", rec
    if sb_local == nod:
        return "NEXT", rec
    return None, None


# ---------------------------------------------------------------- messages
def fmt_when(iso, today):
    t = dt.datetime.fromisoformat(iso).astimezone(ET_TZ)
    d = t.date()
    day = "today" if d == today else ("yesterday" if d == today - dt.timedelta(days=1) else t.strftime("%a %b %-d"))
    return day


def line(rec, today, late=False):
    s = "• Order %s — %s" % (rec["order"], rec["title"])
    if rec.get("code"):
        s += " (%s)" % rec["code"]
    if late:
        s += " — was due %s" % fmt_when(rec["ship_by"], today)
    return s


def store_message(name, b, slot, today):
    late, due, nxt, notrack = b["LATE"], b["TODAY"], b["NEXT"], b["NOTRACK"]
    if slot == "pm":
        if not (late or due):
            return None
        parts = ["⏰ *Last call — eBay orders still not shipped, %s*" % name]
    else:
        if not (late or due or notrack):
            return None
        parts = ["📦 *eBay orders to ship today — %s* (%s)" % (name, today.strftime("%a %b %-d"))]
    if late:
        parts.append("🔴 *Already late — please ship these first:*\n" + "\n".join(line(r, today, True) for r in late))
    if due:
        parts.append("*Must ship today to stay on time:*\n" + "\n".join(line(r, today) for r in due))
    if slot == "am" and notrack:
        parts.append("⚠️ *Marked shipped but no tracking number — please add tracking in eBay:*\n"
                     + "\n".join(line(r, today) for r in notrack))
    if slot == "am" and nxt:
        parts.append("Heads-up: %d more order%s due your next open day." % (len(nxt), "" if len(nxt) == 1 else "s"))
    parts.append("Buy the label through eBay so tracking uploads automatically. Thank you!")
    return "\n\n".join(parts)


# ---------------------------------------------------------------- plumbing
def ledger(sentence):
    row = "| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (
        dt.datetime.now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence)
    try:
        with open(LEDGER, "a") as f:
            f.write(row)
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
        return {"slots": {}, "late": {}}


def save_state(s):
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        cutoff = (dt.date.today() - dt.timedelta(days=45)).isoformat()
        s["slots"] = {k: v for k, v in s.get("slots", {}).items() if k[:10] >= cutoff}
        s["late"] = {k: v for k, v in s.get("late", {}).items() if v.get("first", "") >= cutoff}
        tmp = STATE + ".tmp"
        json.dump(s, open(tmp, "w"), indent=1)
        os.replace(tmp, STATE)
    except OSError:
        pass


def main():
    args = sys.argv[1:]
    render, debug = "--render" in args, "--debug" in args
    slot = args[args.index("--slot") + 1] if "--slot" in args else None
    if slot not in ("am", "pm"):
        print("usage: ebay_ship_alert.py --slot am|pm [--render] [--debug]")
        return 2
    now_utc = dt.datetime.now(dt.timezone.utc)
    today = now_utc.astimezone(ET_TZ).date()
    open_today = open_codes(today)
    if not open_today and not render:
        print("no store open today (%s) — nothing to do" % today)
        return 0
    state = load_state()
    slot_key = "%s-%s" % (today.isoformat(), slot)
    if not render and state["slots"].get(slot_key):
        print("slot %s already sent — exit" % slot_key)
        return 0

    try:
        toks, keys = load_tokens()
    except Exception as e:
        print("eBay credentials unreadable:", e)
        if not render:
            ledger("The eBay ship-by reminders did not go out — the eBay store credentials could not be read.")
        return 1

    results, failed = {}, []
    for code, name in STORES:
        tok = toks.get(name.lower())
        if not tok:
            failed.append(name)
            continue
        try:
            orders = get_orders(tok, keys, now_utc, debug)
        except Exception as e:
            print("%s: %s" % (name, e))
            failed.append(name)
            continue
        b = {"LATE": [], "TODAY": [], "NEXT": [], "NOTRACK": []}
        cache = {}

        def dispatch_days(item_id, _tok=tok):
            if item_id not in cache:
                cache[item_id] = None
                try:
                    r = ebay_call(_tok, keys, "GetItem", "<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>" % item_id, retries=2)
                    v = r.findtext(".//" + q(r, "DispatchTimeMax"))
                    cache[item_id] = int(v) if v not in (None, "") else None
                except Exception as e:
                    print("GetItem %s: %s" % (item_id, e))
            return cache[item_id]

        for o in orders:
            k, rec = classify(o, code, now_utc, today, dispatch_days)
            if debug and k in ("LATE", "TODAY", "NEXT"):
                print("DEBUG %s %s %s paid=%s ship_by=%s est=%s handling=%s HandleByTime=%s" % (
                    name, k, rec["order"], rec["paid"], rec["ship_by"], rec["estimated"], rec.get("handling_days"),
                    all_text(o, "HandleByTime")))
            if k:
                b[k].append(rec)
        for k in b:
            b[k].sort(key=lambda r: r.get("ship_by") or r.get("shipped") or "")
        results[code] = b
        print("%s: %d paid orders in %dd — late %d, today %d, next %d, no-tracking %d%s" % (
            name, len(orders), LOOKBACK_DAYS, len(b["LATE"]), len(b["TODAY"]), len(b["NEXT"]), len(b["NOTRACK"]),
            "  (ship-by estimated on %d)" % sum(1 for x in b["LATE"] + b["TODAY"] + b["NEXT"] if x.get("estimated"))))

    if failed and not render:
        ledger("eBay ship-by reminders could not check %s this run (eBay did not answer or the store sign-in has expired)."
               % ", ".join(failed))

    active = set()
    try:
        active = {e.get("slack_id") for e in json.load(open(ROSTER))["employees"] if e.get("slack_id")}
    except Exception as e:
        print("roster unreadable (%s) — refusing to guess who is employed" % e)
        if not render:
            ledger("The eBay ship-by reminders were not sent — the staff roster could not be read.")
        return 1

    outbox = []
    for code, name in STORES:
        b = results.get(code)
        if not b or (code not in open_today and not render):
            continue
        text = store_message(name, b, slot, today)
        if not text:
            continue
        for uid in TEAM.get(code, []):
            if uid in active:
                outbox.append((uid, code, text))
            else:
                print("skip %s (%s): not on the active roster" % (uid, code))

    # Joshua — morning only, only when something is late or missing tracking
    week_start = (today - dt.timedelta(days=today.weekday())).isoformat()
    for code, b in results.items():
        for r in b["LATE"]:
            state["late"].setdefault(r["order"], {"first": today.isoformat(), "store": code})
    if slot == "am":
        rows = []
        for code, name in STORES:
            b = results.get(code)
            if b and (b["LATE"] or b["NOTRACK"]):
                bits = []
                if b["LATE"]:
                    bits.append("%d late" % len(b["LATE"]))
                if b["NOTRACK"]:
                    bits.append("%d shipped without tracking" % len(b["NOTRACK"]))
                rows.append("• %s: %s" % (name, ", ".join(bits)))
        if rows:
            wk = {}
            for oid, v in state["late"].items():
                if v.get("first", "") >= week_start:
                    wk[v.get("store")] = wk.get(v.get("store"), 0) + 1
            wk_line = ", ".join("%s %d" % (n, wk[c]) for c, n in STORES if wk.get(c)) or "none"
            outbox.append((JOSHUA, "JOSHUA",
                           "📦 eBay shipping — needs attention this morning:\n" + "\n".join(rows)
                           + "\n\nThe stores have been sent their lists. Late orders so far this week: " + wk_line + "."))

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
    if bad:
        ledger("eBay ship-by reminders went to %d of %d people; these did not go through: %s." % (sent, len(outbox), ", ".join(bad)))
    state["slots"][slot_key] = {"sent": sent, "at": dt.datetime.now().isoformat(timespec="seconds")}
    save_state(state)
    print("sent %d/%d" % (sent, len(outbox)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
