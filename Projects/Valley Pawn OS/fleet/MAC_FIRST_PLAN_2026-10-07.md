# Mac-first plan — move every recurring Cowork task onto the Mac (launchd)

Written 2026-10-07 by a read-only investigation session (Joshua's goal, 10/7: get the fleet off Claude's Cowork scheduler so Anthropic product changes stop breaking it). Nothing was disabled or converted here. One harmless test task was created and cleaned up (see section 2.4).

Sources: local registry snapshots `fleet/_backups/registry/auto/` (latest 12:24), `mcp__scheduled-tasks__list_scheduled_tasks` (10/7 11:47), and the live cloud routine list read from claude.ai in Joshua's Chrome (`GET https://claude.ai/v1/code/triggers`, 10/7 11:55 and 12:33, read-only).

## 1. Headline

- **98 recurring Cowork tasks are live today**: **48 run as cloud copies** (2 of them also still enabled locally) and **50 run locally**. Not counted: 81 native `com.valleypawn.*` launchd agents (already off Cowork), 4 enabled one-offs (2 local, 2 cloud reminders), and ~130 disabled or retired registry entries.
- **Class counts (98):** M 35 · A 20 · API 17 · B 13 · R 11 · H 2.
- **Waves:** Wave 1 daily team-facing 13 · Wave 2 daily-internal + weekly 33 · Wave 3 monthly (next fire 11/1–11/6, a few on 10/15–10/20) 35 · Wave 4 quarterly/annual 5 · retire 11 · supervised H 1 (+1 H in wave 3).
- **The cloud copies are visible and can be switched off.** They are claude.ai "routines" (trigger IDs `trig_…`), bound to device "Claude Desktop (macOS)". `update_scheduled_task enabled:false` does NOT touch them. See section 2.
- **The cloud move is still happening.** The app's "sweep" moved `vp-staff-video-chase` at 11:31 ET today, 9 minutes after its 2nd clean local run. Any local task with a couple of runs and no browser or Mac tool use is a candidate to move next. **Highest near-term risk: `vp-deal-of-week-monday-prompt` and `vp-deal-of-week-monday-reminder`** (2 clean runs each, next run Mon 10/12). The 1st-of-month batch (≈25 tasks with 1 clean run each) is likely to move after its 11/1 run.
- **New cloud-only tasks are being created that never appear in the local registry.** Today 11:59–12:00 ET another session created `Gusto signature check (daily)` (trig_011ctgLsqBgbMtS9fKsC3f3p, 09:52 Mon–Sat) and `Gusto session keeper` (trig_01AyoSGD1m7jNp5a7kNZQems, every 2 h), both `created_kind: cowork_task`, `created_via: meta_mcp`. They are not in the table below (they postdate it). Fleet inventories must read the cloud list, not just the local registry.

## 2. Cloud copies — how to see them, tell them apart, and switch them off

### 2.1 Where the cloud copies are listed
- **Local registry** (`scheduled-tasks.json`, snapshots in `fleet/_backups/registry/auto/`): every moved task carries `"migratedToRemote": {"triggerId": "trig_…", "via": "sweep"}` + `migratedToRemoteAt`, and the app sets local `enabled:false`. 48 entries, moved 10/6 15:31–17:32 ET in batches of ~10 at :31/:01, plus 1 on 10/7 11:31.
- **claude.ai routines API** (Joshua's browser session): `GET https://claude.ai/v1/code/triggers` (headers `anthropic-version: 2023-06-01`, `anthropic-beta: ccr-triggers-2026-01-30`, paginated with `next_cursor`). 10/7 12:33: 75 triggers = the 48 moved tasks (all `enabled:true`, `created_via:http_api`, cron prefixed `CRON_TZ=America/New_York`, bound to "Claude Desktop (macOS)"), 2 enabled one-off reminders, the 2 new Gusto cloud tasks, and 23 disabled or one-shot leftovers (the 8/21 cloud→local holds, fired reminders).
- **Not visible** on the claude.ai/code/routines page ("No routines yet"). The `list_scheduled_tasks` tool shows the local entry only (enabled:false). No trigger tool is offered to local Cowork sessions. Cloud Cowork sessions do have one (MCP connector `Claude_Code_Remote` appears in each trigger's `mcp_connections`), which is how the 10/7 08:00 chekkit run saw its own trigger.

### 2.2 Does `update_scheduled_task enabled:false` stop the cloud copy?
**No.** It only changes the local registry row. Proof: `chekkit-unanswered-alert` has been local `enabled:false` since the 10/6 move (and was set false again after the 10/7 self-heal), yet trigger `trig_016fRstAx3ySdNen1QUGaNr3` is `enabled:true`, fired 10/7 08:27 ET as a cloud session, and has its next run 10/8 08:12. The same holds for all 46 moved tasks whose local row is disabled. The reverse is also true: setting the local row back to `enabled:true` (northwest, dress-code) does not turn the cloud copy off, so those two now run **twice** a day.

### 2.3 How to tell a cloud run from a local run
| Signal | Cloud copy | Local run |
|---|---|---|
| Registry `lastRunAt` / `observedToolUse.runsObserved` | not updated (frozen at move time) | updated |
| claude.ai sessions (`GET /v1/code/sessions?tags=cowork-remote…`) | session with `environment_kind: anthropic_cloud`, tags `cowork-scheduled`, `routine:chrome-eligible`, `routine_notify_push`, title = task display name | not listed |
| Session context | runs on Anthropic's servers, reaches the Mac only through the `remote-devices` bridge (files under Projects work, Chrome/osascript/computer-use often don't) | primary cwd `/private/var/empty`, extra dirs = local-agent-mode outputs + Projects, shell `mcp__workspace__bash` (sandbox `/sessions/<name>`), Chrome tools present (proven by test file `fleet/state/cloudtest/run-*.txt`) |
| Timing | 10–30+ min after cron (trigger jitter) | jitter of a few minutes |
| Slack | posts show as Joshua, "Sent using Claude" (same as local) — **not a distinguishing signal** | same |
Note: interactive Cowork chats are now cloud sessions too (tag `cowork-remote-interactive`).

### 2.4 How to switch a cloud copy OFF — what is proven and what is not
- **Proven: the switch is the trigger's own `enabled` flag, not the local task.** Evidence: the 9 cloud triggers disabled on 8/21 (e.g. `hiring-inbox-watch` trig_012TbuwabkcJuFj5roSMvvmc, `Precious Metals Settlement Handler` trig_01K8pTE3CfdC7jkiK5LD6sBV) still read `enabled:false` today with `next_run_at` frozen at 8/21–9/1, i.e. they stayed off for 7 weeks and the app never re-enabled them. The 10/6 sweep made new trigger IDs; it did not revive the old ones.
- **Exact call (Claude Code routines API, same one the 8/21 session used through its trigger tool):** `POST https://claude.ai/v1/code/triggers/<trig_id>` with body `{"enabled": false}`, headers `anthropic-version: 2023-06-01`, `anthropic-beta: ccr-triggers-2026-01-30`, signed in as Joshua. Then verify with `GET /v1/code/triggers/<trig_id>`: `enabled:false` and no new `cowork-scheduled` session for that title at the next cron slot.
- **Not proven by a live test in this session.** I tried to make a throwaway cloud trigger so the PATCH could be tested on it. Claude's auto-mode safety check blocked creating it ("Unauthorized Persistence"), and I did not retry. The local test task (`zz-cloudtest-timestamp`, every 10 min, Write-only) ran 7 times locally 12:02–13:02 and was **never** moved by the sweep, so there was no app-made cloud copy to test on either. The task is now deleted. Its files are in `fleet/state/cloudtest/run-*.txt`. The `update_scheduled_task` call was never used on a real task.
- **Who can run the switch-off:** (a) Joshua approves the browser API call above once per trigger (or per batch) in a session. (b) A cloud Cowork session that has the `Claude_Code_Remote` trigger tool (`update` action, `enabled:false`). (c) Unverified: a toggle in the desktop app's Scheduled sidebar. **First live use should be on an R-class trigger** (e.g. `nrf-riseup-approval-watch` trig_0153NrUPEY4Ks41yNjzgEFjT, hourly, harmless to stop). Confirm the next hourly slot produces no session, then use it fleet-wide.
- **Don't delete the local task to "kill" the cloud copy.** Whether deleting the local row also removes the trigger is untested. Disabling the trigger is the reversible path.
- Trigger IDs for every cloud copy are in the `migratedToRemote.triggerId` field of the registry snapshot and in section 3 (column "Runs where now" = C).

### 2.5 Trigger IDs of the 48 cloud copies (all enabled:true at 12:33 ET)
| task | trigger |
|---|---|
| `asset-recovery-daily-refresh` | `trig_014PS7pZqihrdybSZZ8q6ZPP` |
| `bald-rock-15-day-contract` | `trig_01TfdYKoTp7fAi5VTifhCjrX` |
| `bald-rock-guest-reviews` | `trig_01GP5XyBvV1axBqdzed9tWu8` |
| `bonus-paid-verify` | `trig_01V7GZeEsh6XcweUG2s6iFPV` |
| `ceo-weekly-scorecard` | `trig_01856nWC7RsCas5P5LXqt7Rk` |
| `chekkit-new-review-alert` | `trig_014exmyAWq1GgZNRHU1HonXD` |
| `chekkit-smart-replies-weekly-check` | `trig_019hXx7ZqvgVMEBnnnuUV3Uy` |
| `chekkit-unanswered-alert` | `trig_016fRstAx3ySdNen1QUGaNr3` |
| `chekkit-unanswered-eod-followup` | `trig_01TkmNGjoAY1bk9uoS7vtFNq` |
| `connector-health-daily` | `trig_01CzbLTtMwnq5FTaiWkbzmEX` |
| `daily-clockin-check` | `trig_01XtvNrnsuiFkfP2NhUCpcBN` |
| `daily-cloudcover-check` | `trig_017ef3AnQBKcnqSdKUztYWLA` |
| `daily-dress-code-check` | `trig_01B9QqCVv6Dc9G8xnVfDhzaE` |
| `daily-store-audit-digest` | `trig_013pZSiLfkYW3MjrJbWhBtha` |
| `ebay-weekly-channel-audit` | `trig_01SK1GpYNeXBW4K1VDhgtRM4` |
| `fleet-guardian` | `trig_01VdqzHNkgwAGjQBXi9vLqFQ` |
| `fortis-email-monitor` | `trig_01Pn1EMuCY4JpeLP45fHLxTP` |
| `gdrive-cache-refresh` | `trig_01AXwYKos3ziujKZzdBpePDG` |
| `health-weekly-digest` | `trig_01EDyLrJ31mUQuyouHrrAUnW` |
| `hiring-inbox-watch` | `trig_01KAJ8yYRM2see7NB3UJQhRy` |
| `insurance-inbox-watch` | `trig_01KBTnaVAoJbJJpYytdKH2wU` |
| `insurance-renewal-runner` | `trig_011v6szW3SbBXX1NuR5jCSn5` |
| `jewelry-onhand-catchup` | `trig_013aQGcjJYLdEHMMuarXD8HC` |
| `jewelry-onhand-nightly-pull` | `trig_01VvvttPGf7VTqK6thQhf36m` |
| `marketing-ceo-briefing-weekly` | `trig_019VgDDaBme57uZmh3jrKz6z` |
| `monday-bravo-cell-gapfill` | `trig_01MoiwXW76pFej73eT1G2zPV` |
| `monday-bravo-combined-compile` | `trig_018He1SGinYgMjvop7i5wc4j` |
| `monday-bravo-combined-run` | `trig_01LaNukN5az4k7ZdQ3xWcE2f` |
| `monday-bravo-postcheck` | `trig_01JmQFpapytm2YBzm4L4odXv` |
| `monthly-mobilepawn-participation` | `trig_01EpKGukgYQGjQtr9RbWi2Tm` |
| `monthly-publication-audit` | `trig_01SRcLQmJuuPDcKZvNVyrWS1` |
| `morning-brief` | `trig_01J21WFoeW4GUr3joWt5kbjB` |
| `northwest-registered-agent-daily-check` | `trig_01KpsKHMBUSfTZ4hzZSyNJB9` |
| `nrf-riseup-approval-watch` | `trig_0153NrUPEY4Ks41yNjzgEFjT` |
| `precious-metals-settlement-handler` | `trig_01PkENxRfwEctPtxmiw7EnFP` |
| `roster-refresh` | `trig_01Twt4LVZFosX9yDZA25Nyyp` |
| `scrap-monthly-bravo-approval-watch` | `trig_0175bSLFRwZntmCJ5AchCQee` |
| `scrap-monthly-bravo-manifest-stage` | `trig_01CoWCPHiohV7z3UQ4d7ae7b` |
| `vp-dashboard-refresh` | `trig_01PWjbKfQnVZ9GrLaL8xdmjd` |
| `vp-publer-analytics-friday` | `trig_01WuT7dJKNpnr6n6ThSFdwiT` |
| `vp-staff-video-chase` | `trig_01CuAPxpHxPhu3uDchTBSE6X` |
| `vp-staff-video-prompt` | `trig_01Rqc9ubJWhXhmQDboLJ4NUu` |
| `vp-thursday-email-watchdog` | `trig_011jrCeDwbE8RcbFP8p45Gas` |
| `vp-website-shop-nightly` | `trig_01Dmc694iuSNDUdb5UKpw98s` |
| `vp-website-shop-weekly-report` | `trig_01DLBZetJVk3SbdWkjvAdeB2` |
| `vp-website-trend-daily-refresh` | `trig_01EYXSLfRchsXNh3oWDTNzsP` |
| `weekly-returns-summary` | `trig_01WX1bCmVBNjQLpcWt726Utd` |
| `weekly-website-health-audit` | `trig_01XiuHftN4rqVWz3RWQPpk1b` |

## 3. Classified inventory (98 recurring tasks)

Where: C = cloud copy only (local row disabled by the move), C+L = both enabled (runs twice), L = local only. Class key: M mechanical Python · A needs Claude via bin/vp_ai.py · B website without API (Playwright + dedicated logged-in Chrome profile) · API usable API · H needs Joshua · R retire. Wave: 1 daily team-facing · 2 daily internal + weekly · 3 monthly · 4 quarterly/annual · R retire · H supervised.

| # | Task | Runs where now | Cadence (ET) | Output | Class | Credentials / notes | Wave |
|---|---|---|---|---|---|---|---|
| 1 | `chekkit-new-review-alert` | C | hourly :10, 09-21 daily | #google-reviews | **API** | Chekkit API (reviews) + Slack bot | 1 |
| 2 | `chekkit-unanswered-alert` | C | 08:00 Mon-Sat | #chekkit-messages-missed + store-employee DMs | **API** | Chekkit API (Keychain vp-chekkit-token-<STORE>, bin/chekkit_api.py) + Slack bot; logic is counting/hours math | 1 |
| 3 | `chekkit-unanswered-eod-followup` | C | 19:00 Mon-Sat | #chekkit-unanswered-summary | **API** | Chekkit API + Slack bot | 1 |
| 4 | `daily-clockin-check` | C | 10:15 Mon-Sat | #general | **API** | Gusto: NO token on the Mac today (only the claude.ai connector + Chrome). Needs a Gusto API/partner token or falls back to B | 1 |
| 5 | `daily-cloudcover-check` | C | 10:25 Mon-Sat | #general | **B** | Pandora CloudCover portal, no API. Cloud copy already failing (no post 10/7) | 1 |
| 6 | `daily-dress-code-check` | C+L | 10:30 Mon-Sat | #general | **B** | Google Home camera stills (Playwright, passkey-guarded fullcirclepawn@gmail.com profile) + vision via vp_ai. Both copies enabled; cloud copy blocked | 1 |
| 7 | `daily-store-audit-digest` | C | 09:40 Mon-Sat | outbox to Joshua (Preston later) | **M** | bin/daily_audit_digest.py already deterministic; task is a wrapper | 1 |
| 8 | `hiring-inbox-watch` | C | 10/12/14/16/18 Mon-Sat | DM Preston; Gmail label HiringLogged | **A** | No Gmail API token on the Mac (Google token = Sheets only). Read via Apple Mail Envelope Index (mail-brief pattern) + vp_ai parse; labelling needs Gmail scope | 1 |
| 9 | `jewelry-onhand-catchup` | C | 07:45 Tue-Sun | #jewlery-counts (self-heal) | **M** | Fold into the same native jewelry job (catch-up mode) | 1 |
| 10 | `jewelry-onhand-nightly-pull` | C | 20:30 Mon-Sat | #jewlery-counts | **M** | Bravo trigger pipeline (bravo_pull.sh) + Slack bot history of #end-of-day count sheets; if sheets are photos, vp_ai vision for that step | 1 |
| 11 | `northwest-registered-agent-daily-check` | C+L | 08:40 daily | #registered-agent + Drive filing | **B** | Northwest portal + SMS code (native sms_code_relay already exists). Both copies enabled; cloud copy blocked | 1 |
| 12 | `roster-refresh` | C | 06:15 daily | hr/ROSTER.json (no messages) | **API** | Gusto (no token yet) + Slack bot users:read; roster_write.py already validates | 1 |
| 13 | `vp-website-shop-nightly` | C | 07:00 + 15:00 daily | #website (launcher/verifier only) | **M** | Native shop_refresh.py + staged fleet/com.valleypawn.shop-refresh.plist - just install it | 1 |
| 14 | `asset-recovery-daily-refresh` | C | 19:15 daily | Asset Recovery artifact | **M** | Reads EOM CSVs; publish to the dashboard instead of a Claude artifact | 2 |
| 15 | `bonus-paid-verify` | C | Mon 10:00 (after payday) | DM only on mismatch | **API** | Gusto payroll (no token yet) vs bonus ledger - arithmetic | 2 |
| 16 | `ceo-weekly-scorecard` | C | Mon 12:15 | DM one-pager | **A** | Reads published Slack output; vp_ai writing | 2 |
| 17 | `ebay-weekly-channel-audit` | C | Mon 11:45 | #ebay-performance | **API** | eBay tokens in ~/.vp_secrets (ebay_store_tokens / analytics) | 2 |
| 18 | `gdrive-cache-refresh` | C | 03:00 daily | Unified Search gdrive cache | **M** | Read the Google Drive for desktop folder (~/Library/CloudStorage/GoogleDrive-jdavis@...) instead of the Drive connector | 2 |
| 19 | `gusto-keep-alive` | L | every 15 min | keeps Gusto Chrome session warm | **B** | Only exists because Gusto is driven by browser; retire once Gusto has an API path | 2 |
| 20 | `health-weekly-digest` | C | Sun 09:00 | DM Joshua | **A** | Local health DB (Oura import is native) + vp_ai | 2 |
| 21 | `insurance-inbox-watch` | C | 06:44 daily | registry + broker nudges | **A** | Apple Mail read + vp_ai; nudges are outbound email -> keep as drafts for Joshua (H for the send) | 2 |
| 22 | `marketing-ceo-briefing-weekly` | C | Mon 11:30 | DM + rolling artifact | **A** | Rolls up existing lane audits; vp_ai summary | 2 |
| 23 | `monday-bravo-cell-gapfill` | C | Sun 20:30 | native gap-fill runner (silent) | **M** | Already a launcher for a native runner - give it a plist | 2 |
| 24 | `monday-bravo-combined-compile` | C | Mon 08:00 | 5 ops channels | **M** | Native monday-compile covers all but #store-performance rankings (store_rankings.py exists) - finish that, then retire | 2 |
| 25 | `morning-brief` | C | 08:00 Mon-Fri | HTML artifact | **A** | Calendar/Gmail: use Apple Calendar + Mail locally (no Google Gmail/Calendar token); vp_ai | 2 |
| 26 | `precious-metals-settlement-handler` | C | 09:00 daily | REVIEW workbook (silent no-op) | **M** | Elemetal emails via Apple Mail (no Gmail API) + Bravo scrap CSVs; allocation is arithmetic | 2 |
| 27 | `sunday-checklist-summary` | L | Sun 20:00 | Apple Reminders TODOs | **A** | Slack bot history of #in-store-checklists + vp_ai + osascript Reminders (native-only capability) | 2 |
| 28 | `tuesday-supply-prep` | L | Tue 08:00 | DM Joshua the priced list | **B** | Slack #supply-request (bot) + Amazon Business pricing (Playwright, logged-in profile) + vp_ai item matching | 2 |
| 29 | `valley-pawn-blog-publisher` | L | Mon + Thu 01:30 | new blog post on thevalleypawn.com | **A** | vp_ai writes; WP REST (vp-wp-app-password); native blog-announce already posts the announcement | 2 |
| 30 | `vp-ai-search-health-check` | L | Mon 06:10 | #ai-marketing | **M** | Fetch schema/llms.txt + compare NAP; Bing/Google NAP pages may need Playwright | 2 |
| 31 | `vp-dashboard-refresh` | C | 08:15 + 19:15 daily | vp-dashboard.pages.dev | **M** | Slack bot history + Cloudflare deploy (wrangler token to confirm) | 2 |
| 32 | `vp-deal-of-week-monday-prompt` | L | Mon 08:10 | #deal-of-the-week prompt | **M** | Fixed post; 2 clean runs observed -> next in line to be auto-moved to cloud | 2 |
| 33 | `vp-deal-of-week-monday-reminder` | L | Mon 11:00 | #deal-of-the-week store pings | **M** | Slack bot history: who has not submitted; 2 clean runs -> at risk of cloud move | 2 |
| 34 | `vp-follower-growth-monthly-check` | L | Mon 09:50 | DM Joshua | **API** | Publer API | 2 |
| 35 | `vp-gusto-signature-chase` | L | Mon 09:05 | #policy-announcements + DM | **B** | Gusto documents page (browser) until a Gusto token exists | 2 |
| 36 | `vp-hiring-pipeline` | L | every 15 min 09-19 daily | Indeed screening/replies, interview booking, #employee-prospects | **B** | Indeed (no API) + Google Calendar; vp_ai for screening; candidate contact rules apply | 2 |
| 37 | `vp-publer-analytics-friday` | C | Fri 16:00 | DM + weekly-adjustments.json | **API** | Publer API (publer_config.json) | 2 |
| 38 | `vp-staff-video-chase` | C | Wed 11:15 | Slack chase + process video + Publer | **M** | Slack bot history + existing ffmpeg/Whisper/Publer pipeline (vp_publer.py) | 2 |
| 39 | `vp-staff-video-prompt` | C | Tue 09:10 | Slack prompt post | **M** | Fixed-text post via Slack bot | 2 |
| 40 | `vp-thursday-email-watchdog` | C | Thu 10:30 | Brevo self-heal | **API** | Brevo API key on Mac; check overlap with native brevo-watchdog/brevo-draft-guard before building (may be R) | 2 |
| 41 | `vp-website-shop-weekly-report` | C | Mon 07:40 | DM Joshua | **API** | WooCommerce/WP REST + GA4 (needs analytics scope) | 2 |
| 42 | `vp-website-trend-daily-refresh` | C | 00:45 daily | website-trend artifact | **API** | GA4: google-oauth-token.json has only spreadsheets scope - add analytics.readonly (google_grant.py exists) | 2 |
| 43 | `weekly-analytics-summary` | L | Mon 01:00 | #website | **API** | GA4 (+GSC) needs analytics scope; formatter format_weekly_website.py already deterministic | 2 |
| 44 | `weekly-returns-summary` | C | Mon 01:20 | #weekly-returns-summary + Returns_Trend.xlsx | **A** | Slack bot history of free-text #returns posts -> vp_ai extraction -> openpyxl | 2 |
| 45 | `weekly-timekeeping-analysis` | L | Mon 00:30 | #timekeeping-summary | **API** | Gusto time records (no token on Mac yet) | 2 |
| 46 | `weekly-website-health-audit` | C | Mon 05:15 | #website + WP auto-fixes | **M** | Crawl + WP REST (Keychain vp-wp-app-password) | 2 |
| 47 | `bald-rock-15-day-contract` | C | 04:00 daily | DocuSign contract + guest ID asks; DM Joshua | **B** | Airbnb/VRBO reservations (no API) + DocuSign (connector only on claude.ai; DocuSign API token would make it API); guest messages = H-adjacent | 3 |
| 48 | `bald-rock-guest-reviews` | C | 11:00 daily | Airbnb/VRBO host reviews | **B** | Host portals, no API; vp_ai writes the review | 3 |
| 49 | `bald-rock-monday-briefing` | L | Mon 04:15 | #airbnb | **B** | Guesty/Airbnb/VRBO data (portal) + vp_ai | 3 |
| 50 | `bonus-month-close` | L | 10th 09:00 | DM payout breakdown | **M** | bonus_engine.py; Chekkit API + Publer API inputs; payout itself H | 3 |
| 51 | `bonus-month-close-pull` | L | 1st 11:30 | DM Joshua draft targets | **M** | bonus_engine.py + one Bravo trigger | 3 |
| 52 | `ceo-monthly-scorecard` | L | 3rd 12:00 | DM one-pager | **A** | Reads published output; vp_ai | 3 |
| 53 | `ebay-campaign-chekkit-monthly` | L | Thu 11:00 (acts 3rd Thu) | Chekkit text campaign | **B** | Chekkit campaign upload is a website runbook; check if chekkit_api.py can create campaigns (then API). Customer-facing send | 3 |
| 54 | `entity-compliance-check` | L | 1st 09:00 | DM if action needed | **M** | Date math over ENTITY_COMPLIANCE_CALENDAR | 3 |
| 55 | `eom-bravo-gl-export` | L | 1st 06:00 | GL to Drive + QBO import | **API** | Bravo pipeline (M) + QBO API (Quickbooks Set UP/qbo_api.py, refreshed weekly) instead of Chrome import; books-tax gates apply | 3 |
| 56 | `eom-bravo-gl-export-watchdog` | L | 2nd 08:00 | DM if missing | **M** | File/QBO checks | 3 |
| 57 | `insurance-renewal-runner` | C | Mon 07:26 | registry walk; one decision to Joshua | **A** | Registry JSON + vp_ai; any quote/bind is H | 3 |
| 58 | `mobilepawn-app-social-monthly` | L | 20th 09:10 | Publer schedule (11 pages) | **API** | Publer API + vp_ai copy. Next fire 10/20 | 3 |
| 59 | `monthly-amazon-store-allocation` | L | 6th 09:00 | xlsx + DM | **B** | Amazon Business shipments report (Playwright download) then pure M | 3 |
| 60 | `monthly-analytics-report` | L | 1st 01:45 | #company-performance + Sheets | **M** | Prestage is already native (monthly-prestage) | 3 |
| 61 | `monthly-analytics-watchdog` | L | 1st 07:00 | DM if missing | **M** | Slack bot history | 3 |
| 62 | `monthly-bravo-user-audit` | L | 3rd 10:00 | audit | **M** | bin/bravo_user_audit.py exists | 3 |
| 63 | `monthly-ebay-ratings-sweep` | L | 1st 10:00 | #ebay-performance | **API** | Native ebay-ratings-pull already fetches; move the post into it | 3 |
| 64 | `monthly-employee-sales-rankings` | L | 1st 02:00 | #employee-performance + workbook | **M** | Bravo pipeline + existing formatter | 3 |
| 65 | `monthly-eom-recap` | L | 1st 10:30 | Month in Review per channel | **A** | Slack bot history + vp_ai | 3 |
| 66 | `monthly-gun-audit-report` | L | 16th 02:30 | #monthly-gun-audit + Trends sheet | **M** | Slack bot history of the 5 forms + gun_audit_format.py + Sheets token. Next fire 10/16 | 3 |
| 67 | `monthly-loan-layaway-outcomes` | L | 2nd 10:30 | outbox to Joshua | **M** | bin/loan_layaway_outcomes.py deterministic | 3 |
| 68 | `monthly-mobilepawn-participation` | C | 1st-3rd 09:15 | #mobilepawn-participation | **M** | bin/mobilepawn_monthly.py deterministic | 3 |
| 69 | `monthly-publication-audit` | C | 2nd + 4th 10:00 | DM if unrecoverable | **M** | Slack bot history vs PUBLICATION_CALENDAR.md | 3 |
| 70 | `monthly-scrap-rankings` | L | 1st 04:30 | #scrap-rankings | **M** | Bravo CSVs | 3 |
| 71 | `sales-tax-monthly-update` | L | 1st 08:00 | Sales Tax.xlsx | **M** | Reuses GL CSVs; openpyxl | 3 |
| 72 | `scrap-bucket-name-check` | L | 5th/15th/25th 10:15 | manager reminder | **M** | Bravo read via trigger pipeline + Slack bot. Next fire 10/15 | 3 |
| 73 | `scrap-monthly-bravo-approval-watch` | C | every 3 h | Bravo post on Joshua's 'post' | **M** | Slack bot reads his DM reply; hardened AHK handler already native; approval itself is H | 3 |
| 74 | `scrap-monthly-bravo-manifest-stage` | C | 1st-5th 09:45 | approval DM | **M** | Elemetal emails via Apple Mail + Bravo read; Joshua approves (H step stays) | 3 |
| 75 | `vp-ai-visibility-metrics` | L | Fri 06:30 | #ai-marketing + tracker sheet | **A** | Prompt tests across AI engines (APIs for each would be needed) + GA4 scope; Sheets token exists | 3 |
| 76 | `vp-comms-drift-monthly-check` | L | 3rd 08:00 | DM digest | **A** | Slack bot history + vp_ai vs Field Communication Standard | 3 |
| 77 | `vp-hr-policy-monthly-sync` | L | 1st 08:35 | P&P/Handbook edits | **A** | Slack bot history + vp_ai drafting; doc edits stay reviewable | 3 |
| 78 | `vp-new-customer-report` | L | 3rd 07:00 | #new-customers + artifact | **M** | Pipeline chekkit-invites-range cell | 3 |
| 79 | `vp-presence-audit-weekly` | L | Sun 16:20 | presence audit | **B** | Directory/listing pages (Bing/Yelp/Apple) - Playwright; BrightLocal export may make it API | 3 |
| 80 | `vsp-nics-fee-monthly` | L | 5th 10:15 | stage payments; Joshua clicks Pay | **H** | Browser login (lockout risk) and payment = Joshua; Playwright can stage, never pay | 3 |
| 81 | `yield-by-asset-class-monthly` | L | 6th 14:00 | Yield artifact | **M** | EOM exports + regression harness | 3 |
| 82 | `annual-board-review` | L | Jan 1 | board deck to Drive | **A** | vp_ai + python-pptx | 4 |
| 83 | `insurance-coverage-audit` | L | 1st Jan/Apr/Jul/Oct | coverage findings | **A** | Registry + Bravo/Gusto numbers + vp_ai | 4 |
| 84 | `quarterly-capex-sweep` | L | 1st Jan/Apr/Jul/Oct | CAP GAIN trackers | **A** | Drive-for-desktop + iCloud folders local; vp_ai to read docs | 4 |
| 85 | `vp-creative-refresh-quarterly` | L | 1st Jan/Apr/Jul/Oct | creative ledger | **A** | vp_ai | 4 |
| 86 | `vp-hr-compliance-quarterly-review` | L | 2nd Jan/Apr/Jul/Oct | compliance review | **A** | vp_ai (legal review stays advisory) | 4 |
| 87 | `chekkit-smart-replies-weekly-check` | C | 18:30 daily | DM Joshua | **R** | Smart Replies folders were deleted 10/1 at Joshua's direction (OPEN_ITEMS) - checks something that no longer exists | R |
| 88 | `connector-health-daily` | C | 05:40 daily | failure ledger | **R** | Probes claude.ai connectors - irrelevant once off Cowork; replace with a native token-expiry check | R |
| 89 | `daily-supply-order` | L | Tue 03:15 | order data (no cart) | **R** | Overlaps tuesday-supply-prep; checkout task already disabled - merge into one Tuesday job | R |
| 90 | `fleet-guardian` | C | 12:45 + 21:45 | DM Joshua | **R** | Its job (re-run missed Cowork tasks) disappears with Cowork; native fleet-doctor + registry-guard already exist | R |
| 91 | `monday-bravo-combined-run` | C | Sun 18:00 | Bravo triggers | **R** | Replaced by native com.valleypawn.monday-pull (CHANGELOG 9/30: confirmed obsolete). Cloud copy still ON = duplicate pull | R |
| 92 | `monday-bravo-postcheck` | C | Mon 08:30 | backfill | **R** | Native monday-compile de-dupes and fills gaps | R |
| 93 | `monthly-capability-drift-audit` | L | 1st 07:40 | Slack deltas | **R** | Diffs Cowork tools/tasks - obsolete after migration | R |
| 94 | `nrf-riseup-approval-watch` | C | hourly 08-19 Mon-Sat | DM Joshua once | **R** | Approval already received; re-sending the same DM every ~2 h (CHANGELOG 10/7 noise) | R |
| 95 | `scheduled-task-model-audit-weekly` | L | Mon 05:00 | model pin log | **R** | Cowork-only housekeeping | R |
| 96 | `task-hygiene-sweep` | L | 1st 04:00 | deletes stale Cowork tasks | **R** | Cowork-only housekeeping | R |
| 97 | `tuesday-supply-summary` | L | Tue 10:50 | DM Joshua / auto-approve | **R** | Same overlap; approval is H anyway | R |
| 98 | `fortis-email-monitor` | C | 09/13/17 Mon-Fri | acts on Fortis replies, nudges | **H** | Vendor correspondence on Joshua's behalf; self-retires when 4 items done - leave as a supervised one-off | H |
One-offs (not recurring, not counted): `mobilepawn-bravo-reply-check` (L, 10/22), `gun-safety-cert-followup-20261015` (L, 10/15), cloud reminders `Build PM loan growth Bravo report` (trig_01SUmrWWBr…, 10/7 20:00 ET) and `Follow up: July TPA + Guideline docs` (trig_01HMFwYTwR…, 10/8 10:00 ET). Also not counted: the two cloud-only Gusto tasks created 10/7 ~12:00 (section 1).

## 4. Credentials already on the Mac (names only, no values read)
| System | Where | Good for |
|---|---|---|
| Slack bot "VP Ops Engine" | Keychain `vp-ops-slack-bot-token` (bin/vp_slack.py) | post, DM, read channel history, canvases. Scopes: users:read, chat:write, im:write, channels:history, groups:history, files:read, canvases:read/write. **No search scope**, so history reads only, and the bot must be a member of each private channel |
| Anthropic API | Keychain `vp-agent-anthropic-key` (bin/vp_ai.py; also ~/.vp_secrets/anthropic.json) | every class-A step (writing, judgment, vision) |
| Chekkit | Keychain `vp-chekkit-token-<STORE>` (bin/chekkit_api.py) | messages, reviews, invites (used by native chekkit-ai-responder) |
| Brevo | ~/.config/valley-pawn/brevo_api_key | email campaigns, contacts |
| Publer | Refine Social Media/publer_config.json (bin/vp_publer.py) | posts, analytics |
| eBay | ~/.vp_secrets/ebay_store_tokens.py, ebay_oauth_tokens.py, ebay_analytics_oauth.json | Trading + Analytics APIs, all 5 stores |
| QuickBooks Online | Quickbooks Set UP/qbo_api.py tokens (native qbo-token-refresh keeps them alive) | GL import, reports. Books-tax gates still apply |
| WordPress | Keychain `vp-wp-app-password` | thevalleypawn.com REST |
| Zoom Phone | ~/.vp_secrets/zoom_s2s.json | missed calls (already native) |
| Google | ~/.config/valley-pawn/google-oauth-token.json, **scopes = spreadsheets only** (10/2 check) | Sheets. GA4, Search Console, Gmail, Drive and Calendar need a re-grant (Website/analytics/bin/google_grant.py) |
| Meta pages | facebook-post skill data/tokens.json; Refine Social Media/tokens.json | page posts |
| **Missing** | Gusto (claude.ai connector + Chrome only), Gmail/Calendar (connector only; Apple Mail Envelope Index is readable natively, see mail-brief), DocuSign (connector only), Indeed / Airbnb / VRBO / Guesty / CloudCover / Northwest / Amazon Business / Google Home (no API, so Playwright) | |

Getting a **Gusto API token** (developer app + OAuth for the company) unlocks 5 tasks (clock-in, roster, timekeeping, bonus-paid-verify, signature-chase) and retires gusto-keep-alive plus the two new Gusto cloud tasks. Adding **analytics.readonly + webmasters.readonly** to the Google token unlocks 4 (website trend, weekly analytics, shop weekly report, AI-visibility GA4 part). Adding **gmail.modify** removes the Apple-Mail workaround for hiring/insurance/precious-metals.

## 5. Recommended waves

Each conversion follows the proven pattern: build `bin/<job>.py` (+ `.sh`), shadow-render against the channel's last real post (`bin/parity_check.py`), install the plist via the host queue, let it run once beside the Cowork copy (native jobs de-dupe against the channel), then **switch the cloud copy off with the trigger PATCH (section 2.4)** and leave the local row disabled. Never leave a converted task with an enabled trigger.

**Wave 0 — today/tomorrow, no building (switch-offs only, needs Joshua's OK per task):**
- Turn off cloud copies of R-class tasks that are already replaced or obsolete: `monday-bravo-combined-run` and `monday-bravo-postcheck` (native monday-pull/compile own them), `nrf-riseup-approval-watch` (approval received, duplicate DMs), `chekkit-smart-replies-weekly-check` (feature deleted 10/1).
- Pick ONE copy for `northwest-registered-agent-daily-check` and `daily-dress-code-check`. Both run twice now. Keep local (cloud can't log in), so turn the cloud trigger off.
- Pre-empt the next auto-moves: convert or watch `vp-deal-of-week-monday-prompt`/`-reminder` before Mon 10/12.

**Wave 1 — daily, team-facing (13):** the chekkit trio, daily-store-audit-digest, shop-nightly (just install the staged plist), jewelry pull + catch-up, roster, clock-in, cloudcover, northwest, dress-code, hiring-inbox-watch.

**Wave 2 — daily internal + weekly (33),** Monday team-facing first: monday compile store-rankings gap, deal-of-week prompt/reminder, staff-video prompt/chase, returns summary, timekeeping, weekly analytics, website health; then the Joshua-only weeklies (CEO/marketing briefings, health digest, Publer/eBay audits, follower growth) and dailies (dashboard, asset recovery, trend refresh, gdrive cache, precious metals, insurance inbox, hiring pipeline, supply prep).

**Wave 3 — monthly (35):** must be live before **11/1** (most monthlies fire 11/1–11/6). Earlier fires: scrap-bucket-name-check + ebay-campaign-chekkit 10/15, monthly-gun-audit-report 10/16, mobilepawn-app-social 10/20. Most of the 1st-of-month set is M around existing deterministic scripts.

**Wave 4 — quarterly/annual (5):** next fire 1/1–1/2/2027. Lowest urgency.

**Retire (11):** listed with class R. For each, turn off the cloud trigger (if any) and leave the local row disabled.

## 6. Top 15 conversions, in order
1. `chekkit-unanswered-alert` (API) — daily 08:00, store DMs. Already double-posted once (10/7).
2. `chekkit-unanswered-eod-followup` (API) — same code path, 19:00.
3. `chekkit-new-review-alert` (API) — hourly, #google-reviews.
4. `daily-store-audit-digest` (M) — wrapper around daily_audit_digest.py; trivial.
5. `vp-website-shop-nightly` (M) — install staged com.valleypawn.shop-refresh.plist, then turn off the trigger.
6. `jewelry-onhand-nightly-pull` + `jewelry-onhand-catchup` (M) — one native job, two modes.
7. `roster-refresh` (API: Gusto token) — every staff-facing job reads ROSTER.json.
8. `daily-clockin-check` (API: Gusto token; B fallback) — #general 10:15.
9. `northwest-registered-agent-daily-check` (B) — Playwright + existing sms_code_relay; removes the double run.
10. `daily-cloudcover-check` (B) — cloud copy can't do it at all today.
11. `daily-dress-code-check` (B + vision) — needs a dedicated logged-in Chrome profile (passkey once by Joshua).
12. `hiring-inbox-watch` (A) — Apple Mail read + vp_ai parse → Preston DM (or Gmail scope).
13. `vp-deal-of-week-monday-prompt` + `-reminder` (M) — before Mon 10/12 auto-move.
14. `monday-bravo-combined-compile` (M) — add store rankings to native monday_compile.py, then retire the Cowork compile.
15. `weekly-returns-summary` (A) — Mon 01:20, team channel.

## 7. Open questions / unknowns
- The exact rule the sweep uses to pick tasks (observed: zero local-tool use plus at least 2 runs; not every eligible task moved on 10/6, and the test task did not move within ~50 min of its 2nd run).
- Whether the app's sweep would **re-create** a trigger for a task whose trigger was disabled by hand. It hasn't so far: the 8/21 disabled holds have stayed disabled.
- The two new Gusto cloud tasks (created 10/7 ~12:00 by another session) overlap `gusto-keep-alive` (local, */15) and `vp-gusto-signature-chase` (local, Mon). Needs a decision.
