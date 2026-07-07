---
name: salt-run-monthly-seo-audit
description: Monthly SEO and competitor audit for Salt Run Landscape Co.
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

Monthly SEO audit and competitor scan for Salt Run Landscape Co. (saltrunlandscape.com).

Goal: Check how Salt Run is ranking on Google, what competitors are doing differently, and what should change on the site this month.

Steps:
1. Indexing check — Google search "site:saltrunlandscape.com" via WebSearch. Report how many pages are indexed.
2. Ranking check — Run WebSearch for these key terms and note where Salt Run appears (page 1 / page 2 / not found):
   - "St. Augustine landscape company"
   - "landscape Nocatee FL"
   - "Ponte Vedra lawn care"
   - "Anastasia Island landscaping"
   - "palm tree installation St. Augustine"
3. Competitor scan — visit these 3 sites via Chrome (or WebFetch where available) and note any visible changes vs last month:
   - lawnsharkfl.com (Lawnshark Landscaping — direct competitor)
   - themasterslawncare.com (The Master's Lawn & Pest)
   - bigoaklandscapes.com (Big Oak Landscape Design)
   - Take a screenshot of each homepage hero for visual comparison.
4. New competitor check — WebSearch "landscape company St. Augustine 2026" and note any new entrants in the top 10 results.
5. Phase readiness signal — does Salt Run still have only 1 page? If yes, flag whether it's time to add subpages (Phase 2: /portfolio + /about; Phase 3: per-service pages; Phase 4: per-area pages + /blog).
6. Report a punch list of 3–5 specific actions Joshua should take this month, prioritized.

Keep the report under 400 words. Post to the chat session.