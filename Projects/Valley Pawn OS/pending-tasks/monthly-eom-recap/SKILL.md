---
name: monthly-eom-recap
description: 1st of month 10:30 AM — posts a "Month in Review" summary of the prior month into each analytics and marketing Slack channel that has no dedicated monthly report, built only from that channel's own verified weekly/daily posts (Slack connector only; no Bravo, no external systems). Created 2026-09-05 per Joshua — every analytics + marketing channel gets an EOM summary.
model: claude-sonnet-5
cron: 30 10 1 * *
---

<!-- NOT YET REGISTERED. Creating this task from an autonomous session was blocked by the app's
     permission classifier on 2026-09-05 (a scheduled task that posts to team channels needs Joshua's
     approval). To register: in a Cowork chat say "create the monthly-eom-recap scheduled task from
     Valley Pawn OS/pending-tasks/monthly-eom-recap/SKILL.md, cron 30 10 1 * *" and approve the prompt. -->

You publish the prior month's "Month in Review" into each Valley Pawn analytics and marketing Slack channel that does not already have its own dedicated monthly report. Source of truth is ONLY what was already posted in that channel during the month (the weekly/daily automated posts, which were verified when they posted). No Bravo, no external systems, no estimates.

CONTEXT LOAD: invoke the `enterprise-map` skill first (osascript fallback if the Projects folder is not mounted), then `vp-operating-rules` and `valley-pawn-context`. Read `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/PUBLICATION_CALENDAR.md` (the canonical channel list and exclusions) and `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`.

TARGET MONTH: the prior calendar month (run date is the 1st). Compute the month's start/end Unix timestamps in ET.

CHANNELS (from PUBLICATION_CALENDAR.md "Month in Review — channels covered"):
Analytics — #loan-review C0B08RS2BMK · #layaway-review C04N24STDP1 · #aged-inventory-review C04NGH4FF35 · #first-payment-default C0B17894S2Y · #timekeeping-summary C0AN6TNA4ES · #weekly-returns-summary C0B1K4WK2HZ · #daily-funds-reconcilation C0B3R9B3S8H · #pawn-walks C0B8WR95N31 · #google-reviews C04NDE52U2G
Marketing — #social-media C0BMRC2LN3D · #email-campiagns C0APR5WUL2Z · #website C0ASE9C0GQ0 · #ai-marketing C0BCEESUANM · #ebay-performance C0ANVN5KX4Y · #blog-posts C0APY6TE604
NEVER post a monthly recap to #store-performance (Joshua, 2026-09-05: weekly only there), nor to any channel with its own monthly producer (#company-performance, #employee-performance, #scrap-rankings, #ffl-transfer-performance, #new-customers, #bonus-goals, #monthly-gun-audit).

FOR EACH CHANNEL:
1. Duplicate guard: read the channel's last 30 messages; if a post containing "Month in Review" and the target month name already exists, skip the channel.
2. Read the channel history for the target month (paginate; include bot/webhook messages such as the eBay webhook posts). Collect the automated report posts (weekly summaries, daily posts). Ignore chit-chat and join messages.
3. Completeness gate (Rule 18): a weekly-cadence channel needs at least 3 of the month's weekly posts; a daily-cadence channel needs at least 60% of its expected days. If the gate fails, post nothing to that channel and record it in the run log — never post a recap built on gaps and never caveat a gap in a team channel.
4. Build the recap from the numbers in those posts. Month totals only where the underlying figures are additive (returns count/$; reviews received; posts published; new 5-star reviews; funds verified; overpay flags; blog posts published); otherwise report the month's trajectory (first vs last weekly figure, best/worst week, which store led/lagged most often). If the prior month's "Month in Review" exists in the channel, add a one-line month-over-month comparison.
5. Post in this shape (plain everyday language, no system/tool/report/file names, no "pulled automatically", no signature footer):
📅 *{Month} {Year} — Month in Review*
{2–4 sentences: what happened this month, who led, what moved, what to watch}
{compact bullet list of the month's key figures — max 8 lines}
Field-facing channels (all analytics channels except #timekeeping-summary and #daily-funds-reconcilation; plus #google-reviews) must read like a manager wrote it. Leadership-only channels (#timekeeping-summary, #daily-funds-reconcilation, #email-campiagns, #ai-marketing, #website, #social-media, #ebay-performance, #blog-posts) may carry a little more detail.
6. Move to the next channel. Post at most one message per channel.

FINISH: write `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Month in Review.md` via osascript heredoc listing, per channel: posted (permalink) / skipped-duplicate / skipped-gate (with the count found). Add one dated line under a `## {today}` heading at the top of `Valley Pawn OS/CHANGELOG.md`: "monthly-eom-recap: {n} channels posted, {m} skipped". No DM to Joshua on success. If the Slack connector is unavailable for the whole run, send ONE plain-language DM to Joshua (D03BHQH5VGT): "The month-in-review posts for {Month} didn't go out — will retry." and stop.

Hard rules: Slack connector only (read + post); all file I/O via osascript; never post partial or estimated numbers; never name systems/tools/files in a channel; never post to #store-performance; one post per channel per month.
