#!/usr/bin/env python3
"""log_triage.py — find native agents that are silently dead.

WHY (2026-09-18): field_scorecard.py — the fleet's own watchdog — had been crashing on EVERY run
with an AttributeError, because a loop variable named `state` shadowed the persistent state dict and
the script then wrote a bare string into its own state file. Nothing noticed, because a crashed
watchdog produces no alarm about itself. It was dead through both multi-day outages.

If that happened to the watchdog, assume it happened elsewhere. This reads every heartbeat log and
reports: last write (is it even running?), crash/traceback counts, and the most recent error line.
A log that has not been written in days is as damning as a log full of tracebacks — more so, because
a silent agent looks exactly like a healthy one from outside.

    log_triage.py [--days 7]
"""
import datetime as dt
import glob
import os
import plistlib
import re
import sys

LOG_DIR = os.path.expanduser("~/Library/Logs/valleypawn")
LA = os.path.expanduser("~/Library/LaunchAgents")


def expected_gap_hours():
    """Map each log file -> how long that agent may legitimately stay quiet.

    2026-09-18: the first version of this tool used a flat 48h threshold and reported
    `compliance-brief` as STALE. It is a WEEKLY agent and had run exactly on schedule four days
    earlier. Calling a healthy weekly job dead is the same false-alarm class that has already cost
    trust this week, so staleness is now derived from each agent's OWN schedule, read from its
    plist, instead of assumed."""
    gaps = {}
    for f in sorted(glob.glob(os.path.join(LA, "*.plist"))):
        try:
            with open(f, "rb") as fh:
                d = plistlib.load(fh)
        except Exception:
            continue
        sci = d.get("StartCalendarInterval")
        if d.get("StartInterval"):
            gap = max(2.0, d["StartInterval"] / 3600.0 * 3)
        elif isinstance(sci, list):
            # several fire times: weekly if any entry pins a Weekday, else daily
            gap = 9 * 24.0 if any("Weekday" in e for e in sci if isinstance(e, dict)) else 30.0
            # 2026-10-06: a list of Day entries (monthly-prestage fires on days 28-31) is MONTHLY,
            # not daily — it was reported stale every month from the 30h daily guess.
            if all(isinstance(e, dict) and "Day" in e and "Weekday" not in e for e in sci):
                gap = 40 * 24.0
        elif isinstance(sci, dict):
            if "Month" in sci:
                # a dated one-shot (e.g. fwb-catchup-20261005) shares the real agent's log; letting it
                # set the gap made forfeiture-winback's weekly log "allowed 40 days". It has no cadence.
                continue
            if "Weekday" in sci:
                gap = 9 * 24.0
            elif "Day" in sci:
                gap = 40 * 24.0            # monthly
            elif "Hour" in sci:
                gap = 30.0                 # once a day
            else:
                gap = 3.0                  # every hour
        else:
            gap = 48.0
        # Two plists can name the same log; the MORE FREQUENT schedule is the one that must hold.
        names = []
        for key in ("StandardOutPath", "StandardErrorPath"):
            v = d.get(key)
            if v:
                names += [os.path.basename(v),
                          os.path.basename(v).replace(".out.log", ".log").replace(".err.log", ".log")]
        for n in names:
            gaps[n] = min(gap, gaps.get(n, gap))
        # the vlog file is often named after the LABEL: evidence only — it must not change the gap
        # of a log nobody declared (chrome-extension-watchdog.log logs on events, not every 2 min)
        lab = str(d.get("Label", "")).replace("com.valleypawn.", "")
        group = names + ([lab + ".log"] if lab else [])
        if lab:
            LABEL_LOGS.setdefault(lab, set()).update(group)
        for n in group:
            for o in group:
                SIBLINGS.setdefault(n, set()).add(o)
    return gaps


# ---- 2026-10-06: liveness EVIDENCE, not one file's mtime -----------------------------------------
# The nightly doctor reported 20 "quiet" jobs on 10/6; 17 were running fine. Many native agents write
# nothing to launchd's stdout file (.out.log stays 0 bytes forever) because they log through vlog to
# <task>.log, to a run.log in a sub-folder, or only leave a receipt in fleet/receipts/. Judging each
# FILE alone made a healthy agent look dead. A log is now stale only if NONE of its agent's evidence
# is fresh: sibling logs (same stem / same plist / label-named vlog), <stem>/run.log, the receipt
# file, and any extra paths in fleet/log_triage_expectations.json. A .err.log is NEVER evidence of
# health (it is written only on failure). A genuinely dead agent has no fresh evidence anywhere, so
# it is still reported.
SIBLINGS = {}
LABEL_LOGS = {}
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
EXPECT_PATH = os.path.join(OS_DIR, "fleet", "log_triage_expectations.json")


def load_expectations():
    """{"retired": {log: why}, "aliases": {log: label}, "evidence": {log: [glob, ...]},
    "gap_hours": {log: hours}} — every entry carries its reason; absent file = no expectations."""
    try:
        import json
        d = json.load(open(EXPECT_PATH))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def stem_of(name):
    for suf in (".launchd.log", ".out.log", ".err.log", ".log"):
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def evidence_paths(name, exp):
    st = stem_of(name)
    cands = set(SIBLINGS.get(name, set()))
    cands.update({st + ".log", st + ".out.log", st + ".launchd.log"})
    alias = (exp.get("aliases") or {}).get(name)
    if alias:
        cands.update(LABEL_LOGS.get(alias.replace("com.valleypawn.", ""), set()))
    paths = [os.path.join(LOG_DIR, c) for c in cands if c != name and not c.endswith(".err.log")]
    for s in {st} | {stem_of(c) for c in cands}:
        paths.append(os.path.join(LOG_DIR, s.replace("-", "_"), "run.log"))
        paths.append(os.path.join(OS_DIR, "fleet", "receipts", s + ".jsonl"))
    for g in (exp.get("evidence") or {}).get(name, []):
        paths += glob.glob(os.path.expanduser(g))
    return paths


def freshest(paths):
    best = None
    for p in paths:
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if best is None or mt > best[0]:
            best = (mt, p)
    return best
DAYS = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
BAD = re.compile(r"CRASH|Traceback|AttributeError|KeyError|TypeError|ValueError|NameError|"
                 r"command not found|No such file|Permission denied|"
                 r"unexpected EOF|SyntaxError|Operation not permitted", re.I)

# Phrases that MATCH a failure word while describing something working correctly. Left in, they
# make the nightly report cry wolf, and an alert that cries wolf is an alert nobody reads —
# which is how the fleet got here. Each entry is a real false positive seen on 2026-09-18:
#   "certificate written: ... items-to-price FAILED WAY"  -> WAY is a STORE CODE in a success line
#   "REFUSED <job>" in host-queue.log                     -> the allow-list doing exactly its job
#   "slack refused: channel_not_found"                    -> real, and kept: see BAD_EXTRA below
BENIGN = re.compile(r"certificate written|^\s*\d{4}-\d{2}-\d{2} [\d:]+ REFUSED |"
                    r"REFUSED: line \d+|DRY RUN|SIMULAT", re.I)
# Failures worth reporting that the generic pattern above deliberately no longer catches.
BAD_EXTRA = re.compile(r"slack refused|refused the post|FAILED —|FAILED -|bootout failed", re.I)


def main():
    files = sorted(glob.glob(os.path.join(LOG_DIR, "*.log")))
    if not files:
        print("no logs in %s" % LOG_DIR)
        return 0
    now = dt.datetime.now()
    gaps = expected_gap_hours()
    exp = load_expectations()
    retired = exp.get("retired") or {}
    for n, lab in (exp.get("aliases") or {}).items():
        lg = LABEL_LOGS.get(lab.replace("com.valleypawn.", ""), set())
        g = [gaps[x] for x in lg if x in gaps]
        if g and n not in gaps:
            gaps[n] = min(g)
    for n, h in (exp.get("gap_hours") or {}).items():
        gaps[n] = float(h)
    rows = []
    skipped = []
    for p in files:
        if os.path.basename(p) in retired:
            skipped.append((os.path.basename(p), retired[os.path.basename(p)]))
            continue
        try:
            mt = dt.datetime.fromtimestamp(os.path.getmtime(p))
            age_h = (now - mt).total_seconds() / 3600.0
            lines = open(p, errors="replace").read().splitlines()
        except OSError:
            continue
        # Only count problems INSIDE the window. Without this, a fault that was fixed today keeps
        # being counted forever off old log lines — and the nightly doctor would DM Joshua about
        # already-repaired problems every night until the log rotated, which is precisely the
        # crying-wolf pattern that makes a real alert get ignored.
        cutoff = (now - dt.timedelta(days=DAYS)).strftime("%Y-%m-%d")
        recent = lines[-4000:]
        hits = []
        for l in recent:
            if not (BAD.search(l) or BAD_EXTRA.search(l)):
                continue
            if BENIGN.search(l):
                continue
            m = re.match(r"(\d{4}-\d{2}-\d{2})", l.strip())
            if m:
                if m.group(1) >= cutoff:
                    hits.append(l)
            elif age_h <= DAYS * 24:
                hits.append(l)          # undated line: judge it by the file's own recency
        # "problems in the last 7 days" cannot tell FAILING NOW from failed-and-already-fixed. The
        # scorecard crashed at 23:14 and was repaired at 23:18; a 7-day count would report it as
        # broken for a week. `still_failing` asks the only question that matters for an alert: does
        # the END of the log — the most recent run — show a problem?
        # Must be judged off `hits`, which is already date-filtered. Matching the raw tail instead
        # flagged two .err.logs whose only traceback was weeks old, and reported "STILL FAILING (0
        # problem lines)" — a self-contradicting line that would have destroyed trust in the report
        # on its first night.
        tail = [l for l in recent[-12:] if l.strip()]
        still_failing = bool(hits) and hits[-1] in tail
        name = os.path.basename(p)
        gap = gaps.get(name, 48.0)
        # For a .err.log the tail is ALWAYS the last error, because nothing else is ever written to
        # it — so "the tail shows a problem" is permanently true once anything has failed. What
        # actually matters is whether it has been written to since the agent last should have run.
        # github-backup's EOF error was fixed on 9/18; without this its .err.log would report it
        # forever. So: an error log untouched for longer than the agent's own interval means clean.
        if name.endswith(".err.log") and age_h > gap:
            still_failing = False
        # A .err.log is written ONLY when something goes wrong, so an OLD one means the agent has
        # been clean — the healthiest possible signal. Flagging it as stale (as the first two
        # versions of this tool did) inverts the meaning and manufactures alarms out of good news.
        # Staleness applies to .log / .out.log, which every run writes to.
        is_err = name.endswith(".err.log")
        stale = (not is_err) and age_h > gap
        via = ""
        if stale:
            fb = freshest(evidence_paths(name, exp))
            if fb and (now.timestamp() - fb[0]) / 3600.0 <= gap:
                stale = False
                via = os.path.relpath(fb[1], os.path.expanduser("~"))
        rows.append({"name": name, "age_h": age_h, "mt": mt, "gap": gap, "is_err": is_err,
                     "still_failing": still_failing, "via": via,
                     "stale": stale,
                     "lines": len(lines), "bad": len(hits),
                     "last_bad": (hits[-1][:150] if hits else "")})
    rows.sort(key=lambda r: (-r["bad"], r["age_h"]))
    print("# Native agent log triage (%d logs, last %d days)\n" % (len(rows), DAYS))
    print("STALE = quiet for longer than THAT agent's own schedule allows, read from its plist —")
    print("a weekly agent is not stale at four days. A silent agent looks identical to a healthy")
    print("one from outside, so real staleness is reported as loudly as crashes.\n")
    print("| Log | Last write | Age | Allowed gap | Problem lines | Most recent problem |")
    print("|---|---|---:|---:|---:|---|")
    for r in rows:
        flag = " **STALE**" if r["stale"] else (" (alive: ~/%s)" % r["via"] if r["via"] else "")
        print("| %s%s | %s | %.0fh | %.0fh | %d | %s |"
              % (r["name"], flag, r["mt"].strftime("%m/%d %H:%M"), r["age_h"], r["gap"], r["bad"],
                 (r["last_bad"] or "-").replace("|", "/")))
    dead = [r for r in rows if r["still_failing"] and not r["stale"]]
    fixed = [r for r in rows if r["bad"] and not r["still_failing"] and not r["stale"]]
    stale = [r for r in rows if r["stale"]]
    print("\n**%d STILL FAILING on their most recent run, %d had problems that appear resolved, "
          "%d stale (quiet beyond their own schedule).**" % (len(dead), len(fixed), len(stale)))
    if dead:
        print("\nInvestigate these — the END of their log shows a problem, so the LATEST run failed:")
        for r in dead:
            print("- **%s** (%d problem lines): %s" % (r["name"], r["bad"], r["last_bad"][:120]))
    if fixed:
        print("\nHad problems earlier in the window but their most recent run looks clean — "
              "no action unless it recurs:")
        for r in fixed:
            print("- %s (%d earlier problem lines)" % (r["name"], r["bad"]))
    if skipped:
        print("\nNot judged — retired or one-off logs listed in fleet/log_triage_expectations.json:")
        for n, why in skipped:
            print("- %s: %s" % (n, why))
    # Stable machine-readable line. The doctor used to grep this tool's PROSE, so when the
    # wording changed it parsed 0 and reported "clean" while 8 agents were failing. Prose is for
    # humans; this line is the contract.
    print("\nSUMMARY still_failing=%d resolved=%d stale=%d logs=%d"
          % (len(dead), len(fixed), len(stale), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
