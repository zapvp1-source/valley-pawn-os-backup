# Communications Review — inside and outside the company
**Date:** 2026-10-20 · **Domain:** 1 — Valley Pawn · **Project:** Communcations · **Status:** findings verified against live output (Rule 12); fixes built the same day (see §4)
**Board:** customer-experience / contact-center lead · reliability engineer (fleet owner) · brand & reputation reviewer
**Standard applied:** every automatic communication must be *functional* — the customer gets the right answer, quickly, without a person in the loop; every channel must produce data someone can act on.

---

## 1. Where customers actually reach us (verified 10/13–10/20)

| Channel | Volume | What handles it today | Verified state |
|---|---|---|---|
| **Phone (Zoom, 5 stores)** | ~100 inbound calls/day; 84% of all contact | Staff answer; missed-call → text (native, 60 s); call-back list in #voicemails-calls-missed; EOD "still no callback" | 86% answered 10/19 company-wide, **Harrisonburg 67%**; 3-week review: HAR 21% missed while open, 44 callers never reached; WAY missed all 9 calls on its first open Wednesday |
| **Text (Chekkit SMS)** | 50–80 conversations/store/3 wks | Staff + in-house AI responder (24/7, Claude, reads the Chekkit API) | AI replies ~9/day, stays silent on ~25/day "ongoing with staff"; replies were never read back by anyone (see §2.3) |
| **Web chat (Chekkit Textchat)** | ~30/3 wks | Same inbox as SMS | Covered by the AI responder |
| **Facebook Messenger / Instagram** | low single digits | Chekkit (per-store Meta tokens) | Tokens invalidated 10/6 at 4 stores, reconnected; HAR review site still points at the legacy page |
| **Google reviews** | ~7 new/week, 4.8–4.9★ | 5★ shout-outs hourly; invites Tue (API); **reply task OFF since 9/15** | **Waynesboro 19 awaiting response**; 1★ Culpeper and 3★ Waynesboro (10/16) unanswered, and the channel celebrated them |
| **Email (customer)** | ≈0 | Store mailboxes are 98% marketplace/machine mail | Not a customer channel; nothing to build |
| **Email marketing (Brevo)** | 11–13k contacts | Weekly send + monthly gold + win-back (live 9/30) | Weekly cadence lapsed 9/10→10/15; 10/15 send produced 0 calls/texts; email traffic to the site −44% |
| **Website** | 440 sessions, 107 leads/wk | GA4 lead events (calls 78, texts 12, directions 10, forms 7) | Working; the only channel with clean lead attribution |
| **Push (MobilePawn app)** | unknown | Vendor app | No visibility; out of scope |
| **Social** | 86 posts/wk across FB/GBP/IG | Publer, weekly recap | Volume fine; engagement lane reply sweep exists |

## 2. Structural failures (what the board found)

### 2.1 The review-reply loop is dead (reputation)
`nightly-chekkit-review-responses` was disabled in the 9/16 fleet freeze and never rebuilt natively. Nothing replaced it. The hourly alert used one wording for every rating, so on 10/16 #google-reviews read *"Nice job Team Culpeper! You just got a new 1 star review"* and nobody was told to do anything. Chekkit's own API has no reply endpoint, so the only automatic path is the dashboard.

### 2.2 The daily texting scorecard was wrong
`texting_scorecard.py` counted every Chekkit "message via" notification as a 10-minute miss (that email type was added to the shared reader on 10/5 for the AI responder). It reported Waynesboro 12 unanswered on 10/19; the morning summary — the correct method — said 0. A number Joshua reads every evening overstated friction 5–10×.

### 2.3 Automated texts had no accuracy loop
The AI responder's fact list still said *"loans 75+ days past due must be brought current by Saturday Oct 3, 2026"* on 10/20. On 10/14 it told a Waynesboro customer "we're closed right now" on the first open Wednesday (config fixed that day — found by a human reading transcripts four days later). Its event log stores the decision, never the text, so no one could audit what customers were told. Harrisonburg's automated review-reminder text still said **"Dixie Pawn Inc."** (36 sends 10/9 + 10/16).

### 2.4 Phone is the weakest channel and the richest data is manual
The weekly Phone & Text Review (1,790 calls read 10/18) surfaced the real failures — holds on past-due loans against the Oct 1 policy, account details to unverified callers, PII read to an unverified "ATF" caller, a possible under-21 sale, stores out of cash, 20-minute holds — and its automation never started ("local scheduled-task creation blocked"). The missed-call text covers about half of open-hours misses (7 texts for 13 misses on 10/19); the call-back list names numbers but no metric closes the loop.

### 2.5 SMS channel risk
Harrisonburg's 30-day opt-out rate in Chekkit is **2.71%** (carrier threshold 2%) after the Oct 1 loans blast and the open-Wednesdays blast. Above 2% the carriers can start filtering the store's texts — including the missed-call texts and AI replies. Blasts need a frequency rule before the next one.

### 2.6 Internal
Automated posts still arrive under two identities (ops bot vs "Joshua — *Sent using Claude*": the 10/19 weekly rankings, clock-in, dress-code — the latter two go native 10/21). Team-facing report walls still draw zero reactions (8/24 verdict unchanged). #emails-missed has been dead since 9/17 with an orphan "delayed" post. The 9/5 Comms plan's Phase 1–3 (engine, bot identity, dedupe) is largely done natively; Phase 4 (customer frequency/consent ledger, attribution) is not.

## 3. What is working and should not be touched
Missed-call → text (60 s, deduped, hours-aware); Chekkit unanswered morning/EOD loop (correct method, closes every 10-minute miss by day end); win-back email (weekly, automatic); website lead tracking; SPF on fcfpawn.com fixed (one record); DMARC published on both domains (p=none, reports to Brevo); native fleet-guardian/doctor coverage.

## 4. Built today (additive; backups beside each file; nothing sent to a customer)

| # | Change | File(s) | Status |
|---|---|---|---|
| 1 | Scorecard counts only real "Unanswered Message Alert" emails, once per message | `bin/texting_scorecard.py` (bak `fleet/_backups/…bak-pre-commsreview-20261020`) | **Verified**: 10/19 re-render now HAR 1 / LEX 1 = morning summary |
| 2 | Stale Oct 3 deadline replaced by an evergreen rule; dated facts now flagged nightly | `fleet/chekkit_ai_config.json` | Live |
| 3 | Review alert: 1–3★ get a plain heads-up in #google-reviews + one DM to Joshua with the review text; 4–5★ unchanged | `bin/chekkit_review_alert.py` | **Verified** render (dedupe held) |
| 4 | **Nightly AI-reply audit** — reads back every automated text from the Chekkit API, grades it against current hours/facts (rules + Claude), DMs Joshua only when something was wrong; scorecard shows "N read back, M wrong" | `bin/ai_reply_audit.py/.sh`, `fleet/com.valleypawn.ai-reply-audit.plist` (21:45) | **Verified**: 10/14 caught both Waynesboro "we're closed" replies; 10/19 read all 9 sends, 0 wrong. Live nightly. |
| 5 | **Weekly Phone & Text Review, native** — Monday 02:30: pull + transcribe, grade every call via the API (same schema as the hand review), stats, Chekkit text audit, PDF to Drive "Call Reviews", 3-line DM | `bin/call_week_grade.py/.sh`, `fleet/com.valleypawn.call-week-review.plist` | **Verified end to end** on Oct 12–18: 616 of 617 calls graded, PDF in Drive › Call Reviews, DM delivered 10/20 6:10 PM. Live every Monday. |
| 6 | **Review replies, native** — 19:30: 4–5★ drafted and posted through the Chekkit dashboard on the shared automation profile; 1–3★ drafted to Joshua only | `bin/review_reply.py/.sh`, `fleet/com.valleypawn.review-reply.plist` | Installed **dormant** (gated on `native_live/nightly-chekkit-review-responses`) until Chekkit is signed in on pw-vp + one clean render |
| 7 | Harrisonburg drip reminder text: "Dixie Pawn Inc." → "Valley Pawn in Harrisonburg" | Chekkit → Settings → Review → Drip Campaigns | **Done and verified after reload** |
| 8 | Sign-in window gains a Chekkit tab (`vp_signin_front.sh --only chekkit`) | `bin/vp_signin_front.sh` | Live |

## 5. Still open (ranked)
1. **Chekkit sign-in on the automation profile** (Joshua, once, ~1 min: `bin/vp_signin_front.sh --only chekkit`, then quit) → then one `review_reply.py --render` and `touch fleet/state/native_live/nightly-chekkit-review-responses`. Until then Waynesboro's 19 (and the rest) stay unanswered.
2. **Harrisonburg phones** — 21% missed while open, 44 never reached in 3 weeks. Not a software problem: staffing/ring-group. Weekly review will show whether it moves.
3. **SMS blast frequency rule** — the 9/5 plan's Phase 4 ledger (2 touches / 7 days, consent flag) is still unbuilt; HAR opt-out rate 2.71%.
4. ~~Facebook review site at Harrisonburg~~ — resolved 10/23: points at the live store page 474248069342834 (see §7).
5. **Other 4 stores' drip templates** not yet read (Culpeper known correct); check LEX/ROA/WAY for the old name the same way.
6. Brevo weekly cadence and the Store Spotlight segments (precision beats volume 100×) — marketing lane, separate plan.
7. \#emails-missed: archive with a pinned pointer to the mail brief (Joshua's call — Phase 5).

## 6. Evidence read
`fleet/texting_scorecard/2026-10-13…19.json`, `fleet/ai_responder/events-*.jsonl`, `fleet/chekkit_ai_config.json`, `Call Analysis/week_2026-09-28/{stats.json,review_*.json,chekkit_texts.md}`, Slack #general / #google-reviews / #chekkit-messages-missed / #voicemails-calls-missed / #store-performance / #email-campiagns / #website / #social-media / #emails-missed, Chekkit dashboard (Waynesboro reviews, Harrisonburg settings/compliance), DNS (SPF/DMARC/MX via DoH), `Life OS/HUMAN_QUEUE.md`, `fleet/FAILURE_LEDGER.md`, CHANGELOG 10/18–10/20.

## 7. Follow-up 2026-10-21 (Joshua: "fix all this")
- **No overlap:** no native agent or cloud scheduled task (50 active checked) replies to reviews, audits AI texts, or runs the call review, other than the three built here.
- **Review backlog cleared:** 70 public replies to 4–5★ reviews (WAY 16, CUL 20, ROA 12, LEX 8, HAR 14); every store at 0 except three lower-rated Waynesboro reviews left for Joshua.
- **Harrisonburg Facebook review link:** checked again on 10/23 and set to the live store page (474248069342834). The 10/21 change to 795439020329931 was wrong because that page no longer exists. All five reminder texts verified clean (CUL correct; LEX/ROA/WAY reminders off; HAR fixed 10/20).
- **Text opt-out rates (30-day):** ROA 14.29%, LEX 4.17%, CUL 3.02%, HAR 2.71%, WAY 1.97%. The monthly "Shop Us Online" text now checks each store first and holds any store at 1.8%+. Its wording now uses "Text STOP to unsubscribe" (what blocked the 10/15 send), and campaign copy no longer advertises phones.
- **Still needs Joshua once:** the Chekkit sign-in in the automation browser so future 4–5★ replies post nightly on their own.

## 8. Follow-up 2026-10-23 (Joshua: "go")
- **Review replies now run on their own.** Joshua signed in once. The test run reached all 5 stores and drafted 5 new 4–5★ replies (Waynesboro 2, Roanoke 3). From tonight, 4–5★ replies post at 7:30 PM every night; 1–3★ reviews still come to Joshua as drafts.
- **Monthly Chekkit logins check** (3rd of the month) compares the Gusto staff list with Chekkit users. First run: nobody who left still has access. 4 staff were never set up: Joshua Burnett (Culpeper), Camden Ahern (Harrisonburg), Brendon Thomas (Roanoke), Stephanie Chaplin (Waynesboro). Those 4 are on the human list because Chekkit's API cannot add users.
- **Customer tags from Bravo** (nightly): `bravo-customer-2yr` (about 15,400 customers), `bravo-visited-60d` (about 3,800), `bravo-borrower`, `bravo-do-not-text`, `bravo-winback`. The tags are on customers who are already in Chekkit; nobody is added. With them, a text campaign can go to people who have actually been in recently instead of the whole list, which is the lever on opt-outs. The first full pass finishes in about two nights.
- **Carrier safety (Joshua: yes, 10/23).** Each store's monthly text list now leaves out anyone Bravo marks do-not-text and anyone we texted marketing in the last 14 days, and is capped at 2,000. For November that's 568 fewer numbers, with 5,703 left across the five stores. The win-back texts skip do-not-text customers too. The AI text responder no longer sends any reply that mentions guns, firearms or ammo, because carriers restrict that content; staff answer those instead. The send still holds any store whose opt-out rate is 1.8% or higher.
