# Email Department — Full Review & Automation Plan
**Date:** 2026-09-05 · **Status:** PHASE 0 + PHASE 1 SHIPPED 2026-09-05 (Joshua: "fix what you can fix"). Phases 2–5 queued.
**Scope:** Every email-touching workflow, cadence, task, list, and data feed for Valley Pawn. Reviewed against live Brevo API, the scheduled-task registry (168 tasks), CHANGELOG, EFFICIENCY_LOG, the 8/22 audit, and all 19 prior files in this folder.

---

## 1. What the department is today (verified, not assumed)

### The weekly engine (Mon → Fri), 9 tasks in a chain
| When | Task | Job |
|---|---|---|
| Mon 8:10 | `vp-deal-of-week-monday-prompt` | Posts deal prompt to #deal-of-the-week |
| Mon 11:00 | `vp-deal-of-week-monday-reminder` | Chases stores that haven't submitted |
| Mon 11:50 | `brevo-weekly-draft-guard` | Guarantees this Thursday's draft exists, named correctly, lists 7+10(+wave) |
| Mon 12:30 | `vp-deal-of-week-monday-pick` | Fills deal blocks, schedules Thu 10 AM send |
| Mon 13:05 | `vp-website-deals-weekly` | Mirrors deals to thevalleypawn.com/retail |
| Wed 18:00 | `vp-deals-social-wednesday` | Deals → Publer social posts |
| Thu 10:00 | Brevo scheduler | Send |
| Thu 10:30 | `vp-thursday-email-watchdog` | Verifies send; self-heals from Slack if still draft |
| Fri 3:30 | `email-analytics-weekly` | Per-link clicks → Google Sheet + dashboard + 5-line Slack post |
| Fri 8:00 | `brevo-weekly-efficiency-audit` | Deep audit: auth, lists, runway, waves, fixes what it can, writes EFFICIENCY_LOG |
| Mon 11:30 | `marketing-ceo-briefing-weekly` | Rolls up the email lane into the CEO briefing |

### Always-on
| Cadence | Task | Job |
|---|---|---|
| Daily 7:00 | `brevo-preflight-watchdog` | Suspends any campaign missing call/text tracking or leaking the legal name; forces seed list 10 |
| Daily 10:00 | `brevo-welcome-new-contacts` | Transactional welcome (template 72) to contacts created in last 48h |
| Tue 16:40 | `chekkit-weekly-review-requests` | Chekkit review asks + imports new emails into Brevo |
| Tue 17:30 | `bravo-brevo-attribute-sync` | Name / store / phone top-up from Bravo archive |
| 1st of month | `monthly-we-buy-gold-silver-email` | Gold & Silver to the full list (3+10) |
| Queued | Giveaway ladder 20% (9/24), 30% (10/24) | List 6, 85 entrants |

### Live Brevo state (pulled today)
- Lists: master **13,226** · Engaged **177** · Seeds 8 · Waves A–E **2,145–2,247 each** · Lexington store list 2,647 · Forfeited win-back **0** · Giveaway 85 · "monthly" 299
- **17 weekly drafts staged Sep 10 → Dec 31**, each already wired to engaged + seeds + 1 wave (Sep) or 2 waves (Oct on)
- Domain auth: fcfpawn.com single SPF ✔, thevalleypawn.com DKIM ✔, DMARC p=none with reports going to an inbox we read
- Results: last two weekly sends 11.8 and ~12 calls+texts/1,000 — first ever above the 8/1,000 target. Sep 1 Gold & Silver: 11,000 delivered, 1.8% bounce, 0.15% unsub — healthy.

**Verdict:** the plumbing is solid and the recovery from the August blackout held. The department is now a reliable broadcast machine. What it is *not* yet is a system that (a) can't run out of road, (b) knows who its customers actually are, or (c) sends anything triggered by customer behavior — which is where the money in pawn email lives.

---

## 2. What the review found (11 friction points, ranked)

| # | Finding | Impact | Evidence |
|---|---|---|---|
| **F1** | **Monthly Gold & Silver sends at ~2:20 AM ET, not 9 AM.** Cron `15 2 1 * *` fires in local time; the task then sends immediately. | 11,000-person send lands overnight and is buried by morning | Sep 1 sentDate `02:20 -04:00`; Aug 1 `03:09` |
| **F2** | **Calendar cliff Dec 31.** Nothing stages the next quarter. Draft-guard only *warns* in mid-December. Runway exhaustion was one of the two causes of the Aug 6/13/20 blackout. | Guaranteed repeat outage in January unless built | draft-guard SKILL; CHANGELOG 8/21 "still open" |
| **F3** | **Zero triggered email.** No loan-due reminder, layaway-due, forfeited win-back (list 11 = 0 contacts since July, creative finished), birthday, or multi-step welcome. | Highest-ROI email in the industry not sent; forfeitures and missed interest go unaddressed | 8/22 audit F07; file 15 |
| **F4** | **Customer data half-empty in Brevo.** Engaged list: FIRSTNAME 35%, STORE 52%, SMS 50%. Sync source is the Chekkit-invites archive, which has structurally limited coverage; gains are ~0.1 pt/week. No BIRTHDAY, LOAN_DUE, LAYAWAY_DUE fields exist. | Personalized "YOUR STORE" block renders blank for half the audience; no triggered flow can exist | EFFICIENCY_LOG 9/1, 9/4 |
| **F5** | **Engaged-list definition recruits bots.** "Any link click → list 7" pulls in security scanners; list-7 sends have reported 58–136% click-of-delivered. | The core audience and the headline metric are both partly noise | 8/22 audit F02 |
| **F6** | **Conflicting instructions inside the pick task.** `vp-deal-of-week-monday-pick` Step 5 still says upload photos via Brevo `POST /v3/media` (endpoint doesn't exist — this killed 3 weeks in July/Aug); the addendum below it and the Thursday watchdog say the opposite. | A fresh run can follow the wrong step and fall back to AI images instead of real deal photos | Registry read today |
| **F7** | **Orphan drafts aimed at the full list.** Campaigns 43 (Aug gold rebuild), 49 (Hiring), 23 (W5 July 4), 1 (TEST) sit as drafts targeting list 3 / empty. | One mis-click or one script bug = accidental 13k send of stale content | Brevo drafts today |
| **F8** | **Two Friday reporters, two metric methods.** `email-analytics-weekly` uses per-link stats (correct); `efficiency-audit` uses an aggregate click proxy for calls+texts and says so. Channel name `#email-campiagns` (typo) in analytics vs `#email-campaigns` elsewhere. | Two slightly different numbers for the same send; possible split across two channels | Both SKILL.md files; EFFICIENCY_LOG 9/4 |
| **F9** | **Reply-to is jdavis@fcfpawn.com.** Every customer reply to a store spotlight lands in Joshua's inbox, not the store's. | Owner becomes the bottleneck for customer replies; slower response | draft-guard spec |
| **F10** | **Bad emails enter at the counter unchecked.** 64–121 new hard bounces/month; 15.9% of file suppressed. | Steady reputation drag; wasted sends | 8/22 audit F11 |
| **F11** | **A/B testing is sequential only** (Brevo API won't persist winner criteria). Acceptable, but confounded. | Slower learning | SUBJECT_LINE_EXPERIMENT.md |

Not a finding, but a standing constraint: every task in the chain requires the Mac awake with Claude open. Brevo's own scheduler covers the Thursday send once scheduled; the Thursday watchdog covers a missed Monday if the Mac is up Thursday. Fleet Guardian already watches the pick task's output. That's adequate — no rebuild needed.

---

## 3. Expert board deliberation

**PANEL:** martech/lifecycle engineer · email deliverability specialist · pawn-industry compliance reviewer · SRE for scheduled systems

**Key forks weighed**

- *Triggered flows: Brevo Automations vs. our own transactional-API pattern.* Brevo's automation builder has no creation API and there's no persistent browser session. The welcome flow already proved the transactional-API + attribute-flag pattern (template + `WELCOMED=true`). **Decision: transactional API for every triggered flow.** Same pattern, already hardened, fully scriptable, idempotent via attribute flags.
- *Data source for the sync: keep the Chekkit-invites archive vs. build a proper Bravo customer export.* Archive has hit its ceiling (35/52/50%). A Customers-module Ad Hoc report exposing Email, Phone, Store, DOB, plus the existing `loan-portfolio-2026` cell for due dates, is the only way to reach 90%+ and to get any date field at all. **Decision: build a new additive pipeline cell (`customer-contact-sync`), never touch existing cells.** Joshua started this report in July — check whether it exists before creating.
- *Engaged-list fix: edit list 7 in place vs. build a parallel list.* Editing the live send audience mid-flight is the one thing that could break a working Thursday. **Decision: build list "Engaged v2 (human-verified)" alongside, populate for 4 weeks, compare, then switch the draft-guard target. Reversible in one field.**
- *Calendar staging: one big annual build vs. rolling quarterly task.* Annual is what ran out. **Decision: a quarterly `brevo-stage-next-quarter` task (Dec 1, Mar 1, Jun 1, Sep 1) that drafts 13 weeks from the theme calendar + subject-line experiment rules, and a draft-guard floor raised from 4 to 8 weeks.**
- *Loan-due reminders: send as marketing or transactional.* Compliance reviewer: these are account notices about a live contract — transactional, no unsubscribe-gating problem, but notice language must be reviewed and must never state or imply a legal consequence beyond what Virginia pawn law and the ticket say. **Decision: build the flow fully, hold the switch until Joshua approves the copy (his call — customer-facing + legal).**
- *DMARC to quarantine.* Deliverability: not until 4+ weeks of reports have been read. **Decision: audit task reads the rua reports monthly; recommend p=quarantine only after clean data. Not now.**

**Rejected:** Brevo SMS (cost; Chekkit already is the SMS channel — orchestrate, don't duplicate) · rebuilding the weekly chain (it works; harden the edges) · sunsetting the dormant 11k (wave rotation is already re-warming them and is reversible).

---

## 4. The plan — five phases, additive only

### Phase 0 — Hygiene ✅ SHIPPED 2026-09-05
1. ✅ **Retimed `monthly-we-buy-gold-silver-email`** — cron `15 2 1 * *` → `0 9 1 * *`. First 9 AM send 2026-10-01 (F1).
2. ✅ **Orphan drafts 43/49/23/1 parked** — renamed `[PARKED — do not send] …` and repointed from list 3 to the internal seed list (10), so a stray send can only reach staff. Content untouched (F7).
3. ✅ **`vp-deal-of-week-monday-pick` STEP 5 rewritten** to the proven website-media path; the dead `/v3/media` endpoint is now named as forbidden instead of instructed. Backup `.bak-pre-20260905-phase0` (F6).
   ✅ *Bonus fix found while in there:* STEP 8's Slack confirmation named `#deal-of-the-week` but not its ID — that post has been silently missing every Monday since 7/27 while the sends themselves succeeded. Step 8 now pins `C0AVCANK7E3` and re-reads the channel to confirm it landed. **Watch Monday 9/7 — that is the test.**
4. ✅ **Channel question settled** — there is only ONE channel and it really is spelled `#email-campiagns` (`C0APR5WUL2Z`, private). No split; nothing to merge. Every Brevo task already posts there (F8).
5. ✅ **Fleet Guardian manifest** — `brevo-stage-next-quarter` added; the efficiency audit, preflight watchdog and monthly gold send were already covered by the same-day publications audit. 63 entries total, backup written.
6. ⏸️ **Per-store reply-to — HELD FOR JOSHUA.** This is one of the three decisions that are his (it changes who answers customers), so it was not applied unilaterally (F9).

### Phase 1 — Never run out of road ✅ SHIPPED 2026-09-05
7. ✅ **`brevo-stage-next-quarter` created** — quarterly, 25th of Jan/Apr/Jul/Oct at 6 AM, sonnet-pinned. Writes the quarter's theme spine (5 store spotlights, 2 gold, loans on bill-cycle weeks, warranty, seasonal, community-only holidays), then runs the new committed script `bin/stage_quarter.py`, which clones the live template, fills only the variable regions, continues the A–E wave rotation, and GET-verifies every draft (name, lists, deal placeholder, no unfilled markers, 5× call + 5× text links, primary CTA, no legal-name leak). Dry-run proven against live campaign 70. **First run 2026-10-25 for Q1 2027** — earlier than the Dec 1 originally planned, so the runway never dips below ~9 weeks.
8. ✅ **Runway floor raised 4 → 8 weeks** in the Friday efficiency audit, and the draft-guard's hardcoded "calendar ends Dec 31" note replaced with a standing runway check pointed at the stager. Both backed up.
9. ✅ **Engaged v2 built and populated — Brevo list 19.** *Correction to the 8/22 audit, which said the scanner purge "needs per-contact click data the API won't expose": it does expose it.* `GET /contacts/{email}` returns `statistics.clicked` (campaignId, url, eventTime, ip, count) and `statistics.delivered` to pair against. Scoring rule: an intent click (primary CTA / store call / text / map / store finder) within 90 days, **≥45 s after delivery**, in a campaign where the contact clicked ≤7 distinct URLs and not only chrome links.
   **First pass result — F5 confirmed with real data: of 177 on list 7, only 87 are human-engaged.** 90 are stale or scanner-shaped (289 no-click-in-90d across the wider scan, 19 chrome-only, 4 clicked within 31 s of delivery, 1 walked 12 URLs). List 19 created and populated with the 87, verified by re-read.
   Maintained by the new `brevo-engaged-v2-refresh` task (Wed 6:20 AM, sonnet-pinned) via `bin/engaged_v2.py`, which scans list 7 + v2 + a rotating slice of the 11.5k pool (capped so each run stays ~15–20 min and the pool cycles over ~10 weeks). **Nothing sends to list 19** — list 7 is still the live audience, and the switch stays Joshua's call after 4 stable weekly comparison rows.

### Phase 2 — Know the customer (Sep–Oct) — the unlock for everything below
10. **Bravo Customers Ad Hoc report `Claude Customer Contact Sync`** (Email, Phone, First/Last, Home Store, DOB, SMS consent, Email consent). New AHK handler cloned from an existing one, **new pipeline cell**, registered additively, proven on the island, then daily. Contention check first, per `bravo-context`.
11. Extend `loan-portfolio-2026` usage (already exists, don't modify): pull active tickets → Due Date, Pull Date, Disposition per customer.
12. **`bravo-brevo-attribute-sync` v3** (new script alongside v2): adds BIRTHDAY, LOAN_DUE_DATE, LOAN_STORE, LAYAWAY_DUE_DATE, FORFEITED_LOAN/LAST_FORFEIT_DATE/FORFEIT_STORE, EMAIL_CONSENT. Keeps v2's guards (no username-as-name, no shared phone numbers, never overwrite non-empty). Moves from Tuesday-weekly to **daily** once the cell is live. Validates syntax + MX on every new address before import (F10).
13. Backfill STORE=Lexington from list 12 (2,647 contacts) — one-shot, gated to contacts with STORE empty.
14. Populate **list 11 Forfeited Win-Back** from the cross-reference (file 15, steps 3–4). Consent-aware, deduped against the general win-back.

### Phase 3 — Triggered flows (Oct) — transactional API, one new daily task each, welcome-flow pattern
15. **Loan-due reminders** — T-5 ("your loan is due Friday — pay in the app or in store"), T-1, grace-ending. Attribute flags per ticket so nothing sends twice. Copy drafted for Joshua's approval; **built dark, switched on only when he approves the language.**
16. **Layaway payment due** — same mechanic, ready before Christmas layaway peaks.
17. **Forfeited win-back Month-1 email** from the Drive copy pack (relationship-only, no discount, never references the item), then the monthly rotation as its own scheduled task. Cross-suppressed with the general win-back.
18. **Welcome series** — extend template 72 into 3 touches (day 0 brand/warranty, day 3 loans 101, day 10 your store + deal of the week). Same WELCOMED flag, extended to WELCOME_STEP.
19. **Birthday** — 20% offer per `valley-pawn-context`, 7 days before, one per year (BIRTHDAY_SENT_YEAR flag). Needs the DOB field from Phase 2.

### Phase 4 — Relevance and reach (Nov)
20. Store-aware weekly send: the existing `{% if contact.STORE %}` block already personalizes; once STORE >85%, add a per-store hero variant so a Culpeper customer never leads with a Harrisonburg address.
21. **Chekkit SMS orchestration** for high-intent contacts (clicked call/text but didn't transact within 7 days — Bravo cross-check): one SMS from their own store. Uses existing Chekkit path; no Brevo SMS spend.
22. Annual "we're still here" to the dormant file at Thanksgiving (already in the sunset policy; wave rotation covers the rest).

### Phase 5 — Measurement that can't lie (ongoing, starts Phase 0)
23. One metric source: `email-analytics-weekly` (per-link `linksStats`) becomes the sole computer of calls+texts/1,000; the Friday audit and CEO briefing *read* its Sheet instead of recomputing. Nothing deleted — the audit's own numbers are replaced by a read.
24. **Send-day in-store lift** (the Phase-2 KPI never built): pair each Thursday send with Bravo daily transaction counts Thu–Sat vs. no-send weeks, by store, from the pipeline's existing daily CSVs. Adds one row per week to the Sheet.
25. Loan-reminder KPI: redemption rate and on-time interest payments for reminded vs. unreminded tickets — the number that proves Phase 3 paid for itself.

---

## 5. What Joshua decides (only these)
1. **Loan-due reminder copy** — customer-facing notice about a live loan. I'll draft it; you approve the wording (or route to counsel) before it switches on.
2. **Birthday 20% offer** — confirm the offer stands as documented, or change it.
3. **Reply-to per store** — confirms store managers own customer email replies from spotlights (they'll see them in the store inbox).

Everything else is technical and the board has decided it. All work is additive: new tasks, new lists, new scripts, new pipeline cell — no edits to the Monday combined run, existing saved Bravo reports, existing handlers, or the live Thursday chain beyond the two documented fixes (F1 retime, F6 doc correction) which are backed up first.

## 6. Sequencing & proof points
- ~~Week of Sep 7: Phase 0~~ ✅ **done 2026-09-05.** Proof points to watch: **Mon 9/7** the picker posts its confirmation line to #deal-of-the-week (tests the channel-ID fix); **Thu 9/10** campaign 54 reach jumps ~180 → ~2,400 with wave list 14; **Thu 10/1** the gold send lands at 9 AM, not 2 AM.
- ~~By Sep 30: Phase 1~~ ✅ **done 2026-09-05.** Proof points: **Wed 9/9** first automatic v2 refresh writes a comparison row; **Sun 10/25** the stager creates 13 Q1-2027 drafts that all pass preflight.
- **By Oct 15:** Phase 2 cell live daily; attribute coverage on engaged list >85% names/store, DOB and due dates populated. Proof: EFFICIENCY_LOG fill-rate table.
- **By Oct 31:** Phase 3 flows built; loan/layaway reminders dark pending approval; win-back and welcome series live. Proof: first triggered sends logged with per-contact flags.
- **Dec 1:** first `brevo-stage-next-quarter` run stages Q1 2027. Proof: 13 new drafts pass preflight.

## 7. What this changes for Joshua day-to-day
Nothing new to do. Monday prompt, Monday confirmation DM, Friday numbers — unchanged. Three approvals above, once each. The department stops needing a rescue every quarter because the road never ends, the audience is real people, and the highest-value emails fire themselves off Bravo data.
