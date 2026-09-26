#!/usr/bin/env python3
"""sms_code_relay.py — hand a scheduled Cowork task the SMS code it is waiting for, without any
connector.

WHY (2026-09-25): northwest-registered-agent-daily-check logs in fine, then Northwest texts a code
to Joshua's phone. The SKILL reads it with the Read_and_Send_iMessages connector — which, like
Control_your_Mac, does not exist inside a scheduled session. The Messages database is readable by
the native runner (Full Disk Access proven 9/21). So: a launchd agent copies the newest matching
code into a plain file under Projects, and the task reads THAT.

Reads ~/Library/Messages/chat.db read-only. Writes fleet/sms_codes/<name>.json:
  {"code": "123456", "received": "<ISO>", "from": "+1509...", "age_s": 12}
only when the message is newer than `max_age_min`; otherwise writes {"code": null, ...}.
Configuration lives in fleet/sms_code_relay.json (sender -> name -> regex). Nothing else from
Messages is ever copied; the code file is overwritten every run and holds one number.

  sms_code_relay.py            run (launchd, every 30 s inside each entry's window)
  sms_code_relay.py --render   print what would be written, write nothing
"""
import datetime as dt
import json
import os
import re
import sqlite3
import sys
from zoneinfo import ZoneInfo

OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
CFG = os.path.join(OS_DIR, "fleet", "sms_code_relay.json")
OUT = os.path.join(OS_DIR, "fleet", "sms_codes")
CHAT = os.path.expanduser("~/Library/Messages/chat.db")
ET = ZoneInfo("America/New_York")
APPLE_EPOCH = dt.datetime(2001, 1, 1, tzinfo=dt.timezone.utc)


def msg_time(raw):
    if raw is None:
        return None
    raw = int(raw)
    if raw > 10 ** 12:      # nanoseconds since 2001 (modern macOS)
        raw = raw / 1e9
    return APPLE_EPOCH + dt.timedelta(seconds=raw)


def text_of(row_text, blob):
    if row_text:
        return row_text
    if blob:
        # attributedBody: the plain string sits after 'NSString' + length byte(s); a loose search
        # for the code pattern in the decoded bytes is enough for a 6-digit code.
        try:
            return blob.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return ""


def newest(sender, pattern, since):
    c = sqlite3.connect("file:%s?mode=ro" % CHAT, uri=True)
    q = """select m.date, m.text, m.attributedBody from message m
           join handle h on h.ROWID = m.handle_id
           where h.id = ? and m.is_from_me = 0 order by m.date desc limit 20"""
    rx = re.compile(pattern)
    for d, t, b in c.execute(q, (sender,)):
        when = msg_time(d)
        if not when or when < since:
            break
        m = rx.search(text_of(t, b) or "")
        if m:
            return m.group(1), when
    return None, None


def main():
    render = "--render" in sys.argv
    cfg = json.load(open(CFG))
    now = dt.datetime.now(dt.timezone.utc)
    now_et = now.astimezone(ET).time()
    os.makedirs(OUT, exist_ok=True)
    for name, e in cfg["relays"].items():
        a, b = e.get("window", ["00:00", "23:59"])
        in_win = dt.time.fromisoformat(a) <= now_et <= dt.time.fromisoformat(b)
        if not in_win and not render:
            continue
        since = now - dt.timedelta(minutes=int(os.environ.get("SMS_RELAY_MAX_AGE_MIN") or e.get("max_age_min", 10)))
        code, when = None, None
        try:
            code, when = newest(e["sender"], e["pattern"], since)
        except Exception as ex:
            print("%s: chat.db read failed: %s" % (name, type(ex).__name__))
        rec = {"code": code, "received": when.isoformat() if when else None, "from": e["sender"],
               "age_s": int((now - when).total_seconds()) if when else None,
               "checked": now.astimezone(ET).isoformat(timespec="seconds")}
        if render:
            print(name, json.dumps({**rec, "code": ("******" if code else None)}))
            continue
        tmp = os.path.join(OUT, name + ".json.tmp")
        with open(tmp, "w") as f:
            json.dump(rec, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, os.path.join(OUT, name + ".json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
