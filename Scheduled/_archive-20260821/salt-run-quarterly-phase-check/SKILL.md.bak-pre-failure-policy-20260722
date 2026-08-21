---
name: salt-run-quarterly-phase-check
description: Quarterly phase readiness check for Salt Run Landscape Co. — recommend whether to graduate to next site phase.
---

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

Quarterly phase readiness check for Salt Run Landscape Co. (saltrunlandscape.com).

Goal: Determine whether Salt Run has accumulated enough business inputs (real photos, reviews, completed projects) to graduate from one website phase to the next. The site started in Phase 1 (single homepage) and was designed to evolve into Phase 2 → 3 → 4 over time.

Phase definitions:
- **Phase 1 (Current at launch):** Single homepage. No subpages needed yet.
- **Phase 2:** Add /portfolio (real project photos) + /about-joshua (founder story). Trigger: 5+ completed projects with phone photos.
- **Phase 3:** Add /services/lawn-maintenance, /services/palm-installation, /services/irrigation, etc. Trigger: SEO is becoming a priority and per-service ranking matters.
- **Phase 4:** Add /service-area/nocatee, /service-area/ponte-vedra, etc. + /blog. Trigger: ready to invest in content marketing for organic traffic.

Steps:
1. Check the live site — count current pages, note which phase the site is in.
2. Ask Joshua via chat (he should answer when this report fires):
   a. How many completed projects does he have photos for?
   b. How many Google reviews does the business have now?
   c. What's the biggest growth bottleneck right now — getting found, converting visitors, or capacity?
3. Based on his answers, recommend whether to:
   - **Stay in current phase** (and what to focus on instead),
   - **Graduate to next phase** (and offer to build the new pages this session), or
   - **Skip to a later phase** (if the bottleneck makes that more impactful).
4. If recommending a phase upgrade, lay out the specific pages to add and rough scope (each subpage = ~30 min of build work with the existing custom theme).

Keep the report concise. Post to chat. Wait for Joshua's answers if Step 2 questions need a response.