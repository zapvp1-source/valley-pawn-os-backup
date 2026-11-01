# We Buy Gold — Operating Loop (implement → measure → evaluate → fix → repeat)
Created 2026-10-31. Owner: Claude (autonomous). Decision owner: Joshua (money / customer-facing sends only).

## 1. The one outcome
Gold, silver and jewelry BUYS from the public, per store-day, in dollars and count — from Bravo (intake-detail, Ticket Kind=BUY).
Everything else (page views, text clicks, calls, email opens) is a leading indicator and is reported only as a step in the funnel toward that number.

## 2. Baseline (locked)
Sep 1 – Oct 6, 2026 (pre-launch): 3.65 PM buys / store-day, $270 / store-day (Bravo intake-detail, 7-day weeks, captured store-days only; computed by bin/gold_scorecard.py).
Target by 2026-12-31: +25% buys/store-day and +25% $/store-day vs baseline, company-wide, with every store above its own baseline.

## 3. The funnel and where each number comes from (weekly, automated)
1. Found: organic + GBP + email + social sessions landing on /sell-gold*/ (GA4 by page; Search Console impressions/clicks for "sell gold near me", "gold buyer <city>", "cash for gold <city>").
2. Acted: cta_text_click / sms_click, cta_call_click, calc_quoted, calc_text_offer per store (GA4 events, store_id dimension).
3. Conversed: Chekkit conversations where the customer wrote about gold/silver/jewelry/coins, per store (Chekkit API, per-store Keychain tokens — live).
4. Bought: PM BUY count and $ per store (Bravo intake-detail — pipeline must capture EVERY store-day; missing days are backfilled automatically the next night).
5. Margin: intake margin on those buys (daily-intake-margin lane already computes T1/T2/T3).

## 4. Cadence
- Nightly: Bravo intake-detail for all 5 stores (morning pull); com.valleypawn.intake-backfill (03:35) re-pulls any missing store-day in the trailing 14 days, ≤2 dates/night. GA4 windows pull (exists, 09:20).
- Weekly (Mon 07:40, com.valleypawn.gold-scorecard): `bin/gold_scorecard.py` writes `ceo-briefing/gold/week_<date>.json` + appends `gold_history.csv`, renders the ONE finished report (formatter, not model), evaluates the decision rules below, and writes the actions to `Ai Optimized Marketing/register/MARKETING_OPEN_ITEMS.json`.
- Every 14 days: implement the next fix from the backlog (one variable at a time per store so cause is attributable), note it in `gold_history.csv` as an annotation so the chart shows what changed when.
- Monthly: Gold & Silver email (exists) — its send date is an annotation; email-channel buys measured the following 7 days.

## 5. Decision rules (evaluated by the script, not by judgment)
- Found < 50 sessions/week company-wide on /sell-gold*/ → traffic problem → next fix comes from the Traffic backlog.
- Found ≥ 50 but (text+call clicks)/sessions < 8% → page problem → next fix from the Page backlog.
- Clicks fine but Chekkit gold conversations/clicks < 30% → response problem → store-side fix (reply time, scripts).
- Conversations fine but buys flat → offer/price or counter problem → payout % review against competitors (Precious Metals Settlements has melt and spot).
- Any store 2 weeks below its baseline while others rise → store-specific fix, named in the report.

## 6. Backlogs (ordered)
Traffic: ~~internal links~~ (already present: nav on every page + body links on all 5 location pages, verified 10/31); ~~GBP website + services~~ (DONE 10/31 via BrightLocal: services lead with We Buy Gold, website → /locations/<city>/, pending BrightLocal NAP review on 4 stores); GBP posts twice monthly with live gold price; Search Console indexing request; ~~FAQPage schema~~ and ~~$25,000 mismatches~~ (both false findings, closed 10/31); monthly blog post per city on gold price; Google Local Services / Search ads on "sell gold <city>" (MONEY — Joshua decision, proposed with a budget when traffic rules fire twice).
Page: live price above the fold; photo-quote CTA first on mobile; 3 proof points (payout %, same-day cash, 5 locations); remove calculator friction (default 14k, grams/dwt toggle).
Response: Chekkit gold tag + 2-minute reply SLA script; store bonus hook for gold buys (bonus-program lane).
Offer: payout % by karat published vs top 2 competitors per city, refreshed monthly from Precious Metals Settlements.

## 6b. Rank tracking
Search Console query positions (in the scorecard) are the rank source. BrightLocal LRT reports 1813835 (CUL) 1813836 (WAY) 1813837 (HAR) 1813838 (LEX) 1813839 (ROA) exist with the 6 gold keywords each, but the plan has no free scheduled slots or ad-hoc credits — running them is a plan upgrade (money, Joshua).

## 7. Human-only items (HUMAN_QUEUE, once)
- (none for Google — GA4 Data API + Search Console API granted 2026-09-09, pulled headless daily by com.valleypawn.analytics-api-pull; the token lives only on the Mac at ~/.config/valley-pawn, so a `--check` run anywhere else reports NO ACCESS falsely.)
- Approve any paid spend.

## 8. Reporting rule
One weekly finished report (Slack #website or the CEO brief, formatter output only, Rule 16/18). No partial numbers; if a source is dark the report says the funnel step is unmeasured and why that is being fixed, never a caveated guess.

## 9. Log
- 2026-10-31: loop built and live. First reading (10/19–25): 37 gold-page sessions, TRAFFIC rule. BrightLocal listing changes pushed. Re-measure 2026-11-16.
