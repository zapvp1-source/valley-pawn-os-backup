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

**2026-10-16 finding: prefer Option C by default.** When this session IS linked to the Mac (device_bash works fine for file I/O, `get_device_info`/`device_list_dir` all succeed), running `wrangler pages deploy` itself *through device_bash* still reliably hangs forever with zero output past the 2nd `GET .../pages/projects/<project>` API call (confirmed via `WRANGLER_LOG=debug`; reproduced 5x with --no-bundle / CI=true / WRANGLER_SEND_METRICS=false / stdin redirected / `timeout -k` kill-after -- all identical). Plain `curl` to the Cloudflare REST API and all other device_bash file operations work fine in the same shell, so this is specific to wrangler's own upload-prep step inside that VM, not the bridge or egress generally. Don't burn more than one retry on device_bash-run wrangler -- go straight to Option C below (stage `site/` + `.cloudflare/` via `device_stage_files`, run wrangler in the cloud sandbox instead). It deployed cleanly in ~5s on the first try. This supersedes Option C's old framing as a "device_bash is down" fallback -- treat it as the default deploy path whenever a plain device_bash wrangler attempt doesn't finish within ~60s.



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
3. (Added 2026-10-15, confirmed on device_bash too, not just osascript.) The wrangler binary can
   print "Deployment complete!" and then hang afterward with no further output (telemetry/cleanup?),
   well past a 150s call limit, so a plain foreground run looks like a failure when the deploy
   itself already succeeded in under 10s. A background `nohup wrangler ... & disown` does NOT
   reliably survive past the end of its own device_bash call either (the process was gone on the
   next poll with no further log output). The reliable pattern: redirect to a log file and wrap in
   `timeout N` (N comfortably above ~10s, e.g. 170), e.g.
   `timeout 170 wrangler pages deploy site --project-name=... --commit-dirty=true > /path/log 2>&1`,
   then ALWAYS read the log afterward even if the shell reports a nonzero/timeout (124) exit --
   look for "Deployment complete!" and the deployment URL in the log before concluding the deploy
   failed, and verify independently via curl (Step 4) either way.
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

## Note (2026-11-04, dashboard-refresh run)
The scheduled task's current-rules block says #chekkit-unanswerd-summary (C0B1PEW0C30) "nothing
posts there any more." That's stale -- the channel (now named #chekkit-messages-missed, same ID)
is still posting a daily "Daily Response Summary" at 8 AM plus an "End-of-Day Follow-up" at 7 PM.
This run used the latest Daily Response Summary post and refreshed data.daily.chekkit normally.
If the scheduled task's stored prompt is ever edited, this line can come out of its current-rules
block.

## Note (2026-11-09, dashboard-refresh run)
Confirmed the 2026-11-02 "bridge quirk" (CHANGELOG) still happens on this folder: a just-created
or just-copied file reports nlink>1 to device_stage_files and is refused ("file is hardlinked"),
even seconds after a fresh `cp`/`tar` into this mount -- it did NOT clear within the first ~5-10s
this run. It DID clear on a retry roughly 30-60s later (no change to the file, just waited and
re-issued device_stage_files with the same path). Files elsewhere under the plain `Projects` mount
(outside the `Business Dashboard Website` subfolder) staged fine immediately. So: if a stage call
on a freshly-written file in this folder fails with the nlink error, don't treat it as Option C
being down -- wait ~30-60s (do something else, like a Slack read, in between) and retry the exact
same device_stage_files call once or twice before falling back further.
Also confirms #chekkit-messages-missed (C0B1PEW0C30) is still live and posting daily -- updated
data.daily.chekkit normally again this run (per the 2026-11-04 note above); the scheduled task's
"nothing posts there any more" line in its stored prompt is still stale.

## 2026-11-09 — Slack Restructure: where the full data lives now (read this before Step 1)
Channel posts are now HEADLINES (≤5 lines) and all-clear monitors are silent. Do not parse channel messages
for tables any more. The full body of every routed report is written, verbatim (canvas markdown), to the Mac
at `Valley Pawn OS/fleet/canvas_state/dept_sections/<dept>.json` — `{section_key: {md, updated}}` — and
mirrored on the department canvas in Slack:
- loans (layaway table, layaway yield, first-payment-default): `dept_sections/loans.json` · canvas F0CG1NUG093
- scoreboard (store rankings, employee rankings, FFL/NICS): `dept_sections/scoreboard.json` · canvas F0CG6S3EXA6
- aged inventory / markdowns: `dept_sections/aged.json` · canvas F0CG0QPVDDH
- leadership (monthly analytics, scrap, mobilepawn, pawn walk / sold / discount): `dept_sections/leadership.json` · canvas F0CG6S5CTDY
- daily checks (funds, jewelry, texts, calls): `dept_sections/daily.json` · canvas F0CG0QRPJJX
- marketing: `dept_sections/marketing.json` · canvas F0CFRLDV2EB
Funds: a matched day posts nothing. Treat a `funds-clean` line in `Valley Pawn OS/fleet/quiet_ledger/<YYYY-MM-DD>.md`
as "all 5 stores matched" for that date; a discrepancy day still appears in `dept_sections/daily.json` and in #daily-checks.
Channel ids are unchanged by the renames (#layaway-review → #loans-layaways, #company-performance → #leadership-reports,
#daily-funds-reconcilation → #daily-checks, #social-media → #marketing).

## Note (2026-11-16, dashboard-refresh run)
Two observations worth flagging for future runs:
1. The dept_sections/*.json files described in the 2026-11-09 restructure note above have NOT
   been updated since they were created (all 7 files still show mtime/`updated` timestamps of
   2026-11-09 14:3x-4x). In practice this run went back to reading the Slack channels directly
   (headline posts still carry the data this dashboard needs: Weekly Layaway Review, Funds
   verification, Items to Price, Daily Pawn Walk, Chekkit Daily Response Summary all still post
   full content, not just headlines) and that worked fine. Treat the "channel posts are now
   headlines only" framing in the 2026-11-09 note as not reflecting current reality until the
   dept_sections files are confirmed to actually be refreshing.
2. #pawn-walks "Daily Pawn Walk" did not post this morning (no 2026-11-16 07:15 post for
   2026-11-15 data) -- last post found was 2026-11-15 07:15 for 2026-11-14 data. kpis.json's
   daily.intakeMargin was correctly left unchanged per the "no newer report -> keep existing"
   rule, and the feeds[] Last Run date for Intake Margin was corrected from a stale "Nov 16" to
   the accurate "Nov 15". Not treated as a dashboard-refresh failure (not this task's feed to
   fix), but may be worth a look if it keeps happening.

This run also confirmed Option C (cloud-sandbox deploy via a single tar bundle staged through
device_stage_files, rather than staging 50+ individual files) works cleanly and is faster than
enumerating the whole site/ tree file-by-file: `tar czf .deploy_bundle.tar.gz site .cloudflare`
inside the project folder, stage that one file, extract in the sandbox, deploy from there.

## Note (2026-11-18, dashboard-refresh run)
The Nov 17 07:15 "Daily Pawn Walk" post (for 2026-11-16 data) switched to a new, simpler format:
only a company-wide "N overpay flags out of M items taken in" line plus a list of just the
flagged items per store -- it no longer includes the Buy Intake / Loan Intake per-store avg-margin
tables that daily.intakeMargin's schema needs (stores[store, items, avgMargin, flags]). Per-store
items and avgMargin can't be derived from the flagged-items list alone, so this run left
daily.intakeMargin unchanged (still the 2026-11-14 data from the last post in the old format,
per the 2026-11-16 note above) rather than fabricate per-store margins. Not treated as a failure.
If #pawn-walks keeps posting in this new format going forward, the intakeMargin schema or its
parse logic will need to be revisited -- it will otherwise stay permanently stale.
This run: asOf bumped to Nov 18, 2026 (no feed had a newer parseable report than what was already
in kpis.json -- funds/items-to-price/chekkit/layaway/company-performance all already reflected
their latest available post). Deploy used the tar-bundle Option C path per the 2026-11-16 note;
.deploy_bundle.tar.gz hit the documented nlink>1 bridge quirk on first stage attempt, cleared
after a ~20s gap doing other work, consistent with the 2026-11-09 note.

## Note (2026-11-18, dashboard-refresh run, 13:20 UTC firing)
Second refresh today (an earlier run already bumped asOf to Nov 18 at ~00:17 UTC). Picked up
genuinely new posts that landed after that run: Daily Funds Verification for Tue Nov 17 (posted
2026-11-17 20:11 ET -- 3/5 stores verified, Roanoke and Waynesboro could not be verified, no
Bravo data -- not a discrepancy, so funds.status changed from "4/5 MATCHED" to "3/5 VERIFIED (2
unverified)"; funds.actual now sums only the 3 verified stores' Bravo amounts, Roanoke/Waynesboro
excluded rather than treated as $0), Items to Price for Nov 18 (225 items / $12,316.00, down from
267/$17,793 the day before), and the Chekkit Daily Response Summary posted this morning covering
Nov 17 (all clear, 0 unanswered, confirmed by the Nov 17 7PM End-of-Day Follow-up).
Left unchanged (no newer report than what was already in kpis.json): layaway (next Weekly Layaway
Review is Nov 23), loan-review (retired, per standing rule), company-performance watch[] (no new
Monthly Analytics post since Nov 1), and daily.intakeMargin (#pawn-walks is still posting the
simplified overpay-flags-only format introduced ~Nov 16-17 -- no per-store Buy/Loan Intake margin
tables to parse; still showing Nov 14 data per the 2026-11-16/11-18 notes above).
Artifacts sync (Step 2) skipped silently -- ~/Documents/Claude/Artifacts is not a connected folder
on this device_bash session.
Deploy: Option C (tar-bundle staged via device_stage_files, wrangler run in the cloud sandbox).
Bundle hit the documented nlink>1 bridge quirk on first stage attempt; cleared on retry after
doing other work in between (no fixed delay needed -- just don't retry back-to-back). Deployed
cleanly, ~1.5s upload + worker deploy. Verified: apex https://vp-dashboard.pages.dev/ returns 401
with no auth and 200 with basic auth; kpis.json parses and matches the values written above; the
deployment-specific URL (https://b638f416.vp-dashboard.pages.dev/) also returned 200, no stale-CDN
concerns this run.

## Note (2026-11-19, dashboard-refresh run)
Picked up one genuinely new post: Daily Funds Verification for Wed Nov 18 (posted 2026-11-18
18:43 ET -- 4 of 5 stores matched, Waynesboro discrepancy: expected $0.00, Bravo $2,000.00).
funds.status changed from "3/5 VERIFIED (2 unverified)" to "4/5 MATCHED (1 discrepancy)";
expected/actual updated to $0.00 / $2,000.00 (actual = sum of reported Bravo amounts).
Left unchanged (no newer report than what was already in kpis.json): layaway-review (next
Weekly Layaway Review is Nov 23), loan-review (retired, per standing rule), company-performance
watch[] (no new Monthly/Gift-card post with KPI data since Nov 1-2), items-to-price (still the
Nov 18 08:00 post, next due ~8 AM Nov 19), and daily.intakeMargin (#pawn-walks reposted the Nov
17 simplified overpay-flags-only format again on Nov 18 -- still no per-store Buy/Loan Intake
margin tables to parse; still showing Nov 14 data per the 2026-11-16/11-18 notes above).
Chekkit unchanged -- latest Daily Response Summary still covers Nov 17 (all clear); the Nov 18
End-of-Day Follow-up has no new daily-summary data to add until tomorrow's 8 AM post.
Artifacts sync (Step 2) skipped silently -- ~/Documents/Claude/Artifacts is not a connected
folder on this device_bash session.
Deploy: Option C (tar-bundle staged via device_stage_files, wrangler run in the cloud sandbox).
Bundle staged cleanly on the first attempt this run (no nlink>1 quirk). Deployed cleanly in
~1.2s. Verified: apex https://vp-dashboard.pages.dev/ returns 401 with no auth and 200 with
basic auth; kpis.json parses and matches the values written above (asOf bumped to Nov 19,
2026); the deployment-specific URL (https://260e7870.vp-dashboard.pages.dev/) also returned
200, no stale-CDN concerns this run.
Minor housekeeping note: the .deploy_bundle.tar.gz staging file in this project folder could
not be deleted (device_bash delete permission not granted in this folder) -- left in place,
harmless, gets overwritten next run.


## Note (2026-11-19, dashboard-refresh run, 13:19 UTC firing)
Third refresh today (earlier runs bumped asOf to Nov 19 at ~00:17 UTC, then updated the Wed Nov
18 funds discrepancy before this firing). Picked up two genuinely new posts: Items to Price for
Nov 19 (178 items / $16,026.97, down from 225/$12,316 the day before -- Culpeper and Harrisonburg
both worked down their backlog materially) and the Chekkit Daily Response Summary posted this
morning covering Nov 18 (all clear, 0 unanswered, confirmed by the Nov 18 7PM End-of-Day
Follow-up).
Left unchanged (no newer report than what was already in kpis.json): funds (still Wed Nov 18 --
no new Daily Funds Verification post since the 18:43 ET post already captured), layaway-review
(next Weekly Layaway Review is Nov 23), loan-review (retired, per standing rule),
company-performance watch[] (no new Monthly/Gift-card post since Nov 1-2), and daily.intakeMargin
(#pawn-walks posted again at 07:15 ET for Nov 18 data, still in the simplified overpay-flags-only
format introduced ~Nov 16-17 -- "4 overpay flags out of 36 items taken in" with no per-store
Buy/Loan Intake margin tables to parse; still showing Nov 14 data per the 2026-11-16/11-18 notes
above).
Artifacts sync (Step 2) skipped silently -- ~/Documents/Claude/Artifacts is not a connected
folder on this device_bash session.
Deploy: Option C (tar-bundle staged via device_stage_files, wrangler run in the cloud sandbox).
The bundle hit the documented nlink>1 bridge quirk on the first two stage attempts (consecutive,
no gap) -- resolved this time not by waiting but by `cp`-ing the tarball to a second filename
(breaks the hardlink, confirmed via `stat` showing Links: 1) and staging that copy instead, which
worked on the first try. Worth noting as a faster alternative to the wait-and-retry approach in
the 2026-11-09/11-18 notes when there's no natural "do something else" task in between. Deployed
cleanly (~1.3s upload + worker deploy). Verified: apex https://vp-dashboard.pages.dev/ returns 401
with no auth and 200 with basic auth; kpis.json parses and matches the values written above
(asOf still November 19, 2026); the deployment-specific URL
(https://ad024db2.vp-dashboard.pages.dev/) also returned 200, no stale-CDN concerns this run.

## Note (2026-11-19 EST / 2026-11-20 run)
One genuinely new post: Daily Funds Verification for Thu Nov 19 (posted 2026-11-19 18:38 ET --
4 of 5 stores verified; Culpeper could not be verified, no Bravo data; the 4 verified stores all
matched -- Harrisonburg $0/$0, Lexington $0/$0, Roanoke $2,000/$2,000, Waynesboro $2,000/$2,000).
funds.status changed from "4/5 MATCHED (1 discrepancy)" to "4/5 VERIFIED (1 unverified)" per the
Nov 17 precedent (unverified-only case uses VERIFIED/unverified wording, not MATCHED/discrepancy);
expected/actual both set to $4,000 (sum of the 4 verified stores only, Culpeper excluded rather
than treated as $0).
Left unchanged (no newer report than what was already in kpis.json): items-to-price (still the
Nov 19 08:00 post, 178/$16,026.97 -- no Nov 20 post yet, local time was still Nov 19 evening at
run time), layaway-review (next Weekly Layaway Review is Nov 23), loan-review (retired, per
standing rule), company-performance watch[] (no new Monthly/Gift-card post since Nov 1-2),
chekkit (latest Daily Response Summary still covers Nov 18, all clear; no Nov 19 End-of-Day
Follow-up posted yet at run time), and daily.intakeMargin (#pawn-walks still posting the
simplified overpay-flags-only format introduced ~Nov 16-17 -- no per-store Buy/Loan Intake
margin tables to parse; still showing Nov 14 data per the 2026-11-16/18/19 notes above). Bumped
the Intake Margin feeds[] Last Run date to Nov 19, 2026 to reflect the latest post in the channel
(data itself still unchanged).
Artifacts sync (Step 2) skipped silently -- ~/Documents/Claude/Artifacts is not a connected
folder on this device_bash session.
Deploy: Option C (tar-bundle staged via device_stage_files, wrangler run in the cloud sandbox).
Bundle staged cleanly on the first attempt despite nlink=2 on the fresh tar (the documented
nlink>1 quirk didn't block this stage). Deployed cleanly (~1.3s upload + worker deploy).
Verified: apex https://vp-dashboard.pages.dev/ returns 401 with no auth and 200 with basic auth;
kpis.json parses and matches the values written above (asOf bumped to November 20, 2026); the
deployment-specific URL (https://d76f7593.vp-dashboard.pages.dev/) also returned 200, no
stale-CDN concerns this run.

## Note (2026-11-20, dashboard-refresh run, 13:19 UTC firing)
Second refresh today (an earlier run already bumped asOf to Nov 20 at ~00:17 UTC and updated the
Thu Nov 19 funds verification). Picked up three genuinely new posts that landed after that run:
Items to Price for Nov 20 (189 items / $16,204.80, up from 178/$16,026.97 the day before -- all
5 stores ticked up slightly), the #pawn-walks Daily Pawn Walk for Nov 19 data (19 overpay flags
out of 85 items -- still the simplified overpay-flags-only format introduced ~Nov 16-17, no
per-store Buy/Loan Intake margin tables, so daily.intakeMargin data stays unchanged at Nov 14;
only its feeds[] Last Run date was bumped to Nov 20 per the Nov 19 precedent), and the Chekkit
Daily Response Summary posted this morning covering Nov 19 (1 unanswered at Harrisonburg --
Kaywan Hama Amin, confirmed still unanswered at close by the Nov 19 7:49 PM End-of-Day
Follow-up; all other stores 0).
Left unchanged (no newer report than what was already in kpis.json): funds (still Thu Nov 19 --
no new Daily Funds Verification post since the 18:38 ET post already captured; next due ~6 PM
today), layaway-review (next Weekly Layaway Review is Nov 23), loan-review (retired, per
standing rule), company-performance watch[] (no new Monthly/Gift-card post since Nov 1-2).
Artifacts sync (Step 2) skipped silently -- ~/Documents/Claude/Artifacts is not a connected
folder on this device_bash session (only "Business Dashboard Website" and "Projects" are
connected this run).
Deploy: Option C (tar-bundle staged via device_stage_files, wrangler run in the cloud sandbox).
Could not delete the prior run's .deploy_bundle*.tar.gz (device_bash delete permission not
granted in this folder), so this run created a fresh-named bundle (.deploy_bundle_<epoch>.tar.gz)
-- that alone still showed nlink>1 to device_stage_files (the documented bridge quirk); a `cp` to
a second filename did NOT clear it immediately this time either, but a retry ~15s later (after
installing wrangler in the cloud sandbox in between) succeeded on the copy. Deployed cleanly
(~1.4s upload + worker deploy). Verified: apex https://vp-dashboard.pages.dev/ returns 401 with
no auth and 200 with basic auth; the deployment-specific URL
(https://5b97dd52.vp-dashboard.pages.dev/) also returned 200; kpis.json parses as valid JSON and
matches the values written above (asOf still November 20, 2026). No Slack post (success, per
standing no-Slack-ever rule for this task).

## Note (2026-11-20, dashboard-refresh run, ~19:18 ET firing)
Third refresh today. Picked up one genuinely new post: Funds verification for Fri Nov 20
(posted 2026-11-20 18:37:46 ET -- all 5 stores matched, every dollar sent is in Bravo:
Culpeper $2,000/$2,000, Harrisonburg $2,000/$2,000, Lexington $2,000/$2,000, Roanoke $0/$0,
Waynesboro $2,000/$2,000). funds.status changed from "4/5 VERIFIED (1 unverified)" to
"5/5 MATCHED"; expected/actual both set to $8,000 (sum of all 5 stores, all verified+matched).
Left unchanged (no newer report than what was already in kpis.json): items-to-price (still the
Nov 20 08:00 post, 189/$16,204.80), layaway-review (next Weekly Layaway Review is Nov 23),
loan-review (retired, per standing rule), company-performance watch[] (no new Monthly/Gift-card
post since Nov 1-2), daily.intakeMargin (#pawn-walks posted again at 07:15 ET for Nov 19 data,
still the simplified overpay-flags-only format introduced ~Nov 16-17 -- "19 overpay flags out of
85 items" with no per-store Buy/Loan Intake margin tables to parse; still showing Nov 14 data),
and chekkit (latest Daily Response Summary still covers Nov 19, 1 unanswered at Harrisonburg;
no new Daily Response Summary for Nov 20 yet -- that posts ~8 AM Nov 21; a Nov 20 7PM End-of-Day
Follow-up reported "no misses flagged today" but that's a same-day real-time note, not a new
Daily Response Summary, so left the stored block as-is per the "no newer report -> keep
existing" rule).
Artifacts sync (Step 2) skipped silently -- ~/Documents/Claude/Artifacts is not a connected
folder on this device_bash session (only "Business Dashboard Website" and "Projects" connected).
Deploy: Option C (tar bundle staged via device_stage_files, wrangler run in the cloud sandbox).
First stage attempt on a freshly-made bundle hit the documented nlink>1 bridge quirk; a `cp` to
a second filename did NOT clear it immediately either this time, but a retry ~25s later (no
specific action needed in between, just a short wait) succeeded. Deployed cleanly (~1.4s
upload + worker deploy). Verified: apex https://vp-dashboard.pages.dev/ returns 401 with no
auth and 200 with basic auth; kpis.json parses as valid JSON and matches the values written
above (asOf unchanged at November 20, 2026 -- already current from an earlier run today); the
deployment-specific URL (https://1bb6d9cc.vp-dashboard.pages.dev/) also returned 200, no
stale-CDN concerns this run. No Slack post (success, per standing no-Slack-ever rule for this
task).
