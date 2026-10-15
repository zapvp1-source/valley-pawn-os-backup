#!/usr/bin/env python3
"""publer_friday.py [--render] [--send] [--day YYYY-MM-DD]

Native replacement (Mac-first wave 2, 2026-10-14) for the Cowork task `vp-publer-analytics-friday` (Fri 16:00 ET).
The SKILL's steps, unchanged — the scripts are the same ones the Cowork run called:
  1 `python3 publer_weekly_digest.py` in Refine Social Media (writes friday_digests/friday_digest_<date>.md,
    weekly-adjustments.json, adjustments_log.jsonl, ~/.vp-studio/lessons.md — Monday's planner reads them)
  2 `python3 -m vp_social digest --days 7`: exit 0 -> that stdout IS the DM to Joshua, verbatim;
    exit 2 -> no DM, the reason goes under "## Run holds" in Valley Pawn Studios/STATUS.md
  3 sanity: weekly-adjustments.json must be modified today, else one FAILURE_LEDGER row (silent)
Duplicate guard: a "Weekly Social Digest — <from> to <to>" DM for the same window already in Joshua's DM = no DM.
--render: no step 1, no DM — prints the digest for --day's 7-day window (default today). --send publishes.
"""
import datetime as dt
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack  # noqa: E402

TASK = "vp-publer-analytics-friday"
ET = ZoneInfo("America/New_York")
RSM = os.path.expanduser("~/Documents/Claude/Projects/Refine Social Media")
STATUS = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md")
LEDGER = os.path.join(os.path.dirname(HERE), "fleet", "FAILURE_LEDGER.md")
ADJ = os.path.join(RSM, "weekly-adjustments.json")
PY = "/usr/bin/python3"
ENV = dict(os.environ, PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin")
JOSHUA = "U03BB52MDSA"


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def hold(reason):
    now = dt.datetime.now(ET)
    try:
        txt = open(STATUS).read()
    except OSError:
        txt = ""
    line = "- %s — Friday social digest not sent (native %s): %s\n" % (now.strftime("%Y-%m-%d %H:%M ET"), TASK, reason.strip()[:400])
    with open(STATUS, "a") as f:
        if "## Run holds" not in txt:
            f.write("\n## Run holds\n")
        f.write(line)


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def render_digest(day):
    sys.path.insert(0, RSM)
    from vp_social import reader, report  # noqa: E402
    orig = reader.date_range
    reader.date_range = lambda back, fwd=0, today=None: orig(back, fwd, today or day)
    try:
        return report.digest(7)
    finally:
        reader.date_range = orig


def main():
    render = "--render" in sys.argv
    send = "--send" in sys.argv and not render
    day = dt.date.fromisoformat(arg("--day")) if arg("--day") else dt.datetime.now(ET).date()
    if not send:
        try:
            print(render_digest(day))
        except Exception as e:  # noqa: BLE001
            print("WITHHOLD (no DM):", type(e).__name__, e)
        return 0
    # 1 the digest engine (files Monday's planner reads)
    p = subprocess.run([PY, "publer_weekly_digest.py"], cwd=RSM, capture_output=True, text=True, timeout=900, env=ENV)
    print("\n".join((p.stdout + p.stderr).strip().splitlines()[-15:]))
    # 2 the DM text
    q = subprocess.run([PY, "-m", "vp_social", "digest", "--days", "7"], cwd=RSM, capture_output=True, text=True, timeout=600, env=ENV)
    if q.returncode != 0 or not q.stdout.strip():
        hold((q.stderr or "no output").strip().splitlines()[-1] if (q.stderr or "").strip() else "digest returned nothing")
        print("no DM:", q.stderr.strip()[-300:])
    else:
        text = q.stdout.strip()
        head = text.splitlines()[0].strip("*")
        dm = vp_slack.dm_channel(JOSHUA)
        if vp_slack.has(dm, head, 5 * 24):
            print("already sent:", head)
        else:
            os.environ["VP_TASK"] = TASK
            vp_slack.post(dm, text)
    # 3 sanity
    try:
        fresh = dt.datetime.fromtimestamp(os.path.getmtime(ADJ), ET).date() == dt.datetime.now(ET).date()
    except OSError:
        fresh = False
    if not fresh:
        ledger("Friday social digest ran but weekly-adjustments.json was not updated today, so Monday's batch will reuse last week's mix.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        if "--send" in sys.argv:
            ledger("Friday social digest did not complete (%s)." % type(e).__name__)
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
