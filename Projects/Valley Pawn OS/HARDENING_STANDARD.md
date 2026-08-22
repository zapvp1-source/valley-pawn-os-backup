# Fleet Hardening Standard — Valley Pawn / Full Circle Finance
**Created 2026-08-21 per Joshua's directive:** "Tasks should be hardened and reliable... iterations can't be to explain failure but to overcome it."

The goal state: **zero maintenance**. A failure that a session merely *explains* is an unfinished job. Every failure must be either (a) automatically recovered, or (b) impossible by design. Joshua hears about a failure only when recovery itself failed AND a decision only he can make is blocking.

---

## The 6 requirements — every scheduled task MUST meet all of them

Every NEW task is built with all 6 from day one. Every EXISTING task gets upgraded to all 6 **the first time any session touches it for any reason** (fix, edit, review — no separate migration project; the fleet converges organically). Additive-only rules still apply: upgrade means adding these blocks, never rewriting working logic.

1. **Access fallback (no approval-click dependencies).** Never depend on `request_cowork_directory` succeeding — in a scheduled run there is no one to click approve. All host file access must work via the osascript shell (`do shell script`) as primary or fallback. (Codified in `enterprise-map` STEP -1, 2026-08-21.)

2. **Self-verify output before exiting (Rule 12 applied to self).** After doing the work, the task READS ITS OWN OUTPUT — the Slack message it just posted, the file it just wrote, the row it just added — and confirms it exists and is sane (row counts, date stamps, non-empty). A run that can't confirm its output treats itself as failed and proceeds to #3, not to a clean exit. This kills the "silent success-failure" class (timekeeping 8/10+8/17, google-reviews 8/17, PART1 8/10).

3. **Retry once, differently.** On any step failure: retry the step once. If the same path fails twice, try the documented alternate path (MCP↔Chrome, direct login vs SSO, cached data vs live pull) before declaring failure. Known alternates get written INTO the SKILL.md as they're discovered (e.g. Guesty email/password vs Google SSO, Gusto MCP vs Chrome scrape).

4. **Catch-up on missed windows.** Every recurring task, on every run, checks whether its PREVIOUS expected run(s) actually produced output (read the channel/file, not lastRunAt). If missed and the data is still recoverable, back-fill up to 3 missed periods before doing today's work. Duplicate-guard first: never re-post what's already in-channel. (Pattern proven: jewelry-onhand-catchup, timekeeping v3, google-reviews watchdog.)

5. **Duplicate guard on every external write.** Before any Slack post, email, publish, or record creation: check whether it already exists (channel scan, sent-mail check, register/log check). Makes every task safe to re-run — which is what makes #4 and the Fleet Guardian possible.

6. **Standard failure alerting (policy v2).** Only after #3 and #4 are exhausted: ONE plain-language DM to Joshua (D03BHQH5VGT), nothing technical, full detail to the run log/STATUS file. Never to any team channel or employee. Silence on success.

## Date discipline (the PART1/PART2 lesson)
Any task that writes files another task reads must stamp them with the PIPELINE date (the business date the data covers), and every consumer must look up by that same convention — never "today at my own run time." Cross-task file handoffs state the date convention explicitly in BOTH SKILL.md files.

## No new per-task watchdogs
The watchdog-per-task pattern (jewelry-pull-watchdog, google-reviews-post-watchdog, funds-verification-watchdog, monday-bravo-postcheck...) does not scale — it doubles the fleet. Existing watchdogs stay (hardened infra), but NEW coverage comes from requirement #2/#4 inside the task itself plus the **Fleet Guardian** (below). Do not create new standalone watchdog tasks without a specific reason the guardian can't cover.

## The Fleet Guardian
`fleet-guardian` (scheduled task, 12:45 PM + 9:45 PM ET daily) is the single fleet-wide recovery layer:
- Reads the scheduler registry, computes which enabled tasks MISSED their most recent scheduled fire (lastRunAt earlier than the last cron occurrence).
- **Output-verification pass (Step 1b, added 2026-08-21):** also reads `fleet/expected_outputs.json` and verifies each listed task's ACTUAL output (Slack marker string in its destination channel within the expected window). A task whose run record looks healthy but whose output is absent is treated as missed — this catches the silent-mid-run-death class (the one that kept the weekly Brevo emails dark 3 weeks) that lastRunAt-based detection structurally cannot see. Manifest is additive-only and converges to fleet coverage the same way the 6 requirements do: every verified touch adds an entry.
- For missed tasks marked **rerun-safe** in `Valley Pawn OS/fleet/rerun_manifest.json`: executes the task's own SKILL.md instructions in-session, immediately, honoring the task's duplicate guards. Cap: 5 reruns per guardian run (cost bound); remainder queue to the next guardian run.
- For missed tasks marked **verify-only** (external messaging, publishing, money, HR, Bravo-driving): never auto-rerun. Logged, and included in the digest DM only if nothing else already covered them.
- One digest DM to Joshua ONLY when something could not be recovered. Fully silent otherwise.
- Run log: `Valley Pawn OS/fleet/guardian_runs/`.

## Layer 0 — Fleet Health Sentinel (native, outside Claude entirely)
Added 2026-08-21 (PM), same day as the Guardian, by a parallel hardening session. The Guardian
has one blind spot it can never cover: **it is itself a Cowork scheduled task**, so it dies with
the app, the scheduler, the usage cap, or the Mac's login session — exactly the common-mode
failure that took the whole fleet dark 8/18–8/21. The sentinel is the layer beneath it:

- `Valley Pawn OS/bin/fleet_health_sentinel.py`, run by native launchd agent
  `com.valleypawn.fleet-health` via vp-runner — pure Python, ZERO Claude usage, immune to caps.
- Runs **13:30 + 22:30 daily — deliberately ~45 min AFTER each Guardian pass** (12:45/21:45), so
  its DM only fires for what the Guardian failed to recover, plus what the Guardian can't see:
  the Claude app being down, launchd agents failing/unloaded (caught + fixed
  dashboarddatacollector's post-reboot exit-78 the day it was built), skip-rate bursts, and a
  missing Bravo morning-pull certificate.
- Detect-and-DM only (via the vp-ops Slack bot, `conversations.open` to Joshua) — it never
  re-runs anything; recovery stays the Guardian's job. Per-occurrence dedup, silent when green.
- Rolling log: `Valley Pawn OS/FLEET_HEALTH.md`; state: `.fleet_health_state.json`.

Division of labor: **Sentinel detects (always alive), Guardian recovers (when Claude is alive),
per-task requirements #2–#5 prevent (inside each run).** This is not a "new per-task watchdog" —
it's the fleet-wide outer detection ring the moratorium above assumes exists.

## Rerun-safety manifest
`Valley Pawn OS/fleet/rerun_manifest.json`. Default for any task not listed: **verify-only** (safe default). Classification rules:
- **rerun-safe:** reads files/APIs, posts internal Slack reports/refreshes with duplicate guards. No external humans contacted, no public publishing, no money, no Bravo UI driving.
- **verify-only:** anything that messages customers/applicants/employees/guests, publishes publicly (social, blog, website content changes, review responses), moves money or inventory records, touches HR, or drives the Bravo VM (contention risk — see `bravo-context`).
New tasks get classified at creation time; sessions editing a task re-check its row.

## Chrome Tab Hygiene (added 2026-08-21)

Chrome is shared infrastructure — dozens of tasks drive it daily and leftover tabs
compound into memory bloat and frozen renderers (see the 8/21 load-176 incident in
CHANGELOG). Three layers:

**Automatic layer (zero-Claude, Layer 0):** native agent `com.valleypawn.chrome-tab-hygiene`,
daily 5:10 AM (before the 6:30–8:15 Bravo corridor, collision-safe by schedule). Closes
automation-residue URLs (slack app_redirect, oauth/signin leftovers, about:blank,
new-tab pages, chrome-error) and exact-duplicate tabs. Never closes the active tab of
any window; the duplicate rule keeps the leftmost copy so pinned tabs survive (Chrome's
AppleScript API can't see "pinned" — leftmost-wins is the safe proxy). Only residue and
duplicates are ever closed — unique real tabs are never touched regardless of count
(>80 after cleanup logs a WARN instead). Script: `Valley Pawn OS/bin/chrome_tab_hygiene.sh`
(canonical); the runtime copy launchd actually executes lives at
`~/Library/Application Support/valleypawn/bin/chrome_tab_hygiene.sh` because TCC blocks
launchd exec under ~/Documents (unified-search lesson). KEEP BOTH IN SYNC when editing.
Log: `~/Library/Logs/valleypawn/chrome-tab-hygiene.log`. Verified live 8/21 (launchd
kickstart closed a real duplicate, no TCC/Automation block).

**Policy layer:** Chrome managed policies set via `defaults write com.google.Chrome`:
`HighEfficiencyModeEnabled=true` (Memory Saver — background tabs release memory
automatically) and `TabDiscardingExceptions` = slack.com, *.slack.com, thevalleypawn.com,
*.thevalleypawn.com, localhost (automation-critical tabs never discarded mid-flow).
Chrome shows these two settings as "managed" — expected, not malware. Applies on
Chrome's periodic policy refresh or next restart.

**Task-authoring rule (opportunistic, like the 6 requirements above):** any task that
opens Chrome tabs closes what it opened before its run ends, unless the tab IS the
deliverable. Apply whenever a Chrome-driving task is touched — no big-bang rewrite.
