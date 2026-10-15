#!/usr/bin/env python3
"""staff_video_prompt.py [--render] [--send] [--day YYYY-MM-DD] [--at HH:MM]

Native replacement (Mac-first wave 2, 2026-10-14) for the Cowork task `vp-staff-video-prompt` (Tue 09:10 ET).
Same steps as its SKILL.md:
  0 OPEN-ASK GUARD: a staff-video ask posted in #deal-of-the-week (C0AVCANK7E3) in the last 5 days whose
    Wednesday-2-PM deadline has not passed -> post NOTHING, add a SKIP row to ASK_LOG.md, stop.
    Also: an ask already posted today -> nothing (re-run / catch-up safety).
  1 pick this week's ask: the first ask in ASKS not used in the last 8 weeks (channel history 60 d + ASK_LOG);
    if every ask was used inside 8 weeks, the least recently used one.
  2 post it (the live 9/27 + 10/13 layout: ask, vertical line, length/no-polish line, deadline, the 5 managers
    @-mentioned by Slack id from hr/ROSTER.json). #casual-video still does not exist -> #deal-of-the-week.
  3 log the ask in fleet/vp-staff-video-prompt/ASK_LOG.md. Silent on success (no DM).
--render prints what would be posted and writes nothing. --send is required to publish.
"""
import datetime as dt
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack  # noqa: E402

TASK = "vp-staff-video-prompt"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
ASK_LOG = os.path.join(OS_DIR, "fleet", "vp-staff-video-prompt", "ASK_LOG.md")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
CH = "C0AVCANK7E3"
ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
FALLBACK_IDS = {"Culpeper": "U04C5DL5EKH", "Waynesboro": "U04U136MF6V", "Harrisonburg": "U09UTFT4P7X",
                "Lexington": "U09H9ES2LKA", "Roanoke": "U0631AECK4K"}   # = the live 9/27 post
# The SKILL's five asks, worded as they were posted. Order = rotation preference (first unused wins).
ASKS = [
    "Quick tour of what's new on the jewelry counter this week.",
    "Show us the best deal on your counter right now. Phone video, hold it upright, 20 seconds.",
    "Show us something that came in that you had to look up.",
    "What's the one item on your floor right now you'd take home yourself? Show it to us and tell us why.",
    "30 seconds — the weirdest thing that walked in this week.",
]
KEYS = ["jewelry counter", "best deal on your counter", "had to look up", "take home yourself", "weirdest thing"]
BODY = """{ask}

Hold the phone upright (vertical) — horizontal video doesn't work on Reels and TikTok.

15–45 seconds. No script, no polish. Point the camera and talk. Don't overthink it — it's fine if it isn't perfect, the polish is our job, yours is just pointing the camera.

Deadline: Wednesday 2 PM

{mentions}"""
ASK_MARKERS = ("Hold the phone upright", "Deadline: Wednesday 2 PM", "Wednesday 2 PM deadline")


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def history(days, before):
    """Channel messages newer than `days` ago and older than `before` (epoch). Paginated, no `oldest` (see vp_slack.has)."""
    cutoff, out, cur = before - days * 86400, [], None
    for _ in range(20):
        p = {"channel": CH, "limit": 200}
        if cur:
            p["cursor"] = cur
        r = vp_slack.call("conversations.history", params=p)
        if not r.get("ok"):
            raise RuntimeError("history: " + r.get("error", "?"))
        msgs = r.get("messages", [])
        out += [m for m in msgs if cutoff <= float(m["ts"]) < before]
        if not msgs or float(msgs[-1]["ts"]) < cutoff or not r.get("has_more"):
            break
        cur = r.get("response_metadata", {}).get("next_cursor")
    return out


def is_ask(m):
    t = m.get("text") or ""
    return any(k in t for k in ASK_MARKERS)


def deadline(posted):
    """Wednesday 14:00 ET on/after the post (a post after Wed 14:00 points at next Wednesday)."""
    d = posted.date() + dt.timedelta(days=(2 - posted.weekday()) % 7)
    dl = dt.datetime.combine(d, dt.time(14, 0), ET)
    return dl if dl > posted else dl + dt.timedelta(days=7)


def which_ask(text):
    tl = (text or "").lower()
    for i, k in enumerate(KEYS):
        if k in tl:
            return i
    return None


def log_uses(before_day):
    """(date, ask index) from ASK_LOG.md rows dated before before_day."""
    uses = []
    try:
        for line in open(ASK_LOG):
            m = re.match(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|", line)
            if m and dt.date.fromisoformat(m.group(1)) < before_day and which_ask(m.group(2)) is not None:
                uses.append((dt.date.fromisoformat(m.group(1)), which_ask(m.group(2))))
    except OSError:
        pass
    return uses


def mentions():
    ids = dict(FALLBACK_IDS)
    try:
        for e in json.load(open(ROSTER)).get("employees", []):
            if e.get("title") == "Manager" and e.get("department") in ids and e.get("slack_id"):
                ids[e["department"]] = e["slack_id"]
    except (OSError, ValueError):
        pass
    return ", ".join("<@%s> (%s)" % (ids[s], s) for s in ORDER)


def append_log(row):
    with open(ASK_LOG, "a") as f:
        f.write(row + "\n")


def main():
    render = "--render" in sys.argv
    send = "--send" in sys.argv
    now = dt.datetime.now(ET)
    if arg("--day"):
        hh, mm = (arg("--at") or "09:10").split(":")
        now = dt.datetime.combine(dt.date.fromisoformat(arg("--day")), dt.time(int(hh), int(mm)), ET)
    msgs = history(60, now.timestamp())
    asks = sorted([m for m in msgs if is_ask(m)], key=lambda m: float(m["ts"]))
    # 0 open-ask guard + same-day guard
    for m in reversed(asks):
        posted = dt.datetime.fromtimestamp(float(m["ts"]), ET)
        if posted.date() == now.date():
            print("ask already posted today (%s) — nothing to do" % posted.strftime("%H:%M"))
            return 0
        if (now - posted).days < 5 and deadline(posted) > now:
            print("OPEN ASK from %s (deadline %s) — silent skip" % (posted.strftime("%a %m/%d %H:%M"), deadline(posted).strftime("%a %m/%d %H:%M")))
            if send and not render:
                append_log("| %s (SKIP) | — | — | — | — | Open ask still live (%s post, deadline %s); no new ask posted (native). |"
                           % (now.date(), posted.date(), deadline(posted).strftime("%Y-%m-%d 2 PM")))
            return 0
    # 1 rotation
    last = {}
    for m in asks:
        i = which_ask(m.get("text"))
        if i is not None:
            last[i] = max(last.get(i, dt.date.min), dt.datetime.fromtimestamp(float(m["ts"]), ET).date())
    for d, i in log_uses(now.date()):
        last[i] = max(last.get(i, dt.date.min), d)
    fresh = [i for i in range(len(ASKS)) if (now.date() - last.get(i, dt.date.min)).days > 56]
    pick = fresh[0] if fresh else min(range(len(ASKS)), key=lambda i: (last.get(i, dt.date.min), i))
    print("rotation: " + "; ".join("%s=%s" % (KEYS[i], last.get(i, "never")) for i in range(len(ASKS))) + " -> " + KEYS[pick])
    text = BODY.format(ask=ASKS[pick], mentions=mentions())
    print("=== POST %s" % CH)
    print(text)
    if render or not send:
        return 0
    os.environ["VP_TASK"] = TASK
    os.environ["VP_SLACK_RAW"] = "1"          # mentions + em dashes verbatim, exactly as the outbox sent them
    vp_slack.post(CH, text)
    wed = now.date() + dt.timedelta(days=(2 - now.weekday()) % 7)
    append_log("| %s | \"%s\" | %s 2 PM | — | — | native post; 8-week rotation pick (%s) |" % (now.date(), ASKS[pick], wed, KEYS[pick]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        if "--render" not in sys.argv:
            ledger("This week's staff video ask was not posted (%s)." % type(e).__name__)
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
