# VP Ops Engine — BUILD SPEC v1.0

**Designed:** 2026-07-26 by Claude Fable 5 (design session), expert-board reviewed.
**Build model:** claude-sonnet-5 (execute this spec exactly; escalate to Joshua/design session only on architectural forks).
**Owner:** Joshua Davis (Slack U03BB52MDSA, DM channel D03BHQH5VGT).

## Mission (read this before every build session)

Valley Pawn's recurring analytics and Slack publishing currently run with **Claude as the engine**. When Claude credits ran out on Thu 2026-07-23, every automation stopped silently. This project builds **VP Ops Engine**: plain Python jobs on launchd timers that produce the recurring analytics with **zero LLM in the runtime path**. Claude Code's only role afterward is maintenance of this repo.

**Design principle:** Claude is the mechanic, never the motor.

---

## HARD RULES (non-negotiable, from BUSINESS_OS.md + Joshua 2026-07-26)

1. **DO NOT TOUCH `daily-funds-verification`** or anything in its chain (Joshua: "works fine, do not touch it"). It is OUT OF SCOPE entirely.
2. **Additive only (Rule #4).** Never modify: existing scheduled tasks under `Documents/Claude/Scheduled/`, saved Bravo Ad Hoc reports, AHK handlers, `bravo_watcher.ahk`/`bravo_export.ahk` dispatch tables, the Monday combined Bravo run. New code lives in THIS project folder only. Existing Claude tasks get disabled (never deleted) by JOSHUA, only after their replacement passes cutover.
3. **#claude-notifications DOES NOT EXIST.** All failure alerts = ONE plain-language Slack DM to Joshua (D03BHQH5VGT): `⚠️ VP Ops job "<job>" did not complete — <date>.` No technical detail in the DM; diagnostics go to the log file. Never alert any other person or channel.
4. **Canonical Slack formats are sacred.** Each job must reproduce its established format EXACTLY (specs in Section 6). Consistency beats improvement. Never invent metrics or layouts.
5. **Never publish Preston Peters in employee rankings** (his revenue counts in company totals; his name never appears).
6. **Secrets:** Slack bot token via the existing resolution chain in `common.py` (env → `Bravo Data Extraction/slack_config.json` → `~/.vp_slack_config.json` → shell profile). New secrets go in macOS Keychain only. Never write a secret into a file in this repo.
7. **launchd jobs that touch ~/Documents must use `~/bin/vp-runner`** as ProgramArguments[0] (TCC gate — proven pattern, see VP Agent README).
8. **Shadow mode before cutover** (Section 8). No job posts to a production channel until its shadow output is verified word-for-word.

---

## 1. What already exists (REUSE, don't rebuild)

| Asset | Path | Use |
|---|---|---|
| Bravo pipeline (Claude-independent) | `Documents/Claude/Projects/Bravo Data Extraction/` | Source of ALL data. Trigger = drop JSON in `triggers/`, result in `results/`, CSVs in `output/`. Trigger schema in BUSINESS_OS.md Section 4. |
| `common.py` (Slack lib, stdlib-only) | `Documents/Claude/Projects/Business Continuity/common.py` | COPY into this repo as `vpops/common.py` (do not move/edit the original). Has slack_post, slack_dm, logging, token chain, channel IDs. |
| VP Command Center (live, localhost:8765) | `Documents/Claude/Projects/VP Agent/command_center.py` | Phase 2 UI host. LaunchAgent `com.valleypawn.commandcenter` already running. |
| Cloudflare Pages site + creds | `Documents/Claude/Projects/Business Dashboard Website/` (`.cloudflare/`, `site/`, REFRESH_RUNBOOK.md) | Phase 2 web publish target: vp-dashboard.pages.dev (Basic Auth). `_worker.js` is the password gate — never delete. Node at `~/Documents/Claude/tools/node`. |
| vp-runner TCC wrapper | `~/bin/vp-runner` | ProgramArguments[0] for every new LaunchAgent. |
| Native job precedents | `com.valleypawn.dashboarddatacollector`, 5× eBay LaunchAgents | Copy their plist patterns. |
| daily-loan-inventory-text native pull | `Documents/Claude/Scheduled/daily-loan-inventory-text/` (`native_run.sh`, `daily_run.sh`, `compute.py`, `send_imsg.applescript`) | Phase 1 job F wraps this — verify + schedule, don't rewrite. |
| vp_agent.py (break-glass LLM runner) | `Documents/Claude/Projects/VP Agent/` | Not used by the engine. Stays as outage fallback for judgment tasks. |
| Nightly GitHub backup | task `vp-os-github-nightly-backup` → repo valley-pawn-os-backup | Init `vp-ops/` as a git repo; confirm the backup whitelist picks it up (or add additively). |

**Known context quirks:** the layaway "Past Payment Due Date" badge lies (use Last Payment Date ≤ today−60 data); EOM CSVs are the canonical cross-store source (`bravo-end-of-month`); 0 rows is a legitimate pipeline result — check `row_count`, don't treat as failure.

---

## 2. Repo layout (create at `.../VP Ops Engine/vp-ops/`)

```
vp-ops/
├── README.md                  # what this is + runbook
├── vpops/
│   ├── common.py              # copied from Business Continuity (attribution note at top)
│   ├── bravo.py               # trigger-drop + result-poll + CSV locate/parse helpers
│   ├── formats.py             # canonical Slack format renderers (one function per report)
│   ├── store.py               # SQLite writer/reader (data/vpops.db) + JSON export
│   └── watchdog.py            # heartbeat check + Joshua DM
├── jobs/
│   ├── job_aged_inventory.py
│   ├── job_store_rankings.py
│   ├── job_employee_rankings.py
│   ├── job_loan_layaway_review.py
│   └── job_daily_loan_inv_text.py   # thin wrapper around existing native_run.sh flow
├── launchd/                   # plist templates (installed to ~/Library/LaunchAgents)
├── data/                      # vpops.db + latest JSON snapshots (gitignore db, keep JSON)
├── tests/                     # golden-format tests using REAL historical CSVs from output/
└── STATE.md                   # per-job cutover state: shadow | verified | LIVE
```

Python 3 stdlib only (match common.py). No pip dependencies. Every job: writes a heartbeat file `data/heartbeats/<job>.json` (ts + status + one-line detail) on every run, success or fail.

---

## 3. Phase 0 — Triage (first build session, ~1 session)

1. Inventory `Documents/Claude/Scheduled/` (~150 folders) + cloud triggers (`Scheduled/_ccr-trigger-export/ccr_triggers_export_2026-07-16.md`, plus `hiring-inbox-watch` added 7/23). Produce `TRIAGE.md` in this folder: every task → **Tier 1** (must run without Claude — this spec), **Tier 2** (judgment/content — stays on Claude, non-critical), **Native already** (launchd/AHK — no action), **Dead/stale** (list only; Joshua decides deletions).
2. Verify freshness/availability of each Tier-1 data source in `Bravo Data Extraction/output/` (filename patterns below).
3. Do NOT reclassify `daily-funds-verification` — mark it "WORKS — DO NOT TOUCH (Joshua 2026-07-26)".

## 4. Phase 1 — Tier-1 jobs (build order = most-broken first)

Slack evidence (2026-07-26 audit): store rankings last posted 3/23; aged inventory canonical format has NEVER posted; employee rankings + loan/layaway missed 7/20 then died in the 7/23–25 outage.

| # | Job | Schedule (launchd) | Data in | Posts to |
|---|---|---|---|---|
| A | `job_store_rankings` | Mon 08:30 ET | 5× EOM CSVs (`<END_DATE>_<STORE>_end-of-month.csv`) | #store-performance `C03CGTN3KN1` — main msg + THREADED reply |
| B | `job_aged_inventory` | Mon 09:00 ET | 5× `<date>_<STORE>_aged-inventory-summary.csv` | #aged-inventory-review `C04NGH4FF35` |
| C | `job_employee_rankings` | Mon 09:15 ET | employee-activity CSVs (MTD) | #employee-performance `C0ATTLPQHR8` |
| D | `job_loan_layaway_review` | Mon 09:30 ET | `<date>_<STORE>_loans-75-days-past-due.csv` + EOM Ending Loan Base + layaways cell CSVs | #loan-review `C0B08RS2BMK` + #layaway-review `C04N24STDP1` |
| E | `trigger_dropper` (data producer) | Mon 05:30 ET | — | drops ONE combined trigger JSON for cells: `end-of-month`, `aged-inventory-summary`, `employee-activity`, `loans-75-days-past-due`, `layaways` × 5 stores; polls `results/` |
| F | `job_daily_loan_inv_text` | Daily 07:30 ET | company-kpis via existing `daily_run.sh` | iMessage Joshua (804) 930-4221 + Preston (540) 836-4200 via existing `send_imsg.applescript`; Slack-DM fallback |
| G | `watchdog` | Daily 10:30 ET | `data/heartbeats/*` | DM Joshua ONLY on a missed window (Rule 3 format) |

**Job E rules (duplicate-pull guard, BUSINESS_OS gap #17/18):** before dropping the trigger, check `output/` for CSVs already produced today for each cell/store and SKIP those. Runs at 05:30 to stay clear of the Claude-side Monday combined run; while both systems coexist, whichever runs first produces the files and the other reuses them. NEVER edit the existing Monday run to accommodate this.

**File access note:** `Bravo Data Extraction/` and `triggers/` are plain local paths for a native process — launchd jobs read/write them directly (the osascript bridge is only a Claude-sandbox workaround; native code doesn't need it).

## 5. Phase 2 — One dashboard

1. Every job also writes its metrics to `data/vpops.db` (SQLite: `kpis(store, metric, value, as_of, period, source)` + `runs(job, ts, status, detail)`) and exports `data/latest.json`.
2. **Command Center**: add a KPI page reading `latest.json` (additive module/route; back up `command_center.py` before touching; keep existing pages working).
3. **Web publish**: small `publish_dashboard.py` (post-job step) renders `latest.json` into the existing `Business Dashboard Website/site/data/kpis.json` schema and deploys via the wrangler command in REFRESH_RUNBOOK.md. Result: vp-dashboard.pages.dev stays current with NO Claude and NO Slack-parsing. Organize by the 8 KPI categories from the store-rankings spec + task-health table.
4. After 2 clean weeks: propose to Joshua retiring the Apps Script dashboard + the Claude `vp-dashboard-refresh` task (his call; disable, don't delete).

## 6. Canonical Slack formats (renderers in `formats.py` — reproduce EXACTLY)

These are the locked formats from Joshua's standing rules (also in his global CLAUDE.md). Golden tests must compare renderer output against the most recent real post in each channel.

**A. Store Performance ("Full Category Rankings") → #store-performance.** Source: 5 EOM CSVs. 8 categories, each medal-ranked high→low with Company Total: 1) Loan Balance = Ending Loan Base; 2) Inventory Balance = Ending Inventory Base; 3) Total Assets = 1+2; 4) Retail Sales Total = Taxable + Nontaxable Sales totals; 5) Pawn Service Charges = In-Store (Interest+Fees) + MobilePawn (Interest+Fees); 6) Scrap Sales = Refined (Cost of Sales) Month; 7) Layaway Balance = Layaways Ending Balance; 8) Net Revenue MTD = PSC + in-store Misc + mobile Misc + MobilePawn Convenience Fees + Sales Revenue (Profit). Overall ranking = avg rank across 8 (lower better), tiebreak = #1 finishes. 🥇🥈🥉 then "4th"/"5th". Structure: main message `:trophy: Overall Store Rankings` (avg rank + category wins + short summary), then Full Category Rankings as a THREADED reply ending with `Company Totals` line.

**B. Aged Inventory Review → #aged-inventory-review.** Serialized inventory aged >1yr at COST (aging cols 1yr-18mo + 18mo-2yr + 2yr-3yr + >3yr), split Jewelry vs Gen Merch (Mfg Goods); each % = bucket ÷ store's serialized Subtotals cost (J% + GM% = Tot%). Monospace code-block table `Store | Jewelry | J% | Gen Merch | GM% | Total | Tot%`: header + separator + 5 stores + separator + TOTAL row, ranked by Tot% DESC. Header (italic): `:bar_chart: _Aged Inventory Review — <Month DD, YYYY>_` / `_Inventory Aged Over 1 Year (Cost Basis)_` / `_Ranked by Total Aged % of Inventory_`. Footer: `:trophy: Cleanest book: <store> (<Tot%>).  :hammer_and_wrench: Needs the most attention: <store> (<Tot%>).` + Google Sheets link + `_Source: Bravo POS · Aged Inventory Summary report_`.

**C. Employee Sales Rankings → #employee-performance.** `_MTD Employee Sales Rankings — Retail Sales Excluding Fees (Bravo POS)_` / `:bar_chart: Period: <range>` / medal list by PERSON aggregated company-wide (sum Retail Sales Excluding Fees across stores; show store codes e.g. `(HAR + WAY)`): `:first_place_medal: _Name_ (STORE) — $X.XX` … then `4th`, `5th`, etc. EXCLUDE Preston Peters (never listed), SYSTEM rows, $0 employees. Company Total line = sum of all 5 stores' "Total Store" Retail Sales Excl Fees (Preston's revenue INCLUDED in the total).

**D. Past-Due Loan Review → #loan-review.** `:clipboard: _Weekly Past-Due Loan Review — <Month DD, YYYY>_` / blank / `_PAST DUE LOANS (75-day rule — cap 5% of loan balance)_` / per store: `• _<STORE>_ — N items / $X.XX / P% <✅ if ≤5% | 🔴 if >5%>` / `_Total past 75d:_ N items / $X.XX (P% of $Y company loan balance)`. Store % = store 75d past-due $ ÷ that store's Ending Loan Base. If any store >5%: 🔴 callout naming it; else note the store closest to threshold.

**E. Layaway Review → #layaway-review.** For each metric (overdue, past payment due, no payment 30d, contacted/no activity, locate): per-store value AND that store's % of the company total for that metric. Match the last canonical post (2026-07-13) for exact layout — pull it via Slack API during build and mirror it.

## 7. What stays on Claude (Tier 2 — unchanged by this project)

Email campaigns (Brevo), social content batch/casual video/Publer analytics, AI-visibility autofixes, hiring inbox watch, supply ordering, Chekkit flows, QBO work, sales-tax tasks. These are judgment-shaped; an outage delays them without harming operations. No changes to any of them.

## 8. Shadow mode → cutover (per job)

1. Build job + golden test against historical CSVs.
2. Create private channel `#vp-ops-shadow` via Slack API (`conversations.create`, invite Joshua). If the bot lacks the scope, ask Joshua to create it (one time).
3. Run the job on schedule posting ONLY to #vp-ops-shadow for ≥1 real cycle (Monday jobs: 1 Monday; daily: 3 days).
4. Verification = side-by-side against the canonical spec above (and, where the Claude task still fires, against its live post — numbers must match to the penny).
5. Flip: point the job at the production channel, update `STATE.md` to LIVE, and tell Joshua which Claude task he can now disable in the scheduler UI (he flips it; we never do).
6. Watchdog picks up the job's heartbeat from its first shadow run.

## 9. Acceptance criteria (project done when…)

- All Phase-1 jobs LIVE in production channels ≥2 consecutive cycles with penny-accurate numbers.
- vp-dashboard.pages.dev + Command Center show current KPIs with Claude fully idle.
- Watchdog proven: a deliberately-skipped test job produces exactly one plain-language DM to Joshua.
- `vp-ops/` in git and riding the nightly GitHub backup.
- Kill test passed: with all Claude scheduled tasks imagined offline (credits-out simulation), Monday's four reports + the daily text still publish.

## 10. Session ritual for the build model

Start of every build session: read this spec + `STATE.md` + `TRIAGE.md`; resume, don't restart. End of session: update `STATE.md`, commit, and add one line to the change log below. On any architectural fork not covered here: stop and ask Joshua to run a design session — do not improvise around the Hard Rules.

## Change log
- 2026-07-26 — v1.0 spec written (Fable design session). Corrections from Joshua incorporated: daily-funds-verification is healthy and out of scope; #claude-notifications does not exist (DM-only alerts).
- 2026-07-26 — Phase 0 triage complete (claude-sonnet-5 build session). TRIAGE.md written covering all 160 Scheduled/ folders. Found: Jobs A–D each have two overlapping/unreliable legacy code paths targeting the same channel (resolve by golden-testing against latest real Slack post, not either legacy script, per §6); monday-store-rankings vs weekly-store-kpis look like true duplicates; Bravo pipeline healthy but Job A–D data cells stale since 7/13–7/21 (Job E must refresh before golden tests). No hard rules or scope changed. Next session: Phase 1 Job A.
- 2026-07-26 — Phase 1 Jobs A–D and G built, golden-tested against real Slack history/CSVs, and live-verified end-to-end in #vp-ops-shadow (claude-sonnet-5 build session, same day as Phase 0). Key discoveries, all recorded in vp-ops/STATE.md:
  - **No Slack bot token existed anywhere on the Mac** — the "existing token chain" Hard Rule #6 assumed was reusable was actually empty; every currently-working Claude-posted report uses Claude's own MCP Slack connection, not a bot. Resolved: created Slack app "VP Ops Engine", token stored in macOS Keychain (service `vp-ops-slack-bot-token`), `common.py` updated to check Keychain first.
  - Job A: real live format differs from both `store_kpis_compile.py`'s own output and `monday-store-rankings/SKILL.md`'s documented example (italic+shortcode-emoji vs their bold+unicode) — built to match real Slack history instead, verified byte-for-byte against two real posts.
  - Job B: real #aged-inventory-review history has 5+ mutually-inconsistent formats, none matching the CLAUDE.md canonical spec (missing Total-$ column, TOTAL row, Sheets link, Source footer) — built against CLAUDE.md directly, confirming BUILD_SPEC's "never posted" claim was accurate for this one.
  - Job C: ranked-list output matches real 2026-07-13 post byte-for-byte (cross-store aggregation verified, e.g. Martin Dowden LEX+ROA+WAY); added the Company Total line CLAUDE.md requires but no historical post includes.
  - Job D: layaway review %/counts match a real post exactly; loan review counts/$ match exactly but %s deliberately use the freshest EOM Loan Balance rather than a stale snapshot (the historical post being compared against used a loan balance dated a full 3 weeks before the report date).
  - Note: BUILD_SPEC's own claim "store rankings last posted 3/23" does not match live #store-performance history (real posts found through 7/20) — worth a correction in the next design pass, doesn't change what was built.
  - Jobs E (trigger dropper — would drive live Bravo during business hours) and F (daily loan/inventory text — sends real iMessages) deliberately NOT run live; built groundwork only, held for Joshua's explicit go-ahead. Watchdog's real DM-send path also untested live for the same reason.
  - Next session: resume with Jobs E/F once Joshua's back, then launchd plist installation + Monday scheduled-cycle verification before any production cutover.
- 2026-07-26 (same day, continued) — Joshua confirmed stores closed for the day and gave explicit go-ahead ("we are not open today, lets get it done" / "test the texts" / "go as far as possible to complete this"). Completed:
  - **Job F run live for real**: real Bravo pull + real iMessages sent to Joshua and Preston, confirmed delivered.
  - **Job E built and run live**: duplicate-pull guard verified correct (skipped `end-of-month`, already fresh from Job F's pull). Blocked by an EXTERNAL issue, not a code bug — Bravo's VM is stuck on a ClickOnce update dialog (`BRAVO_KNOWN_ISSUES.md`'s documented failure mode; `_clickonce_guard.ahk` isn't catching it). Job correctly failed safe (no partial data, heartbeat + DM sent) and did NOT hammer retries per that doc's explicit warning. **This blocks `monday-bravo-combined-run` too** — flagged prominently in STATE.md for whoever's next, since it needs someone to look at the actual Parallels screen.
  - **All 7 launchd agents installed and loaded** (`com.valleypawn.vpops.*`), via thin `.sh` wrappers (`~/bin/vp-runner` execs through `/bin/sh`, doesn't respect a Python shebang — discovered by testing). Jobs A-D wrappers point at `--shadow` (not `--live`) — first real scheduled Monday cycle (2026-07-27) will populate `#vp-ops-shadow` fully autonomously, satisfying BUILD_SPEC §8's "≥1 real cycle" requirement before Joshua reviews and any cutover decision. Jobs E/F/G wrappers point at `--live` (E has no Slack output to gate; F's whole purpose is the real send; G only DMs Joshua on a genuine miss).
  - Next session: check whether the Bravo ClickOnce dialog got resolved, review Monday's shadow output with Joshua, decide on production cutover for A-D.
- 2026-07-26 (same day, continued yet further) — Joshua reviewed the shadow output, invited the bot to all 5 production channels, and approved cutover ("looks good lets go"). **Jobs A-D flipped to `--live`, confirmed posting for real in production** (`#store-performance` etc.), using freshly-repulled data. Caught and fixed a real hard-rule violation in the process: a fresh Bravo export had employee names in ALL CAPS, which silently broke the case-sensitive "never publish Preston Peters" check — fixed with a code-based (employee code, not name string) exclusion before it ever reached production. Also fixed a filename-locator bug (employee-activity's date-range filename convention differs from other cells) and a timeout-handling bug in the Bravo health check (found while debugging a genuinely stuck "Bravo is already running" dialog, cleared via one computer-use click).
  - Then, per Joshua's "follow the spec" / "all tasks": initialized git properly (`vp-ops/` folder rides the existing parent `~/Documents/Claude` backup repo — corrected a mistaken nested-repo attempt), then built out **Phase 2 in full**: `vpops/store.py` (SQLite + latest.json, wired into all jobs), Command Center's new `/vpops` KPI page, and `publish_dashboard.py` (deployed live to vp-dashboard.pages.dev, verified on the real site). Confirmed via `RemoteTrigger` that the old Claude-side Monday tasks were never auto-scheduled in the first place — no duplicate-posting risk existed.
  - **Everything in BUILD_SPEC.md's charter (Phase 0, 1, 2) is now built and live.** All 8 jobs run on launchd schedules with zero Claude in the runtime path. Remaining acceptance-criteria items (§9) are about proving the schedule holds over consecutive real cycles, not building anything further — see vp-ops/STATE.md "Next steps" for what to watch.
