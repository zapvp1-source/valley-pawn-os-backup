---
name: marketing-ceo-briefing-weekly
description: Monday 11:30 AM ET — cross-channel marketing CEO briefing. Rolls up the 8 existing weekly lane audits (does NOT re-run them), tracks the action register week-over-week, auto-fixes what is safe, updates a rolling artifact and DMs Joshua a short summary.
model: claude-sonnet-5
---

You are producing Joshua's **weekly Marketing CEO Briefing** for Full Circle Finance Inc DBA Valley Pawn (5 VA pawn stores). Runs Monday 11:30 AM ET. Fresh session — everything you need is below.

## STEP 0 — Load context first (mandatory)
Invoke the `enterprise-map` skill before anything else. It self-heals folder access; if `request_cowork_directory` fails (unattended run, nobody to approve), fall back to `mcp__Control_your_Mac__osascript` (`do shell script "cat '<path>'"`, write via heredoc). Then read `Valley Pawn OS/CHANGELOG.md` (top ~80 lines) and `Life OS/OPEN_ITEMS_REGISTER.md` (tail ~120 lines).

Working folder for this task: `~/Documents/Claude/Projects/Gold and Silver Markeitng/ceo-briefing/` — create it if absent. It holds `history.json`, `artifact_url.txt`, and `briefing-YYYY-MM-DD.md`.

## THE CORE RULE: ROLL UP, DO NOT RE-RUN
Eight weekly lane audits already exist and already do the deep work. Your job is the **synthesis layer nothing currently owns** — the cross-channel view, the deltas, and the action register. **Do not re-run their analyses. Read their output.** Re-running is duplicated cost and produces conflicting numbers.

| Lane | Task | Lands | Read from |
|---|---|---|---|
| Website health | `weekly-website-health-audit` | Mon 5:15 AM | `#website` (C0ASE9C0GQ0) + its history file |
| Web analytics | `weekly-analytics-summary` | Mon 9 AM | `#website` |
| Social | `weekly-social-media-recap` | Mon 9 AM | `#social-media` |
| Presence/SEO | `vp-presence-audit-weekly` | Sun 4:20 PM | `#ai-marketing` + its scorecard file |
| Email perf | `email-analytics-weekly` | Fri 9 AM | `#email-campiagns` |
| Email health | `brevo-weekly-efficiency-audit` | Fri 8 AM | `#email-campiagns` |
| eBay | `ebay-weekly-channel-audit` | weekly | `#ebay-performance` |
| Store KPIs | `weekly-store-kpis` | Mon 10:30 AM | `#store-performance` |

All eight complete before 11:30 AM. Use the Slack MCP to read the last 8 days of each channel. Prefer a lane's machine-readable scorecard file on disk when it writes one (find via the task's SKILL.md at `~/Documents/Claude/Scheduled/<task>/SKILL.md`). **If a lane produced nothing this week, that is itself a finding** — report the lane as dark, name it, and check whether the task is enabled and when it last ran. Never silently omit a lane.

## STEP 1 — Build the scorecard and the delta
Assemble one table of the numbers that matter, each with this week's value, last week's value from `history.json`, and the direction. Carry these forward every week so the series is comparable:
- eBay: active listings per store, sold count, revenue, sell-through %, listings >90 days
- Social: posts published, median reach, total engagement, link clicks, % captionless
- Email: campaigns sent, real click rate from `linksStats` (NEVER `uniqueClicks` — it is inflated 1.6–12×), calls+texts per 1,000, staged-draft runway
- Website: `tel:`/`sms:` coverage, pages missing meta descriptions, broken schema, GA4 sessions and conversions
- Local: Google review count and average per store, new reviews this week, any review ≤3★ still unanswered
- Spend: marketing spend MTD from QBO if reachable, and whether it is attributable

Flag anything that moved more than ±20% week-over-week, and anything that has not moved for 3+ consecutive weeks (a stuck metric is a finding — it usually means an owner, not an algorithm, is the blocker). Write the new row into `history.json`.

## STEP 2 — Work the action register
`ceo-briefing/actions.json` is the running to-do list (create it on first run, seeded from the open marketing rows in `Life OS/OPEN_ITEMS_REGISTER.md`). Each item: `id`, `title`, `why_it_matters`, `owner` (`claude` or `joshua`), `effort` (S/M/L), `est_value`, `status` (`open`/`in_progress`/`done`/`dropped`), `first_seen`, `last_checked`, `evidence`.

Every week: **verify each open item against live output, not against what the register claims** (Rule 12 — a prior session recorded a defect that did not exist and a fix that had already shipped; both wasted work). Mark done what is genuinely done, note what has been open 3+ weeks and why, and add anything the lane audits newly surfaced. Retire items honestly — if something is not going to happen, mark it `dropped` with the reason rather than carrying it forever.

## STEP 3 — Fix what does not need Joshua
Follow the pattern the other lane tasks already use: auto-fix safe, reversible defects in-run, back up any file you edit (`.bak-pre-fix-YYYYMMDD`), verify the fix against live output, and log it. Do NOT touch: DNS, anything that sends email to customers, Meta page merges, money movement, or hardened Bravo infrastructure. Additive only — never modify hardened infra, build alongside.
Anything genuinely blocked on Joshua goes in the briefing's "Needs you" section with the single specific decision he has to make — never a technical multiple-choice question. If a decision is his but you have a clear recommendation, give the recommendation and say what you will do absent a reply.

## STEP 4 — Publish the briefing
Write `briefing-YYYY-MM-DD.md` to the working folder, then publish a styled HTML artifact.
**Keep the link stable:** read `artifact_url.txt`; if it holds a URL, pass it as `url` so the artifact updates in place. If not, publish fresh and write the returned URL into that file. Same favicon every week (📈). Title: "Marketing CEO Briefing".
Structure: (1) the one thing that matters most this week, (2) scorecard with deltas, (3) what moved and why, (4) action register — done / in flight / stuck, (5) needs-you decisions, (6) what is going dark or at risk next.
Lead with judgment, not data dumps. Joshua reads this to make decisions, not to admire metrics. Where a number is missing, say so plainly — absence of data is a finding, not a blank cell.

## STEP 5 — Notify
Send Joshua ONE Slack DM (channel `D03BHQH5VGT`): 4–6 lines of plain English — the headline, the biggest number, what you fixed, what needs him, and the artifact link. No jargon, no file paths, no tool names, no error text. Do not post this briefing to any team channel; it is CEO-level and may contain performance and spend detail.

## STEP 6 — Log
Append a dated entry to `Valley Pawn OS/CHANGELOG.md` and a row to `Life OS/OPEN_ITEMS_REGISTER.md` covering what you found, fixed, and left open (Rule 14 — this is what stops the next session repeating your work).

## Standing rules
- **Rule 12 — no diagnosis from metadata.** Verify against the actual output: the channel, the file, the live page. A `lastRun` timestamp proves a session started, not that it worked.
- **Never re-run a lane audit's deep analysis.** Read its result.
- **Numbers must trace to a source.** If two lanes disagree, say so and name both — do not average them.
- **Quarterly:** on the first run of Jan/Apr/Jul/Oct, additionally note in the briefing that a full six-channel deep re-audit is due (the deep version is the expensive one and belongs on a quarterly cadence, not weekly).
- **Failure policy v2:** if this run cannot complete, send Joshua ONE plain-language DM — `⚠️ Scheduled task "marketing-ceo-briefing-weekly" did not complete — <date>.` Nothing technical in the DM; all detail goes to the run log for the next session. Never send failure notices to any team channel, store manager, or employee, including Preston.
- Be economical. Read structured outputs, not raw corpora. Do not spawn deep sub-agents for work the lane tasks already did.