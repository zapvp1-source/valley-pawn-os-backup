# L7_L8_M changes — correction pass 2026-11-21

Group: every lesson in lessons/L7, lessons/L8, lessons/M (30 files read/grepped; 12 changed). `validate_lessons.py`: 0 violations. `check_answer_bias.py`: 0 correct-option-longest. Every changed lesson has "CEO rulings 2026-11-21 (ACADEMY_FINAL_RULINGS)" added to `sources`.

Convention used: rulings that name Preston are written as "the Market Manager", which is how every lesson in these levels already refers to him.

## Narration to re-record (changed `say` lines)

- L7-02: slide [1], slide [8], slide [9]
- L7-03: slide [0], slide [2], slide [5]
- L7-05: slide [3]
- L7-07: slide [4]
- L7-11: slide [3]
- L7-12: slide [1], slide [2]
- L7-14: slide [3], slide [4]
- L8-04: slide [0]
- M-01: slide [3]
- M-05: slide [0], slide [2], slide [4]
- M-06: slide [0], slide [1]

## Changes per lesson (path: old → new, ruling)

### L7-02
- `.slides[1].bullets[3]` (ruling 21): Signed agreement, two signed receipts — one for them, one for the daily folder → No agreement to sign. The customer gets a receipt showing the balance and the payment schedule
- `.slides[1].say` (ruling 21): Every layaway has a signed agreement, and two receipts that both get signed. The original goes to the customer, the copy goes in the daily folder. → There's no layaway agreement to sign. The customer gets a receipt that shows the balance and the payment schedule.
- `.slides[8].bullets[2]` (ruling 9/30): Past 30 days: no automatic refund, a manager reviews it → Past 30 days: no return
- `.slides[8].bullets[3]` (ruling 9): Receipt, original condition, all accessories. No returns on firearms, ammo or consumables → Receipt, original condition, all accessories. No returns on ammo or consumables
- `.slides[8].bullets[4]` (ruling 9): Firearms: no returns; a function problem goes to your manager and the Market Manager (lesson 6.6) → Firearms return like any other item: 7 days money back, store credit through day 30
- `.slides[8].say` (ruling 9/30): After thirty days there's no automatic refund, and a manager reviews it. → After thirty days there's no return.
- `.slides[8].say` (ruling 9): No returns on firearms, ammunition or consumables. → No returns on ammunition or consumables. Firearms return like any other item.
- `.slides[9].bullets[2]` (ruling 30): Past 30 days: a manager reviews it, case by case → Past 30 days: there is no warranty
- `.slides[9].say` (ruling 30): Past thirty days, a manager reviews it case by case. → Past thirty days, there is no warranty.
- `.key_points[6]` (ruling 9/30): days 8–30 store credit, past 30 a manager. Warranty: stops working inside 30 days, we make it right → days 8–30 store credit, firearms included. Warranty: stops working inside 30 days, we make it right; no warranty after 30 days
- `.quiz.questions[6].options[1].text` (ruling 9): Politely explain that we can't take returns on ammunition, firearms or consumables → Politely explain that we can't take returns on ammunition or consumables
- `.quiz.questions[6].options[1].why` (ruling 9): §05.08: no returns on firearms, ammunition or consumables. Say it kindly and plainly. → No returns on ammunition or consumables. Say it kindly and plainly. Firearms return like any other item, but ammunition doesn't.

### L7-03
- `.floor_check` (ruling 13): never confirm a firearm → no firearm detail to an unverified caller
- `.slides[0].bullets[1]` (ruling 13): Three rules: verify before you disclose, quote or capture, never confirm a firearm → Three rules: verify before you disclose, quote or capture, firearm loans only after full verification
- `.slides[0].say` (ruling 13): quote or capture, and never confirm a firearm. → quote or capture, and a firearm on a loan is only discussed once the account is fully verified.
- `.slides[2].bullets[4]` (ruling 13/27): No precious-metal number without the spot sheet open and the item identified → Photos help with a quote. Gold and jewelry are quoted in the store only, after appraisal
- `.slides[2].say` (ruling 13/27): Remember from Level 1: gold, silver and diamonds get no number unless the spot sheet is open and you know what the item is. → Photos help, so ask for them. The exception is gold and jewelry. Those are quoted in the store only, after we appraise them.
- `.slides[5].bullets[3]` (ruling 13): Firearms are never confirmed by phone, to anyone → A firearm on a loan: once the account is fully verified, discuss it like any other loan item
- `.slides[5].say` (ruling 13): And firearms are never confirmed on the phone, to anyone. → And once the account is fully verified, a firearm on a loan is discussed like any other loan item.
- `.key_points[4]` (ruling 13): Never confirm a firearm → Once verified, a firearm on a loan is discussed like any other loan item

### L7-05
- `.slides[3].bullets[3]` (ruling 23): Price off SOLD listings, not active ones, in the same used condition and with at least one bid. Asking prices are just what people hope to get → Price off SOLD listings, not active ones, in the same used condition and with at least one bid. Price at the higher average sold price: you can always come down, you can't go up
- `.slides[3].say` (ruling 23): Asking prices are just what people hope to get. → Asking prices are just what people hope to get. Price at the higher average sold price. You can always come down, but you can't go up.
- `.key_points[4]` (ruling 23): Price from sold comps with a bid, used condition → Price from sold comps with a bid, used condition, at the higher average sold price
- `.quiz.questions[4].options[1].text` (ruling 23): Around the middle of the sold used comps, adjusted for condition and what's included → Around $300, a little under the middle of the sold comps, so it moves quickly
- `.quiz.questions[4].options[1].why` (ruling 23): Use only sold listings that got at least one bid, in used condition. The top of the range assumes new with the full kit (KB comp-methodology-sold-with-bids-used). → Right comps, wrong spot in them. Our rule is the higher average sold price. You can always come down; you can't go up.
- `.quiz.questions[4].options[2].text` (ruling 23): At the top of the sold comps, $340, since it's tested and backed by our 30-day warranty → At the higher average sold price, toward the $340 end of the sold comps
- `.quiz.questions[4].options[2].why` (ruling 23): Right comps, wrong spot in them. Top-of-range prices assume brand new with the full kit (KB comp-methodology-sold-with-bids-used). → Sold listings with a bid, in used condition, priced at the higher average sold price. You can always come down, but you can't go up.
- `.quiz.questions[4].options[1].correct` (ruling 23): True → False
- `.quiz.questions[4].options[2].correct` (ruling 23): False → True

### L7-07
- `.call_clip` (ruling 28): {'file': 'clips/2026-09-01_WAY_call093_GOOD_WAY_service_recovery_after_theft_accusation.m4a', 'caption': 'A customer who was questioned at the counter about an award from his mother calls back upset: listen for how the employee… → null
- `.objectives` (ruling 24): say no with a real referral → say no well and offer what we can do instead
- `.slides[4].bullets[1]` (ruling 24): For something we don't deal in at all, give a real referral — a music store, a lesson program, a collector — never a place that competes with us → Never send a customer to a competitor. Say what we can do instead
- `.slides[4].say` (ruling 24): Sometimes the answer is no, and that's fine. Say it clearly and early, with the real reason. Then give them something useful: who might buy it, or where it might sell. One associate spent a few minutes with a drummer trying to … → Sometimes the answer is no, and that's fine. Say it clearly and early, with the real reason. Then tell them what we can do. Picture a drummer trying to sell his own brand of drumsticks. You say no right away, you explain why, a…
- `.key_points[5]` (ruling 24): Say no early, with a real reason, a real referral and an open door → Say no early, with the real reason, then what we can do. Never send a customer to a competitor
- `.quiz.questions[0].options[1].why` (ruling 28): Let them vent, apologize, then protect them. The real call ended with the customer thanking us just for letting him come back (BEST_CALLS; TRAINING_PROGRAM_PLAN library). → Let them vent, apologize, then protect them. Handled that way, a customer like this ends up thanking us just for letting him come back.
- `.quiz.questions[1].options[1].text` (ruling 30): 'Come on in and let's look. Past 30 days a manager reviews it; I'll get it to one today and call you' → Hear him out, apologize, and tell him honestly the warranty ended at 30 days
- `.quiz.questions[1].options[1].why` (ruling 30): Past 30 days there's no automatic refund, but there is a manager review (§05.08). Invite him in, take it seriously, and follow up promptly (Handbook Customer Service). → There is no warranty after 30 days, and no manager review. Let him vent, apologize, and say no clearly with the real reason. If a coworker told him otherwise, own that too.
- `.quiz.questions[1].options[2].why` (ruling 30): The defective-electronics exchange is within 30 days (§05.08). Past that it's a manager's case-by-case review, so don't promise an outcome you can't give. → There is no warranty after 30 days. Don't promise an exchange we don't give.
- `.quiz.questions[3].options[1].why` (ruling 28): On the real call she was phoned before she even missed it, and it took under a minute. That's the standard (library: going out of your way). → Call before she even misses it. It takes under a minute, and going out of your way is the standard.
- `.quiz.questions[4].options[1].text` (ruling 24): Say no early with the real reason, suggest who might want them (a music store), and say what we pay most for → Say no early with the real reason, then tell him what we do buy and what we pay the most for
- `.quiz.questions[4].options[1].why` (ruling 24): Real reason, real referral, door left open. The drummer call ended in 'That was very encouraging' (BEST_CALLS Call 232; KB what-we-pay-most-for). → Real reason, what we can do, door left open. A firm no can still end in a thank you.
- `.quiz.questions[4].options[2].text` (ruling 24): Say no clearly with the real reason, and keep the call short so he can move on to other shops → Say no clearly with the real reason, and point him to a music store that might want them
- `.quiz.questions[4].options[2].why` (ruling 24): Right answer, but no referral and no open door. A no can still end with the customer thanking you (library: saying no well; §07.04). → Never send a customer to a competitor. Say what we can do instead: what we buy and what we pay the most for.

### L7-11
- `.call_clip` (ruling 28): {'file': 'clips/2026-09-05_HAR_call213_GOOD_HAR_bundled_two_optics_at_160.m4a', 'caption': 'The associate keeps the price on each optic and bundles the two at $160 instead. Listen for how the number comes from the customer firs… → null
- `.slides[3].bullets[1]` (ruling 28): Bundle instead of cut: one associate sold two optics together at $160 rather than slicing one → Bundle instead of cut: two optics together at $160 rather than slicing the price of one
- `.slides[3].say` (ruling 28): One of our associates sold two optics together at a hundred sixty instead of slicing the price of one. → Say a customer wants two optics. Sell the pair together at a hundred sixty instead of slicing the price of one.
- `.quiz.questions[4].options[1].why` (ruling 28): An associate did exactly this on a real call: get the customer's number, then bundle instead of cutting (Call Analysis HAR call213; KB negotiation-first-to-speak). → Get the customer's number first, then bundle instead of cutting. The pair at one price keeps most of the margin (KB negotiation-first-to-speak).

### L7-12
- `.call_clip` (ruling 28): {'file': 'clips/2026-09-04_HAR_call175_GOOD_HAR_what_number_do_you_need_then_added_games.m4a', 'caption': 'The associate asks what number the customer needs to be at, then adds games to fill the deal. Listen for the budget turn… → null
- `.slides[1].bullets[2]` (ruling 15): Firearms: case, ammo (the lock comes with it, free) → Firearms: case, ammo (a lock is offered with handguns only)
- `.slides[1].say` (ruling 15): Firearms get a case, a lock, and ammunition. → Firearms get a case and ammunition, and a lock is offered with a handgun.
- `.slides[2].bullets[0]` (ruling 28): One associate asked 'what number do you need to be at?', then built the deal up with games to fill it → Ask 'what number do you need to be at?', then build the deal up with add-ons to fill it
- `.slides[2].say` (ruling 28): Here's a trick from one of our best calls. The associate asked the customer what number he needed to be at, then built the deal up with games to fill it. → Here's a trick that works. Ask the customer what number he needs to be at, then build the deal up with games to fill it.
- `.quiz.questions[2].options[0].why` (ruling 28): A budget is a basket, not a ceiling. An associate filled the number with games on a real call (Call Analysis HAR call175). → A budget is a basket, not a ceiling. He has forty dollars left that an add-on can fill.
- `.quiz.questions[2].options[1].why` (ruling 28): Build the deal up to the number with the add-on that makes it better (Call Analysis HAR call175; §05.03). → Build the deal up to the number with the add-on that makes it better (§05.03).
- `.quiz.questions[2].options[2].why` (ruling 28): He told you his number. Fill it; don't blow past it (Call Analysis HAR call175). → He told you his number. Fill it; don't blow past it.

### L7-14
- `.slides[3].bullets[0]` (ruling 15): Needs-it-to-work: ammunition in the right caliber. Makes-it-better: a case, a lock, a cleaning kit, optics → Needs-it-to-work: ammunition in the right caliber. Makes-it-better: a case, a cleaning kit, optics. A lock is offered with handguns only
- `.slides[3].say` (ruling 15): The makes-it-better add-ons are a case, a lock, a cleaning kit, optics. → The makes-it-better add-ons are a case, a cleaning kit, optics. A lock is offered with handguns only.
- `.slides[3].bullets[2]` (ruling 9): Account with an email, so the record is on file (no returns on firearms — a function problem is lesson 6.6). Say the four things → Account with an email, so the record is on file. Firearms return like any other item: 7 days money back, store credit through day 30. Say the four things
- `.slides[3].bullets[3]` (ruling 32): A transfer is not a sale and doesn't count toward your number. How it rings is Level 6 → A transfer is a service fee, not a retail sale, so it isn't counted in your sales total. How it rings is Level 6
- `.slides[3].say` (ruling 32): A transfer is not a sale and doesn't count toward your number. → A transfer is a service fee, not a retail sale, so it isn't counted in your sales total.
- `.slides[4].bullets[2]` (ruling 12): Buyer under 21: no handgun and no assault firearm (federal and Virginia law). Not sure what counts? Pause and ask the Market Manager → Buyer under 21: no handgun. Wants a rifle with a detachable magazine or a pistol grip? Call the Market Manager BEFORE you start any paperwork
- `.slides[4].say` (ruling 12): If you think you're looking at an assault firearm, or the buyer is under twenty-one, pause and get the current rule from the Market Manager before you go any further. → If a buyer under twenty-one wants a rifle with a detachable magazine or a pistol grip, call the Market Manager before you start any paperwork, to verify it's legal today.
- `.key_points[3]` (ruling 15): Add-ons: ammo in the right caliber, then case, lock, cleaning kit, optics → Add-ons: ammo in the right caliber, then case, cleaning kit, optics. A lock is offered with handguns only
- `.key_points[4]` (ruling 32): A transfer is not a sale and doesn't count toward your number → A transfer is a service fee, not a retail sale. It isn't counted in your sales total
- `.key_points[5]` (ruling 12): Delay, denial, assault-firearm question, under-21: Level 6 and the Market Manager, never a judgment call at the counter → Delay or denial: Level 6. Under-21 buyer and a rifle with a detachable magazine or pistol grip: call the Market Manager before any paperwork
- `.quiz.questions[2].options[1].text` (ruling 15): Ammo in the right gauge, then case, lock and cleaning kit; an account with an email; the four things; then the paperwork per Level 6 → Ammo in the right gauge, then case and cleaning kit; an account with an email; the four things; then the paperwork per Level 6
- `.quiz.questions[5].options[0].why` (ruling 32): A transfer is not a sale and doesn't count toward your number. The optic he's looking at would (KB transfer-firearm-accounting). → A transfer is a service fee, not a retail sale, so it isn't counted in your sales total. The optic he's looking at would be (KB transfer-firearm-accounting).
- `.quiz.questions[5].options[1].why` (ruling 32): A transfer is a service. The man at the optics shelf is a sales customer, and that sale is yours (KB transfer-firearm-accounting; §05.03). → A transfer is a service fee, not a retail sale. The man at the optics shelf is a sales customer, and that sale is yours (KB transfer-firearm-accounting; §05.03).
- `.quiz.questions[6].prompt` (ruling 12): A buyer who looks about 20 asks about a rifle you think might fall under the assault-firearm rules. What do you do? → A buyer who is 20 wants a rifle with a detachable magazine and a pistol grip. What do you do?
- `.quiz.questions[6].options[0].why` (ruling 12): The 4473 and the background check don't settle an age or assault-firearm question. Pause and get the current rule from the Market Manager (HUDDLE_INPUTS F1/F2). → The 4473 and the background check don't settle this. An under-21 buyer and this kind of rifle means a call to the Market Manager before any paperwork starts.
- `.quiz.questions[6].options[1].why` (ruling 12): That's also a judgment call at the counter. The store rule comes from the Market Manager, not from memory (HUDDLE_INPUTS F1/F2). → That's a judgment call at the counter. The Market Manager verifies what's legal today, before any paperwork.
- `.quiz.questions[6].options[2].text` (ruling 12): Pause the sale and get the current rule from the Market Manager → Call the Market Manager before you start any paperwork
- `.quiz.questions[6].options[2].why` (ruling 12): Possible assault firearm or under-21 buyer: the current rule comes from the Market Manager (HUDDLE_INPUTS F1/F2; Academy L6-02). → Under-21 buyer and a rifle with a detachable magazine or pistol grip: call the Market Manager before paperwork starts, to verify current legality.

### L8-04
- `.slides[0].bullets[0]` (ruling 18): photos, fingerprints, signatures → photos of IDs, signatures
- `.slides[0].say` (ruling 18): photos of I Ds, fingerprints, signatures → photos of I Ds, signatures
- `.quiz.questions[3].options[0].text` (ruling 5): Ring it under his login, then tell him when he's back so his drawer matches → Ring it under his login, then tell him when he's back so he knows
- `.quiz.questions[3].options[0].why` (ruling 5): There is never a reason to conduct a transaction under another employee's login; telling him later doesn't fix drawer accountability or the audit trail (§02.04). → There is never a reason to conduct a transaction under another employee's login; telling him later doesn't fix accountability or the audit trail (§02.04).

### M-01
- `.slides[3].bullets[1]` (ruling 10): Days 1–15: legal hold. Never pull on day 16. Held through day 30 → Days 1–5: grace period, no late fee
- `.slides[3].bullets[2]` (ruling 10): Day 31: eligible to pull. Day 61: the pull is done → Day 6: a late fee of 5% of the loan principal starts. It is not printed on the ticket
- `.slides[3].bullets[3]` (ruling 10): Past day 61 needs the CEO's written approval → Then 10 more days, and the loan expires. Nothing is pulled before that
- `.slides[3].bullets[4]` (ruling 10): Never made a first payment? No 30-day hold: mark it expired in Bravo as soon as it's past due, any amount — but nothing is pulled, priced or sold before the 15-day legal hold is up → Never made a first payment? Mark it expired in Bravo as soon as it's past due, any amount — but nothing is pulled, priced or sold before those 15 days are up
- `.slides[3].bullets[5]` (ruling 19): A renewal payment resets the due date; count from the latest due date in Bravo → A renewal must show the correct loan date in Bravo; count from the latest due date in Bravo
- `.slides[3].say` (ruling 10/19): Loans run on one timeline, and every count here is days past due. Day one is the day after the due date. Days one through fifteen are the legal hold. Nobody pulls on day sixteen. We hold through day thirty. Day thirty one, it's… → Loans run on one timeline, and every count here is days past due. Day one is the day after the due date. Days one through five are the grace period. On day six, a late fee starts. It's five percent of the loan principal, and it…
- `.key_points[2]` (ruling 10): Loans: every count is days past due; legal hold through 15, held through 30, eligible day 31, pull done by day 61 → Loans: every count is days past due; 5-day grace, a 5% late fee on the principal from day 6 (not printed on the ticket), then 10 more days and the loan expires
- `.key_points[3]` (ruling 10/19): First-payment defaults get no 30-day hold (expired at day 1 past due, pulled only after the 15-day legal hold); nothing is held past day 61 without the CEO's written approval → First-payment defaults are marked expired at day 1 past due and pulled only after the 15 days are up; a renewal must show the correct loan date in Bravo
- `.quiz.questions[3].options[0].text` (ruling 10): Pull and price it — at 40 days past due it's past day-31 eligibility → Pull and price it — at 40 days past due the loan expired weeks ago
- `.quiz.questions[3].options[0].why` (ruling 10): Day 31 makes a loan eligible to pull, but no item moves into sellable inventory without a statement of ownership, whatever the day count (§06.01; Va. Code § 54.1-4005). → An expired loan still doesn't move into sellable inventory without a statement of ownership, whatever the day count (§06.01; Va. Code § 54.1-4005).
- `.quiz.questions[4].prompt` (ruling 10): A loan is 63 days past due. The customer promised to pay 'Friday for sure.' A team member wants to keep holding it. What's the rule? → A customer comes in on day 8 past due to pay. He says, 'My ticket doesn't say anything about a late fee.' What's right?
- `.quiz.questions[4].options[0].text` (ruling 10): Hold it — a promise to pay restarts the clock → Waive it — if the fee isn't printed on the ticket, we can't charge it
- `.quiz.questions[4].options[0].why` (ruling 10): A promise doesn't restart anything. Only a payment changes the due date, and past day 61 the only hold is one the CEO approved in writing (§06.01). → The late fee is not printed on the ticket, but it's the rule: 5% of the loan principal, starting on day 6 past due.
- `.quiz.questions[4].options[1].text` (ruling 10): Pull it, or get the CEO's approval to hold — day 61 has already passed → Explain that a 5% late fee on the principal started on day 6
- `.quiz.questions[4].options[1].why` (ruling 10): The pull is done by day 61; holding past it takes the CEO's written approval (§06.01). → Five-day grace period, then a late fee of 5% of the loan principal from day 6. It isn't printed on the ticket, so explain it plainly.
- `.quiz.questions[4].options[2].text` (ruling 10): Hold it through Friday, note the promise in Bravo, and pull it if he misses → Charge 5% of the full payoff, interest included, since he's past the grace period
- `.quiz.questions[4].options[2].why` (ruling 10): A promise doesn't move the timeline. The pull was due by day 61, and only the CEO, in writing, can approve a hold past it (§06.01). → The late fee is 5% of the loan principal, not of the payoff.
- `.quiz.questions[5].prompt` (ruling 10): A new associate pulls a loan on day 16 past due because 'the 15-day hold is over.' What do you tell her? → A new associate pulls a loan on day 8 past due because 'the grace period is over.' What do you tell her?
- `.quiz.questions[5].options[0].text` (ruling 10): Good catch — the 15-day legal hold is over, so day 16 is the pull date → Good catch — the 5-day grace period is over, so day 8 is fine to pull
- `.quiz.questions[5].options[0].why` (ruling 10): The 15-day legal hold is the statutory floor, not a pull date. Staff never pull on day 16 (§05.01; §06.01). → The end of the grace period starts the late fee, not the pull. The loan has 10 more days before it expires.
- `.quiz.questions[5].options[1].text` (ruling 10): Put it back. 15 days is the legal floor; it's eligible on day 31 → Put it back. The late fee started on day 6; it hasn't expired
- `.quiz.questions[5].options[1].why` (ruling 10): Company practice is day 31 past due for eligibility, with the pull done by day 61 (§06.01). → Five days of grace, the late fee from day 6, then 10 more days before the loan expires. Nothing is pulled before that.
- `.quiz.questions[5].options[2].text` (ruling 10): Leave it pulled, but don't price it until day 31 → Leave it pulled, but don't price it until the loan expires
- `.quiz.questions[5].options[2].why` (ruling 10): Pulling it is the problem. It stays in loan status until day 31 past due; the hold runs through day 30 (§06.01). → Pulling it is the problem. It stays in loan status until the loan expires.
- `.quiz.questions[6].options[0].why` (ruling 10): First-payment defaults get no 30-day hold, but the 15-day statutory hold still applies before anything is pulled or sold (§06.01; §05.01). → First-payment defaults are marked expired as soon as they're past due, but the 15-day statutory hold still applies before anything is pulled or sold (§06.01; §05.01).
- `.quiz.questions[6].options[1].text` (ruling 10): Treat it like any other loan: it's eligible to pull on day 31 past due → Treat it like any other loan and wait out the grace period before you mark it expired
- `.quiz.questions[6].options[1].why` (ruling 10): First-payment defaults get no 30-day hold. They're expired as soon as past due and pulled after day 15, not day 31. → First-payment defaults don't wait. They're marked expired as soon as they're past due, and pulled once the 15 days are up.
- `.quiz.questions[7].options[0].text` (ruling 10/19): Pull it — day 35 is past day 31, and a renewal doesn't change the original date → Pull it — day 35 is long expired, and a renewal doesn't change the original date
- `.quiz.questions[7].options[0].why` (ruling 10/19): A renewal payment resets the due date. Counting from the old one pulls a loan that isn't past due (§06.01). → A renewal moves the due date. Counting from the old one pulls a loan that isn't past due (§06.01).
- `.quiz.questions[7].options[1].why` (ruling 19): Every count runs from the latest due date in Bravo. After a renewal, the clock starts over. → A renewal must show the correct loan date in Bravo, and every count runs from the latest due date there.
- `.quiz.questions[7].options[2].text` (ruling 10/19): Leave it alone until day 61 from the original date, then pull it → Charge the 5% late fee now, since it's past day 6 from the original due date
- `.quiz.questions[7].options[2].why` (ruling 10/19): Day 61 is the pull deadline for a loan that's actually past due. This one isn't; its due date moved (§06.01). → This loan isn't past due; its due date moved with the renewal. Check that the renewal shows the correct loan date in Bravo.

### M-04
- `.quiz.questions[4].prompt` (ruling 27/13): gave a gold price without the spot sheet → quoted a gold price over the phone

### M-05
- `.slides[0].bullets[3]` (ruling 32): Added to Gusto, so their onboarding documents are waiting → They're added to Gusto for you — managers don't onboard new hires in Gusto — so their documents are waiting
- `.slides[0].say` (ruling 32): And they're added to Gusto, so their paperwork is waiting for them. → You don't onboard them in Gusto. That's done for you, so their paperwork is waiting for them.
- `.slides[2].bullets[0]` (ruling 7): Gun safety class + certificate, on the clock, company pays, verified at gunsafety.co/verify → Gun safety class + certificate, on the clock. They pay for the class and are reimbursed as a paid-out from the till. The certificate goes to the Market Manager, who gets it filed in Gusto
- `.slides[2].say` (ruling 7): The gun safety class and certificate are done on the clock, the company pays for the certificate, and it's verified at the provider's site. → The gun safety class and certificate are done on the clock. The employee pays for the class and is reimbursed as a paid-out from the till. The certificate goes to the Market Manager, who gets it filed in Gusto.
- `.slides[4].bullets[1]` (ruling 8): Watch them do it, then mark it off in the New Hire Training Tracker the same day → Do one when the training prompts for it, and at your discretion. Watch them do it, then mark it off in the New Hire Training Tracker the same day
- `.slides[4].say` (ruling 8): Watch them do the real thing, then mark it off in the training tracker the same day. → You do one when the training prompts for it, and at your discretion. Watch them do the real thing, then mark it off in the training tracker the same day.
- `.quiz.questions[2].options[0].text` (ruling 32): Give her until Friday and note it in Gusto, since the store's computer caused the delay → Give her until Friday and note it on the checklist, since the store's computer caused the delay

### M-06
- `.slides[0].bullets[0]` (ruling 5): counting a drawer → counting the till
- `.slides[0].bullets[1]` (ruling 8): You watch them do it, for real, and tap ✅ → When the training prompts for one, or at your discretion, you watch them do it, for real, and tap ✅
- `.slides[0].say` (ruling 5/8): counting a drawer, opening and closing the store. You watch them do it for real, and then you tap the check. → counting the till, opening and closing the store. You do one when the training prompts for it, and at your discretion. You watch them do it for real, and then you tap the check.
- `.slides[1].bullets[0]` (ruling 5): real drawer → real till
- `.slides[1].bullets[3]` (ruling 5): drawer counts only → till counts only
- `.slides[1].say` (ruling 5): a real drawer → a real till
- `.key_points[0]` (ruling 8): Screen test + Floor Check = mastered; → Screen test + Floor Check = mastered; do one when the training prompts for it, and at your discretion;
- `.quiz.questions[0].prompt` (ruling 4/5): Watching a drawer-balance Floor Check, you see your trainee about to skip the calculator tape. You say, 'Don't forget the tape.' She runs it and finishes perfectly. Pass or redo? → Watching a till-count Floor Check, you see your trainee about to skip printing the Bravo count report. You say, 'Don't forget the report.' She prints it and finishes perfectly. Pass or redo?
- `.quiz.questions[0].options[0].text` (ruling 4/5): Pass — the drawer balanced, and every step, the tape included, got done → Pass — the till balanced, and every step, the report included, got done
- `.quiz.questions[0].options[1].text` (ruling 4/5): Redo. Coach the tape step now and watch a full balance another day → Redo. Coach the report step now and watch a full count another day
- `.quiz.questions[0].options[2].text` (ruling 4/5): Pass, and note in the Academy that you gave her one reminder on the tape → Pass, and note in the Academy that you gave her one reminder on the report
- `.quiz.questions[5].prompt` (ruling 5): A trainee's drawer count came out $10 short. → A trainee's till count came out $10 short.
- `.quiz.questions[5].options[0].text` (ruling 5): Redo — the drawer didn't balance, and a pass means the numbers have to match → Redo — the till didn't balance, and a pass means the numbers have to match
- `.quiz.questions[5].options[0].why` (ruling 5): The Floor Check line for drawer balancing includes handling a mismatch: recount, research, call the Market Manager before EOD, document. She did every step (L2-03 floor_check). → The Floor Check line for balancing the till includes handling a mismatch: recount, research, call the Market Manager before EOD, document. She did every step (L2-03 floor_check).

## Checked, no change needed
- L8-01 title pawns: describes a title PAWN throughout (we hold the vehicle); the only "title loan" mention is "that's what makes it a pawn and not a title loan". CEO approval there is for title pawns, left as is. Third-party line already matches ruling 14.
- L8-05 texting/calling rules: marketing-contact law only; nothing conflicts with ruling 13.
- M-02, M-03: no 90-day employee-purchase rule and no retail pricing rule is stated (the 90-day figures are the discount age ladder, the eBay markdown clock and a report label), so nothing to correct for rulings 20/23.
- L7-09, L7-10 already teach "never send a customer to a competitor". L7-05 Best Offer stays off (ruling 31). No social-media/gun-posting content anywhere in these levels (ruling 29).
- L7-00, 01, 04, 06, 08, 09, 10, 13, 15, L8-00, 02, 03, 06, M-00: grepped for every ruling's wrong facts; none found.

## Judgment calls for the reviewer
- L7-02 returns slide: "Past 30 days: no automatic refund, a manager reviews it" was changed to "Past 30 days: no return" to match rulings 9 and 30 (7 days money back, store credit to day 30, nothing after). Ruling 30 names the warranty only; revert this one line if a manager review of late RETURNS is still wanted.
- L7-02 layaway slide: the "two signed receipts, copy in the daily folder" detail was dropped along with the signed agreement, because ruling 21 describes one receipt showing balance and schedule.
- L7-07: `call_clip` is null. Slides 1 and 2 still tell the upset-customer story as an anecdote ("On one call…"); they don't refer to a clip the learner heard, so the narration was left alone. The drumstick story on slide 4 is now a scripted scenario with no referral.
- L7-07 Q1 (PlayStation at 40 days): rewritten to the honest no (no warranty after 30 days, no manager review). The rulings don't say what staff may offer instead, so the answer stops at hear him out, apologize, say no with the reason.
- L7-14 slide 2 and Q4 still say a firearm in INVENTORY is never confirmed to a caller. Ruling 13 covers a firearm on a verified customer's loan only, so the inventory rule was left.
- L7-04 still says customer texts go through Chekkit, never a personal phone. Ruling 26 (personal phones are used for work, e.g. eBay photos) doesn't address customer texting, so it was left. No lesson in these levels says personal phones can't be used for eBay photos.
- M-01 loan timeline now teaches only ruling 10 (5-day grace, 5% of principal from day 6, not on the ticket, 10 more days, expired) with the day-31/day-61 pull standard and the CEO-approval-past-day-61 line removed. No replacement pull deadline is stated because the rulings don't give one. The first-payment-default rule (marked expired at day 1 past due, not pulled before the 15 days) was kept.
- M-05 / M-06: ruling 8 wording added (do a Floor Check when the training prompts for one, and at your discretion). The "pending more than 3 days shows on the scorecard by your name" lines (M-05 slide 4, M-06 slide 4, key points, M-06 Q4) were left because the ruling doesn't say the scorecard flag is gone; remove them if it is.
- M-05 still says keys come at 90 days + Certified. Ruling 6 is about the safe combination, so store keys were left.
- M-05 slide 2 no longer says the certificate is "verified at the provider's site" in narration (the gate wording "certificate verified" elsewhere is unchanged).
