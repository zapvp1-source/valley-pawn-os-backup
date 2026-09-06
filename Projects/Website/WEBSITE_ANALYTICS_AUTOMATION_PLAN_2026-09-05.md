# Website Analytics — Automation Overhaul Plan
**Date:** 2026-09-05 · **Status:** PROPOSED — nothing changed yet · **Domain:** 1 (Valley Pawn)
**Goal:** one Claude-free data layer feeding every website report; reports that measure calls/texts/emails/directions, not just sessions; deterministic posts that cannot drift or lie.

---

## 1. What exists today (verified against #website / #ai-marketing output, not run records)

| Publication | Task | Cadence | Method | Health |
|---|---|---|---|---|
| Weekly Website Analytics → #website | `weekly-analytics-summary` (sonnet) | Mon 9 AM | Chrome scrapes 2 GA4 UI reports | Posting on time. Reports "Key events: 15" only — never says how many calls/texts/directions. |
| Website trend artifact (D/W/M/Q/A) | `vp-website-trend-daily-refresh` (haiku) | daily 2:40 AM | Chrome scrapes 10 GA4 UI pages, rewrites HTML by hand | Not in guardian. "Approximate is acceptable" is written into the task. |
| Website KPI artifact | `weekly-website-kpi-artifact-refresh` | — | — | Disabled 8/04, cause never confirmed (Open Items L152). |
| Weekly Website Health Audit → #website | `weekly-website-health-audit` (sonnet) | Mon 5:15 AM | Real crawler `AUDIT_2026-08-22/bin/weekly_crawl.py` + history JSON | Healthy. Best-built task in the function. |
| Shop refreshed → #website | `vp-website-shop-nightly` (sonnet) | 7 AM / 3 PM | Model re-derives the method every run; 20+ throwaway `fetch_*.py` copies; `BASE` path hand-edited every run | Missed 8/19, 8/20, 8/26 PM, 8/27 PM; double-fired 8/29; excluded-count swings 0 → 132 → 21 same week (filter not deterministic); post format differs every run. |
| Shop weekly DM → Joshua | `vp-website-shop-weekly-report` | Mon 7:40 AM | Jetpack stats via WP MCP | 3rd separate traffic pull for the same numbers. |
| Retail deals → #website | `vp-website-deals-weekly` | Mon 1:05 PM | Slack → images → WP REST | Working since 8/21 hardening; not in guardian. |
| Shop-in-store sync | `shop-in-store-sync` | 10:10 / 16:10 | WP + Woo REST | Healthy, ~empty (1 item). 6 differently-named log files. |
| AI-search health / AI visibility / presence → #ai-marketing | 3 tasks + 2 autofix | Mon/Fri/Sun | Browser prompt tests + GA4 UI scrape (Part B) | Posting. 4th GA4 pull of the week. |
| Month in Review → #website, #ai-marketing | `monthly-eom-recap` | 1st | Re-reads Slack posts | New 9/5 — depends on the posts above being accurate. |

**Structural findings**
1. **Zero programmatic GA4 access.** No service account, no Data API client anywhere. Every number is screen-scraped by a browser 4× a week (weekly summary, daily trend, AI-visibility Part B, plus Jetpack for the DM). Our own connector policy (VP Ops Engine, 2026-07-27) already classifies GA4 as *API lane → native*. It was never done.
2. **Reporting measures traffic, not leads.** GA4 already fires `phone_click`, `sms_click` (shipped 8/23), `directions_click` with store attached. No report breaks them out by store or page. The site's job is calls/texts/emails/doors — we don't measure that.
3. **No Search Console data at all.** Organic is 64–71% of sessions; GSC alerts (structured-data errors) arrive by email and sit unread. Rankings for "pawn shop near me + city" are never tracked.
4. **Shop refresh is the biggest automation debt** — non-deterministic method, no idempotency, no guardian entry, no canonical script.
5. **No safety net** for 4 of 8 publications (shop-nightly, deals-weekly, trend-daily, shop weekly DM aren't in `fleet/expected_outputs.json`).
6. **Same items carried weekly, never fixed:** 55 zero-H1 pages (template), Gutenberg dev plugin/perf, Clarity emitting nothing, 26 duplicate pages, max-loan-amount contradiction (blocked on Joshua since 8/23, no Open Items row).
7. **Post format drift** in shop posts — same root cause as the 8/31 aged-inventory failure (model re-renders the table). Fix pattern already proven 9/5: deterministic formatter, post stdout verbatim, exit 2 = post nothing.

---

## 2. Target architecture (additive — nothing hardened is modified)

```
Google (GA4 Data API + Search Console API)  ──┐
eBay storefront (5 stores)                     ├─►  Projects/Website/analytics/bin/*.py  (native, stdlib, launchd)
WordPress REST (App Password, exists)         ─┘         │
                                                         ▼
                              Projects/Website/analytics/data/{ga4,gsc,shop}/YYYY-MM-DD.json   ← single source of truth
                                                         │
          ┌──────────────────┬───────────────────┬───────┴────────────┬──────────────────┐
   format_weekly_       build_trend_       format_shop_        website_kpis.json    monthly-eom-recap
   website.py           artifact.py        post.py             → vp-dashboard        (reads data, not Slack)
   (exact Slack body)   (HTML, no LLM)     (exact Slack body)
          │                  │                   │
   Cowork task = launcher + verifier + poster only (sonnet/haiku), Rule-18 gate: exit 2 → post nothing
```

Judgment stays on Claude: AI-engine prompt tests, presence audit, deals page copy, health-audit auto-fix decisions, "needs a decision" narrative.

---

## 3. Phases

### Phase 0 — the one thing only Joshua can do (~10 min, once)
Create a Google Cloud service account, enable **Google Analytics Data API** + **Search Console API**, add its email as **Viewer** on GA4 property 353209303 and as a user on the `thevalleypawn.com` Search Console property, drop the JSON key at `~/.config/valley-pawn/google_sa.json`. I'll write the exact click-path. Never expires, no browser, no password screens. This unlocks everything below.

### Phase 1 — Website Data Layer (native, Claude-free)
- `ga4_pull.py` — daily 3:00 AM: sessions, users, engagement, channels, landing pages, **events by name × store × page** (phone/sms/directions/email/form), AI-assistant source rows. Writes yesterday + rolling 7/28/90/365 windows. Idempotent, resumable.
- `gsc_pull.py` — daily: clicks/impressions/CTR/position by query and page; tracks a fixed keyword set ("pawn shop near me", "sell gold {city}", "pawn shop {city}" × 5); pulls index-coverage + rich-result errors so GSC emails become data.
- `shop_fetch.py` — replaces the 20+ ad-hoc scripts: parameterized paths, per-store throttle/retry, deterministic weapons filter (same regex every run, logged), writes `items.json` + `result.json`.
- launchd `com.valleypawn.website-data-daily` + `com.valleypawn.shop-refresh` (7 AM / 3 PM). Plists staged; installation is one click from Joshua.
- Fresh-file watchdog entries in `fleet/expected_outputs.json` (file-age, not Slack).

### Phase 2 — Deterministic publications (same channels, same cadence, locked format)
- `format_weekly_website.py` → exact Slack body for #website Monday 9 AM. New **Leads block**: calls / texts / directions / email clicks by store, lead rate per 100 sessions, top converting pages, WoW. Then traffic, then top pages, then **Search block** (rank moves on the keyword set, new GSC errors). Footer unchanged.
- `format_shop_post.py` → exact "Shop refreshed" body; per-store counts, excluded count, H1/ItemList check. Same-day duplicate guard.
- `build_trend_artifact.py` → regenerates the `vp-website-trend` DATA object from real daily series (no "approximate is acceptable"), publishes to the Cloudflare dashboard's `artifacts/` and `kpis.json` (website row added to the KPI dashboard).
- `weekly-analytics-summary`, `vp-website-trend-daily-refresh`, `vp-website-shop-nightly` SKILL.md rewritten as launcher/verifier/poster (backups kept). `vp-website-shop-weekly-report` and `vp-ai-visibility-metrics` Part B read the data layer instead of pulling again — 4 GA4 pulls/week → 1 daily native pull.
- `weekly-website-kpi-artifact-refresh` formally retired (superseded; Open Items L152 closed).
- Add the 4 missing publications to `expected_outputs.json`; `monthly-eom-recap` #website section sourced from data files.

### Phase 3 — Measure what the site is for (conversion instrumentation)
- Verify all 5 click events fire per store on live pages (automated weekly check inside the health audit).
- Add `form_submit` on email-capture forms; `email_click` on mailto.
- Clarity: fix project ID or remove the dead tag (removal recommended unless someone will watch replays).
- Meta Pixel / Google Ads tag: only when paid spend starts — staged snippet ready, not installed.
- Weekly post gets a **Lead cost proxy** once paid runs (spend ÷ leads).

### Phase 4 — Retire the carried-forever items
- 55 zero-H1 pages: template-level fix via WP REST (theme template part), verified live, reversible.
- Performance: remove Gutenberg dev plugin, add image dimensions, scope Woo assets off non-shop pages; weekly page-weight sample already tracked so the win is measurable.
- Duplicate-content consolidation + 301s (26 pages): I prepare the merge map + redirect list; **Joshua approves the map** (editorial), then it ships in one pass.
- Max loan amount: added as an Open Items row today; needs Joshua's number.
- `shop-build/` cleanup: canonical scripts stay, 40+ scratch files archived to `_archive_20260905/`. `instore-sync/logs` consolidated to one log.

### Phase 5 — Proving week + cutover
Native jobs run in shadow for one week alongside the current tasks; byte-compare outputs; then the Cowork tasks flip to verifier mode. Rollback = re-enable the prior SKILL.md from backup. Guardian covers every publication from day one.

---

## 4. Decisions that are Joshua's (everything else I just do)
1. **Phase 0 grant** (service account + two API enables + two Viewer adds) — one 10-minute sitting.
2. **Install the launchd plists** — one approval click each.
3. **Max loan amount** — $10K / $25K / $100K, which one is true.
4. **Duplicate-content merge map** — approve before 301s go live (editorial, irreversible-ish).
5. Clarity: remove (recommended) or keep.

## 5. What could break / blast radius
- Touches: #website, #ai-marketing, Joshua DM, `vp-website-trend` artifact, Cloudflare dashboard, `/shop/` page 833, `/retail/` page 10, `marketing-ceo-briefing-weekly` (reads #website post — format stays a superset), `monthly-eom-recap`.
- Does NOT touch: Bravo pipeline, any hardened infra, `daily-funds-verification`, WooCommerce page 1110 guard.
- Risk: eBay throttling on the storefront endpoint (mitigated: per-store retry + reuse last good file, never publish a short list — Rule 18).

## 6. Sequence & effort
Phase 0 (Joshua, 10 min) → Phase 1 (1 session) → Phase 2 (1–2 sessions) → shadow week → Phase 3–4 (rolling, each item verified live) → Phase 5 cutover. Phase 4 cleanup and Open Items row can start immediately without Phase 0.
