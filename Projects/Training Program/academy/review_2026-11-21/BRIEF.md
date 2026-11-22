# Lesson correction pass 2026-11-21 — brief for editors

CEO Joshua Davis locked these rulings on 2026-11-21 (Preston Peters' feedback + his 11/5 answers + Joshua's own rulings). They override anything in the lessons, the P&P and earlier rulings. Your job: make the lesson JSONs in `lessons/` for your assigned levels match them. Nothing else.

## How to work
- Work dir (device_bash on the Mac): `$HOME/mnt/Projects/Training Program/academy`. Every device_bash call is a fresh shell; cd each time.
- Read `LESSON_SPEC.md` first (format + writer rules). Backup already exists at `backups/20261121-preston-pre/`.
- Find passages with `python3 review_2026-11-21/grep_lessons.py '<regex>' '<file-regex e.g. /L1/>'` (prints file, JSON path, text). Read each assigned lesson in full before editing it.
- Edit ONLY with a python read-modify-write on the JSON (json.load / json.dump with indent=2, ensure_ascii=False). Never retype a file. Never touch `.bak` files, `lessons_target_20261028/`, build_scorm.py, voice.py, dist/, media/.
- Fix EVERY place the wrong fact appears in a lesson: slides[].heading/bullets/say, key_points, objectives, floor_check, quiz prompts/options/why, call_clip. Keep slide bullets, `say`, key points and quiz consistent with each other.
- Narration budget is tight: each changed `say` line or key point is re-recorded. Change only lines that state something wrong; keep rewrites about the same length; don't polish lines that are already right.
- Keep the spec: 6–8 graded questions (9 only with a goldilocks question), >=4 scenarios, exactly one correct option per question, every option has a `why`, the right answer is not the longest option. If a question tests a rule that no longer exists, rewrite it to test the new rule (don't just delete it).
- Voice: company voice ("Our rule is…"), no "Preston says", no dates, short spoken sentences in `say`.
- Add to `sources` : "CEO rulings 2026-11-21 (ACADEMY_FINAL_RULINGS)". 
- Don't invent policy. If a ruling doesn't cover a detail, remove the wrong claim rather than inventing a replacement.
- Do NOT run voice.py, build_scorm.py, or anything in a browser. Do not message anyone.
- When done: run `python3 validate_lessons.py` and `python3 check_answer_bias.py` (fix anything they flag in your files), then write `review_2026-11-21/<your-group>_changes.md`: per lesson, each change (old → new, one line each) and anything you could not resolve. Your final message = that summary, short.

## Rulings (all levels)
1. Store cash limit is $5,000. Any cash over $5,000 goes to the bank. (No $2,000/$3,000 limit.)
2. Deposits: cash stays in the till at close. A deposit is made only when the store is over $5,000 or is told to deposit down. In Bravo a deposit moves till → safe, then safe → bank, during bank hours.
3. Opening: the till opens with whatever cash the store closed with the night before. There is no set opening amount (no $275).
4. Counting: count with Bravo's counting tool and the printed report. There is NO calculator tape.
5. Tills: each store runs one shared (global) till, not a personal drawer per employee. Culpeper also has one satellite till that runs with $250–$1,000 and is counted every morning and at end of day.
6. Safe: one combination. Employees get it after 90 days of employment. No spare keys / no spare-key protocol / no multiple combinations.
7. Gun-safety certificate: the employee pays for the class and is reimbursed as a paid-out from the till. The certificate is sent to Preston, who gets it filed in Gusto. (Employees don't upload it themselves.)
8. Floor checks: managers do them when the training prompts for one, and at their discretion.
9. Firearm returns: same as other items — 7-day money back, up to 30 days store credit. (Remove "no returns/no refunds on firearms".)
10. Loan timeline: 5-day grace period; a late fee of 5% of the loan principal starts on day 6; then 10 more days before the loan expires. The late fee is NOT printed on the ticket. Remove any "day 61 pull" (and "day 31 pull") operating standard.
11. Buy holds: only precious metals are held — 15 days before they can be priced and sold. Everything else bought outright can be priced immediately. (Remove "buys are held 30 days".)
12. Under-21 buyer wanting a rifle with a detachable magazine or pistol grip: call Preston BEFORE starting paperwork, to verify current legality.
13. Phone: once the account is fully verified, a firearm on a loan is discussed like any other loan item. Photos of items are fine and helpful for quotes. Gold and jewelry are quoted in store only, after appraisal.
14. Third-party firearm redemption: we don't do it. Only the account holder redeems a firearm.
15. Gun locks: offered with handguns only.
16. Form mistakes (4473 etc.): correct on the original until the transaction is complete; after completion, changes go on a photocopy only.
17. A&D book lives in Bravo (no binders). Multiple-handgun-sale forms are filed with their 4473.
18. Pawn paperwork: loans are paid out in cash only, no checks. The statement of ownership is part of the signed ticket (not a separate form). We photograph the ID, not the person (military ID is the exception: no photo of a military ID). No fingerprints.
19. Extension and renewal are two different options — don't treat them as the same thing. Writing a new loan on the same item is a reloan (a reloan needs a new worksheet; a renewal does not). There is no "redemption ticket". Renewals must show the correct loan date in Bravo.
20. Employee purchases / employee pricing: the item must be on the floor 30 days (not 90).
21. Layaway: there is no signed layaway agreement. The customer gets a receipt showing the balance and the payment schedule.
22. We do not make title loans (a title pawn where we hold the vehicle is different; leave accurate title-pawn content alone, and remove "needs Josh's approval" wording for title loans).
23. Pricing: price at the higher average sold price — you can always come down, you can't go up.
24. Never send a customer to a competitor. Say what we can do instead.
25. Managers' meeting: 9:30 AM, by Slack huddle (not 9:00; drop "1st and 3rd Monday" — say weekly).
26. Personal phones: employees do use personal phones for work, especially eBay listing photos. Say so plainly.
27. Jewelry: there is no spot sheet (Bravo does the melt valuation). Bravo adjusts the valuation for stones but does not give a gold weight minus stones. Diamonds bought outright are always priced at the Fair grade; drop any "fair/good/great" pay-by-grade teaching.
28. Real-call clips in L3-04, L5-04, L7-07, L7-11, L7-12 don't match their lessons: set `call_clip` to null in those five and replace any quiz question or slide line that refers to "the call you heard" with a scripted scenario that teaches the same lesson point. Don't touch call clips in other lessons.
29. No handguns or any guns on social media, ever (Instagram, Facebook, anything).
30. There is no warranty after 30 days. Remove "managers review/approve warranty outside 30 days".
31. eBay Best Offer stays OFF (unchanged).
32. Intro lesson: the answer to every quiz question must be stated in the lesson itself; say what happens under 80% (you retake it; after two tries your manager is nudged). M-05: managers do not onboard new hires in Gusto. L3-01 typo: "say it back" → "pay it back". L7-14: make "a transfer is not a sale and doesn't count toward your number" clear (an FFL transfer is a service fee, not a retail sale, so it isn't counted in your sales total).
