---
name: vsp-nics-fee-monthly
description: Monthly (5th, 10:15 AM ET): log into VSP eReceivables, read all 5 stores' open FIRE invoices, stage each payment to the final Pay screen, DM Joshua one line. Type: browser only (no Bravo contact). model: claude-sonnet-5
---

model: claude-sonnet-5

Run the monthly Valley Pawn Virginia State Police gun-check fee payment run.

1. Load the `enterprise-map` skill, then the `vsp-nics-fee-payment` skill, and follow the skill exactly. It is the source of truth (account numbers, login lockout guard, flow, hard rules). Also read `~/Documents/Claude/Projects/Compliance/VSP-NICS-Fee-Payment-Runbook.md`.
2. Use Claude in Chrome (Joshua's real Chrome, where the VSP password is saved). Open https://ebilling.vsp.virginia.gov in a new tab. ONE login attempt only — if it fails, stop, do not retry or reset, send Joshua one plain Slack DM (channel D03BHQH5VGT) saying the State Police billing sign-in saved in Chrome isn't working and whoever pays it needs to sign in once on his Mac and let Chrome save the password; update `Compliance/OBLIGATIONS.json` row `vsp-nics-fee-monthly` next_step; end.
3. If logged in: for all 5 accounts (ROA 15848, WAY 16284, HAR 16627, CUL 280758, LEX 283759) record every open FIRE-##### invoice (number, dates, amount, balance) and confirm the account name/address look right (CUL should be Full Circle Finance / Valley Pawn, LEX 125 Walker St). Write `~/Documents/Claude/Projects/Compliance/vsp/<YYYY-MM>.json` and `.md`.
4. Stage each store with a balance: select its open invoice(s) → MAKE PAYMENT → complete everything up to, but NOT including, the final Pay/Submit click. Never click the final payment submit — that is Joshua's click. Leave each staged tab open.
5. Send Joshua ONE Slack DM (D03BHQH5VGT), plain language, no technical words: "VSP gun-check fees for <Month> are ready: CUL $x, HAR $x, LEX $x, ROA $x, WAY $x — total $X, due <date>. The payment screens are open in Chrome — click Pay on each." If all five are $0, DM "VSP gun-check fees for <Month>: nothing owed at any store." Never post to any team channel or store manager.
6. Update the `vsp-nics-fee-monthly` row in OBLIGATIONS.json (last_verified, evidence path, due = the 20th of this month) and add a dated row to `~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md` ("VSP payments staged, awaiting Joshua's Pay click").
7. Also check the previous month's file: if it shows staged-but-unconfirmed payments, re-open those accounts, confirm $0 balance, and record confirmation numbers (close the register row) — or tell Joshua in the same DM if anything from last month is still open.
8. If any portal screen differs from the skill, update the runbook with the real layout before ending.