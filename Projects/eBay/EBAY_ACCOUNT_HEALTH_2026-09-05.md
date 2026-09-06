# eBay — markdown engine failure, badging, and feedback replies

Session date: 2026-09-05. Everything below was verified against live API output or the run logs,
not inferred from run records.

## 1. Monthly markdown was half-failing — FIXED

The price cuts are applied by the **native launchd agent `com.valleypawn.ebay-markdown-monthly`**
(1st of the month, 6:00 AM → `~/ebay_markdown_monthly.sh` → `~/ebay_markdown_engine.py`), not by a
Cowork scheduled task. The Cowork task `ebay-markdown-terminal-weekly` (Mondays) only handles the
*pull* half — ending listings that have sat at the 30%-off floor.

**2026-09-01 run:**

| Store | Applied | Failed |
|---|---|---|
| Roanoke | 30 | 0 |
| Culpeper | 43 | **105** |
| Harrisonburg | 11 | 0 |
| Lexington | 10 | 0 |
| Waynesboro | 0 | 0 |

Every Culpeper failure was `Invalid AutoAccept price.` (one was `Auto decline amount cannot be
greater than or equal to the Buy It Now price.`).

**Cause.** Those listings carry Best Offer auto-accept / auto-decline thresholds. The engine
revised `StartPrice` only, so after a 10% cut the untouched thresholds sat at or above the new
Buy It Now price and eBay rejected the entire revise. Culpeper is the store that uses Best Offer
thresholds heavily, which is why it was the only store affected.

**Fix applied** (`~/ebay_markdown_engine.py`, backup at `.bak-20260905`): on a Best-Offer-related
rejection the engine now reads the listing's current thresholds, scales them by the **same ratio**
as the price cut (so the store's offer policy is preserved, not reset), clamps them so
auto-decline < auto-accept < Buy It Now, and retries once. Non-offer failures behave as before.
Verified: dry run on Culpeper returns 122 eligible items and compiles clean.

**Still outstanding:** the 105 Culpeper items have not received their September cut. Running
`python3 ~/ebay_markdown_engine.py Culpeper --apply` clears them immediately; otherwise the
1 October run picks them up automatically now that the fix is in.

## 2. The monthly Slack summary was unreadable — FIXED

The old post was one line of raw counters: applied N, failures N. No stores, no dollars, and the
failure count leaked technical noise into the channel (against Rule 16).

Replaced with `~/ebay_markdown_summary.py`, called from `ebay_markdown_monthly.sh`
(backup `.bak-20260905`). New format:

> **eBay monthly markdown — September 2026**
> Every listing 90+ days old gets another 10% off, up to three times. After that it holds at 30% off and stops.
> • **Culpeper** — 148 listings marked down, $19,666 → $17,360
> • **Roanoke** — 30 listings marked down, $3,412 → $3,009
> • **Waynesboro** — nothing due this month
> **Total: 199 listings, $24,845 → $21,934 in asking price.**

Dollar figures come only from items that actually changed on eBay, so the channel can never show
a number that didn't happen (Rule 18). Anything that fails is written to
`~/ebay_markdown_incomplete.flag` and stays out of the channel.

## 3. Buyer feedback — 8 replies posted 2026-09-05

**Correction to the first version of this doc:** the "30 unanswered" and later "47 unanswered"
counts were wrong. eBay's `GetFeedback` response does **not** reliably return the seller's own
reply, so "has a reply" cannot be read back from the API — three of the eleven replies attempted
came back `Reply to Feedback already submitted`, proving replies existed that the pull could not
see. The honest count is 47 negative/neutral received, of which an unknown number were already
answered.

Because of that, `ebay_feedback_replies.py` now keeps its own record at
`~/ebay_feedback_answered.json`: a feedback id lands there both when a reply posts successfully
and when eBay says one already exists. That file — not the API — is what makes the job idempotent.

**Posted 2026-09-05** (text at `feedback_replies_2026-09-05.json`, run output at
`feedback_replies_2026-09-05_result.txt`): 8 replies — Culpeper 4, Waynesboro 1, Harrisonburg 1,
Lexington 2. Three more (Harrisonburg Switch charger, Lexington chess set, Roanoke buckle) already
had replies. Every reply takes ownership of the specific mistake and says plainly that we don't
like how the buyer's order went; none claims an internal process change that can't be verified.

Remaining after this pass: **36**, essentially all older than 12 months. Replying to 2020-2023
feedback now would only resurface it publicly, so it is deliberately left alone.

## 3a. Original finding — nobody was replying to buyer feedback

Pulled live via `GetFeedback` across all 5 accounts. Negative/neutral feedback with **no seller
reply**:

| Store | Unanswered |
|---|---|
| Lexington | 9 |
| Waynesboro | 6 |
| Harrisonburg | 6 |
| Roanoke | 5 |
| Culpeper | 4 |

Most recent: Culpeper 2026-08-26 (trolling motor condition), Harrisonburg 2026-07-08 (console sold
without charger), Roanoke 2026-05-24 (loose buckle, "messaged seller but no response"), Lexington
2026-04-10 (listing said complete set, wasn't).

Several read as recoverable — a public reply is what future buyers see, and a few of these are
plainly answerable. There is no automation doing this today: `preston-ebay-feedback-watch` was
superseded on 2026-08-26 by `preston-interactive-assistant`, which only acts when Preston asks
in Slack. **Fix:** a weekly task that pulls unanswered negative/neutral feedback, drafts replies in
brand voice, and posts them with `RespondToFeedback` (Trading API — works with existing tokens).

## 4. Why the badge/standards data keeps going missing

`monthly-ebay-ratings-sweep` produced no September document (last one is
`ebay-ratings-sweep-2026-08.md`, run 2026-08-21). That sweep reads Seller Standards out of the
**Seller Hub in Chrome**, so it only ever captures whichever store account Chrome happens to be
signed into — August captured Lexington only, and the other four were left as "data gaps."

Two headless paths were tested today:

- `GetSellerDashboard` (Trading API) → **404**. eBay retired it.
- `GET /sell/analytics/v1/seller_standards_profile` (REST) → **403, "Insufficient permissions"** on
  all 5 stores. The endpoint is right; the tokens lack the `sell.analytics.readonly` scope.

**Fix:** re-consent each of the 5 store tokens once with `sell.analytics.readonly` added, then the
sweep pulls level, late-shipment rate, defect rate and Top Rated status for all 5 stores with no
browser at all. That single change also settles the open badge question from August — whether
Roanoke and Harrisonburg are missing a Top Rated requirement or simply not surfacing the badge.

Known standing issue from the August sweep: **Lexington was Below Standard**, driven by a 4.23%
late-shipment rate against a 3% target, and would flip to Above Standard at the **2026-09-20**
re-evaluation if handling times held.
