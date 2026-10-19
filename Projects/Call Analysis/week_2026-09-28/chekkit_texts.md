# Chekkit Text Audit: Valley Pawn, Mon 9/28 to Sun 10/18/2026 (Eastern)

Pulled 2026-10-18 (Sunday afternoon). This was a read-only pull. Nothing was sent, closed, assigned, tagged or changed in Chekkit.

## Method
- **Data source:** the dashboard's own conversation-list call (`POST chat.chekkit.io/api/webchat/customer-conversations`, `previewOnly:false`, which returns full threads). It was run under each location's session, covering both the Open and Closed lists. Paging continued until the latest-message date was before 9/28 04:00 UTC. Conversations were never opened in the UI, so the Lexington freeze issue did not come up.
- **Conversations fetched:** Lexington 321, Harrisonburg 480, Culpeper 520, Roanoke 1,600 (80 still open), Waynesboro 482. Only messages dated 9/28 00:00 to 10/18 23:59 EDT are counted.
- **Weeks:** wk1 is 9/28–10/4, wk2 is 10/5–10/11, wk3 is 10/12–10/18.
- **Customer** means an inbound SMS or webchat message. Facebook Messenger is excluded from the text counts and reported separately.
- **Automated** means any of the following: a Chekkit automation or review-request flag; no staff user; sent from the owner account (Joshua Davis), which carries the campaigns and AI auto-replies; a missed-call, STOP-footer or campaign template; or a message matching a scheduled-message event.
- **Human** means every other staff-sent SMS. This includes proactive outreach such as late-loan notices, not only replies.
- **Unanswered (raw):** customer messages with no later staff message in that thread. Every message counts, including photos, "thanks", "ok" and STOP. The substantive ones are listed below.
- **Median first reply:** for each conversation-week, the clock-time minutes from the first customer text to the first staff text after it. It does not adjust for business hours. *n* is the number of conversation-weeks that got a reply.

## Store × week summary (SMS/webchat)

| Store | Wk | Convs w/ customer msg | Inbound msgs | Human staff msgs | Automated msgs | Unanswered (raw) | Median 1st human reply (n) |
|---|---|---|---|---|---|---|---|
| Culpeper | 1 | 28 | 103 | 51 | 371 | 16 | 23 min (17) |
| Culpeper | 2 | 14 | 47 | 24 | 92 | 7 | 3 min (9) |
| Culpeper | 3 | 11 | 44 | 24 | 83 | 11 | 2 min (7) |
| Harrisonburg | 1 | 37 | 142 | 52 | 369 | 27 | 90 min (24) |
| Harrisonburg | 2 | 25 | 139 | 38 | 78 | 42 | 61 min (14) |
| Harrisonburg | 3 | 14 | 83 | 34 | 79 | 8 | 36 min (11) |
| Roanoke | 1 | 15 | 28 | 19 | 485 | 9 | 5 min (6) |
| Roanoke | 2 | 21 | 55 | 27 | 1,089 | 15 | 2 min (9) |
| Roanoke | 3 | 10 | 27 | 15 | 66 | 3 | 105 min (8) |
| Waynesboro | 1 | 28 | 129 | 34 | 346 | 25 | 16 min (15) |
| Waynesboro | 2 | 21 | 93 | 31 | 43 | 20 | 116 min (15) |
| Waynesboro | 3 | 28 | 157 | 54 | 53 | 29 | 28 min (22) |
| Lexington | 1 | 10 | 22 | 23 | 221 | 6 | 4 min (7) |
| Lexington | 2 | 7 | 16 | 12 | 36 | 1 | 6 min (7) |
| Lexington | 3 | 10 | 34 | 23 | 45 | 4 | 5 min (7) |

### Automated messages by type (missed-call / AI auto-reply / review request / campaign)

| Store | wk1 | wk2 | wk3 |
|---|---|---|---|
| Culpeper | 8 / 15 / 0 / 348 | 13 / 6 / 36 / 37 | 19 / 7 / 28 / 29 |
| Harrisonburg | 34 / 18 / 0 / 317 | 27 / 11 / 21 / 19 | 26 / 7 / 22 / 24 |
| Roanoke | 28 / 1 / 0 / 456 | 12 / 6 / 30 / 1,041 | 20 / 5 / 30 / 11 |
| Waynesboro | 27 / 11 / 0 / 308 | 15 / 8 / 13 / 7 | 15 / 17 / 15 / 6 |
| Lexington | 23 / 5 / 0 / 193 | 21 / 5 / 8 / 2 | 13 / 6 / 14 / 12 |

- **Campaigns in the window:**
  - 10/1 "Pawn loans are different" blast to all stores, with smaller re-sends on 10/8 and 10/15.
  - 9/30 owner "75-day past due" notice.
  - Roanoke 10/6 "now open Wednesdays / new hours" blast: about 1,032 messages.
  - Second "thanks again for visiting… leave a few kind words" review request on 10/9 and 10/16 (reviw.me link) at Culpeper and Harrisonburg.
- **STOP / opt-outs (SMS):**

| Store | wk1 | wk2 | wk3 |
|---|---|---|---|
| Culpeper | 8 | 2 | 1 |
| Harrisonburg | 10 | 3 | 1 |
| Roanoke | 9 | 9 | 2 |
| Waynesboro | 9 | 1 | 1 |
| Lexington | 3 | 0 | 1 |

  Total: 60. Almost all came in reply to the 10/1 campaign and the Roanoke 10/6 hours blast. One Waynesboro customer texted STOP and then START on 10/1.
- **Facebook Messenger (excluded from table), customer messages / staff replies:**
  - Lexington: wk2 2/0, wk3 16/12
  - Culpeper: wk1 3/0, wk2 1/0, wk3 5/3
  - Waynesboro: wk2 2/0, wk3 3/2
- **Staff seen:**
  - Culpeper: Sandi Cole, Robert Swagger
  - Harrisonburg: Walker Tapley, Preston Peters
  - Roanoke: Benji Moore, Joseph Epperly
  - Waynesboro: Chadd Mcclintic
  - Lexington: Uriah Tiglao

## October month-to-date Messenger Analytics (as shown 10/18)

| Store | New convs SMS / Textchat / FB | Assigned | Open / Closed / Total | Outgoing / Incoming msgs | Avg initial human response | Avg all replies | Textchat leads |
|---|---|---|---|---|---|---|---|
| Culpeper | 170 / 4 / 3 | Robert Swagger 12, Sandi Cole 6 | 0 / 177 / 177 | 608 / 141 | 14m 42s | 347h 3m | 4 |
| Harrisonburg | 176 / 4 / 0 | Walker Tapley 21, Preston Peters 2 | 0 / 180 / 180 | 605 / 328 | 52m 49s | 127h 46m | 4 (3 home, 1 /ffl-transfer) |
| Roanoke | 224 / 5 / 0 | Benji Moore 10, Joseph Epperly 2 | 13 / 216 / 229 | 1,679 / 107 | 5m 4s | 33h 35m | 5 |
| Waynesboro | 155 / 6 / 2 | Chadd Mcclintic 26 | 2 / 161 / 163 | 523 / 332 | 15m 30s | 224h | 8 |
| Lexington | 103 / 0 / 1 | Uriah Tiglao 10 | 1 / 103 / 104 | 343 / 82 | 2m 19s | 127h 8m | 1 |

Email, Google Business Messages, Instagram, Google Ads and Forms were 0 for all stores.

## Concerning items

### Wrong information sent to customers
- **Waynesboro, 10/14** (first day open Wednesdays): 8 messages still said closed Wednesdays (7 missed-call texts plus 1 AI auto-reply).
  - The AI told Anthony: "The hours I have show us closed on Wednesdays, and we're closed right now… open tomorrow."
  - Chadd corrected it about an hour later ("we are open!").
  - Messages were correct from 10/16 on.
- **Roanoke, 9/30 and 10/1:** 11 missed-call texts (8 on 9/30, 3 on 10/1) listed hours as Mon/Tue/Thu/Fri/Sat, implying closed Wednesday, after Wednesday opening started 9/30. Correct from 10/3 on.
- **Harrisonburg, 10/9 (19) and 10/16 (17):** 36 review requests said "thanks again for visiting **Dixie Pawn Inc.**". This is the old name, with a reviw.me link. Culpeper's version of the same campaign uses the correct name.
- **Waynesboro, 10/2:** Phillip has late pawns and will pay next Thursday. Chadd: "They will still be here they'll just be late." This was the day before the 10/3 75-day deadline.
- **Culpeper, 9/29:** Alfredo asked whether the store is transferring ARs covered by the VA assault-weapons law while the injunction is in place. Sandi: "We are. $25 transfer fee." That is a legal/compliance answer given by text.

### Loan or account details by text without verification, and account changes by text
- **Lexington, 10/1, Devonte:**
  - The AI said it couldn't give loan totals by text.
  - Uriah then texted "total of $555".
- **Lexington, 10/8, rifle (30-06) in pawn:** Uriah asked "is this the number under the account?" and then gave $192.50 pickup and 18 days late.
- **Lexington outbound notices with amounts and ticket numbers:**
  - Chasity, 9/26 and 10/2: $528.25 / $288.25.
  - Chasity, 10/17: tickets FT-VA1026891-01/-02, 73 days.
  - Amanda, 10/1: $307.50 / $173.50. She paid online.
- **Lexington, 10/15, Chestine:** "I will note your account" for a 10/22 payment.
- **Harrisonburg, 10/2, Angela:** she gave her account phone number. Walker: "Your items have sold :(".
- **Harrisonburg, 10/1, David:** Walker gave late status ("still late… within the 75 day rule").
- **Harrisonburg, 10/10–10/17, Donna (third party):**
  - She says her daughter pawned a laptop and PS5 that were not hers, without permission.
  - Preston correctly required the ticket or the daughter.
  - Walker later texted Donna the cost, $99.94, and a layaway was arranged.
  - Ownership claim, and account information given to a non-borrower.
- **Culpeper, 10/2:** Sandi gave due dates and $52.17 due to an unverified texter, and noted the account for 10/10.
- **Culpeper, 10/2, Elaine:** amount due $8.80, account noted.
- **Culpeper, 10/1, Sterlina:** "your loan went to default on 9/18/26".
- **Roanoke, 10/1 and 10/5, Melissa (pawned handgun):**
  - Benji: "No one made any payments. It has been put out for sale", then $367.50 to pick up.
  - Joseph: $140.50 to re-pawn.
- **Roanoke, 10/6, Jamal ("MY NAME IS NOT WAYNE"):** Benji: "We have removed your phone number from our system". Account change by text, curt.
- **Roanoke, 10/15–17, Virginia** (hospital): note placed for a late payment.
- **Waynesboro, 10/15, Brittany** (hardship): Chadd extended to the 31st by text.

### Specific firearm details or offers by text
- **Lexington:**
  - 10/3, Thomas: the AI said firearms can't be discussed by text. Uriah then listed a Mosin Nagant $399.99, Uberti 1873 $999.99 and Savage Axis 308 $359.99.
  - 9/28, Shy: Springfield Echelon handgun, "$240 range".
  - 10/17, Emma (FB): Savage 110 .300 Win Mag, "$175–$225".
- **Harrisonburg:**
  - 10/12, John: pistol, Walker "about $375".
  - 10/6: muzzleloader photos and prices.
- **Culpeper, 9/28, Randolph:** shotgun about $200.
- **Roanoke, 10/1:** handgun loan amounts (Melissa, above).

### Stolen property and police
- **Harrisonburg, 10/2, Maria:** looking for her "Saddlebred ring", asked whether "Officer Specor" had come in. Walker: "No he didn't."
- **Harrisonburg, 10/10, Donna:** says items were pawned without the owner's permission (above).
- **Waynesboro, 9/29:** a customer reported scammers spoofing the store number as "Verizon wireless". Chadd: "Everyone wants to be us I guess haha."

### Store low on cash (told to customers)
- **Waynesboro, 10/12, 5:50 pm:** to a loan customer 5 minutes away: "We don't have enough cash to do this loan today."
- **Lexington, 10/17:**
  - Duane asked whether the money had come in: "Not yet buddy". Uriah then offered "about $70".
  - Emma (FB): "running low on cash right now".

### Casual or unprofessional
- Lexington, 10/17: "Not yet buddy".
- Harrisonburg (Walker): "😂", "<3" and "Oh, hi Josh" (to the owner test), "Your items have sold :(".
- Roanoke, 10/1 (Benji): "We will be wanting" (typo for waiting).
- Waynesboro, 9/28 (Chadd): "We aren't trained for much else".
- **Possible shared logins at Culpeper** (the account and the signed name don't match):
  - 10/15, from Robert Swagger's account: "This is Joshua with Valley Pawn".
  - 10/14, from Robert Swagger's account: "Sandi here".

### Complaints and odd conversations
- **Culpeper, 10/14–15, Jacob:** bought an Xbox on Buya. Robert relisted it on eBay "with accurate pictures". Implies a listing or photo problem.
- **Lexington, 10/5, John:** item bought Saturday doesn't work. Told to come in.
- **Roanoke, 10/7, Thomas:** pressure-washer offer of $70–90 called "desperation selling". Declined.
- **Waynesboro, 10/6–7:** a customer asked "What did I buy yesterday / Did I buy sell anything there". No staff reply.
- **Waynesboro, 10/10, Max:** "It belonged to someone else. I got it at a garage sale" (Super Nintendo). No further staff reply.
- **Owner and vendor test conversations included in the counts:**
  - "Joshua Davis …4221" at every store (9/29 "Are you open", 10/1 watches).
  - "Chekkit Support" test at Culpeper on 10/1.
- **Vendor solicitations:** Lexington 9/29 (MobileWala), Harrisonburg 10/7 (SAS American Logistics).

### Substantive customer messages with no human reply (as of 10/18 afternoon)
- **Harrisonburg:**
  - 10/7 Feni: the app doesn't show her loan, so she can't pay. Never answered.
  - 10/7 Melissa: extension request. Only the AI replied.
  - 10/9 Leila: PS5 quote request.
  - 10/8: scope offer.
  - 10/5: private firearm transfer question. Only the AI replied.
  - 10/2 Richard: Nintendo Switch 2.
  - 9/29: sports cards.
  - 10/10: new shoes, photos sent.
  - 10/10 Rebecca/Timothy: final $40 counter on figures, wanted to recover a hard drive.
  - 10/16: photos.
- **Waynesboro:**
  - 10/16 Cortney: wants to sell.
  - 10/16 David: JBL PartyBox.
  - 10/13: item at $60.
  - 10/13: AirPods counter.
  - 10/10 Max: "How much would I get".
  - 10/9 Jermaine: .45 ACP. Only the AI replied.
  - 10/6: air compressor ("???").
  - 10/2: model-number photos.
  - 10/1 Taylee: photos.
  - 9/29 Renee: Gibson banjo.
  - Waiting for Monday: 10/17 Dell monitors, 10/18 William's 14k necklaces.
- **Culpeper:**
  - 10/7 Thomas: can't log into MobilePawn for a layaway.
  - 10/14 Hunter: cross pendant.
  - 10/10: monitors, amp, etc.
  - 10/1 Shawn: "What can I do about a loan?". Only the AI replied.
- **Roanoke:** 10/10 Renee asked for a break on a late payment and said the app shows a white screen. Only the AI replied and no staff follow-up was ever sent.
- **Lexington:**
  - 10/15 Bobby (website): "Looking for a small refrigerator". Assigned to Uriah, never replied.
  - 9/28 Shy: handgun thread dropped after the customer's answer.
  - 10/6 Damon (FB): shotgun question.
  - Waiting for Monday: 10/18 dragonfly pendant offer at $135.

## Notable outcomes (sample)
- **Culpeper:**
  - 10/17 Jeffrey: '02 Sequoia title loan declined (age and mileage; Robert, Sandi).
  - 10/15 Rachel: $120 offer accepted, selling.
  - 10/9: TV, tools and bike offers declined or below ask.
  - 10/12 Anneka: PS5 quoted $125–200.
  - 9/30 Ashley: generator quoted $150–175 loan / +$25 to sell.
- **Harrisonburg:**
  - 10/5 Lucion: PSA card bought for $60 (Walker).
  - 10/10 Aaron: tool trade agreed, coming in.
  - 10/16 Justin: $150 Xbox Series S / $50 TV offered.
  - Many turn-aways (subs, fish tank, fridge, jerseys).
- **Roanoke:**
  - 10/15 Darren: impact with battery, $100, coming in.
  - 10/1: crossbow $299.99, interested.
  - 10/8 Chris: bike, about $100 loan.
- **Waynesboro:**
  - 10/1 Sharon: Subaru collateral loan offered $800.
  - Shaper Origin CNC router, $800.
  - 10/12: loan of $150, then customer told to wait for cash (above).
  - Many turn-aways (Chadd).
- **Lexington:**
  - 10/17 Duane: Xbox loan about $70, coming at 5.
  - Water dispenser, dolls, weights, wood stove, safe ($20 vs $40) declined.
  - 10/1 Amanda: paid $173.50 online after outreach.

## Coverage gaps and caveats
- **All five stores' SMS/webchat threads were covered** in full, Open and Closed, back to 9/28. No conversation was skipped and none froze, because threads were read from the list data rather than opened in the UI.
- **Facebook Messenger** is excluded from the table (counts given separately).
- **Automated vs human is rule-based.**
  - At Roanoke, about 4 staff-sounding quick replies with no staff user were counted as automated, for example "We can do $80 on it" and "We have a few what kind…".
  - At Culpeper, the FB FFL-pickup replies have no staff user and were counted as automated.
- **"Human staff msgs"** includes proactive outreach (late-loan notices at Culpeper and Lexington), not only replies.
- **Unanswered (raw)** counts every message, including STOP, thanks and photos. The substantive list above is judgment-based.
- **Medians** are clock time and are not adjusted for business hours. Chekkit's "Avg initial response" is business-hours based, so the two do not match.
- **Sunday 10/18 messages** are pending Monday follow-up.
- **The analytics panel** is October month-to-date only, through 10/18. It does not cover 9/28–9/30.
