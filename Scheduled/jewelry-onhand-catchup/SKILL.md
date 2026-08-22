---
name: jewelry-onhand-catchup
model: claude-sonnet-5
description: Morning self-heal 7:45 AM (Tue-Sun): if last night's 8:30 PM jewelry pull was missed, rerun it inside the freeze window (before stores open at 10) and post the table — makes the daily jewelry count self-healing.
---

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
CATCH-UP run for the jewelry-onhand-nightly-pull task. That task runs 8:30 PM Mon-Sat but is silently skipped if the Claude app is closed. You run the next morning and self-heal: Bravo on-hand doesn't change overnight (stores closed 6 PM-10 AM), so a pull before 10 AM still reflects last night's close.

STEP 0 — Should you run at all?
1. Via mcp__Control_your_Mac__osascript get: date '+%Y-%m-%d %A' and yesterday: date -v-1d '+%Y-%m-%d %A'.
2. If YESTERDAY was Sunday: no count expected — end silently.
3. Check: ls ~/Documents/Claude/Projects/'Bravo Data Extraction'/output/ | grep '<YESTERDAY>_.*jewelry-case-counts'. If CSVs exist for yesterday: the nightly run worked — end silently, post NOTHING.
4. If it's already past 9:30 AM when you start, do NOT begin a pull (won't finish inside the freeze window) — end silently; the 9:15 watchdog handles alerting.

STEP 1 — Read the playbook. Read ~/Documents/Claude/Scheduled/jewelry-onhand-nightly-pull/SKILL.md and follow ITS full procedure (open-stores gate, health gate, contention check, trigger format, per-store walls, no-false-zeros rule, empty-category rule, remapping PENDANTS=Pendants+Charms+Brooches and NECKLACES=Chains+Necklaces, posting format), with these overrides:
- Use YESTERDAY's date in trigger ids and the report date field (id pattern: jewelry-onhand-<YESTERDAY>-catchup-<STORE>).
- CONTENTION: before dropping triggers, verify no unclaimed triggers exist in the triggers/ dir and the most recent log in logs/ is not mid-run (tail it; if a pull is actively writing, wait 10 min and re-check, max 3 waits, then abort silently).
- HARD SEQUENCING RULE: never touch Chrome while the VM is pulling — Chrome freezes under VM load (learned 2026-08-21). Bravo pulls FIRST, then read the PM sheets from Slack #end-of-day (channel C03C7HV8L48) via Chrome, zooming each sheet and sum-verifying each store's PM column against its written total.
- Post the Expected/Counted/Variance table to #jewlery-counts (C0BM9NHGTT4), titled "Jewelry Count — <Yesterday day + date> CATCH-UP (expected = Bravo pulled this morning inside freeze window; counted = last night's PM sheet)". No commentary beyond the standard notes (empty-category-as-zero notes, any store missing a sheet is excluded, never guessed).

STEP 2 — Log a run record by APPENDING (never Edit tool, use osascript >>) to ~/Documents/Claude/Projects/'Bravo Data Extraction'/STATUS.md.

FAILURE PATH: on any failure, ONE plain-language Slack DM to Joshua (D03BHQH5VGT), nothing technical, no team channels. Never report an empty-category error as 0 without cross-checking the most recent prior-day CSV.