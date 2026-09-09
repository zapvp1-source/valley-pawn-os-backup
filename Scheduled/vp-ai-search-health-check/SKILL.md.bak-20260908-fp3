---
name: vp-ai-search-health-check
description: Weekly Valley Pawn AI-search (GEO) health check — schema, llms.txt, and Google/Bing NAP; posts to Slack #ai-marketing
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.

> 🛡️ **HARDENING RULES (added 2026-08-21, after a run stalled at step 0):** A prior run never reached Check 1 because it tried to mount `~/Documents/Claude/Projects` (an enterprise-map / global-instruction reflex) and that interactive folder-approval call aborted with no user present to click it, then a second tool call was flagged as user-interrupted. Neither was a real problem with the website checks — the run just never got there. To prevent repeats:
> 1. **This task is fully self-contained — skip ALL interactive/approval-gated steps.** Do NOT call `request_cowork_directory`, do not attempt to mount `~/Documents/Claude/Projects` or any other folder, and do not wait on any tool that requires a live user click (OAuth, folder pickers, confirmation dialogs). Scheduled runs are non-interactive — nothing under Documents/Claude is needed for this check. Go straight to CHECK 1 below using Claude-in-Chrome and the Slack MCP connector only.
> 2. **Retry transient tool errors before treating them as a failure.** If a browser navigation, JS execution, or Slack call errors with something that looks like a hiccup (AbortError, "tool permission stream closed," blank/incomplete page load, timeout, "user doesn't want to take this action right now" with no actual user present) — wait a few seconds and retry that one step up to 2 times. Only escalate to the Failure Alert Policy above if the SAME step still fails after 2 retries.
> 3. **A real finding is not a failure.** Missing schema blocks, a broken llms.txt, or NAP drift are the expected output of this check — report them in the Slack post per usual (🚨/⚠️ bullet list). Only trigger the Joshua DM failure alert if the check genuinely could not run end-to-end (e.g., site unreachable after retries, Slack post itself fails after retries) — never for a clean "here's what's wrong on the site" result.
> 4. **Always finish with a Slack post to #ai-marketing**, even a partial one, rather than stopping silently — e.g. "⚠️ Completed Checks 1–2, Check 3 (directory NAP) failed after retries — see next run" is a valid, non-alarming partial result and does NOT require the Joshua DM (core work substantially completed); only a total failure to post anything does.

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
Run the weekly Valley Pawn AI-search (GEO) health check, then post a summary to the Slack channel #ai-marketing (private channel, ID C0BCEESUANM). Use the Claude in Chrome browser tools for the web checks and the Slack MCP connector to post. Each run starts fresh — everything you need is below.

CONTEXT: Valley Pawn (thevalleypawn.com, WordPress). Schema is injected site-wide via WPCode snippet #738; /llms.txt is served via WPCode snippet #742. These were deployed for AI-search visibility and this check confirms nothing has silently broken or drifted.

CHECK 1 — SCHEMA (biggest lever):
- Navigate to https://thevalleypawn.com/?cb=health (cache-buster) and run JavaScript to collect every <script type="application/ld+json"> block.
- Confirm these 7 are present AND each parses as valid JSON: Organization "Valley Pawn"; PawnShop for Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke; and one FAQPage. (An 8th block from Yoast is normal — ignore it.)
- Flag if any of the 7 are missing or fail to parse.

CHECK 2 — LLMS.TXT:
- Navigate to https://thevalleypawn.com/llms.txt and confirm it returns plain-text content containing "Valley Pawn" and all five city names. Flag if it 404s, is empty, or returns HTML instead of text.

CHECK 3 — DIRECTORY NAP (Google + Bing, all 5 stores):
For each store, open the public listing and compare Name / Address / Phone / Hours to canonical below.
- Google: https://www.google.com/maps/search/valley+pawn+<city>+va
- Bing:   https://www.bing.com/maps?q=valley+pawn+<city>+va
Canonical NAP:
  • Culpeper — 571 James Madison Highway, Culpeper, VA 22701 — (540) 445-5510 — Mon–Sat 10am–6pm (ONLY store open Wednesdays)
  • Waynesboro — 1321 West Broad Street, Waynesboro, VA 22980 — (540) 221-6346 — Mon,Tue,Thu,Fri,Sat 10am–6pm (closed Wed & Sun)
  • Harrisonburg — 1790 East Market Street, Harrisonburg, VA 22801 — (540) 574-4500 — closed Wed & Sun
  • Lexington — 125 Walker Street, Lexington, VA 24450 — (540) 461-8349 — closed Wed & Sun
  • Roanoke — 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 — (540) 562-0776 — closed Wed & Sun

> 📌 **CANONICAL NAP CORRECTIONS (2026-08-23, confirmed by Joshua — do not revert):**
> 1. **Harrisonburg has NO suite number.** It is "1790 East Market Street" — full stop. The old
>    "Ste 22" that used to be in this file was WRONG, and was removed from our own website schema
>    and footer template on 2026-08-23. If "Ste 22" appears on ANY listing, that is a DEFECT to
>    correct — never treat it as canonical.
> 2. **Roanoke occupies BOTH Suite C and Suite D.** Customer-facing canonical stays "Suite C".
>    The ATF FFL record reads "2362-D" — that is **CORRECT, not drift.** Never "fix" 2362-D and
>    never flag it as an error. Where the full footprint is stated, "Suite C & D" is correct.
SOURCE-OF-TRUTH RULE (added 2026-08-03 after 5 weeks of misattributed drift). The public map page is a RENDERED surface, not our data. Bing Maps composes its address line from TomTom/OpenStreetMap geodata, which regularly disagrees with a perfectly correct Bing Places listing. Before flagging any Bing address as drift, open the owning console and compare:
- Bing Places console: https://www.bing.com/forbusiness/management (signed in as Joshua; per-store pages at /forbusiness/singleEntity?bizid=<id>)
  • Waynesboro 7ddd697b-9fe1-4c2c-b509-f1f129248ffb · Harrisonburg d3db1bc6-bf38-4695-bc02-180a9bd4b3da · Roanoke 9dd5c903-6a00-4c6f-86c0-41c8178473b6 · Culpeper a73bfbe6-a8f5-4b0c-b098-4246d9242376 · Lexington 042deef9-9f27-4045-9def-387e727b3c09
Then classify into one of three buckets, and NEVER collapse them into one "drift" count:
  1. LISTING DEFECT — console value is wrong. Actionable, whitelisted, hand to vp-ai-search-autofix.
  2. RENDER MISMATCH — console is correct, public map differs. NOT a listing bug and NOT fixable by editing the listing. Report it once as informational, then suppress it on subsequent weeks unless it changes. Known and accepted as of 2026-08-03: Roanoke public map drops "Suite C"; Harrisonburg public map shows "1790 Toni St".
  3. FOREIGN LISTING — a record we do not own (legacy MapQuest "Dixie Pawn Inc.", unclaimed Apple Business Connect). Needs a claim/merge, never an edit.
Also check the DESCRIPTION field in the Bing Places console for each store. It must name exactly five stores — Waynesboro, Culpeper, Harrisonburg, Roanoke, Lexington — and must be at or under 500 characters, or Bing silently keeps a stale version. A phantom sixth location (e.g. "Salem") is a real defect and AI engines quote this text directly.
NOTE: Bing listings SYNC FROM Google Business Profile. GBP is the upstream source of truth; a Bing-side edit can be overwritten on the next sync.

Flag as DRIFT: any legacy/wrong name (especially "Dixie Pawn"), wrong street number, missing suite (Roanoke must show "Suite C"), any wrong phone digit, wrong hours (watch the Culpeper-only-Wednesday rule), or a missing / duplicate / "permanently closed" listing. Ignore pure formatting differences (St vs Street, ZIP vs ZIP+4, phone format).

POST TO SLACK — channel #ai-marketing (ID C0BCEESUANM; do NOT DM anyone):
- If everything is clean, post one line: "✅ Valley Pawn AI-search health check — schema 7/7 ✅, llms.txt live ✅, listings 10/10 clean ✅"
- If anything is off, post a short skimmable bullet list of exactly what's wrong and the suggested fix (e.g. which snippet to re-enable in WPCode, or which store/directory drifted and to what). Keep it phone-readable. Lead with a 🚨 or ⚠️ header line.