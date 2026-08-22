#!/usr/bin/env python3
"""perf_guard.py — native Layer-0 performance guard (added 2026-08-21).

WHY: 2026-08-21 the Mac hit load average 171+ twice in one day because unified-search
index runs stacked (5 concurrent refresh.sh chains, ~45 pool workers + pdftotext,
on a 92%-full swap-thrashing disk) and froze the UI/Chrome/Slack. usearch.py and
refresh.sh now carry their own locks; this guard is the backstop that also catches
pre-lock strays, orphaned pool workers, and anything else that pins the machine.

Runs every 30 min via launchd com.valleypawn.perf-guard (vp-runner pattern,
logs in ~/Library/Logs/valleypawn/). Detect-and-fix, log always; DM Joshua
(plain language, vp-ops bot, conversations.open) at most once per 6h and only
when it had to take action. NEVER touches Parallels/Bravo, Claude, Chrome.
"""
import os, sys, json, time, subprocess, urllib.request

HOME = os.path.expanduser("~")
LOGDIR = os.path.join(HOME, "Library/Logs/valleypawn")
LOG = os.path.join(LOGDIR, "perf_guard.log")
STATE = os.path.join(LOGDIR, "perf_guard_state.json")
JOSHUA_USER = "U03BB52MDSA"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"
DM_COOLDOWN_S = 6 * 3600
LOAD_RENICE_THRESHOLD = 60.0

# process patterns owned by the unified-search index pipeline (safe to manage)
INDEX_PATTERNS = ("usearch.py mail", "usearch.py files", "usearch.py gdrive",
                  "msgindex.py", "notesindex.py", "remindersindex.py",
                  "photosindex.py", "bash refresh.sh")


def log(msg):
    os.makedirs(LOGDIR, exist_ok=True)
    line = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line)


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=30).stdout
    except Exception:
        return ""


def ps_snapshot():
    out = sh("ps -Aro pid,ppid,etime,pcpu,args")
    rows = []
    for ln in out.splitlines()[1:]:
        parts = ln.split(None, 4)
        if len(parts) == 5:
            rows.append({"pid": parts[0], "ppid": parts[1], "etime": parts[2],
                         "pcpu": float(parts[3] or 0), "args": parts[4]})
    return rows


def etime_seconds(e):
    # etime formats: MM:SS, HH:MM:SS, D-HH:MM:SS
    days = 0
    if "-" in e:
        d, e = e.split("-", 1)
        days = int(d)
    bits = [int(x) for x in e.split(":")]
    while len(bits) < 3:
        bits.insert(0, 0)
    return days * 86400 + bits[0] * 3600 + bits[1] * 60 + bits[2]


def main():
    actions = []
    rows = ps_snapshot()

    # 1) Stacked index runs: keep the NEWEST of each pattern, kill the rest.
    for pat in INDEX_PATTERNS:
        procs = [r for r in rows if pat in r["args"] and "perf_guard" not in r["args"]]
        if len(procs) > 1:
            procs.sort(key=lambda r: etime_seconds(r["etime"]))  # newest first
            for r in procs[1:]:
                sh("kill %s" % r["pid"])
                actions.append("killed duplicate '%s' pid %s (age %s)" % (pat, r["pid"], r["etime"]))

    # 2) Orphaned multiprocessing pool workers (ppid 1, idle 'Python -c from...').
    for r in rows:
        if r["ppid"] == "1" and "Python -c from" in r["args"] and etime_seconds(r["etime"]) > 1800:
            sh("kill %s" % r["pid"])
            actions.append("killed orphaned pool worker pid %s (age %s)" % (r["pid"], r["etime"]))

    # 3) pdftotext swarm: cap at 8, kill the oldest beyond that.
    pdfs = [r for r in rows if r["args"].startswith("pdftotext") or "/pdftotext" in r["args"].split(" ")[0]]
    if len(pdfs) > 8:
        pdfs.sort(key=lambda r: -etime_seconds(r["etime"]))  # oldest first
        for r in pdfs[:len(pdfs) - 8]:
            sh("kill %s" % r["pid"])
            actions.append("killed excess pdftotext pid %s" % r["pid"])

    # 4) High load: renice any surviving index-pipeline processes to +15.
    try:
        load1 = float(sh("sysctl -n vm.loadavg").strip("{} \n").split()[0])
    except Exception:
        load1 = 0.0
    if load1 > LOAD_RENICE_THRESHOLD:
        for pat in INDEX_PATTERNS + ("pdftotext",):
            for r in ps_snapshot():
                if pat in r["args"]:
                    sh("renice 15 -p %s" % r["pid"])
        actions.append("load %.0f > %.0f: reniced index pipeline" % (load1, LOAD_RENICE_THRESHOLD))

    if not actions:
        log("ok (load %.1f)" % load1)
        return

    for a in actions:
        log(a)

    # DM Joshua, plain language, max once per 6h.
    st = {}
    try:
        st = json.load(open(STATE))
    except Exception:
        pass
    if time.time() - st.get("last_dm", 0) > DM_COOLDOWN_S:
        tok = sh("security find-generic-password -s %s -w 2>/dev/null" % KEYCHAIN_SERVICE).strip() \
              or os.environ.get("SLACK_BOT_TOKEN", "").strip()
        if tok:
            try:
                def call(method, payload):
                    req = urllib.request.Request(
                        "https://slack.com/api/" + method,
                        data=json.dumps(payload).encode(),
                        headers={"Authorization": "Bearer " + tok,
                                 "Content-Type": "application/json; charset=utf-8"})
                    return json.load(urllib.request.urlopen(req, timeout=15))
                ch = call("conversations.open", {"users": JOSHUA_USER})
                if ch.get("ok"):
                    txt = ("Performance guard: I cleaned up %d runaway background "
                           "process(es) that were slowing the Mac down. Everything's "
                           "handled — no action needed." % len(actions))
                    call("chat.postMessage", {"channel": ch["channel"]["id"], "text": txt})
                    st["last_dm"] = time.time()
                    json.dump(st, open(STATE, "w"))
            except Exception as e:
                log("DM failed: %s" % e)


if __name__ == "__main__":
    main()
