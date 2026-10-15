#!/usr/bin/env python3
"""thursday_email_watchdog.py [--render] [--send] [--day YYYY-MM-DD]

Native replacement (Mac-first wave 2, 2026-10-14) for the Cowork task `vp-thursday-email-watchdog` (Thu 10:30 ET).
  1 CHECK: a Brevo campaign whose name carries today's date ("October 15, 2026") is sent / queued / in process
    -> nothing posted (the normal week).
  2 SELF-HEAL: still a draft -> run the native compiler that builds it every Monday (deal_of_week_pick.py, same
    submissions, same Publer-hosted photos, same pre-send check) with --thursday <today> --send-now, re-check
    the status, then post the SKILL's ONE line to #deal-of-the-week:
    "This week's email is out — {N} deals featured. (Recovered by the Thursday watchdog.)"
  3 FAILURE (no draft at all, or the recovery did not send): one FAILURE_LEDGER row, no DM (Failure policy v3,
    which overrides the SKILL's step-3 DM).
--render only reports what step 1 finds and what step 2 would do (compiler --render). --send is required to act.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack  # noqa: E402

TASK = "vp-thursday-email-watchdog"
ET = ZoneInfo("America/New_York")
LEDGER = os.path.join(os.path.dirname(HERE), "fleet", "FAILURE_LEDGER.md")
CH = "C0AVCANK7E3"
API = "https://api.brevo.com/v3"
PY = "/usr/bin/python3"
LINE = "This week's email is out — %d deals featured. (Recovered by the Thursday watchdog.)"


def ledger(sentence, human="no"):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence, human))


def brevo(path):
    k = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
    req = urllib.request.Request(API + path, headers={"api-key": k, "accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def main():
    render = "--render" in sys.argv
    send = "--send" in sys.argv and not render
    day = dt.date.fromisoformat(arg("--day")) if arg("--day") else dt.datetime.now(ET).date()
    labels = {"%s %d, %d" % (day.strftime("%B"), day.day, day.year), day.strftime("%B %d, %Y")}
    for st in ("sent", "queued", "inProcess"):
        for c in brevo("/emailCampaigns?status=%s&limit=50&sort=desc" % st).get("campaigns", []):
            if any(lb in (c.get("name") or "") for lb in labels):
                print("email verified %s: #%s %s" % (st, c["id"], c["name"]))
                return 0
    drafts = [c for c in brevo("/emailCampaigns?status=draft&limit=100").get("campaigns", [])
              if any(lb in (c.get("name") or "") for lb in labels)]
    if not drafts:
        print("no sent/queued campaign and no draft for", sorted(labels))
        if send:
            ledger("This week's deal email (%s) did not go out and there is no draft to recover it from." % day, "yes, stage this week's email in Brevo")
        return 1
    print("still a DRAFT: #%s %s -> self-heal" % (drafts[0]["id"], drafts[0]["name"]))
    cmd = [PY, os.path.join(HERE, "deal_of_week_pick.py"), "--thursday", day.isoformat()]
    if not send:
        p = subprocess.run(cmd + ["--render"], capture_output=True, text=True, timeout=900)
        print("compiler --render:\n" + p.stdout[-3000:] + p.stderr[-500:])
        return 0
    if vp_slack.has(CH, "Recovered by the Thursday watchdog", 20):
        print("recovery line already posted today — not re-sending")
        return 0
    p = subprocess.run(cmd + ["--send-now"], capture_output=True, text=True, timeout=1800)
    print(p.stdout[-3000:], p.stderr[-800:])
    m = re.search(r"SENDNOW #\d+ status=(\S+) deals=(\d+)", p.stdout)
    if p.returncode != 0 or not m:
        ledger("This week's deal email (%s) was still a draft at 10:30 and the automatic recovery did not send it." % day,
               "yes, open the draft in Brevo and send it")
        return 1
    os.environ["VP_TASK"] = TASK
    vp_slack.post(CH, LINE % int(m.group(2)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        if "--send" in sys.argv:
            ledger("Thursday email check did not complete (%s)." % type(e).__name__)
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
