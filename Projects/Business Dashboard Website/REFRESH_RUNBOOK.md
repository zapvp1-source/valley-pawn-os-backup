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
PREFERRED (works in any session, incl. scheduled tasks) — deploy from the Mac via osascript
`do shell script` (node lives at ~/Documents/Claude/tools/node):
```
export PATH=$HOME/Documents/Claude/tools/node/bin:$PATH
cd '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website'
export CLOUDFLARE_API_TOKEN=$(cat .cloudflare/api_token) CLOUDFLARE_ACCOUNT_ID=$(cat .cloudflare/account_id)
npx wrangler pages deploy site --project-name=vp-dashboard --commit-dirty=true 2>&1 | tail -1
```
(osascript calls are killed after ~25s; the deploy takes ~10s. If it times out, run it
nohup-backgrounded with output to /tmp/vp_deploy.log and poll the log.)
NOTE: in scheduled-task sessions the project folder is NOT mounted in the sandbox —
do ALL file edits there via osascript `do shell script` (printf/python3 heredoc), never the Write tool.
Live URL: https://vp-dashboard.pages.dev (HTTP Basic Auth: user `valleypawn`,
password in `.cloudflare/site_password`).
IMPORTANT: `site/_worker.js` is the password gate — never delete it from the deploy folder.
Credentials live in `.cloudflare/` inside the project folder (api_token, account_id, project_name, site_password).

## Step 4 — Confirm
Post a one-line summary to Slack #general ONLY if something failed. On success, no Slack post needed.
