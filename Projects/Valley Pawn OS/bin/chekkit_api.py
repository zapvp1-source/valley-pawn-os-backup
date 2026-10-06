#!/usr/bin/env python3
"""chekkit_api.py — shared READ helpers for the Chekkit API (api.chekkit.io), one token per store in
Keychain `vp-chekkit-token-<CODE>` (CHANGELOG 2026-10-05). stdlib only. GET only in this module.

Message shape (verified 2026-10-05, bin/chekkit_schema_probe.py):
  sender  = "customer" | "business" | "event"
  sentBy  = staff display name for business/event rows ("Walker Tapley"); automated texts that go
            out through the store webhooks (missed-call text, AI replies) and scheduled campaigns
            show the account owner ("Joshua Davis") — so "automated" is decided by the TEXT, not sentBy.

Business rule (Joshua 2026-10-05): "if we are communicating to them via text in Chekkit, then a call
back is not needed." text_status() below is the single place that rule lives.
"""
import datetime as dt, json, subprocess, time, urllib.error, urllib.request

BASE = "https://api.chekkit.io"
AUTOMATED_MARKERS = ("hi, this is valley pawn in", "automated reply", "thanks for reaching out. a team member",
                     "scheduled message for")
_tok_cache = {}


def token(code):
    if code not in _tok_cache:
        _tok_cache[code] = subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"],
                                          capture_output=True, text=True, timeout=15).stdout.strip()
    return _tok_cache[code]


def get(code, path, retries=2):
    tok = token(code)
    if not tok:
        raise RuntimeError("no Chekkit token for %s" % code)
    last = None
    for i in range(retries + 1):
        req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + tok, "Accept": "application/json",
                                                           "User-Agent": "ValleyPawnOps/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429 or e.code >= 500:
                time.sleep(2 + 3 * i); continue
            raise
        except Exception as e:
            last = e; time.sleep(2 + 3 * i)
    raise last


def ts(s):
    try:
        return dt.datetime.fromisoformat((s or "").replace("Z", "+00:00"))
    except Exception:
        return None


def digits10(num):
    d = "".join(c for c in (num or "") if c.isdigit())
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 else None


def conversations_since(code, since_utc, max_pages=15):
    """{phone10: conversation} for every conversation with activity since since_utc (newest first)."""
    out, before = {}, None
    for _ in range(max_pages):
        b = get(code, "/v1/conversations" + ("?before=" + before if before else ""))
        convs = b.get("conversations") or []
        stop = False
        for c in convs:
            last = ts(c.get("lastMessageAt"))
            if last and last < since_utc:
                stop = True; continue
            p = digits10((c.get("customer") or {}).get("phone"))
            if p and p not in out:
                out[p] = c
        nb = b.get("nextBefore")
        if nb == before:  # API ignored ?before= — don't spin on the same page
            break
        before = nb
        if stop or not before or not convs:
            break
        time.sleep(1.05)
    return out


def messages(code, conv_id):
    return (get(code, "/v1/conversations/%s/messages" % conv_id) or {}).get("messages") or []


def is_automated(m):
    t = (m.get("text") or "").strip().lower()
    return any(k in t for k in AUTOMATED_MARKERS)


def text_status(msgs, since_utc):
    """Text-thread status after the missed call.
    'handled'        - a staff member (not an automated text) texted the customer after the call
    'customer_waiting' - the customer texted back but no staff member has answered yet
    'none'           - no two-way texting since the call (a call back is still needed)"""
    after = [m for m in msgs if (ts(m.get("createdAt")) or since_utc) >= since_utc]
    staff = [m for m in after if m.get("sender") == "business" and not is_automated(m)]
    cust = [m for m in after if m.get("sender") == "customer" and (m.get("text") or m.get("media"))]
    if staff:
        return "handled", staff[-1].get("sentBy")
    if cust:
        return "customer_waiting", None
    return "none", None
