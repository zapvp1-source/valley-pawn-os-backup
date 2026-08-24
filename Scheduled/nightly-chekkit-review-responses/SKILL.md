---
name: nightly-chekkit-review-responses
description: Respond to all 4 and 5 star reviews across 5 pawn shop locations in Chekkit, then post summary to Slack #chekkit-updates channel (no DMs).
model: claude-opus-4-8
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

Navigate to https://dashboard.chekkit.io/reviews and respond to all 4-star and 5-star reviews across all 5 Valley Pawn store locations using Chekkit's AI "Generate Response" button. Process BOTH Google and Facebook reviews for each store.

**Stores to process:**
1. Valley Pawn - Culpeper
2. Valley Pawn - Harrisonburg
3. Valley Pawn - Roanoke
4. Valley Pawn - Waynesboro
5. Valley Pawn-Lexington

**For each store, process Google reviews first, then Facebook reviews:**
- Switch to the store using the location dropdown in the top-left corner
- In the top-right corner of the reviews dashboard, there is a platform dropdown that defaults to "Google". Process all reviews under Google first, then click that dropdown and switch it to "Facebook" and process those reviews too.
- For each platform, scroll through all reviews and find any with a "Respond to [Name]" button (these are unresponded reviews)
- For each unresponded review, zoom in to confirm the star rating before acting:
  - **4 or 5 stars:** Click "Respond to [Name]", click "Generate Response", wait for the AI to finish generating, then click "Post". Confirm the "Success - You responded to your review!" toast appears.
  - **1, 2, or 3 stars:** Skip — do NOT respond. Record the reviewer's name, star rating, store location, platform (Google or Facebook), and a brief snippet of the review text for the summary report.

**After all 5 stores and both platforms are complete, post a single message to the Slack channel #chekkit-updates (channel ID C0B0FQZ4FS8) with a summary that includes:**

1. Confirmation that all 4 and 5-star reviews were responded to successfully, with a count of how many were responded to across all locations (combined Google + Facebook).
2. A breakdown of any 1-3 star reviews that need attention, including: reviewer name, platform (Google/Facebook), store location, star rating, and a brief excerpt of the review. If there are no 1-3 star reviews needing attention, explicitly say "No 1-3 star reviews require attention tonight."

Do NOT DM Preston Peters. Post the routine nightly summary only to the #chekkit-updates channel.

**ADDED 2026-08-23 - LOW-STAR ESCALATION (additive; nothing about the 4/5-star response flow changes).**
A 1-3 star review mentioned only in #chekkit-updates does not reliably get seen. In August 2026 two 1-star
Culpeper reviews alleging gold lowballing sat unanswered for two weeks while this task ran nightly and
correctly reported them to the channel every single night. Reporting is not escalation.

So IN ADDITION to the channel summary above: if this run finds any review of 3 stars or fewer that has no
response yet, send Joshua ONE Slack DM (channel D03BHQH5VGT), plain everyday language, e.g.:

    Heads up - Culpeper got a 1-star review from [Name] on Google: [short snippet]. Nobody has replied yet.

Rules for this DM:
- Only for reviews at 3 stars or below with NO response yet.
- ONE DM per run listing all of them - never one DM per review.
- If there are no new low-star reviews, send nothing. Silence is the correct outcome.
- Do NOT auto-reply to a low-star review. A human writes those. Keep skipping them in the response flow
  exactly as the step above says.
- Do not re-alert a review that was alerted on a previous run. Track alerted reviews in state.json in this
  task folder (create it if absent), keyed by reviewer name + store + review date.
- This is a customer-service escalation, NOT a failure alert, so it does not conflict with the Failure
  Alert Policy at the top of this file.


Example message format:
---
✅ Nightly review responses complete! Successfully responded to X reviews across all 5 Valley Pawn locations (Google + Facebook).

⚠️ The following 1-3 star reviews need attention:
• [Reviewer Name] — [Google/Facebook] — [Store] — [X stars]: "[Review snippet]"
• ...

(or "No 1-3 star reviews require attention tonight." if none found)
---

<!-- migrated to working model 2026-06-15 -->