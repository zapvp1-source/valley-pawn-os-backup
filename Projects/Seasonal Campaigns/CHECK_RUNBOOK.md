# Seasonal campaign check — runbook (2026-11-21)

Run this when asked to "run the seasonal campaign check", or from a scheduled task (intended cadence: Mon, Wed, Fri 6:20 AM ET, bound to the Mac Studio).
Load enterprise-map first. READ-ONLY toward customers: do not send, schedule, re-schedule, suspend or edit any email; no Slack, email, text or push. Only writes allowed: the log files below, and publishing a due sale page (2b).

Source of truth: `campaigns.json` in this folder. Standing offer: 15% off in store on the listed sale days, "Some exclusions apply", public, email to the full list.

1. Pick every campaign where today (America/New_York) is between 21 days before its email send date (or banner_from, whichever is earlier) and 8 days after its last sale day (message campaigns: banner_to). None in window: append "<date> nothing in window" to RUN_LOG.md and stop.
2. For each campaign, record PASS/FAIL:
   a. EMAIL (look only). Chrome: https://app.brevo.com/marketing-campaign/edit/<brevo_campaign>. Before send: status Scheduled, date/time equals campaigns.json, recipients >= 10,000, preview names the right sale days and "Some exclusions apply" (sale campaigns). After send: status Sent; record recipients, opens, clicks, unsubscribes. #70 is a weekly-chain draft, exempt until 3 days before its date. Never click Schedule, Send now, Suspend, Save or Duplicate.
   b. LANDING PAGE. From banner_from: https://thevalleypawn.com<landing> loads, shows the right sale days and "Some exclusions apply". If a page that should be live is unpublished, publish it (WordPress connector, page id in campaigns.json), content unchanged.
   c. HOMEPAGE BANNER. In the banner window: element id `vp-camp` visible on https://thevalleypawn.com/ and its headline names this campaign. Outside every window: hidden.
   d. SOCIAL / GOOGLE PROFILES. Sale week: newest plan in `Refine Social Media/state/plans/` and its `_results.json` show at least one post per store Facebook page and one per store Google profile naming the sale with the right dates. CAMPAIGN-BRIEFS block still in `Refine Social Media/CALENDAR_AUG_DEC_2026.md`.
   e. STORE FACTS. Hours, addresses, phones on the landing page match valley-pawn-context.
3. Eight days after the last sale day, write `results/<campaign id>.md` once: email numbers; whether page, banner and social ran; store sales for the two sale days vs the same weekdays one week earlier from `Bravo Data Extraction/output/` if present (else "sales data not available"). Never open Bravo or Parallels.
4. Append a dated block to RUN_LOG.md (one PASS/FAIL line per item). Any FAIL: one plain-language row in `Life OS/HUMAN_QUEUE.md` (campaign, what is wrong, date it matters by), unless already listed.
