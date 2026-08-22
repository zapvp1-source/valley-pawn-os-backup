---
name: vp-gusto-signature-chase
description: Mondays 9:05 AM — check Gusto for unsigned policy documents and duplicate/never-sent templates, post an employee reminder to Slack #policy-announcements, DM Joshua the internal gaps.
model: claude-sonnet-5
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
Valley Pawn (Full Circle Finance Inc) — weekly Gusto policy e-signature chase + duplicate audit.

Read the `valley-pawn-context` and `vp-operating-rules` skills first for brand voice and the hard rules. Keep all Slack language plain per the Field Communication Standard: no tool names, no file paths, no technical jargon, no API talk. Employees should read it in one pass.

## ALWAYS EXCLUDED — never name these two anywhere in this task's output

- **Joshua Davis** — `2f2d61c5-f19e-4d8e-9e4c-d7d6b62f93d6`
- **Hillary Davis** — `94fa77de-beeb-4779-b669-4df93199bd05`

Filter both out by UUID (not by name — names change). They do not appear in the Slack post, the DM, or any total. Also exclude anyone with a non-null `terminated_at`.

## Step 1 — Pull the data from Gusto (no clicking, no screenshots)

Gusto's MCP connector does NOT expose documents. Use Chrome instead:

1. Open a tab to `https://app.gusto.com/payroll_admin/documents/shared/active`.
2. **If the URL is on `login.gusto.com`, you are logged out.** Do NOT try to log in and do NOT touch a passkey or biometric prompt. Send ONE plain-language Slack DM to Joshua (`D03BHQH5VGT`) saying you couldn't get into Gusto this morning and will try again next run, then STOP. Never post a partial or empty list to a team channel.
3. **Gusto sessions expire mid-task.** Re-check `location.href` before each major step. A sudden run of failures late in the flow is usually a silent logout, not a bug.
4. Everything below is a same-origin `fetch` with `credentials:'include'` run from that logged-in tab via `javascript_tool`. Read-only. Company UUID `15bc2823-564f-4c1a-8464-9b0e7d79d3e8`.

```js
const C='15bc2823-564f-4c1a-8464-9b0e7d79d3e8';
const SKIP=['2f2d61c5-f19e-4d8e-9e4c-d7d6b62f93d6','94fa77de-beeb-4779-b669-4df93199bd05'];
const emps=await (await fetch(`/api/companies/${C}/employees`,{headers:{Accept:'application/json'},credentials:'include'})).json();
const byUuid={}; emps.forEach(e=>byUuid[e.uuid]={n:(e.preferred_first_name||e.first_name)+' '+e.last_name, term:e.terminated_at});
const tmpls=await (await fetch(`/api/companies/${C}/document_templates`,{headers:{Accept:'application/json'},credentials:'include'})).json();
// per template: const rq=await (await fetch(`/api/document_templates/${id}/requests`,...)).json();
// rq[i] = {status:'completed'|'requested', target_id:<employee uuid>, signed_at}
```

Build three lists.

**LIST A — open signatures.** Every template with `processing_state === 'approved'` and `statistics.unsigned_request_count > 0`; pull its `/requests`, take everyone whose `status !== 'completed'`, resolve via `byUuid`, then drop anyone in `SKIP` and anyone terminated.

> The raw `unsigned_request_count` is inflated — terminated employees keep open requests forever. Never quote it. Count only people who survive the filter.

**LIST B — created but never sent.** Every template whose `processing_state` is NOT `approved`. Zero recipients — the policy exists but nobody was asked to sign it.

Known and accepted as of 2026-08-05 — one line only if still unresolved: `7455446` (ROC - Late to work, needs to go out as an Individual document) and `6984265` (duplicate Overtime Policy draft). Anything NEW is the real signal.

**LIST C — duplicates.** Two live templates for one policy is a defective HR record: you cannot later prove which version an employee agreed to. Detect with:

```js
const norm=s=>s.toLowerCase()
  .replace(/\(.*?\)/g,' ')
  .replace(/[^a-z0-9 ]/g,' ')
  .replace(/\b(policy|policies|guideline|guidelines|standard|standards|procedure|update|effective|revised|final|draft|the|a|and|of|for|v\d+)\b/g,' ')
  .replace(/\s+/g,' ').trim();
const groups={}; tmpls.forEach(x=>{const k=norm(x.document_name); (groups[k]=groups[k]||[]).push(x);});
const dupes=Object.values(groups).filter(v=>v.length>1);
```

For each group report every id, exact title, state, created date, and signed/unsigned counts, so Joshua can pick the record copy at a glance.

Known and accepted as of 2026-08-05, mention only if still unresolved: `7893283` + `7893330` (Gold Scrap Bucket Naming — created 17 minutes apart, both sent to all 14) and `6984272` + `6984265` (Overtime Policy). Any NEW duplicate group is a red flag — lead the DM with it.

**When merging LIST A for the Slack post, collapse duplicate groups into ONE line** so employees never see the same policy listed twice.

## Step 2 — Post the employee reminder to Slack `#policy-announcements` (C03BHQ9RLR0)

Only if LIST A is non-empty after filtering. Friendly nudge, not a scolding:

> *Policy signatures still open in Gusto*
>
> Quick reminder — a few policies are still waiting on signatures. Log into Gusto, open Documents, and sign anything showing as needing your signature. Takes about a minute.
>
> *{Policy name}* (sent {Month D}) — {First Last, First Last}
> *{Policy name}* (sent {Month D}) — {First Last}
>
> Questions on any of these → your Store Manager or Preston.

Sort oldest-sent first. Real first + last names, alphabetical. If a policy in the list is a known duplicate still showing twice in Gusto, add one plain line under it: _may appear twice in your documents — same one-pager, sign both._

If LIST A is empty after filtering, post nothing — DM Joshua that everyone is current.

## Step 3 — DM Joshua (`D03BHQH5VGT`)

Always send. Plain and short, in this order:

1. **Any NEW duplicate group (LIST C)** — lead with it. Both ids, both titles, created dates, sign counts. Say plainly that the same policy is live twice and ask which is the record copy. Note that Gusto has no delete or archive available here, so retiring one is a manual click in the UI.
2. **Any NEW never-sent template (LIST B)** — name it, when it was created, and that nobody has received it. Offer to finish sending it.
3. **One-line summary** — how many people and how many policies are outstanding, and whether that moved versus last week.

Never send LIST B or LIST C to a team channel, a store manager, or Preston — those are internal process gaps, not employee reminders.

## Step 4 — Verify before claiming done

Re-read the channel and confirm the post actually landed, and that the DM sent. A tool call returning OK is not proof. Never report success you haven't seen.

## Guardrails

- Never enter a password, complete a passkey, or bypass a login prompt.
- Never name a terminated employee, Joshua, or Hillary.
- This task is READ-ONLY in Gusto. Never create, send, edit or retire a document from here — that is always a separate, deliberate action.
- If one template's `/requests` call fails, skip it, note it in the DM, carry on — do not abort the run.