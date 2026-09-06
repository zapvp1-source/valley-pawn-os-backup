# eBay Department — Full Review + Automation Plan

**Date:** 2026-09-05 · **Status:** PLAN ONLY — nothing built, nothing changed on eBay, no Slack posts.
**Scope:** all 5 store accounts (`valley_pawn_culpeper / _roanoke / _waynesboro / _harrisonburg / _lexington`), every task, script, agent, channel, and document that touches them.
**Method:** enterprise-map protocol; every SKILL.md, plist, and script copy read; verified against Slack `#ebay-performance` output, launchd logs, and the live state files on the Mac — not run records (Rule 12).

---

## 1. What the department is (in numbers)

| | 6/29 | 8/22 | 9/4 |
|---|---:|---:|---:|
| Active listings (5 stores) | 616 | 514 | 453 |
| 90-day revenue | — | $82,064 | $86,354 (8/31) |
| 90-day fees | — | $13,617 (16.6%) | $14,306 (16.6%) |
| Aged >90 days | 41% of active | 207 / $27,255 | 205 / $23,401 |
| Channel sell-through (30d) | — | 34% | 41% |

August 2026: **$30,080 / 174 orders / AOV $173** — Culpeper $11,534 · Roanoke $8,492 · Lexington $5,254 · Harrisonburg $2,977 · Waynesboro $1,822. Run-rate ≈ **$330K/yr**.

Structure: Culpeper carries 59% of listings for 31–38% of revenue at $27–42/listing; Lexington/Waynesboro/Harrisonburg make $182–433/listing on 26–37 listings each — **supply-constrained, not demand-constrained.** Roanoke is the pace store (71% sell-through, 5 days to sell).

## 2. What exists today (the inventory)

### Automation — 3 execution layers, 22 moving parts

**Native launchd (no Claude, run whether the app is open or not) — 4 installed**

| Agent | When | Does | Posts to |
|---|---|---|---|
| `ebay-weekly-rankings` | Mon 9:30 AM | MTD sales ranking | #ebay-performance |
| `ebay-daily-listings` | daily 1:30 PM | yesterday's new listings, active count, listed value | **#ebay-listings** (moved 8/21; the CHANGELOG/skill still say #ebay-performance) |
| `ebay-efficiency-weekly` | Fri 3:30 PM | sell-through, days-to-sell, aged, rev/listing | #ebay-performance |
| `ebay-markdown-monthly` | 1st 6:00 AM | 10% cut on 90+ day listings, 3 cuts max (the "reprice" half of the Listing-Age Standard) | #ebay-performance |

(`ebay-photo-upscale` disabled. `com.valleypawn.ebay-quality-weekly.plist` exists only as a copy in this folder — **not installed**, never ran.)

**Cowork scheduled tasks — 9 live, 3 retired-but-present**

| Task | When | Does | Writes to eBay? |
|---|---|---|---|
| `weekly-online-store-audit` | Sun 8:06 AM | estate pull; **auto-fixes** returns policy + Best Offer; per-store table | yes |
| `ebay-title-photo-accuracy-audit` | Sun 8:05 AM | title vs photos, all listings; **auto-fixes** confirmed title errors; DMs managers on photo problems | yes |
| `ebay-weekly-quality-fix` | Mon 11:08 AM | new listings: strip intake codes, fix CAPS, rewrite weak titles, fix categories, reorder photos; DM each manager | yes |
| `ebay-weekly-channel-audit` | Mon 11:45 AM | read-only Channel Pulse (sales/fees/quality/TRS/messages/feedback/offers); refreshes dashboard | no |
| `ebay-markdown-terminal-weekly` | Mon 12:24 PM | the "pull" half: flag at 30% floor, 14-day grace, then end listing | yes |
| `ebay-feedback-reply-weekly` | Thu 10:23 AM | replies to unanswered neg/neutral feedback (<12 mo) | yes (permanent) |
| `monthly-ebay-ratings-sweep` | 1st 10:00 AM | scrapes 5 public feedback profiles in Chrome + whichever Seller Hub Chrome is logged into | no |
| `vp-website-shop-nightly` | 7 AM + 3 PM | rebuilds thevalleypawn.com/shop/ from live eBay inventory | no |
| `preston-interactive-assistant` | every 2 h | ad-hoc: can rewrite titles on Preston's request | yes |
| `preston-ebay-feedback-watch` / `ebay-return-policy-retry` / `store-mail-archive-sweep` | — | disabled, superseded | — |

Consumers (read, don't touch eBay): `vp-presence-audit-weekly`, `marketing-ceo-briefing-weekly`, `monthly-eom-recap`, `compile-monthly-minutes`, `sales-tax-monthly-update` (eBay column), `vp-website-shop-weekly-report`.

**Scripts:** ~30 `~/ebay_*.py` in the home folder + ~45 in this project folder. Credentials in `~/.vp_secrets/` (Trading Auth'n'Auth tokens ×5; one 2-hour REST OAuth token for Lexington only).

**Policy:** *eBay Listing-Age Standard (Reprice & Pull)* — signed by all 14 employees via Gusto 8/5. "Reprice at 30 days. Reduce or relist at 60. Pull or final-relist at 90."

**Publications:** 5 different producers post into `#ebay-performance` (rankings, efficiency, online-store audit, channel pulse, markdown floor + monthly ratings + monthly markdown). All verified live in the channel this week.

## 3. What's wrong — findings ranked by what they cost

### A. Money on the table (ops/strategy, unchanged since June)
1. **Top Rated Plus: 0 of 453 listings qualify.** Needs 1-day handling (we're at 2–3 days) + free returns (100% buyer-pays). **$3,600–5,200/yr** in fee discount; capturing it only on listings ≥$100 nets ~$3,600 with a fraction of the return exposure.
2. **Promoted Listings dark at 4 of 5 stores** — $0 on ~$57K/90d of sales; Culpeper alone spends $400/90d. Pay-per-sale, bounded downside. Flagged 6/29, 8/22, 8/31 — still no decision.
3. **Culpeper is the aging problem** — 149 listings / $17.8K over 90 days (45% of its catalog), $42 rev/listing. 40% of channel orders are sub-$50 (8.5% of revenue) and most are Culpeper: each one costs a photo session, a listing, a label, and a slot in the ship queue.
4. **Lexington Below Standard** (late-ship 4.23% vs 3%) — re-evaluated **9/20**. Search demotion in effect now.

### B. The listing-creation side is blind
5. **Bravo ↔ eBay link is being destroyed, not used.** Every Bravo-created listing carries the Bravo item number in its title, e.g. `(VAP031234)`. `ebay-weekly-quality-fix` **strips it** for cosmetics, and the eBay **SKU field is empty on 100% of listings at all 5 stores** (both audit weeks). Net effect: no automated way to tie an eBay sale to a Bravo item, no cost-basis floor for markdowns/Best Offers, no double-sell detection. BUSINESS_OS still lists "no Bravo↔eBay sync verification" as an open gap — this is why.
6. **No traffic data at all.** Impressions/CTR/conversion are invisible (Trading API deprecated `HitCount`; REST analytics needs OAuth scopes). Every listing-quality decision is made without knowing whether anyone saw the listing.
7. **Listing quality still below our own written standard:** photos avg 5.8 vs 8–12 (64–92% of listings short, Roanoke worst); item specifics median 4 (155 listings ≥$100 with <5 specifics = $67K staged in `SPECIFICS_FILL_QUEUE.md`, never applied); titles avg 63/80 chars.
8. **Buyer messages unmonitored** — 387 unread over 60 days incl. 23 return/refund notices (8/31); Roanoke 157. Unwatched return notices are exactly how "cases closed without seller resolution" happen (Lexington has 2).

### C. The automation is duplicated, not robust
9. **Four independent title writers, two unlinked undo ledgers** (`ebay_title_stripper/caps_fixer` → `ebay_title_state.json`; `ebay_title_revise` → `ebay_toolfix_state.json`; plus Preston's assistant). Sunday 8:05 and Monday 11:08 can both rewrite one listing; a `--revert` in one can't see the other. The 8/22 incident (17 live titles changed by "verifying" a script) came from this sprawl.
10. **Six separate state files** (`markdown_state`, `markdown_terminal_state`, `vp_ebay_fix_state`, `title_state`, `caps_state`, `toolfix_state`, `feedback_answered`…), no lock, no single "what did we change to this listing and when" ledger. The 9/5 double-cut (63 items took two 10% steps in one day) is the same class of bug.
11. **Five producers, one channel, near-identical KPIs** — Sun audit, Fri efficiency, Mon rankings, Mon pulse, Mon floor check, all into `#ebay-performance`, from 4 different pull scripts with two look-alike output folders (`weekly_audit/` vs `audit_weekly/`). Each pull hits all 5 stores' APIs separately (Sun 8:05 and 8:06 run concurrently). Monthly: 2 more posts (ratings sweep, markdown) + EOM recap.
12. **Ratings/standards sweep is structurally broken** — it reads Seller Hub from whatever account Chrome is signed into (August: Lexington only; September: none). Headless path (`seller_standards_profile`) returns 403 until each store completes OAuth consent. Only Lexington has, and only a 2-hour token with no refresh token.
13. **Category fixes are unreliable by design** — eBay's catalog auto-reverts, mandatory `Type` specifics block, 9 of 9 failed 8/17. Still attempted every Monday.
14. **Judgment work runs on Claude where a script would do** — markdown, returns/Best-Offer drift, caps/intake-code cleanup, KPI math and formatting are all deterministic but several are inside Sonnet tasks (cost, 3-slot queue skips, model drift in table formatting — the same failure class as the 8/31 aged-inventory post).

### D. Hygiene (fix this week regardless)
15. **Plaintext store Gmail passwords** in `Scheduled/store-mail-archive-sweep/SKILL.md` run logs **and** in the 2026-08-24 row of `Life OS/OPEN_ITEMS_REGISTER.md`. Scrub both; rotate (the 8/14 rotation predates these entries).
16. `~/ebay_daily_listings.py` line 34 still hardcodes a Slack webhook literal (contradicts the "zero residual literals" migration note). Move to `~/.vp_secrets/`.
17. Stale docs: skill/CHANGELOG say daily listings post to #ebay-performance (it's #ebay-listings); BUSINESS_OS Domain 7 gap list is stale (listing-health audit exists twice over); `ebay-ratings-sweep` writes to a non-existent "Online Store" project; `ebay-quality-weekly.plist` copy is dead weight.
18. Open item never closed: Roanoke `307000372642` title fix failed twice ("cannot be modified"); Harrisonburg `385626892405` photo wrong after 3 manager notices; `ebay-return-policy-retry` fully absorbed by the Sunday audit (archive).
19. Active listings shrinking 616 → 453 over 10 weeks with no explanation anywhere — nothing reports net change (new − sold − ended − pulled).

---

## 4. Expert board

**PANEL:** marketplace-integration engineer (eBay APIs), SRE / data-pipeline lead, a 5-store e-commerce ops manager.

**OPTIONS WEIGHED**
- *Keep patching the 22 parts individually* — for: zero migration risk; against: the duplication is the cause of the incidents, and every new fix adds a 7th state file.
- *Replace everything with one Claude "eBay super-task"* — for: simplest to describe; against: puts deterministic math on a model (Rule 18 exposure), runs only when the app is up, cost.
- *One native eBay engine (snapshot → rules → apply → publish) with Claude reserved for judgment* — for: one pull, one ledger, one lock, runs without Claude, deterministic posts; against: 3–4 weeks of build, needs a shadow-run before cut-over.

**DECISION:** the engine. Build it additively alongside the current stack, shadow-run for one full weekly cycle, cut over one publication at a time, retire the duplicates only after their replacement has posted twice.

**REJECTED:** rewriting the markdown engine into Claude (it's the best-hardened piece we have — it becomes the engine's first module, untouched logic); auto-filling item specifics from titles (the 8/22 incident lesson — only from eBay's catalog match or a photo-verified fact); a "feedback auto-reply without review" (permanent, public — stays Claude-drafted, rule-gated).

---

## 5. The target design — one eBay engine, four layers

All native Python 3.9 (`/usr/bin/python3`, stdlib only, launchd), in `Projects/eBay/engine/`. Reads credentials from `~/.vp_secrets/`. Claude tasks only where judgment is needed.

**Layer 1 — Snapshot (`ebay_snapshot.py`, nightly 5:00 AM + on-demand).** One pull per store per day: active listings with `GetItem` detail (price, offers thresholds, returns, handling, photos count, specifics, SKU/ApplicationData, start date, watchers if exposed), 90-day orders, fees (`GetAccount`), feedback, messages, open Best Offers, seller standards (REST, once consented). Written to `engine/data/YYYY-MM-DD/<store>.json` + `latest/`. Everything downstream reads the snapshot — eBay is hit once, not five times.

**Layer 2 — Rules (`ebay_rules.py`).** Deterministic evaluation of every listing against the two written standards, emitting an action queue with a reason per row:
- Listing-Age Standard: day 21–30 → send offer to watchers / first 10% cut; day 60 → second cut; day 90 → third cut; at floor + 14 days → end listing (existing markdown + terminal logic, moved in as-is; `MIN_DAYS_BETWEEN_CUTS` kept).
- Policy drift: returns not 30-day, Best Offer off, thresholds not 90/75 — auto-fix (already proven safe).
- Mechanical title hygiene: intake code → **moved into SKU** (not deleted), CAPS normalised, duplicate-title suffix.
- Flags (no auto-write): photos <8, specifics <5, title <60 chars, category mismatch, listing not in Bravo active inventory, Bravo item sold in-store while still listed (double-sell), unread return/refund message, open Best Offer expiring <48 h, feedback needing a reply.
- Cost floor: once SKU = Bravo item number, cost from the Bravo pipeline's inventory CSVs; no cut or auto-accept ever goes below cost + fees.

**Layer 3 — Apply (`ebay_apply.py`).** Executes only whitelisted deterministic actions from the queue. One lock file, one append-only ledger `engine/ledger.jsonl` (listing, action, before, after, run id, reversible-by) replacing the six state files; `--revert <run id>` for any run; Rule-18 gate (if any store's snapshot is incomplete, that store is skipped, never partially applied). Runs Mon 10:30 AM (weekly) and 1st 6:00 AM (monthly cuts), both launchd.

Judgment actions stay with Claude but read the queue and write the same ledger: title-vs-photo corrections (existing Sunday task, re-pointed), feedback replies (existing Thursday task), buyer-message triage drafts (new), Preston's ad-hoc fixes (re-pointed to `ebay_apply.py --title`). One title writer, one ledger.

**Layer 4 — Publish (`ebay_publish.py`).** Deterministic formatters, posted verbatim (the same fix that cured `#aged-inventory-review`):
- **Daily** — #ebay-listings (exists) + a net-change line (new − sold − ended − pulled) so the shrinking-catalog question answers itself.
- **Monday "eBay Weekly"** — ONE post to #ebay-performance replacing rankings + efficiency + online-store audit + channel pulse + floor check: MTD sales ranking, sell-through/days-to-sell/aged, what the engine fixed this week, what needs a human (offers expiring, return messages, photo problems), TRS/standards per store.
- **Monday manager DM** — one DM per store manager (and Preston roll-up) replacing the three separate DM streams: fixed for you / needs you / your aging items due to pull.
- **Monthly "eBay Month"** (1st 10:30 AM) — markdown results + ratings/standards + month totals; feeds `monthly-eom-recap`.
- Dashboard artifact "eBay Channel Pulse" rebuilt from the snapshot.
- Guardian: every publication registered in `fleet/expected_outputs.json`.

**Access unlock (prerequisite for standards, traffic, promoted listings):** build the OAuth authorization-code flow with refresh tokens (`engine/ebay_oauth.py`) so all 5 stores hold a self-renewing REST token with `sell.analytics`, `sell.marketing`, `sell.finances`, `sell.inventory`. One Chrome consent per store using saved passwords — Claude runs it; Joshua only needed if a store prompts 2FA.

## 6. Sequence

| Phase | Window | Build | Retire (only after replacement posts twice) |
|---|---|---|---|
| **0 — Hygiene** | this week | scrub passwords (2 files), rotate; move webhook literal to secrets; fix stale docs; archive `ebay-return-policy-retry`; delete dead plist copy; close/route the 2 stuck listings; add net-change line to daily post | — |
| **1 — Access + link** | wk 1–2 | OAuth refresh-token flow, consent 4 remaining stores; snapshot layer live; intake-code → SKU migration (all active listings, reversible); Bravo↔eBay reconciliation report (first real read of double-sells / cost floors) | `monthly-ebay-ratings-sweep` (Chrome scrape) → headless standards in snapshot |
| **2 — Engine** | wk 2–3 | rules + apply + ledger; markdown engine and terminal action moved in unchanged; returns/Best-Offer drift moved in; caps/intake hygiene moved in; **shadow-run dry alongside existing tasks for one full week, diff the queues** | `weekly-online-store-audit`'s fixer half, `ebay-weekly-quality-fix`'s mechanical half, launchd `ebay-markdown-monthly` + `ebay-markdown-terminal-weekly` (logic preserved) |
| **3 — Publications** | wk 3–4 | eBay Weekly, manager DM, eBay Month, dashboard from snapshot; guardian entries | `ebay-weekly-rankings`, `ebay-efficiency-weekly`, `ebay-weekly-channel-audit`, remaining halves of the Sun/Mon tasks |
| **4 — Growth levers** | wk 4–6 | send-offers-to-watchers at day 21 (policy already says so); Promoted Listings campaigns via API at the 4 dark stores (**after your budget call**); item-specifics fill from eBay catalog match only (verified, ≥$100 first); buyer-message triage → same-day manager DM for returns/refunds; photo-count nudges in the Monday DM | `SPECIFICS_FILL_QUEUE.md` manual queue |

What stays exactly as is: `ebay-title-photo-accuracy-audit` (re-pointed to the ledger), `ebay-feedback-reply-weekly`, `vp-website-shop-nightly` (moves to the snapshot as its source, later), `preston-interactive-assistant`.

Result: 22 moving parts → **1 native engine (4 modules) + 3 Claude judgment tasks**, 6 state files → 1 ledger, 7 weekly posts → 3, 5 API pulls → 1.

## 7. Decisions that are yours (everything else proceeds without you)

1. **Promoted Listings budget** — recommend 2% ad rate at Roanoke/Waynesboro/Harrisonburg/Lexington on listings ≥$100, review after 30 days. Pay-per-sale; expected cost ≈ $100–150/month against ~$19K/month of currently-unpromoted sales.
2. **Top Rated Plus ops policy** — 1-business-day handling + free 30-day returns on listings ≥$100. Recommend sequencing: after Lexington clears on 9/20 and only where the store can actually ship next-day (Roanoke first, it's at 3 days).
3. **Culpeper intake floor** — stop listing items under $50 on eBay (route to in-store/bundle). Merchandising call.
4. **Pull destination** — when the engine ends a 90-day/30%-off listing, where does the item go (back to the counter at the marked-down price, bundle, wholesale)? Needed so the Monday manager DM tells them what to do with it.
5. **Manager DM cadence** — one Monday DM per manager with fixed/needs-you/aging (default yes).

---

*Detail sources: `eBay_Channel_Audit_2026-08-22.md`, `EBAY_ACCOUNT_HEALTH_2026-09-05.md`, `audit_weekly/2026-08-31/summary.md`, `weekly_audit/2026-09-04/summary.md`, `WEEKLY_QUALITY_FIX_LOG.md`, `eBay_Listing_Age_Standard.md`, the 14 task SKILL.md files, 4 plists, `#ebay-performance` history 8/4–9/5, launchd logs on the Mac.*
