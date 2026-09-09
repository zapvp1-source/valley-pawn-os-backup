---
name: dismiss-employee
description: RETIRED 2026-09-05 — superseded by the `offboard-employee` skill (Gusto dismissal + Slack + Chekkit + Bravo + VA final-pay checklist). Kept disabled for rollback only; do not re-enable.
model: claude-opus-4-8
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

## Failure policy (Rule 16 / Hardening Standard #6 — updated 2026-09-05)
Retry once, then try the documented alternate path. If still failing: write the technical detail to this task's run log/STATUS file and stop. Silence in every Slack channel. At most ONE plain-language DM to Joshua (D03BHQH5VGT), and only if a decision only he can make is blocking. Never post failure notices, technical jargon, or partial/incomplete data anywhere.

> ⚠️ **FIELD COMMUNICATION RULE (retained from the 2026-07-22 v2 banner):** anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths.

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
You are performing a full employee dismissal and offboarding for Valley Pawn (Full Circle Finance Inc). Joshua (the CEO) has triggered this task and will provide the employee's name and reason for dismissal. Your job is to complete the ENTIRE flow — Gusto termination, Slack removal, and Chekkt removal — via Chrome browser and available connectors. No human intervention needed after initial input.

## IMPORTANT: Get Input First

At the very start, ask Joshua for:
1. **Employee name** (first and/or last)
2. **Reason for termination** (e.g., performance, attendance, misconduct, layoff, voluntary resignation, etc.)
3. **Effective date** (or assume today if not specified)

Wait for his response before proceeding.

---

## PHASE 1: GUSTO — Terminate the Employee

### Step 1.1: Verify the Employee in Gusto API

Use the Gusto MCP tool `list_employees` with `terminated=false` and `search_term` set to the employee name Joshua provided. Confirm you found the correct person — verify their name and location match a known Valley Pawn employee. If multiple matches or no match, ask Joshua to clarify.

Then use `get_employee` with their UUID to pull full details (name, job title, location, hire date). Present a brief confirmation to Joshua:
- Full name
- Job title
- Location
- Hire date

Say: "Proceeding with dismissal for [Name] at [Location]. Starting now."

### Step 1.2: Navigate to Gusto via Chrome

1. Call `tabs_context_mcp` with `createIfEmpty: true` to get or create a tab.
2. Create a new tab with `tabs_create_mcp`.
3. Navigate to `https://app.gusto.com` — take a screenshot to confirm you're logged in.
4. If not logged in or on a login page, tell Joshua he needs to be logged into Gusto in Chrome first, then stop.
5. Once confirmed logged in, navigate to the People section. The URL is typically `https://app.gusto.com/people` or find the "People" or "Team" link in the navigation.
6. Take a screenshot to see the employee list.

### Step 1.3: Find and Select the Employee

1. Use `find` to locate the employee by name on the People page, or search for them using any search bar.
2. Click on the employee's name/row to open their profile.
3. Take a screenshot to confirm you're on the correct employee's profile page.

### Step 1.4: Initiate the Dismissal/Offboarding Flow

1. Look for an action menu, "..." menu, or a button like "Dismiss", "Terminate", "Offboard", "End employment", or similar. Use `find` to locate it.
2. If there's a "..." or actions/kebab menu, click it first to reveal the dismiss option.
3. Click the dismiss/terminate/offboard option.
4. Take a screenshot to see the dismissal form/wizard.

### Step 1.5: Complete the Termination Form

Gusto's termination flow typically asks for several fields. Fill in each one:

- **Last day of work / Termination date**: Use the date Joshua provided (or today). Use `find` to locate the date field, click it, clear it, and type the date.
- **Reason for termination**: Select from dropdown or radio buttons. Map Joshua's stated reason to the closest Gusto option (Involuntary termination, Voluntary resignation, Laid off, Job performance, Misconduct, etc.). Use `find` and `read_page` to see available options.
- **Additional details / notes**: If there's a text field for notes, enter the specific reason Joshua provided.
- **Final paycheck**: Select the default/standard option unless Joshua specified otherwise.
- **Benefits / COBRA**: Select default options if asked.
- **Any other required fields**: Take screenshots at each step, read the page, and fill in whatever is required.

At EACH step of the wizard/form:
1. Take a screenshot
2. Use `read_page` or `find` to understand what's being asked
3. Fill in the appropriate values
4. Click "Continue", "Next", or equivalent to proceed

### Step 1.6: Review and Submit

1. Before clicking the final "Submit" / "Confirm" / "Dismiss employee" button, take a screenshot of the review/summary page.
2. Tell Joshua: "About to finalize dismissal for [Name]. Effective [date]. Reason: [reason]. Confirming now."
3. Click the final confirmation button.
4. Take a screenshot to confirm the dismissal was processed successfully.

---

## PHASE 2: SLACK — Remove from All Channels

After Gusto termination is complete, remove the employee from all Slack channels.

### Step 2.1: Find the Employee in Slack

Use the Slack MCP tool `slack_search_users` to find the employee by name. Note their Slack user ID and display name.

### Step 2.2: Find All Their Channels

Use `slack_search_channels` or browse Slack channels to identify which channels the employee is a member of. You may need to check each channel the company uses. 

Common Valley Pawn Slack channels to check — read each channel's member list:
- Search for the employee across all public and private channels using available Slack search tools.

### Step 2.3: Remove from Each Channel via Chrome

For each channel the employee is in:
1. Navigate to the Slack workspace in Chrome: `https://app.slack.com`
2. Open each channel where the employee is a member
3. Click on the channel name or member list to see members
4. Find the employee's name in the member list
5. Click on their name to open their profile/options
6. Look for "Remove from channel" option and click it
7. Confirm the removal if prompted
8. Take a screenshot to confirm
9. Repeat for ALL channels

Alternative approach if Slack admin panel is available:
1. Navigate to `https://app.slack.com/admin` or the workspace settings
2. Find the employee in the member management section
3. Deactivate their account entirely (this removes them from all channels at once)
4. This is the preferred approach if available — it's faster and more thorough

### Step 2.4: Confirm Slack Removal

Report: "Removed [Name] from all Slack channels" or "Deactivated [Name]'s Slack account" — whichever method was used.

---

## PHASE 3: CHEKKT — Remove from All Channels

After Slack is done, remove the employee from Chekkt (the reputation management / messaging platform Valley Pawn uses).

### Step 3.1: Navigate to Chekkt via Chrome

1. Use an existing tab or create a new one.
2. Navigate to `https://app.chekkit.io` (or the Chekkt login/dashboard URL — try variations like `https://dashboard.chekkit.io`, `https://app.chekkit.com` if the first doesn't work).
3. Take a screenshot to confirm you're logged in.
4. If not logged in, tell Joshua he needs to log into Chekkt in Chrome first.

### Step 3.2: Find Team/User Management

1. Look for a "Settings", "Team", "Users", or "Members" section in the Chekkt dashboard.
2. Use `find` and `read_page` to navigate to user/team management.
3. Take a screenshot to see the team members list.

### Step 3.3: Remove the Employee

1. Find the employee's name in the team/users list.
2. Click on their name or the action menu next to them.
3. Look for "Remove", "Delete", "Deactivate" or similar option.
4. Click it and confirm any dialogs.
5. Take a screenshot to confirm removal.

### Step 3.4: Confirm Chekkt Removal

Report: "Removed [Name] from Chekkt."

---

## FINAL SUMMARY

After all three phases are complete, provide a final summary to Joshua:

"All done. Here's what was completed for [Employee Name]:
✓ Dismissed from Gusto — effective [date], reason: [reason]
✓ Removed from Slack — [deactivated account / removed from X channels]
✓ Removed from Chekkt — account removed

[Employee Name] has been fully offboarded."

---

## Error Handling

- If any page doesn't load or looks unexpected, take a screenshot and describe what you see.
- If a UI has changed and you can't find expected elements, use `read_page` with `filter: "interactive"` to discover available buttons/links.
- If a confirmation dialog or popup appears, read it carefully, take a screenshot, and proceed if it's part of the normal flow.
- Always wait 1-2 seconds after clicking major buttons for pages to load before taking screenshots.
- If you get stuck on any phase, report what happened and move on to the next phase so the other platforms still get cleaned up.

## Tools Available

- **Gusto MCP**: `list_employees`, `get_employee` — for looking up the employee
- **Slack MCP**: `slack_search_users`, `slack_search_channels`, `slack_read_channel`, `slack_send_message` — for finding the employee in Slack
- **Chrome MCP**: `tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `find`, `read_page`, `computer` (screenshot, left_click, type, key, wait, scroll), `form_input`, `get_page_text` — for all browser automation across Gusto, Slack, and Chekkt
- **AskUserQuestion** — if you need clarification from Joshua

<!-- migrated to working model 2026-06-15 -->