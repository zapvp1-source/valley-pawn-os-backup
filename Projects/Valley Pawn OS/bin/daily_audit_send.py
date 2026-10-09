#!/usr/bin/env python3
"""daily_audit_send.py [--render] [--send] [--no-wait] [YYYY-MM-DD]

Native replacement (Mac-first wave 1, 2026-10-08) for the Cowork task `daily-store-audit-digest`
(Mon-Sat 09:40 ET). The task was already a wrapper: run bin/daily_audit_digest.py, apply a readiness gate,
send the file the script wrote VERBATIM to Joshua (and Preston when the switch says yes), write <DATE>.sent
and one RUN_LOG line. This does exactly those steps with the ops bot (Goldilocks) instead of the outbox.

  Step 1  run daily_audit_digest.py (exit 2 / NO_OPEN_STORES = nothing to do, stop silently)
  Step 2  complete=true -> send. Incomplete -> wait 10 min, run once more. Still incomplete but at least one
          store has an Intake or Sales line -> send anyway (the message already names what is missing).
          Nothing usable -> send Joshua ONLY the one plain on-hold line.
  Step 3  <DATE>.sent exists -> already sent, stop. Else post <DATE>.mrkdwn.txt to Joshua (U03BB52MDSA) and,
          if PRESTON_ENABLED: yes, to Preston (U03BWMEM9GR); write <DATE>.sent (one line per recipient).
  Step 4  one line in daily-audit/RUN_LOG.md (path=native).

THE SWITCH stays where it was: the `PRESTON_ENABLED:` line in the task's SKILL.md
(~/Documents/Claude/Scheduled/daily-store-audit-digest/SKILL.md). Missing/unreadable = no.

--render prints exactly what would be sent (and to whom) and sends nothing; it never waits (prints the gate
decision instead), writes the digest files to fleet/test_output/daily_audit_render/ (never over the real
daily-audit/ files) and writes no .sent / RUN_LOG line. --send is required to publish.
"""
import datetime as dt, json, os, re, subprocess, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
OUT = os.path.join(OS_DIR, "daily-audit")
RUNLOG = os.path.join(OUT, "RUN_LOG.md")
SKILL = os.path.expanduser("~/Documents/Claude/Scheduled/daily-store-audit-digest/SKILL.md")
JOSHUA, PRESTON = "U03BB52MDSA", "U03BWMEM9GR"


def preston_enabled():
    try:
        m = re.search(r"^PRESTON_ENABLED:\s*(\w+)", open(SKILL).read(), re.M)
        return bool(m) and m.group(1).lower() == "yes"
    except OSError:
        return False


def digest(day, out=None):
    r = subprocess.run([sys.executable, os.path.join(HERE, "daily_audit_digest.py")] + ([day] if day else [])
                       + (["--out", out] if out else []),
                       capture_output=True, text=True, timeout=600)
    line = (r.stdout or "").strip().splitlines()[-1:] or [""]
    return r.returncode, line[0]


def runlog(day, complete, sent_to, note):
    with open(RUNLOG, "a") as f:
        f.write("- %s | date=%s | complete=%s | sent_to=%s | path=native | note=%s\n"
                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), day, complete, sent_to or "none", note))


def main(a):
    render, send = "--render" in a, "--send" in a
    dry = render or not send
    day = next((x for x in a if re.fullmatch(r"\d{4}-\d{2}-\d{2}", x)), None)
    out = os.path.join(OS_DIR, "fleet", "test_output", "daily_audit_render") if dry else OUT
    rc, line = digest(day, out if dry else None)
    if rc == 2 or line.startswith("NO_OPEN_STORES"):
        print("NO_OPEN_STORES — nothing to do"); return 0
    m = re.search(r"DATE=(\S+)", line)
    if rc != 0 or not m:
        print("DIGEST FAILED:", line[:200])
        if not dry:
            runlog(day or "?", "?", None, "digest script failed both tries? rc=%s %s" % (rc, line[:80]))
        return 1
    d = m.group(1)
    js = json.load(open(os.path.join(out, d + ".json")))
    note = []
    if not js.get("complete"):
        if dry or "--no-wait" in a:
            note.append("incomplete (a live run waits 10 min and re-runs once)")
        else:
            time.sleep(600)
            rc, line = digest(d)
            js = json.load(open(os.path.join(OUT, d + ".json")))
            note.append("re-ran after 10 min")
    mfile = os.path.join(out, d + ".mrkdwn.txt")
    text = open(mfile).read()
    usable = bool(re.search(r"(?m)^• (Intake|Sales): ", text))
    recips = [JOSHUA] + ([PRESTON] if preston_enabled() else [])
    if js.get("complete") or usable:
        plan = [(u, text) for u in recips]
        kind = "digest"
    else:
        wd = dt.date.fromisoformat(d)
        hold = ("The daily store audit for %s %d/%d is on hold — the store reports for that day aren't in yet. "
                "It will go out once they are." % (wd.strftime("%A"), wd.month, wd.day))
        plan = [(JOSHUA, hold)]
        kind = "hold"
    sent_marker = os.path.join(OUT, d + ".sent")
    if dry:
        print("GATE date=%s complete=%s usable=%s -> %s%s" % (d, js.get("complete"), usable, kind,
              " | ALREADY SENT (.sent exists) — a live run would stop" if os.path.exists(sent_marker) and kind == "digest" else ""))
        for u, t in plan:
            print("=== DM %s\n%s" % (u, t))
        return 0
    if kind == "digest" and os.path.exists(sent_marker):
        print("already sent"); return 0
    import vp_slack
    done = []
    for u, t in plan:
        vp_slack.post(u, t)
        done.append(u)
        if kind == "digest":
            with open(sent_marker, "a") as f:
                f.write("%s | %s | native daily_audit_send.py | via ops bot\n" % (d, u))
    runlog(d, js.get("complete"), ",".join(done), ("on-hold line only; " if kind == "hold" else "")
           + "; ".join(note + ["%d exceptions" % len(js.get("exceptions") or [])]) + ("; Preston enabled" if PRESTON in done else "; Preston disabled per switch"))
    print("SENT %s %s to %s" % (kind, d, ",".join(done)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
