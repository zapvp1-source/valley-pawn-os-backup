# VSP eReceivables — Portal Map (live-mapped 2026-10-20)

Oracle iReceivables (OA Framework). Login X009686. Session idles out in ~10–15 min → "Your session has expired" error page; re-login lands on `AppsLocalLogin.jsp` (username prefilled, Chrome autofills password).

## Password expiry (ROOT CAUSE of the 10/7 "rejected" login)
Oracle EBS rotates the password on a schedule. After expiry the login succeeds but is redirected to **Change Password** (`function_id=30341`): Current / New / Re-enter, ≥8 chars, Submit. Any automation must detect this page title and hand it to Joshua — never set a password itself.

## Screen 1 — Customer Search (`OAFunc=ARI_EXTERNAL_PAGE`)
- Search By poplist (Customers default) + **Go** button `id=Icxgocontrol`. Click Go with "Show All Sites"/"Show All Customers" UNCHECKED.
- Result table rows, 2 per account (All Locations row + Bill To site row). Live 10/20:
  | Row | Name | Cust # | Address |
  |---|---|---|---|
  | 0/1 | VALLEY PAWN | 15848 | 2362 Peters Creek Rd, Roanoke |
  | 2/3 | VALLEY PAWN 2/FULL CIRCLE FINANCE, INC. | 16284 | 1321 West Broad St, Waynesboro |
  | 4/5 | VALLEY PAWN 2/FULL CIRCLE FINANCE, INC. | 16627 | 1790 East Market St, Harrisonburg |
  | 6/7 | VALLEY PAWN - 1 (FULL CIRCLE FINANCE INC) | 280758 | 571 James Madison Hwy Unit C, Culpeper (name FIXED by VSP 9/30) |
  | 8/9 | VALLEY PAWN -4 LEXINGTON | 283759 | 125 Walker St, Lexington (address FIXED 9/30) |
- Account Summary (eyeglasses) link per row: `id=N25:Aricustdetail:<n>`, onclick `submitForm('DefaultFormName',1,{'Ircustomerid1':..,'Ircustomersiteuseid1':..})`. Use the All-Locations row (even n).

## Screen 2 — Account Summary (after eyeglasses click)
Header `Department of State Police-<NAME>-<cust#>`. Text: `Your Account Balance: USD n`, `Overdue Receivables n`, `Total Open Receivables n`, Open Payments, Unapplied Credit Memos. Orange **Dashboard** / green **Account** tiles. `Return to Customer Search` link.
Link ids: Account tab = `#ARIMENUACCTDETAILS`; breadcrumb `Customer Search` (text link).

## Screen 3 — Account Details (`_rc=ARIACCTDETAILSPAGE`)
- `Account Balance: n`, optional `Overdue Invoices: USD n`.
- Search: Status select `#Iraccountstatus` (Any Status / Closed / Open/pending / Overdue / Current / aging buckets), Transaction Type `#Iracctdtlstype`, Go `#Iracctdtlgocontrol`, Clear `#IrClearBtn`. Default view = Open/pending.
- Table columns: Transaction | Type | Status | Date | Due Date | Original Amount | Remaining Amount. Rows: `FIRE-#####` Invoice (monthly, dated the 1st, due end of month), `B########` / `OIR########` Payment (negative amount). 25 per page; pager select `#M__Id` ("1 - 25 of N"), links `Next 24` / `Previous 25`.
- Row checkbox `input[name="Iracctdetailstables:selected:<i>"]`, header tri-state `#Iracctdetailstables:triState`. Invoice link `#Iracctdetailstables:Irtransaction:<i>`.
- **MAKE PAYMENT** = `button#Pay` (submitForm). Server reloads the page and embeds
  `open('https://vsppayments.virginiainteractive.org/Checkout?token=<uuid>', '_blank')` — Chrome's pop-up blocker eats it. Read the URL out of `document.documentElement.outerHTML` and open it in a tab you control (that is what the script and the Cowork task do). Token is one-time per MAKE PAYMENT click.

## Screen 4 — Virginia Interactive checkout (window 2) `vsppayments.virginiainteractive.org/Checkout?token=`
Shows store name/address, SKU = invoice number, Description = DIN, amount. Fields: hidden `VI_Token`, `FormData.FormId=16`, `originalAmount`; text `#amount` (prefilled, editable — partial pay); submit `#PaymentBtn` "Next"; `#btnClosePopup` Exit.

## Screen 5 — NIC secure checkout (window 2 continues) `securecheckout.cdc.nicusa.com/Checkout/Payment?token=`
1. Payment Type `<select>`: `CC` Credit/Debit Card | `ACH` Electronic Check (+ IAT checkbox for foreign-funded ACH). **Next**.
2. Customer Information (prefilled from VSP: name, address, email FULLCIRCLEPAWN@GMAIL.COM; **Edit** button; editing does not change VSP's record). Receipt goes to that email.
3. Payment Information (ACH): Name on Account*, "This is a business account" checkbox, Routing Number*, Account Number*, Re-enter Account Number*, Checking/Savings radios → **Next** → review → **Submit Payment** → receipt page (printable, emailed). Card path: standard card fields instead.
   VSP/NIC stores NO payment method — details are entered every time.
   Help: (804) 318-4133 / customerservice@virginiainteractive.org.

## Oracle session quirks
- `_ti` transaction id and `oapc` counter in URLs; pages are POST-driven — never bookmark deep URLs.
- Idle ~10–15 min → "Your session has expired" error page; `/` redirects to `AppsLocalLogin.jsp` (username prefilled).
- `get_page_text` on the NIC domain is permission-gated for the Chrome extension; screenshots/read_page work.

## 2025 invoices by store (read 2026-10-20, Status=Any) — file `2025_invoices_by_store.json`
ROA $824 · WAY $946 · HAR $907 · CUL $1,307 · LEX $932 = **$4,916**; bank 2025 = $4,970 → the $54 difference is two $27 charges (May, Nov) for Salem DIN 10222 (closed 9/29/26, no longer listed). Ten of twelve months tie to the bank to the penny.

## Native automation (built 2026-10-20)
`Valley Pawn OS/bin/vsp_fee_pay.py` (+ `.sh`, agent `com.valleypawn.vsp-fee-pay`, 5th 10:15). Uses the shared `pw-vp` automation Chrome (`vp_browser.py`) — the VSP password must be saved in THAT profile (run `bin/vp_signin_front.sh`, sign in to ebilling.vsp.virginia.gov once). Modes: `--read` (default in the .sh) · stage · `--pay [--dry-run]` with ACH details from Keychain `vp-vsp-ach-routing/account/name`. Guard rails in the docstring.

## NIC review screen (learned on the 10/20 live runs)
- Review shows `Electronic Check ****<last4>`, Name on Account, Terms, and ONE visible checkbox "Yes, I authorize this transaction." (must be ticked; its label is not exposed to get_by_label — use the only visible checkbox) → **Submit Payment**.
- The bank form after "Electronic Check → Next" can take 20–45 s to render; wait for "Name on Account" to be visible, re-click Next if needed.
- Multiple hidden "Next" buttons exist in the DOM — always click the `:visible` one.
