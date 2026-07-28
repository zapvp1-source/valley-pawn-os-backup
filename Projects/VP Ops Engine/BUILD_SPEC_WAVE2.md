# VP Ops Engine — BUILD SPEC WAVE 2 (v1.0)

**Designed:** 2026-07-27 by Claude Fable 5 (design session), expert-board reviewed.
**Build model:** claude-sonnet-5.
**Prerequisite reading:** `BUILD_SPEC.md` v1.0 (Wave 1 — its Hard Rules, repo layout, shadow/cutover procedure, and session ritual ALL apply here unchanged) + `vp-ops/STATE.md` + this file.
**Scope:** three new analytics jobs — H (weekly FPD), I (monthly company analytics), J (monthly gold trend) — plus the codified connector policy (Section 1).

---

## 0. Inherited hard rules — plus Wave-2 additions

All 8 Hard Rules from BUILD_SPEC.md §HARD RULES apply verbatim. Additions:

9. **The FPD 12-month archive (`Scheduled/_fpd-archive/fpd-history.csv`) is shared state** with the legacy Monday-combined path. Append-only, dedupe by `Ticket Number` (same logic as the legacy task). Never rewrite or reorder existing rows. Dedupe makes concurrent writers idempotent — that is the safety mechanism; preserve it.
10. **#gold-trend- has NO established canonical format** (verified 2026-07-27: the only post ever is a blocked status update). Job J's format below is the proposed canon — the FIRST successful post establishes it. Do not improvise beyond it.
11. **FPD ranking sort = FPD loan COUNT ascending** (lowest count = best = rank 1). Ties break by $ exposure ascending. Verified against the live 7/22 post (Roanoke 26 ranks above Culpeper 36).

## 1. Connector policy (board decision 2026-07-27 — codified for all future waves)

Every task falls in exactly one lane:

| Lane | Test | Fate |
|---|---|---|
| **API lane** | The service has a real API a plain Python job can call with a stored key (Gusto, Brevo, Publer, Slack, Google-via-Apps-Script, GA4 Data API) | Portable → native engine job, when its wave comes |
| **Browser lane** | UI-only surface (Chekkit, BrightLocal, Bing Places, Amazon checkout, QBO UI) | **Stays with Claude.** Scripted headless browsers REJECTED — they fail silently on vendor UI changes, recreating the failure mode this project exists to kill. Nothing browser-only is operationally critical; the watchdog makes Claude-outage pauses visible. |
| **Judgment lane** | LLM is the point (content, review replies, vision/OCR) | Stays with Claude permanently |

Wave-3 candidates from the API lane (NOT in this wave — listed so they're not lost): `daily-clockin-check` (Gusto API), `email-analytics-weekly` (Brevo API), `weekly-timekeeping-analysis` (Gusto API). One discovery item for Wave-3 design: check whether Chekkit exposes an API before assuming browser lane.

---

## 2. Job H — Weekly FPD Ranking → #first-payment-default (`C0B17894S2Y`)

**Schedule:** Mon 09:45 ET (after Jobs A–D). **Data:** `fpd-cohort` pipeline cell × 5 stores — ADD this cell to Job E's Monday trigger (that's our own vp-ops code, editable). CSV shape: `Ticket Number,Category,Full Description,Loan Amount` (one row per defaulted loan; `$`-prefixed amounts; quoted commas — use `csv` module; header-only file = clean store with 0 FPD, not a failure).

**Steps:** (1) read 5 CSVs → per-store count + $ exposure; (2) append new tickets to the shared archive per Rule 9 (`first_seen_date,store,ticket_number,category,full_description,loan_amount`); (3) compute this-week top-3 categories company-wide (by count, tie-break $) and chronic top-3 from archive rows where `first_seen_date >= today − 365d`; (4) render + post.

**Canonical format (verbatim from live 7/22/2026 post — golden test against it; `_x_` = Slack italic):**

```
:dart: _Weekly First-Payment-Default Ranking — <YYYY-MM-DD>_
_Source: Bravo saved report "Claude First Payment Default" · cohort = loans originated 60–90 days ago with no customer payment activity_

_Store ranking — best to worst_
1. _<Full Store Name>_ — <N> FPD loans - $<X,XXX.XX> exposure
2. ... (5 rows, count ASC per Rule 11)
_Company:_ <ΣN> FPD loans - $<ΣX.XX> total exposure

_Top default-prone categories (this week)_
1. <Category> — <N> loans - $<X.XX>
2. ...  3. ...
_Chronic-risk categories (last 12 months)_
1. <Category> — <N> total FPD loans - $<X.XX>
2. ...  3. ...
```

Full store names (Roanoke, Culpeper, Lexington, Harrisonburg, Waynesboro), not codes. DATA ONLY in the channel — no status notes; if a store's cell failed, exactly one trailing line: `_Note: <STORE(S)> not included — pipeline cell failed._` Failures otherwise DM Joshua per Hard Rule 3. **Dup-guard:** before posting, check the channel for a post dated today (the legacy Monday-combined STEP 4.5 also posts FPD until Joshua disables it at cutover — same guard the legacy path uses).

**Dropped from legacy scope (board call):** the Word doc deliverable. Replacement: write the same content as `data/reports/fpd_<date>.md` + KPIs into SQLite → dashboard. If Joshua wants the doc back, that's a Claude Tier-2 add-on, not an engine job.

## 3. Job I — Monthly Analytics → #company-performance (`C0B26GD8D2R`) + #store-performance (`C03CGTN3KN1`)

**Schedule:** 1st of month, 08:00 ET (data prestage: last day of month 21:00 ET — monthly mode of Job E dropping the 6-window pulls). **This job replaces the run that did NOT fire on 2026-07-01** (July post is missing — first real deliverable is the July report, late, then August on schedule).

**⚠️ DISCOVERY STEP FIRST (I-0):** The canonical Jul 3 format's source line says **"Bravo Company Performance (KPI) report"** and defines **Net Revenue = Retail GP + Scrap GP + PSC** (retail vs scrap channel split) — this SUPERSEDES the EOM-based formula in the legacy SKILL.md (which predates the Jul 2 MobilePawn double-count correction). Before building: (a) read `monthly-analytics-prestage/SKILL.md` + `monthly-analytics-report/` scripts (`parse_eom.py` is penny-verified but against the OLD format) to determine exactly what data path produced the Jul 3 numbers; (b) open the companion Google Sheet "Monthly Analytics - June 2026" (Monthly Reports folder `1DYScQQl_dkkf3jGSBqNzGJKKv2uroFoh`) to recover the exact table layout — **the Slack MCP strips the table bodies from old posts, so the Sheet + the Jul 3 framing text below are the only recoverable canon.** (c) If the Jul 3 numbers required a UI-only pull (SSRS Company KPIs screen), STOP and escalate to a design session — that would need a new pipeline handler first, same pattern as Job J-0.

**Canonical framing (verbatim, Jul 3 2026 — table bodies to be recovered from the Sheet in I-0):**

```
:bar_chart: _Monthly Analytics - <Month Year> | Company-Wide — Retail vs Scrap channel split_
_Source: Bravo Company Performance (KPI) report, all 6 windows | matches Bravo to the penny_

_VIEW 1 - Same Month: <Month Year> vs <Month PriorYear>_
[table]
_VIEW 2 - YTD: Jan-<Mon> <Year> vs Jan-<Mon> <PriorYear>_
[table]
_VIEW 3 - T12M: <range> vs <prior range>_
[table]
```

6 windows per legacy spec (same-month/YTD/T12M × current/prior; T12M-prior clamps at Bravo's ~2024-06-03 floor — note variance in post). #store-performance companion post: 5 stores, NO grand total, same 3 views. Sheet output: reuse `xlsxmin.py` to build the workbook locally + publish to the dashboard; Google Sheet upload only if achievable via the proven Apps-Script-ingest pattern (do NOT add new OAuth plumbing for it — flag as optional).

## 4. Job J — Monthly Gold Trend → #gold-trend- (`C0BJ8SYTVBN`, private, trailing hyphen is part of the name)

**Two stages — J-0 is a blocker for J-1:**

**J-0 (one-time infrastructure, needs an interactive Claude session with Bravo/Parallels — schedule with Joshua):** Gold dwt by store/month lives ONLY in Bravo's **Scrap Refining Process** screen — no pipeline handler exists (this is exactly why the 7/17 one-off blocked). Build additively per bravo-context's 4-step recipe: new saved report if the screen supports it (or new AHK handler cloned from the nearest grid-walk template), new cell name e.g. `scrap-refining-dwt`, ADD to dispatch tables, restart watcher, smoke one store. Backfill 2025 + 2026 monthly dwt once, store to `vp-ops/data/gold_dwt_history.csv` (append-only, keyed store+month). **Until J-0 is done, J-1 cannot ship — build H and I first.**

**J-1 (recurring engine job):** 1st of month 08:30 ET. Pull prior-month dwt per store via the new cell, append history, post YoY.

**Proposed canonical format (no prior canon exists — first successful post establishes it; keep to this):**

```
:coin: _Gold Trend — <Month Year> (dwt purchased)_
_Source: Bravo Scrap Refining Process · YoY by store_

_<Month> <Year> vs <Month PriorYear>_
• _Culpeper_ — <X.XX> dwt (vs <Y.YY> — <±Z%>)
• (5 stores)
_Company:_ <X.XX> dwt (vs <Y.YY> — <±Z%>)

_YTD:_ <X.XX> dwt vs <Y.YY> prior — <±Z%>
_Best month T12M:_ <Month> (<X.XX> dwt)
```

Open buckets caveat: current-month dwt accumulates until refining close — always report the PRIOR month, and if any store shows an open/zero bucket, note it in one line (the Feb-Waynesboro missing-bucket case from the 7/17 run is the precedent).

## 5. Shadow → cutover (same as Wave 1, per job)

Shadow to #vp-ops-shadow ≥1 real cycle → verify (H: against the 7/22 post format + legacy dup-guard behavior; I: against the recovered Jul 3 canon, penny-check vs the Sheet; J: format review by Joshua since it's new canon) → flip to production → tell Joshua which legacy path to disable (H: the FPD step inside monday-bravo-combined-compile — HIS flip, not ours; I: monthly-analytics-prestage/-report/-watchdog trio). Heartbeats + watchdog coverage from first shadow run. Update `STATE.md` per job.

## 6. Acceptance criteria

- H live ≥2 Mondays, numbers penny-consistent with the archive and no double-posts alongside the legacy path.
- I ships the missing July report, then August on the 1st unattended; tables match the Bravo source to the penny.
- J-0 handler proven (smoke + 2025 backfill complete); J-1 live ≥1 month with Joshua-approved format.
- All three writing KPIs to SQLite and visible on the dashboard.

## 7. For Joshua (genuine calls only)

1. **J-0 scheduling** — the gold handler build needs one interactive Bravo session; say when.
2. **Gold format** — J-1's proposed format above becomes canon on first post; edits welcome before then.
3. **FPD Word doc** — dropped from the engine (Slack + dashboard + md file instead); say so if you want it kept via a Claude Tier-2 task.

## Change log
- 2026-07-27 — v1.0. Formats captured live from Slack (FPD 7/22 post verbatim; #company-performance Jul 3 canon with table bodies unrecoverable via API — recover from Sheet in I-0; #gold-trend- confirmed no canon). Connector three-lane policy codified.
