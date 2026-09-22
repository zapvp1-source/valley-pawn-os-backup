#!/usr/bin/env python3
"""task_buckets.py — sort EVERY scheduled task into what it needs to run unattended.

WHY (Joshua, 2026-09-21): "I WANT ALL THE TASKS working ... what is the plan that wont take weeks."
The single structural fact: a scheduled session has no Mac-control connector and hits a browser
permission card at any hour. So every task falls into one of three buckets, decided by reading its
own instructions, not by guessing:
  A  needs neither          -> enable now, it will work
  B  needs a browser        -> needs chromePermissionMode=skip + domain, then enable
  C  needs Mac control      -> must be converted to native / host-queue; enabling it does nothing
"""
import json, os, re
REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/"
                         "823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/"
                         "scheduled-tasks.json")
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
LA = os.path.expanduser("~/Library/LaunchAgents")
OSA = re.compile(r"Control_your_Mac|osascript|prlctl|AppleScript|host-shell|host shell", re.I)
BRW = re.compile(r"claude-in-chrome|Claude_Browser|browser_batch|get_page_text|read_page|"
                 r"navigate to|open .*\.(com|io|net)|Chrome extension|computer-use|screenshot", re.I)
DOM = re.compile(r"https?://([a-z0-9.-]+\.[a-z]{2,})", re.I)
# Cowork tasks already replaced by a native agent — must stay OFF or they double-post
RETIRED = {"pawn-walk","sold-review","discount-review","bravo-morning-pull","bravo-prestaging-7am",
           "bravo-preflight-relaunch","bravo-health-watchdog","business-os-daily-refresh",
           "unified-search-index-refresh","unified-search-verify","vp-os-github-nightly-backup",
           "daily-unopened-email-eval","jewelry-onhand-nightly-pull","jewelry-onhand-catchup",
           "daily-funds-verification"}
tasks = json.load(open(REG))["scheduledTasks"]
A, B, C, X = [], [], [], []
for t in tasks:
    tid = str(t.get("id"))
    p = os.path.join(SCHED, tid, "SKILL.md")
    if not os.path.isfile(p):
        X.append((tid, "no SKILL.md")); continue
    body = open(p, errors="replace").read()
    # ignore the blocks THIS week's tooling appended (they mention the connector to say it is gone)
    body = body.split("# DATA-FIRST GATE OVERRIDE")[0].split("## Precondition (MANDATORY)")[0]
    en = bool(t.get("enabled"))
    mode = t.get("chromePermissionMode")
    doms = sorted(set(d.lower() for d in DOM.findall(body) if not d.endswith(("slack.com","anthropic.com","claude.com"))))
    if tid in RETIRED:
        X.append((tid, "retired -> native agent")); continue
    if OSA.search(body):
        C.append((tid, en))
    elif BRW.search(body):
        B.append((tid, en, mode, doms[:4], t.get("chromeAllowedDomains") or []))
    else:
        A.append((tid, en))
def sec(title, rows, fmt):
    print("\n## %s (%d)\n" % (title, len(rows)))
    for r in rows: print(fmt(r))
print("# Every task, by what it needs to run unattended\n")
sec("A — needs nothing special: enable and it works",
    sorted(A, key=lambda r:(r[1],r[0])), lambda r: "- %s  [%s]" % (r[0], "on" if r[1] else "OFF"))
sec("B — needs a browser: permission flag + domain, then enable",
    sorted(B, key=lambda r:(r[1],r[0])),
    lambda r: "- %s  [%s]  mode=%s  needs=%s  has=%s" % (r[0], "on" if r[1] else "OFF", r[2], r[3], r[4]))
sec("C — needs Mac control: convert to native; enabling does nothing",
    sorted(C, key=lambda r:(r[1],r[0])), lambda r: "- %s  [%s]" % (r[0], "on" if r[1] else "OFF"))
sec("Excluded", X, lambda r: "- %s — %s" % r)
offA = sum(1 for _,e in A if not e); offB = sum(1 for r in B if not r[1]); offC = sum(1 for _,e in C if not e)
print("\nSUMMARY A=%d(off %d) B=%d(off %d) C=%d(off %d)" % (len(A),offA,len(B),offB,len(C),offC))
