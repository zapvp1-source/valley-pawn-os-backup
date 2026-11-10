#!/usr/bin/env python3
"""continuity_selftest.py (2026-11-09) — weekly proof that the "IF CLAUDE GOES DOWN" fallbacks still work.

Checks (no Claude involved in any of them):
  1. local_engine  — Ollama answers on this Mac and the configured model is installed (fleet/ai_fallback.json)
  2. local_answer  — the local model actually writes a reply through bin/vp_ai.py's local path
  3. github        — the offsite GitHub backup of ~/Documents/Claude is current (HEAD == origin/main, < 48 h old)
  4. task_export   — the nightly export of the Claude cloud scheduled tasks is < 72 h old
                     (Business Continuity/cloud_tasks_export/latest.json, written by the cloud task
                     "Cloud task export (nightly)")
Writes fleet/state/continuity_selftest.json. A failing check writes ONE FAILURE_LEDGER row (fleet-guardian
handles it). Nothing to Slack, ever. Run: continuity_selftest.py [--quiet-ledger]
"""
import datetime, json, os, subprocess, sys, time, urllib.request

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
sys.path.insert(0, os.path.join(OS_DIR, "bin"))
import vp_ai  # noqa: E402

STATE = os.path.join(OS_DIR, "fleet/state/continuity_selftest.json")
LEDGER = os.path.join(OS_DIR, "fleet/FAILURE_LEDGER.md")
EXPORT = os.path.join(HOME, "Documents/Claude/Projects/Business Continuity/cloud_tasks_export/latest.json")
REPO = os.path.join(HOME, "Documents/Claude")


def check_local_engine(cfg):
    with urllib.request.urlopen(cfg["local_url"].rstrip("/") + "/api/tags", timeout=20) as r:
        names = [m.get("name") for m in json.load(r).get("models", [])]
    ok = cfg["local_model"] in names
    return ok, "models=%s" % ",".join(n for n in names if n)


def check_local_answer(cfg):
    t0 = time.time()
    out = vp_ai._ask_local("Reply with exactly the word OK.", "", 10, cfg).strip()
    return ("OK" in out.upper()), "answer=%r secs=%d" % (out[:30], time.time() - t0)


def git(*a):
    return subprocess.run(["/usr/bin/git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=120).stdout.strip()


def check_github(_cfg):
    head = git("rev-parse", "HEAD")
    remote = (git("ls-remote", "origin", "main").split() or [""])[0]
    ts = int(git("log", "-1", "--format=%ct") or 0)
    age_h = (time.time() - ts) / 3600 if ts else 9999
    return (bool(head) and head == remote and age_h < 48), "head=%s remote=%s last_commit_age_h=%.1f" % (head[:7], remote[:7], age_h)


def check_task_export(_cfg):
    if not os.path.exists(EXPORT):
        return False, "missing %s" % EXPORT
    age_h = (time.time() - os.path.getmtime(EXPORT)) / 3600
    try:
        n = len(json.load(open(EXPORT)).get("tasks", []))
    except Exception as e:
        return False, "unreadable: %s" % e
    return (age_h < 72 and n > 0), "age_h=%.1f tasks=%d" % (age_h, n)


CHECKS = [("local_engine", check_local_engine), ("local_answer", check_local_answer),
          ("github", check_github), ("task_export", check_task_export)]
PLAIN = {"local_engine": "The free local AI engine on the Mac (the Claude backup) is not running or its model is missing.",
         "local_answer": "The free local AI engine on the Mac (the Claude backup) did not answer a test question.",
         "github": "The offsite GitHub backup of the Claude folder is not current.",
         "task_export": "The nightly copy of the Claude cloud scheduled tasks is missing or more than 3 days old."}


def main():
    cfg = vp_ai._cfg()
    res, bad = {}, []
    for name, fn in CHECKS:
        try:
            ok, detail = fn(cfg)
        except Exception as e:
            ok, detail = False, "%s %s" % (type(e).__name__, str(e)[:200])
        res[name] = {"ok": ok, "detail": detail}
        print(("PASS " if ok else "FAIL ") + name + " " + detail)
        if not ok:
            bad.append(name)
    out = {"checked": datetime.datetime.now().isoformat(timespec="seconds"), "all_ok": not bad, "checks": res}
    tmp = STATE + ".tmp"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE)
    if bad and "--quiet-ledger" not in sys.argv:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET")
        with open(LEDGER, "a") as f:
            for b in bad:
                f.write("| %s (native) | continuity-selftest | %s (%s) | NEEDS_HUMAN: no | OPEN |\n"
                        % (now, PLAIN[b], res[b]["detail"][:160].replace("|", "/")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
