---
name: vp-gusto-signature-chase-firstrun
description: [SUPERSEDED 2026-08-05 — ran manually same day, disabled to prevent a duplicate post] One-time first run of the Gusto policy e-signature chase.
model: sonnet
---

Valley Pawn (Full Circle Finance Inc) — Gusto policy e-signature chase. THIS IS THE ONE-TIME FIRST RUN. The recurring version (`vp-gusto-signature-chase`) takes over on Mondays at 9:05 AM. Behaviour is identical.

Read the `valley-pawn-context` and `vp-operating-rules` skills first for brand voice and the hard rules. Keep all Slack language plain per the Field Communication Standard: no tool names, no file paths, no technical jargon, no API talk. Employees should read it in one pass.

## ALWAYS EXCLUDED — never name these two anywhere in this task's output

- **Joshua Davis** — `2f2d61c5-f19e-4d8e-9e4c-d7d6b62f93d6`
- **Hillary Davis** — `94fa77de-beeb-4779-b669-4df93199bd05`

Filter both out by UUID (not by name — names change). They do not appear in the Slack post, they do not appear in the DM, and they are not counted in any total. Also exclude anyone with a non-null `terminated_at`.

## Step 1 — Pull the data from Gusto (no clicking, no screenshots)

Gusto's MCP connector does NOT expose documents. Use Chrome instead:

1. Open a tab to `https://app.gusto.com/payroll_admin/documents/shared/active`.
2. **If the URL lands on `login.gusto.com`, you are logged out.** Do NOT try to log in, and do NOT attempt a passkey or biometric prompt. Send ONE plain-language Slack DM to Joshua (`D03BHQH5VGT`) saying you couldn't get into Gusto this morning, then STOP. Never post a partial or empty list to a team channel.
3. Everything below is a same-origin `fetch` with `credentials:'include'` run from that logged-in tab via the `javascript_tool`. These are read-only endpoints. Company UUID is `15bc2823-564f-4c1a-8464-9b0e7d79d3e8`.

```js
const C='15bc2823-564f-4c1a-8464-9b0e7d79d3e8';
const SKIP=['2f2d61c5-f19e-4d8e-9e4c-d7d6b62f93d6','94fa77de-beeb-4779-b669-4df93199bd05'];
const emps=await (await fetch(`/api/companies/${C}/employees`,{headers:{Accept:'application/json'},credentials:'include'})).json();
const byUuid={}; emps.forEach(e=>byUuid[e.uuid]={n:(e.preferred_first_name||e.first_name)+' '+e.last_name, term:e.terminated_at});
const tmpls=await (await fetch(`/api/companies/${C}/document_templates`,{headers:{Accept:'application/json'},credentials:'include'})).json();
// per template: const rq=await (await fetch(`/api/document_templates/${id}/requests`,...)).json();
// rq[i] = {status:'completed'|'requested', target_id:<employee uuid>, signed_at}
```

**LIST A — open signatures.** Every template with `processing_state === 'approved'` and `statistics.unsigned_request_count > 0`; pull its `/requests`, collect everyone whose `status !== 'completed'`, resolve names via `byUuid`, then drop anyone in `SKIP` and anyone terminated.

> The raw `unsigned_request_count` is inflated — terminated employees keep open requests forever. Never quote it. Count only people who survive the filter.

**LIST B — created but never sent.** Every template whose `processing_state` is NOT `approved`. Zero recipients — the policy exists but nobody was asked to sign it.

Known and already accepted as of 2026-08-05, one line only if still unresolved: `7455446` (ROC - Late to work) and `6984265` (duplicate Overtime Policy). Anything NEW is the real signal.

## Step 2 — Post to Slack `#policy-announcements` (C03BHQ9RLR0)

Only if LIST A is non-empty after filtering. This is the first time the team is seeing this reminder, so open it warmly — one short line acknowledging that a couple of these went out a while back and it's on us as much as anyone. Then the list.

> *Policy signatures still open in Gusto*
>
> Quick housekeeping — a few policies are still waiting on signatures, including a couple that went out a while ago. Log into Gusto, open Documents, and sign anything showing as needing your signature. Takes about a minute.
>
> *{Policy name}* (sent {Month D}) — waiting on: {First Last, First Last}
> *{Policy name}* (sent {Month D}) — waiting on: {First Last}
>
> We'll post this as a standing reminder on Mondays until everything's clear. Questions → your Store Manager or Preston.

Sort oldest-sent first. Real first + last names.

If LIST A is empty after filtering, post nothing — DM Joshua that everyone is current.

## Step 3 — DM Joshua (`D03BHQH5VGT`)

Plain and short: anything NEW in LIST B first, then a one-line summary of how many people and how many policies are outstanding. Never send LIST B to a team channel, a store manager, or Preston.

## Step 4 — Verify before claiming done

Re-read the channel and confirm the post actually landed, and that the DM sent. A tool call returning OK is not proof.

## Guardrails

- Never enter a password, complete a passkey, or bypass a login prompt.
- Never name a terminated employee, Joshua, or Hillary.
- Read-only in Gusto. Never send a document from this task.
- If one template's `/requests` call fails, skip it, note it in the DM, carry on.