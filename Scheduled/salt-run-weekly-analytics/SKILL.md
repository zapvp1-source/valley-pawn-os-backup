---
name: salt-run-weekly-analytics
description: Weekly Google Analytics review for Salt Run Landscape Co.
model: claude-haiku-4-5
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

Weekly Google Analytics check-in for Salt Run Landscape Co. (saltrunlandscape.com).

Goal: Pull last 7 days of site analytics, surface what changed, and recommend any actions Joshua should take.

Steps:
1. Open Chrome to https://analytics.google.com/analytics/web/ and navigate to the "Salt Run Landscape Co." property. (Joshua is logged in via his Google account.)
2. If GA tracking isn't yet installed on the site (no data at all), report that and stop — note Joshua needs to provide his GA Measurement ID.
3. Otherwise, pull and report these metrics for the last 7 days vs. the previous 7 days (% change):
   - Total sessions and users
   - Top 5 landing pages
   - Top 5 traffic sources (organic, direct, social, referral)
   - Average session duration and bounce rate
   - Form submissions / conversion events (the inline hero form fires when "Get My Free Estimate" is clicked)
   - Mobile vs desktop split
4. Identify the single most interesting signal — the thing that changed most week-over-week — and call it out specifically.
5. Recommend 1–2 concrete actions based on what you saw (e.g. "your Nocatee landing page got 3x traffic — add more Nocatee-specific content", or "bounce rate is 80% on mobile — investigate mobile hero form").
6. Post the summary to the chat session that owns this task (notifyOnCompletion is on).

Context Joshua may need:
- Site is live at saltrunlandscape.com on WordPress.com Business (Atomic platform).
- Custom theme is "Salt Run Landscape" (single-page).
- Top competitors: Lawnshark Landscaping, The Master's Lawn & Pest, Big Oak Landscape Design.
- Service area: St. Augustine, Anastasia Island, Ponte Vedra, Nocatee, Vilano Beach, St. Johns County.

Keep the report under 300 words.