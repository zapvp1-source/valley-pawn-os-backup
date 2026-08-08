# Open Items Register — Every Drafted/Sent Thing, All 3 Domains

**Backfilled 2026-08-07** from `Valley Pawn OS/CHANGELOG.md`, `Valley Pawn OS/BUSINESS_OS.md` gap
analysis (Section 8/9 "(G)" bullets), and the `Life OS/REAL_ESTATE_OS.md` / `Life OS/PERSONAL_OS.md`
files — the rows below predate this register's creation and use the same source dating where the
changelog gave one; items pulled from gap-analysis sections with no changelog date use "—".

**Created:** 2026-08-07, directly in response to the Culpeper lease miss — a session pulled the
lease correctly but didn't know a renewal notice had already been drafted, because that fact
lived only in a Drive file nothing pointed to. Building a bespoke tracker per topic (leases,
insurance, permits, warranties...) doesn't scale — there are too many categories. **This file is
the general-purpose fix: one running log, checked every time, instead of a new file per topic
discovered after the fact.**

**The rule going forward (see `enterprise-map` and each context skill):** any time a session
drafts a letter, sends an email, submits a notice, creates a contract, or starts something with a
pending follow-up — in ANY of the 3 domains — it logs a row here **before ending its turn**, not
after being asked. This is what makes the register worth checking: it's current because writing
to it is mandatory, not optional cleanup.

**How to use this file:** before answering any question that could have a "did we already do
this" angle — not just leases, anything with a pending action — scan the OPEN table below first.
It's short by design; if it gets long, that's a sign to close out or archive resolved rows, not to
stop maintaining it.

---

## OPEN (unresolved or status unconfirmed)

| Date logged | Domain | Item | Status | Next action / what would close it |
|---|---|---|---|---|
| 2026-07-21 | 1 — Valley Pawn | Culpeper lease renewal option notice | **Drafted** (docx + PDF in Drive). Send/landlord-response status **unconfirmed** — filename says DRAFT, no confirmed-sent evidence found yet. | Verify via Gmail Sent or ask Joshua directly; update `STORE_LEASES.md` and this row once confirmed. |
| 2026-08-07 | 1 — Valley Pawn | Bald Rock DocuSign contract bug fix (pool-towel clause contradiction, check-in time mismatch, "three (2) nights" typo) | Corrected PDFs staged (`Airbnb_Rental_Contract_CORRECTED_2026-08-07.pdf`, `VRBO_Rental_Contract_CORRECTED_2026-08-07.pdf` in `Short Term Rental Optimization/`). **NOT yet uploaded to live DocuSign templates** — needs Joshua's Touch ID once (passkey-only account, no saved Chrome password). | Joshua does the one-time DocuSign login; then upload corrected PDFs to templates `cf0bdcb8-…` / `c264e23c-…`. |
| 2026-08-07 | 1 — Valley Pawn | Bald Rock listing "Minimum age 30 (ID verified)" — nothing currently verifies ID | Flagged, not built. DocuSign ID Verification (IDV) is the natural fix (~$2.50+/verification), blocked on the same DocuSign login above. | Same DocuSign login unblocks this; then a real build decision (cost/on for all guests?). |
| 2026-07-23 | 1 — Valley Pawn | Harrisonburg Facebook page merge (legacy page `474248069342834` → `795439020329931`) | Consolidation plan written, not yet executed per `valley-pawn-context`. | Run Facebook's Page Merge tool; see `valley-pawn-context` for full steps. |
| 2026-08-03 | 1 — Valley Pawn | Apple Business Connect — missing suite numbers (Harrisonburg "Ste 22", Roanoke "Suite C", Waynesboro street name wrong) | Identified, editable, **not yet fixed** in the console. | Log into Apple Business Connect and correct the 3 addresses. |
| 2026-08-03 | 1 — Valley Pawn | Legacy "Dixie Pawn Inc." record on MapQuest (owner-verified) | Identified, needs a claim dispute filed. Not started. | File MapQuest claim dispute to correct/remove. |
| — | 1 — Valley Pawn | Meta Business Verification (Articles of Incorporation + EIN letter) | Portfolio `221863965111592` still `not_verified`. | Submit verification docs to Meta. |
| 2026-08-07 | 1 — Valley Pawn | `STORE_LEASES.md` tracker built, but Harrisonburg/Lexington/Roanoke/Waynesboro rows are TODO placeholders | Culpeper is the only store actually located/populated so far. | Locate and populate lease docs for the other 4 stores in Drive. |
| 2026-08-07 | 1 — Valley Pawn | Culpeper and Roanoke not yet on Zoom Phone | Only Lexington (via Joshua's ext 800), Harrisonburg, Waynesboro are live. Joshua said "will have them at 5 soon." | No action needed from Claude — `zoom-voicemail-alert` auto-picks up new lines each run once Joshua/Zoom adds them. |
| 2026-08-07 | 1 — Valley Pawn | Skill auto-triggering (`enterprise-map`) is probabilistic, not guaranteed to fire every session | Known limitation, told to Joshua directly. Deterministic fix requires an addition outside this session's write access. | Joshua adds a line to his global Cowork instructions forcing `enterprise-map` to load first, unconditionally. |
| 2026-08-05 | 1 — Valley Pawn | Duplicate Gusto policy templates: ROC "Late to work" (should be an Individual doc, not Team), Overtime Policy (6984272 vs 6984265), Gold Scrap Bucket Naming (7893283 vs 7893330) | Flagged — Gusto exposes no delete/archive via API, so retiring a duplicate is a manual UI click Joshua has to make. | Joshua picks the record copy for each pair; manually retire the loser in the Gusto UI. |
| 2026-08-05 | 1 — Valley Pawn | `policy-lifecycle` skill DELTA patch staged (send-in-Gusto-before-announce-in-Slack gate) | Patch file staged at `Human Resources/policy-lifecycle_DELTA_2026-08-05.md`; skills aren't editable from a session. | Joshua applies the patch via Settings → Capabilities. |
| 2026-08-04 | 1 — Valley Pawn | HAR gold-scrap Feb/March 2025 collection weight still genuinely missing (2 buckets, periods 2025-03/2025-04) | Remaining gap after the multi-day backfill/dedup investigation — no independent backup source exists. | Targeted live re-pull of those 2 specific bucket instances, verified by screenshot rather than an automated read. |
| 2026-08-04 | 1 — Valley Pawn | Cross-store missing-weight gold-scrap gap: 16 buckets across CUL/LEX/ROA/WAY, Feb–Jun 2026, never successfully weight-read | Pre-existing, unrelated to the HAR fix; excluded from totals so not urgent, but still open. | Dedicated cross-store re-pull pass at some point. |
| 2026-08-04 | 1 — Valley Pawn | `weekly-website-kpi-artifact-refresh` flipped enabled→disabled the same day as `eom-bravo-gl-export` | `eom-bravo-gl-export`'s cause was confirmed transient and fixed; this one's cause was never confirmed. | Confirm cause and re-enable if appropriate. |
| 2026-08-03 | 1 — Valley Pawn | `sales-tax-monthly-update` (July 2026 cycle) blocked — `Sales Tax.xlsx` not updated that cycle | Blocked on a GL hang that was fixed 2026-08-04; unclear whether the cycle was ever re-run. | Confirm whether the update has re-run post-fix; update `Sales Tax.xlsx` if not. |
| 2026-08-03 | 1 — Valley Pawn | VA pay-transparency remediation incomplete: employment application + interview scripts still contain salary-history questions | Careers page, social posts, and the Gusto policy were fixed; these two artifacts were not. | Remove salary-history questions from the application and interview scripts. |
| 2026-07-27 | 1 — Valley Pawn | Old master "Policies & Procedures" doc (pre-update version) not deleted from Drive | Flagged — no delete/trash tool available in session. | Joshua manually deletes/archives the old file. |
| 2026-07-27 | 1 — Valley Pawn | Layaway Yield Slack post flagged as unclear by Preston/Walker | Unresolved — needs a week-over-week comparison, not a point-in-time number. | Redesign the post format to show WoW trend. |
| 2026-08-04 | 1 — Valley Pawn | `vp-content-batch-weekly` approval-pause bug not root-caused at the trigger level | Mitigated with a "no-pause canary" workaround only, not actually fixed. | Root-cause the trigger-level pause bug. |
| 2026-08-04 | 1 — Valley Pawn | Bravo "Post button" UI-automation bug (post-to-accounting-post step) | Still open/intermittent per `BRAVO_KNOWN_ISSUES.md`. | Fix pass on the AHK click-detection logic. |
| 2026-07-27 | 1 — Valley Pawn | Jewelry Count Policy Gusto e-signature rollout to all store staff | Was "in progress" as of 7/27; completion status unconfirmed. | Verify signature completion rate in Gusto. |
| — | 1 — Valley Pawn | No cross-store anomaly-alert / drift-detection dashboard | Identified gap (`BUSINESS_OS.md` Section 9), not yet started. | Build a rolling-average comparator on existing pipeline data (~3 hr estimate). |
| — | 1 — Valley Pawn | No monthly email-performance digest (Brevo) | Identified gap (Section 8), not yet started. | Build a digest pull from Brevo (~1 hr estimate). |
| — | 1 — Valley Pawn | No vendor performance scorecard (lead time, defect rate, margin) | Identified gap, not yet started. | Combine new-inventory tracker + Bravo sell-through data (~2 hr estimate). |
| — | 1 — Valley Pawn | No customer-tier segmentation (A/B/C/D by redemption history) | Identified gap, deliberately deferred pending the current Loan Portfolio project. | Build once the Loan Portfolio project completes (~4 hr estimate). |
| — | 1 — Valley Pawn | No real-time P&L / weekly finance dashboard | Identified gap, not yet started. | Assemble a weekly QBO snapshot (~4 hr estimate). |
| — | 1 — Valley Pawn | No eBay listing-health audit (stale/mispriced listings) | Identified gap, not yet started. | Build an audit pass (~3 hr estimate). |
| — | 2 — Real Estate | Jacksonville, FL prospective-acquisition property search | `weekly-jacksonville-property-search` scheduled task is built but on-disk/unregistered — never fires. | Decide whether to register the task or replace it before doing new Jacksonville work. |
| — | 2 — Real Estate | St. Augustine / St. Johns County, FL prospective-acquisition property search | `weekly-st-augustine-property-search` scheduled task is built but on-disk/unregistered — never fires. | Decide whether to register the task or replace it before doing new St. Augustine work. |
| — | 2 — Real Estate | Cost segregation study for Bald Rock + Cypress Crossing portfolio | Readiness package prepared (`Portfolio_Cost_Seg_Readiness.docx`, `Bald_Rock_Cost_Seg_Intake_Package.docx`); not yet engaged with a cost-seg firm. | Joshua decides whether to move forward and engage a provider. |
| — | 2 — Real Estate | Bald Rock capital-improvement substantiation gap ($110,673.74 invoiced-not-proven, ~$176,000 quoted-only, against a $305,086.51 claimed total) | Documented in the Full Evidence Log; unresolved for tax/basis purposes. | Chase down proof-of-payment for the invoiced/quoted amounts before filing. |
| — | 2 — Real Estate | Cypress Crossing capital-improvement substantiation gap (~$289,912.80 quoted/estimated, not proven paid; Manning Building Supply doors possible double-count) | Documented in the substantiation log; unresolved for tax purposes. | Chase down proof-of-payment; resolve the Manning Building Supply double-count before filing. |
| — | 3 — Personal | No personal net-worth tracker / personal cash-flow-runway view / consolidated personal-vs-business exposure view | Identified gap (`PERSONAL_OS.md`), not yet started. | Build if/when Joshua asks for one. |
| — | 3 — Personal | Unconfirmed whether Silverline Tax (CPA) also prepares Joshua & Hillary's personal 1040 | Status unconfirmed. | Confirm scope directly with Silverline Tax. |
| — | 3 — Personal | Unconfirmed whether personal (non-FCF-Inc) finances are tracked anywhere — QBO is only confirmed for FCF Inc books | Status unconfirmed. | Confirm with Joshua before assuming QBO covers personal finances. |

---

## RECENTLY CLOSED (kept briefly for reference — trim once stale)

| Date logged/resolved | Domain | Item | Resolution | How verified |
|---|---|---|---|---|
| 2026-08-07 | 1 — Valley Pawn | `zoom-voicemail-alert` was posting to #general for lack of a dedicated channel | Joshua created `#voicemails-missed-calls` (`C0BND1NK65V`); task updated to post there instead. | Task prompt/description updated via `update_scheduled_task`; `ZOOM_PHONE.md` updated. |
| 2026-08-05 | 1 — Valley Pawn | Two Gusto policies (eBay Listing-Age Standard, Gold Scrap Bucket Naming) had been announced in Slack but were sitting unsent in Gusto with zero recipients | Both sent as Team documents to all 14 active employees. | Live Gusto API check: `approved` status, 14 requests, all `requested`. |
| 2026-08-03 | 1 — Valley Pawn | VA pay-transparency law (effective 7/1/26) — hiring content lacked wage ranges | Careers page + JobPosting JSON-LD updated, 11 live social posts patched via Publer, Gusto policy HR-2026-03 published (14 signatures requested), preflight guardrail added to `brevo_preflight.py`. | Live re-pull of edited posts (3 platforms visually confirmed); preflight guardrail run live, correctly failed/passed test campaigns. |
| 2026-08-03 | 1 — Valley Pawn | Brevo hiring campaign #51 believed to be a live pay-transparency violation | Confirmed the campaign was suspended before it ever sent — no violation existed. | Live Brevo API check: status suspended, 0 sent/delivered. |
| 2026-08-03 | 1 — Valley Pawn | Bing Places description errors (Lexington phantom "Salem" location + over-limit, Harrisonburg typo + over-limit) | Both descriptions corrected; all 5 listings confirmed Published with correct addresses. | Re-read from console after save. |
| 2026-08-03 | 1 — Valley Pawn | Apple Business Connect status was believed unclaimed | Retracted — confirmed claimed under Full Circle Finance Inc., all 5 locations Verified. | Opened live console directly. |
| 2026-08-03 | 1 — Valley Pawn | Publer API returning 403 errors | Root cause found (missing browser User-Agent header, Cloudflare block) and fixed. | Reproduced the 403, then got 200 immediately after the fix. |
| 2026-08-04 | 1 — Valley Pawn | Q1 2026 Bravo GL lump-sum journal entries misallocated revenue into March | Reversed all 5 stores' Q1 lump JEs, posted 15 classed monthly JEs, redated reversals into the correct period. | Direct QBO P&L pull, Jan–Jul 2026 all landed in a normal band. |
| 2026-08-04 | 1 — Valley Pawn | `eom-bravo-gl-export` failing for all 5 stores since 8/1 | Root cause found (unposted-date dialog silently swallowed) and fixed. | All 5 stores' July Consolidated GL exported cleanly, CSVs confirmed on disk. |
| 2026-08-04 | 1 — Valley Pawn | July 2026 Bravo GL revenue/COGS not yet posted to QBO | Posted classed JEs for all 5 stores. | Verified against live July P&L — income/COGS tie out exactly. |
| 2026-08-04 | 1 — Valley Pawn | Inflated scrap-rankings YoY/YTD figures (+84%/31%) had been posted publicly | Retraction posted to #scrap-rankings with corrected, honest figures. | Recomputed from recovered/deduped source data. |
| 2026-08-04 | 1 — Valley Pawn | Believed Waynesboro/Roanoke Instagram posts were missing from a weekly batch | Confirmed false — all 29 platform posts were correctly scheduled/published. | Re-verified each Publer post ID directly. |
| 2026-08-03 | 1 — Valley Pawn | Team-facing Slack posts contained jargon, build-log content, and audit narration | Field Communication Standard v3 shipped; 27 tasks audited/updated, 4 routing contradictions fixed. | Comms audit against the v3 standard. |
| 2026-08-02 | 1 — Valley Pawn | `weekly-store-kpis` was redundantly re-pulling Bravo data already fresh from `daily-loan-inventory-text` | Fixed with a new `bravo_reuse_check.sh` gate. | Audit of output file timestamps confirmed the duplicate-pull pattern and the fix. |

---

## How to log a new item

One row, added the moment something is drafted/sent/started with a pending follow-up:

```
| {date} | {1/2/3 — domain name} | {what, one line} | {status: Drafted / Sent-unconfirmed / Sent-confirmed / Awaiting response} | {the one next action that closes it} |
```

Move a row to RECENTLY CLOSED (with resolution date + how it was verified — not just "done") once
confirmed closed. Don't delete rows outright — a trimmed closed-log is still useful evidence if
the same question comes up again ("did we already handle this?").
