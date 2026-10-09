# Dashboard Refresh Runbook

Used by the nightly `dashboard-refresh` scheduled task. Follow these steps exactly.

## Site location
- Project folder: `/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/`
- Deployable site root: `site/` (index.html + data/ + artifacts/)
- Sandbox path: `/sessions/<session>/mnt/Business Dashboard Website/site/`

## Step 1 — Refresh KPI data (site/data/kpis.json)
Read the LATEST report message from each Slack channel and parse into kpis.json
(keep the existing JSON schema exactly — the dashboard render code depends on it):

| Channel | ID | Feeds |
|---|---|---|
| #loan-review | C0B08RS2BMK | pastDue table, pastDueTotal, companyLoanBalance, dates.loans |
| #layaway-review | C04N24STDP1 | layaway table, layawayTotal, dates.layaway |
| #daily-funds-reconcilation | C0B3R9B3S8H | funds block, dates.funds |
| #company-performance | C0B26GD8D2R | watch items (monthly analytics warnings) |

Rules:
- Only use the standard-format report posts ("Sent using Claude"); skip conversational messages.
- Update `asOf` to today's date. Update the `feeds` table Last Run column.
- If a channel has no new report since last refresh, keep its existing values.
- Never fabricate numbers. If parsing fails, keep old data and note it in the Slack summary.

## Step 2 — Refresh artifacts
Via osascript shell:
```
cp -R /Users/joshuadavis/Documents/Claude/Artifacts/* '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/artifacts/'
rm -rf '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/artifacts'/*/versions
```
If a NEW artifact appears (not in site/data/artifacts.json), add a manifest entry
(id, name, category, desc, updated, standalone = true if `grep -c "window.cowork"` is 0).
Update `updated` dates for changed artifacts.

## Step 3 — Deploy to Cloudflare Pages

### Option A (use this FIRST if the session has no Control_your_Mac/osascript tool —
confirmed working 2026-09-30): sandbox-direct wrangler deploy
In Cowork sessions where `~/Documents/Claude/Artifacts` isn't mountable and
`mcp__Control_your_Mac__osascript` doesn't exist even via ToolSearch (this has been a
recurring gap since ~9/17 — see FAILURE_LEDGER.md), the "Business Dashboard Website" and
"Projects" folders are still directly mounted into the sandbox, and the sandbox has its own
node/npm and outbound network access. No osascript is needed for the deploy step at all:

```
mkdir -p /tmp/npm-global   # or any writable dir in the sandbox, e.g. under the scratchpad
npm config set prefix /tmp/npm-global
export PATH=/tmp/npm-global/bin:$PATH
npm install -g wrangler --silent
cd "<mounted path to 'Business Dashboard Website'>"
export CLOUDFLARE_API_TOKEN=$(cat .cloudflare/api_token)
export CLOUDFLARE_ACCOUNT_ID=$(cat .cloudflare/account_id)
PROJECT=$(cat .cloudflare/project_name)
wrangler pages deploy site --project-name="$PROJECT" --branch=main \
  --commit-message="Auto-refresh: $(date +%F)" --commit-dirty=true
```
(A plain `npm install -g wrangler` without setting `prefix` first fails EACCES in the
sandbox — the default global path isn't writable there. Also note: this sandbox mount has no
`.git` directory, so none of the host-Mac git-hang gotchas below apply — no `--commit-hash`
needed.) This does NOT sync `site/artifacts/` (Step 2 still needs Control_your_Mac to reach
`~/Documents/Claude/Artifacts`) — it just deploys whatever is already in the mounted
`site/` folder, so run Step 1 (and Step 2 if possible) first.

### Option B — deploy from the Mac via osascript (use when Control_your_Mac IS available)
`do shell script` (node lives at ~/Documents/Claude/tools/node).

**Two confirmed gotchas on this Mac, both with workarounds baked in below:**
1. `npx wrangler ...` / `npm install -g wrangler` / any npm-wrapped invocation **hangs
   indefinitely with zero output**. Always call the direct binary
   `$HOME/Documents/Claude/tools/node/bin/wrangler` — never prefix with `npx`/`npm exec`.
2. `~/Documents/Claude` is itself one giant git repo (auto-backed-up). Wrangler's git
   auto-detection runs `git status --porcelain` against that whole tree to compute the dirty
   flag, which can hang for minutes. Always pass `--branch`/`--commit-hash`/`--commit-message`
   explicitly (grabbed via fast `git rev-parse` calls, which don't walk the tree) so wrangler
   skips auto-detection entirely.

```
export PATH=$HOME/Documents/Claude/tools/node/bin:$PATH
cd '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website'
export CLOUDFLARE_API_TOKEN=$(cat .cloudflare/api_token) CLOUDFLARE_ACCOUNT_ID=$(cat .cloudflare/account_id)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
HASH=$(git rev-parse HEAD)
$HOME/Documents/Claude/tools/node/bin/wrangler pages deploy site --project-name=vp-dashboard \
  --branch="$BRANCH" --commit-hash="$HASH" --commit-message="Auto-refresh: $(date +%F)" \
  --commit-dirty=true 2>&1 | tail -1
```
(osascript calls are killed after ~25s; the deploy itself takes ~2-10s once the git-detection
step is skipped via the flags above. If a call still needs backgrounding, nohup it with output
to /tmp/vp_deploy.log and poll the log — but check the log for progress before killing a running
attempt; use a narrow `kill -9 <pid>`, not a broad `pkill -f`, so you don't kill an attempt that's
about to succeed.)
NOTE: in scheduled-task sessions the project folder is NOT mounted in the sandbox —
do ALL file edits there via osascript `do shell script` (printf/python3 heredoc), never the Write tool.
Live URL: https://vp-dashboard.pages.dev (HTTP Basic Auth: user `valleypawn`,
password in `.cloudflare/site_password`).
IMPORTANT: `site/_worker.js` is the password gate — never delete it from the deploy folder.
Credentials live in `.cloudflare/` inside the project folder (api_token, account_id, project_name, site_password).

### Option C — cloud-sandbox deploy when device_bash itself is down (confirmed working 2026-10-08, 2 consecutive runs)
Distinct from Option A's premise (no Control_your_Mac tool at all) and Option B's premise (Mac
linked, device_bash works): this is for when the Mac IS linked (`get_device_info` succeeds,
`device_list_dir`/`device_stage_files`/`device_commit_files` all work) but `device_bash`
specifically errors on every call, including a trivial `echo hello`. Don't burn more than ~3
retries on device_bash in that shape — treat it as the Rule 15 "same failure twice" case and
switch to this path:

1. `device_stage_files` every file under `site/` (root files + every file under `site/artifacts/`,
   enumerate recursively via `device_list_dir(recursive=true)` first — there is no glob, so list
   paths explicitly) plus the 4 files under `.cloudflare/`, into the cloud sandbox.
2. Edit `kpis.json` (Step 1) locally in the sandbox against the staged copy, then overlay it onto
   the staged `site/data/kpis.json` before deploying — don't deploy the stale staged copy.
3. `mkdir -p /tmp/npm-global && npm config set prefix /tmp/npm-global && export PATH=/tmp/npm-global/bin:$PATH && npm install -g wrangler --silent`
   (the default global prefix isn't writable in the sandbox — EACCES without this).
4. `cd` into the merged local copy, `export CLOUDFLARE_API_TOKEN=$(cat .cloudflare/api_token) CLOUDFLARE_ACCOUNT_ID=$(cat .cloudflare/account_id)`,
   `wrangler pages deploy site --project-name=vp-dashboard --commit-dirty=true --commit-message="Auto-refresh: $(date +%F)"`.
   No `.git` dir in the staged copy, so no git-auto-detection hang — no `--branch`/`--commit-hash` needed.
5. Verify as in Step 4 below. Note: the FIRST curl to the apex domain right after a deploy can
   return a stale CDN-cached response for a few seconds — if verification looks stale, retry once
   with a cache-busting query param, or hit the deployment-specific `https://<hash>.vp-dashboard.pages.dev`
   URL wrangler prints, before concluding the deploy didn't take.
6. This path does NOT sync `site/artifacts/` from `~/Documents/Claude/Artifacts` (that source folder
   still needs Control_your_Mac or a connected-folder grant) — it only deploys whatever is already
   in `site/artifacts/` on the Mac, staged as-is. Run Step 2 first if that folder ever becomes
   reachable.

## Step 4 — Confirm
Post a one-line summary to Slack #general ONLY if something failed. On success, no Slack post needed.
