#!/usr/bin/env python3
"""health_weekly_digest.py [--render] [--send] [--day YYYY-MM-DD]

Native replacement (Mac-first wave 2, 2026-10-14) for the Cowork task `health-weekly-digest` (Sun 09:00 ET).
SKILL steps on the folder ~/Documents/Claude/Projects/Health Optimization:
  1 refresh the nights ledger (scripts/night_signature.py), read Nights_Summary.md + Nights_Ledger.csv
  2 this week's episodes: Episode_Log.csv rows + files added to episodes/ in the last 7 days
  3 open tests: Open_Tests_Tracker.md rows not resulted/filed/n/a, days open from `Opened` (>30 = overdue);
    STATUS.md "## Update <date>" sections SUPERSEDE tracker rows (10/8: the bundled draw WAS ordered 6/25 etc.)
  4 drift check: content files newer than Master_Findings_Index.md -> written into STATUS.md's "Unfolded" section
  5 ONE DM to Joshua, written by Claude (bin/vp_ai.py) from the facts computed here — the SKILL's four sections,
    under ~200 words, no jargon/paths, never diagnose/speculate/recommend treatment
  6 one dated line at the top of the folder's CHANGELOG.md
The numbers are computed here, not by the model; the model only words them and is told to use no other facts.
--render prints the facts + the DM and writes nothing (ledger refresh skipped). --send publishes.
Duplicate guard: a digest already sent to Joshua's DM today (marker "This week's sleep") = no second DM.
"""
import csv
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_ai  # noqa: E402
import vp_slack  # noqa: E402

TASK = "health-weekly-digest"
ET = ZoneInfo("America/New_York")
HF = os.path.expanduser("~/Documents/Claude/Projects/Health Optimization")
LEDGER = os.path.join(os.path.dirname(HERE), "fleet", "FAILURE_LEDGER.md")
JOSHUA = "U03BB52MDSA"
DONE = ("resulted", "filed", "n/a", "closed", "done")
DRIFT_IGNORE = {"STATUS.md", "CHANGELOG.md", "Nights_Ledger.csv", "Nights_Summary.md", "Open_Tests_Tracker.md",
                "Master_Findings_Index.md", "Episode_Log.csv"}

SYSTEM = """You write Joshua Davis's private weekly health digest, a Slack DM to him only. Plain English, warm and direct,
the way you'd tell a friend what his own data showed this week. No jargon, no file paths, no file or script names.
NEVER diagnose, never speculate about causes, never recommend a treatment — describe what the data shows and what is
outstanding. Use ONLY the facts in the JSON you are given; do not add numbers, dates, names or items that are not in it.
Where a STATUS update corrects a tracker row, the STATUS update wins (e.g. an item it says was ordered is not 'never ordered').
Format exactly (Slack mrkdwn), dropping any section with nothing to say except episodes:
*This week's sleep*
<one or two sentences: how many of the last 7 nights flagged the episode pattern (name the dates only if few;
mention how many nights had data only when it is fewer than 6, as a data gap),
the last-30 vs prior-30 share and whether that trend is up, down or flat>

*Episodes you logged*
<each with date, time, what the Oura data showed — or one line saying nothing was logged this week (and since when)>

*New records*
<only if something was filed this week; repeat only the lab's own flags>

*Needs a nudge* (<short qualifier, e.g. all open 30+ days>)
• <item> — <how long / what is outstanding>. <what would close it>.
(max 5 bullets, most important first; merge related items)

End with one short line: "Nothing diagnosed here — just what the data and the file show. Medical calls are yours with your doctors."
Whole message under ~200 words. Output ONLY the message."""


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def nights(day, upto=None):
    """Nights are keyed by wake-up date. Live window = the 7 nights ending today (today's night is in the ledger once
    the 08:30 Oura import ran). `upto` (render replays) caps the data at what the live run could have seen."""
    rows = [x for x in csv.DictReader(open(os.path.join(HF, "Nights_Ledger.csv"))) if not upto or x["day"] <= upto]
    def win(a, b):
        r = [x for x in rows if a <= x["day"] <= b]
        sig = [x for x in r if str(x.get("signature_night")).strip() in ("1", "True", "true")]
        return r, sig
    d = lambda n: (day - dt.timedelta(days=n)).isoformat()  # noqa: E731
    w7, s7 = win(d(6), d(0))
    w30, s30 = win(d(29), d(0))
    p30, sp30 = win(d(59), d(30))
    last_sig = max((x["day"] for x in rows if str(x.get("signature_night")).strip() in ("1", "True", "true")), default=None)
    pct = lambda a, b: round(100.0 * len(a) / len(b)) if b else None  # noqa: E731
    return {"last_7_nights": {"nights_with_data": len(w7), "signature_nights": len(s7), "dates": [x["day"] for x in s7],
                              "logged_as_episode": [x["day"] for x in s7 if str(x.get("episode_logged")).strip() in ("1", "True", "true")]},
            "last_30": {"nights": len(w30), "signature": len(s30), "pct": pct(s30, w30)},
            "prior_30": {"nights": len(p30), "signature": len(sp30), "pct": pct(sp30, p30)},
            "most_recent_flagged_night": last_sig,
            "newest_night_in_data": max((x["day"] for x in rows), default=None)}


def summary_windows():
    """The SKILL reads Nights_Summary.md (night_signature.py's own 30-night windows). Used on live runs."""
    out = {}
    for line in open(os.path.join(HF, "Nights_Summary.md")):
        m = re.match(r"\|\s*(Last|Prior) 30 nights\s*\|\s*(\d+)\s*\|\s*(\d+) \((\d+)%\)", line)
        if m:
            out["last_30" if m.group(1) == "Last" else "prior_30"] = {"nights": int(m.group(2)), "signature": int(m.group(3)), "pct": int(m.group(4))}
    return out


def episodes(day):
    since = day - dt.timedelta(days=7)
    rows = list(csv.DictReader(open(os.path.join(HF, "Episode_Log.csv"))))
    this = [r for r in rows if since.isoformat() <= (r.get("date") or "") < day.isoformat()]
    files = [os.path.basename(p) for p in glob.glob(os.path.join(HF, "episodes", "*"))
             if dt.datetime.fromtimestamp(os.path.getmtime(p), ET).date() >= since]
    last = max((r.get("date") or "" for r in rows), default=None)
    return {"this_week": [{k: r.get(k) for k in ("date", "start_time", "end_time", "symptoms", "severity_1to10", "HR_during_bpm", "notes")} for r in this],
            "episode_files_added": files, "last_logged_date": last}


def records(day):
    since = day - dt.timedelta(days=7)
    out = []
    for sub in ("records", "_inbox"):
        for p in glob.glob(os.path.join(HF, sub, "*")):
            if os.path.basename(p).lower() != "readme.md" and dt.datetime.fromtimestamp(os.path.getmtime(p), ET).date() >= since:
                out.append(os.path.basename(p))
    for p in glob.glob(os.path.join(HF, "New_Records_*.md")):
        if dt.datetime.fromtimestamp(os.path.getmtime(p), ET).date() >= since:
            out.append(os.path.basename(p))
    return out


def open_items(day):
    out = []
    for line in open(os.path.join(HF, "Open_Tests_Tracker.md")):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 7 or not re.match(r"^(R?\d+)$", c[0]):
            continue
        try:
            opened = dt.date.fromisoformat(c[4])
        except ValueError:
            continue
        if c[5].lower() in DONE:
            continue
        age = (day - opened).days
        out.append({"id": c[0], "item": c[1], "why": c[2], "opened": c[4], "status": c[5], "notes": c[6], "days_open": age, "overdue": age > 30})
    return out


def status_updates():
    txt = open(os.path.join(HF, "STATUS.md")).read()
    parts = re.findall(r"(## Update [^\n]*\n.*?)(?=\n## |\Z)", txt, re.S)
    return "\n\n".join(parts)[:4000]


def drift():
    idx = os.path.getmtime(os.path.join(HF, "Master_Findings_Index.md"))
    out = []
    for p in glob.glob(os.path.join(HF, "*.md")) + glob.glob(os.path.join(HF, "*.csv")) + glob.glob(os.path.join(HF, "*.xlsx")):
        b = os.path.basename(p)
        if b in DRIFT_IGNORE or b.startswith("Episode_"):
            continue
        if os.path.getmtime(p) > idx + 120:     # 2-min slack: same-session saves are timestamp noise (9/6, 10/4 runs)
            out.append(b)
    return sorted(out)


def write_unfolded(files, day):
    p = os.path.join(HF, "STATUS.md")
    txt = open(p).read()
    body = ("\n".join("- `%s`" % f for f in files) if files else "- (none — drift check %s found nothing newer than the index)" % day)
    new = "## Unfolded (files newer than the index that the index doesn't reflect) — checked %s\n%s\n" % (day, body)
    txt2, n = re.subn(r"## Unfolded[^\n]*\n(?:(?!\n## ).)*?\n(?=\n## |\Z)", new, txt, count=1, flags=re.S)
    if n == 0:
        txt2 = txt.rstrip("\n") + "\n\n" + new
    if txt2 != txt:
        open(p, "w").write(txt2)


def changelog(line):
    p = os.path.join(HF, "CHANGELOG.md")
    txt = open(p).read()
    head, _, rest = txt.partition("\n\n")
    open(p, "w").write(head + "\n\n" + line + "\n\n" + rest)




def _dm_already(dm, marker, hours, key):
    """2026-10-23: the ops bot has no im:history scope, so vp_slack.has() on Joshua's DM exits with
    'missing_scope' and killed the run BEFORE the DM was sent (Publer 10/16, health digest 10/18 — no receipts).
    Dedupe on a local sent-marker instead; the Slack read is tried only as a bonus and never fatal."""
    import time
    f = os.path.join(HERE, "..", "fleet", "state", "dm_sent", key)
    try:
        if os.path.exists(f) and time.time() - os.path.getmtime(f) < hours * 3600:
            return True
    except OSError:
        pass
    try:
        return bool(vp_slack.has(dm, marker, hours))
    except SystemExit:
        return False


def _dm_mark(key):
    d = os.path.join(HERE, "..", "fleet", "state", "dm_sent")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, key), "w").write(dt.datetime.now().isoformat(timespec="seconds") + "\n")

def main():
    render = "--render" in sys.argv
    send = "--send" in sys.argv and not render
    day = dt.date.fromisoformat(arg("--day")) if arg("--day") else dt.datetime.now(ET).date()
    refreshed = "skipped (render)"
    if send:
        p = subprocess.run(["/usr/bin/python3", "scripts/night_signature.py"], cwd=HF, capture_output=True, text=True, timeout=600)
        refreshed = "ok" if p.returncode == 0 else "failed: " + (p.stdout + p.stderr).strip()[-200:]
    facts = {"today": day.isoformat(), "sleep": nights(day, None if day >= dt.datetime.now(ET).date() else (day - dt.timedelta(days=1)).isoformat()), "episodes": episodes(day), "new_records_this_week": records(day),
             "open_items": open_items(day), "status_updates_supersede_tracker": status_updates(),
             "ledger_refresh": refreshed}
    if day >= dt.datetime.now(ET).date():
        facts["sleep"].update(summary_windows())
    fresh_gap = (day - dt.date.fromisoformat(facts["sleep"]["newest_night_in_data"])).days if facts["sleep"]["newest_night_in_data"] else 99
    if fresh_gap > 2:
        facts["data_warning"] = "Sleep data has not updated since %s (%d days) — say so first, plainly." % (facts["sleep"]["newest_night_in_data"], fresh_gap)
    files = drift()
    print("FACTS", json.dumps(facts, indent=1, default=str)[:6000])
    print("DRIFT", files)
    text = vp_ai.ask("Facts for this week's digest (JSON):\n" + json.dumps(facts, default=str), system=SYSTEM, max_tokens=4000).strip()
    print("=== DM %s\n%s" % (JOSHUA, text))
    if not send:
        return 0
    write_unfolded(files, day)
    dm = vp_slack.dm_channel(JOSHUA)
    if _dm_already(dm, "This week's sleep", 12, "health-weekly-digest"):
        print("digest already sent today")
        return 0
    os.environ["VP_TASK"] = TASK
    vp_slack.post(dm, text)
    _dm_mark("health-weekly-digest")
    s = facts["sleep"]
    changelog("## %s — Weekly digest sent (native). Ledger refresh %s. Signature nights %d of last 7; %s%% last 30 vs %s%% prior 30. "
              "Episodes logged this week: %d (last logged %s). Open items over 30 days: %d. Index drift: %s."
              % (day, refreshed, s["last_7_nights"]["signature_nights"], s["last_30"]["pct"], s["prior_30"]["pct"],
                 len(facts["episodes"]["this_week"]), facts["episodes"]["last_logged_date"],
                 sum(1 for o in facts["open_items"] if o["overdue"]), ", ".join(files) or "none"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        if "--send" in sys.argv:
            ledger("This week's health digest was not sent (%s)." % type(e).__name__)
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
