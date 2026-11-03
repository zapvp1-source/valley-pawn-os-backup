# Communication: verified stats for the Nov 4, 2026 team meeting deck
Compiled 2026-11-02. No dollar amounts. Every figure lists its source and date range. Scripts that reproduce the call numbers are in this folder: `calls_monthly.py`, `call_reasons.py` and `text_reasons.py`. All three are read-only.

## Headline callouts (for big slide numbers)
| # | Before | After | Source |
|---|---|---|---|
| 1 | **2 in 5 calls went unanswered.** 40% of 798 calls, Sep 9–23 | **Fewer than 1 in 5.** 17–18% in the last two weeks of Oct; 21% for all of October (577 of 2,744) | Zoom call history (Call Analysis/week_*/call_history.json) |
| 2 | **31%** of missed callers were reached by phone within 24 h (Sep 9–23) | **55%** (Oct). Every missed caller also gets a text within about 2 min: **370 texts in October** | call history; fleet/missed_call_text_results.csv |
| 3 | First staff reply to a text took **about 6 hours** on average (Sep 1–27) | **About 19 minutes** (Oct 1–18) | Chekkit Messenger Analytics, "avg initial response", recorded in week_2026-09-21 and week_2026-09-28 chekkit_texts.md |
| 4 | **27 customer texts a day** (2025 average, 820/mo) | **59 a day** (Oct 1–23, 2026). That is 2.2x | Chekkit text census (fleet/state/chekkit_text_census_2025-01-01.json) |
| 5 | Message to drive home: in October, **about 4,500 customers reached out**: 2,744 calls plus about 1,800 texts, or roughly 150 a day. **354 calls still rang out while we were open.** | | combined |

## A. Calls (inbound to the five store lines, Zoom Phone)
"Unanswered" means Zoom logged the call as no_answer, abandoned or voicemail. "While open" uses each store's posted hours. Waynesboro Wednesdays count as open from 10/14 on.

| Period | Stores on Zoom | Inbound calls | Unanswered | While open: missed / inbound | Missed callers reached by phone within 24 h |
|---|---|---|---|---|---|
| Aug 31–Sep 6 (proxy) | HAR, LEX, WAY | 273 recorded inbound | **38%** of recordings had no conversation (the caller hung up in the queue) | — | — |
| Sep 1–23 (figure already in the deck) | HAR, LEX, WAY (+CUL from 9/21) | 1,178 | **415 (35%)**, no follow-up | — | — |
| Sep 9–23 (recomputed) | HAR, LEX, WAY, CUL (from 9/21) | 798 | **322 (40%)** | 162 / 635 (26%) | 31% |
| Sep 24–30 (missed-call text live 9/24) | + ROA from 9/28 | 529 | 128 (24%) | 55 / 452 (12%) | 45% |
| **Oct 1–31** | all 5 | **2,744** (~89/day) | **577 (21%)** | **354 / 2,520 (14%)** | **55%** |

Weekly trend, all stores (unanswered share): wk of 9/7 42%, 9/14 43%, 9/21 23%, 9/28 29%, 10/5 23%, 10/12 22%, 10/19 **17%**, 10/26 **19%**.

**October by store**
| Store | Inbound | Unanswered | Missed while open |
|---|---|---|---|
| Culpeper | 587 | 77 (13%) | 48 / 558 (9%) |
| Harrisonburg | 610 | 176 (29%) | 113 / 547 (21%) |
| Lexington | 296 | 100 (34%) | 56 / 252 (22%) |
| Roanoke | 717 | 122 (17%) | 71 / 666 (11%) |
| Waynesboro | 534 | 102 (19%) | 66 / 497 (13%) |

Same three stores, before and after (HAR/LEX/WAY, Sep 9–23 compared with Oct): unanswered 41% to 26%; missed while open 26% to 18%. HAR 45% to 29%, LEX 45% to 34%, WAY 34% to 19%.

Sources:
- Call Analysis/week_2026-09-09, -09-21, -09-28, -10-12, -10-19, -10-26 /call_history.json, covering Sep 9–Nov 1 and deduplicated by call id. Computed by deck_2026-11/calls_monthly.py.
- The Sep 1–23 baseline is from Valley Pawn OS/bin/missed_call_text.py and CHANGELOG 2026-09-24.
- The Aug 31–Sep 6 proxy is from Call Analysis/FINDINGS_2026-08-31_week.md §5.

## B. Texts (Chekkit, all five stores)
**Inbound customer texts per month** (from chekkit_text_census_2025-01-01.json):
| Period | Per month | Per day |
|---|---|---|
| 2025 (Jan–Dec) | 820 | 27 |
| Jan–Jun 2026 | 996 | 33 |
| Jul–Sep 2026 | 1,442 | 47 |
| Oct 1–23, 2026 | 1,346 counted (≈1,800 for the full month at that pace) | **59** |

Oct 1–23 by store: WAY 470, HAR 425, CUL 219, ROA 123, LEX 109. Oct 2025 for comparison: 624 in the whole month.

**Response speed**: Chekkit Messenger Analytics, average time to the first staff reply, weighted by conversations.
| Store | Sep 1–27 (before) | Oct 1–18 (after) |
|---|---|---|
| Culpeper | 6h 28m | 14m 42s |
| Harrisonburg | 7h 14m | 52m 49s |
| Lexington | 6h 54m | 2m 19s |
| Roanoke | 4h 15m | 5m 04s |
| Waynesboro | 4h 32m | 15m 30s |
| **Company** | **≈5h 47m** | **≈19m** |

**Same-week answer rate, before.** In the hand audit of Sep 21–27, 16 of 103 text conversations (about 1 in 6) had a customer message that never got a staff reply that week (week_2026-09-21/chekkit_texts.md).

**After, with the 7 PM check.** From Oct 20–31 (the scorecard counts are reliable from 10/20 on), only **8 customer texts in the whole company waited 10+ minutes without a reply**: 5 during open hours and 3 while closed, over 11 open days. Every one goes to the 7 PM end-of-day check. Source: fleet/texting_scorecard/2026-10-20…31.json.

**AI text responder** (live 9/30), from fleet/ai_responder/events-2026-10-*.jsonl:
- October: **142 customer texts answered by the AI**. 99 came in during open hours and **43 while the store was closed**. By store: WAY 45, HAR 38, CUL 23, LEX 21, ROA 15.
- It screened **1,010 inbound texts**. It stayed silent on 156 (photo only, sign-off, or a reply to a staff thread). It left 712 to staff because a staff member was already in the conversation (the 10-minute alert is the backup).
- It sent no replies Oct 27–31 because the AI account hit its monthly limit. The limit was raised 10/31 and replies resumed 11/1 (CHANGELOG 2026-10-31).

**Missed-call auto-texts**, from fleet/missed_call_text_results.csv (Chekkit API matched):
- October: **370 sent**. CUL 55, HAR 104, LEX 73, ROA 72, WAY 66.
- **68 replies (18%)**: 60 real conversations (16%) and 8 STOP (2%). The median customer reply came **2 minutes** after our text.
- By store, conversations: HAR 29 of 104, LEX 13 of 73, WAY 13 of 66, ROA 7 of 72, CUL 6 of 55.
- Sep 24–30 (first week): 87 sent, 17 replied (20%).

## C. Before and after (summary)
| Measure | Before | After |
|---|---|---|
| Calls unanswered | 35–40% (Sep 1–23) | 21% Oct; 17–19% last 2 weeks |
| Calls missed while open | 26% (Sep 9–23) | 14% Oct |
| Missed callers followed up | none (texts) · 31% reached by phone | every one texted in ~2 min (370 in Oct) · 55% reached by phone |
| First text reply | ~6 hours | ~19 minutes |
| Customer texts | 27/day (2025) | 59/day (Oct 2026) |
| After-hours texts answered | 0 (nobody) | 43 answered by AI in Oct |

## D. Why customers contact us
**Calls.** 2,079 answered inbound customer calls, Sep 21–Oct 31. Each call was read and graded, and the intent field is used here. Sources: Call Analysis/week_2026-09-21 review_batch*.json, week_2026-09-28 review_*.json, and the 10-12 regrade, 10-19 and 10-26 review_native.json files, deduplicated (deck_2026-11/call_reasons.py).
| Reason | Calls | Share |
|---|---|---|
| Loan payment, extension, payoff, due date | 615 | **29.6%** |
| Selling an item / "what will you give me" | 482 | **23.2%** |
| "Do you have X" / price of an item in store | 229 | **11.0%** |
| Firearms (buying, background check status, transfers: 33 of 167) | 167 | **8.0%** |
| Follow-up on an item, hold or layaway | 110 | **5.3%** |
| Gold, silver, jewelry | 89 | **4.3%** |
| New pawn loan | 85 | **4.1%** |
| Hours / location | 52 | **2.5%** |
| Other (asking for a staff member, stolen-item checks, police, returns, jobs) | 250 | 12.0% |

Loan servicing rose from 24% of calls in late September to 31% in October (the Oct 1 loan-rule change).

**Texts.** 218 customer-started text conversations. 76 are every customer-started thread at all five stores for Sep 21–27, read by hand (week_2026-09-21/chekkit_texts.md). 142 are every first text the AI answered in October (events-2026-10-*.jsonl, deck_2026-11/text_reasons.py).
| Reason | Texts | Share |
|---|---|---|
| Selling an item (photos + "how much would you give") | 68 | **31.2%** |
| "Do you have X" / price | 40 | **18.3%** |
| Loan payment, extension, payoff | 27 | **12.4%** |
| Firearms | 18 | **8.3%** |
| New pawn loan on an item | 17 | **7.8%** |
| Gold, silver, jewelry, coins, watches | 16 | **7.3%** |
| Hours / location | 9 | **4.1%** |
| Other (thanks, jobs, app sign-in, lost item) | 23 | 10.6% |

Takeaway: the top reason people call is to take care of a loan they already have. Texts are mostly new business: someone with an item to sell or looking for something. Both are money walking in the door, if we answer.

**Example quotes** (anonymized, no amounts):
- Call, loan: *"I don't think I'm gonna make it today, but you said y'all open tomorrow?"*
- Call, looking for an item: *"You guys wouldn't have happened to have a [PS5] brought in today, would you?"*
- Text, firearms: *"What guns do you have for sale and how much?"*
- Text, loan and selling: *"Can I make payment over the phone or bring something in to sell? Unable to download app."*

## E. Caveats
- **No disposition data before Sep 9.** Culpeper and Roanoke were on Verizon until 9/21 and 9/28, so there is no 5-store baseline. The Aug 31–Sep 6 figure (38%) is a recording-based proxy.
- **Text counts stop at Oct 23.** The Chekkit census ends Oct 23 because the tokens are in the Mac's Keychain and can't be read from this session. October's full-month text total is a pace estimate.
- **AI responder offline Oct 27–31.** The AI account hit its spend limit, so its October total (142) covers Oct 1–26.
- **Text reasons are a sample.** They come from 218 conversations, not every text. Firearm texts are undercounted after 10/23, when the AI stopped answering gun questions and left them to staff.
- **Two baselines for September.** The 35% figure (Sep 1–23, a separate pull) and the recomputed 40% (Sep 9–23) differ. Use 35% as the conservative number.
