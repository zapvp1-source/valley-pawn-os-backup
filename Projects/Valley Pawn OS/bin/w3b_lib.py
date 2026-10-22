#!/usr/bin/env python3
"""w3b_lib.py — shared helpers for the Mac-first wave 3 SECOND PASS agents (2026-10-20).
Nothing here publishes on its own. Every send goes through vp_slack.post (receipt keyed off $VP_TASK, the fleet
publish guard, the native-table conversion) — never through anything else.

  months(period)            -> (YYYY-MM, first date, last date, "September 2026")
  prev_month(today)         -> YYYY-MM of the month that just closed
  history(ch, oldest, latest, bot_only=False) -> every message in the window, oldest first (paginated)
  thread(ch, ts)            -> replies of one thread
  download(file)            -> bytes of a Slack file (files:read)
  post(task, ch, text, render, label) -> posts (live) or writes fleet/test_output/<task>-<ts>.txt (render)
  ledger(task, sentence, needs="no")
  ask / ask_json            -> bin/vp_ai.py (claude-sonnet-5-5)
"""
import calendar
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
ET = ZoneInfo("America/New_York")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
TEST_OUT = os.path.join(OS_DIR, "fleet", "test_output")
JOSHUA = "U03BB52MDSA"
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}


def now():
    return dt.datetime.now(ET)


def prev_month(today=None):
    t = today or now().date()
    first = t.replace(day=1)
    return (first - dt.timedelta(days=1)).strftime("%Y-%m")


def months(period):
    y, m = map(int, period.split("-"))
    first = dt.date(y, m, 1)
    last = dt.date(y, m, calendar.monthrange(y, m)[1])
    return period, first, last, first.strftime("%B %Y")


def ts_of(d, end=False):
    t = dt.datetime.combine(d, dt.time(23, 59, 59) if end else dt.time(0, 0), ET)
    return "%.6f" % t.timestamp()


def ledger(task, sentence, needs="no"):
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (now().strftime("%Y-%m-%d %H:%M ET"), task, sentence, needs))
    except OSError:
        pass


def _slack():
    import vp_slack
    return vp_slack


def history(ch, oldest, latest, bot_only=False):
    """Every message (top level) in [oldest, latest], oldest first. Raises RuntimeError if the bot cannot read."""
    vs = _slack()
    out, cursor = [], None
    for _ in range(60):
        p = {"channel": ch, "limit": 200, "oldest": oldest, "latest": latest, "inclusive": "true"}
        if cursor:
            p["cursor"] = cursor
        r = vs.call("conversations.history", params=p)
        if not r.get("ok"):
            raise RuntimeError("history %s: %s" % (ch, r.get("error")))
        out.extend(r.get("messages", []))
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not r.get("has_more") or not cursor:
            break
        time.sleep(0.4)
    out = [m for m in out if m.get("subtype") not in ("channel_join", "channel_leave", "channel_topic", "channel_purpose")]
    if bot_only:
        out = [m for m in out if m.get("bot_id") or m.get("subtype") == "bot_message" or m.get("user") == JOSHUA]
    return sorted(out, key=lambda m: float(m.get("ts", 0)))


def thread(ch, ts):
    r = _slack().call("conversations.replies", params={"channel": ch, "ts": ts, "limit": 200})
    return r.get("messages", [])[1:] if r.get("ok") else []


def text_of(m):
    """Message text, including the text of Block Kit sections/tables the bot posts (the connector shows those empty)."""
    t = m.get("text") or ""
    parts = []
    for b in m.get("blocks") or []:
        if b.get("type") == "section" and isinstance(b.get("text"), dict):
            parts.append(b["text"].get("text", ""))
        elif b.get("type") == "table":
            for row in b.get("rows", []):
                cells = []
                for c in row:
                    cells.append("".join(e.get("text", "") for el in c.get("elements", []) for e in el.get("elements", [])
                                         if isinstance(e, dict)) if c.get("type") == "rich_text" else str(c.get("text", "")))
                parts.append(" | ".join(cells))
        elif b.get("type") == "context":
            parts.append(" ".join(e.get("text", "") for e in b.get("elements", []) if isinstance(e, dict)))
    joined = "\n".join(p for p in parts if p)
    best = joined if len(joined) > len(t) else t
    foot = [p for p in parts if "Sent using" in p and p not in best]
    return best + ("\n" + foot[0] if foot else "")


def download(f):
    vs = _slack()
    url = f.get("url_private_download") or f.get("url_private")
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + vs.token()})
    return urllib.request.urlopen(req, timeout=90).read()


def users():
    """user id -> display name (real_name), from users.list (cached per process)."""
    if hasattr(users, "_c"):
        return users._c
    vs = _slack()
    m, cursor = {}, None
    for _ in range(10):
        r = vs.call("users.list", params={"limit": 200, **({"cursor": cursor} if cursor else {})})
        if not r.get("ok"):
            break
        for u in r.get("members", []):
            p = u.get("profile") or {}
            m[u["id"]] = p.get("display_name") or p.get("real_name") or u.get("real_name") or u.get("name")
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break
    users._c = m
    return m


def post(task, ch, text, render, label="main"):
    """Live: vp_slack.post (receipt + publish guard). Render: write fleet/test_output/<task>-<label>-<ts>.txt with a first
    line naming the destination, print it, publish nothing."""
    if render:
        os.makedirs(TEST_OUT, exist_ok=True)
        p = os.path.join(TEST_OUT, "%s-%s-%s.txt" % (task, label, now().strftime("%Y%m%d-%H%M%S")))
        with open(p, "w") as f:
            f.write("TO: %s (render — not sent)\n%s\n" % (ch, text))
        print("----- RENDER %s -> %s (%s) -----\n%s\n----- end -----" % (label, ch, p, text))
        return True
    os.environ["VP_TASK"] = task
    vs = _slack()
    # 2026-10-21 (Nov 1 rehearsal): a send the publish guard DIVERTS returns "DRYRUN" (truthy, so callers do not
    # log a failure) instead of True. Callers advance state / write "sent" logs only on `ok is True`, so an
    # isolation test can never move hr-policy-sync's since-date, overwrite the CEO carry-forward, or log a DM.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import vp_dryrun
        diverted = vp_dryrun.active_for(task)
    except Exception:   # noqa: BLE001  (guard unreadable = live, same fail-open rule as vp_slack)
        diverted = False
    if diverted:
        vs.post(ch, text)          # vp_slack diverts to fleet/test_output (no conversations.open needed)
        return "DRYRUN"
    target = vs.dm_channel(ch) if ch.startswith("U") else ch
    try:
        vs.post(target, text)
        return True
    except SystemExit as e:
        ledger(task, "the %s message did not send (%s)" % (label, str(e)[:80]))
        return False


def already(ch, marker, hours):
    try:
        return _slack().has(ch, marker, hours)
    except SystemExit:
        return False


def _raw(prompt, system, max_tokens, content):
    """Same call as bin/vp_ai.ask (same key, same model) but keeps stop_reason so an empty answer is visible."""
    import vp_ai
    body = {"model": vp_ai.MODEL, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content if content is not None else prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(vp_ai.API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": vp_ai.key(), "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    txt = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    return txt, resp.get("stop_reason"), resp.get("usage")


def ask(prompt, system="", max_tokens=3000, content=None):
    """bin/vp_ai (claude-sonnet-5-5). An empty or cut-off answer is retried once with double the token budget."""
    for attempt in range(2):
        txt, stop, usage = _raw(prompt, system, max_tokens, content)
        if txt.strip() and stop != "max_tokens":
            return txt
        print("vp_ai: empty/truncated answer (stop=%s usage=%s) — retry %d" % (stop, usage, attempt + 1))
        max_tokens *= 2
    return txt


def ask_json(prompt, system="", max_tokens=3000, content=None):
    import re as _re
    out = ask(prompt, system, max_tokens, content)
    m = _re.search(r"(\{.*\}|\[.*\])", out, _re.S)
    if not m:
        raise ValueError("no JSON in answer: " + out[:200])
    return json.loads(m.group(1), strict=False)


BANNED_FIELD = ("bravo", "cowork", "chekkit", "gusto", "brevo", "qbo", "quickbooks", "publer", "pipeline", "handler",
                "watchdog", " sync", "csv", "export", "claude", "automation", "script", "/users/", "docs.google", "drive.google")


def field_clean(text):
    """Rule 16 check for team-channel text: returns the banned terms found (empty list = clean)."""
    low = text.lower()
    return [b.strip() for b in BANNED_FIELD if b in low]
