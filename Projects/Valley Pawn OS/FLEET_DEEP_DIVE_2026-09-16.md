# Fleet Deep Dive — why the back office has never completed a clean week, and the plan to make it one that just works

**Date:** 2026-09-16 (Wed) · **Requested by:** Joshua — "deep dive, no shortcuts, read everything, don't do anything, what's the plan"
**Method:** enterprise-map load → CHANGELOG (all Sep entries + 9/4 root-cause entries), BUSINESS_OS live state, FLEET_HEALTH.md (native sentinel), DISK_HEALTH.md, FAILURE_LEDGER, HUMAN_QUEUE, guardian run JSONs, PUBLICATION_CALENDAR, both existing plans (SCHEDULED_TASK_RELIABILITY_PLAN 9/4, REPORTING_ANALYTICS_PLAN 9/5), DUPLICATE_TASK_AUDIT 9/10, Bravo pipeline output/results/logs, QBO write log, Sales Tax folder, Joshua's DM channel, and a read-only audit of 28 Slack channels for Sep 1–16 (every automation post, timed, quality-graded). Nothing was changed, posted, or sent. A separate interactive session ("Scheduled tasks sidebar issue") is fixing today's registry outage in parallel — this document deliberately does not touch that work.

---

## 1. What the field actually got (verified against Slack, not run records)

| Week | Publications expected | On time | Late (>2 h) | Never landed | Wrong / partial / duplicate |
|---|---|---|---|---|---|
| Sep 1–7 (incl. Mon 9/7 weeklies, 1st-of-month, 14 Month-in-Review) | 107 | 79 (74%) | 19 | 9 | 7 |
| Sep 8–14 (incl. Mon 9/14 weeklies) | 87 | 41 (47%) | 2 | 44 | 2 |
| Sep 15–16 (through Wed 2:30 PM) | 19 | 0 | 0 | 19 | 0 |

- **Monday 9/14: 0 of 15 weekly publications posted** (loan review, layaway review, aged inventory, store rankings, employee MTD, first-payment-default, timekeeping, returns, google reviews, website, social, FFL MTD, markdowns, layaway yield, canvases). The only Monday post anywhere was the native eBay webhook.
- **Nothing automated has posted in any staff channel since Fri 9/12 ~10:17 AM** except one native eBay webhook and the daily sales-tax failure DM.
- **Wed 9/10 morning** (the registry outage): funds, pawn walk, items-to-price, sold, discount, jewelry, chekkit PM all missed or caught up hours late.
- **August month-end:** of 12 monthly publications, 2 posted on time on 9/1 (FFL final, eBay ratings). Company analytics, employee FINAL, scrap rankings, new customers and all 14 Month-in-Review posts landed 9/5 between 1:38 PM and 5:44 PM — by hand-driven catch-up sessions, four days late. The FINAL employee ranking ranked the "Free1 Valley Pawn" house account as the #1 employee. #first-payment-default was withheld for the whole month (Culpeper cell failed every Monday in August). The August GL → QBO chain, due 9/1, posted 9/6 after Joshua's session dealt with the unposted 8/29 day — and created one duplicate journal entry that had to be deleted. Bonus targets were never posted to #bonus-goals (Sandi asked for them 9/7; the task is DM-only by design pending Joshua's post). The daily sales-tax sweep has failed with the identical error every day since 9/11 and has DM'd Joshua a technical error dump five days running.
- **Quality defects the field saw in 12 days:** the same Store Performance ranking posted twice on 9/7 (8:14 and 11:12, different data); duplicate 5-star review alerts (9/1, 9/8–9/9); an employee-performance post at 2 AM on 9/1 that had to be deleted after Walker asked "is that for the last 3 months?"; a FFL MTD post that said "Waynesboro's pull errored twice (inconclusive render)"; music-check posts with the wrong weekday in the header (9/3, 9/11); a #general post about "node/wrangler deploy… Gatekeeper/codesign"; a "silent failure… credential" line in #email-campiagns; an empty message in #new-customers. Ten-plus technical-jargon violations of Rule 16 in staff channels in 12 days, after three separate sweeps that were supposed to end them.

That is the "sporadic information when it works" Joshua described. The field cannot count on it, and the numbers say why: **the fleet has never had a clean week because it has never had a stable week.**

---

## 2. Why — the failure classes, ranked by blast radius (each verified, source cited)

### Class 0 — The whole back office runs inside one desktop chat app on one Mac, and that host is unhealthy
This is the class that erased 9/10 morning and everything since 9/12. Nothing above it matters until it is fixed.

1. **The scheduler only runs while Claude.app is open and the Mac is awake.** Jewelry counts were missed 8/18–8/20 simply because the app was closed at 8:30 PM (Bravo Data Extraction/STATUS.md). The `claude-keepalive` launchd agent that should relaunch the app has exited 126 on every run since at least 9/4 (FLEET_HEALTH, every entry) — the safety net has been broken the entire period.
2. **One `null` in `scheduled-tasks.json` makes the app load zero tasks.** 9/10 02:12–09:55 the entire fleet was dark for that reason (CHANGELOG 9/10). The sidebar went empty again today; FLEET_HEALTH shows the fleet effectively silent since Sun 9/13, with a burst of sessions dispatched Mon 9/14 00:06–06:55 that produced no output at all (bravo-morning-pull, business-os-daily-refresh, gdrive-cache, unified-search all show a 9/14 start time and nothing on disk). The exact cause of the 9/13–9/16 stretch is not yet verified — the app log is a protected path this session cannot read — and the parallel session is diagnosing it now. Whatever it turns out to be, the registry file is a single point of failure with no validator in front of it.
3. **The disk is full and iCloud is evicting the fleet's own files.** DISK_HEALTH: data volume 93–97% full since 9/4, 12 GiB free today. On 9/4, 27,352 files under ~/Documents/Claude were evicted, including 47 task SKILL.md files. "Resource deadlock avoided" (the eviction symptom) blocked HIRING_OUTREACH.md and the dashboard site on 9/10 (HUMAN_QUEUE), made HARDENING_STANDARD.md unreadable on 9/4, and is the nightly exit-1 of two launchd agents. Each new session also boots a Linux sandbox that needs disk. The durable fix ("Optimize Mac Storage" off, Keep Downloaded) has been on Joshua's list since 9/4 and is still open.
4. **Time was wrong by 19 days on 9/3** (VM clock drift; sandbox and osascript agreed with each other and were both wrong). One task now checks an external clock; the other 190 do not.
5. **Two Macs, one registry per Mac.** `list_scheduled_tasks` shows only the current machine's tasks (CHANGELOG 9/14). A session on the wrong Mac sees an empty fleet and can misdiagnose from there.
6. **Backups:** Time Machine had no destination 8/25–9/4; the GitHub OS backup's pack file is corrupt since 9/11 (HUMAN_QUEUE). The system that is supposed to be the back office currently has no verified restore path.

### Class 1 — Capacity: 167 enabled tasks on a hard limit of 3 concurrent sessions
- Verified in app logs on 9/4: `global_limit (active=3, limit=3)`, server-side, not adjustable. 8,428 queue-wait skips in the 8 days before 9/4; **9,565 in the 7 days to 9/12** (BUSINESS_OS live state) — it got worse after Phase 0, because the fleet kept growing: 147 enabled on 9/4 → 167 on 9/12; 58 tasks in May → 193 registered today.
- The slots are burned by pollers, not reports. `preston-interactive-assistant` was moved to every 5 minutes 7 AM–10 PM on 9/10 (≈180 dispatches/day on its own); zoom-voicemail-alert ≈33/day (and every one of its ~100 runs since 9/9 has failed on an expired Zoom login and written a ledger row); mail-brief-reply-executor ≈34/day; chekkit hourly; gusto every 2 h; indeed hourly; ask-handbook twice hourly. Roughly 300 poller dispatches a day compete with ~120 report dispatches for the same 3 slots. Reports due at 8 AM land at 11 AM, and downstream compiles run before upstream pulls exist.
- Long "babysitter" sessions hold a slot 40–80 min watching a shell script (jewelry, morning pull, gdrive, unified-search, Bald Rock). Phase 1 of the 9/4 plan (launch→exit→verify) was done for one of six.

### Class 2 — Unattended runs cannot approve anything, so they stall, die, or route around the rule
- A tool not pre-approved for a task → the run idles → the 30-minute reaper kills it before it can even write a failure row (bald-rock 9/4; 67 tasks had partial approvals; 697 approvals were bulk-added 9/4).
- Chrome-driving tasks stall on the permission card unless `skip_all_permission_checks` is set (set on 27 tasks 9/8; interactive sessions still lack it).
- The auto-mode classifier blocks, in unattended runs: credential reads (killed brevo-weekly-efficiency-audit and brevo-preflight-watchdog 9/11), SKILL.md edits (the fix for that block was itself blocked), form_input into Amazon (9/9), Gmail drafts (9/11), eBay writes (9/6), computer-use ("can't be approved during a scheduled run" — the 8/29 GL blocker 9/1), launchd plist edits, the verified-text script (9/11–9/12), and it is intermittent (same call denied then allowed). So a scheduled task frequently *cannot* self-heal by design.
- Today a session built `bin/host_queue_run.sh`: any script dropped into `fleet/host_queue/` is executed on the host by a launchd agent within minutes, with Joshua's full user privileges, outside every Cowork permission check. It is being used right now to relaunch the app and install another watchdog. It solves the stall problem and it also means an unattended session can run anything on the Mac. That is a decision for Joshua (Section 5), not a technical detail.

### Class 3 — Every number comes from driving one Bravo window in one VM
- 61% of pulls fully clean (Aug 6–Sep 5 audit); 45% of failures happen before the report handler even runs (Bravo not ready, login screen, EnsureStore); the Monday combined run drops one 30-cell trigger with no per-cell retry (10 of 30 cells failed 8/30).
- The VM wedged for 4+ hours on 9/10 and needed hands on the Parallels desktop; it blocked that night's cash and jewelry checks. The pipeline's last output of any kind is 9/12 06:53.
- The month-end GL chain (`post-to-accounting-*`) was 0/17 and 0/6 in the audit window. August was blocked for five days because one day (8/29) sat unposted in every store — a store-closing process gap, not an automation bug, and no automation can fix it.
- Bravo has no API (vendor in writing). The non-UI paths — Bravo's own scheduled emailed reports (live today, we only ever asked for one PDF) and Reporting Pro (~$85/store/mo, quoted March, never bought) — have been identified since 9/5 and not pursued because both need Joshua (vendor email / spend).

### Class 4 — Reports are typed out by the model, so "posted" does not mean "right"
- ~85 of ~90 reporting tasks still hand-render their Slack table each run (three converted to deterministic formatters on 9/5–9/6). That is the mechanism behind the $123,029 inventory balance posted as an aged total (8/31), the missing header rows, the broken code fences, the house account ranked #1, the wrong weekday labels, and the 9/7 double Store Performance post.
- Rule 18 (post nothing if incomplete) is correct but, combined with Class 3, it turns a failed cell into an empty channel with no explanation — the field sees silence and does not know whether to wait.
- Rule 16 (no jargon) is a prompt instruction repeated in ~190 files; it has been violated 10+ times in 12 days because a prompt cannot enforce it. Only a formatter can.

### Class 5 — The way the fleet is being operated is itself the biggest risk
- **Continuous change, no freeze, no proving week.** Between 9/4 and 9/11 the record shows: 697 tool approvals added; 7 cadences and 8 schedules changed; 190 SKILL.md files bulk-patched (9/8) after 107 were bulk-patched (8/21); 27 permission modes changed; 24+ guardian entries added; ~15 new tasks registered; five whole-department "fix what you can fix" rebuilds shipped in two days (9/5–9/6: eBay engine, social engine, website analytics, compliance OS, insurance OS, HR Phase 0, marketing umbrella); two registry outages; three one-shot launchd agents left loaded that would have quit the app nightly. Every one of those changes was individually reasonable. Together they mean the fleet has never run the same configuration for seven consecutive days, so "does it work" has never been measurable.
- **Watchdogs watching watchdogs.** There are now ~19 watchdog/guardian/sentinel/gap-fill/audit tasks and agents (fleet-guardian, fleet_health_sentinel, monday-bravo-postcheck, monday-bravo-cell-gapfill, monthly-publication-audit, monthly-analytics-watchdog, connector-health-daily, chrome-extension-watchdog, registry-guard (today), jewelry-pull-watchdog, funds-verification-watchdog, backup-health-watchdog, bravo-health-watchdog, eom-bravo-gl-export-watchdog, blog-publisher-watchdog, google-reviews-post-watchdog, brevo-preflight-watchdog, vp-content-batch-quota-watchdog, vp-thursday-email-watchdog). Each Cowork one is a session competing for the 3 slots; each has produced at least one false alarm or missed a real outage (the guardian is blind past 48 h; the sentinel's 90-minute grace means Joshua learns of a dead morning at lunch; the backup watchdog sent ten identical CRIT DMs then a false "offsite stalled" for six weeks).
- **Concurrent sessions collide.** Two sessions ran weekly-training-pipeline at once on 9/8 and overwrote each other's output; a shell-pipe error masked a QBO post on 9/6 and a duplicate journal entry was created; the 9/14 hiring session sent 19 messages mid-audit, 10 to people already contacted. There is no lock, no single owner, and no "one fleet session at a time" rule.
- **Context bloat slows and destabilizes every run.** enterprise-map tells every session to read CHANGELOG.md first; it is 617 KB. HIRING_OUTREACH.md is 929 KB. Sessions spend their first minutes and a large share of their budget reading history before doing the job, which lengthens slot occupancy and raises the odds of the reaper.
- **Diagnosis by inference has been the norm**, and the record says so: three confident wrong diagnoses 8/2, the false "offsite backup stalled" 7/24–9/4, the Continuous-Scrolling theory 8/3–8/4, the "long holds / abandoned calls" theory 9/7, the WordPress-keepalive theory 9/9, the Amazon pipeline "worked for months" 9/9. Rules 12, 17, 19 and 20 were each added after an incident. They are good rules; they are also evidence that the system is being run by trial and error at production scale.

---

## 3. The honest conclusion

The two existing plans (9/4 scheduler plan, 9/5 reporting plan) diagnosed Classes 1–4 correctly and their designs are sound. They did not work because:

1. Class 0 was treated as "four clicks for Joshua" and left open, so every fix was built on a host that keeps falling over.
2. Class 5 was never addressed — the plans were executed *alongside* a stream of other builds instead of under a freeze, so nothing was ever proven.
3. The response to unreliability has been to add automation (watchdogs, gap-fillers, catch-ups, more tasks) rather than remove load. The fleet grew 14% during the reliability effort.

A back office the field can count on needs the opposite: fewer moving parts, a host that stays up, deterministic output, one owner, and a measurable definition of "working" that must be met before anything is added back.

---

## 4. Expert board

🧑‍⚖️ EXPERT BOARD — how to get from "sporadic" to "it just works" without rebuilding from scratch

PANEL: SRE (capacity/host), release manager (change control), controller (the field must get correct numbers on time), desktop-automation engineer (Cowork permission model)

OPTIONS WEIGHED
- **Keep patching on the current trajectory** — for: every fix is individually cheap; against: six weeks of evidence that the sum of fixes makes it worse (skips 8.4k → 9.6k, two registry outages, 47%→0% on-time). Rejected.
- **Move everything native (launchd/cron, no Claude)** — for: no 3-slot limit, no permission classifier; against: TCC blocks launchd from ~/Documents, and ~30% of tasks genuinely need judgment (mail brief, hiring, narrative). Rejected as a wholesale move; adopted for data-only publishing.
- **Buy the data problem down (Bravo scheduled emails + Reporting Pro)** — for: removes the single largest failure class at its source; against: costs money and a vendor thread only Joshua can own. Recommended, as Joshua's decision.
- **Freeze, shrink to a field-facing core, stabilize the host, make the core deterministic, then re-expand one tier at a time under a pass/fail gate** — for: it is the only option that produces a measurable clean week; against: ~120 tasks go dark for 2–4 weeks (they are almost all internal, marketing, personal, or duplicate lanes — none are staff-facing reports). **Recommended.**

DECISION
- Do the freeze-and-shrink plan in Section 5. The controller's test governs everything: **seven consecutive days with every Tier-1 publication on time and zero defective posts, measured by a native script from Slack, before any task is re-enabled.**

REJECTED
- Another watchdog. The registry guard being installed today is reasonable as a Class-0 backstop; no further guardian/sentinel/gap-fill task is added until the core is clean.
- Bulk-editing 190 SKILL.md files again. The core tasks get rewritten one at a time onto the thin pattern (script → verbatim post), and nothing else is touched.
- Deleting anything. Disable, never delete (Rule 4).

---

## 5. The plan

### Phase 0 — this week: stop the bleeding and freeze (prerequisite for everything)
1. **Change freeze, 14 days.** No new scheduled tasks, no new watchdogs, no bulk SKILL.md or registry edits, no department rebuilds. One named "fleet owner" session per day does fleet work; no parallel fix sessions. The freeze is written into `vp-operating-rules` as Rule 21 and into every context skill's header so a fresh session cannot accidentally break it.
2. **Host stabilization (Joshua at the Mac Studio, ~1 hour, one time):** (a) free the data volume to well over 100 GB — the 3 stale installer DMGs in Downloads are 400 MB, the real space is elsewhere; DISK_HEALTH will name it; (b) iCloud Drive → Optimize Mac Storage OFF, and ~/Documents/Claude → Keep Downloaded; (c) Energy: never sleep, app in Login Items; (d) confirm `claude-keepalive` now exits 0 (the parallel session's bootstrap rewrites it through vp-runner — verify with `launchctl list | grep keepalive` after it runs); (e) repair the GitHub backup repo. Until (a)–(c) are done, no result below is trustworthy.
3. **Fleet diet — 167 enabled → ~45 (Tier 1), everything else disabled, not deleted.** Tier 1 = what the field or Joshua reads and what feeds it: daily funds verification + watchdog; pawn walk; sold review; discount review; items to price; the three 10 AM ops checks merged into one; jewelry nightly + catch-up + watchdog; chekkit unanswered AM/PM; missed-email sweep; the Sunday combined Bravo run + gap-fill + Monday compile + postcheck; weekly store KPIs; layaway yield; FFL weekly/monthly; timekeeping; returns; google reviews weekly; markdown pull/review; the five canvases merged into one; monthly prestage/analytics/employee FINAL/scrap/new-customers/EOM recap/GL export + watchdog/sales-tax monthly/bonus close + pull; and the infrastructure that keeps those alive: bravo-morning-pull, bravo-prestaging, bravo-preflight-relaunch, bravo-health-watchdog, fleet-guardian (12:45 silent + 21:45), business-os-daily-refresh, GitHub nightly backup, ceo-mail-brief AM/PM, Bald Rock 15-day contract. Everything else (all social/content lanes, eBay Cowork audits — the native eBay agents keep running, marketing metrics, brevo pollers, hiring pollers, insurance/health/personal tasks, preston-interactive at */5, zoom polling, mail-brief-reply-executor, ask-handbook, gusto-keep-alive, duplicate GA4 pulls, indexers beyond unified-search) goes dark for the proving period. This removes roughly 300 poller dispatches a day and should take queue skips from ~9,500/wk to near zero on its own.
4. **The scorecard that defines "working."** A native script (no Claude) reads the Tier-1 publication list from `fleet/expected_outputs.json`, checks each channel for the marker by its deadline, and writes `fleet/FIELD_SCORECARD.md` daily: per publication, on time / late / missing / defective. This is the only fleet metric that matters and the only thing Joshua is shown daily — one plain line, "All 22 reports landed on time," or the short list that did not.
5. **Two field-facing decisions that are Joshua's (see Section 6):** whether a missed report gets a one-line "delayed" notice in its channel (today the rule is silence), and whether store closing checklists add "post the day in Bravo" so month-end can never be blocked by an unposted day again.

### Phase 1 — weeks 2–3: make the core deterministic (the 9/5 plan's Phase 1, scoped to Tier 1 only)
- One formatter per Tier-1 publication (extend the `format_aged_inventory.py` / `format_weekly_website.py` pattern): parse the pipeline CSVs, validate, emit the exact Slack body, exit 0 = post verbatim, exit 2 = post nothing. A prompt can violate Rule 16; a formatter cannot.
- A post ledger (sqlite): channel, marker, period, hash. Every poster checks it; duplicates become impossible; the scorecard and guardian read it instead of scraping Slack.
- A native Slack poster so data-only publications post from launchd with no Cowork session at all (the eBay agents already do this). Cowork sessions are reserved for the ~10 Tier-1 items that need judgment (mail brief, sold/discount narrative, bonus close, EOM recap).
- Each remaining Cowork task rewritten onto the thin pattern: pinned model, pre-approved tools (all read tools of any server it uses, explicit write grants), no Chrome unless `skip_all_permission_checks`, ≤10-minute session, launch→exit→verify for anything that waits on Bravo. Rewritten one at a time, each proven three nights before the old one is disabled.
- Trim what every session reads: enterprise-map points at a 30-day CHANGELOG excerpt (auto-generated), not the 617 KB file; HIRING_OUTREACH gets a current-state header.

### Phase 2 — weeks 3–6: take the data off the UI (Joshua's money decision)
- Ask Bravo support (existing ticket #43428350763) to add scheduled CSV/Excel emails for End of Month, Safe Register Journal, Aged Inventory, Employee Activity, Layaways, 75-Days-Past-Due, Items to Price, Buys From Public. Draft exists (9/5 plan). Run the $0 Reporting Pro demo; if subscriptions export CSV, buy it (~$425/mo all stores). Every report that moves to an emailed CSV stops depending on the VM, the login, EnsureStore and the 3 slots. Ingest is a native 15-minute launchd job into the same sqlite the formatters read.
- What must stay UI-driven (GL posting, employee activity if not exported) gets the jewelry allow-list, the Continuous-Scrolling removal, and the Chrome↔VM mutex from the 9/5 plan — and nothing else.

### Phase 3 — after the core has a clean week: re-expand one tier at a time
- Tier 2 (Joshua-facing: insurance, health, Bald Rock reviews, backup health, registered agent) → Tier 3 (marketing/social/eBay/email lanes) → Tier 4 (hiring, preston assistant, pollers — every poller converted to an event or API path first: Zoom Phone API, Chekkit/Preston via a native watcher, mail via the unified-search index). A tier is re-enabled only after the previous tier has held the scorecard at 100% for seven days, and each re-enabled task must already be on the thin pattern.
- Month-end runbook: the monthly tier is rehearsed on the island before 10/1 (August's data, dry run), and the 1st-of-month has a named human check at 10 AM against the scorecard, because the first live month after a rebuild is the one that fails.

### What this costs the business during the proving period
About two to four weeks without automated social posting, marketing metrics, hiring polling, Preston's Slack assistant, and the personal/insurance tasks. All of those have manual fallbacks and none are staff-facing reports. The field-facing core is what the field is losing today anyway.

---

## 6. For Joshua — the only decisions that are yours

1. **Approve the freeze and the diet** (Phase 0.1 and 0.3). This is a business call: ~120 tasks go dark for the proving period.
2. **The host hour** (Phase 0.2) — physical, at the Mac Studio. Nothing else is testable without it.
3. **Silence vs. a delayed notice.** Today a missed report produces silence in the channel. The controller's recommendation: one plain line, "Today's [report] is delayed — it will post when ready," so staff stop guessing. Your call; it changes what the field sees.
4. **Store process: "post the day in Bravo" on the closing checklist.** The unposted 8/29 day blocked August's books for five days. No automation can post it for you unattended.
5. **Bravo scheduled CSV emails (vendor email under your name) and Reporting Pro (~$425/mo).** The single biggest lever on the Bravo failure class.
6. **The host job queue built today** (`fleet/host_queue/`) lets any unattended session run arbitrary scripts on the Mac with your privileges, bypassing Cowork's approval checks. Options: keep it as-is (fastest self-healing, highest trust), restrict it to a reviewed allow-list of named scripts (recommended by the board), or remove it. The registry-guard relaunch it enables is worth keeping either way.

Nothing in this document has been executed. Sections 5.1–5.4 proceed only on your "go."
