# Forfeited-Loan Win-Back — Consolidated Master Doc

**Consolidated:** 2026-07-10. This file merges everything scattered across prior sessions (Google Drive "Optimize Loan Portfolio" project + this Email Refinement project) into one place so no future session has to re-discover it. Read this file first before touching anything on this initiative.

**Goal (Joshua, 2026-07-10):** Identify Valley Pawn customers who forfeited a pawned item, and market to them specifically — reassuring them there's no shame in not repaying a loan, and that we want them back. Some embarrassment is expected and fine; we don't care, we want them back. Build a repeatable Bravo → Brevo pipeline (same mechanism as every other automated report) and a long-term cadence, not a one-off blast.

---

## 1. Where things stood before this session (found in Google Drive, undocumented in any project folder)

A prior session already did the strategic and creative work. Files live in Drive (not previously linked into this project):

- `forfeited-loan-winback-plan.md` (Drive id `1YQV00zrsZXoz46DlpZWh7AKUWkSZCwhF`) — full strategy: emotional/relationship-only approach, no discount, no item references, channel-by-channel plan (Bravo push, Chekkit SMS, Brevo email, IG/FB, GBP, website), monthly rotating cadence, KPI framework, compliance guardrails.
- `forfeited-winback-copy-pack.md` (Drive id `1WpwOaOWbDtjFAil_ljIz8pDNLAk49rWh`) — ready-to-ship copy: 2 full emails built for VP Master Template 11 (marker fill-ins + body HTML), 3 Chekkit SMS variants, 3 Bravo push lines, 3 IG/FB posts, 3 GBP posts.
- **Status noted in the copy pack itself:** "Audience wiring (Bravo pull → Brevo segment + Chekkit) is on hold until the store-cycle fix lands." — i.e., the entire creative product has been ready and idle for weeks because nobody finished the data pull.

**The approach is locked and should not be redesigned:** relationship-only, no incentive/discount, never reference the specific lost item, never imply fault, no "we miss you" guilt framing. Full detail in the two files above — pull the actual HTML/copy from Drive when building the send, don't rewrite it.

## 2. The Bravo pipeline — what already exists vs. what's missing

Valley Pawn has a working, additive-only Bravo Data Extraction pipeline (AHK automation in a Parallels-hosted Windows VM, triggered by dropping a JSON file, watched and executed by `bravo_watcher.ahk`, output lands as CSV in `Bravo Data Extraction/output/`). This is the same mechanism behind aged inventory, loan/layaway review, daily funds verification, etc. — see `bravo-context` skill and `Bravo Data Extraction/README.md`.

**Already built (from the separate "Optimize Loan Portfolio" project, additive, does not touch any pre-existing saved report):**
- Saved Ad Hoc report in Bravo: **"Claude Loan Portfolio 2026"** (Loans/Buys → Custom Reports), Ticket Kind = LOAN, historical + active.
- Handler: `Bravo Data Extraction/reports/LoanPortfolio2026.ahk`, registered pipeline cell `loan-portfolio-2026` in `bravo_watcher.ahk` and `config.json`.
- **Columns it exports today:** `Ticket Number, Disposition, Disposition Date, Due Date, Pull Date, Customer, Loan Amount, Age, MobilePawn, SMS, Address`. `Disposition` includes `EXPIRED` / `REDEEMED` (forfeiture shows as EXPIRED in this export — confirm exact forfeited-status label during next Bravo session, may also appear as FORFEITED depending on ticket state). `SMS` column is a real consent signal already (`SMS` = opted in, `DNT` = do not text) — useful directly for Chekkit gating.
- **Coverage gap:** data is partial — only some months/stores have been pulled (spans 2025-05 through 2026-05 in patches, not a clean rolling 12-24mo window across all 5 stores). Files: `Bravo Data Extraction/output/*_loan-portfolio-2026.csv`.
- **Missing column:** no Email address. This report was built for ROI/portfolio analysis, not customer outreach, so email was never added to its column layout.

**What Joshua is building right now (2026-07-10, live in Bravo):** a NEW saved Ad Hoc report under the **Customers** module (not Loans/Buys) — Bravo's Customers tab has its own ad hoc/custom report builder that should expose Email + Phone directly on the customer record, which the Loans/Buys report does not. This is the more direct source for a marketable contact list. **Joshua asked to hold on any further computer-use/Bravo actions until he confirms the report is built** — do not resume driving Bravo until he says go.

### Plan once the Customers-tab report is built
1. Confirm exact column set available (Name, Email, Phone, Store, any loan-status/disposition field, SMS/email consent flag if Bravo tracks one).
2. If the Customers-tab report can directly filter to "has a forfeited/expired loan" — pull it directly, all 5 stores, trailing 24 months. Name the saved report distinctly (e.g. **"Claude Forfeiture Winback"**) — additive only, per Rule #4, never touch "Claude Loan Portfolio 2026" or any pre-existing saved report.
3. If it can't filter by loan status (likely — customer records may not join to ticket disposition), pull ALL customers with a non-blank email (all 5 stores), then **cross-reference by name/ticket against the existing `loan-portfolio-2026` CSVs** (which already have Disposition=EXPIRED per ticket) to filter down to the forfeiture-only set. Name matching will need normalization (case, middle names) — flag any ambiguous matches rather than silently guessing.
4. Clone an existing AHK handler (e.g. `LoanReviews.ahk` or `LoanPortfolio2026.ahk`) into a new file for the Customers-tab automation, register a new pipeline cell (additive), restart the watcher, run across all 5 stores via `bravo-store-cycle`.
5. Merge the 5 per-store CSVs, dedupe by customer, filter to forfeited-only, split into "new this month" vs. "rolling pool" (trailing 24mo) per the original plan's monthly-diff logic.

## 3. Brevo side — prepped and ready (done 2026-07-10)

Bridged the Brevo API key from the Mac (`~/.config/valley-pawn/brevo_api_key`, same mechanism as `brevo-key-sandbox-bridge`) and built the receiving infrastructure ahead of the data pull, so the import is a single step once the CSV lands:

- **New list created:** `Forfeited Loan Win-Back` — **list ID 11**, folder 1 ("Your First Folder", same folder as the master `Valley Pawn Customers` list and the Engaged List). Sending to a real list (not a bare segment) avoids the known Brevo API blind-stats bug — see [[brevo-segment-stats-api-blind]].
- **New durable contact attributes created** (category `normal`, so they persist across list moves — per the Phase 2 segmentation design philosophy of "attributes for durable signal, lists for audience-of-the-moment"):
  - `FORFEITED_LOAN` (boolean) — durable flag, survives regardless of which list the contact sits in.
  - `FORFEIT_STORE` (text) — which store the forfeiture occurred at.
  - `LAST_FORFEIT_DATE` (date) — drives the "new this month" vs. "rolling pool" cadence split.
  - `FORFEIT_ROLLING_POOL` (boolean) — true once they've had their first-touch email and entered the ongoing monthly rotation.
- **Not yet done:** no contacts imported (waiting on the Bravo pull), no campaigns drafted in Brevo yet (the HTML/copy exists in Drive, just needs to be duplicated into VP Master Template 11 and scheduled once the list has real contacts).

## 4. Cross-check against other live Brevo work (avoid duplicate sends)

Per [[email-reactivation-duplicate]], Valley Pawn already runs a **general dormant/lapsed win-back** (Win-back 01/02/03, campaigns #32/33/34, ~9,500 recipients) — that is a DIFFERENT audience (anyone inactive) and a different message (generic "come back"). The forfeited-loan audience is a subset that needs its own distinct, more careful message (the "no shame" framing) — **do not fold them into the general win-back send**, and conversely don't let a forfeited customer who's already dormant get double-messaged without realizing it's the same person. When both sequences are live, cross-suppress: a contact actively in the `Forfeited Loan Win-Back` list's first-touch window should be held out of that month's general win-back send, and vice versa isn't necessary (general win-back tone is compatible with also getting the forfeiture email in a different month per the rotation).

## 5. Cadence (from the original plan — don't redesign, just execute)

Monthly rotation, one direct touch per month, varies channel so no one gets hit everywhere at once:
- **Month 1:** Evergreen email — "Here whenever you need us" (copy pack section 1).
- **Month 2:** Chekkit SMS from the customer's own store (copy pack section 3).
- **Month 3:** Bravo push (app users) + second email angle "How pawn protects your credit" (copy pack sections 2 & 4).
- Repeat. New-this-month forfeitures always get the Month-1 email first regardless of where the rolling pool is in the cycle.
- Always-on layer (every month regardless): 1-2 Story/Heritage social posts, 1 trust-first GBP post per store (copy pack sections 5 & 6) — normalizes the message publicly so no one feels singled out.
- **Health brake:** if SMS opt-outs or email unsubscribes climb, drop the rolling pool to every-other-month; new forfeitures stay monthly regardless.

## 6. Open items / next actions (in order)

1. **[Joshua, in progress]** Build the Customers-tab saved ad hoc report in Bravo.
2. Once built: pull all 5 stores, confirm columns, build/clone the AHK handler + pipeline cell (additive), run the extraction.
3. Cross-reference against `loan-portfolio-2026` Disposition data if the Customers report can't filter by loan status directly.
4. Import the clean, deduped, consent-aware list into Brevo list ID 11; set the 4 durable attributes per contact.
5. Duplicate VP Master Template 11, fill markers from copy pack section 1, run `brevo_preflight.py` (mandatory per [[email-send-instrumentation-guard]]), send Month-1 email to the full new list.
6. Set up the monthly rotation as a recurring scheduled task (mirroring how `monthly-we-buy-gold-silver-email` and the deal-of-week tasks work) so this becomes fully self-running — not something to babysit.
7. Pull the current re-transaction rate of forfeited customers from Bravo as the KPI baseline before the first send.

---
*Sources merged into this doc: `forfeited-loan-winback-plan.md`, `forfeited-winback-copy-pack.md` (Drive), `Optimize Loan Portfolio/STATUS.md` (Drive), Brevo API state as of 2026-07-10.*
