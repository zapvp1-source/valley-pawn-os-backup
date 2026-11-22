# L3_L4 corrections — 2026-11-21 pass

Lessons changed: L3-01, L3-02, L3-03, L3-04, L3-05, L3-06, L3-07, L4-01, L4-02, L4-03, L4-04, L4-05, L4-06. Unchanged: L3-00, L4-00.
Every changed lesson has `CEO rulings 2026-11-21 (ACADEMY_FINAL_RULINGS)` added to `sources`. validate_lessons.py: 0 violations. check_answer_bias.py: 0 correct-strictly-longest.

Format: `json path`: old → new (long text truncated).


## L3-01

- `call_clip.caption`: keeps going until the customer can say it back → keeps going until the customer understands it
- `slides.1.say`: Say it plainly, then ask them to say it back to you. → Say it plainly, then check they got it.
- `slides.2.bullets.3`: Late fee — applies on the 6th day past due, up to 10% of the amount loaned, ONLY if it's printed on the ticket → Late fee — 5% of the loan principal, starting on the 6th day past due. It is NOT printed on the ticket
- `slides.2.bullets.4`: Plus a $5 lost-ticket fee, again only if it's on the ticket. Nothing else, ever → Plus a $5 lost-ticket fee, only if it's on the ticket. Nothing else, ever
- `slides.2.say`: The late fee applies on the sixth day past due, never sooner. There's also a five dollar lost ticket fee, and like the late fee, it's only legal if it's printed on the t… → Our late fee is five percent of the loan principal. It starts on the sixth day past due, never sooner, and it is not printed on the ticket. There's also a five dollar lo…
- `slides.4.bullets`: ["Day 0: loan written. Day 30: due", "The law's 15-day legal hold means nothing is sold before day 45 of the loan", "Our hold is longer: through 30 days past due. Day 31… → ["Day 0: loan written. Day 30: due", "Days 1 to 5 past due: the 5-day grace period. No late fee", "Day 6 past due: a late fee of 5% of the loan principal starts", "Then …
- `slides.4.say`: Now the timeline. The loan is written on day zero and it's due thirty days later. Virginia gives a fifteen day legal hold, so nothing can be sold before day forty five o… → Now the timeline. The loan is written on day zero and it's due thirty days later. After the due date there's a five day grace period. On the sixth day past due, a late f…
- `key_points.2`: Four charges only, each capped. Late fee (6th day past due) and lost-ticket fee only if they're on the ticket. Bravo computes; you never change a rate or fee → Four charges only, each capped. Late fee: 5% of principal from the 6th day past due, not printed on the ticket. Bravo computes; you never change a rate or fee
- `key_points.3`: Nothing is sold before day 45 of the loan. Our hold runs through 30 days past due; day 31 it can be pulled, done by day 61. First-payment defaults get no hold, so check … → Due on day 30. 5-day grace, then a late fee of 5% of principal from day 6 past due, then 10 more days before the loan expires. Read where a loan stands off Bravo
- `quiz.questions.2.options.1.text`: A late fee the customer was never told about on the ticket → A lost-ticket fee the customer was never told about on the ticket
- `quiz.questions.2.options.1.why`: A late fee is lawful only if the customer was told about it on the ticket. No notice on the ticket, no late fee. → The $5 lost-ticket fee applies only if the customer was told about it on the ticket. No notice on the ticket, no lost-ticket fee.
- `quiz.questions.4.prompt`: A customer is redeeming during the 15-day legal hold. → A customer is redeeming 8 days past due.
- `quiz.questions.4.options.1.why`: including during the legal hold → including the late fee
- `quiz.questions.5 (rewritten)`: A customer picks up on day 8 past due. Bravo adds a late fee. He says, 'Nobody told me about that.' What do you do? [correct: Show him the notice on his ticket and charg… → A customer picks up on day 8 past due. Bravo adds a late fee. He says, 'Nobody told me about that.' What do you do? [correct: Explain it starts on day 6 past due. Charge…
- `quiz.questions.6 (rewritten)`: A customer has extended his loan every month for a year. This time he's 16 days past due. A coworker says: 'The legal hold is 15 days. He's out, pull it.' What's right? … → A customer's loan is 8 days past due. A coworker says: 'He's past the grace period, so it's expired. Pull it.' What's right? [correct: Keep it on loan. The late fee has …
- `production_notes`: (loan day 0 → due date → +15 legal floor → +30 hold → day 31 pull → day 61) → (loan day 0 → due date → 5-day grace → late fee from day 6 past due → 10 more days → loan expires)

## L3-02

- `slides.1.bullets.3`: Photo of the customer AND the ID, every intake. Not optional → Image the ID on every intake. Not optional. We photograph the ID, not the person
- `slides.1.say`: Take a photo of the customer and a photo of the I D on every intake. That's not optional. → That image is not optional, on every intake. We photograph the I D, not the person.
- `key_points.1`: Unexpired government photo ID with the current address, recorded and imaged, plus a customer photo. Military ID is never imaged → Unexpired government photo ID with the current address, recorded and imaged. We photograph the ID, not the person. Military ID is never imaged
- `quiz.questions.4.prompt`: A customer is renewing a $1,200 loan. A coworker says, 'Reloans don't need the worksheet.' What's right? → A customer redeemed a $1,200 loan last week and wants a new $1,200 loan on the same item. A coworker says, 'Reloans don't need the worksheet.' What's right?
- `quiz.questions.4.options.1.text`: Only new customers and new money need it. A straight renewal of the same amount doesn't → Only new customers and new money need it. A reloan for the same amount as before doesn't
- `quiz.questions.4.options.1.why`: The threshold is the dollar amount ($1,000+), not whether the customer or the money is new. Reloans are included, without exception. → The threshold is the dollar amount ($1,000+), not whether the customer or the money is new. A reloan is a new loan, so it needs a new worksheet.
- `quiz.questions.4.options.2.why`: The worksheet applies to every loan or buy of $1,000 or more, including reloans, without exception. → A reloan is a new loan on the same item, so it needs a new worksheet at $1,000 or more. A renewal doesn't need one.

## L3-03

- `floor_check`: ID imaged (or the military-ID rule followed) and customer photographed. → ID imaged (or the military-ID rule followed). We photograph the ID, not the person.
- `floor_check`: Statement of ownership captured. → Statement of ownership in the signed ticket.
- `floor_check`: Ticket printed, initialled, signed, dated and fingerprinted. → Loan paid out in cash, no checks. Ticket printed, initialled, signed and dated (no fingerprint).
- `slides.1.bullets.3`: Cash or check → Save. The ticket prints → Cash only, no checks → Save. The ticket prints
- `slides.1.say`: Third, the payment. Cash or check, then Save, and the ticket prints. → Third, the payout. Loans are paid out in cash only, never by check. Then Save, and the ticket prints.
- `slides.3.heading`: The ID and the photos → The ID and its image
- `slides.3.bullets.2`: Photo of the customer too, every intake → We photograph the ID, not the person
- `slides.3.say`: Take the customer's photo too, every intake. → We photograph the I D, not the person.
- `slides.4.bullets.3`: Capture it at the counter, every time → It's part of the ticket the customer signs, not a separate form. Get the signature at the counter, every time
- `slides.4.say`: The statement of ownership is the field you can't fix later. → The statement of ownership is the one thing you can't fix later. It's part of the ticket the customer signs, not a separate form.
- `slides.4.say`: Get it at the counter, every single time. → Get that signature at the counter, every single time.
- `key_points.2`: Unexpired government photo ID, recorded and imaged, plus a customer photo. Never image a military ID → Unexpired government photo ID, recorded and imaged. We photograph the ID, not the person. Never image a military ID
- `key_points.3`: No statement of ownership = the item can never be sold → The statement of ownership is part of the signed ticket. Without it, the item can never be sold
- `key_points.4`: One loan per item. More money = redeem and rewrite → One loan per item. More money = redeem and rewrite. Loans are paid out in cash only
- `quiz.questions.1.prompt`: You're entering the statement of ownership and Bravo keeps rejecting the entry. The customer is getting impatient. What do you do? → You're entering the customer's ID number and Bravo keeps rejecting the entry. The customer is getting impatient. What do you do?
- `quiz.questions.1.options.1.text`: Finish the loan and flag it for your manager to add the statement later → Finish the loan and flag it for your manager to add the ID number later
- `quiz.questions.1.options.1.why`: Without a statement of ownership the item can never be lawfully sold. No ticket is completed with a required field blank. → The ID number is a required field, and no ticket is completed with a required field blank.
- `quiz.questions.5.prompt`: You notice there's no statement of ownership on file for it. → You notice the ticket was never signed, so there's no statement of ownership on file.
- `quiz.questions.5.options.2.text`: Hold it, and have the coworker who wrote it fill in the statement → Hold it, and have the coworker who wrote it sign the ticket now
- `quiz.questions.5.options.2.why`: The statement comes from the customer. An employee filling one in is a false record. → The statement of ownership is the customer's, in the ticket the customer signs. An employee signing for them is a false record.

## L3-04

- `floor_check`: The trainee points out the late-fee and $5 lost-ticket notices on the ticket and tells the customer to keep the ticket safe. → The trainee explains the late fee out loud (5% of the loan principal, starting on the 6th day past due; it is not printed on the ticket), points out the $5 lost-ticket n…
- `floor_check`: Ticket initialled, signed, dated and fingerprinted. → Ticket initialled, signed and dated (no fingerprint).
- `call_clip`: {"file": "clips/2026-09-05_LEX_call241_GOOD_LEX_pawn_explainer_to_title_loan_caller.m4a", "caption": "A caller asks about title loans and gets a clean pawn explainer, un… → null
- `production_notes`: Not a Bravo screen recording. The best replacement is a 2–3 min filmed counter role-play (manager as customer) with a close-up of a real printed ticket's disclosure box … → Not a Bravo screen recording. The best replacement is a 2–3 min filmed counter role-play (manager as customer) with a close-up of a real printed ticket's disclosure box …
- `slides.3.heading`: Point at the fees on the ticket → The late fee, the lost ticket, and who can pick up
- `slides.3.bullets`: ["Late fee: applies on the 6th day past due, up to 10% of the loan, only if it's printed on the ticket", "Lost ticket: $5, only if it's printed on the ticket", "Whoever … → ["Late fee: 5% of the loan principal, starting on the 6th day past due. It is NOT printed on the ticket, so say it out loud", "The timeline: a 5-day grace period, the la…
- `slides.3.say`: Show them the fee notices on the ticket. A late fee applies on the sixth day past due, and a lost or stolen ticket is five dollars. Both are only legal because they're p… → The late fee isn't printed on the ticket, so say it out loud. On the sixth day past due, a late fee of five percent of the loan principal starts. Behind that is our time…
- `slides.4.bullets.0`: Initialled, signed, dated and fingerprinted, every contract. No fingerprint, no contract — still refusing? Stop and ask your manager → Initialled, signed and dated, every contract. We don't take fingerprints
- `slides.4.say`: Every contract gets initialled, signed, dated and fingerprinted. → Every contract gets initialled, signed and dated. We don't take fingerprints.
- `key_points.3`: Late fee (6th day past due) and $5 lost-ticket fee: only because they're on the ticket. Point at them → Late fee: 5% of principal from the 6th day past due, after a 5-day grace; then 10 more days before the loan expires. It isn't printed on the ticket, so say it out loud
- `key_points.4`: Initialled, signed, dated, fingerprinted. Customer copy out, store copy filed → Initialled, signed, dated. No fingerprints. Customer copy out, store copy filed
- `quiz.questions.0.options.1.why`: Then initial, sign, date and fingerprint. → Then initial, sign and date.
- `quiz.questions.6 (rewritten)`: A new customer won't give a fingerprint: 'I'm not a criminal.' Everything else on the ticket is done. What do you do? [correct: Explain every contract is fingerprinted a… → A coworker closing a loan tells a new customer, 'The late fee's printed right there on your ticket. It's 10% the day after your due date.' What's accurate? [correct: 5% …
- `quiz.questions.7.options.1.why`: Those are on the ticket and were explained before he signed. The send-off is the four talking points. → Those were explained before he signed. The send-off is the four talking points.

## L3-05

- `floor_check`: take one extension (renewal) and one full redemption → take one renewal and one full redemption
- `floor_check`: Extension: Renewal → Current Loans → Renewal: Renewal → Current Loans
- `floor_check`: Save; one of the two redemption tickets handed to the customer and one filed in the redemption ticket box; every redeemed item → Save; every redeemed item
- `objectives`: take an extension and a redemption in Bravo → take a renewal and a redemption in Bravo
- `slides.0.bullets.2`: A third party can REDEEM with their own valid photo ID plus the ticket, but never a firearm or a vehicle title (Level 6 denied-pledgor exception only, with Market Manage… → A third party can REDEEM with their own valid photo ID plus the ticket, but never a firearm or a vehicle title. Only the account holder redeems a firearm
- `slides.0.say`: The one exception is the denied pledgor designation you'll learn in Level Six, with Market Manager approval every time. → Only the account holder redeems a firearm.
- `slides.1.heading`: The extension → The renewal
- `slides.1.bullets`: ["Customer pays the current charges, and gets a new 30-day loan on the same item", "Bravo: Renewal → find it on Current Loans → note a lost ticket if needed → select → p… → ["A renewal: the customer pays the current charges, and gets a new 30-day loan on the same item", "A renewal and an extension are two different options. Don't treat them…
- `slides.1.say`: An extension is the most common thing you'll do. In the manual it's called a refinance, and in Bravo it's Renewal. The customer pays the current charges and gets a fresh… → A renewal is the most common thing you'll do. The customer pays the current charges and gets a fresh thirty day loan on the same item. An extension is a different option…
- `slides.3.bullets`: ["Bravo: Redemption → find the item → note a lost ticket if needed → select → payment → Save", "Two redemption tickets print: one to the customer, one in the redemption … → ["Bravo: Redemption → find the item → note a lost ticket if needed → select → payment → Save", "Scan every redeemed item before the customer leaves", "The redemption amo…
- `slides.3.say`: Two redemption tickets print. One goes to the customer, and one goes in the redemption ticket box. → 
- `slides.3.say`: take the payment, and save. Scan → take the payment, and save. Scan
- `slides.3.say`: It needs a forty four seventy three, a State Police check and a gun lock. → It needs a forty four seventy three and a State Police check, and gun locks are offered with handguns only.
- `key_points.1`: Extension = Renewal in Bravo: current charges paid, new 30-day loan on the original amount, new due date said out loud → Renewal: current charges paid, new 30-day loan on the original amount, new due date said out loud. An extension is a different option
- `key_points.2`: Redemption: two tickets (customer and box), every item scanned before they leave, amount not negotiable → Redemption: every item scanned before they leave, amount not negotiable
- `key_points.5`: Firearm redemption is a transfer (4473, State Police check, gun lock). Level 6 only → Firearm redemption is a transfer (4473, State Police check; gun locks offered with handguns only). Level 6 only
- `quiz.questions.1.options.1.why`: The only exception is the denied-pledgor designation taught in Level 6, with Market Manager approval each time. → Only the account holder redeems a firearm.
- `quiz.questions.4 (rewritten)`: You've just saved a redemption in Bravo and two redemption tickets printed. Which of these still has to happen before the customer walks out? [correct: Scan each redeeme… → You've just saved a redemption in Bravo. Which of these still has to happen before the customer walks out? [correct: Scan every redeemed item before she leaves]

## L3-06

- `call_clip.caption`: One thing to fix: he describes the late fee from memory ('5% of the principal'). In our script you read the late fee off Bravo and the ticket. → One note: he gives the late fee as '5% of the principal'. That is our rule, but in our script you still read the amount off Bravo.
- `slides.1.bullets.3`: if Bravo shows it's inside our hold → if Bravo shows the loan hasn't expired
- `slides.1.say`: If Bravo shows it's inside our hold, say it plainly → If Bravo shows the loan hasn't expired, say it plainly
- `slides.2.bullets`: ["Nothing can be sold during the 15-day legal hold after the due date", "Our hold is longer: through 30 days past due", "Day 31 past due it can be pulled; the pull is fi… → ["After the due date: a 5-day grace period, with no late fee", "Day 6 past due: a late fee of 5% of the loan principal starts", "Then 10 more days before the loan expire…
- `slides.2.say`: So what does safe actually mean? After the due date there's a fifteen day legal hold, and nothing can be sold during it. Our hold goes further: we hold the item through … → So what does safe actually mean? After the due date there's a five day grace period, with no late fee. On the sixth day past due, a late fee of five percent of the loan …
- `key_points.1`: 15-day legal hold; our hold runs through 30 days past due; day 31 it can be pulled, done by day 61. Don't promise the hold on a first-payment default → 5-day grace, then a late fee of 5% of principal from day 6 past due, then 10 more days before the loan expires. Don't promise the hold on a first-payment default
- `quiz.questions.0.options.0.why`: That's answering from memory, and we never mention a grace period to a customer. The 15-day legal hold is the floor, and our hold runs to 30 days past due. → That's answering from memory, and we never mention a grace period to a customer. Read where the loan stands off Bravo.
- `quiz.questions.0.options.1.why`: Every fact comes from Bravo, the hold is our standing rule, and it ends → Every fact comes from Bravo, and it ends
- `quiz.questions.1 (rewritten)`: A verified customer asks, 'How much is the late fee?' You remember a coworker saying it's 5% of principal. What do you do? [correct: Read the amount off his account in B… → A verified customer who is 8 days past due asks, 'How much is the late fee?' What do you do? [correct: Read the amount off his account in Bravo]
- `quiz.questions.2 (rewritten)`: A verified customer who has extended every month for a year is now 20 days past due. He asks, 'Are you going to sell it tomorrow?' What's accurate? [correct: 'It's here … → A verified customer who has extended every month for a year is now 12 days past due. He asks, 'Are you going to sell it tomorrow?' What's accurate? [correct: 'It's here …
- `quiz.questions.7.options.0.why`: False and a threat. Day 31 is when an item becomes eligible to pull, not when it's gone, and threats about what we'll do are out. Read each loan's real standing from Bra… → False and a threat. Threats about what we'll do are out. Read each loan's real standing from Bravo.

## L3-07

- `slides.0.bullets.2`: Never confirm a firearm on the phone, to anyone → Once the account is fully verified, a firearm on a loan is discussed like any other loan item
- `slides.0.say`: , and you never confirm a firearm on the phone to anyone. Then pull it up → . Once the account is fully verified, a firearm on a loan is discussed like any other loan item. Then pull it up
- `key_points.0`: Never confirm a firearm by phone → Once verified, a firearm on a loan is discussed like any other item
- `quiz.questions.7.options`: [{"text": "True", "correct": false, "why": "We never confirm a firearm on the phone, to anyone, verified or not."}, {"text": "False", "correct": true, "why": "Never conf… → [{"text": "True", "correct": true, "why": "Once the account is fully verified, a firearm on a loan is discussed like any other loan item."}, {"text": "False", "correct":…

## L4-01

- `slides.1.bullets.2`: A buy: more cash today, and the item is ours. Same contract, signed, dated and fingerprinted. We hold it thirty days before it's sold → A buy: more cash today, and the item is ours. Same contract, signed and dated. Only precious metals are held: 15 days before they're priced and sold
- `slides.1.say`: They sign, date and fingerprint the same contract, and we hold the item thirty days before we sell it. → They sign and date the same contract. Only precious metals are held, fifteen days before they can be priced and sold. Everything else we buy can be priced right away.
- `slides.2.bullets.4`: at least two months → at least 45 days
- `slides.2.say`: for at least two months before we can sell anything → for at least forty five days before we can sell anything
- `key_points.2`: A buy is more cash, the item is ours, same contract, held 30 days → A buy is more cash, the item is ours, same contract. Only precious metals are held, 15 days; everything else can be priced right away
- `quiz.questions.1.options.0.why`: at least two months → at least 45 days
- `quiz.questions.4.options.2.why`: There's still a deal here. Give the real number and ask what else they brought. That's the procedure when the item doesn't cover what they need. → We never send a customer to a competitor, and there's still a deal here. Give the real number and ask what else they brought.
- `quiz.questions.5.options.1.why`: at least two months → at least 45 days
- `quiz.questions.6 (rewritten)`: You bought a drill this morning and the floor is thin. Can it go out today? [correct: No. A buy is held thirty days before it can be sold] → You bought a drill this morning and the floor is thin. Can it go out today? [correct: Yes, once it's cleaned, tested, priced and tagged]

## L4-02

- `slides.4.bullets.2`: Point them somewhere real if you can → Never send a customer to a competitor. Say what we can do instead
- `slides.4.say`: And if you can point them somewhere real, do it. One employee turned down a man's drumsticks, explained why, and gave him a list of places that might carry them. He hung… → And never send a customer to a competitor. Say what we can do instead, and tell them what we pay more for.
- `key_points.5`: Say no with a real reason and leave the door open → Say no with a real reason, say what we can do, and leave the door open. Never send a customer to a competitor
- `quiz.questions.3.options.2.why`: Callers told to text photos almost never follow through. Ask the titles now and give them a reason to come in. → Photos are fine and can help a quote, but waiting on photos of every game stalls the deal. Ask the titles now and give them a reason to come in.
- `quiz.questions.7 (added)`: (none) → You've turned down a customer's off-brand speaker. She asks, 'So who around here would take it?' [correct: Say what we can do, and tell her what we pay the most for]

## L4-03

- `slides.5.bullets.3`: No gold, silver or diamond numbers without the spot sheet → Gold and jewelry are quoted in store only, after appraisal
- `slides.5.say`: And no number on gold, silver or diamonds unless the spot sheet, the day's metal prices, is open and you know what the item is. → And no number on gold or jewelry over the phone. Those are quoted in the store only, after appraisal.
- `slides.6.bullets.0`: completed and approved BEFORE you finalize → completed and approved BEFORE you finalize. A renewal doesn't need a new worksheet
- `slides.6.bullets.3`: Every title pawn (a loan on a vehicle title) needs the CEO's approval at any amount → We don't make title loans
- `slides.6.say`: And every title pawn, that's a loan on a vehicle title, needs the CEO's approval at any amount before it's funded. → A renewal doesn't need a new worksheet, but a reloan does. And we don't make title loans.
- `quiz.questions.2.options.0.why`: Callers told to text photos almost never come in, and you've captured nothing. Every sell-side call ends with a range, a time, or a name and number. → Photos are fine and can help a quote, but asking for them with no range and no time captures nothing. Every sell-side call ends with a range, a time, or a name and numbe…
- `quiz.questions.5.prompt`: A regular is renewing a $1,100 loan on the same jet ski as last time. A coworker says the worksheet was done on the first loan, so skip it. What's right? → A regular redeemed his jet ski last week and wants a new $1,100 loan on it, a reloan. A coworker says the worksheet was done on the first loan, so skip it. What's right?
- `quiz.questions.5.options.1.why`: Every loan or buy of $1,000 or more needs a completed and confirmed Large Loan/Buy Worksheet, reloans included — no exceptions. → A reloan is a new loan, so it needs a new, completed and confirmed Large Loan/Buy Worksheet at $1,000 or more. A renewal doesn't need a new one.

## L4-04

- `floor_check`: (31+ days past due, statement of ownership on file) → (expired: past the 5-day grace period and the 10 days after it, statement of ownership on file)
- `slides.0.bullets`: ["Count from the day after the due date. That's day 1 past due. Through day 30 past due, we hold it and keep calling", "Day 31 past due: eligible for Pull From Inventory… → ["Count from the day after the due date. That's day 1 past due. Days 1 to 5 are the grace period: no late fee, and we keep calling", "Day 6 past due: a late fee of 5% of…
- `slides.0.say`: Here's the one timeline for pulling a defaulted loan. Count from the day after the due date. That's day one past due. For the first thirty days past due, the item is hel… → Here's the one timeline for pulling a defaulted loan. Count from the day after the due date. That's day one past due. The first five days are the grace period, with no l…
- `slides.2.bullets.1`: A buy only lands on the list after its hold is up. Everything on the list is cleared to sell. → Only precious-metal buys are held: 15 days before they're priced and sold. Everything else we buy can be priced right away.
- `slides.2.bullets.4`: Price it right the first time: low enough to sell, with about 10% room to negotiate — and get their offer first → Price it right the first time: at the higher average sold price, with about 10% room to negotiate — and get their offer first. You can always come down; you can't go up
- `slides.2.say`: A buy only shows on the pricing list after its hold is up, so everything on that list is cleared to sell. → Only precious metals we buy are held, fifteen days before they can be priced and sold. Everything else can be priced right away.
- `slides.2.say`: Low enough to sell, with about ten percent of room to negotiate. → Price at the higher average sold price, with about ten percent of room to negotiate. You can always come down, but you can't go up.
- `key_points.0`: A defaulted loan is eligible for PFI at 31 days past due and done by day 61. Never pull on day 16 → 5-day grace, a late fee of 5% of principal from day 6 past due, then 10 more days. A loan is pulled once it's expired, never before
- `key_points.2`: Price to sell with about 10% room → Price at the higher average sold price with about 10% room
- `quiz.questions.0 (rewritten)`: A loan is 18 days past its due date. The customer hasn't answered calls, and a coworker says, 'The legal hold is 15 days, so we can pull it.' What's right? [correct: Kee… → A loan is 8 days past its due date. The customer hasn't answered calls, and a coworker says, 'The grace period's over, so we can pull it.' What's right? [correct: Keep h…
- `quiz.questions.7.options.1.why`: Price it right first: low enough to sell, with roughly 10% negotiating room. → Price it right first: at the higher average sold price, with roughly 10% negotiating room.

## L4-05

- `slides.0.bullets.1`: Imaged. A photo of the customer too. Not optional → Imaged. Not optional. We photograph the ID, not the person
- `slides.0.say`: You image it, and you take a photo of the customer too. This is not optional. → You image it. This is not optional. We photograph the I D, not the person.
- `key_points.0`: photo ID imaged (never a military ID), customer photo, serial number → photo ID imaged (never a military ID), serial number

## L4-06

- `slides.0.bullets.1`: at least ninety days in a row → at least thirty days in a row
- `slides.0.say`: for at least ninety days in a row → for at least thirty days in a row
- `slides.3.bullets.0`: same 90 days → same 30 days
- `slides.3.say`: Same ninety day floor → Same thirty day floor
- `key_points.0`: 90 consecutive days → 30 consecutive days
- `quiz.questions.0 (rewritten)`: A Makita impact driver has been on the floor for 45 days and you'd like to buy it. What's the answer today? [correct: Not yet. It needs 90 days on the floor first] → A Makita impact driver has been on the floor for 12 days and you'd like to buy it. What's the answer today? [correct: Not yet. It needs 30 days on the floor first]
- `quiz.questions.3.prompt`: hits 90 days on the floor → hits 30 days on the floor
- `quiz.questions.5.options.0.why`: form, 90 days on the floor → form, 30 days on the floor
- `quiz.questions.5.options.1.text`: form, 90 days, → form, 30 days,

## L3-04

- `slides.2.bullets.1`: once the hold runs out → once the loan expires
- `slides.2.say`: once the hold period runs out, we can sell it → once the loan expires, we can sell it

## L3-02

- `gate`: Firearm and title-pawn qualifying are not in this lesson: firearms are Level 6, title pawns Level 8 and every one needs CEO approval (§04.04). → Firearm qualifying is not in this lesson: firearms are Level 6. We do not make title loans.

## Re-record list (changed `say` lines)

- L3-01 `slides.1.say`
- L3-01 `slides.2.say`
- L3-01 `slides.4.say`
- L3-02 `slides.1.say`
- L3-03 `slides.1.say`
- L3-03 `slides.3.say`
- L3-03 `slides.4.say`
- L3-04 `slides.3.say`
- L3-04 `slides.4.say`
- L3-05 `slides.0.say`
- L3-05 `slides.1.say`
- L3-05 `slides.3.say`
- L3-06 `slides.1.say`
- L3-06 `slides.2.say`
- L3-07 `slides.0.say`
- L4-01 `slides.1.say`
- L4-01 `slides.2.say`
- L4-02 `slides.4.say`
- L4-03 `slides.5.say`
- L4-03 `slides.6.say`
- L4-04 `slides.0.say`
- L4-04 `slides.2.say`
- L4-05 `slides.0.say`
- L4-06 `slides.0.say`
- L4-06 `slides.3.say`
- L3-04 `slides.2.say`

Key points changed are listed per lesson above (`key_points.N`).

## Not resolved / needs a decision

1. **Extension vs renewal (ruling 19) has no definition.** The ruling says they are two different options but not what an extension is. In L3-05 the Bravo Renewal procedure (pay the current charges, new 30-day loan) is now called a renewal, the lines equating the two are gone, and the lesson says an extension is a different option. The word "extension" is still used for "pay the finance charge and keep the item" in L3-05 (title, slides 0, 2, 4, quiz), L3-01, L3-04, L3-06, L3-07 ("the extension is the minimum", "the app takes extensions only") and L4-01. Renaming those needs Preston's one-line definition of each option; not done, to avoid inventing policy and re-recording five lessons on a guess.
2. **"Never mention a grace period to a customer" (L3-06 slide 2, key point 2, Q0) was kept.** Ruling 10 makes the 5-day grace period the real timeline but does not say staff may quote it to customers, so the customer script ("your loan is due on its due date", read it off Bravo) was left alone. L3-04 now tells staff to say the late fee out loud at closing (it is not on the ticket) without telling them to name the grace period to the customer. If staff may say "grace period" to customers, L3-06 needs those three places changed.
3. **L3-01 "say it back" → "pay it back".** Both places the phrase appeared were a teach-back (ask the customer to say it back); swapping in "pay it back" would make nonsense. Reworded both so the phrase is gone: slide 1 narration now ends "then check they got it", and the clip caption says "until the customer understands it". The quiz already says "pay this back".
4. **Late fee not printed on the ticket vs. the law cited in the lessons' own sources.** L3-01/L3-04 sources quote Va. Code § 54.1-4009(C)(2): a late fee is lawful only if disclosed on the ticket. The lessons now teach ruling 10 as written (not printed on the ticket; staff say it out loud). Worth a compliance check before Policy Day.
5. **First-payment default.** The old "no 30-day hold" exception was removed from L3-01 and L3-06 with the 30-day hold. L4-04 still says Bravo marks a first-payment default expired right away but it isn't pulled before the 15-day legal hold is up, and L3-06's Goldilocks slide still says "don't promise the hold" on first-payment defaults. Ruling 10 doesn't address them.
6. **Military ID.** Ruling 18 read as: no image of a military ID; image another government photo ID or photograph the customer (the one case a customer photo is taken). L3-02, L3-03, L4-05 keep that existing wording.
7. **Redemption paperwork.** "Two redemption tickets / redemption ticket box" removed from L3-05 (ruling 19). Nothing was put in its place about what the customer is handed at redemption, because no ruling says.
8. **L3-04 real-call clip** set to null (ruling 28). No slide or quiz line referred to the call; the old fingerprint question (Q6) is now a scripted late-fee scenario. The clip file in media/ was not touched.
9. **Sources arrays** still carry the old P&P v2026.9 citations and OPEN notes that describe the superseded rules (day-61, fingerprints, customer photo); only the new CEO-rulings source line was added. Titles and file names unchanged (L3-05 is still titled "Payments, extensions and redemptions").
10. L3-02 gate text changed: the title-pawn/CEO-approval sentence replaced with "We do not make title loans" (ruling 22). L4-03's CEO-approval line for title pawns replaced the same way.
