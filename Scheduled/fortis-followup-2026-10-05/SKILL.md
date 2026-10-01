---
name: fortis-followup-2026-10-05
description: RETIRED 9/30 — superseded by fortis-email-monitor.
---

Load the enterprise-map skill first, then vp-operating-rules and my-writing-style.

Context: On 2026-09-30 Joshua (jdavis@fcfpawn.com) sent Fortis (our card processor):
(A) to rep Corey Mantell (Corey.Mantell@fortispay.com), cc preston@fcfpawn.com, subject "Valley Pawn - contact update + Mobile Pawn lockout rule (Case #964DBD)".
(B) to customersupport@fortispay.com + premiersupport@fortispay.com, cc support@fortispay.com, Corey, Preston, subject "Valley Pawn - account contact update + Mobile Pawn lockout rule (Case #964DBD)", plus a same-thread reply adding item 4.
Asks: (1) update contact on all active MIDs to Joshua Davis / jdavis@fcfpawn.com / (804) 930-4221 and send portal + virtual terminal logins; (2) lock out any card-not-present transaction through the Mobile Pawn app after 3 failed attempts; (3) confirm Salem 6281340008385247 + Staunton 6281740007377542 MIDs closed (Case #4D8A8C); (4) activate the virtual terminal ("crash portal" — lets a store key a sale when its card machine is down) on all 5 MIDs, one user per store with the invite sent to that store's email, jdavis@fcfpawn.com as admin on all 5, and tell us which stores already had it plus the login URL.
Active MIDs / store emails: Waynesboro 6281740007377336 waynesboro@fcfpawn.com; Harrisonburg 6281740007609902 harrisonburg@fcfpawn.com; Culpeper 6281740007377484 culpeper@fcfpawn.com; Lexington 6281740007377567 lexington@fcfpawn.com; Roanoke 6281340008386351 roanoke@fcfpawn.com.

Steps:
1. Gmail connector (jdavis@fcfpawn.com): search `(from:fortispay.com OR from:fortis.support OR from:fluidpay OR 964DBD OR "virtual terminal") newer_than:6d`. Support replies often come from comm.XXXX@my.fortis.support with a "Ref ID" subject. Also check the unified-search index (mail corpus: "fortispay", "fluidpay", "fortis.tech") including the 5 store mailboxes, since login invites go to store emails and Corey may reply to zapvp1@me.com.
2. If Fortis replied or invites arrived: note which of the 4 items are done vs outstanding and which stores now have virtual terminal logins. If they ask for a form/signature or info only Joshua can give, do NOT sign anything — tell Joshua. Send ONE plain Slack DM to Joshua (D03BHQH5VGT), no jargon. Update the 2026-09-30 Fortis row in ~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md. Do not text or message store staff.
3. If NO reply from anyone: reply on thread (B), same recipients, in Joshua's voice, short, e.g. "Following up. No ticket number or reply yet. Need the contact update, the 3 attempt lockout on Mobile Pawn and virtual terminal logins for all 5 stores done this week. Joshua Davis (804) 930-4221". Update the register row to "follow-up sent 10/5". One plain Slack DM to Joshua: Fortis hasn't answered, nudge went out, and support takes calls at (855) 465-9999 option 1 (7a-11p ET, have a MID ready) if he wants to push by phone.
Never post failure notices to team channels.