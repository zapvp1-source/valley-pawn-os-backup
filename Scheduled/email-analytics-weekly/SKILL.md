---
name: email-analytics-weekly
description: Friday 9 AM ET — pull Brevo API per-link clicks, update master Google Sheet via OAuth, refresh live dashboard, post 5-line summary to #email-campiagns.
model: claude-sonnet-5
---


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running the Valley Pawn weekly email analytics job. Today is Friday at ~9:04 AM ET. This task pulls the prior week's email campaign performance, refreshes the master Google Sheet, updates the live dashboard, and posts a 5-line summary to `#email-campiagns`.

## Goal
Produce decisions from every send, not just events. Every weekly post should give Joshua a recommendation tied to data, not just numbers.

## North-star metric (Phase 1, today)
**Directions clicks per 1,000 recipients.** A Maps "Directions" tap is the strongest measurable foot-traffic-intent signal we can get from Brevo right now. Calls + Texts clicks become measurable once the `/c/<store>` and `/t/<store>` redirects ship on thevalleypawn.com (Phase 1.6) — until then, this metric stays as the proxy.

## Tools (all production-grade, no Chrome scraping)
- `~/Documents/Claude/Scheduled/_shared/brevo_helper.py` — Brevo API v3 client. Loads key from `~/.config/valley-pawn/brevo_api_key`. Per-link click data via `BrevoClient().per_link_clicks(campaign_id)` and UTM-bucketed via `utm_content_bucketed_clicks(campaign_id)`.
- `~/Documents/Claude/Scheduled/_shared/sheets_helper.py` — Google Sheets read/append/update/upsert. Auth via cached OAuth token at `~/.config/valley-pawn/google-oauth-token.json` (refreshes automatically when expired). Authenticates as Joshua → inherits his Drive permissions.
- Slack MCP for the post.
- Cowork artifact `email-analytics-dashboard` reads the sheet on each open — no manual refresh needed.

## Master sheet
- ID: `1EPj22S1zzbSm4B_mRZ4y8TEXXpiCj6YM_75TmVV4d2o`
- Tab: `Email Campaign Performance` (quote the tab name in ranges because it has spaces — e.g. `'Email Campaign Performance'!A:V`)
- Primary key: `campaign_id` (use `sheets_helper.upsert_by_key`)
- Slack channel for summary: `#email-campiagns` (`C0APR5WUL2Z`)

## Execution Contract — DO NOT STOP EARLY
This task is complete only after the Slack post returns success. Every assistant turn ends with a tool call that advances toward it. If a step fails, retry once, then post a `:warning:` line in the Slack channel and stop.

==============================
STEP 0 — LOAD CONTEXT
==============================
Read `valley-pawn-context` (especially the "Email-program tech stack" section) and `brevo-context`. Skim — you've done this before.

==============================
STEP 1 — PULL CAMPAIGNS FROM BREVO API
==============================
```python
import sys; sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from brevo_helper import BrevoClient
b = BrevoClient()
sent = b.list_email_campaigns(status='sent')
```
For each campaign, you have `id`, `name`, `sentDate`, plus enough fields to fill the sheet row (recipients via per-campaign `get_email_campaign(id).statistics.campaignStats[0].sent`). For new sends, the Brevo aggregate fields you care about per campaign: `sent`, `delivered`, `uniqueViews`, `uniqueClicks`, `unsubscriptions`, `softBounces`, `hardBounces`, `complaints`.

==============================
STEP 2 — DIFF AGAINST THE SHEET
==============================
```python
from sheets_helper import SheetsClient
s = SheetsClient()
existing = s.read_as_dicts(SHEET_ID, 'Email Campaign Performance')
existing_ids = {r['campaign_id'] for r in existing}
```
- **NEW** (id not in sheet) → drill into per-link stats in STEP 3, then append
- **STALE** (in sheet, send_date within last 14 days) → re-pull aggregate + per-link, then update
- **FROZEN** (in sheet, send_date > 14 days old) → skip; numbers are mature

==============================
STEP 3 — PER-LINK CLICK BUCKETING
==============================
For each NEW or STALE campaign:
```python
buckets = b.utm_content_bucketed_clicks(campaign_id)
# buckets is {utm_content: click_count} — e.g.:
#   {'logo': 16, 'store_culpeper_map': 8, 'store_harrisonburg_map': 6, 'primary_cta': 4, ...}
directions_clicks = sum(v for k, v in buckets.items() if k.endswith('_map'))
calls_clicks     = sum(v for k, v in buckets.items() if k.endswith('_call'))   # 0 until WordPress redirects ship
texts_clicks     = sum(v for k, v in buckets.items() if k.endswith('_text'))   # 0 until WordPress redirects ship
primary_cta_clicks = buckets.get('primary_cta', 0)
```
Compute derived metrics:
- `directions_per_1k = directions_clicks / recipients * 1000`
- `calls_texts_per_1k = (calls_clicks + texts_clicks) / recipients * 1000`
- `primary_cta_pct = primary_cta_clicks / recipients * 100`

==============================
STEP 4 — WRITE TO SHEET
==============================
```python
result = s.upsert_by_key(SHEET_ID, 'Email Campaign Performance', 'campaign_id', new_or_updated_rows)
print(f"updated {result['updated']} existing rows, appended {result['appended']} new rows")
```
Each row dict needs every header column from the sheet (see schema). `last_synced_at` = current UTC ISO timestamp.

==============================
STEP 5 — COMPUTE TRENDS
==============================
Pull active (non-legacy) rows from the sheet, sort by `send_date` desc. For each KPI, compute:
- This week's value (most recent sent campaign)
- Trailing 4-week avg (next 4 active sends)
- Direction: up (>5% favorable change), down (>5% unfavorable change), flat (within ±5%)

KPIs (order them by importance):
1. **Directions per 1,000** (north star) — higher is better
2. **Primary-CTA click rate** — higher is better
3. **Unsubscribe rate** — lower is better, red line at 0.5%
4. **Open rate** — directional only, never the lead

Also: identify the most striking pattern this week — biggest delta vs trailing avg, theme breakthrough, or red-line breach. That's the "lead movement" line in the Slack post.

==============================
STEP 6 — POST SLACK SUMMARY
==============================
Post to `#email-campiagns` (`C0APR5WUL2Z`) — exactly 5 lines:
```
:bar_chart: Email — Week of <YYYY-MM-DD>
Lead movement: <metric that moved most, with direction and delta>
Directions per 1,000: <this send> (avg <trailing 4wk>) <arrow>
<KPI #2 or #3 line — whichever is more newsworthy this week>
Recommendation for next send: <one concrete thing tied to the data>
:link: <dashboard URL or sheet link>
```
Concrete > vague. Don't say "consider improving CTA"; say "Education weeks consistently underperform on Directions/1k — alternate with Deals weeks to maintain weekly traffic-intent volume."

==============================
GUARDRAILS
==============================
- Brevo `tel:` and `sms:` clicks are NOT trackable. Calls+Texts columns stay blank until WordPress redirects ship. Don't fabricate.
- Sheet writes are atomic — if `upsert_by_key` raises, fix and retry; never write partial.
- Open rate is shown for context only. Never lead the Slack post with open rate (MPP bot opens make it unreliable).
- If a metric has been off-target for 2+ consecutive weeks, flag it in the recommendation. Don't flag single bad weeks.
- The Friday cron's runtime window is tight. Total runtime should be <3 minutes — the API + Sheets path is much faster than the old Chrome scraping path.

==============================
PHASE 1.6 (when WordPress redirects ship)
==============================
Once `/c/<store>` and `/t/<store>` redirects are live and the weekly email template references them, swap the north-star metric to **Calls + Texts per 1,000**. The sheet columns are already in place; the bucketing code in STEP 3 will start returning non-zero values automatically.

==============================
PHASE 2 (future)
==============================
- Email-to-Bravo customer matching for send-day in-store lift
- Promo code attribution
Both belong in a separate scheduled task that runs Sunday night (after the post-send transaction window closes), reading from the email-analytics-weekly sheet to identify the cohort.

<!-- migrated to working model 2026-06-15 -->