# Valley Pawn — Publer 90-Day Published-Output Audit

**Window:** 2026-05-24 through 2026-08-22 (91 calendar days)  
**Source:** Publer API `GET /posts?state=published` + `GET /analytics/{account}/post_insights` — live pull, not manifests.  
**Pulled:** 2026-08-22T13:04:39.990367  
**Raw data:** `audit_2026-08-22/publer_90day_raw.json`

---

## 1. Total published posts by account

**TOTAL PUBLISHED POSTS IN WINDOW: 554**

| Account | Platform | Published posts | Per week (÷13) |
|---|---|---:|---:|
| Brand | facebook | 43 | 3.3 |
| Culpeper | facebook | 111 | 8.5 |
| Harrisonburg | facebook | 13 | 1.0 |
| Lexington | facebook | 34 | 2.6 |
| Roanoke | facebook | 81 | 6.2 |
| Waynesboro | facebook | 80 | 6.2 |
| BrandIG | instagram | 76 | 5.8 |
| BrandTikTok | tiktok | 0 | 0.0 |
| BrandTwitter | twitter | 26 | 2.0 |
| BrandBlog | wordpress_oauth | 24 | 1.8 |
| GBP_Lexington | google_business | 13 | 1.0 |
| GBP_Waynesboro | google_business | 13 | 1.0 |
| GBP_Harrisonburg | google_business | 13 | 1.0 |
| GBP_Roanoke | google_business | 16 | 1.2 |
| GBP_Culpeper | google_business | 11 | 0.8 |
| **TOTAL** | | **554** | **42.6** |

**Connected accounts with ZERO published posts in the window:** BrandTikTok

## 2. Posts per week per account (week starting Monday)

Every week bucket touching the window is shown (14 buckets). The first bucket (2026-05-18) is PARTIAL — the window opens Sunday 2026-05-24, so it holds only that one day. The last bucket is partial too (window closes 2026-08-22). Column totals therefore equal the full 554.

| Account | 05-18 | 05-25 | 06-01 | 06-08 | 06-15 | 06-22 | 06-29 | 07-06 | 07-13 | 07-20 | 07-27 | 08-03 | 08-10 | 08-17 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Brand | 0 | 18 | 3 | 0 | 0 | 0 | 1 | 4 | 0 | 9 | 0 | 3 | 2 | 3 | 43 |
| Culpeper | 5 | 27 | 15 | 14 | 7 | 3 | 2 | 1 | 6 | 13 | 4 | 9 | 3 | 2 | 111 |
| Harrisonburg | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 6 | 0 | 2 | 0 | 1 | 13 |
| Lexington | 5 | 18 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 6 | 0 | 1 | 0 | 1 | 34 |
| Roanoke | 6 | 26 | 14 | 14 | 7 | 1 | 3 | 0 | 1 | 6 | 0 | 2 | 0 | 1 | 81 |
| Waynesboro | 5 | 25 | 14 | 14 | 7 | 1 | 3 | 1 | 1 | 6 | 0 | 2 | 0 | 1 | 80 |
| BrandIG | 3 | 18 | 3 | 0 | 0 | 0 | 6 | 8 | 0 | 23 | 0 | 12 | 0 | 3 | 76 |
| BrandTikTok | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| BrandTwitter | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 4 | 0 | 6 | 0 | 8 | 2 | 3 | 26 |
| BrandBlog | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 24 |
| GBP_Lexington | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 1 | 6 | 0 | 1 | 0 | 1 | 13 |
| GBP_Waynesboro | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 1 | 6 | 0 | 2 | 0 | 1 | 13 |
| GBP_Harrisonburg | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 1 | 6 | 0 | 2 | 0 | 1 | 13 |
| GBP_Roanoke | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 1 | 1 | 6 | 0 | 2 | 0 | 1 | 16 |
| GBP_Culpeper | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 6 | 0 | 2 | 0 | 1 | 11 |
| **ALL** | 24 | 134 | 51 | 44 | 24 | 7 | 31 | 31 | 16 | 107 | 6 | 50 | 8 | 21 | **554** |

## 3. Media type breakdown

| Media type | Posts | % of total |
|---|---:|---:|
| image | 430 | 77.6% |
| text | 53 | 9.6% |
| video | 47 | 8.5% |
| article | 24 | 4.3% |
| **TOTAL** | **554** | 100% |

### Media type by account

| Account | image | text | video | article |
|---|---|---|---|---|
| Brand | 13 | 14 | 16 | 0 |
| Culpeper | 100 | 3 | 8 | 0 |
| Harrisonburg | 10 | 3 | 0 | 0 |
| Lexington | 23 | 4 | 7 | 0 |
| Roanoke | 71 | 2 | 8 | 0 |
| Waynesboro | 70 | 3 | 7 | 0 |
| BrandIG | 75 | 0 | 1 | 0 |
| BrandTikTok | 0 | 0 | 0 | 0 |
| BrandTwitter | 15 | 11 | 0 | 0 |
| BrandBlog | 0 | 0 | 0 | 24 |
| GBP_Lexington | 10 | 3 | 0 | 0 |
| GBP_Waynesboro | 10 | 3 | 0 | 0 |
| GBP_Harrisonburg | 10 | 3 | 0 | 0 |
| GBP_Roanoke | 14 | 2 | 0 | 0 |
| GBP_Culpeper | 9 | 2 | 0 | 0 |

### Video posts over time (the 'no videos' question)

| Week starting | Video | Image | Text | Article | Total | Video % |
|---|---:|---:|---:|---:|---:|---:|
| 2026-05-18 | 0 | 24 | 0 | 0 | 24 | 0% |
| 2026-05-25 | 45 | 82 | 5 | 2 | 134 | 34% |
| 2026-06-01 | 0 | 46 | 3 | 2 | 51 | 0% |
| 2026-06-08 | 0 | 42 | 0 | 2 | 44 | 0% |
| 2026-06-15 | 0 | 21 | 1 | 2 | 24 | 0% |
| 2026-06-22 | 0 | 5 | 0 | 2 | 7 | 0% |
| 2026-06-29 | 2 | 25 | 2 | 2 | 31 | 6% |
| 2026-07-06 | 0 | 29 | 0 | 2 | 31 | 0% |
| 2026-07-13 | 0 | 14 | 0 | 2 | 16 | 0% |
| 2026-07-20 | 0 | 79 | 26 | 2 | 107 | 0% |
| 2026-07-27 | 0 | 4 | 0 | 2 | 6 | 0% |
| 2026-08-03 | 0 | 36 | 12 | 2 | 50 | 0% |
| 2026-08-10 | 0 | 3 | 4 | 1 | 8 | 0% |
| 2026-08-17 | 0 | 20 | 0 | 1 | 21 | 0% |

- All 47 video posts fall between **2026-05-25T11:19** and **2026-07-04T15:20**.
- Publer `source` field on those video posts: {'sync': 45, 'post_now': 2}.
- Video posts per calendar day: {'2026-05-25': 45, '2026-07-04': 2}

**Read this carefully — it is the crux of the 'no videos' complaint.** 45 of the 47 videos carry `source: sync` and timestamps inside a single ~19-minute window on the morning of 2026-05-25 (11:19–11:38 ET). Their `post_link` values are real `facebook.com/reel/...` URLs, so they genuinely published — but they were hand-uploaded to Facebook in one manual batch and only *imported* into Publer afterwards (`updated_at` on those records is 2026-06-19, three weeks later). They were not produced or scheduled by the content pipeline. Since that one burst, video output across all 15 connected accounts over the remaining 89 days is **2 posts**.

| Timestamp | Account | Source | Caption (first 120 chars) |
|---|---|---|---|
| 2026-05-25T11:19 | Brand | sync | Some items just walk in and command the room. ⌚ ⏎  ⏎ We buy watches every day at Valley Pawn — and we pay more than you  |
| 2026-05-25T11:22 | Brand | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:22 | Brand | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:22 | Brand | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-05-25T11:23 | Brand | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:23 | Brand | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:23 | Brand | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:23 | Brand | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-05-25T11:23 | Brand | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:24 | Brand | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:24 | Brand | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:24 | Brand | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-05-25T11:24 | Brand | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:24 | Brand | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:25 | Brand | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:28 | Waynesboro | sync | Some items just walk in and command the room. ⌚ ⏎  ⏎ We buy watches every day at Valley Pawn — and we pay more than you  |
| 2026-05-25T11:28 | Lexington | sync | Some items just walk in and command the room. ⌚ ⏎  ⏎ We buy watches every day at Valley Pawn — and we pay more than you  |
| 2026-05-25T11:28 | Culpeper | sync | Some items just walk in and command the room. ⌚ ⏎  ⏎ We buy watches every day at Valley Pawn — and we pay more than you  |
| 2026-05-25T11:29 | Roanoke | sync | Some items just walk in and command the room. ⌚ ⏎  ⏎ We buy watches every day at Valley Pawn — and we pay more than you  |
| 2026-05-25T11:29 | Lexington | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:29 | Waynesboro | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:29 | Culpeper | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:30 | Lexington | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:30 | Waynesboro | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:30 | Culpeper | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:30 | Roanoke | sync | Some items just walk in and command the room. ⌚ ⏎  ⏎ We buy watches every day at Valley Pawn — and we pay more than you  |
| 2026-05-25T11:30 | Roanoke | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:32 | Roanoke | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:32 | Culpeper | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-05-25T11:32 | Lexington | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:32 | Waynesboro | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:32 | Culpeper | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:32 | Roanoke | sync | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 2026-05-25T11:32 | Lexington | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:32 | Lexington | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-05-25T11:32 | Waynesboro | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-05-25T11:33 | Waynesboro | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:33 | Culpeper | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:33 | Roanoke | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:34 | Lexington | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:34 | Waynesboro | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:34 | Culpeper | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:35 | Roanoke | sync | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 2026-05-25T11:37 | Culpeper | sync | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 2026-05-25T11:38 | Roanoke | sync | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 2026-07-04T13:51 | Brand | post_now | (no caption) |
| 2026-07-04T15:20 | BrandIG | post_now | (no caption) |

### Publishing source: pipeline vs. synced-from-platform

| source | Posts | Meaning |
|---|---:|---|
| sync | 332 | posted natively on the platform; Publer only imported the record afterwards |
| schedule | 189 | published BY Publer on a schedule (the automation pipeline) |
| post_now | 33 | published BY Publer immediately (manual/immediate send through the pipeline) |

### Raw Publer `type` values seen (unmapped, for transparency)

| Publer post.type | count |
|---|---:|
| photo | 430 |
| status | 53 |
| video | 47 |
| article | 24 |

## 4. Engagement

- Accounts Publer exposes post-level analytics for: Brand, BrandBlog, BrandIG, BrandTwitter, Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro
- Accounts returning NO analytics rows at all: BrandTikTok, GBP_Culpeper, GBP_Harrisonburg, GBP_Lexington, GBP_Roanoke, GBP_Waynesboro
- Analytics rows fetched vs. Publer's own reported `total` (completeness check): Brand 42/42, Culpeper 111/111, Harrisonburg 13/13, Lexington 34/34, Roanoke 81/81, Waynesboro 80/80, BrandIG 75/75, BrandTikTok 0/0, BrandTwitter 25/25, BrandBlog 24/24, GBP_Lexington 0/0, GBP_Waynesboro 0/0, GBP_Harrisonburg 0/0, GBP_Roanoke 0/0, GBP_Culpeper 0/0
- Posts with any engagement metric available: **485** of 554 published posts (87.5%).

Engagement score = likes + comments + shares + saves (Publer's own per-post analytics values).

### TOP 15 posts by engagement

| # | Eng | Likes | Cmts | Shares | Reach | Account | Date | Media | Caption (first 120 chars) |
|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 1 | 9 | 6 | 0 | 3 | 942 | Lexington | 2026-07-23 | text | Lexington — we're hiring! Valley Pawn on Walker Street is looking for a Retail Sales Associate. ⏎  ⏎ Sundays off, closed |
| 2 | 7 | 6 | 0 | 1 | 275 | Culpeper | 2026-07-24 | text | There's $100 on the table every month — and it could be yours. 💵 ⏎  ⏎ One customer wins $100 each month, drawn on the la |
| 3 | 6 | 5 | 0 | 1 | 435 | Waynesboro | 2026-07-23 | text | Waynesboro friends — we're hiring! Valley Pawn on West Broad Street is looking for a Retail Sales Associate. ⏎  ⏎ What m |
| 4 | 5 | 4 | 0 | 1 | 101 | Brand | 2026-07-21 | image | Skyline Drive has 75 overlooks between Front Royal and Rockfish Gap, and on a clear July morning half of them look like  |
| 5 | 5 | 5 | 0 | 0 | 448 | Lexington | 2026-07-21 | image | Before the shops open and the VMI cadets are out marching, Walker Street is just brick sidewalks, quiet storefronts, and |
| 6 | 5 | 4 | 0 | 1 | 469 | Culpeper | 2026-07-23 | text | Culpeper, we're hiring! Valley Pawn is looking for a Retail Sales Associate right here in town. ⏎  ⏎ Sundays off, home b |
| 7 | 5 | 5 | 0 | 0 | 83 | Waynesboro | 2026-08-06 | image | This week's deal at our Waynesboro store: a Case 1905 75th Anniversary 7-knife set for $1,199.99 — one of the nicest set |
| 8 | 4 | 3 | 1 | 0 | 17 | Waynesboro | 2026-05-30 | image |  |
| 9 | 4 | 3 | 1 | 0 | 87 | Culpeper | 2026-07-13 | image | ⚡️ Power You Can Trust – Now at an Incredible Price! ⚡️ ⏎  ⏎ Don’t miss this deal on the Honda EU2200i Inverter Generato |
| 10 | 4 | 3 | 0 | 1 | 72 | Culpeper | 2026-07-16 | image |  |
| 11 | 4 | 4 | 0 | 0 | 78 | Culpeper | 2026-07-22 | image | Sandi Cole and Bree run the counter at our Culpeper store. Both appraise gold, jewelry, tools, and everything else that  |
| 12 | 4 | 4 | 0 | 0 | 333 | Brand | 2026-08-03 | text | Every item that leaves our counter comes with a 30-day warranty. That's not a slogan, it's store policy at all 5 of our  |
| 13 | 4 | 3 | 1 | 0 | 300 | Brand | 2026-08-04 | text | How a pawn loan actually works at Valley Pawn: bring in an item, we appraise it on the spot using our data-driven pricin |
| 14 | 3 | 2 | 1 | 0 | 14 | Waynesboro | 2026-05-28 | image |  |
| 15 | 3 | 2 | 1 | 0 | 16 | Waynesboro | 2026-06-01 | image |  |

### BOTTOM 15 posts by engagement

| # | Eng | Likes | Cmts | Shares | Reach | Account | Date | Media | Caption (first 120 chars) |
|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 1 | 0 | 0 | 0 | 0 | 26 | Culpeper | 2026-05-24 | image | 💥 PAY IN CASH this Memorial Day and SAVE UP TO 30% STOREWIDE! 💥 ⏎  ⏎ Tools 🔧 Jewelry 💎 PS5 🎮 Xbox 🎮 Laptops 💻 and so muc |
| 2 | 0 | 0 | 0 | 0 | 1 | Culpeper | 2026-05-24 | image | Everything in this post is worth real money at Valley Pawn. ⏎  ⏎ Go look in your drawer. Your jewelry box. Your loose-ch |
| 3 | 0 | 0 | 0 | 0 | 1 | Culpeper | 2026-05-24 | image | Got gold sitting in a drawer? Let's get you paid for it. ⏎  ⏎ We pay the most for gold in the area — chains, rings, brok |
| 4 | 0 | 0 | 0 | 0 | 17 | Culpeper | 2026-05-24 | image |  |
| 5 | 0 | 0 | 0 | 0 | 20 | Lexington | 2026-05-24 | image | 💥 PAY IN CASH this Memorial Day and SAVE UP TO 30% STOREWIDE! 💥 ⏎  ⏎ Tools 🔧 Jewelry 💎 PS5 🎮 Xbox 🎮 Laptops 💻 and so muc |
| 6 | 0 | 0 | 0 | 0 | 24 | Lexington | 2026-05-24 | image |  |
| 7 | 0 | 0 | 0 | 0 | 1 | Lexington | 2026-05-24 | image | Everything in this post is worth real money at Valley Pawn. ⏎  ⏎ Go look in your drawer. Your jewelry box. Your loose-ch |
| 8 | 0 | 0 | 0 | 0 | 2 | Lexington | 2026-05-24 | image | That gold chain in the back of your drawer? It's worth more than you think. ⏎  ⏎ We pay the most for gold in the valley  |
| 9 | 0 | 0 | 0 | 0 | 24 | Lexington | 2026-05-24 | image |  |
| 10 | 0 | 0 | 0 | 0 | 5 | Roanoke | 2026-05-24 | image | 💥 PAY IN CASH this Memorial Day and SAVE UP TO 30% STOREWIDE! 💥 ⏎  ⏎ Tools 🔧 Jewelry 💎 PS5 🎮 Xbox 🎮 Laptops 💻 and so muc |
| 11 | 0 | 0 | 0 | 0 | 3 | Roanoke | 2026-05-24 | image |  |
| 12 | 0 | 0 | 0 | 0 | 0 | Roanoke | 2026-05-24 | image | Everything in this post is worth real money at Valley Pawn. ⏎  ⏎ Go look in your drawer. Your jewelry box. Your loose-ch |
| 13 | 0 | 0 | 0 | 0 | 0 | Roanoke | 2026-05-24 | image | Top dollar for your gold — every day, no exceptions. ⏎  ⏎ Whether it's a single chain or a whole jewelry box of broken p |
| 14 | 0 | 0 | 0 | 0 | 0 | Roanoke | 2026-05-24 | image | Top dollar for your gold — every day, no exceptions. ⏎  ⏎ Whether it's a single chain or a whole jewelry box of broken p |
| 15 | 0 | 0 | 0 | 0 | 3 | Roanoke | 2026-05-24 | image |  |

### Median engagement per account

| Account | Posts w/ metrics | Median engagement | Mean | Max | Median reach |
|---|---:|---:|---:|---:|---:|
| Brand | 42 | 0.0 | 0.64 | 5 | 15.0 |
| Culpeper | 111 | 0.0 | 0.72 | 7 | 23.0 |
| Harrisonburg | 13 | 1.0 | 0.92 | 2 | 46.0 |
| Lexington | 34 | 0.0 | 0.79 | 9 | 25.0 |
| Roanoke | 81 | 0.0 | 0.16 | 3 | 6.0 |
| Waynesboro | 80 | 0.0 | 0.80 | 6 | 14.0 |
| BrandIG | 75 | 0.0 | 0.23 | 3 | 4.0 |
| BrandTikTok | 0 | n/a — no analytics exposed | n/a | n/a | n/a |
| BrandTwitter | 25 | 0.0 | 0.36 | 1 | 1.0 |
| BrandBlog | 24 | 0.0 | 0.00 | 0 | 0.0 |
| GBP_Lexington | 0 | n/a — no analytics exposed | n/a | n/a | n/a |
| GBP_Waynesboro | 0 | n/a — no analytics exposed | n/a | n/a | n/a |
| GBP_Harrisonburg | 0 | n/a — no analytics exposed | n/a | n/a | n/a |
| GBP_Roanoke | 0 | n/a — no analytics exposed | n/a | n/a | n/a |
| GBP_Culpeper | 0 | n/a — no analytics exposed | n/a | n/a | n/a |

## 5. Comments / community signal

- Posts where a comment count is measurable: **485**
- Posts that received AT LEAST ONE comment: **18**
- TOTAL comments across all measured posts: **18**
- Share of measured posts with any comment: **3.7%**

| Account | Date | Comments | Caption |
|---|---|---:|---|
| Brand | 2026-08-04 | 1 | How a pawn loan actually works at Valley Pawn: bring in an item, we appraise it on the spot using our data-driven pricin |
| Culpeper | 2026-07-13 | 1 | ⚡️ Power You Can Trust – Now at an Incredible Price! ⚡️ ⏎  ⏎ Don’t miss this deal on the Honda EU2200i Inverter Generato |
| Roanoke | 2026-08-05 | 1 | Roanoke has a Klein Tools 3-piece ModBox rolling tool set priced at $229.99 - stackable, latched, built for moving gear  |
| Waynesboro | 2026-07-04 | 1 |  |
| Waynesboro | 2026-06-22 | 1 |  |
| Waynesboro | 2026-06-21 | 1 |  |
| Waynesboro | 2026-06-19 | 1 |  |
| Waynesboro | 2026-06-18 | 1 |  |
| Waynesboro | 2026-06-13 | 1 |  |
| Waynesboro | 2026-06-09 | 1 |  |
| Waynesboro | 2026-06-08 | 1 |  |
| Waynesboro | 2026-06-07 | 1 |  |
| Waynesboro | 2026-06-06 | 1 |  |
| Waynesboro | 2026-06-01 | 1 |  |
| Waynesboro | 2026-05-30 | 1 |  |
| Waynesboro | 2026-05-28 | 1 |  |
| Waynesboro | 2026-05-26 | 1 |  |
| Waynesboro | 2026-05-24 | 1 |  |

- Cross-check: the `comments[]` array on the raw `/posts` objects (Publer's own stored replies) contains **0** entries across all 554 posts.

## 6. Caption sample — 25 most recent, verbatim

**1. Brand — 2026-08-22T11:02 — image**

```
We buy gold and silver at all five Valley Pawn stores — rings, coins, bars, sterling, even broken chains. Bring it in for a fair, no-pressure evaluation from people who actually know the metal, and walk out paid the same day.
```

**2. BrandIG — 2026-08-22T11:00 — image**

```
We buy gold and silver at all five Valley Pawn stores — rings, coins, bars, sterling, even broken chains. Bring it in for a fair, no-pressure evaluation from people who actually know the metal, and walk out paid the same day.
```

**3. BrandTwitter — 2026-08-22T11:00 — image**

```
We buy gold and silver at all five Valley Pawn stores — rings, coins, bars, sterling, even broken chains. Bring it in for a fair, no-pressure evaluation from people who actually know the metal, and walk out paid the same day.
```

**4. Lexington — 2026-08-21T16:31 — image**

```
Pulsar 12,000-watt dual-fuel generator — $849.99 at Valley Pawn Lexington. That's more than $500 under the $1,399 retail. Serious backup power that runs on gas or propane. 30-day warranty, free layaway. 125 Walker St, Lexington.
```

**5. GBP_Lexington — 2026-08-21T16:30 — image**

```
Pulsar 12,000-watt dual-fuel generator — $849.99 at Valley Pawn Lexington. That's more than $500 under the $1,399 retail. Serious backup power that runs on gas or propane. 30-day warranty, free layaway. 125 Walker St, Lexington.
```

**6. Culpeper — 2026-08-21T16:17 — image**

```
Husqvarna 585 chainsaw — $1,149 at Valley Pawn Culpeper. This saw runs $1,539.99 new. Professional-grade power, durability, and performance — big tools for big jobs. 30-day warranty, free layaway. 571 James Madison Hwy, Culpeper.
```

**7. GBP_Culpeper — 2026-08-21T16:15 — image**

```
Husqvarna 585 chainsaw — $1,149 at Valley Pawn Culpeper. This saw runs $1,539.99 new. Professional-grade power, durability, and performance — big tools for big jobs. 30-day warranty, free layaway. 571 James Madison Hwy, Culpeper.
```

**8. Roanoke — 2026-08-21T16:03 — image**

```
Samsung T5 EVO 4TB portable SSD, sealed in the box — $399.99 at Valley Pawn Roanoke. Four terabytes that fit in your pocket. 30-day warranty like everything we sell. Grab it before it's gone. 2362 Peters Creek Rd Suite C, Roanoke.
```

**9. GBP_Roanoke — 2026-08-21T16:00 — image**

```
Samsung T5 EVO 4TB portable SSD, sealed in the box — $399.99 at Valley Pawn Roanoke. Four terabytes that fit in your pocket. 30-day warranty like everything we sell. Grab it before it's gone. 2362 Peters Creek Rd Suite C, Roanoke.
```

**10. Harrisonburg — 2026-08-21T15:47 — image**

```
Apple iMac (A3137) with Bluetooth keyboard, like-new condition — now $849.94 at Valley Pawn Harrisonburg, marked down from $949.94. It'll run anything you need it to. 30-day warranty, free layaway. 1790 E Market St STE 22, Harrisonburg.
```

**11. GBP_Harrisonburg — 2026-08-21T15:45 — image**

```
Apple iMac (A3137) with Bluetooth keyboard, like-new condition — now $849.94 at Valley Pawn Harrisonburg, marked down from $949.94. It'll run anything you need it to. 30-day warranty, free layaway. 1790 E Market St STE 22, Harrisonburg.
```

**12. Waynesboro — 2026-08-21T15:33 — image**

```
Cornwell 4-drawer rolling tool cart with keys — $399.99 at Valley Pawn Waynesboro. These don't come up for sale often, and this one's priced to move. 30-day warranty like everything we sell, and layaway is free. 1321 W Broad St, Waynesboro.
```

**13. GBP_Waynesboro — 2026-08-21T15:30 — image**

```
Cornwell 4-drawer rolling tool cart with keys — $399.99 at Valley Pawn Waynesboro. These don't come up for sale often, and this one's priced to move. 30-day warranty like everything we sell, and layaway is free. 1321 W Broad St, Waynesboro.
```

**14. BrandBlog — 2026-08-21T09:10 — article**

```
Selling Gold: What Really Determines Your Payout
```

**15. Brand — 2026-08-20T13:02 — image**

```
Layaway is free at Valley Pawn. Found something you want but can't grab it all at once? Put a little down, pay it off on your own schedule, and take it home when it's yours. No holding fees, five stores across the Valley.
```

**16. BrandIG — 2026-08-20T13:01 — image**

```
Layaway is free at Valley Pawn. Found something you want but can't grab it all at once? Put a little down, pay it off on your own schedule, and take it home when it's yours. No holding fees, five stores across the Valley.
```

**17. BrandTwitter — 2026-08-20T13:01 — image**

```
Layaway is free at Valley Pawn. Found something you want but can't grab it all at once? Put a little down, pay it off on your own schedule, and take it home when it's yours. No holding fees, five stores across the Valley.
```

**18. Culpeper — 2026-08-19T07:00 — image**

```
(no text)
```

**19. Brand — 2026-08-18T10:01 — image**

```
Buy something from Valley Pawn and it's covered by a 30-day warranty — every item, every one of our five Shenandoah Valley stores. If it doesn't work right, bring it back. Family-owned, and we stand behind what we sell. What's Right Is Right.
```

**20. BrandIG — 2026-08-18T10:01 — image**

```
Buy something from Valley Pawn and it's covered by a 30-day warranty — every item, every one of our five Shenandoah Valley stores. If it doesn't work right, bring it back. Family-owned, and we stand behind what we sell. What's Right Is Right.
```

**21. BrandTwitter — 2026-08-18T10:01 — image**

```
Buy something from Valley Pawn and it's covered by a 30-day warranty — every item, every one of our five Shenandoah Valley stores. If it doesn't work right, bring it back. Family-owned, and we stand behind what we sell. What's Right Is Right.
```

**22. Culpeper — 2026-08-14T09:00 — image**

```
(no text)
```

**23. Culpeper — 2026-08-12T11:00 — image**

```
(no text)
```

**24. Brand — 2026-08-11T10:00 — text**

```
We buy gold and silver at all 5 Valley Pawn locations -- coins, bars, scrap, broken chains, class rings, whatever's in the drawer. We pay against real-time market spot, weighed and priced in front of you at the counter. No appointment needed, walk in during store hours.
```

**25. BrandTwitter — 2026-08-11T10:00 — text**

```
We buy gold and silver at all 5 Valley Pawn locations -- coins, bars, scrap, broken chains, class rings, whatever's in the drawer. We pay against real-time market spot, weighed and priced in front of you at the counter. No appointment needed, walk in during store hours.
```

### Near-duplicate caption analysis

- Posts carrying ANY caption text: **302** of 554. **252** posts published with no caption at all (mostly image-only posts Publer synced from Facebook).
- Distinct caption strings among those 302 posts with text: **141**
- Caption strings used MORE THAN ONCE: **68**
- Posts that reuse a caption verbatim with another post: **229**

Top reused captions:

| Times used | Accounts | Caption (first 120 chars) |
|---:|---|---|
| 21 | BrandIG, Culpeper, Lexington, Roanoke, Waynesboro | Valley Pawn’s End of Month Blowout Sale is happening NOW! 🔥 ⏎  ⏎ See something you like, but not the price? Make us a CA |
| 15 | Culpeper, Roanoke, Waynesboro | ✨ June Birthstones: Pearl • Alexandrite • Moonstone ✨ ⏎  ⏎ June is one of only three months with three official birthsto |
| 12 | Brand, Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro | There's $100 on the table every month — and it could be yours. 💵 ⏎  ⏎ One customer wins $100 each month, drawn on the la |
| 10 | BrandIG, Culpeper, Lexington, Roanoke, Waynesboro | 💥 PAY IN CASH this Memorial Day and SAVE UP TO 30% STOREWIDE! 💥 ⏎  ⏎ Tools 🔧 Jewelry 💎 PS5 🎮 Xbox 🎮 Laptops 💻 and so muc |
| 6 | BrandIG, BrandTwitter, Culpeper, GBP_Culpeper | The brick storefronts on Davis Street have watched Culpeper grow for a century and a half. Between the depot, the restau |
| 5 | BrandIG, BrandTwitter, GBP_Lexington, Lexington | Before the shops open and the VMI cadets are out marching, Walker Street is just brick sidewalks, quiet storefronts, and |
| 5 | BrandIG, BrandTwitter, GBP_Waynesboro, Waynesboro | Clean condition, full smartwatch feature set, ready for a new wrist. No price set yet — call or stop by and ask for it b |
| 5 | GBP_Culpeper, GBP_Harrisonburg, GBP_Lexington, GBP_Roanoke, GBP_Waynesboro | Every month we give away $100 to one Valley Pawn customer. Entering is quick and free — just visit thevalleypawn.com/fol |
| 5 | GBP_Culpeper, GBP_Harrisonburg, GBP_Lexington, GBP_Roanoke, GBP_Waynesboro | Every month we give away $100 to one Valley Pawn customer. Entering is quick and free — just visit https://thevalleypawn |
| 4 | Brand | A Martin D-28 doesn't just sit on a wall. It waits. ⏎  ⏎ We buy and sell instruments at Valley Pawn — and we know what t |
| 4 | Brand | Estate jewelry carries history. We carry it forward. ⏎  ⏎ Valley Pawn buys and sells fine jewelry — rings, necklaces, br |
| 4 | BrandIG, BrandTwitter, Culpeper, GBP_Culpeper | One of our Culpeper team's own picks: a John Hardy sterling silver pendant, priced at $199.99. Designer jewelry like thi |
| 4 | BrandIG, BrandTwitter, GBP_Roanoke, Roanoke | Roanoke has a Klein Tools 3-piece ModBox rolling tool set priced at $229.99 - stackable, latched, built for moving gear  |
| 4 | BrandIG, BrandTwitter, GBP_Waynesboro, Waynesboro | Waynesboro has a fiber optic outdoor Coca-Cola bottle decoration priced at $149.99 - a good head start on holiday lawn d |
| 3 | Brand | Every diamond has a story. Ours starts with a fair offer. ⏎  ⏎ We buy jewelry every day at Valley Pawn — no appointment  |
| 3 | Brand | Gold doesn't lie. Neither do our prices. ⏎  ⏎ Valley Pawn pays top dollar for gold, silver, and precious metals — every  |
| 3 | Brand, BrandIG | Skyline Drive has 75 overlooks between Front Royal and Rockfish Gap, and on a clear July morning half of them look like  |
| 3 | BrandIG, GBP_Harrisonburg, Harrisonburg | Tested and working, no price set yet since it's brand new to the shelf. Call about it before it's priced and gone. 📍 179 |
| 3 | BrandIG, GBP_Roanoke, Roanoke | 10K white gold, 60 diamonds, 1.27 total carat weight. No price set yet — ask for it by the diamond ring at the counter.  |
| 3 | BrandIG, Culpeper, GBP_Culpeper | Sandi Cole and Bree run the counter at our Culpeper store. Both appraise gold, jewelry, tools, and everything else that  |

Most repeated opening 5 words (voice-repetitiveness signal):

| Count | Opening |
|---:|---|
| 21 | Valley Pawn’s End of Month |
| 15 | ✨ June Birthstones: Pearl • |
| 12 | A Martin D-28 doesn't just |
| 12 | Estate jewelry carries history. We |
| 12 | There's $100 on the table |
| 10 | 💥 PAY IN CASH this |
| 10 | Every month we give away |
| 8 | Every diamond has a story. |
| 8 | We buy gold and silver |
| 7 | Gold doesn't lie. Neither do |
| 6 | Some items just walk in |
| 6 | The brick storefronts on Davis |
| 5 | Before the shops open and |
| 5 | Clean condition, full smartwatch feature |
| 5 | Valley Pawn is hiring in |
