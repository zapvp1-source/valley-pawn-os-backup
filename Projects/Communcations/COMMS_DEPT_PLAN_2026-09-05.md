# Communications Department — Full Review + Automation Plan

**Drafted:** 2026-09-05 · **Status:** PLAN — awaiting Joshua's go (nothing built)
**Domain:** 1 — Valley Pawn · **Project:** Communcations
**Method:** Every claim below was verified against the actual Slack channel, file, or audit output (Rule 12), not run records. Sources: `PUBLICATION_CALENDAR.md`, `FIELD_COMMUNICATION_STANDARD.md`, `fleet/expected_outputs.json`, the three Communcations plans, mail-brief STATUS files, the 8/22 marketing / email / online-store audits, live reads of #store-performance and #email-campiagns, Open Items Register.

---

## 1. What the department is today (inventory)

**Internal (Slack) — 62 publications on a fixed calendar**, all owned by scheduled tasks or native agents:
- 12 monthly · ~30 weekly · ~20 daily, across ~45 channels + DMs (`PUBLICATION_CALENDAR.md`).
- Enforcement that exists: Field Communication Standard v3 (routing test, plain language, ~100 words, no footers), Rule 16 (no failure noise), Rule 18 (withhold incomplete data), fleet-guardian + `expected_outputs.json` (twice-daily "did it land" check), Fleet Health Sentinel (native), `vp-comms-drift-monthly-check` (3rd of month), `monthly-eom-recap` (registered 9/5, first live run 10/1), one deterministic formatter (`format_aged_inventory.py`).
- Leadership feeds: `ceo-mail-brief` (2×/day, working — 2 "needs you" items per run, reply-executor live), `marketing-ceo-briefing-weekly` (Mon 11:30), `morning-brief`, `sold-review`/`discount-review`.
- Manager feeds: `weekly-loan-layaway-manager-dms` (hardcoded 5-store roster), nothing else per-store.

**External (customer) — 9 channels**, from the 8/22 audits:
Brevo email (13.2k contacts, Thu weekly + 1st monthly + 17 staged holiday drafts) · Chekkit SMS (Tue review requests, 4–5★ auto-responses) · Facebook/Instagram via Publer (~6 posts/day fleet-wide, median reach 9) · GBP posts (unmeasured) · Google reviews (~21/week, best asset) · website (shop 2×/day, deals Mon, blog Mon/Thu) · eBay ($82k/90d — only channel with attributable revenue) · directory listings (weekly drift check) · Zoom phone (3 of 5 stores; missed-call alerts every 20 min).

**Communcations project folder:** 3 prior plans (Internal restructure ON HOLD 8/24 · Tiered exec brief PLAN ONLY 8/24 · Email triage EXECUTED 8/26–27), 2 daily trend reports (missed calls, missed emails — HTML on disk, not published anywhere), mail-brief run logs.

---

## 2. What's actually wrong (verified findings)

### Internal
1. **Every automated post appears as "Joshua" with a `Sent using Claude` footer.** Verified live in #store-performance and #email-campiagns. This violates the v3 standard ("no signature footers") on every single post, and staff cannot distinguish "Joshua said this" from "the system posted this." The one exception is the `VP OPS ENGINE` bot user, which posted in July and then stopped. Trust problem: three "CORRECTION" cycles since June all appeared under Joshua's name.
2. **Near-zero engagement on team-facing reports.** Weeks of 8-category, 50-number rankings dumps get 0–1 reactions (8/24 restructure diagnosis still holds; the ON-HOLD verdict was "too little info" — the fix is structure, not less data).
3. **Success-noise in channels.** #email-campiagns carries a daily "Email watchdog: all clean" post — that is silent-success material per v3 §1 and it buries the one weekly post that matters.
4. **Hand-rendered tables still drift.** Only aged-inventory has a deterministic formatter. Loan, layaway, employee, FPD (Monday compile) plus most weekly marketing posts are still free-text rendered by the model every run — the exact cause of the illegible 8/31 post (CHANGELOG 9/5 §5).
5. **Multi-writer channels.** #google-reviews (3 writers), #ebay-performance (5+), #email-campiagns (3+), #social-media (3), #website (3), #general (3), #store-performance (2), #loan-review (2), #layaway-review (2). Duplicate-delivery risk is structural, and the 8/24 double post proved it.
6. **No per-store, per-manager brief exists.** Managers receive company-wide data walls; the tiered CEO/Supervisor/Manager brief (8/24 plan) was never built. The 5-store DM roster is hardcoded in one task, not shared.
7. **Trend reports are dead-ended.** Missed-calls and missed-emails HTML reports regenerate daily on disk with zero readers; the same data is posted as raw daily alerts.
8. **`monthly-publication-audit` not registered** (classifier-blocked 3×) — the monthly safety net that the 9/5 audit designed is half-installed.
9. **Fleet pressure.** 148 enabled tasks, 7,876 queue-wait skips/7 days (3-slot dispatch limit). Every new comms task added as a separate task makes the Monday morning stack worse.

### External
10. **Nothing is attributable to revenue.** No Meta Pixel, no GTM, no call tracking, no "how did you hear about us" key in Bravo. GBP — the highest-intent surface — returns zero metrics.
11. **Precision beats volume by 100×, and precision sits idle.** Store Spotlight segments do 11.6–28 calls+texts/1k vs 1.5 list-wide; 5 store segments were built 7/22 and are barely used. Forfeited-loan win-back is fully built (copy 6/15, list 7/10) and has sent 0 contacts in 10+ weeks.
12. **No customer frequency governance.** Same customer can get Thu email + Tue SMS + daily social + GBP the same week; nothing coordinates it. TCPA consent flag for SMS is not verified to exist in Bravo.
13. **Deliverability foundation partly broken.** SPF PermError on fcfpawn.com (two competing records); Brevo bounce/blacklist counters return 0 (stale). DKIM on thevalleypawn.com was fixed 8/23.
14. **Reputation loops are one-sided.** Reviews ≤3★ only got a DM alert after two 1★ reviews sat 2 weeks; 36 old eBay negatives unanswered; 528 unread eBay buyer messages at Lexington; hostile 2021 boosted ad still live on the brand page; Harrisonburg posting to a legacy page (762 followers) instead of the brand page (21).
15. **Website captures nothing** — 0 forms, GA4 `sms_click`/`form_submit` never fire, 1 product live despite working checkout.

---

## 3. Expert Review Board

**PANEL:** corporate-communications director · BI/reporting architect · martech + deliverability engineer · reliability engineer (fleet owner) · brand-risk reviewer.

**Options weighed**
- *A. Keep adding tasks per problem.* For: fastest per item. Against: fleet is already queue-bound; every added Monday task raises skip rates; each new writer adds a duplicate-delivery path. Rejected.
- *B. Big-bang channel consolidation (archive ~10 channels).* For: cleaner surface. Against: destroys the marker/guardian coverage just rebuilt 9/5; team habits break overnight; the 8/24 hold shows Joshua wants density preserved. Rejected as a first move.
- *C. A rendering + routing layer under the existing calendar (recommended).* Keep every producer task and every channel as-is (Rule 4). Add one shared **Comms Engine** (native Python, no Claude tokens) that owns identity, formatting, dedupe, and audience tiering, and let existing tasks hand it data instead of writing Slack themselves. Add customer-side governance the same way — one shared consent/frequency ledger that every outbound channel checks.

**DECISION:** Option C. It fixes the systemic causes (identity, hand-rendering, multi-writer, no audience tiers, no attribution) once, in code, instead of 62 times in prompts, and it is fully additive and reversible (a task switches to the engine one at a time; the old path still works).

**Escalated to Joshua (his by right):** bot identity name; whether managers get a Monday brief (default yes); win-back activation (customer-facing send); channel archive list (Phase 4, later).

---

## 4. The plan — five phases, additive, each proven before the next

### Phase 1 — Identity + rendering foundation (week 1)
1. **Post as a bot, not as Joshua.** Re-activate `VP OPS ENGINE` (or a new "Valley Pawn Ops" bot user) as the sender for every automated post; Joshua's own account posts only what Joshua writes. Kills the footer problem and the "who said this" problem in one move. Add a second bot identity, "Valley Pawn Marketing," for the marketing channels.
2. **`bin/comms_engine.py` (native, stdlib):** one CLI that takes a JSON payload (`channel`, `publication_id`, `data`) and produces the exact Slack body from a per-publication template — header row, TOTAL row, fences, trophy line — with the same gates as `format_aged_inventory.py` (all stores present, reconciles, exit 2 = post nothing). Templates for the 4 remaining Monday tables first (loan, layaway, employee, FPD), then the weekly marketing posts.
3. **Dedupe in the engine, not the prompt:** engine reads the channel for the publication's marker in the cadence window and refuses a second post. Removes the multi-writer risk without touching any producer task.
4. **Silent-success rule enforced in code:** publications flagged `silent_when_clean` (email watchdog, drift checks, listing monitors) post only on exceptions; clean runs write to the STATUS file.
5. Wire `monday-bravo-combined-compile` to the engine for its 4 remaining tables (same pattern as 9/5 aged fix). Backup + CHANGELOG each.

### Phase 2 — Audience tiers (week 2)
6. **Shared roster file** `Valley Pawn OS/ROSTER.json` (store → manager Slack IDs, Preston, Lainie, Joshua) — one source, every task reads it; retire the hardcoded roster in `weekly-loan-layaway-manager-dms` by pointing it here.
7. **Build the tiered brief from the 8/24 plan as ONE task, `weekly-enterprise-brief`** (Mon 11:45, after all producers land), reading the engine's already-verified payloads — zero new Bravo pulls. Tier 1 Joshua (KPI scorecard + opportunity store + decisions waiting from the register), Tier 2 Preston (per-store detail), Tier 3 five manager DMs (~80 words, own store, one focus item). Monthly variant reuses the same code on the 1st. Graceful degradation: missing feed = "not available," never abort.
8. **Team-channel format = headline + takeaway + full table in thread** (the fix the 8/24 hold asked for: keep density, fix structure). Applied via engine templates, not by editing 62 prompts.
9. **Recognition line** in the weekly scoreboard (one shout-out per week, pulled from the same data) — the only thing that has ever drawn staff replies.

### Phase 3 — Safety net + fleet relief (week 2–3)
10. Register `monthly-publication-audit` (needs Joshua's one click — classifier-blocked). Add Phase 1–2 publications to `expected_outputs.json`.
11. **Consolidate Monday marketing posts** into the engine so #social-media / #website / #email-campiagns / #ai-marketing / #ebay-performance each get ONE Monday digest built from their producers' STATUS files, instead of 3–5 separate writer sessions each fighting for a dispatch slot. Producers keep running; only the Slack-writing step moves. Target: −15 to −20 Monday-morning Cowork sessions.
12. Publish the two Trend Reports (missed calls, missed emails) as a single weekly line inside the Monday ops digest + a Slack canvas refreshed weekly; stop the daily raw posts once the weekly line is proven.
13. `vp-comms-drift-monthly-check` extended to score every team-facing post against v3 mechanically (footer present, jargon list, word count, system names) and DM a one-line digest — same task, sharper check.

### Phase 4 — Customer outreach governance (weeks 3–4)
14. **Consent + frequency ledger** (`bin/customer_touch_ledger.py`, keyed on phone/email hash): every outbound send (Brevo, Chekkit SMS, win-back) logs a touch; a preflight refuses any customer who has been touched ≥2× in 7 days or lacks SMS consent. Bravo→Brevo sync adds an SMS-consent attribute (verify the field exists first; if it doesn't, SMS marketing stays review-request-only until it does).
15. **Fix the foundation:** merge the two SPF records into one that includes Brevo; re-verify bounce/blacklist pulls against Brevo's events API instead of the stale counters.
16. **Shift Brevo to precision by default:** weekly send rotates Store Spotlight / 30-Day Warranty on the 5 store segments; list-wide only for the monthly Gold & Silver and holidays. The 17 staged holiday drafts get segment recipients checked by the existing watchdog.
17. **Win-back activation** — staged as a 1-store, 1-channel pilot (email only, Lexington, 30 days) with the ledger enforcing rotation. Goes live only on Joshua's go (customer-facing send).
18. **Reputation loops closed:** ≤3★ review alert already DMs Joshua — add a drafted reply; weekly eBay feedback-reply task (drafts + posts via `RespondToFeedback`, the 9/5 fix proved the path); eBay buyer-message triage sweep (unread > 48h → store DM with count + oldest 3).
19. **Attribution minimum:** GTM + Meta Pixel + GA4 events fixed on the site, one "How did you hear" attribute added to the Bravo→Brevo sync, GBP Insights pulled via the Business Profile API once admin access is fixed. Nothing is "measured" until these exist.

### Phase 5 — Surface cleanup (month 2, on Joshua's approval)
20. Archive channels that Phase 3 has emptied (candidates: #chekkit-unanswered-summary, #supply-order-summary, #mark-downs-summary, #emails-missed, #voicemails-calls-missed — each with a pinned pointer). Only after 4 clean weeks of the digest.
21. Harrisonburg legacy-page merge, remove the 2021 boosted ad, Roanoke profile → page (brand-risk items; irreversible, so listed here for Joshua's go).

---

## 5. What this does NOT touch
No producer task's data pull changes. No Bravo cell added. No channel archived before Phase 5. Every switch to the engine is per-publication with the old path intact (backup + CHANGELOG). Rules 4, 12, 16, 17, 18 and v3 all enforced in the engine rather than restated in prompts.

## 6. Decisions Joshua owns
1. Bot sender name(s) — "VP OPS ENGINE" (exists) or new names.
2. Managers get a Monday own-store brief: yes (default) / no.
3. Win-back pilot: go / hold.
4. Register `monthly-publication-audit` (one click when prompted).
Everything else is executed without check-ins on "go."

## 7. Expected result
| | Now | After |
|---|---|---|
| Sender identity | Joshua's account, footer on every post | Two bot identities, no footers |
| Team-facing posts drifting/duplicating | 8 channels with 2–5 writers | Engine-owned, one writer per publication |
| Per-store manager brief | none | weekly + monthly, ~80 words |
| Monday Cowork sessions (comms) | ~35 | ~15–20 |
| Customer frequency control | none | ledger-enforced, 2 touches / 7 days |
| Attributable marketing revenue | eBay only | email, SMS, web, GBP measurable |
| Monthly safety net | half installed | audit task live + guardian entries |
