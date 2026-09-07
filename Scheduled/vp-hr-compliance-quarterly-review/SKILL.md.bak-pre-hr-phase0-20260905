---
name: vp-hr-compliance-quarterly-review
description: Quarterly HR/employment-law compliance review of Valley Pawn's Handbook and P&P docs against current VA/federal law, building on the prior review.
model: claude-opus-4-8
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


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
Perform Valley Pawn's quarterly HR/employment-law compliance review for Full Circle Finance Inc DBA Valley Pawn (a 5-location Virginia pawn business — Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke — with an FFL at the Roanoke store). This is a recurring audit; treat this prompt as complete, self-contained instructions since this task run has no memory of any prior conversation or prior run.

Context:
- Governing documents live in the "Policies & Handbook" folder of Valley Pawn's Google Drive (jdavis@fcfpawn.com account): the "Employee Handbook — MASTER (editable)" (.docx) and "Valley Pawn — Policies & Procedures" (Google Doc).
- Prior compliance reports (titled things like "Valley Pawn Handbook Compliance Audit" or "Valley Pawn Handbook & P&P Compliance Review") also live in that Drive folder or its subfolders (e.g. "Original Handbook"). Locate the MOST RECENT prior report and build on it — do not repeat findings that are unchanged; only report what is new, resolved, or has changed since that report's date.
- The real-time policy channel is Slack #policy-announcements (channel ID C03BHQ9RLR0).
- Company email is jdavis@fcfpawn.com.

Steps:
1. Read the current Handbook and P&P documents in full.
2. Locate and read the most recent prior compliance review in the Drive folder; note its date and open findings.
3. Search Slack #policy-announcements and company email for any policy announced since the prior report's date that is not yet incorporated into the Handbook or P&P doc.
4. Research current Virginia and federal employment law via web search — Virginia law changes cluster around January 1 (minimum wage) and July 1 (Values Act, non-compete statute, and other amendments) each year, so specifically check for anything effective since the prior report. Cover at minimum: FLSA (minimum wage, overtime, exempt threshold), Title VII/ADA/ADEA/PDA/FMLA/USERRA/NLRA/COBRA, Virginia Minimum Wage Act, Virginia Overtime Wage Act, Virginia Wage Payment Act, Virginia Human Rights Act/Values Act, Virginia Pregnant Workers Fairness provisions, Virginia's non-compete restrictions, Virginia cannabis/off-duty-conduct law, Virginia whistleblower protection law, and pawn/FFL-specific considerations.
5. Produce: (a) a status table tracking every open finding from the prior report (resolved / still open / superseded by a law change), (b) a gap/deficiency table for anything new (Issue | Document & Section | Risk High/Med/Low | Law/Source | Recommended Fix), (c) a table of new policies found via Slack/email reconciliation with recommended placement, (d) a short list of items needing Virginia-licensed employment attorney sign-off. Cite specific statutes and effective dates; never invent a citation — mark "verify with counsel" if unsure. This is a compliance review, not legal advice, and should say so explicitly.
6. Build the report as a Word document (.docx) using the docx skill, save it to the "Policies & Handbook" Google Drive folder (or the local "Human Resources" project folder if Drive write access is unavailable), named "Valley_Pawn_Compliance_Review_[Month]_[Year].docx".
7. Post a concise summary to Slack #policy-announcements tagging Joshua Davis, highlighting anything newly high-risk or any Virginia/federal law change effective that quarter, and linking or naming the saved report.

Act autonomously using best judgment; do not stop to ask clarifying questions — flag genuine ambiguities in the report itself.