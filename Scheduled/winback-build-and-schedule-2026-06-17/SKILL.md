---
name: winback-build-and-schedule-2026-06-17
description: One-shot: build & schedule the 3-email dormant win-back sequence via Brevo API to segment 6, and retarget upcoming weekly drafts to the Engaged segment 5.
---

You are executing a one-time email build for Valley Pawn (Full Circle Finance Inc). This was set up interactively by Joshua, who approved fully-autonomous execution including scheduling live customer sends. Read `valley-pawn-context` and `brevo-context` first (skim — brand voice, CTA rules, VP Master Template ID 11, API key location).

FAILURE POLICY: If anything fails irrecoverably, do NOT post to Slack. DM Joshua (zapvp1@me.com) on Slack with a clear short failure summary and what state things are in. Only report success once the work genuinely completed.

== BREVO API ==
- Base: https://api.brevo.com/v3
- API key file: ~/.config/valley-pawn/brevo_api_key (mode 600)
- Helper available: ~/Documents/Claude/Scheduled/_shared/brevo_helper.py (use it where convenient; raw API calls are fine too)
- Segments already created (verified 2026-06-16): Engaged = segment ID 5 ("Engaged - 90d (clicked)", ~115 contacts); Dormant = segment ID 6 ("Dormant - no click 90d (subscribed)", ~9,515 contacts).
- Master template: VP Master Template = template ID 11 (GET /smtp/templates/11 → htmlContent with [[MARKER]] tokens).

== PART A — BUILD & SCHEDULE THE 3-EMAIL WIN-BACK SEQUENCE (target: Dormant segment ID 6) ==
1. Read the exact copy (subjects, preheaders, and the 10 marker values per email) from this file:
   /Users/joshuadavis/Documents/Claude/Projects/Gold and Silver Markeitng/winback-sequence-drafts.md
   It contains EMAIL 1 (Day 0), EMAIL 2 (Day 7), EMAIL 3 (Day 14), each with a marker table + subject + preheader + a BODY_HTML block.
2. For EACH of the 3 emails: GET /smtp/templates/11, take its htmlContent, and find-and-replace all markers ([[CAMPAIGN_SLUG]], [[HERO_EYEBROW]], [[HERO_HEADLINE]], [[HERO_SUBLINE]], [[BODY_HTML]], [[PRIMARY_CTA_LABEL]], [[PRIMARY_CTA_URL]], [[PRIMARY_CTA_SUB]], [[SUBJECT_FALLBACK]]) with that email's values from the file. Primary CTA URL for all 3 is exactly https://thevalleypawn.com/keep-in-touch (this page is LIVE — verified 2026-06-16). Leave all LOCKED blocks (logo, trust strip, 5-store directory, hours, footer) untouched.
3. Create 3 email campaigns via POST /emailCampaigns. For sender/from-name/reply-to, copy them from the most recent SENT weekly campaign (list_email_campaigns status=sent, newest) so they match what customers already see. Set:
   - recipients: segment ID 6 (Dormant). Use the recipients.segmentIds field.
   - subject + the filled htmlContent + campaign name (use the CAMPAIGN_SLUG, e.g. "Win-back 01 — Miss You — 2026-06-22").
   - scheduledAt (America/New_York, EDT = -04:00):
       Email 1 -> 2026-06-22T10:00:00-04:00
       Email 2 -> 2026-06-29T10:00:00-04:00
       Email 3 -> 2026-07-06T10:00:00-04:00
   Schedule each (status should become "queued"). Verify by GETting each campaign back and confirming status=queued and recipient segment = 6.
4. If a marker is missing or the template fetch fails, STOP and DM Joshua — do not send a malformed campaign to ~9,515 people.

== PART B — RETARGET THE WEEKLY NEWSLETTER TO THE ENGAGED SEGMENT (segment ID 5) ==
Goal: future weekly "Deal of the Week"/themed sends go to the Engaged segment instead of the full list, per the new strategy.
1. GET /emailCampaigns?status=draft&limit=50. Identify the pre-staged WEEKLY themed campaign drafts (names like "W#… — … — Month DD, YYYY"; the Deal-of-the-Week series). Do NOT touch the monthly Gold & Silver campaign, and do NOT touch the 3 win-back campaigns you just made.
2. For each such WEEKLY DRAFT, PUT /emailCampaigns/{id} setting recipients to segment ID 5 (Engaged). Preserve everything else — only change recipients.
3. Do NOT modify any campaign already in "queued" or "sent" status — leave the imminent Thursday send exactly as-is. Only drafts.
   (The vp-deal-of-week-monday-pick task preserves a draft's existing recipients when it fills/schedules it, so setting the drafts to segment 5 makes future weeklies go to Engaged without changing that task.)
4. If there are zero weekly drafts, note that in the summary (nothing to retarget yet).

== PART C — VERIFY & REPORT ==
DM Joshua (zapvp1@me.com) on Slack with:
- Win-back: confirm 3 campaigns queued, each to Dormant segment 6 (~9,515), with send dates + Brevo preview links (https://my.brevo.com/camp/edit/{id}/email-template).
- Weekly retarget: list the weekly draft campaign(s) now pointed at Engaged segment 5, or "no weekly drafts found yet."
- One line: "Win-back live + weekly retargeted to Engaged. Reply if you want any subject/copy tweaks before June 22."
Keep it concise. This is a customer-facing send going out June 22 — accuracy over speed.