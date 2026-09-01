# Dashboard Refresh — Run Status

**Run date:** 2026-08-31 (scheduled task `vp-dashboard-refresh`)

## Result: SUCCESS — all steps completed

### 1. KPI data refresh (site/data/kpis.json) — DONE
- Checked all 7 feed channels against latest Slack posts.
- Loan review / layaway review: latest post already Aug 31 (Mon) — matched existing data, unchanged.
- Company-performance watch: no newer report since Jul 3 — unchanged.
- Daily Funds Verification: NEW Aug 31 18:15 post — $6,000 expected = $6,000 actual, all matched (Culpeper had two separate $2k sends). Updated `funds`, `dates.funds`, and `feeds[]` Last Run -> Aug 31, 2026.
- Items to Price: latest post already Aug 31 — matches existing data, unchanged.
- Intake Margin (pawn-walks): still no newer legacy combined-format post since Aug 13 (channel now only posts the same-day Buy-vs-Loan split format) — held over per never-fabricate rule, unchanged.
- Chekkit Unanswered: latest "Daily Response Summary" post already Aug 31 (covering Aug 30) — matches existing data, unchanged. (Note: the channel also posts a separate "End-of-Day Follow-up" format that is NOT the schema's source — don't confuse the two.)
- `bravoDaily` section untouched (owned by daily-bravo-kpis task).
- `asOf` already August 31, 2026 — confirmed correct.
- JSON validated via live fetch + python3 json.load after deploy — parses clean.

### 2. Artifact sync (site/artifacts/) — DONE
- `cp -R` from `~/Documents/Claude/Artifacts/*` completed via osascript.
- 8 source folders synced (asset-recovery-2025-vs-2026, email-analytics-dashboard, marketing-ceo-briefing, valley-pawn-returns-tracker, vp-fb-content-audit-90d, vp-new-customer-report, vp-website-kpis, vp-website-trend).
- **NEW artifact found:** `marketing-ceo-briefing` (not previously in manifest) — added to `site/data/artifacts.json` (category Marketing, standalone=true since `grep -c window.cowork` = 0). Also bumped `updated` dates for `asset-recovery-2025-vs-2026` and `vp-website-trend` (source folders had newer mtimes than the manifest reflected) and the top-level `artifacts.json` `updated` field.

### 3. Deploy to Cloudflare Pages — DONE (new failure mode found + fixed)
- **`npx wrangler ...` (and running the `wrangler`/`wrangler2` shim scripts through npm) still hangs indefinitely on this Mac** — reconfirmed today, consistent with 8/27 and 8/29 runs. Root cause still not found; direct-binary invocation remains the workaround, not a fix.
- **NEW issue found today, not present in prior run notes:** even the *direct* `wrangler` binary (`~/Documents/Claude/tools/node/bin/wrangler`, no npm/npx) hung for 90+ seconds at the "Detecting git repository information..." step. Root cause: `git rev-parse --show-toplevel` from inside this project resolves to `~/Documents/Claude` (the ENTIRE Claude folder is one git repo, auto-committed by some backup process — saw commit message "Auto-backup: 2026-08-31 — 17 files" in deployment metadata). Wrangler's git auto-detection runs `git status --porcelain` against that whole tree to determine the dirty flag, and on this large/slow-to-stat repo that can take minutes.
- **Fix: pass git metadata explicitly to skip auto-detection.** Get `git rev-parse --abbrev-ref HEAD` and `git rev-parse HEAD` first (both instant — they don't walk the tree), then deploy with `--branch=<branch> --commit-hash=<hash> --commit-message="..."` in addition to `--commit-dirty=true`. This skipped the slow git status entirely — deploy completed in ~2 seconds once invoked this way (6 files uploaded, 22 already cached).
- Deployment URL: `https://36102d45.vp-dashboard.pages.dev`
- **For next session:** always deploy with explicit `--branch`/`--commit-hash`/`--commit-message` flags (grab branch+hash via quick `git rev-parse` calls first) rather than letting wrangler auto-detect git info — auto-detection is unreliably slow on this machine because the repo root is the whole `~/Documents/Claude` tree. Combine this with the existing direct-binary-not-npx workaround from the 8/29 run.
- Caution: while troubleshooting, an earlier background deploy attempt was killed mid-`git status` via `pkill -9 -f 'cli.js pages deploy'` — that's safe (no partial/corrupt deployment resulted), but a narrower `kill -9 <pid>` is preferable next time to avoid killing an attempt that might be about to succeed.

### 4. Verify — DONE
- `curl https://vp-dashboard.pages.dev/` without auth -> **401** (pass)
- `curl` with basic auth -> **200** (pass)
- `data/kpis.json` fetched live (through the deployed site, with auth) -> 200, parses clean, `asOf` = August 31, 2026, `funds` reflects the new $6,000/$6,000 figures.
- `site/_worker.js` (password gate) confirmed present in the deploy folder, untouched.

## Context notes for next session
- Same VP Ops Engine stand-down note as prior runs still applies — Cowork-side weekly tasks are the source for loan/layaway/company-performance.
- No Slack post made — success, and the runbook only requires a post on failure.
- The npm/npx hang on this Mac is now confirmed across three run dates (8/27, 8/29, 8/31). Direct-binary invocation continues to be a reliable workaround. The new git-status slowness is a related but distinct issue with its own workaround (explicit commit flags) — worth folding both into REFRESH_RUNBOOK.md's Step 3 permanently so future sessions don't have to rediscover this.
