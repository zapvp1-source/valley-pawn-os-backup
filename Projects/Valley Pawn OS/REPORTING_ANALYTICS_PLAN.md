# Reporting & Analytics — Robustness Plan

**Date:** 2026-09-05 · **Status:** PROPOSED — awaiting Joshua's go / decisions in §6
**Scope:** every daily/weekly/monthly publication, the Bravo Data Extraction pipeline, the scheduled-task fleet that produces reports, and the watchdog layers.
**Method:** enterprise-map load → full inventory (164 registered tasks, 82 pipeline cells, PUBLICATION_CALENDAR, guardian manifest) → verified against 30 days of results/logs/Slack output, not run records → expert board.
**Evidence files:** `Valley Pawn OS/_reporting-audit-2026-09-05/` (fleet audit, pipeline audit, non-UI research).

---

## 1. What we have (the honest picture)

| Measure (Aug 6 – Sep 5) | Value |
|---|---|
| Bravo pulls fully clean | **61%** (236/386 triggers); 35% partial, 4% aborted |
| Cell failure rate | 21.7% raw / **~18% real** (46 "failures" are genuinely-empty jewelry categories) |
| Share of failures where the report never got a chance (Bravo not ready / nav cascade) | **45%** |
| Bravo VM time consumed by reporting | **40–55 hours/month**; 13 tasks touch Bravo every day |
| Scheduler queue-wait skips | **~8,000/week** (hard 3-concurrent-session ceiling, server-side) |
| Reporting tasks whose Slack table is hand-typed by the model each run | **~85 of ~90** (1 converted to a deterministic script on 9/5) |
| Monthly publications that broke in August | 4 of 12 (+2 unverified) — no safety net existed until 9/5 |
| Guardian output-verification coverage | 38 of ~90 reporting tasks |
| GL → QBO chain (`post-to-accounting-*`) | **0% success** in window (0/17, 0/6) |
| Backups | Time Machine dead since 8/25; disk 97% full; iCloud evicted 27k files incl. 47 task files |

**Root causes, ranked by blast radius**

1. **Everything depends on driving a single Bravo window.** One login, one VM, strictly serial, 82 UI handlers, DevExpress quirks, ClickOnce auto-updates, foreground steals. Nothing in this class is fixable to 99%; it can only be shrunk.
2. **Reports are rendered by the model, not by code.** Header rows vanish, totals get mis-mapped ($123,029 inventory balance posted as an aged total on 8/31), fences break. Rule 18 stops *incomplete* posts; nothing stops *wrong* ones except the one formatter shipped 9/5.
3. **The scheduler is the bottleneck, not the work.** 148 enabled tasks fight for 3 slots; long-running "babysitter" sessions (jewelry 81 min, morning pull 40 min) hold slots doing nothing but waiting for Bravo. Reports due at 8 AM land at 11.
4. **Self-repair is blocked.** The permission classifier stopped 7 fixes on 9/5 alone, including registering the monthly audit net. Chrome-driving tasks stall on approvals and get reaped at 30 min.
5. **Watchdogs check presence, not correctness**, and go blind after 48 h — which is exactly how July *and* August monthly reports were missed.
6. **Redundancy and debris**: store performance posted by 3 writers Monday morning (2 separate Bravo pulls); 5 canvas sessions; on-disk-unregistered tasks still referenced by live tasks (`weekly-store-kpis` waits on a job that's disabled); 9 rollback holds never deleted; 12 dead launchd plists.

---

## 2. Non-UI data access — what is actually possible (project instruction)

Tested today, from outside the VM:

| Path | Status | What it gives |
|---|---|---|
| **Bravo's own emailed reports** (`noreply-reporting@bravostoresystems.com`) | ✅ **Live now.** Daily KPI PDF per store ~9:35 AM + Monthly KPI on the 1st. ~200 in the mailbox. | Zero-Bravo-touch source for daily/monthly store KPIs. PDF, needs parsing. **Bravo can schedule reports — we have only ever asked for one.** |
| **SSRS report server** `ssrs.bravoapplication.com:9176` (what Bravo's "Company KPIs" renders from) | ⚠️ **Headless login WORKS** (verified today: the logon form accepts the pre-filled service user with no password; unauthenticated requests are redirected, authenticated ones reach the report engine). **But** every render needs a fresh `r=` token that only the Bravo client mints via its private WCF service; stale tokens → `rsErrorExecutingCommand`. | Pure-headless is blocked by the token, not by auth. Half-useful: the existing hybrid (Bravo mints token → we fetch xlsx) stays. |
| **Reporting Pro** (Bravo's paid web reporting: 60+ reports, Ad Hoc, CSV/Excel export, per-company web login) | Confirmed product; quoted to Joshua Mar 2026 at ~$85/store/mo (all reports); ticket #43428350763 open, never subscribed. SSRS-based → almost certainly supports **subscriptions** (scheduled CSV/Excel email of any report). | The real non-UI path for most of the 82 cells. **Money decision → §6.** |
| Bravo API / Zapier | ❌ Vendor in writing: "There isn't an API." | — |
| SQL/ODBC | ❌ Hosted; local SQL Express stopped; thin WCF client. | — |
| Replaying Bravo's WCF calls | ❌ Undocumented, signed auth, vendor said no. | — |

**Conclusion:** the way off the UI is not a hack — it is (a) Bravo's report scheduler emailing us CSV/Excel instead of one PDF, and (b) Reporting Pro if (a) can't cover the list. Both go through Bravo support, which is a vendor email under Joshua's name (§6).

---

## 3. Target architecture (what "it just works" looks like)

```
SOURCES                       INGEST (native, no Claude)         STORE            PUBLISH
Bravo emailed CSV/PDF ──┐                                       ┌──────────┐    deterministic
Reporting Pro CSV ──────┤   bin/ingest_*.py  (launchd, 15-min) │ vp_data  │──► formatters ──► Slack
Bravo pipeline CSV ─────┤   validate → normalize → upsert       │ .sqlite  │    exit 0 = post verbatim
Gusto / eBay / GA4 / ───┘                                       │ + ledger │    exit 2 = post NOTHING
Brevo / Publer APIs                                             └──────────┘         │
                                                                                     ▼
                                              Cowork task = thin: run script, post stdout, log.
                                              fleet-guardian verifies shape (exit code) not just marker.
```

Principles: **one warehouse, one formatter per publication, one post ledger** (dedup by construction), Claude sessions only where judgment is needed (narrative, anomalies, DMs), everything else native and cheap.

---

## 4. The plan — phases, sequenced by payoff ÷ risk

All work is additive (Rule 4): new files alongside, backups of anything touched, proven on the island before swapping consumers.

### Phase 0 — Week 1: shrink the UI surface where data already exists elsewhere
| # | Action | Kills |
|---|---|---|
| 0.1 | `bin/ingest_bravo_email_kpis.py`: pull the 5 daily + monthly KPI PDFs from Gmail, parse to `vp_data.sqlite`. Pilot on 30 days of history. | Store-KPI dependence on `company-kpis` (the SSRS/Edge cell) and part of the Monday EOM re-pull |
| 0.2 | Ask Bravo support (existing ticket) to add scheduled **CSV/Excel** emails for: End of Month, Safe Register Journal, Aged Inventory, Employee Activity, Layaways, 75-Days-Past-Due, Items to Price, Buys From Public. Draft ready; **Joshua sends or OKs** (§6). | Potentially 60–70% of daily/weekly VM minutes |
| 0.3 | Reporting Pro: run the $0 demo-login test (vendor demo credential in the Mar-2026 thread) to confirm subscriptions + CSV export, then price. | Feeds §6 decision |
| 0.4 | GL chain: add a pre-check that reads each store's unposted-day list before Step 2, and a plain hold line instead of 17 silent failures. | 0% GL/sales-tax success |
| 0.5 | Register `monthly-publication-audit` (file is ready in `pending-tasks/`; needs Joshua's click). | Monthly blindness |

### Phase 1 — Weeks 2–3: deterministic reporting layer
| # | Action |
|---|---|
| 1.1 | `vp_data.sqlite` + `bin/ingest_pipeline_csv.py`: every `output/*.csv|xlsx` lands in normalized tables (DevExpress decoration rows stripped, column drift anchored on headers). Native launchd, every 15 min, idempotent. |
| 1.2 | Convert the remaining hand-rendered tables to formatters on the `format_aged_inventory.py` pattern, in this order (highest damage first): loan review, layaway review, employee MTD, first-payment-default, daily funds, pawn walk, sold/discount review, items-to-price, jewelry counts, store KPIs, canvases. Each: validation gate → exit 0 verbatim / exit 2 nothing. |
| 1.3 | Post ledger table (`publications`): channel, marker, period, hash, ts. Every formatter checks it → duplicates impossible; guardian reads it instead of scraping Slack. |
| 1.4 | Native Slack poster (`bin/post_slack.py`, reuse the token the eBay launchd agents already use) so scripts can publish **without a Cowork session** for pure data posts. Cowork keeps DMs/narrative. |

### Phase 2 — Weeks 3–4: harden what must stay UI-driven
| # | Action |
|---|---|
| 2.1 | Jewelry: allow-list genuinely-empty categories (HAR Charms, LEX Brooches, WAY Charms) → 46 false failures/month disappear; `jewelry-case-counts-v2` from 63% fail to ~20%. |
| 2.2 | Remove the Continuous-Scrolling toggle from the 8 handlers still carrying it — starting with `SafeRegisterJournal` (runs daily, 15% fail). Approved 6/15, never done. |
| 2.3 | Watcher: fix `started_at`/`finished_at` (both stamped at write); 0-row guards on the 4 lenient handlers + `ChekkitInactivesV2`; store-hours gate fleet-wide (Sun all, Wed HAR/WAY/LEX/ROA); grid-walk watchdog (bounded). |
| 2.4 | One Chrome↔VM mutex file honored by every Chrome-driving task and by the watcher's trigger poll. |
| 2.5 | Consolidate Bravo touches: single nightly manifest (jewelry + funds + next-day prestage) and single morning manifest; retire `weekly-store-kpis`' own EOM pull (dead reuse-check) by reading the warehouse. Target: 13 daily touches → 4. |
| 2.6 | Secrets sweep: plaintext password fallback in `bravo_watcher.ahk`, old password in `FINDINGS_AND_PLAN.md`. |

### Phase 3 — Weeks 4–6: fleet and scheduler
| # | Action |
|---|---|
| 3.1 | Convert the 5 babysitter tasks (jewelry, morning pull, gdrive cache, photos index, Bald Rock contract) to launch→exit→verify: native runner does the waiting; Cowork verifies in 2 min. Frees ~4 slot-hours/day. |
| 3.2 | Merge the 5 canvas refreshes into one; merge the 10 AM ops-check trio; move all data-only posts to native (1.4). Target: 148 enabled → ~110, skips 8k/wk → <1k. |
| 3.3 | Guardian v2: drop the 48-h blindness (verify "since last scheduled fire" per cadence), extend `expected_outputs.json` to all ~90 reporting tasks, verify shape via ledger + formatter exit code, cover native agents. |
| 3.4 | `bin/dispatch_health.py` (native, 30 min) → `fleet/DISPATCH_HEALTH.md` + one daily plain DM only when something is unrecovered. |
| 3.5 | Debris: delete 9 rollback holds, 12 dead `vpops` plists, `weekly-aged-inventory-review` duplicate; fix `daily-loan-inventory-text` reference; assign an owner to `new-inv-weekly-report` (currently dark); pin the 3 unpinned tasks; decide `vp-new-customer-report` → #store-performance (contradicts the weekly-only decision). |

### Phase 4 — parallel, this week: platform risk
| # | Action | Needs |
|---|---|---|
| 4.1 | Backups: Time Machine target gone since 8/25; disk 97%. Pick a destination (external drive / new NAS) and turn TM back on. | Joshua: hardware |
| 4.2 | Move `~/Documents/Claude` out of iCloud eviction reach (Keep-Downloaded or relocate + symlink). Evicted task files = silent task deaths. | one click |
| 4.3 | `claude-keepalive` plist fix (exits 126 nightly) + `chromeperms` registry edit (27 Chrome tasks stall on approvals). | one click each |

---

## 5. Expert board

🧑‍⚖️ **EXPERT BOARD — how to make Valley Pawn reporting frictionless**

PANEL: Windows/.NET UI-automation engineer · Data-pipeline/SRE · Release-management lead · Controller (data integrity)

OPTIONS WEIGHED
- **Keep hardening the AHK fleet cell by cell** — for: known territory, additive; against: 45% of failures happen before a handler runs; ceiling is ~90% clean, never 99%.
- **Rewrite around a vendor API/DB** — rejected: none exists (vendor in writing, verified locally).
- **Headless SSRS** — auth works, `r` token doesn't; keep the hybrid, don't build on it.
- **Move data acquisition to Bravo's own scheduler + Reporting Pro, and move rendering to code** — for: removes the two root causes (UI dependence, model-rendered tables) instead of patching symptoms; against: costs money for Reporting Pro and needs vendor cooperation; PDF parsing has its own brittleness (mitigated by asking for CSV).

DECISION
- Do the last option, in the order above: free wins first (emails, formatters, jewelry allow-list), the vendor conversation in parallel, scheduler diet after. Every phase pays for itself even if the next never happens.

REJECTED
- Adding a second VM/login for parallel pulls — Bravo's per-user module lock and one universal login make it a lockout risk, and Reporting Pro solves the same throughput problem without it.
- Replacing Cowork tasks wholesale with launchd — judgment/narrative tasks stay in Cowork; only data-only posts move native.

---

## 6. For Joshua — the only decisions that are yours

1. **Reporting Pro spend** (~$425/mo for 5 stores, all reports; cheaper tiers exist). Recommendation: yes, *after* the $0 demo test confirms scheduled CSV export. This is the single biggest robustness lever available.
2. **Vendor email**: OK for me to send the Bravo support request (add scheduled CSV/Excel reports to the existing daily email) from jdavis@fcfpawn.com, or you send it. Draft will be in the Open Items Register.
3. **Backup destination** — hardware/spend.
4. **Four clicks** when you're at the Mac: register `monthly-publication-audit`, `chromeperms` registry edit, `claude-keepalive` plist, iCloud Keep-Downloaded on `~/Documents/Claude`.

Everything else in §4 proceeds autonomously and additively on your go.

## 7. Success measures (reviewed weekly in `fleet/DISPATCH_HEALTH.md`)
Clean-pull rate 61% → 95% · Bravo VM hours 40–55/mo → <15 · hand-rendered tables 85 → 0 · queue skips 8k/wk → <1k · monthly tier 12/12 on the 1st · zero duplicate/incomplete posts (ledger-enforced).
