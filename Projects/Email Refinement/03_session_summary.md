# Email Refinement — Session Summary (2026-05-28)

## What shipped

### 1. Call + Text click tracking — LIVE
Every per-store Call and Text button in the VP Master Template now produces measurable click data in Brevo. The north-star metric (Calls + Texts per 1,000 recipients) finally has data behind it as of the next send.

- WPCode Lite snippet (ID 566) on thevalleypawn.com handles 10 redirects: `/c/<store>` → `tel:+1...` and `/t/<store>` → `sms:+1...`, all 302.
- VP Master Template (Brevo ID 11) updated: 10 substitutions made (5 `tel:` → `/c/<store>?utm_content=store_<name>_call`, 5 `sms:` → `/t/<store>?utm_content=store_<name>_text`). Zero residual unmeasurable links.

### 2. Phase 2 segmentation — proven, ready to expand
- Pattern confirmed in Brevo UI: "Link clicked in an email" filter, "Link URL contains" operator, with the new URL conventions.
- Proof segment built: **Prefers Roanoke** (segment ID 2) — currently 3 contacts.
- Runbook for the remaining 11 segments documented in `brevo-context.md`. Built on-demand as themed campaigns arise (so Joshua doesn't waste time building near-empty segments that don't have a use case yet).

### 3. Documentation
- `brevo-context` SKILL extended with: redirect URL table, snippet pointer, segmentation runbook, list-count gotcha, working API endpoints.
- Three docs saved to this folder for review: redirect spec, Phase 2 plan, this summary.

## A finding worth sitting with

Of 11,161 contacts on the master list, **only 95 have clicked any email link in the last 6 months**. That's a ~0.85% engaged rate. The infrastructure we just shipped makes Phase 2 segmentation possible — but the bigger lever is probably re-engaging or culling the silent 99%. Worth a future session: a reactivation sequence to wake people up (or move them off the list to improve sender reputation, which compounds future deliverability).

## Verification (three-layer chain)

1. **HTTPS layer:** `curl -sI https://thevalleypawn.com/c/<store>` returns `HTTP/2 302` and `location: tel:+1...` for all 10 URLs. Verified.
2. **Brevo template layer:** API re-fetch of template ID 11 shows 0 residual `tel:`/`sms:` hrefs and 10 new tracked URLs. Verified.
3. **Brevo segmentation layer:** new segment filtering on `store_roanoke_` returns real contacts from prior Maps-link clicks, confirming the URL field is indexed and queryable. Verified.

The one manual check left is opening an existing email with the new template on an iPhone and tapping a Call button — should open the dialer with the number filled. 10 seconds to test, doesn't require a new send.

## What changes for the next campaign

When you (or the weekly-campaign skill) send the next email from VP Master Template:
- Brevo's campaign report will show per-link clicks tagged by `utm_content=store_<name>_call` / `_text` / `_map` / `primary_cta` etc.
- The "Friday 9am" analytics post in `#email-campiagns` can now report the north-star metric for the first time.
- For sends with a defined audience (Culpeper-only, gold-themed, etc.), target the relevant segment instead of all 11K.

## Open work (not done this session)

- Build the remaining 11 segments (4 store + 6 topic + 1 engagement baseline) — runbook documented; build per-campaign-need
- Brevo Python helper for `duplicate_template(id=11, replacements={...})` to skip the manual find-and-replace step in the campaign workflow
- The Slack photo pipeline (you parked it last; still parked)
- Reactivation campaign for the dormant ~9,500-of-11,161 (open question — worth designing if you want to chase that lever)
