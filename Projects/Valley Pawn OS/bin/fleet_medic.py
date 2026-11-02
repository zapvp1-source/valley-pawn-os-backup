#!/usr/bin/env python3
"""fleet_medic.py — Layer-1 self-healing for the native Valley Pawn agent fleet (2026-11-01).

Runs every 5 minutes (launchd com.valleypawn.fleet-medic via ~/bin/vp-runner). Pure stdlib, no Claude, no
network except 127.0.0.1. Reads the Fleet Deck's live picture (http://127.0.0.1:8790/api/status; falls back to
building it in-process) and applies a FIXED, conservative playbook. Everything it does is logged to
fleet/medic/actions.jsonl (shown on the Fleet Deck tape) and ~/Library/Logs/valleypawn/fleet-medic.log.

WHERE IT SITS (do not duplicate the other layers):
  Layer 1  fleet-medic (this)   minutes   mechanical infra repair of the agents themselves
  Layer 2  catchup (native)     15 min    re-triggers critical scheduled jobs missed while the Mac was off
  Layer 3  fleet-guardian       2x/day    Claude: works FAILURE_LEDGER, reruns rerun-safe jobs, fixes forward
  Human    Life OS/HUMAN_QUEUE  1x/day    only what only Joshua can do (permissions, passwords, MFA)

PLAYBOOK
  R1  installed but not loaded      -> launchctl bootstrap it (skips one-shots/ignored; a calendar job with
                                       RunAtLoad is routed to the ledger instead so a report can't fire early)
  R2  always-on agent not running,
      or interval agent last exit!=0 -> launchctl kickstart -k   (30-min cooldown, max 3 per 24 h per agent)
  R3  scheduled job last exit != 0  -> make sure FAILURE_LEDGER has an OPEN row so fleet-guardian works it
                                       (never reruns a scheduled job itself: that could double-post a report)
  R3b scheduled job missed its last slot -> same routing as R3 ("[medic-missed]"), once per day at most
  R4  same scheduled job failed on 3 consecutive runs -> one "repeat failure, needs a code fix" ledger row
  R5  exit 126 (macOS permission)   -> one HUMAN_QUEUE line; no retries (only Joshua can grant access)
  R6  Fleet Deck itself down        -> kickstart com.valleypawn.fleet-deck (and its window)
  R7  agent out of retries          -> one ledger row "auto-restart did not hold", then hands off

SAFETY
  * never runs, reruns or edits a report job, never touches Bravo/Parallels, never posts to Slack or DMs,
    never deletes anything, never edits a script or plist.
  * brake: more than BRAKE_ACTIONS repair actions in one pass = something systemic -> stop acting, one ledger row.
  * observe-only switch: touch fleet/state/fleet_medic_off  (logs what it WOULD do, changes nothing).
  * --dry-run prints the plan and changes nothing.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
LIFE_DIR = os.path.join(HOME, "Documents/Claude/Projects/Life OS")
FLEET = os.path.join(OS_DIR, "fleet")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(FLEET, "FAILURE_LEDGER.md")
HUMAN_Q = os.path.join(LIFE_DIR, "HUMAN_QUEUE.md")
POLICY = os.path.join(FLEET, "medic_policy.json")
STATE = os.path.join(FLEET, "state/fleet_medic.json")
OFF = os.path.join(FLEET, "state/fleet_medic_off")
ACTIONS = os.path.join(FLEET, "medic/actions.jsonl")
LOG = os.path.join(HOME, "Library/Logs/valleypawn/fleet-medic.log")
LA_DIR = os.path.join(HOME, "Library/LaunchAgents")
DECK = "http://127.0.0.1:8790"
UID = os.getuid()

DRY = "--dry-run" in sys.argv
NOW = dt.datetime.now()

DEFAULT_POLICY = {
    "_doc": "fleet-medic policy. ignore = labels never touched (one-shots, retired, intentionally unloaded). "
            "no_kickstart = interval/always-on agents medic must not restart. Edit freely; medic re-reads every pass.",
    "ignore": ["com.valleypawn.taskperms-oneshot", "com.valleypawn.fleet-medic"],
    "ignore_substrings": ["oneshot", "-catchup-2026"],
    "no_kickstart": [],
    "cooldown_min": 30,
    "max_restarts_24h": 3,
    "brake_actions": 8,
    "repeat_failure_runs": 3,
}


# ------------------------------------------------------------------ io
def log(msg):
    line = NOW.strftime("%Y-%m-%d %H:%M:%S ") + msg
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_json(p, default):
    try:
        v = json.load(open(p))
        return v if isinstance(v, type(default)) else default
    except Exception:
        return default


def save_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(tmp, p)


def record(kind, label, what, ok=True, observe=False):
    row = {"ts": NOW.isoformat(timespec="seconds"), "kind": kind, "agent": label.replace("com.valleypawn.", ""),
           "what": what, "ok": ok, "observe_only": observe or DRY}
    log(("[observe] " if row["observe_only"] else "") + "%s %s — %s%s" % (kind, row["agent"], what, "" if ok else " (FAILED)"))
    if DRY:
        return
    try:
        os.makedirs(os.path.dirname(ACTIONS), exist_ok=True)
        with open(ACTIONS, "a") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def ledger_rows():
    try:
        return open(LEDGER, errors="replace").read().splitlines()
    except Exception:
        return []


def _norm(name):
    n = name.replace("com.valleypawn.", "").lower()
    for pre in ("monthly-", "weekly-", "daily-", "vp-", "nightly-"):
        n = n[len(pre):] if n.startswith(pre) else n
    return n


def ledger_has_open(agent, hours=26, marker=None):
    """True if an OPEN ledger row in the last `hours` mentions this agent (fuzzy) or carries `marker`."""
    a = _norm(agent)
    cutoff = NOW - dt.timedelta(hours=hours)
    for l in ledger_rows():
        if not l.startswith("|") or "| OPEN |" not in l:
            continue
        if marker and marker in l:
            return True
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) < 2:
            continue
        m = re.match(r"(\d{4}-\d\d-\d\d) (\d\d:\d\d)", c[0])
        if m:
            try:
                if dt.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M") < cutoff:
                    continue
            except ValueError:
                pass
        t = _norm(c[1])
        if a and t and (a in t or t in a):
            return True
    return False


def ledger_handled_since(agent, since_iso):
    """True if ANY ledger row (any status: OPEN, RECOVERED, UNRECOVERED...) about this agent was written at or after
    the failed run. fleet-guardian closes rows in place (RECOVERED/UNRECOVERED); re-opening them just makes it
    re-triage work it already did (seen 2026-11-01)."""
    a = _norm(agent)
    try:
        since = dt.datetime.fromisoformat(since_iso) - dt.timedelta(minutes=10)
    except Exception:
        since = NOW - dt.timedelta(hours=26)
    for l in ledger_rows():
        if not l.startswith("|"):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) < 2:
            continue
        m = re.match(r"(\d{4}-\d\d-\d\d) (\d\d:\d\d)", c[0])
        if not m:
            continue
        try:
            when = dt.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if when < since:
            continue
        t = _norm(c[1])
        if a and t and (a in t or t in a):
            return True
    return False


def ledger_add(agent, sentence, needs_human="no", marker=""):
    row = "| %s ET (native) | %s | %s%s | NEEDS_HUMAN: %s | OPEN |" % (
        NOW.strftime("%Y-%m-%d %H:%M"), agent, sentence.replace("|", "/"), (" " + marker) if marker else "", needs_human)
    if DRY or os.path.exists(OFF):
        log("[observe] would add ledger row: " + row)
        return
    with open(LEDGER, "a") as f:
        f.write(row + "\n")


def human_add(key, sentence):
    try:
        if key in open(HUMAN_Q, errors="replace").read():
            return False
    except Exception:
        pass
    row = "| %s | 1 — Valley Pawn (Mac Studio) | %s | OPEN | fleet-medic [%s] |" % (NOW.strftime("%Y-%m-%d"), sentence, key)
    if DRY or os.path.exists(OFF):
        log("[observe] would add HUMAN_QUEUE row: " + row)
        return True
    with open(HUMAN_Q, "a") as f:
        f.write(row + "\n")
    return True


# ------------------------------------------------------------------ launchd
def lc(*args):
    if DRY or os.path.exists(OFF):
        return True, "observe-only"
    r = subprocess.run(["launchctl"] + list(args), capture_output=True, text=True, timeout=30)
    return r.returncode == 0, (r.stdout + r.stderr).strip()[:200]


def kickstart(label):
    return lc("kickstart", "-k", "gui/%d/%s" % (UID, label))


def bootstrap(label):
    p = os.path.join(LA_DIR, label + ".plist")
    if not os.path.isfile(p):
        return False, "plist missing"
    return lc("bootstrap", "gui/%d" % UID, p)


# ------------------------------------------------------------------ snapshot
def get_snapshot():
    try:
        with urllib.request.urlopen(DECK + "/api/status", timeout=10) as r:
            d = json.loads(r.read().decode())
        if d.get("agents"):
            return d, True
    except Exception:
        pass
    sys.path.insert(0, BIN)
    import fleet_deck  # same bin/ folder; builds the identical picture in-process
    return fleet_deck.build_snapshot(), False


def last_log_line(agent):
    for lg in agent.get("logs") or []:
        try:
            with open(lg, "rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - 4000))
                lines = [x for x in f.read().decode("utf-8", "replace").splitlines() if x.strip()]
            if lines:
                return re.sub(r"\s+", " ", lines[-1]).strip()[:160]
        except Exception:
            continue
    return ""


# ------------------------------------------------------------------ main pass
def main():
    pol = dict(DEFAULT_POLICY)
    if not os.path.exists(POLICY) and not DRY:
        save_json(POLICY, DEFAULT_POLICY)
    pol.update(load_json(POLICY, {}))
    st = load_json(STATE, {})
    restarts = st.setdefault("restarts", {})       # label -> [iso, ...]
    fails = st.setdefault("fails", {})             # label -> {"last_seen_activity": iso, "streak": n}
    flags = st.setdefault("flags", {})             # one-time keys already written
    observe = os.path.exists(OFF)

    snap, from_deck = get_snapshot()
    agents = snap.get("agents") or []
    actions = 0
    braked = False
    brake = int(pol.get("brake_actions", 8))

    def ignored(lbl):
        return lbl in pol.get("ignore", []) or any(s in lbl for s in pol.get("ignore_substrings", []))

    def can_restart(lbl):
        hist = [t for t in restarts.get(lbl, []) if dt.datetime.fromisoformat(t) > NOW - dt.timedelta(hours=24)]
        restarts[lbl] = hist
        if hist and dt.datetime.fromisoformat(hist[-1]) > NOW - dt.timedelta(minutes=int(pol.get("cooldown_min", 30))):
            return False, "cooldown"
        if len(hist) >= int(pol.get("max_restarts_24h", 3)):
            return False, "out_of_retries"
        return True, ""

    # R6 — the deck itself
    if not from_deck:
        ok, msg = can_restart("com.valleypawn.fleet-deck")
        if ok:
            good, out = kickstart("com.valleypawn.fleet-deck")
            restarts.setdefault("com.valleypawn.fleet-deck", []).append(NOW.isoformat())
            record("restart", "com.valleypawn.fleet-deck", "dashboard was not answering — restarted it", good, observe)
            actions += 1

    for a in agents:
        lbl, status = a["label"], a["status"]
        # R3b — scheduled job that MISSED its last slot (no run, no evidence): route once, never rerun
        if status == "stale" and a.get("calendar") and not ignored(lbl):
            act = a.get("last_activity") or ""
            key = "missed-%s-%s" % (lbl, NOW.strftime("%Y-%m-%d"))
            if key not in flags and not ledger_handled_since(a["name"], act or (NOW - dt.timedelta(days=2)).isoformat()):
                ledger_add(a["name"], "Did not run on schedule: %s. Check the agent's own log on the Mac and why "
                                      "launchd did not start it or it exited silently." % a.get("why", ""), marker="[medic-missed]")
                record("route", lbl, "missed its scheduled run — logged for fleet-guardian", True, observe)
                flags[key] = NOW.isoformat()
            continue
        if ignored(lbl) or status in ("ok", "running", "dormant", "disabled", "quiet"):
            if status in ("ok", "running") and lbl in fails:
                fails.pop(lbl, None)  # recovered: reset the streak
            continue
        if actions >= brake:
            braked = True   # at least one more agent still needed attention
            break
        exit_code = str(a.get("last_exit") or "")
        is_daemon = a.get("always_on") or (a.get("interval") and not a.get("calendar"))

        # R5 — macOS permission problem: only a person can fix it
        if exit_code == "126":
            key = "tcc-" + a["name"]
            if key not in flags:
                if human_add(key, "Mac permission: background job '%s' is blocked by macOS (exit 126). "
                                  "Open System Settings → Privacy & Security → Full Disk Access and make sure "
                                  "'vp-runner' is listed and switched on." % a["name"]):
                    record("escalate", lbl, "blocked by a macOS permission — added to the human queue", True, observe)
                flags[key] = NOW.isoformat()
            continue

        # R1 — installed but not loaded
        if status == "notloaded":
            if a.get("calendar") and a.get("runatload"):
                if not ledger_has_open(a["name"], hours=72):
                    ledger_add(a["name"], "Agent is installed but not loaded; fleet-medic did not load it because it "
                                          "would run a report immediately (RunAtLoad). Load it at a quiet time.")
                    record("route", lbl, "not loaded; left for guardian (would fire a report on load)", True, observe)
                continue
            ok, why = can_restart(lbl)
            if not ok:
                continue
            good, out = bootstrap(lbl)
            restarts.setdefault(lbl, []).append(NOW.isoformat())
            record("reload", lbl, "was installed but not loaded — loaded it back into launchd" + ("" if good else ": " + out), good, observe)
            actions += 1
            continue

        # R2 — always-on / interval daemons
        if status == "error" and is_daemon:
            if lbl in pol.get("no_kickstart", []):
                continue
            ok, why = can_restart(lbl)
            if not ok:
                if why == "out_of_retries" and ("giveup-" + lbl + NOW.strftime("%Y%m%d")) not in flags:
                    if not ledger_has_open(a["name"]):
                        ledger_add(a["name"], "Kept failing after %d automatic restarts in 24 h (%s). Last log: %s" % (
                            int(pol.get("max_restarts_24h", 3)), a.get("why", ""), last_log_line(a) or "(none)"),
                            marker="[medic-giveup]")
                    record("handoff", lbl, "restarts did not hold — handed to fleet-guardian", True, observe)
                    flags["giveup-" + lbl + NOW.strftime("%Y%m%d")] = NOW.isoformat()
                continue
            good, out = kickstart(lbl)
            restarts.setdefault(lbl, []).append(NOW.isoformat())
            record("restart", lbl, "%s — restarted it" % (a.get("why") or "not healthy") + ("" if good else ": " + out), good, observe)
            actions += 1
            continue

        # R3 / R4 — scheduled job whose last run failed: route, never rerun
        if status == "error" and a.get("calendar"):
            act = a.get("last_activity") or ""
            f = fails.setdefault(lbl, {"last_seen_activity": "", "streak": 0})
            if act and act != f["last_seen_activity"]:
                f["streak"] = int(f.get("streak", 0)) + 1
                f["last_seen_activity"] = act
            key = "route-%s-%s" % (lbl, act[:10])
            if key not in flags:
                if not ledger_handled_since(a["name"], act):
                    ledger_add(a["name"], "Last scheduled run ended with an error (exit %s). Last log: %s" % (
                        exit_code, last_log_line(a) or "(none)"), marker="[medic]")
                    record("route", lbl, "last run failed (exit %s) — logged for fleet-guardian to rerun/fix" % exit_code, True, observe)
                flags[key] = NOW.isoformat()
            n = int(pol.get("repeat_failure_runs", 3))
            rkey = "repeat-%s-%s" % (lbl, NOW.strftime("%Y-%W"))
            if f["streak"] >= n and rkey not in flags:
                ledger_add(a["name"], "REPEAT FAILURE: failed on %d runs in a row — needs a code fix, not a rerun. "
                                      "Logs: %s" % (f["streak"], ", ".join(os.path.basename(x) for x in a.get("logs") or [])),
                           marker="[medic-repeat]")
                record("escalate", lbl, "failed %d runs in a row — flagged for a code fix" % f["streak"], True, observe)
                flags[rkey] = NOW.isoformat()
            continue

    if braked and "brake-" + NOW.strftime("%Y%m%d%H") not in flags:
        ledger_add("fleet-medic", "Safety brake: more than %d agents needed repair in one pass — something system-wide "
                                  "is wrong (Mac just restarted, permissions, disk). Stopped after %d repairs." % (brake, actions))
        record("brake", "com.valleypawn.fleet-medic", "too many repairs at once — paused for this pass", True, observe)
        flags["brake-" + NOW.strftime("%Y%m%d%H")] = NOW.isoformat()

    # prune one-time flags older than 14 days
    cutoff = (NOW - dt.timedelta(days=14)).isoformat()
    st["flags"] = {k: v for k, v in flags.items() if v >= cutoff}
    if observe:
        # observe-only must not remember "already handled": reload the persisted state and only stamp the run,
        # so the first live pass after the switch is flipped still does everything.
        st = load_json(STATE, {})
    st["last_run"] = NOW.isoformat(timespec="seconds")
    st["last_actions"] = actions
    st["observe_only"] = observe
    st["source"] = "deck" if from_deck else "in-process"
    if not DRY:
        save_json(STATE, st)
    log("pass done — %d agents seen, %d repair actions%s" % (len(agents), actions, " (observe-only)" if observe else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        log("CRASH: %s | %s" % (e, traceback.format_exc().replace("\n", " | ")))
        sys.exit(1)
