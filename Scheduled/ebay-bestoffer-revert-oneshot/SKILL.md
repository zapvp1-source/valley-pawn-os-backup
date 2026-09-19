---
name: ebay-bestoffer-revert-oneshot
description: ONE-SHOT (retry): switch Best Offer back OFF on the ~193 Culpeper listings our own August remediation turned it on for. Joshua approved. Deletes itself when done.
---

ONE-TIME TASK. Run once, then delete yourself. Do not reschedule.

## Prior attempt — 2026-09-17 16:15 ET (READ THIS FIRST)

That run did NOT execute. Nothing on eBay was changed, in either direction, so the job below is
still entirely outstanding and still safe to run exactly as written. It failed at the local-access
gate: `mcp__Control_your_Mac__osascript` was genuinely absent from the session (ToolSearch returned
"No matching deferred tools found" on two separate calls — absent, not merely unloaded). Re-checked
2026-09-18 in a live session: still absent, so this is an app-wide connector gap, not a
scheduled-run quirk. That run also ruled out the Linux workspace sandbox as a fallback on facts:
the sandbox does reach api.ebay.com and has python3, but the script sources credentials from
`~/ebay_weekly_rankings.py` and prior-value state from `~/ebay_policy_fix_state.json`, both in the
Mac home directory outside the mounted `~/Documents/Claude/Projects` folder, with no copy anywhere
in the mount. Do not re-derive any of that — it is settled. A FAILURE_LEDGER row is already open.

## Why

On 2026-08-22 an audit recommended "Turn Best Offer on for 193 Culpeper listings" and
`ebay_policy_fix.py --apply --only BESTOFFER` did exactly that. On 2026-09-17 Joshua reversed
that policy after store feedback:

  "Stop changing listings that are marked as no offers allowed to offers allowed.
   We do not want make an offer on video games at all."

A listing with Best Offer off is a deliberate store decision. We are the reason these 193 are
on, so we put them back. Joshua explicitly approved this reversal. The forward path that
enabled them has already been removed from the codebase — this only undoes what we did.

## Steps

**0. LOCAL ACCESS GATE.** If `mcp__Control_your_Mac__osascript` is not loaded, load it via
ToolSearch `select:mcp__Control_your_Mac__osascript`, then probe with `do shell script "echo READY"`.
If the tool loads but the probe errors, wait 30 s and retry for up to 12 minutes — that is transient
and the run has local access. BUT if ToolSearch itself answers "No matching deferred tools found"
on two separate calls, the tool is absent from this session entirely and no amount of waiting will
produce it — do NOT poll for 12 minutes. Go straight to step 6, write the FAILURE_LEDGER row,
re-arm this task for the next morning, and stop. All other filesystem I/O goes through osascript
`do shell script`. The wrapper kills any single call at ~25 s, so never sleep longer than ~18 s in
one call and poll across separate calls for the longer eBay passes.

**1. DRY RUN FIRST — mandatory, do not skip.**
```
/usr/bin/python3 "$HOME/Documents/Claude/Projects/eBay/ebay_policy_fix.py" --revert --only BESTOFFER
```
Without `--apply` this only prints what it would change. Capture the count.

**2. Sanity-check the dry run before writing anything.** Proceed to step 3 ONLY if all of these hold:
   - every line printed says `WOULD REVERT` and the fix column reads `BESTOFFER`
   - **not a single line mentions `RET30` or `RETON`** — those are the returns-policy fixes and
     they must be KEPT; reverting them would put listings back on 14-day or no returns and damage
     Top Rated Seller standing
   - the count is plausible: somewhere between 1 and 200
   If any check fails, STOP, change nothing, and write one FAILURE_LEDGER row (see step 6) saying
   the dry run did not look right and what it showed. Do not improvise a fix.

**3. Apply.**
```
/usr/bin/python3 "$HOME/Documents/Claude/Projects/eBay/ebay_policy_fix.py" --revert --only BESTOFFER --apply
```
It paces itself (~0.35 s/item) and saves state after each one, so it is safe to resume if it
stops early. Items that have since sold or ended are skipped automatically. Expect this to take
a couple of minutes. If it stops on an eBay usage limit, that is handled — just note where it got to.

**4. VERIFY AGAINST LIVE OUTPUT (Rule 12 — do not skip and do not trust the script's own count).**
Pick 3 item IDs the script reported as reverted and pull each fresh via the Trading API `GetItem`
(credentials pattern: the STORES / APP_ID / DEV_ID / CERT_ID names from `~/.vp_secrets/`, POST to
`https://api.ebay.com/ws/api.dll` with header `X-EBAY-API-IAF-TOKEN`). Confirm
`BestOfferDetails/BestOfferEnabled` now reads `false`. Also confirm on those same 3 that
`ReturnPolicy/ReturnsWithinOption` still reads `Days_30` — i.e. the returns fixes survived.
If any spot-check fails, say so plainly in the report rather than claiming success.

**5. Report — ONE Slack message to #ebay-performance (`C0ANVN5KX4Y`).** Plain language, no script
names, no API names, no file paths. Something like:

> Best Offer has been switched back off on the Culpeper listings where we'd turned it on back in
> August — about <N> of them. Going forward, whether an item takes offers is the store's call, and
> we don't put offers on video games at all. Return policies were not changed.

Then DM Sandi (Culpeper, `U04C5DL5EKH`) the same thing in one or two friendly sentences, since
they are her store's listings.

**6. On any failure** — do NOT DM Joshua and do not message anyone. Append ONE row to
`/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md`:
`| <YYYY-MM-DD HH:MM ET> | ebay-bestoffer-revert-oneshot | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |`
then re-arm this task for ~09:30 ET the following morning so it retries itself, and stop. Do NOT
delete the task on a failure — step 8 is success-only. If the re-arm is auto-declined because no
approver is available, say so plainly in the ledger row and flag NEEDS_HUMAN: yes.

**7. Log it.** Append a dated line to `Projects/Valley Pawn OS/CHANGELOG.md` recording the count
reverted and the spot-check result, and close out the related row in
`Projects/Life OS/OPEN_ITEMS_REGISTER.md` (2026-09-17, eBay / Policy) noting the Best Offer
sub-item is done — leave the rest of that row open, the policy re-issue is separate. Also close
the open FAILURE_LEDGER rows from the 2026-09-17 attempt.

**8. Delete this task.** Call `mcp__scheduled-tasks__delete_scheduled_task` with taskId
`ebay-bestoffer-revert-oneshot`. It exists only for this one run. Success only.

## Guardrails
- Touch ONLY Best Offer. Never a price, a title, a photo, a category, a quantity, or a return policy.
- Never `exec()` or run any other `~/ebay_*.py` script "to check" something — they perform live
  writes at module level. Read them or `py_compile` them.
- If `--only BESTOFFER` is rejected or the script refuses to run, that is the safety guard doing
  its job. Do not work around it, do not edit the script, do not run a blanket `--revert`. Write
  the FAILURE_LEDGER row and stop.