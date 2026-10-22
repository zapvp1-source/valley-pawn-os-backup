#!/usr/bin/env python3
"""backup_repo_tool.py — narrow host helper for the nightly GitHub backup repo (~/Documents/Claude) (2026-10-22).

WHY: the 10/22 00:15 vp-os-github-nightly-backup stopped on purchasing/runs/ Amazon page dumps. Sessions cannot
reach ~/Documents/Claude/.git or ~/Library from the sandbox, so this is the one allow-listed door. It never
commits, pushes, rewrites history or deletes a working-tree file; github_backup.sh stays the only committer.

    status          read-only: .gitignore rule present? staged run files? any commit EVER touching purchasing/runs?
    ignore-runs     back up .gitignore (outside the repo), add the purchasing/runs/ rule, unstage those files
                    (git rm --cached: index only, files on disk untouched)
    redact-runs     copy every purchasing/runs/**/*.html to ~/Library/Application Support/valleypawn/
                    redacted_backups/purchasing_runs_<stamp>/ then redact the originals in place (bin/vp_redact.py)
    last-commit     read-only: HEAD vs origin/main, last commit's file list, any purchasing/runs path in HEAD's tree
"""
import datetime as dt
import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "Documents", "Claude")
REL_RUNS = "Projects/Valley Pawn OS/purchasing/runs"
RUNS = os.path.join(REPO, REL_RUNS)
RULE = "/" + REL_RUNS + "/"
GITIGNORE = os.path.join(REPO, ".gitignore")
BK = os.path.join(HOME, "Library", "Application Support", "valleypawn", "redacted_backups")
STAMP = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
sys.path.insert(0, os.path.join(REPO, "Projects", "Valley Pawn OS", "bin"))


def git(*a, check=False):
    r = subprocess.run(["/usr/bin/git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    if check and r.returncode:
        print("GIT_FAIL", " ".join(a), r.stderr.strip()[:300])
        sys.exit(2)
    return r.stdout


def has_rule():
    try:
        return any(l.strip() == RULE for l in open(GITIGNORE))
    except OSError:
        return False


def status():
    print("repo:", REPO, "| .gitignore exists:", os.path.exists(GITIGNORE), "| rule present:", has_rule())
    staged = [l for l in git("diff", "--cached", "--name-only").splitlines() if l.startswith(REL_RUNS)]
    print("staged purchasing/runs files:", len(staged))
    print("check-ignore:", git("check-ignore", "-v", REL_RUNS + "/x.html").strip() or "(not ignored)")
    hist = git("log", "--all", "--format=%H %ad %s", "--date=iso", "--", REL_RUNS).strip()
    print("commits EVER touching purchasing/runs:", hist or "NONE")
    hist2 = git("log", "--all", "--format=%h %ad", "--date=short", "--", "Projects/Valley Pawn OS/purchasing").strip()
    print("commits touching purchasing/ (any file):", hist2.replace("\n", " ; ") or "NONE")
    print("total staged:", len(git("diff", "--cached", "--name-only").splitlines()))


def ignore_runs():
    os.makedirs(BK, exist_ok=True)
    if os.path.exists(GITIGNORE):
        shutil.copy2(GITIGNORE, os.path.join(BK, "gitignore.bak-" + STAMP))
        print("backed up .gitignore ->", os.path.join(BK, "gitignore.bak-" + STAMP))
    if not has_rule():
        with open(GITIGNORE, "a") as fh:
            fh.write("\n# 2026-10-22: Amazon checkout page dumps/screenshots from bin/supply_order.py — debug artifacts,\n"
                     "# never backup material (addresses, order totals, page tokens). Run JSON stays local too.\n"
                     + RULE + "\n")
        print("added rule:", RULE)
    else:
        print("rule already present")
    git("rm", "-r", "--cached", "-q", "--ignore-unmatch", REL_RUNS)
    staged = [l for l in git("diff", "--cached", "--name-only").splitlines() if l.startswith(REL_RUNS)]
    tracked = [l for l in git("ls-files", REL_RUNS).splitlines()]
    print("after: staged runs files =", len(staged), "| tracked runs files =", len(tracked))
    print("check-ignore:", git("check-ignore", "-v", REL_RUNS + "/x.html").strip() or "(NOT ignored)")
    print("on-disk run files still present:", sum(len(f) for _, _, f in os.walk(RUNS)))


def redact_runs():
    import vp_redact
    dest = os.path.join(BK, "purchasing_runs_" + STAMP)
    n = changed = 0
    for root, _, files in os.walk(RUNS):
        for f in files:
            if not f.endswith(".html"):
                continue
            src = os.path.join(root, f)
            rel = os.path.relpath(src, RUNS)
            os.makedirs(os.path.join(dest, os.path.dirname(rel)), exist_ok=True)
            shutil.copy2(src, os.path.join(dest, rel))
            n += 1
            if vp_redact.redact_file(src):
                changed += 1
    os.chmod(dest, 0o700) if os.path.isdir(dest) else None
    print("backed up %d html file(s) to %s ; redacted %d in place" % (n, dest, changed))


def last_commit():
    print("HEAD:", git("log", "-1", "--format=%H %ad %s", "--date=iso").strip())
    print("origin/main (remote):", git("ls-remote", "origin", "main").strip()[:60])
    names = git("show", "--name-only", "--format=", "HEAD").splitlines()
    print("last commit file count:", len(names))
    bad = [n for n in names if n.startswith(REL_RUNS)]
    print("purchasing/runs paths in last commit:", len(bad))
    for n in names[:40]:
        print("  ", n)
    print("purchasing/runs paths in HEAD tree:", len([l for l in git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
                                                     if l.startswith(REL_RUNS)]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "ignore-runs": ignore_runs, "redact-runs": redact_runs, "last-commit": last_commit}[cmd]()
