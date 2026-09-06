# Email Department — Full Review & Automation Plan
**Date:** 2026-09-05 · **Status:** PLAN — awaiting Joshua's go before any build
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

### Phase 0 — Hygiene, this week (zero risk, no new sends)
1. Retime `monthly-we-buy-gold-silver-email` so the send lands **9:00 AM ET** on the 1st (fixes F1).
2. Rename orphan drafts 43/49/23/1 to `[PARKED — do not send]` and strip their recipient lists (F7).
3. Rewrite Step 5 of `vp-deal-of-week-monday-pick` to the proven WordPress photo path; remove the dead `/v3/media` instruction (backup first) (F6).
4. Confirm whether `#email-campiagns` and `#email-campaigns` are one channel or two; point every task at one (F8).
5. Add the Thursday send and the Friday audit to Fleet Guardian's `expected_outputs.json` so silent misses are caught within 12h.
6. Set reply-to per store on the store-spotlight drafts (store@fcfpawn.com already exist and are monitored by `daily-unopened-email-eval`) (F9).

### Phase 1 — Never run out of road (Sep)
7. **New task `brevo-stage-next-quarter`** — quarterly. Drafts 13 weekly campaigns from Master Template 11 using the theme calendar (store spotlights ×5, gold, loans, layaway, warranty, seasonal), assigns CONCRETE/GENERIC subject styles per the experiment rules, wires lists 7+10+waves in rotation, names them so draft-guard and the picker match. First run: **Dec 1** for Q1 2027. Runs preflight on every draft it creates.
8. Raise draft-guard's runway floor from 4 → 8 weeks so a stall is caught with two months of margin.
9. **Engaged v2 list** (F5): membership = clicked a call/text/CTA link (not the logo, not the unsubscribe mirror) in ≥1 send in 90 days, *and* the click was ≥60s after delivery. Built as a new list, populated by a new weekly script, compared to list 7 for 4 weeks, then the draft-guard target flips. List 7 kept as-is until then.

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
- **Week of Sep 7:** Phase 0 complete. Proof: Oct 1 gold send lands at 9 AM; Sep 10 send reaches ~2,400 (first wave test).
- **By Sep 30:** Phase 1 built; Engaged v2 populating. Proof: draft-guard reports 8+ weeks runway; v2 vs list 7 comparison in EFFICIENCY_LOG.
- **By Oct 15:** Phase 2 cell live daily; attribute coverage on engaged list >85% names/store, DOB and due dates populated. Proof: EFFICIENCY_LOG fill-rate table.
- **By Oct 31:** Phase 3 flows built; loan/layaway reminders dark pending approval; win-back and welcome series live. Proof: first triggered sends logged with per-contact flags.
- **Dec 1:** first `brevo-stage-next-quarter` run stages Q1 2027. Proof: 13 new drafts pass preflight.

## 7. What this changes for Joshua day-to-day
Nothing new to do. Monday prompt, Monday confirmation DM, Friday numbers — unchanged. Three approvals above, once each. The department stops needing a rescue every quarter because the road never ends, the audience is real people, and the highest-value emails fire themselves off Bravo data.
