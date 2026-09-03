# Bravo Data Extraction — Unified Health & Self-Heal Runbook

**Owner:** Joshua Davis · **Created:** 2026-06-17 · **Status:** Phase 1 live (gate + watchdog), Phase 2 backlog (handler conversions)

This is the single source of truth for **how Valley Pawn gets data out of Bravo reliably, and how it heals itself when Bravo breaks** — with no human intervention except the one genuinely-manual case (dead guest agent / login lockout), which is escalated by a single Slack DM.

Read this alongside `KNOWN_ISSUES.md` (the confirmed root-cause log). This runbook is the *operating* layer; KNOWN_ISSUES is the *diagnosis* layer.

---

## 0. RULE - never touch Bravo blind. Check for contention FIRST, every time. (set 2026-08-10)

**Why this exists:** on 2026-08-10, a manual jewelry-reconciliation pull collided with the
scheduled daily-items-to-price run during the Monday-morning task cluster. Bravo runs one
shared login (FREE1) across every automation and hard-locks it per module - the collision
surfaced on screen as: Cannot switch stores: FREE1 is busy with Inventory. The session had
already misread an earlier stall that morning as a UI/inv-select bug when it was actually this
same contention. Both the manual pull and the scheduled task ended up half-stuck. Joshua's
instruction: never operate Bravo - manually, via a dropped trigger, or via computer-use - without
checking first, and if there's a conflict, STOP and tell him rather than pushing through.

**This is a live check, not a static timetable.** A hardcoded list of "safe hours" would go
stale the same way the dead scheduled-task debris did (see task-hygiene-sweep). Check the actual
state every time instead:

1. **Is anything already running?** ls triggers/claimed/ - anything sitting there (not yet in
   processed/ or results/) means Bravo is currently in use. Do not drop a second trigger or
   open a computer-use session on top of it.
2. **Is a scheduled Bravo task about to fire?** Check mcp__scheduled-tasks__list_scheduled_tasks
   (or grep -rl 'Bravo Data Extraction' ~/Documents/Claude/Scheduled/*/SKILL.md for the full
   Bravo-touching set) for anything enabled with a nextRunAt within the next ~20 minutes, or
   that just fired in the last ~20 minutes and may still be mid-run/mid-retry. Monday mornings
   (roughly 5:30-9:00 AM ET) are the densest cluster - treat that whole window as high-risk by
   default, not just a specific minute.
3. **If either check is unclear or positive: STOP. Do not retry through it.** A 'FREE1 is busy'
   dialog, an unexplained inv-select hang, or a trigger that won't get claimed are the SIGNAL, not
   noise to route around. Dismiss any dialog cleanly, leave Bravo on whatever screen it's on (don't
   force it back to Dashboard mid another task's run), and send Joshua one plain-language line:
   what collided, and that you're holding until it clears.
4. **Only proceed once both checks are clear**, or Joshua explicitly says to go anyway.

This applies to every manual/on-demand Bravo touch: ad-hoc triggers, computer-use sessions,
backfills, probes, and diagnostic pulls. Scheduled tasks already run through the Health Gate
(below) and single-flight trigger claiming, which handles contention BETWEEN scheduled tasks -
this rule is specifically about a human/session-initiated action stepping on that traffic.

**Retiming candidate, not yet applied:** the 8-9 AM window is genuinely overloaded (items-to-price,
monday-bravo-postcheck, vp-dashboard-refresh, plus the tail of the 5:30 AM Monday cluster all land
here). Sundays are viable for any Bravo pull that doesn't need same-day freshness - every store is
closed Sunday, so Bravo sits idle all day. Candidates for a Sunday or off-peak move: weekly/monthly
analytics and ranking tasks that summarize a period rather than 'yesterday.' This has NOT been
executed - bring a specific move-list to Joshua before touching any cron expression.

---

## 1. The two ways data leaves Bravo (and which one wins)

| Path | What it is | Used by | Reliability |
|---|---|---|---|
| **Headless pipeline** (canonical) | `bravo_watcher.ahk` watches `triggers/`, runs an AHK report handler per cell, writes a CSV to `output/` + a `results/<id>.result.json`. No screenshots, no Parallels grant. | ~20 scheduled tasks: funds verification, items-to-price, intake margin, loan/layaway, aged inventory, employee sales, monthly analytics, Monday combined run, **chekkit** | High **when Bravo is on a Dashboard**; cascades to 0 when Bravo is wedged or off-Dashboard |
| **Computer-use Monday run** (fallback) | `monday-bravo-combined-run` SKILL drives Bravo by screenshots/clicks in one granted Parallels session | Monday combined review only | Reliable but needs a Parallels grant + a present operator; heavy |

**Rule:** the headless pipeline is the canonical path. The computer-use run is the *fallback of last resort* — used only when the pipeline gate cannot recover Bravo and Joshua is DM'd.

The single thing that makes the pipeline reliable: **Bravo must be on a verified store Dashboard before any trigger is dropped.** That is the entire job of the Health Gate.

---

## 2. The Health Gate — one entrypoint, full recovery ladder

**Script:** `bravo_health_gate.sh` (project root). Additive — it only *invokes* existing hardened primitives, edits none of them.

**Run it (detached) before any pull, then poll the status file:**
```bash
nohup bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_health_gate.sh" CUL >/dev/null 2>&1 &
# poll: cat logs/_health_gate_status.txt  ->  "PASS <code>" | "FAIL <reason>" | "RUNNING"
# add --smoke to also run a 1-cell aged-inventory pull as a live proof
```

**The ladder (each rung self-heals before escalating):**

| Rung | Check | Auto-recovery | Covers failure mode |
|---|---|---|---|
| 1 | VM running? (`prlctl list … status`) | `prlctl start`; wait 40s | VM stopped |
| 2 | Guest agent alive? (`prlctl exec echo READY` within 20s) | bounded `prlctl restart`; wait 60s; re-check → else **FAIL guest-agent-dead** | Parallels guest agent dead (the 06-10 hang — `prlctl exec` times out forever) |
| 3 | Bravo running + responsive? (`tasklist` Status ≠ "Not Responding") | not running → `_relaunch_bravo_and_watcher.ps1`; hung → kill (only acceptable kill) + relaunch; then `_run_nudge_session1.ps1` to wake black render / un-minimize | Bravo off; Bravo "(Not Responding)"; black-window render; minimized |
| 4 | On a verified Dashboard? (`_recover_to_dashboard.ahk` → "OK <code>") | up to 2 attempts (login-attempt cap to prevent lockout) | Select-Store screen; login bounce / auto-lock; cascade-wedged nav |
| 5 (`--smoke`) | 1-cell `aged-inventory-summary` pull succeeds | n/a (proof step) | Confirms the pipeline actually produces data end-to-end |

**Output:** `logs/_health_gate_status.txt` (`PASS`/`FAIL <reason>`), full trace in `logs/_health_gate.log`. Exit 0 = healthy, 1 = needs Joshua.

**Proven live 2026-06-17:** drove Bravo from the Select-Store screen → CUL Dashboard (defeating a login bounce) → smoke success (16 rows, real CSV).

### Two implementation gotchas (already handled — don't re-introduce)
- **AHK launch is fire-and-forget.** `prlctl exec … AutoHotkey64.exe script.ahk` returns in seconds while the script keeps running. The gate **launches then polls the result file** (~120s) — it does NOT read the result immediately.
- **AHK writes result files with a UTF-8 BOM.** `OK CUL` is really `﻿OK CUL`. The gate strips the BOM (`tr -d '\357\273\277'`) before matching. Any new code that reads `_recover_result.txt` must do the same.

---

## 3. The Watchdog — proactive, scheduled, self-contained

**Task:** `bravo-health-watchdog` — runs **5 AM and 5 PM daily** (before the morning pipeline batch + Monday combined run; before the 6 PM funds run).

- **Silent on success.** Runs the gate; if `PASS`, does nothing.
- **Guards against active runs.** If `triggers/claimed` is non-empty or a result landed in the last 6 min, it waits/exits so it never steals Bravo's foreground mid-run.
- **One notification path.** On `FAIL`, sends exactly one Slack DM to Joshua (`U03BB52MDSA`) with the reason and the specific manual fix. Mirrors `funds-verification-watchdog` / `monthly-analytics-watchdog`. Never posts to public channels, never loops logins.

---

## 4. Failure-mode → solution matrix (the "account for all failures" table)

| # | Symptom in `result.json` / logs | Root cause | Automated solution | Manual? |
|---|---|---|---|---|
| 1 | every cell `error`, Bravo "(Not Responding)" | CS-toggle hang on a closing/journal report (see KNOWN_ISSUES) | **Phase 2:** remove CS toggle from the 8 remaining handlers (EndOfMonth already done); gate relaunches a hung Bravo | no |
| 2 | later cells `EnsureStore failed` / `BackToDashboard` | cascade after a wedge | gate recovers to Dashboard before the run; **SHIPPED 2026-08-31:** watcher now also auto-recovers between cells (calls `EnsureBravoDashboard` on any non-login EnsureStore failure) + fail-fast (trips after 2 consecutive non-login failures). See `KNOWN_ISSUES.md` 2026-08-31 entry. | no |
| 3 | `Bravo window not found/ready within 30s` | foreground stolen (console `prlctl exec` during a run) / window not foregrounded | gate nudge (maximize/activate); **operating rule:** never run console `prlctl exec` while a run is active | no |
| 4 | `ClickByName: … not found` (e.g. Custom Reports) | handler-specific nav fragility | **Phase 2/4:** harden that handler; retry from clean Dashboard | no (usually) |
| 4b | cell `status=success` but `row_count: 0` / header-only CSV | **CONFIRMED handler defect** — `chekkit-inactives` grid-walk writes the header then captures 0 rows (verified 2026-06-17 across all 5 stores AND on the historical 2026-05-30 set). Recurred on `chekkit-invites` 2026-08-30 (CUL/LEX/WAY reported success/0-rows and the CSVs never landed in `output/`). | **PARTIALLY SHIPPED 2026-08-31:** `ChekkitInvites.ahk` now reports `status:"error"` on 0 rows instead of false success (see `KNOWN_ISSUES.md`). Still open: the underlying grid-walk row-capture bug itself is unrepaired, and `ChekkitInactivesV2.ahk` (a separate handler) has NOT received the same 0-row guard yet — do that next if it recurs. | no |
| 5 | `prlctl exec` hangs; `status=running` but `IP=-` | Parallels **guest agent dead** | gate Rung 2 bounded VM restart → if still dead, **DM Joshua** | **yes** |
| 6 | Bravo at "Select a store" screen | not logged into a store | gate Rung 4 `_recover_to_dashboard.ahk` | no |
| 7 | login screen reappears after submit | login bounce / auto-lock | recover handles it; **capped at 2 attempts** to avoid account lockout | escalate if capped |
| 8 | black window, UIA finds no "Reports" | freshly-relaunched render not painted | gate nudge (WinRestore+Activate+Maximize) | no |
| 9 | ROA End-of-Month never produces CSV in 240s | heaviest store/date-range export exceeds timeout | **Phase 4:** longer local-write window + confirm export-OK click | no |

**Hard rules (never broken):** killing/restarting Bravo is triage only, never "the fix"; never hammer logins (lockout risk); recovery primitives run via `--current-user` GUI exec, Bravo+watcher relaunch via the Session-1 scheduled-task trick.

---

## 5. Roadmap

- **Phase 1 — DONE (2026-06-17):** `bravo_health_gate.sh` + `bravo-health-watchdog`. Proactive recovery now wraps the day.
- **Phase 2 — backlog (Joshua-approved 2026-06-15):** convert the 8 CS-toggle handlers (DepositsAndPaidOuts, DisbursementJournal, EndOfDay, EndOfDayConsolidated, GeneralException, InterStoreCashTransfer, LargeCashTransactions, Transfers, SafeRegisterJournal) to the EndOfMonth gold standard — one at a time, backup + single-cell smoke each.
- **Phase 3:** wire the gate as an inline preflight into each pipeline scheduled task; add watcher fail-fast (abort store after 2 EnsureStore failures) + auto-recover between cells + fail-loud DM on >25% cell errors.
- **Phase 4:** ROA End-of-Month residual timeout; per-handler nav hardening (e.g. chekkit-inactives "Custom Reports").

---

## 6. Scheduled-task hygiene sweep log (fleet-wide, not Bravo-specific — logged here per the sweep task's own instruction)

Monthly automated sweep of the full Cowork scheduled-task list (all 159 tasks fleet-wide, not
just Bravo-touching ones). See the `task-hygiene-sweep` scheduled task for the classification
rules (LIVE / AUTO-DELETE CANDIDATE / REVIEW CANDIDATE). This exists because on 2026-08-10 the
list had accumulated 37 dead/debris tasks nobody had cleaned up.

- **2026-09-01 — first run under the new monthly sweep.** 159 tasks total: 148 enabled/live
  (untouched), 1 future one-time (untouched), 0 auto-deleted this cycle (nothing met the
  conservative bar: disabled 60+ days AND stale AND an obvious throwaway-name marker), 8
  disabled-too-recently-to-judge (<30 days, left alone), 3 flagged as REVIEW CANDIDATEs pending
  Joshua's confirmation before next month's sweep:
  1. `weekly-social-media-content` — disabled ~145 days; looks superseded by the current
     vp-content-batch / Publer content stack, but not deleted without confirmation.
  2. `wordpress-token-keepalive` — disabled 33 days; unclear if any live WordPress-publishing
     task still depends on it.
  3. `jewelry-count-reconciliation` — never ran; looks superseded by the live 4-layer jewelry
     count stack (`jewelry-onhand-nightly-pull` + compare/catchup/watchdog), but flagged rather
     than removed since it never got a chance to prove itself dead.
  Joshua notified via one plain-language Slack DM (D03BHQH5VGT); no jargon, no task IDs in that
  message per Rule 16 — this file is the technical record.
