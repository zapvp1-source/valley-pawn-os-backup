# MobilePawn App-Download Outreach (built 2026-09-29, Joshua: "go")

Goal: grow active MobilePawn (Bravo app) customers. Baseline Aug 2026 = 629 active vs ~3,462 loans (~18%). Target 25% by Mar 2027. Tracked monthly in #mobilepawn-participation.

| Channel | What | Where it lives |
|---|---|---|
| Link | thevalleypawn.com/app — WP page 1300, redirects iPhone → App Store (id1141399930), Android → Google Play (com.bravorevolution.instapawn); desktop shows both | `app_page.html` |
| Website | "Get the free app" banner on Home (page 7) + Loans (page 9), markers VP-APP-BANNER-START/END | backups `page7_home.bak-20260929.html`, `page9_loans.bak-20260929.html` |
| Email | App block in every monthly Shop Online email (first = Nov 2026) | `eBay Customer Campaign/build_month.py` `app_block()`, `config.json app_block_enabled=true` |
| Social | 2nd Tuesday 11 AM ET: Brand FB+IG, 5 store FB, 5 GBP via Publer | `monthly_post.py`, graphics/, task `mobilepawn-app-social-monthly` (20th 9:10 AM) |
| Text | Bravo (Tahoe Mack) free Klaviyo SMS to non-activated customers — asked 9/29 to make it monthly | Gmail thread "Free MobilePawn Marketing?" |
| In store | Mobile Pawn sign missing at HAR/WAY/ROA — part of the sign "full set" | `Valley Pawn OS/STORE_SIGN_SET.md` |

Rollback: banners → restore backups via wp_client; email → `app_block_enabled=false`; social → disable the task; link → set page 1300 to draft.

**Text fallback (Joshua 9/29: "we will do monthly if bravo doesnt"):** `eBay Customer Campaign/config.json app_sms_own`. When true, the monthly Chekkit text reads: "Valley Pawn: pay your loan from your phone w/ our free app thevalleypawn.com/app/?utm_source=sms Shop online thevalleypawn.com/shop Reply STOP to opt out" (153 chars). Decided automatically 10/22 by task `mobilepawn-bravo-reply-check`.
