#!/bin/bash
# Native replacement for vp-os-github-nightly-backup — 2026-09-17 (fixed 2026-09-18).
# Same steps, same secret patterns, same guards as the SKILL.md it replaces.
# The scanner lives in bin/secret_scan.py — it was originally inlined here as a heredoc inside a
# command substitution, which bash 3.2 (the Mac's /bin/bash) mis-parses; the agent died with a
# syntax error every night and never backed anything up. Never inline Python inside $( ) again.
AGENT=github-backup; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 60
cd "$HOME/Documents/Claude" || { ledger "vp-os-github-nightly-backup" "Could not open the folder that gets backed up." "no"; exit 1; }
git add -A
if [ -z "$(git status --porcelain)" ]; then vlog "nothing to back up"; exit 0; fi
git diff --cached > /tmp/nightly_secret_scan.txt
SCAN=$("$PY" "$BIN/secret_scan.py" /tmp/nightly_secret_scan.txt); rc=$?
if [ $rc -ne 0 ]; then ledger "vp-os-github-nightly-backup" "Nightly backup stopped: a likely secret is staged and must be redacted by hand — $(echo "$SCAN" | grep -v SECRETS_FOUND | head -3 | tr '\n' ';')" "yes, redact the listed file(s)"; exit 1; fi
N=$(git diff --cached --name-only | wc -l | tr -d ' ')
git commit -q -m "Auto-backup: $(date +%Y-%m-%d) — $N files" || { ledger "vp-os-github-nightly-backup" "git commit failed." "no"; exit 1; }
git fetch -q origin main && git merge-base --is-ancestor origin/main HEAD || { ledger "vp-os-github-nightly-backup" "origin/main has commits this Mac does not — not force-pushing; needs a look." "yes, reconcile the backup repo"; exit 1; }
GIT_TERMINAL_PROMPT=0 git push -q origin main 2>/tmp/vp_push.err || { ledger "vp-os-github-nightly-backup" "git push failed: $(head -c 200 /tmp/vp_push.err | tr '\n' ' ')" "yes, if it is an auth error the GitHub token needs re-caching"; exit 1; }
[ "$(git rev-parse HEAD)" = "$(git ls-remote origin main | cut -f1)" ] && vlog "backed up $N files" || { ledger "vp-os-github-nightly-backup" "push reported success but remote HEAD differs." "no"; exit 1; }
