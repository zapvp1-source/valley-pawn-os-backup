---
name: vp-os-github-nightly-backup
description: Nightly auto-commit/push of Valley Pawn OS .md files to the private GitHub backup repo
---

You are running the nightly GitHub backup for Valley Pawn OS. This is a fresh session with no memory of prior runs — everything you need is below. Do this entirely headlessly via the "Control your Mac" osascript connector (`do shell script "..."`) — do NOT use computer-use / GUI automation for any part of this, and do NOT prompt anyone interactively.

CONTEXT
- Local repo: ~/Documents/Claude (git repo, branch `main`)
- Remote: https://github.com/zapvp1-source/valley-pawn-os-backup.git
- Auth: repo-local `credential.helper=osxkeychain` is already configured and a valid GitHub PAT is already cached in macOS Keychain for this repo. You should NOT need any interactive auth — if a push fails with an authentication error, that means the cached credential expired or was revoked; do not try to re-auth yourself, just alert (see FAILURE HANDLING below).
- `.gitignore` in that repo is a whitelist: everything is ignored by default except `.md` / `.md.bak*` files, with hard excludes for `Projects/Health Optimization/`, `Projects/Quickbooks Set UP/`, `tools/`, and anything matching `*.pem`, `*.key`, `*.env`, `.env*`, `*credential*`, `brevo_api_key`, `*.p12`, `*.pfx`. Trust this file as-is — do not edit it unless a step below tells you to.

STEPS

1. Run: `cd ~/Documents/Claude && git add -A && git status --porcelain`
   - If the output is empty, there is nothing to back up tonight. Stop here. Do not commit, push, or message anyone.

2. Before committing, scan staged content for accidentally-hardcoded secrets (this bit us once already — a prior run had live eBay API credentials hardcoded in a SKILL.md, which GitHub's push protection correctly blocked). Run:
   `cd ~/Documents/Claude && git diff --cached | grep -inE "APP_ID=|DEV_ID=|CERT_ID=|CLIENT_SECRET|client_secret=|PRD-[A-Za-z0-9]|sk_live|SG\.[A-Za-z0-9_\-]{10,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9\-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"`
   - If this finds ANY matches: do NOT commit or push. Instead go straight to FAILURE HANDLING below with the specific file paths/line numbers it flagged (from `git diff --cached --name-only` cross-referenced with the grep hits), explaining a likely secret was about to be committed and needs manual redaction (see how the eBay incident was fixed: the real credential value was replaced with a pointer to the untracked file that actually holds it, e.g. "see ~/ebay_weekly_rankings.py", never the literal value).

3. If the scan is clean, commit: `cd ~/Documents/Claude && git commit -m "Auto-backup: $(date +%Y-%m-%d) — $(git diff --cached --name-only HEAD~0 2>/dev/null | wc -l | tr -d ' ') files"` — adjust the file-count subcommand if needed so the message is just something reasonable like "Auto-backup: 2026-07-09 — 4 files changed"; exact wording isn't critical.

4. Fetch and confirm we can fast-forward before pushing (protects against any unexpected divergence): `git fetch origin main && git merge-base --is-ancestor origin/main HEAD` — if this fails (non-zero exit), do NOT force-push. Go to FAILURE HANDLING — this means origin/main has commits this local repo doesn't, which shouldn't normally happen for a single-writer backup repo and needs a human look.

5. Push: `GIT_TERMINAL_PROMPT=0 git push origin main`. Confirm success by checking exit code 0 AND that `git rev-parse HEAD` equals `git ls-remote origin main | cut -f1` afterward.

6. If steps 3-5 all succeeded: done, exit silently. No Slack message, no notification — this should be invisible when it works.

FAILURE HANDLING (the only case where you make noise)
If ANY step fails — secret detected, auth/push rejected, merge conflict, network error, anything — send a Slack DM to Joshua (user ID `U03BB52MDSA`) with: what step failed, the exact error text, and (if it was a secret-scan hit) the file path(s) and matched pattern so he knows exactly what to redact. Keep it short and factual. Do not attempt to fix a secret leak yourself in this automated run — flag it and stop, the redaction should be a deliberate human-reviewed action (as it was the first time this happened).