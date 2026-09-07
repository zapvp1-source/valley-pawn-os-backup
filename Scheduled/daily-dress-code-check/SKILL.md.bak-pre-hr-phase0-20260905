---
name: daily-dress-code-check
description: Weekdays + Saturday at 10 AM — check Google Home cameras at Valley Pawn locations, assess dress code compliance for confirmed employees only, and post report to Slack #general. Wednesdays: Culpeper only. All other days: all 5 locations.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are checking Valley Pawn employee dress code compliance via Google Home cameras and posting a summary to Slack #general (channel ID: C03BETSS669).

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

## CRITICAL RULES — READ BEFORE EVALUATING

### 1. Valley Pawn shirts come in MULTIPLE COLORS
Valley Pawn branded clothing includes polos, jackets, and shirts in GREEN, ORANGE, and other colors. Do NOT assume only dark green polos are compliant. Any collared shirt, polo, or jacket — regardless of color — is likely a company shirt. If you see an employee in a colored polo or collared shirt (green, orange, dark green, etc.), that is COMPLIANT.

### 2. Only evaluate people BEHIND THE COUNTER or at WORKSTATIONS
People on the sales floor, browsing merchandise, or standing on the customer side of the counter are CUSTOMERS, not employees. Only evaluate dress code for individuals who are:
- Behind the counter / at a workstation
- In the back room / at a register
- Clearly in an employee-only area

If someone is on the customer side of the counter, they are a customer. Do NOT flag them.

### 3. When in doubt, default to COMPLIANT
If camera angle is unclear, if branding can't be confirmed, if the image is too distant — mark as COMPLIANT. Only flag a violation when you are HIGHLY CONFIDENT that a person behind the counter is wearing something clearly non-compliant (plain hoodie with no branding, casual t-shirt, tank top, etc.).

The threshold for flagging a violation should be very high. If you are less than 90% sure it's a violation, mark it as compliant.

### 4. Employees who are wearing jackets or outerwear over their shirt
Employees may wear jackets, hoodies, or outerwear OVER their Valley Pawn shirt, especially in colder months. This is NOT a violation. If you see a jacket or hoodie and can't see the shirt underneath, default to compliant.

### 5. No employees visible = COMPLIANT
If no employees are visible at a location (empty counter, no one at workstations), mark that location as :white_check_mark: All in dress code. Do NOT use :white_circle: or write "No employees visible." That status DOES NOT EXIST. Every location gets either :white_check_mark: or :red_circle:, nothing else.

## Excluded Employees
Exclude these from analysis: Hillary Davis, Joshua Davis, Sandi Cole, Preston Peters, Audrey Davis, Kennedy Davis, Madison Davis, Savannah Davis

## Locations to Check
- **All days except Wednesday:** Check all 5 locations (Harrisonburg, Lexington, Culpeper, Roanoke, Waynesboro)
- **Wednesdays:** Check Culpeper only

## Steps

### 1. Navigate to Google Home — USE THE RIGHT ACCOUNT
**The cameras are on the `fullcirclepawn@gmail.com` Google account — NOT `jdavis@fcfpawn.com`.** In Chrome that's the second signed-in account, so always go DIRECTLY to:

    https://home.google.com/u/1/home

Do NOT start at plain home.google.com (it defaults to `/u/0/` which is jdavis@fcfpawn.com and shows "Creating a new home isn't supported" — no cameras). Do NOT try home.nest.com. Do NOT attempt to re-auth jdavis@fcfpawn.com for cameras.

If `/u/1/` prompts for a password or passkey: this is a genuine blocker only Joshua can clear (per the Field Communication Standard, do not post a Slack message about it) — DM Joshua directly (U03BB52MDSA) that the camera login needs a refresh, then stop for this run. Do NOT try `/u/0/` or home.nest.com as fallbacks, the cameras aren't there.

From the camera grid:
- Top-left shows the home name (e.g. "Harrisonburg") with a dropdown — click it to switch between Harrisonburg, Lexington, Culpeper, Roanoke, Waynesboro.
- After switching homes the page lands on Devices by default — click the "Cameras" tab in the left sidebar to get the grid view.
- Take a screenshot of each location's camera grid, then zoom in for a closer look at any camera where someone might be present.

### 2. Evaluate Dress Code
For each location:
- Identify people who are BEHIND THE COUNTER or at workstations (these are employees)
- Ignore anyone on the customer side (they are customers)
- Check if employees are wearing any type of collared shirt, polo, or branded clothing in ANY color
- Remember: green, orange, and other colored polos/jackets are ALL Valley Pawn branded and compliant
- Only flag clear violations where someone behind the counter is in obviously non-work attire
- If no employees are visible, mark as compliant

### 3. Build and Send the Slack Message
Format:
```
:camera: _Dress Code Check — [Weekday, Month Day, Year] @ [Time]_
• [Location] — :white_check_mark: All in dress code
• [Location] — :red_circle: [Only if HIGHLY confident — describe specific violation]
```

IMPORTANT: There are only TWO statuses: :white_check_mark: and :red_circle:. There is NO "no employees visible" status. If no employees are visible, use :white_check_mark:.

Only use :red_circle: if you are extremely confident (90%+) that a confirmed employee (behind the counter) is wearing clearly non-compliant clothing. When in doubt, use :white_check_mark:.

### 4. Send to Slack
Send the formatted message to #general (channel ID: C03BETSS669).

## REMEMBER
- **Cameras live on fullcirclepawn@gmail.com → always start at https://home.google.com/u/1/home**
- Multiple shirt colors are Valley Pawn branded (green, orange, etc.)
- People on the sales floor = customers, NOT employees
- Jackets/outerwear over shirts = compliant
- Unclear camera angle = compliant
- Can't confirm branding = compliant
- No employees visible = COMPLIANT (:white_check_mark:)
- When in doubt = COMPLIANT