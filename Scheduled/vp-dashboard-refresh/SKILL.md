---
name: vp-dashboard-refresh
description: Nightly refresh of the Valley Pawn enterprise dashboard (vp-dashboard.pages.dev) — re-parse Slack reports, re-sync artifacts, redeploy to Cloudflare Pages
model: claude-sonnet-5
---


Refresh and redeploy the Valley Pawn enterprise dashboard. The complete runbook is at:
/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/REFRESH_RUNBOOK.md

READ THE RUNBOOK FIRST and follow it exactly. Summary of the steps it defines:

1. UPDATE KPI DATA — Read the latest standard-format report ("Sent using Claude") from each Slack channel and update /Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/data/kpis.json, preserving the exact JSON schema:
   WEEKLY/MONTHLY FEEDS:
   - #loan-review (C0B08RS2BMK): pastDue rows [store, items, dollars, pct], pastDueTotal, companyLoanBalance, dates.loans
   - #layaway-review (C04N24STDP1): layaway rows, layawayTotal, dates.layaway
   - #company-performance (C0B26GD8D2R): watch[] items
   DAILY FEEDS:
   - #daily-funds-reconcilation (C0B3R9B3S8H): funds {status, expected, actual, note}, dates.funds
   - #items-to-price (C0BA5U0GENL): daily.itemsToPrice {date, stores [[store, items, cost]], total {items, cost}}
   - #pawn-walks (C0B8WR95N31) "Intake Margin" posts: daily.intakeMargin {date, note, stores [[store, items, avgMargin, flags]], company {items, avgMargin, flags}}
   - #chekkit-unanswerd-summary (C0B1PEW0C30): daily.chekkit {date, totalUnanswered, summary}
   DO NOT touch the "bravoDaily" section — it is owned by the daily-bravo-kpis task; preserve whatever is there.
   Update asOf to today. Update feeds[] Last Run column. If a channel has no newer report, keep existing values. NEVER fabricate numbers; on parse failure keep old data.

2. SYNC ARTIFACTS — via the osascript tool run:
   cp -R /Users/joshuadavis/Documents/Claude/Artifacts/* '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/artifacts/' && rm -rf '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/artifacts'/*/versions
   If new artifact folders appeared, add entries to site/data/artifacts.json (standalone=true only if its index.html contains no "window.cowork" references). Update "updated" dates for changed artifacts.

3. DEPLOY — in the sandbox shell, from the mounted Business Dashboard Website folder:
   export CLOUDFLARE_API_TOKEN=$(cat .cloudflare/api_token); export CLOUDFLARE_ACCOUNT_ID=$(cat .cloudflare/account_id); npm install -g wrangler --silent; npx wrangler pages deploy site --project-name=vp-dashboard --commit-dirty=true
   NEVER delete site/_worker.js — it is the password gate.

4. VERIFY — curl https://vp-dashboard.pages.dev/ must return 401 without auth, and 200 with basic auth user "valleypawn" and the password from .cloudflare/site_password. Also verify data/kpis.json parses as valid JSON.

5. Only if a step FAILED, post a one-line failure summary to Slack #general. On success, no Slack post.

<!-- migrated to working model 2026-06-15 -->