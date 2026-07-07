# Valley Pawn — Scheduled Task Model Policy & Playbook

_Last updated: 2026-07-07. Owner: Joshua. This doc exists because figuring this out took hours — read it before touching scheduled-task models._

## TL;DR

A scheduled task runs on whatever model the Cowork app happens to be on **at fire time** — UNLESS the task's own `SKILL.md` has a `model:` line in its frontmatter, which **overrides everything**. That frontmatter line is the ONLY durable, per-task, execution-only way to pin a model. Proven live on 2026-07-07 (pinned the FFL task to Haiku while the app was on Sonnet — the run came back Haiku).

## The mechanism (what we proved)

- There is **no** per-task model field in the scheduler tool or in the app's `scheduled-tasks.json` registry. Don't look there.
- At run time, each task spawns a session. That session's model normally follows the **app's active/default model**. On 2026-07-07 the app default was stuck on `claude-fable-5` (expensive, and it had been pulled by an export-control action on 6/12), so tasks ran on Fable and burned budget.
- A `model:` key in the task's `SKILL.md` frontmatter **overrides** the app default for that task. This is the fix.

## How to set or change a task's model

1. Open `/Users/joshuadavis/Documents/Claude/Scheduled/<task-id>/SKILL.md`.
2. In the frontmatter (between the two `---` lines), add or edit:
   ```
   model: claude-sonnet-5
   ```
3. Valid model IDs: `claude-haiku-4-5`, `claude-sonnet-5`, `claude-opus-4-8`, `claude-fable-5`.
4. Back the file up first (`SKILL.md.bak-...`). Change takes effect on the task's **next scheduled run** — nothing else needs restarting.
5. Do NOT touch anything below the second `---` (the task body). Only the frontmatter line changes.

## How to verify which model a run actually used

Each run writes a session file. Check the newest run for a task:
```bash
python3 - <<'PY'
import json,glob,os
base="/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d"
def fm(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k.lower()=="model" and isinstance(v,str): return v
            r=fm(v)
            if r: return r
    elif isinstance(o,list):
        for v in o:
            r=fm(v)
            if r: return r
for f in sorted(glob.glob(base+"/local_*.json"),key=os.path.getmtime)[-40:]:
    d=json.load(open(f)); print(d.get("title"), fm(d))
PY
```

## Tier framework

- **Haiku** (`claude-haiku-4-5`) — cheapest. Token pings, health checks, threshold alerts, mechanical file/artifact refreshes, simple detect-and-notify. No narrative or judgment.
- **Sonnet** (`claude-sonnet-5`) — the default for the bulk. Data pulls, reports, scans, KPI compiles, templated Slack/email posts, lightweight orchestration, most pipeline work.
- **Opus** (`claude-opus-4-8`) — customer-facing copy, brand voice, long-form content, multi-asset creative orchestration, high-stakes HR/financial judgment.
- **Fable** (`claude-fable-5`) — DO NOT USE for scheduled tasks. Most expensive and has been pulled from the platform before; wrong choice for anything unattended. Reserve for interactive one-offs only.

## Current assignments (2026-07-07)

**Haiku (14):** asset-recovery-daily-refresh, blog-publisher-watchdog, chekkit-unanswered-alert, daily-cloudcover-check, ebay-photo-enhance-done-notify, fb-token-health-check-daily, monthly-analytics-prestage, nightly-desktop-cleanup, oura-daily-import, vp-deal-of-week-monday-prompt, vp-website-trend-daily-refresh, vp-weekly-spot-price-update, weekly-website-kpi-artifact-refresh, wordpress-token-keepalive

**Opus (7):** annual-board-review, dismiss-employee, monthly-bonus-targets, monthly-we-buy-gold-silver-email, nightly-chekkit-review-responses, valley-pawn-blog-publisher, vp-content-batch-weekly

**Sonnet (49):** amazon-return, bald-rock-15-day-contract, bald-rock-guest-reviews, bald-rock-monday-briefing, bravo-health-watchdog, brevo-preflight-watchdog, chekkit-new-review-alert, chekkit-weekly-review-requests, daily-clockin-check, daily-dress-code-check, daily-ffl-transfer-check, daily-funds-verification, daily-items-to-price, daily-supply-order, ebay-title-enrichment-backlog, ebay-weekly-quality-fix, email-analytics-weekly, eom-bravo-gl-export, ffl-web-form-to-slack, funds-verification-watchdog, monday-bravo-combined-run, monday-bravo-postcheck, monthly-amazon-store-allocation, monthly-analytics-report, monthly-analytics-watchdog, monthly-capability-drift-audit, monthly-employee-sales-rankings, monthly-gun-audit-report, pawn-walk, review-obtained-last-week, sunday-checklist-summary, tuesday-supply-checkout, tuesday-supply-summary, vp-ai-search-health-check, vp-ai-visibility-metrics, vp-casual-video-daily, vp-content-batch-postflight, vp-content-batch-preflight, vp-dashboard-refresh, vp-deal-of-week-monday-pick, vp-deals-social-wednesday, vp-publer-analytics-friday, vp-website-deals-weekly, vsp-nics-fee-monthly-check, weekly-analytics-summary, weekly-loan-layaway-manager-dms, weekly-returns-summary, weekly-store-kpis, weekly-timekeeping-analysis

_New tasks default to Sonnet unless a `model:` line says otherwise. When you add a task, set its model per the framework above._

## Separate issue: tasks that get SKIPPED (not a model problem)

If tasks aren't running, check the skip log in `scheduled-tasks.json` → `recordedSkips`. Reasons:
- `global_limit` / `per_task_limit` = you hit a **usage/credit cap**, not a model issue. Fix = buy credits and/or lower model weight (which this policy does). On 2026-07-07 the FFL task alone was skipped 243× on `global_limit`.

## Backups

Every task file edited for model has a backup next to it: `SKILL.md.bak-model-pin-<timestamp>`. Revert by restoring that file.
