# Bravo Data Extraction — Unified Health & Self-Heal Runbook

**Owner:** Joshua Davis · **Created:** 2026-06-17 · **Status:** Phase 1 live (gate + watchdog), Phase 2 backlog (handler conversions)

This is the single source of truth for **how Valley Pawn gets data out of Bravo reliably, and how it heals itself when Bravo breaks** — with no human intervention except the one genuinely-manual case (dead guest agent / login lockout), which is escalated by a single Slack DM.

Read this alongside `KNOWN_ISSUES.md` (the confirmed root-cause log). This runbook is the *operating* layer; KNOWN_ISSUES is the *diagnosis* layer.

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
| 2 | later cells `EnsureStore failed` / `BackToDashboard` | cascade after a wedge | gate recovers to Dashboard before the run; **Phase 3:** watcher auto-recovers between cells + fail-fast | no |
| 3 | `Bravo window not found/ready within 30s` | foreground stolen (console `prlctl exec` during a run) / window not foregrounded | gate nudge (maximize/activate); **operating rule:** never run console `prlctl exec` while a run is active | no |
| 4 | `ClickByName: … not found` (e.g. Custom Reports) | handler-specific nav fragility | **Phase 2/4:** harden that handler; retry from clean Dashboard | no (usually) |
| 4b | cell `status=success` but `row_count: 0` / header-only CSV | **CONFIRMED handler defect** — `chekkit-inactives` grid-walk writes the header then captures 0 rows (verified 2026-06-17 across all 5 stores AND on the historical 2026-05-30 set). The `chekkit-gridonly` probe captured phones only. The cell falsely reports success on empty output. | **Phase 4 (next handler to fix):** repair `WriteChekkitGridToCsv` row capture (likely a date-window/grid-iteration bug); make the cell report `error` when 0 rows so it never silently sends empty campaigns | no |
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
