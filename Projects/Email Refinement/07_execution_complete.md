# Reactivation Program — Execution Complete

**Status:** Every structural piece is built. Three reactivation campaigns sit as drafts in Brevo, addressed to the right audience, ready to send.

## What's now in place (verified via API)

### Brevo segments
| ID | Name | Filter | Size |
|---|---|---|---|
| 2 | Prefers Roanoke (clicked store link in last 6mo) | Link URL contains `store_roanoke_`, 6mo | 3 |
| 3 | Engaged — clicked any link in last 6mo | Any link clicked, 1+ time, 6mo | **95** |
| 4 | Dormant — no click 6mo (subscribed) | Link clicked < 1 time AND subscribed | **9,600** |

### Reactivation campaign drafts
| Brevo Campaign ID | Subject | Target | When to send |
|---|---|---|---|
| 16 | Still want us in your inbox? | List 3 + Dormant segment | Day 0 |
| 17 | Should we still be reaching out? | List 3 + Dormant segment | Day +7 |
| 18 | Goodbye? Or one more chance? | List 3 + Dormant segment | Day +14 |

Each draft passes verification:
- Zero residual `[[MARKER]]` placeholders
- 10 store-redirect URLs each (calls + texts trackable)
- 2 references to `/keep-in-touch` CTA per email
- Sender: Valley Pawn / jdavis@fcfpawn.com
- Type: classic, status: draft

### Pages on thevalleypawn.com
- `/keep-in-touch` — live (page ID 569), confirmation page for clickers
- `/c/<store>` and `/t/<store>` — live (WPCode snippet 566), 302 redirects to `tel:` and `sms:`

### Suppression sweep script
- Saved to `/Email Refinement/sweep_dormant_to_sunset.py`
- Runs after Email 3 sends + 3 days of click-window
- Reads Brevo API key from `~/.config/valley-pawn/brevo_api_key`
- `--dry-run` flag for preview
- Requires you to create a "Dormant — Sunset" list in Brevo UI first and paste its ID into the script

## What's left for you

**One decision, three button clicks:**

1. **Decide when to send Email 1.** Recommend a Wed or Thu next week (e.g., Wed June 3, 2026). Tuesday-Thursday between 10am and 2pm Eastern is the highest-engagement window for retail email.

2. **In Brevo: open campaign 16 → click "Schedule" → pick that date/time → Schedule.** Brevo sends it automatically.

3. **One week later, schedule campaign 17.** Same flow.

4. **One week after that, schedule campaign 18.** Same flow.

5. **Three days after Email 3 sends:**
   - In Brevo, create a new list called `Dormant — Sunset` (no contacts in it yet)
   - Copy the new list's ID
   - Edit `sweep_dormant_to_sunset.py`, set `SUNSET_LIST_ID = <that-id>`
   - Run `python3 sweep_dormant_to_sunset.py --dry-run` to preview
   - Run `python3 sweep_dormant_to_sunset.py` to execute
   - About 7,500–9,000 contacts move out of regular sends

## What changes after the sweep

- The weekly newsletter targets the **Engaged segment (ID 3)** as the new default audience (currently 95, but will grow as the reactivation Email 1 click-confirmations land)
- Click rate on subsequent sends mechanically rises from ~2.9% → ~12–20%
- Complaint rate drops (you've stopped emailing people who don't want to hear from you)
- Send cost drops on the per-recipient pricing (~85% fewer recipients per send)
- Gmail/Yahoo/Apple sender reputation improves over 30–60 days, lifting inbox placement

## Files in /Email Refinement/

- `01_redirect_spec.md` — WP redirect spec
- `02_phase2_segmentation_plan.md` — original (superseded) Phase 2 design
- `03_session_summary.md` — first-half wrap
- `04_dormant_list_audit.md` — engagement audit
- `05_reactivation_emails_drafts.md` — copy drafts (now staged in Brevo)
- `06_session_wrap.md` — second-half wrap
- `07_execution_complete.md` — this file
- `sweep_dormant_to_sunset.py` — suppression script

## brevo-context skill is now 384 lines

Future sessions inherit the full operating manual: redirect URLs, segmentation runbook, sunset policy, sender details, working API endpoints.
