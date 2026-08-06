# policy-lifecycle — DELTA patch 2026-08-05

**Apply in Settings → Capabilities → `policy-lifecycle` skill.** Skills cannot be edited from a session.

**Why this patch exists.** On 2026-08-05 an audit of Gusto found two policies that had been
announced to the whole team in Slack but were sitting in Gusto **unsent, with zero recipients**:

| Policy | Announced in Slack | Gusto state found | Recipients |
|---|---|---|---|
| eBay Listing-Age Standard (Reprice & Pull) | 2026-07-04 — *"the formal one-page policy is being sent to each of you in Gusto"* | `mapping_complete` | 0 |
| Gold Scrap Bucket Naming Standard | 2026-08-04 | `prepared` | 0 |

Both were told to staff as done. Neither was. The eBay one sat that way for **31 days**. Two more
templates (`ROC - Late to work`, a duplicate `Overtime Policy`) are also stuck at `prepared`.

The skill's existing verification block is correct but is written as advice at the *end* of
Step 3. Both of these got past it. The failure mode is that Step 2 (announce to Slack) can
complete while Step 3 (send in Gusto) silently does not — and nothing reconciles the two.

---

## CHANGE 1 — Reorder Step 2 and Step 3

Replace the current ordering so that **Gusto distribution happens BEFORE the Slack announcement.**

> ## Step 2 — Distribute for e-signature via Gusto
> ## Step 3 — Publish to the teams (Slack + Drive)

Rationale: the Slack post makes a promise to employees ("you'll receive this in Gusto"). Never
make that promise before the thing is verifiably true. If Gusto is down or the session is logged
out, the correct outcome is *no Slack post yet* — not a promise that quietly goes unkept.

## CHANGE 2 — Add a hard gate between them

Insert immediately before the (newly renumbered) Slack publish step:

> ### ⛔ SEND GATE — do not proceed to the Slack announcement until this passes
>
> ```js
> const t=await (await fetch('/api/document_templates/<ID>',{headers:{Accept:'application/json'},credentials:'include'})).json();
> const q=await (await fetch('/api/document_templates/<ID>/requests',{headers:{Accept:'application/json'},credentials:'include'})).json();
> JSON.stringify({state:t.processing_state, approved_at:t.approved_at,
>                 count:(q||[]).length, statuses:[...new Set((q||[]).map(r=>r.status))]});
> ```
>
> **All four must be true for a Team document:**
> 1. `processing_state === "approved"`
> 2. `approved_at` is non-null
> 3. `count` equals the active roster count from `list_employees` with `terminated: false`
> 4. every entry in `statuses` is `"requested"`
>
> `processing_state` of `prepared` or `mapping_complete` means **it was never sent.** That is a
> failure, not a partial success. Do not post to Slack. Do not update the manual. Do not mark
> anything done. Send ONE plain DM to Joshua (`D03BHQH5VGT`) saying the policy is drafted but not
> yet distributed, and stop.
>
> For an Individual document, `requests` is `[]` — that is expected. Instead confirm the doc is
> listed as **"Needs signing"** on `/payroll_admin/people/<uuid>/documents`.

## CHANGE 2b — Add a DUPLICATE GUARD before creating any template

Insert at the very top of the (newly renumbered) Gusto distribution step, **before** uploading
anything:

> ### ⛔ DUPLICATE GUARD — run this BEFORE creating or uploading a new template
>
> On 2026-08-05 the same policy was created twice, 17 minutes apart, by two different actors
> that could not see each other's work — and both were sent. All 14 employees were asked to sign
> the identical one-pager twice. Nothing in the flow noticed.
>
> ```js
> const C='15bc2823-564f-4c1a-8464-9b0e7d79d3e8';
> const t=await (await fetch(`/api/companies/${C}/document_templates`,{headers:{Accept:'application/json'},credentials:'include'})).json();
> const norm=s=>s.toLowerCase()
>   .replace(/\(.*?\)/g,' ')
>   .replace(/[^a-z0-9 ]/g,' ')
>   .replace(/\b(policy|policies|guideline|guidelines|standard|standards|procedure|update|effective|revised|final|draft|the|a|and|of|for|v\d+)\b/g,' ')
>   .replace(/\s+/g,' ').trim();
> const target=norm('<the policy title you are about to create>');
> t.filter(x=>norm(x.document_name)===target || norm(x.document_name).includes(target) || target.includes(norm(x.document_name)))
>  .map(x=>[x.id,x.document_name,x.processing_state,(x.created_at||'').slice(0,10)]);
> ```
>
> **If that returns anything, STOP.** Do not create a second template. Either finish sending the
> existing one, or DM Joshua (`D03BHQH5VGT`) naming both and let him choose which is the record
> copy. Two live templates for one policy is a defective HR record — you cannot later prove which
> version an employee actually agreed to.
>
> Normalisation deliberately strips parenthetical suffixes, version tags, and filler words, so
> *"Gold Scrap Bucket Naming"* and *"Gold Scrap Bucket Naming Standard (Effective 2026-08-01)"*
> collide as intended. A false positive costs one DM. A false negative costs a duplicate sent to
> the whole company, and Gusto has no delete or archive available through the API — cleanup is
> manual, in the UI, forever.
>
> **Re-run this check immediately before pressing Send**, not only before upload. The 2026-08-05
> duplicate was created *during* another session's in-flight work; a check that runs only at the
> start of a long flow will miss it.

## CHANGE 3 — Add to the Guardrails section

> - **Never announce a policy in Slack before the Gusto send gate has passed.** Telling staff a
>   document is coming when it isn't destroys the credibility of every future announcement, and
>   creates an HR record showing the company said it distributed a policy it did not distribute.
> - **`prepared` and `mapping_complete` are not "sent."** Only `approved` with a request count
>   matching the active roster means the team actually received it.

## CHANGE 4 — Note the recurring backstop

Add under Step 6 (Close out):

> The `vp-gusto-signature-chase` scheduled task (Mondays 8:49 AM) independently re-checks every
> Gusto template and DMs Joshua about any that are created but never sent. That is a safety net,
> not a substitute for the send gate — a policy caught by it has already been unsent for up to a
> week.

---

## Also worth doing (not a skill change)

Four templates are currently stuck and should be resolved or deleted so they stop showing up as
findings every week:

- `7455446` — ROC - Late to work (`prepared`, created 2026-05-18). This is a disciplinary
  template; if it was a one-off for a specific person it should be an **Individual** document,
  never a Team document.
- `6984265` — Overtime Policy (`prepared`, created 2026-02-28) — duplicate; `6984272` of the same
  name is `approved` with 11 signed. Almost certainly a stray draft to delete.
