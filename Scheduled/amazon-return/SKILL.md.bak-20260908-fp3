---
name: amazon-return
description: Process an Amazon return via Chrome browser — find the item, initiate return, select UPS Store drop-off, and send back the QR code/label link.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

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
You are processing an Amazon return for Joshua. He will tell you which item to return.

## Steps

1. Open Amazon orders page using Chrome browser tools (navigate to https://www.amazon.com/gp/your-account/order-history).
2. Search for the item Joshua described in his orders. Try the exact product name first, then broader terms (e.g., "ethernet cable" instead of "cat 6 cable") if no results.
3. Click "View order details" on the matching order, then click "Return or replace items."
4. Select the return reason: "Bought by mistake" (unless Joshua specifies a different reason).
5. For packaging question, select "Package not opened" (unless Joshua says otherwise).
6. Add a brief comment if required (e.g., "Returning item — bought by mistake").
7. Click through any troubleshooting screens by selecting "Continue to return options."
8. Select refund to the default payment method.
9. **Always select "The UPS Store Dropoff"** as the return method — this is Joshua's strong preference.
10. Choose the nearest UPS Store location when prompted.
11. Click "Confirm your return."
12. After confirmation, copy the return confirmation page URL and send it to Joshua so he can access the QR code.
13. Also provide the UPS Store address and hours from the confirmation page.

## Important Notes
- Always use UPS Store drop-off — never select other options like Staples, Whole Foods, Kohl's, etc.
- The QR code link/confirmation URL is the most important deliverable — always send it back to Joshua.
- Amazon Business account is for Full Circle Finance.
- Use Chrome MCP tools (navigate, read_page, find, form_input, etc.) for all browser interactions.

<!-- migrated to working model 2026-06-15 -->