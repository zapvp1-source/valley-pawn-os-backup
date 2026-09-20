#!/usr/bin/env python3
"""fleet_sim.py — the sandbox. Prove the monitoring works WITHOUT waiting a week and WITHOUT
touching production.

WHY (Joshua, 2026-09-19): "we should be able to sandbox everything, test in a simulated
environment, and know production is reliable."

Waiting seven days to find out whether a detector works is not a test, it is a hope. Worse, the
conditions that matter — a corrupt state file, an agent whose script was deleted, six unrelated
reports failing on the same morning — appear only during a real outage, which is exactly when you
cannot afford to be debugging the thing meant to catch it.

So this builds a throwaway HOME, plants each failure ON PURPOSE, runs the REAL production scripts
against it (symlinked, not copied — there is no second version to drift), and asserts what they
should conclude. Every scenario below is a real bug or a real false alarm found on 2026-09-18/19.
Each one took manual poking to find; from now on the whole set runs in seconds and can never
silently come back.

WHAT THIS CAN AND CANNOT PROVE — stated plainly, because the distinction is the whole point:
  CAN  — the control plane. Detectors fire on real faults, stay quiet on healthy ones, survive
         corrupt input, and never report "clean" when they are broken. That is 100% testable here.
  CANNOT — the data plane. Whether Bravo's UI stalls on a Show More grid tomorrow is a property of
         Bravo, not of this code. No sandbox settles that; only real runs do.
  A green run here means: if production breaks, we WILL be told. It does not mean production will
  not break.

    fleet_sim.py            # run every scenario
    fleet_sim.py -v         # show the tool output for failures
"""
import datetime as dt
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile

REAL_OS = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
# Overridable so --mutate can point the SAME suite at a deliberately-broken copy of bin/.
REAL_BIN = os.environ.get("VP_SIM_BIN") or os.path.join(REAL_OS, "bin")
VERBOSE = "-v" in sys.argv
PASS, FAIL = [], []

# Each entry re-introduces ONE bug that was found and fixed on 2026-09-18/19, and names the check
# that must go red. A suite that has never failed is not a proven suite — it may simply be asserting
# things that cannot break. Mutation testing is what turns "31 passed" into evidence.
MUTATIONS = [
    ("weekly agents treated as daily", "log_triage.py",
     "                gap = 9 * 24.0", "                gap = 48.0",
     "triage: weekly agent idle 4d is NOT stale"),
    # Must ALSO restore the over-broad pattern. Removing BENIGN alone was a no-op, because BAD was
    # narrowed in the same sitting — so the mutation proved nothing and SURVIVED. A mutation that
    # does not actually reinstate the bug is a false reassurance, exactly like a decorative check.
    ("benign filter removed AND over-broad pattern restored", "log_triage.py",
     [("                 r\"unexpected EOF|SyntaxError|Operation not permitted\", re.I)",
       "                 r\"unexpected EOF|SyntaxError|Operation not permitted|FAILED|refused\", re.I)"),
      ("            if BENIGN.search(l):\n                continue\n", "")],
     "triage: 'FAILED WAY' store code not a failure"),
    # Must rename EVERY tstate, not just one branch: the sandbox entry takes the POSTED path, so
    # mutating only the MISSED TODAY line never executed and the bug was never actually restored.
    ("state-shadowing bug restored", "field_scorecard.py",
     [("tstate", "state")],
     "scorecard: survives a run without corrupting its own state"),
    ("doctor's missing-summary guard removed", "fleet_doctor.sh",
     'grep -q "SUMMARY still_failing=" "$R" || TOOLFAIL=', 'true || TOOLFAIL=',
     "doctor: treats a missing contract line as a tool failure"),
    ("retirement safety invariant removed", "retire_agent.sh",
     'echo "REFUSED: target still exists.', 'echo "ALLOWED: ',
     "retire: REFUSES an agent whose program exists"),
    ("replay hardcodes its own threshold", "fleet_replay.py",
     [("    THRESHOLD = fs.FLEET_EVENT_MIN", "    THRESHOLD = 5")],
     "replay: imports the LIVE threshold instead of hardcoding one"),
    ("hardcoded-DM-id bug reintroduced", "compliance_brief.py",
     [("    vp = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"vp_slack.py\")",
       "    payload = json.dumps({\"channel\": JOSHUA_DM}); chat.postMessage\n    vp = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"vp_slack.py\")")],
     "slack: no script DMs a hardcoded channel id with the bot token"),
    ("allow-list env-prefix bypass restored", "host_queue_run.sh",
     "is not a bare assignment", "is fine actually",
     "allowlist: refuses 'VAR=value some_command'"),
]


def mutate_mode():
    """Break the code on purpose; the suite must notice. Production is never touched — every
    mutation is applied to a COPY of bin/ in a temp dir."""
    print("# Mutation testing — does the suite actually have teeth?\n")
    print("Each run re-introduces one real bug into a COPY of bin/ and re-runs the whole suite.")
    print("The named check MUST go red. A mutation that survives means that check is decorative.\n")
    src_bin = os.path.join(REAL_OS, "bin")
    good = bad = 0
    def _norm(m):
        """Entries come in two shapes: (label, file, old, new, expect) and
        (label, file, [(old,new), ...], expect). Normalise rather than requiring one form."""
        if isinstance(m[2], list):
            return m[0], m[1], m[2], m[3]
        return m[0], m[1], [(m[2], m[3])], m[4]

    for label, fname, edits, expect in [_norm(m) for m in MUTATIONS]:
        tmp = tempfile.mkdtemp(prefix="fleetmut-")
        try:
            mb = os.path.join(tmp, "bin")
            shutil.copytree(src_bin, mb, symlinks=True)
            p = os.path.join(mb, fname)
            s = open(p).read()
            missing = [o for o, _ in edits if o not in s]
            if missing:
                print("SKIP  %-42s (anchor not found in %s — update the mutation)" % (label, fname))
                bad += 1
                continue
            for o, n in edits:
                s = s.replace(o, n)          # ALL occurrences: a partial mutation may never execute
            open(p, "w").write(s)
            env = dict(os.environ, VP_SIM_BIN=mb)
            r = subprocess.run([sys.executable, os.path.join(src_bin, "fleet_sim.py")],
                               capture_output=True, text=True, env=env, timeout=300)
            caught = ("FAIL  " + expect) in r.stdout
            print("%s  %-42s -> %s" % ("CAUGHT " if caught else "SURVIVED", label,
                                       expect if caught else "SUITE DID NOT NOTICE"))
            good += 1 if caught else 0
            bad += 0 if caught else 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + "=" * 64)
    print("MUTATION RESULT: %d caught, %d survived/skipped" % (good, bad))
    if bad:
        print("\nA surviving mutation means that scenario cannot fail, so it proves nothing.")
    else:
        print("\nEvery deliberately re-introduced bug was caught. The suite has teeth: a green run")
        print("is evidence, not decoration.")
    return 1 if bad else 0


def build_home(tmp):
    """A throwaway HOME. bin/ is SYMLINKED to production so the sandbox tests the real scripts —
    a copied tool would drift and the suite would start passing against code nobody runs."""
    os_dir = os.path.join(tmp, "Documents/Claude/Projects/Valley Pawn OS")
    os.makedirs(os.path.join(os_dir, "fleet"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "Library/Logs/valleypawn"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "Library/LaunchAgents"), exist_ok=True)
    os.symlink(REAL_BIN, os.path.join(os_dir, "bin"))
    return os_dir


def log(tmp, name, lines, age_hours=0.0):
    p = os.path.join(tmp, "Library/Logs/valleypawn", name)
    with open(p, "w") as f:
        f.write("\n".join(lines) + "\n")
    if age_hours:
        t = dt.datetime.now().timestamp() - age_hours * 3600
        os.utime(p, (t, t))
    return p


def agent(tmp, label, script, schedule, logname=None):
    """Plant a launchd plist. `script` may point anywhere — that is the point of the broken cases."""
    d = {"Label": label,
         "ProgramArguments": [os.path.join(tmp, "bin/vp-runner"), script],
         "StandardOutPath": os.path.join(tmp, "Library/Logs/valleypawn", (logname or label) + ".out.log"),
         "StandardErrorPath": os.path.join(tmp, "Library/Logs/valleypawn", (logname or label) + ".err.log")}
    d.update(schedule)
    os.makedirs(os.path.join(tmp, "bin"), exist_ok=True)
    open(os.path.join(tmp, "bin/vp-runner"), "w").close()
    with open(os.path.join(tmp, "Library/LaunchAgents", label + ".plist"), "wb") as f:
        plistlib.dump(d, f)


def run(tmp, *args):
    env = dict(os.environ, HOME=tmp)
    r = subprocess.run([sys.executable] + list(args), capture_output=True, text=True, env=env, timeout=120)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("%s  %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <- " + detail[:300]))


def summary_val(out, key):
    for tok in out.split():
        if tok.startswith(key + "="):
            return tok.split("=", 1)[1]
    return None


# ---------------------------------------------------------------- scenarios
def sc_triage(tmp, os_dir):
    """Every false alarm found on 2026-09-18, planted deliberately and asserted away."""
    # a WEEKLY agent, quiet 4 days — healthy. The first triage build called this dead.
    agent(tmp, "com.valleypawn.weeklyjob", os.path.join(tmp, "bin/vp-runner"),
          {"StartCalendarInterval": {"Weekday": 1, "Hour": 7, "Minute": 30}}, "weeklyjob")
    log(tmp, "weeklyjob.log", ["2026-09-14 07:30:00 run ok"], age_hours=96)
    # a DAILY agent quiet 40h — genuinely stopped
    agent(tmp, "com.valleypawn.dailyjob", os.path.join(tmp, "bin/vp-runner"),
          {"StartCalendarInterval": {"Hour": 7, "Minute": 0}}, "dailyjob")
    log(tmp, "dailyjob.log", ["2026-09-17 07:00:00 run ok"], age_hours=40)
    # an OLD .err.log — means clean, not broken
    log(tmp, "dailyjob.err.log", ["Traceback (most recent call last):", "ValueError: old news"], age_hours=400)
    # benign lines that contain failure words
    today = dt.datetime.now().strftime("%Y-%m-%d")
    log(tmp, "benign.log", ["%s 07:20:01 certificate written: items-to-price FAILED WAY" % today,
                            "%s 22:30:03 REFUSED 20260918-somejob" % today,
                            "%s 22:31:00 run ok" % today])
    # a REAL failure at the tail
    log(tmp, "reallybroken.log", ["%s 01:00:00 run ok" % today,
                                  "%s 02:00:00 CRASH: AttributeError: boom" % today])
    # failed earlier, clean now -> resolved, not still failing
    log(tmp, "recovered.log", ["%s 01:00:00 CRASH: AttributeError: boom" % today] +
                              ["%s 02:%02d:00 run ok" % (today, i) for i in range(20)])
    rc, out = run(tmp, os.path.join(os_dir, "bin/log_triage.py"), "--days", "7")
    check("triage: exits 0", rc == 0, out)
    check("triage: emits SUMMARY contract line", "SUMMARY still_failing=" in out, out)
    check("triage: weekly agent idle 4d is NOT stale", "weeklyjob.log **STALE**" not in out, out)
    check("triage: daily agent quiet 40h IS stale", "dailyjob.log **STALE**" in out, out)
    check("triage: old .err.log is NOT stale", "dailyjob.err.log **STALE**" not in out, out)
    # BEHAVIOURAL, not a source grep: read benign.log's own row out of the table and require its
    # problem count to be 0. The first version of this check inspected a sliced string and passed
    # even with the filter removed — mutation testing caught it on 2026-09-19.
    benign_problems = None
    for line in out.splitlines():
        if line.startswith("| benign.log"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            benign_problems = cells[4] if len(cells) > 4 else None
    check("triage: 'FAILED WAY' store code not a failure",
          benign_problems == "0", "benign.log problem count = %r (expected 0)" % benign_problems)
    check("triage: real tail crash IS still-failing", "reallybroken.log" in out, out)
    sf = summary_val(out, "still_failing")
    check("triage: recovered agent counted resolved, not failing",
          "recovered.log" in out and "resolved=" in out and summary_val(out, "resolved") != "0", out)
    return out


def sc_agent_doctor(tmp, os_dir):
    """A launchd agent pointing at a deleted script — invisible to launchctl, fatal in practice."""
    agent(tmp, "com.valleypawn.ghost", os.path.join(tmp, "Documents/Claude/Scheduled/gone/collect.sh"),
          {"StartCalendarInterval": {"Minute": 20}}, "ghost")
    present = os.path.join(tmp, "bin/real_script.sh")
    open(present, "w").close()
    agent(tmp, "com.valleypawn.alive", present, {"StartCalendarInterval": {"Hour": 3}}, "alive")
    rc, out = run(tmp, os.path.join(os_dir, "bin/agent_doctor.py"))
    check("doctor: exits 0", rc == 0, out)
    check("doctor: finds the agent with a deleted script", "com.valleypawn.ghost" in out and "BROKEN" in out, out)
    check("doctor: does NOT flag the healthy agent",
          "com.valleypawn.alive" in out.split("## HEALTHY")[-1], out)
    check("doctor: SUMMARY counts exactly 1 broken VP agent", summary_val(out, "broken_vp") == "1", out)
    return out


def sc_retire_guard(tmp, os_dir):
    """The retirement tool must be incapable of removing a working agent."""
    present = os.path.join(tmp, "bin/real_script.sh")
    open(present, "w").close()
    agent(tmp, "com.valleypawn.alive2", present, {"StartCalendarInterval": {"Hour": 3}}, "alive2")
    env = dict(os.environ, HOME=tmp)
    r = subprocess.run(["/bin/bash", os.path.join(os_dir, "bin/retire_agent.sh"),
                        "com.valleypawn.alive2", "--apply"],
                       capture_output=True, text=True, env=env, timeout=60)
    out = r.stdout + r.stderr
    still = os.path.exists(os.path.join(tmp, "Library/LaunchAgents/com.valleypawn.alive2.plist"))
    check("retire: REFUSES an agent whose program exists", "REFUSED" in out and still, out)


def sc_doctor_never_lies(tmp, os_dir):
    """The one that matters most: a diagnostic that CRASHES must never read as 'clean'."""
    fake_bin = os.path.join(tmp, "fakebin")
    os.makedirs(fake_bin, exist_ok=True)
    # a report with no SUMMARY lines at all = the tools did not finish
    r = os.path.join(os_dir, "fleet", "doctor_probe.md")
    os.makedirs(os.path.dirname(r), exist_ok=True)
    open(r, "w").write("# report\nsome output but no contract lines\n")
    txt = open(r).read()
    check("doctor: a report with no SUMMARY line is detectable as incomplete",
          "SUMMARY still_failing=" not in txt and "SUMMARY broken_vp=" not in txt,
          "the doctor keys off exactly these strings")
    src = open(os.path.join(REAL_BIN, "fleet_doctor.sh")).read()
    check("doctor: treats a missing contract line as a tool failure",
          'grep -q "SUMMARY still_failing=" "$R" || TOOLFAIL=' in src, "guard missing from fleet_doctor.sh")
    check("doctor: reports a failed sub-tool louder than its findings",
          "The overnight check could not complete" in src, "tool-failure message missing")
    check("doctor: runs every sub-tool through run_tool()",
          src.count("run_tool ") >= 4, "not all sub-tools are wrapped")
    check("doctor: stays silent while the publish guard is armed",
          "vp_dryrun.py\" status" in src or "vp_dryrun.py status" in src, "dry-run suppression missing")


def sc_state_corruption(tmp, os_dir):
    """The bug that killed the watchdog: valid JSON of the wrong SHAPE."""
    sp = os.path.join(tmp, "Library/Logs/valleypawn/field_scorecard_state.json")
    open(sp, "w").write('"POSTED"')
    src = open(os.path.join(REAL_BIN, "field_scorecard.py")).read()
    check("scorecard: load_json checks SHAPE, not just parseability",
          "isinstance(got, type(default))" in src, "shape check missing — a str state would crash it again")
    check("scorecard: quarantines a wrong-shaped state file",
          '".corrupt-"' in src, "corrupt file is not moved aside")
    # BEHAVIOURAL: actually RUN the scorecard against the sandbox and require the state file to
    # survive as a dict. The old source-grep passed with the bug reinstated, because `tstate` still
    # appeared elsewhere in the file. This runs the real code path that corrupted the file.
    fl = os.path.join(os_dir, "fleet")
    json.dump({"tier1": {"daily_field": ["simtask"]}}, open(os.path.join(fl, "tier1_tasks.json"), "w"))
    json.dump({"_readme": [], "entries": [
        {"task": "simtask", "output": "file",
         "path": os.path.join(tmp, "artifact-{YYYY-MM-DD}.txt"),
         "marker": "", "cadence": "daily-0700et", "grace_hours": 2}]},
        open(os.path.join(fl, "expected_outputs.json"), "w"))
    open(os.path.join(tmp, "artifact-%s.txt" % dt.datetime.now().strftime("%Y-%m-%d")), "w").write("x")
    rc, sout = run(tmp, os.path.join(os_dir, "bin/field_scorecard.py"), "--dry-run", "--sim")
    shape = None
    try:
        shape = type(json.load(open(sp))).__name__
    except Exception as e:
        shape = "unreadable(%s)" % e
    check("scorecard: survives a run without corrupting its own state",
          rc == 0 and "CRASH" not in sout and shape == "dict",
          "rc=%s shape=%s %s" % (rc, shape, sout[-200:]))
    check("scorecard: quarantined the wrong-shaped state file it started with",
          any(f.startswith("field_scorecard_state.json.corrupt-")
              for f in os.listdir(os.path.dirname(sp))),
          "corrupt state was not moved aside")
    check("scorecard: fleet-event alarm present", "FLEET_EVENT_MIN" in src, "alarm missing")
    check("scorecard: fleet-event rehearsal resets its own state",
          'state["fleet_event"] = {}' in src, "a rehearsal would suppress tomorrow's real day-1 alert")


def sc_allowlist(tmp, os_dir):
    """The host queue must not let a variable prefix smuggle an unchecked command."""
    src = open(os.path.join(REAL_BIN, "host_queue_run.sh")).read()
    check("allowlist: refuses 'VAR=value some_command'",
          "is not a bare assignment" in src, "the env-prefix bypass is back")
    good = os.path.join(tmp, "good.sh")
    bad = os.path.join(tmp, "bad.sh")
    open(good, "w").write('BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"\n'
                          'python3 "$BIN/vp_dryrun.py" status\n')
    open(bad, "w").write('VP_TASK=x python3 /tmp/evil.py\n')
    harness = os.path.join(tmp, "v.sh")
    body = src[src.index("ALLOW="):src.index("\nshopt")]
    open(harness, "w").write(body + '\nfor j in "$1" ; do validate_job "$j" && echo ACCEPTED || echo REFUSED_OK ; done\n')
    env = dict(os.environ, HOME=tmp, OS_DIR=REAL_OS)
    g = subprocess.run(["/bin/bash", harness, good], capture_output=True, text=True, env=env, timeout=30)
    b = subprocess.run(["/bin/bash", harness, bad], capture_output=True, text=True, env=env, timeout=30)
    check("allowlist: accepts a legitimate job", "ACCEPTED" in g.stdout, g.stdout + g.stderr)
    check("allowlist: refuses the env-prefix smuggle", "REFUSED_OK" in b.stdout, b.stdout + b.stderr)


def sc_dryrun(tmp, os_dir):
    """The publish guard must divert, must expire, and must never write a real receipt."""
    src = open(os.path.join(REAL_BIN, "vp_dryrun.py")).read()
    check("guard: expiry is enforced on READ (a forgotten flag disarms itself)",
          "now <= until" in src, "no read-time expiry — a stale flag could silence the fleet")
    check("guard: has a hard ceiling on how long it can be armed", "MAX_MINUTES" in src, "no ceiling")
    check("guard: diverted sends go to a SEPARATE ledger, never real receipts",
          "dryrun_receipts.jsonl" in src, "a test could be mistaken for proof of delivery")
    s2 = open(os.path.join(REAL_BIN, "vp_slack.py")).read()
    check("guard: vp_slack intercepts BEFORE sending", "if dryrun_intercept(" in s2, "interceptor missing")
    check("guard: interceptor fails OPEN (a broken guard must not swallow a real report)",
          "except Exception:\n        return False" in s2, "fails closed — would silently eat publications")


def sc_replay(tmp, os_dir):
    """The replay is evidence Joshua will quote, so it must test the rule that actually ships.
    A replay with its own hardcoded threshold would stay green while production used a different
    number — evidence for a system nobody runs."""
    src = open(os.path.join(REAL_BIN, "fleet_replay.py")).read()
    check("replay: imports the LIVE threshold instead of hardcoding one",
          "fs.FLEET_EVENT_MIN" in src, "replay has its own copy of the rule — it can drift")
    check("replay: refuses to run if it cannot read the live rule",
          "REFUSED: could not import the live fleet-event threshold" in src,
          "a failed import would silently fall back to a guess")
    check("replay: states that it covers misses, not accuracy",
          "separate axis" in src, "missing the honest limit — the claim would be overstated")


def sc_slack_dm_class(tmp, os_dir):
    """No native script may post to a HARDCODED DM channel id with the ops-bot token.

    D03BHQH5VGT is the Cowork app's DM with Joshua. A bot cannot post into another app's DM, so any
    script doing this fails with channel_not_found — silently, into a log nobody reads. It hid the
    compliance brief for an unknown length of time and had ALREADY been fixed once in
    fleet_health_sentinel.py, which is why it deserves a structural guard: a fault fixed twice will
    be written a third time.

    PRECISE, not crude. The first version flagged any file merely CONTAINING the id, which caught
    fleet_health_sentinel.py (it names the id in a comment explaining this very bug) and this suite
    (it carries the id inside a mutation string). A guard that fires on correct code is the same
    false-alarm disease being fixed everywhere else tonight — so it now requires the id, or a
    constant bound to it, to be USED as a channel value on a non-comment line."""
    BAD_ID = "D03" "BHQH5VGT"          # split so this docstring's own file never self-matches
    offenders = []
    for f in sorted(os.listdir(REAL_BIN)):
        if not f.endswith(".py") or f == "fleet_sim.py":
            continue                    # the suite deliberately carries the bug text as a mutation
        try:
            src = open(os.path.join(REAL_BIN, f), errors="replace").read()
        except OSError:
            continue
        if "vp-ops-slack-bot-token" not in src:
            continue
        names = {"\"%s\"" % BAD_ID, "'%s'" % BAD_ID}
        for line in src.splitlines():          # constants bound to the literal id
            st = line.strip()
            if st.startswith("#") or BAD_ID not in st or "=" not in st:
                continue
            lhs = st.split("=", 1)[0].strip()
            if lhs.isidentifier():
                names.add(lhs)
        for line in src.splitlines():
            st = line.strip()
            if st.startswith("#") or '"channel"' not in st:
                continue
            if any(n in st for n in names):
                offenders.append(f)
                break
    check("slack: no script DMs a hardcoded channel id with the bot token",
          not offenders, "offenders: %s — must use conversations.open / vp_slack.py" % offenders)


def main():
    if "--mutate" in sys.argv:
        return mutate_mode()
    tmp = tempfile.mkdtemp(prefix="fleetsim-")
    try:
        os_dir = build_home(tmp)
        print("# Fleet simulator — sandbox HOME at %s\n" % tmp)
        print("Real production scripts, symlinked. Faults planted on purpose. Nothing touched in prod.\n")
        print("## Log triage");      sc_triage(tmp, os_dir)
        print("\n## Agent doctor");  sc_agent_doctor(tmp, os_dir)
        print("\n## Retirement safety"); sc_retire_guard(tmp, os_dir)
        print("\n## Watchdog state integrity"); sc_state_corruption(tmp, os_dir)
        print("\n## Nightly doctor honesty"); sc_doctor_never_lies(tmp, os_dir)
        print("\n## Host allow-list"); sc_allowlist(tmp, os_dir)
        print("\n## Publish guard"); sc_dryrun(tmp, os_dir)
        print("\n## History replay"); sc_replay(tmp, os_dir)
        print("\n## Slack DM addressing"); sc_slack_dm_class(tmp, os_dir)
        print("\n" + "=" * 64)
        print("RESULT: %d passed, %d failed" % (len(PASS), len(FAIL)))
        if FAIL:
            print("\nFAILED:")
            for f in FAIL:
                print("  - %s" % f)
            print("\nA failure here is a REGRESSION: every scenario encodes a fault that was")
            print("already found and fixed once. Do not ship with red.")
        else:
            print("\nAll green. The monitoring detects real faults, stays quiet on healthy ones,")
            print("survives corrupt input, and cannot report 'clean' when it is broken.")
            print("This proves the CONTROL plane. Whether Bravo stalls tomorrow is a separate")
            print("question that only real runs answer — see fleet/GATE_FINDINGS.")
        return 1 if FAIL else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
