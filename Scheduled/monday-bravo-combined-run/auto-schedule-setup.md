# Auto-schedule setup — Sunday→Monday 2 AM run

This file documents how to set up the Monday-night auto-trigger. It needs to be created from a **non-scheduled-task** Cowork chat session (the schedule system doesn't allow nested scheduled tasks). Open a fresh Cowork chat and paste the block below as your message.

## Schedule parameters

- **Task ID:** `monday-bravo-combined-run-auto`
- **Description:** Automated Monday 2 AM run of the Valley Pawn Bravo combined orchestrator.
- **Cron:** `0 2 * * 1` (Monday at 2:00 AM local / Eastern time)

## What to say in the new chat

```
Create a scheduled task named "monday-bravo-combined-run-auto" with the
cron expression "0 2 * * 1" (Monday 2 AM local). Use the prompt below
verbatim — it's the full runbook for the unattended run.
```

Then paste the prompt body that follows.

## Prompt body to paste

You are running Joshua's automated Monday morning Valley Pawn combined Bravo POS run. The user is not present — execute autonomously with the safeguards described below.

**Authoritative runbook:** read `/Users/joshuadavis/Documents/Claude/Scheduled/monday-bravo-combined-run/SKILL.md` first and follow it exactly. The SKILL documents:
- STEP 0 pre-flight checks (VM running, watcher alive, BravoAutoLogin alive, no stuck triggers). Pre-flight MUST pass before any trigger is dropped.
- STEP 1 drops a single multi-report trigger to the pipeline.
- STEP 2 chains the per-report SKILLs to compile and post to ops channels.
- STEP 3 sends a final roll-up DM to Joshua.

**Standing rules baked into the codebase that you must NOT override:**
- Login user is always FREE1@WAY at CUL/HAR/LEX/ROA and FREE1 at WAY (no @WAY suffix at the Waynesboro store).
- Never click "End Session" — the watcher uses Lock+Resume to preserve sessions. Step 5 of `lib/StoreCycle.ahk` has a username failsafe (Switch User → New User if pre-fill is wrong).
- Ops Slack posts are DATA ONLY. No source footers, no process commentary, no narrative paragraphs. Pipeline status/recovery commentary belongs in the DM to Joshua.
- Aged inventory ranking framing: lowest % is the best performer; add one-line callout naming the leader and laggard.
- Loan review: ">10% of loan balance = out of guidelines" — 🚨 callout for any store over.
- Employee rankings: exclude Preston Peters by name AND any $0.00 employee from the ops-channel post. Full population (including Preston/zeros) goes in the saved xlsx for the internal record.

**Trigger payload to drop in STEP 1** (substitute today's date and start-of-month):

```json
{
  "id": "monday-bravo-combined-YYYY-MM-DDTHH-MM-SS",
  "requested_at": "YYYY-MM-DDTHH:MM:SS-04:00",
  "reports": [
    {"name": "aged-inventory-summary", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD"},
    {"name": "loans-75-days-past-due", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD"},
    {"name": "layaways", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD"},
    {"name": "employee-activity", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-01"},
    {"name": "chekkit-inactives", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD"}
  ]
}
```

The employee-activity `date` field is the Start Date (first of current month). All other dates are today.

**Expected outputs**, saved to `/Users/joshuadavis/Documents/Claude/Scheduled/`:
1. `Aged_Inventory_Review_YYYY-MM-DD.xlsx`
2. `Loan_Layaway_Review_YYYY-MM-DD.docx`
3. `employee-sales-rankings-YYYY-MM-DD.xlsx` (full population, filter applied only in the Slack post)
4. Chekkit CSVs stashed at `_shared-bravo-data/YYYY-MM-DD/chekkit-inactives/{CUL,HAR,LEX,ROA,WAY}.csv`

**Expected ops-channel posts** (in this order):
- `#aged-inventory-review` (`C04NGH4FF35`) — aged inventory table + leader/laggard one-liner
- `#loan-review` (`C0B08RS2BMK`) — 75-day past-due bullet list with 10% threshold
- `#layaway-review` (`C04N24STDP1`) — 5-column badge table with 🔴 Locate callouts
- `#employee-performance` (`C0ATTLPQHR8`) — ranked list with Preston + $0.00 employees filtered out

**Failure handling:**
- The watcher has a 3-strike auth-failure circuit breaker and a 45-min hard-wall timeout. If either trips, the result.json shows `status: aborted` with skipped cells. Post whatever did succeed; DM Joshua with the failure reason.
- If pre-flight Step 0 fails and auto-restart can't recover, DM Joshua at `U03BB52MDSA` with the failure and stop. Do not drop a trigger against a non-functional pipeline.
- If only some cells succeed, post the chained SKILL anyway with the available stores; the chained SKILL's format already accommodates partial data.

**Joshua's Slack DM ID:** `U03BB52MDSA`.
**Preston Peters (Operations Manager):** `U03BWMEM9GR`. Do NOT auto-DM Preston unless the runbook explicitly says to.

Final DM to Joshua at the end should summarize: cells succeeded/failed/skipped, channels posted to, files saved, any anomalies observed, and confirmation that the trigger queue is now empty and the watcher is alive for the next cycle.

## macOS-side prerequisites

- *Mac sleep:* DONE — Joshua confirmed 2026-05-13 that Mac is set to never sleep. No `pmset` wake schedule needed.
- *Parallels VM stays running:* leave it running on shutdown. Or set Parallels → Configure → General → Start automatically: "When Mac user logs in."
- *Parallels Pause-idle:* MUST BE DISABLED. The CLI `prlctl set --pause-idle off` requires admin auth. Do this once via the GUI: Parallels Desktop → with the Windows 11 VM selected → Configure → Optimization → Resource Usage → uncheck "Pause when no apps are open" (and any related "Pause Windows after N minutes of inactivity" toggle). Verify after by running `prlctl list -i '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' | grep 'Pause idle'` and confirming it reads `Pause idle: off`. Without this, the watcher will be paused mid-run by Parallels' power management and the 2 AM auto-trigger will take hours instead of 30 minutes.
- *bravo_watcher.ahk and BravoAutoLogin.ahk auto-start:* both are configured to run from `Startup` folder inside the VM, so they come up automatically when Windows logs in. Verify by checking `Get-ChildItem $env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup` inside the VM.

## To disable the schedule later

From a non-scheduled-task Cowork session: "Disable the `monday-bravo-combined-run-auto` scheduled task." Or delete via the scheduled-tasks UI.
