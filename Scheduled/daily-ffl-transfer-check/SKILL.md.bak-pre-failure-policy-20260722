---
name: daily-ffl-transfer-check
description: Daily: scan jdavis Gmail for incoming FFL transfers, post digest to #ffl-transfer-notifications, and draft replies using the public, signed, content-verified FFL links on thevalleypawn.com.
model: claude-sonnet-5
---

Each day, check the jdavis@fcfpawn.com Gmail inbox for incoming federal firearms (FFL) transfer notifications from the last 24 hours, post a concise digest to Slack channel #ffl-transfer-notifications (channel ID C0BA6SXL8AK), and prepare reply DRAFTS (never auto-send) for any that need our address or FFL copy.

STEP 1 — Find transfers.
Search Gmail (server mcp__00007879-ef17-43e5-9d59-6325cd2f0a31, search_threads) with: (FFL OR firearm OR "inbound transfer" OR "transfer" OR "lower receiver" OR pistol OR rifle OR handgun OR "selected you") newer_than:1d in:inbox. Open promising threads with get_thread. Incoming transfers come from MANY different FFLs/sources, not one sender. Ignore reviews, marketing, VCDL alerts, payroll, etc.

STEP 2 — Post digest.
Post ONE concise message to #ffl-transfer-notifications, one line each: "From (shipping FFL/source) → Store · buyer · item · ref · date". If none, post "No new incoming FFL transfers in the last 24h."

STEP 3 — Decide which need a reply.
- GunBroker / MasterFFL "New Inbound FFL Transfer Confirmation" emails: NO reply needed — MasterFFL already acquires, validates, and delivers our FFL to the shipping dealer. Just include in the digest.
- Direct emails from a customer or dealer asking us to send our FFL copy and/or ship-to address (e.g. "please send a copy of FFL to ...", a dealer requesting our license): DRAFT a reply.
- Chekkit alerts (support@chekkit.io) where a customer selected a Valley Pawn store as their FFL ship-to: note in the digest that it needs a Chekkit reply / upload to the retailer's FFL portal — do NOT create a Gmail draft (no email thread to reply to).

STEP 4 — Draft replies (create_draft, do NOT send).
Determine the destination store, then put that store's address and a link to that store's signed FFL license in the draft. These links are the PUBLIC, signed, current copies hosted on our website (verified by license content, not filename) — they open for any external dealer, unlike the private Drive/Slack copies. Store → address → phone → FFL # → FFL link:
- Culpeper: 571 James Madison Highway, Culpeper, VA 22701 · (540) 445-5510 · FFL # 1-54-047-02-6J-25407 · https://thevalleypawn.com/wp-content/uploads/2026/06/culpeper-ffl.jpg
- Waynesboro: 1321 West Broad Street, Waynesboro, VA 22980 · (540) 221-6346 · FFL # 1-54-820-02-8B-24709 · https://thevalleypawn.com/wp-content/uploads/2026/06/waynesboro-ffl.jpg
- Harrisonburg: 1790 East Market Street, Harrisonburg, VA 22801 · (540) 574-4500 · FFL # 1-54-165-02-7M-26284 · https://thevalleypawn.com/wp-content/uploads/2026/06/harrisonburg-ffl.pdf
- Lexington: 125 Walker Street, Lexington, VA 24450 · (540) 461-8349 · FFL # 1-54-163-02-8F-26584 · https://thevalleypawn.com/wp-content/uploads/2026/06/lexington-ffl.jpg
- Roanoke: 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 · (540) 562-0776 · FFL # 1-54-770-02-7A-27330 · https://thevalleypawn.com/wp-content/uploads/2026/06/roanoke-ffl.jpg

All five signed FFL copies are also browsable on the public FFL Transfer page: https://thevalleypawn.com/ffl-transfer/ . If the destination store is unclear from the email, default to Roanoke for GunBroker-style transfers but flag the uncertainty in the digest. Sign drafts as Joshua Davis, Valley Pawn, jdavis@fcfpawn.com.

NOTE on Culpeper: its FFL expires September 1, 2026 — after that date, do not send the Culpeper copy until a renewed, signed copy replaces it on the website.

STEP 5 — Report.
In the same notification, list any drafts created (recipient + subject) so Joshua can review and send. Note that create_draft cannot attach files, so the FFL is shared via the website link in the body. Keep everything concise.