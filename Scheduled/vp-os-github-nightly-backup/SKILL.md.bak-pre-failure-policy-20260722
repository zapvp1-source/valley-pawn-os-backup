---
name: vp-os-github-nightly-backup
description: Nightly auto-commit/push of Valley Pawn OS .md files to the private GitHub backup repo
---

You are running the nightly GitHub backup for Valley Pawn OS. This is a fresh session with no memory of prior runs — everything you need is below. Do this entirely headlessly via the "Control your Mac" osascript connector (`do shell script "..."`) — do NOT use computer-use / GUI automation for any part of this, and do NOT prompt anyone interactively.

CONTEXT
- Local repo: ~/Documents/Claude (git repo, branch `main`)
- Remote: https://github.com/zapvp1-source/valley-pawn-os-backup.git
- Auth: repo-local `credential.helper=osxkeychain` is already configured and a valid GitHub PAT is already cached in macOS Keychain for this repo. You should NOT need any interactive auth — if a push fails with an authentication error, that means the cached credential expired or was revoked; do not try to re-auth yourself, just alert (see FAILURE HANDLING below).
- `.gitignore` in that repo is a whitelist covering both documentation and hand-written source code: `.md`/`.md.bak*` plus `.py .js .jsx .ts .tsx .mjs .cjs .mts .cts .html .css .ahk .sh .ps1 .bat .cmd`. It hard-excludes vendored tooling (`tools/`), generated build output (`.wrangler/`, `dist/`, `build/`, `node_modules/`, `__pycache__/`, `.next/`, `.cache/`), generated dashboard snapshot history (`Artifacts/`, `Projects/Business Dashboard Website/site/artifacts/`), personal/financial docs (`Projects/Health Optimization/`, `Projects/Quickbooks Set UP/`), a specific list of 19 eBay scripts still pending a credential refactor (under `Projects/eBay/`, e.g. `ebay_listing_audit.py`, `ebay_markdown_engine.py`, etc. — see the `.gitignore` file itself for the full list), and credential-pattern filenames (`*token*`, `*secret*`, `*password*`, `*credential*`, `.env`, `.pem`, `.key`, `.p12`, `.pfx`, `.cloudflare/`). Trust this file as-is — do not edit it unless a step below tells you to, and if you ever fix one of the 19 excluded eBay scripts (moves its hardcoded credential to a read from an external file), you may remove that one filename from `.gitignore` in the same commit.

STEPS

1. Run: `cd ~/Documents/Claude && git add -A && git status --porcelain`
   - If the output is empty, there is nothing to back up tonight. Stop here. Do not commit, push, or message anyone.

2. Before committing, scan staged content for accidentally-hardcoded secrets — this has bitten us twice already (eBay API credentials hardcoded in a SKILL.md and in 19 Python scripts; a live Slack Incoming Webhook URL hardcoded in a shell script). GitHub's push protection is a safety net, not the primary defense — catch it yourself first so a bad night doesn't just fail silently on push. Run this via `do shell script`:

`cd ~/Documents/Claude && git diff --cached > /tmp/nightly_secret_scan.txt && /usr/bin/python3 -c "
import re, sys
patterns = {
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'Generic api_key=': r'(?i)api[_-]?key\s*[:=]\s*[\'\"][A-Za-z0-9_\-]{12,}',
    'Generic secret_key=': r'(?i)secret[_-]?key\s*[:=]\s*[\'\"][A-Za-z0-9_\-]{8,}',
    'Generic password=': r'(?i)\bpassword\s*[:=]\s*[\'\"][^\'\"\n]{4,}[\'\"]',
    'Generic token=': r'(?i)\btoken\s*[:=]\s*[\'\"][A-Za-z0-9_.\-]{12,}[\'\"]',
    'Private key block': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'Slack token': r'xox[baprs]-[A-Za-z0-9-]{10,}',
    'Slack webhook URL': r'hooks\.slack\.com/services/[A-Za-z0-9/]+',
    'Discord/Zapier webhook': r'(discord(app)?\.com/api/webhooks/|hooks\.zapier\.com)[A-Za-z0-9/]+',
    'GitHub token': r'gh[pousr]_[A-Za-z0-9]{20,}',
    'SendGrid key': r'SG\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}',
    'Stripe live key': r'[sp]k_live_[A-Za-z0-9]{10,}',
    'eBay PRD cert/app id': r'PRD-[A-Za-z0-9]{6,}',
    'Generic client_secret=': r'(?i)client[_-]?secret\s*[:=]\s*[\'\"][A-Za-z0-9_.\-]{8,}',
    'Suspicious *_ID = uuid': r'(?i)\b[A-Z_]*_ID\s*=\s*[\'\"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[\'\"]',
    'Generic bearer/auth': r'(?i)(bearer|authorization)\s*[:=]\s*[\'\"][A-Za-z0-9_.\-]{16,}',
}
hits = []
cur_file = None
for line in open('/tmp/nightly_secret_scan.txt', errors='replace'):
    if line.startswith('+++ b/'):
        cur_file = line[6:].strip(); continue
    if not line.startswith('+') or line.startswith('+++'):
        continue
    for name, pat in patterns.items():
        m = re.search(pat, line)
        if m:
            hits.append(f'{cur_file}: [{name}]')
if hits:
    print('SECRETS_FOUND')
    for h in hits: print(h)
    sys.exit(1)
print('CLEAN')
"`

   - If this prints `SECRETS_FOUND` (exit code 1): do NOT commit or push. Go straight to FAILURE HANDLING below with the exact file paths and pattern names it listed — explain a likely secret was about to be committed and needs manual redaction (the established fix pattern: replace the literal value with a read from an untracked file outside the repo, e.g. `~/.vp_secrets/<name>` or `~/ebay_weekly_rankings.py`, and add that specific filename to `.gitignore` if it's a recurring offender — see how the eBay and Slack-webhook incidents were fixed for the exact pattern to follow, but do NOT attempt this rewrite yourself in an unattended run — flag it and stop).

3. If the scan prints `CLEAN`, commit: `cd ~/Documents/Claude && git commit -m "Auto-backup: $(date +%Y-%m-%d) — $(git diff --cached --name-only HEAD~0 2>/dev/null | wc -l | tr -d ' ') files"` — adjust the file-count subcommand if needed so the message is just something reasonable like "Auto-backup: 2026-07-09 — 4 files changed"; exact wording isn't critical.

4. Fetch and confirm we can fast-forward before pushing (protects against any unexpected divergence): `git fetch origin main && git merge-base --is-ancestor origin/main HEAD` — if this fails (non-zero exit), do NOT force-push. Go to FAILURE HANDLING — this means origin/main has commits this local repo doesn't, which shouldn't normally happen for a single-writer backup repo and needs a human look.

5. Push: `GIT_TERMINAL_PROMPT=0 git push origin main`. Confirm success by checking exit code 0 AND that `git rev-parse HEAD` equals `git ls-remote origin main | cut -f1` afterward. If GitHub's push protection rejects the push anyway (our local scan isn't perfect — GitHub's may catch something ours missed), treat that as a scan miss: do not try to resolve it yourself, go to FAILURE HANDLING with the exact GitHub error text (it names the file/line/secret type).

6. If steps 3-5 all succeeded: done, exit silently. No Slack message, no notification — this should be invisible when it works.

FAILURE HANDLING (the only case where you make noise)
If ANY step fails — secret detected (by our scan or GitHub's), auth/push rejected, merge conflict, network error, anything — send a Slack DM to Joshua (user ID `U03BB52MDSA`) with: what step failed, the exact error text or scan hit list, and (if it was a secret) the file path(s) and pattern matched so he knows exactly what to redact. Keep it short and factual. Do not attempt to fix a secret leak yourself in this automated run — flag it and stop, the redaction should be a deliberate human-reviewed action.