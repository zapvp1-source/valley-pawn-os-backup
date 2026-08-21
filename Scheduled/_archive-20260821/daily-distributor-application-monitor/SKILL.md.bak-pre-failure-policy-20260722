---
name: daily-distributor-application-monitor
description: Daily 8am monitor of Joshua's Gmail for replies/bounces from 14 firearms distributor & manufacturer dealer applications, posting status summary to Slack DM.
---

OBJECTIVE
Check Joshua Davis's Gmail (jdavis@fcfpawn.com) for replies, bounces, or follow-ups related to the 14 firearms wholesale distributor and manufacturer dealer-account applications he sent on May 4, 2026, then post a status summary as a Slack DM to Joshua.

VENDORS BEING TRACKED (and email domains to watch for inbound replies)
1. RSR Group — @rsrgroup.com (applied to sales@rsrgroup.com)
2. Sports South — @sportssouth.biz, @theshootingwarehouse.com (applied to ffl@sportssouth.biz)
3. Davidson's — @davidsonsinc.com (applied to salesinfo@davidsonsinc.com, cc forguns@davidsonsinc.com — including GalleryOfGuns enrollment)
4. Lipsey's — @lipseys.com (existing wholesale account — flag any account-status emails)
5. Bill Hicks & Co — @billhicksco.com (applied to application@billhicksco.com)
6. Zanders Sporting Goods — @gzanders.com (applied to info@gzanders.com — best-guess address, watch for bounce)
7. Chattanooga Shooting Supplies — @chattanoogashooting.com (applied to info@chattanoogashooting.com — best-guess, watch for bounce)
8. Crow Shooting Supply — @crowwholesale.com, @crowshootingsupply.com (applied to info@crowwholesale.com — best-guess, watch for bounce)
9. Camfour — @camfour.com (applied to info@camfour.com — best-guess, watch for bounce)
10. MGE Wholesale — @mgewholesale.com (applied to info@mgewholesale.com)
11. Brownells — @brownells.com (specialty: gunsmithing parts/accessories)
12. Numrich Gun Parts Corp — @gunpartscorp.com, @numrichgunparts.com (specialty: parts for old/discontinued firearms)
13. Vortex Optics — @vortexoptics.com (specialty: optics dealer program)
14. Henry Repeating Arms — @henryusa.com (manufacturer-direct dealer program)

PROCESS — execute these steps in order:

1. Use the Gmail MCP `search_threads` tool with this query to find vendor replies in the past 26 hours:
   `from:(@rsrgroup.com OR @sportssouth.biz OR @theshootingwarehouse.com OR @davidsonsinc.com OR @lipseys.com OR @billhicksco.com OR @gzanders.com OR @chattanoogashooting.com OR @crowwholesale.com OR @crowshootingsupply.com OR @camfour.com OR @mgewholesale.com OR @brownells.com OR @gunpartscorp.com OR @numrichgunparts.com OR @vortexoptics.com OR @henryusa.com) newer_than:1d`

2. For each thread found, use `get_thread` to read the full message content. Identify:
   - Which vendor it's from
   - What they're asking for (formal application form to fill, signed FFL copies, signed W-9, storefront photos, banking documentation, additional licenses, account approval, etc.)
   - Whether action is required from Joshua, and how urgent

3. Run a second Gmail search for bounce-back / undelivered notices in the past 26 hours:
   `(from:mailer-daemon OR from:postmaster OR subject:"Delivery Status Notification" OR subject:"Undelivered Mail" OR subject:"failure notice") newer_than:1d`
   For each bounce, identify which vendor and recommend the phone fallback:
   - Zanders Sporting Goods: 618-443-2400
   - Chattanooga Shooting Supplies: (423) 894-3007
   - Crow Shooting Supply: 800-264-2493
   - Camfour: (800) 347-3276
   - Bill Hicks & Co: (800) 223-0702
   - MGE Wholesale: (800) 734-5965
   - RSR Group: (800) 444-8888
   - Sports South: (800) 388-3845
   - Davidson's: 1-800-367-4867
   - Brownells: 800-741-0015
   - Numrich Gun Parts: 866-686-7424
   - Vortex Optics: 1-800-426-0048
   - Henry Repeating Arms: (866) 200-2354

4. Use the Slack MCP `slack_send_message` tool to DM Joshua (channel_id = his user_id, U03BB52MDSA) with this format:

   📋 Daily Distributor Application Status — [DATE]

   *✅ New Replies ([N]):*
   • [Vendor] — [Brief description of what they sent / what they're asking for]
       _Action: [What Joshua needs to do, or "no action — just FYI"]_

   *⚠️ Bounces ([N]):*
   • [Vendor] — [original recipient address] failed to deliver
       _Recommend: call [phone number] or try alternative email_

   *⏳ Still Pending ([N] of 14):*
   [Comma-separated list of vendor names with no reply yet]

   If nothing new in 24 hours, post a much shorter message:
   "📋 Daily Distributor Monitor — All [N] applications still pending, no new replies or bounces."

BACKGROUND CONTEXT (for understanding what each reply might be asking for)
- Sender: Joshua Davis, CEO, Full Circle Finance Inc DBA Valley Pawn (5 Virginia FFL pawn locations: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke)
- Each cover letter included: EIN 47-1198118, VA Sales Tax # 10-471198118F-001, all 5 FFL numbers, Lipsey's as the only existing trade reference, Wells Fargo Waynesboro as bank reference
- Storefront photos referenced at https://thevalleypawn.com/locations
- Articles of Incorporation available in Joshua's Drive at: Full Circle Finance / Executive / Corporate Filings / Articles of Incorp
- W-9 needs to be signed by Joshua when a distributor specifically requests it (he hasn't pre-signed one yet)
- 4 of the 14 vendors were sent to best-guess `info@` addresses: Zanders, Chattanooga, Crow, Camfour. Higher bounce risk on those four.
- Virginia SB749 / HB217 takes effect July 1, 2026 — bans "assault firearms" sales. Some distributor inventory categories will be restricted in VA from that date forward. Joshua may receive vendor communications about this; flag any such emails specifically.

If any vendor reply requires Joshua to upload/sign documents (W-9, FFL PDF, application form), mark that line "🔴 ACTION REQUIRED" so it's visually obvious in the Slack DM.

If any thread is a substantive back-and-forth (more than just an auto-reply), include a one-sentence summary of the latest message in the Slack DM.

NEVER take destructive action on Joshua's email — no archiving, no marking as read, no replying. This task is observe-and-report only.