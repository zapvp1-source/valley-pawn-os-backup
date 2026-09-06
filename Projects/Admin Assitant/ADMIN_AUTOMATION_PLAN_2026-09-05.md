# Records Administrator Department — Automation & Robustness Plan

**Prepared:** 2026-09-05 · **Status:** PLAN — nothing built yet (Joshua asked to see the plan first)
**Scope:** everything the "admin assistant" function owns across all 3 domains — inbox, calendar, Reminders, Notes, filing, correspondence, deadlines/compliance, payables prep, minutes, and the records that back them.
**Evidence base:** full scheduled-task registry (168 tasks), BUSINESS_OS LIVE STATE (9/5), PUBLICATION_CALENDAR.md, SCHEDULED_TASK_RELIABILITY_PLAN.md, Communcations/, Email Refinement/, Life OS/ (register read in full), Compliance/, Human Resources/, this folder, live Reminders list probe. Verified against output files, not run records (Rule 12).

---

## 1. Where the department stands today (verified)

**Inbound is solved. Obligations are not.**

What works and should not be touched: the CEO mail brief (7 AM / 4 PM, 19 unbroken run logs), the reply executor, 9 server-side Gmail filters, the Apple Mail "My Mail" smart mailbox, store-inbox and missed-call EOD sweeps with trend logs, Chekkit unanswered follow-ups, registered-agent daily check, Gusto signature chase, nightly unified-search + document-photo OCR indexing, GitHub OS backup, fleet-guardian, task-hygiene sweep, business-os daily refresh.

What is broken, missing, or manual — every item below was confirmed in a file, not inferred:

| # | Gap | Evidence |
|---|---|---|
| 1 | **No deadline/obligation register and nothing watches one.** FFL renewals, insurance renewals, 5 store leases, BPOL licenses in 5 cities, VSP NICS fees, surety bonds, landlord gross-sales reports, FL reemployment-tax notices are spread across 7 files + Apple Reminders. | `FFL_REGISTRY.md`: "Nothing watches FFL expirations… caught by a human noticing missing mail." Harrisonburg landlord demanded 19 months of missing reports (register 9/4). FL RT filings missing since registration, 5+ Gusto reminders. |
| 2 | **ATF mailing address of record for all 5 FFLs is the St. Augustine house.** Roanoke's renewal form mails ≈ 2026-10-03 to Florida. | `FFL_REGISTRY.md` — root cause of the July Culpeper scramble. |
| 3 | **Apple Reminders is a parallel task system nothing reads.** 248 items, 42 overdue at last snapshot (7/14), lists named Payables, Home Payables, Annual Compliance and Tax Items (38), Corporate Weekly/Monthly, Supervisor Daily/Weekly. Backup is 7 weeks stale and 22 lists were never itemized. AppleScript only exposes ungrouped lists (confirmed live today: 14 lists visible, the Home and Valley Pawn groups invisible). | `Reminders_Backup_2026-07-14.md`; osascript probe 9/5. |
| 4 | **No calendar workflow.** Scheduling happens ad hoc inside sessions (interview grids, appraisal slots). The morning brief carries no calendar. | Register rows; `morning-brief` task description. |
| 5 | **Open Items Register is written to but never groomed.** 388 KB, 522 lines, ~130 "open" rows of which 32 are already marked resolved/done/closed but never moved; 5 ad-hoc .bak copies (1.4 MB). No task triages it. | `Life OS/OPEN_ITEMS_REGISTER.md` (self-describes as "short by design"). |
| 6 | **Store lease tracker is 1-of-5 filled.** Harrisonburg/Lexington/Roanoke/Waynesboro rows are TODO placeholders. | `STORE_LEASES.md`. |
| 7 | **Filing plan (7/29) stopped after the Desktop phase.** Weekly `00 Inbox` sweep, quarterly cross-cloud sweep, `FILING_GUIDE.md`, BUSINESS_OS registration — all specified, none built. 244 files still parked in `_Review for Deletion`. | `FILE_ORGANIZATION_PLAN.md` §8, `delta_addendum.md`. |
| 8 | **Mail system has no health check.** `weekly-mail-health` (volume by account, top senders, subscription creep, tier accuracy) and the vendor-flood quarantine rule were specified 8/27 and never built. Personal iCloud inbox: 12,796 unread of 58,961. | `Email_Triage_Plan.md` §3.6, §3.10; register. |
| 9 | **Orphan state file.** `Projects/mail-brief/reply-executor-state.json` (`lastProcessedTs: 0`) duplicates the live one under `Communcations/mail-brief/`. If the executor ever resolves to it, it replays every brief since time zero. | Both files on disk 9/5. |
| 10 | **Documented tasks that don't exist.** `vsp-nics-fee-monthly-check` (runbook says it runs the 5th), `weekly-email-cleanup`, `daily-mail-unsubscribe`, `domain-transfer-check` (BUSINESS_OS lists them as live; they are unregistered folders). | Registry vs `VSP-NICS-Fee-Payment-Runbook.md`, BUSINESS_OS Cross-Domain table. |
| 11 | **Exec summary layer never built.** `weekly-enterprise-brief` / `monthly-enterprise-brief` (incl. "Decisions waiting" from the register) — PLAN ONLY since 8/24. | `EXEC_SUMMARY_SYSTEM_PLAN.md`. |
| 12 | **Admin has no home.** BUSINESS_OS has 8 domains, none is Administration/Records. This folder is the 3rd-stalest project (7/29). 6 of 7 admin-related folders have no STATUS.md (Rule 10). | BUSINESS_OS headings grep; folder listing. |
| 13 | **Registry debris.** 10 fired one-shots still registered (disabled); 2 dead jewelry siblings; 3 tasks stuck with "⭐ RUN NOW ONCE" titles; 2 quarterly tasks (`quarterly-capex-sweep`, `vp-hr-compliance-quarterly-review`) enabled but never fired; `amazon-return` / `dismiss-employee` manual tasks untouched since April. | Registry 9/5. |
| 14 | **Capacity constraint governs everything above.** Scheduler runs max 3 sessions at once; 148 enabled tasks; 7,876 queue-wait skips in 7 days; 49 tasks fire 8–10 AM. Any plan that adds pollers or long sessions makes the department less reliable, not more. | `SCHEDULED_TASK_RELIABILITY_PLAN.md`. |

---

## 2. Expert Board

**Panel:** a records-management / corporate-secretary consultant (F500 admin function), an SRE (the 3-slot scheduler is the binding constraint), a controller (obligations = money and penalties), a macOS automation engineer (Reminders/Calendar/Notes access realities).

**Options weighed**

- *Build a dedicated Cowork task per gap (deadline watcher, reminders sync, calendar brief, mail health, inbox sweep, register groom…).* For: fastest to write. Against (SRE, hard veto): 6–8 new sessions into a 3-slot queue already recording ~1,100 skips a day; every one of them would be a poller or a babysitter. This is how the fleet got to 168.
- *One consolidated "admin desk" session per day that does all admin checks.* For: one slot, one log, one owner. Against: a 40-minute session is exactly the babysitter pattern the reliability plan is removing; a single failure takes every admin check down with it.
- *Native scripts do the work; Claude only reads results.* Deadline math, Reminders export, register grooming, mail volume stats, inbox sweeps are all deterministic — Python/stdlib + EventKit on launchd, zero scheduler slots, zero Chrome, zero permission cards. Claude sessions that already exist (`morning-brief`, `ceo-mail-brief`, `business-os-daily-refresh`, `fleet-guardian`) read the JSON those scripts write. For (all four): matches the reliability plan's own Phase 3 pattern (`dispatch_health.py`), Rule 18-safe (a script either produces a valid file or nothing), reversible, and it doesn't touch a single hardened task. Against: needs one-time TCC grant for Reminders/Calendar to the script runner (one click).
- *Sync everything into Apple Reminders as the single tracker.* For: Joshua already lives there. Against (records consultant): Reminders has no evidence column, no domain tags, no audit trail, and its API hides grouped lists. It stays the **human view**; the register stays the **system of record**; a one-way export keeps them consistent.

**Decision:** native-scripts-first, fold results into existing sessions, add at most **two** new Cowork sessions in the whole plan (a weekly admin groom and the weekly enterprise brief — both ≤5 min, both off-peak). One system of record for obligations (`OBLIGATIONS.json` + `OBLIGATIONS.md`), one for follow-ups (the existing register, now groomed), Reminders becomes a read-side mirror, calendar becomes a section of the brief that already exists.

**Rejected:** per-gap Cowork tasks (capacity); a monolithic admin session (blast radius); Reminders as system of record (no audit trail); rebuilding the mail brief (it works — leave it).

---

## 3. Target architecture

```
                 SYSTEMS OF RECORD (Life OS/)                       HUMAN VIEWS
  OBLIGATIONS.json/.md  ── native deadline watcher ──► morning-brief "Due" section
  (every dated duty:                (launchd, daily 5:40)   Reminders "Deadlines" list (mirror)
   FFL, insurance, leases,                                   Joshua DM at 120/60/30/7/1 days
   BPOL, VSP, bonds, reports,
   tax notices, payables)
  OPEN_ITEMS_REGISTER.md ── native groom + archive ──► weekly-enterprise-brief "Decisions waiting"
  (drafted/sent/awaiting)        (launchd, nightly)          register stays < 60 KB
  Reminders (all lists) ──── EventKit export (nightly) ──► reminders.json → unified-search + brief
  Google Calendar ──────────── Calendar MCP (in brief) ──► morning-brief "Today / next 7 days"
  Apple Mail Envelope Index ── native mail_health.py ────► weekly-mail-health section in Mon brief
  iCloud + Drive 00 Inbox ──── native inbox_sweep.py ────► filed per FILING_GUIDE; log only
  Compliance/FFL_REGISTRY ──── directory-listing-monitor +FFL block ──► #registered-agent / DM
```

Every arrow on the left is a script with no Claude usage. Every Claude touch on the right is an existing session gaining a section, except the two new weekly ones.

---

## 4. The plan — phases, in execution order

### Phase 0 — Hygiene and a home (Day 1, ~2 hours, all reversible)
1. Create **Domain 9 — Administration & Records** in BUSINESS_OS.md (hand-written section, additive), listing every admin task/skill/file with owner, cadence, and output. Add the admin rows to `PUBLICATION_CALENDAR.md` and `fleet/expected_outputs.json` so fleet-guardian verifies them.
2. `STATUS.md` in Admin Assitant, Communcations, Compliance, Human Resources, Life OS, Email Refinement (Rule 10). Admin Assitant's STATUS becomes the department log.
3. Registry cleanup via the existing `task-hygiene-sweep` path: delete the 10 fired one-shots and the 2 dead jewelry siblings; strip the three "⭐ RUN NOW ONCE" titles; fix the two `2-7,0` crons; correct BUSINESS_OS's Cross-Domain table so it stops listing unregistered folders as live. Nothing enabled is disabled.
4. Resolve the orphan `Projects/mail-brief/` stub: read `mail-brief-reply-executor/SKILL.md` to confirm which path it uses, then move the stub to `99 Archive` (never delete). 
5. Fix `VSP-NICS-Fee-Payment-Runbook.md` to stop claiming a task that doesn't exist (the real check arrives in Phase 2).
6. Re-verify the two never-fired quarterly tasks will actually fire 10/1–10/2 (they were created after the July quarter — expected, but confirm `nextRunAt`).

### Phase 1 — Obligations, Reminders, Calendar (Week 1)
7. **`Life OS/OBLIGATIONS.json` + generated `OBLIGATIONS.md`** — one row per dated duty across all 3 domains: what, domain, entity, due date, recurrence, lead-time, evidence file, owner (Joshua / Preston / Claude / CPA), and "how to close." Seeded from: FFL_REGISTRY (5 renewals incl. Roanoke form ≈ 10/3), INSURANCE_PORTFOLIO renewal calendar (5), STORE_LEASES (Culpeper fully; the other 4 pulled from Drive/unified-search in the same pass — closes gap 6), BPOL for 5 cities, VSP NICS (monthly, 5th), SURETY_BONDS, Harrisonburg monthly gross-sales report, FL reemployment tax, sales-tax filing, gun-audit 15th, Reminders "Annual Compliance and Tax Items" (38) and "Payables" lists, Northwest RA renewals, domain/DNS expiries (DMARC/SPF items from Email Refinement).
8. **`bin/obligations_watch.py`** (native, launchd 5:40 AM daily): computes due/overdue, writes `fleet/OBLIGATIONS_DUE.json`, sends ONE plain DM to Joshua only when something crosses 120/60/30/7/1 days or is overdue (Rule 16 wording, no jargon), and mirrors upcoming items into a Reminders list named **"Deadlines (auto)"** — write-only to that one list, never touches his lists.
9. **`bin/reminders_export.py`** (native, EventKit via pyobjc, nightly 3:15 AM): exports every list including grouped ones to `Life OS/reminders/reminders.json` + a dated markdown snapshot (replaces the stale 7/14 backup permanently), feeds unified-search, and produces the overdue list the brief reads. One-time TCC approval for Reminders + Calendar on the script runner is the only human step.
10. **Morning brief gains three sections** (edit to `morning-brief/SKILL.md` with `.bak`, sonnet-pinned, still one session): *Today's calendar + next 7 days* (Google Calendar MCP: conflicts, prep items, travel), *Due this week* (from OBLIGATIONS_DUE.json), *Overdue reminders by list* (from reminders.json). Numbered so the reply executor can act on them the same way it acts on mail items.
11. **Register grooming script** `bin/register_groom.py` (native, nightly 3:20): moves any OPEN row whose status text says resolved/done/closed/sent-confirmed into RECENTLY CLOSED, archives RECENTLY CLOSED rows older than 30 days to `OPEN_ITEMS_ARCHIVE_YYYY.md`, dedupes the .bak sprawl into `Life OS/_backups/`, and enforces the row schema (adds an **Evidence** column: file path or Gmail/Slack link proving "sent"). Register target: under 60 KB. Any row with a date becomes an OBLIGATIONS entry automatically.

### Phase 2 — Mail health, filing governance, compliance monitoring (Weeks 2–3)
12. **`bin/mail_health.py`** (native, Sunday 11 PM, reads Apple Mail's Envelope Index read-only): volume by account, top-10 senders, new subscription senders, filter-tier accuracy, and the **vendor-flood guard** (>100/day from one sender → writes a proposed Gmail filter to `Communcations/pending-filters/`; the Monday brief shows it as a one-word approve item). Output is a section in Monday's brief — no new channel, no new task.
13. **Personal inbox (12,796 unread)** — proposal only, Joshua's call: a one-time bulk archive of everything older than 90 days that isn't starred or from a contact, same method as the 8/27 Gmail cleanup (archived, not deleted, reversible). 
14. **Filing governance** — write `FILING_GUIDE.md` at both cloud roots; `bin/inbox_sweep.py` (native, Sunday 11:30 PM) files `00 Inbox` items by naming convention/keyword, dedupes `(1)` copies, and logs — never deletes; `_Review for Deletion` (244 files) gets a keep/toss shortlist written to STATUS for Joshua's one-click. Remaining FILE_ORGANIZATION_PLAN phases 2–5, 7 executed one per session with before/after manifests, as originally designed.
15. **Compliance monitoring** — FFL block added to `directory-listing-monitor` (eZ Check all 5, diff vs registry, "Dixie" scan) exactly as `FFL_LISTINGS_STATUS.md` recommends; VSP NICS balance check: the portal can't be read headless, so it becomes a **numbered item in the 5th's morning brief** (runbook link + last-known balances, tracked as an OBLIGATIONS row) instead of a phantom task; the "READ ME – signed FFL copies" Drive doc gets corrected (Culpeper 9J).
16. **Correspondence discipline** — every outbound letter/notice gets a register row with Evidence at draft time and a second Evidence entry at send (Gmail Sent / Slack permalink / tracking #). `register_groom.py` flags rows Sent-unconfirmed for > 7 days into the brief.

### Phase 3 — The executive layer (Week 4)
17. **`weekly-enterprise-brief`** (Mon 11:45 AM, ≤5 min, sonnet) built from the 8/24 plan: CEO tier only to start — what posted, what missed (from fleet-guardian), decisions waiting (register rows blocked on Joshua), obligations due in 30 days, mail health. Preston and manager tiers follow only after Joshua has seen two CEO editions.
18. **`monthly-admin-close`** folded into the existing `monthly-eom-recap` (1st) — obligations closed/missed last month, register stats, filing counts, minutes feeder. `compile-monthly-minutes` gains an "Administration" section sourced from it.
19. **Reminders write-back (optional, Joshua's call):** business rows from the register mirrored into a "Claude – Follow-ups" list so he can tick them from his phone; ticks flow back to the register on the nightly export.

---

## 5. What this does NOT touch
`ceo-mail-brief`, `mail-brief-reply-executor`, Gmail filters, Apple Mail smart mailbox/categories, store-inbox/voicemail/Chekkit sweeps, Bravo pipeline, any hardened Monday task, unified-search internals, Email Refinement/Brevo tasks. All additive; every edited SKILL.md gets a `.bak`; every script is idempotent and produces a valid file or nothing (Rule 18).

## 6. Capacity impact
New Cowork sessions: **+2/week** (enterprise brief, and nothing else — the groom, watcher, export, mail health, and sweep are launchd). Existing sessions modified: `morning-brief` (+3 sections), `monthly-eom-recap` (+1), `directory-listing-monitor` (+FFL block). Net scheduler load: roughly flat; Phase 0 deletes 12 registry entries.

## 7. Success criteria (measured, 30 days after Phase 1)
- Zero obligations discovered by a third party (landlord, ATF, FDOR) — everything dated is in OBLIGATIONS.json with a lead-time alert on file.
- Register under 60 KB, no row "Sent-unconfirmed" older than 7 days.
- Reminders overdue count visible in the brief daily; 7/14-style snapshot never stale by more than 24 h.
- Morning brief carries calendar + due + overdue every weekday.
- Mail health section every Monday; no single sender exceeds 100/day unflagged.
- Admin domain present in BUSINESS_OS LIVE STATE; every admin publication in PUBLICATION_CALENDAR with a guardian entry.

## 8. Decisions that are genuinely Joshua's (everything else proceeds autonomously)
1. **ATF mailing address of record** — keep the St. Augustine house (and let OBLIGATIONS remind you to watch the FL mailbox ≈10/3 for Roanoke) or move it to a Virginia store / the registered agent. Records consultant recommends the registered agent (Northwest) so the existing daily check catches it. Business/legal call — yours.
2. **Personal iCloud inbox bulk archive** (12,796 unread, reversible) — yes/no.
3. **Reminders write-back** ("Claude – Follow-ups" list) — yes/no. Read-side export and the "Deadlines (auto)" list proceed regardless.
4. **One TCC click** granting Reminders + Calendar access to the script runner when Phase 1 lands (I'll DM the exact moment).

Everything else in this plan is technical and proceeds under Rule #1 once you say go.
