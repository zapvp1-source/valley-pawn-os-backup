# Monthly Policy Update ("Policy Day") — the only way policies reach employees

Set by Joshua 2026-10-21: "we don't want to continuously blast them with updates, we need a cadence like monthly where they can sign one ack for all new policies and guidelines" · "policy day should include ALL new policies not just compliance policies" · "we need to coordinate all new policy and procedure updates and acknowledgments to the field once a month, not sporadically."

## The rule
- **Scope: EVERY new or changed staff-facing policy, procedure, guideline, standard, script, form instruction, manual revision or policy reminder — every department** (operations, loans, eBay, firearms, HR and pay, customer service, culture, compliance, training). Not just compliance.
- **Nothing goes to staff the day it is approved.** It is added to `POLICY_QUEUE.md` (status `approved`) and waits for the next Policy Day. This binds every session, skill and scheduled task — policy-lifecycle, the compliance programs, the Preston assistant, HR, marketing, eBay, Academy.
- **Policy Day = the first business day of each month.** Each employee gets ONE Gusto document (the Monthly Policy Update) and signs ONCE.
- **One #policy-announcements post** on Policy Day — the same plain summary as page 1. No other policy posts or "reminder" posts during the month; reminders of existing rules ride in the next update's "What's new" list.
- **Manuals** (Handbook, P&P) are revised in place as items are approved, but a new version is published only on Policy Day — at most one version bump a month. When a version changes, the update names it as NEW and that one signature is the Handbook & P&P acknowledgment for that version.

## How it is delivered (Joshua 2026-10-21: "we dont need docusign if we have fixed the login, we can upload directly to gusto")
- **Signatures: Gusto.** The update PDF (`build_bundle.py`) goes up as ONE Gusto **Team document** with signature — current team members AND all future hires — using the proven `gusto-access` / policy-lifecycle Step 3 upload method. Everything lives in each employee's Gusto file next to the manuals and every earlier signature.
- **Gusto sign-in is automatic:** Gusto is linked to Google sign-in (jdavis@fcfpawn.com). If Gusto has signed out, the runner clicks "Sign in with Google" — never a password or a code. If Gusto asks for a code, one line goes on Life OS/HUMAN_QUEUE.md and the send waits for the next run.
- **Status:** read from Gusto itself (`/api/document_templates/<id>/requests` in the signed-in tab). Unsigned names go to Preston on the 15th.
- **Manuals:** a new Handbook / P&P version goes up the same day as view-only Team documents; the update's last page is the Handbook & P&P acknowledgment (HR-2026-04 Rev2 or its successor) whenever a version changes.
- **New hires** inherit the current update automatically (Team document "future hires").
- DocuSign is no longer used for Policy Day. (`docusign/` is kept as an archived fallback only.)

## Calendar (every month)
| When | What | Who |
|---|---|---|
| All month | Approved items land in `POLICY_QUEUE.md`; manuals revised in place (not published) | Claude (any session) |
| 25th | Cutoff. Anything approved after this waits a month | — |
| 26th (or next run) | Sweep every source, build next month's manifest + the update PDF; email Joshua ONE preview with the PDF (what's in, what's held and why, the Slack post text, the Preston follow-up text) | Policy Day runner |
| Before Policy Day | Joshua replies **approve** (or edits). One approval covers: the Gusto send to staff, the one #policy-announcements post, the Academy edits, and the 15th unsigned list to Preston | Joshua |
| Policy Day (1st business day), 8:40 AM | One Gusto Team document to every employee + future hires; one #policy-announcements post; manuals published (Gusto view-only + store binder) | Policy Day runner |
| Mondays | Signature status read from Gusto; Gusto's own reminder sent to anyone unsigned | Policy Day runner |
| 10th (next business day if weekend) | Signatures due | Employees |
| 15th (next business day if weekend) | Names still unsigned, by store, go to Preston in #preston-claude | Policy Day runner |
| End of month | Packet closed: signed / unsigned count recorded; compliance calendar row updated | Policy Day runner |
| Empty queue | Nothing is sent that month; Joshua gets one line saying so | Policy Day runner |
| No "approve" by Policy Day | Nothing is sent. Runner waits up to the 7th, then rolls the items to next month and tells Joshua once | Policy Day runner |

## Exceptions (go out the same day, then fold into the next update)
A change that cannot wait: a law or court order taking effect before the next Policy Day (e.g. the assault-firearm injunction lifting), a safety or security incident, or a regulator's instruction. Preston tells the stores directly that day; the written policy rides in the next update for signature.

## Acknowledgments vs. Records of Warning (Joshua 2026-10-21: "whether Preston asks or I do, all acks need to have a monthly cadence unless it's a record of warning")
- **Every acknowledgment rides Policy Day** — one person or the whole team, a policy, a manual or a standard, no matter who asks (Joshua, Preston, any session or scheduled task). It becomes a POLICY_QUEUE.md row (with the person's name if it's for one person) and is signed in that month's update.
- **On demand, same day:** Records of Warning (ROW) only — plus Action Plans (30/60/90, PIP), which are individual performance documents, not acknowledgments. Both go out as Gusto Individual documents.
- Retired for on-demand use: the HR E-Sign Playbook's ACK form, its "one envelope per person for a team rollout" line, and its full Handbook/P&P ack (section 9). The weekly Gusto signature chase tasks stay off — the Policy Day runner owns reminders.

## New hires
Onboarding gets the current Handbook + P&P + the current Monthly Policy Update automatically (Gusto Team documents include "future hires") and the Academy — never back issues.

## Academy coupling
Every item in an update is checked against the Valley Pawn Academy lessons the same cycle. If a lesson teaches the old rule, the lesson is fixed in the same month (text first; narration with the next voice run). Staff never get a signed rule that the Academy contradicts.

## Files
- `POLICY_QUEUE.md` — the queue (status draft → approved → update YYYY-MM → sent → closed; `held` = Joshua said wait)
- `manifests/<YYYY-MM>.json` — the update definition
- `out/<YYYY-MM>_Policy_Update.pdf` — printable proof copy (store binder)
- `state/<YYYY-MM>.json` (Gusto template id + status), `POLICY_DAY_RUNBOOK.md` (the runner's exact steps); `docusign/` = archived fallback
- `POLICY_DAY_PLAN_OF_ATTACK.md` — the roadmap of what goes out when
