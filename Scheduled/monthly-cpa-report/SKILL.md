---
name: monthly-cpa-report
description: Process monthly CPA report from Silverline Tax — auto-categorize the uncategorized transactions spreadsheet, send it to Joshua for review, and summarize the management report to Slack.
---

You are processing the monthly CPA report for Full Circle Finance Inc (DBA Valley Pawn). Silverline Tax sends two reports each month via email. Your job is to: (1) edit the uncategorized transactions spreadsheet with categories and send it to Joshua for review, and (2) summarize the management report to Slack.

## Step 1: Find the latest CPA email

Search Gmail for the most recent email from Liana at Silverline Tax. Try these searches in order until you find it:
- `from:liana@silverline.tax has:attachment`
- `from:liana@lodestar.tax has:attachment` (old email, fallback)
- `subject:"Monthly Report" has:attachment newer_than:45d`

The email will have two attachments:
1. A PDF named like `MM.DD.YY Full Circle Monthly Management Report.pdf`
2. An Excel file named like `MM.DD.YY Full Circle Uncategorized Transactions.xlsx`

Record the email's messageId and threadId — you'll need them later to reply to Liana.

If you cannot find a new email from the last 45 days, send a Slack DM to Joshua (user ID: U03BB52MDSA) saying: "No new CPA report found from Silverline Tax this month. You may want to follow up with Liana (liana@silverline.tax / 219-365-9520)." Then stop.

## Step 2: Download the attachments

Use Chrome browser tools to:
1. Navigate to the email in Gmail
2. Download BOTH attachments (hover over each attachment thumbnail, click the download icon)
3. The files will download to the local machine

Then locate the downloaded files. They'll typically be in ~/Downloads/ with the filenames from the email.

## Step 3: Edit the Uncategorized Transactions spreadsheet

This is the PRIMARY task. Read the xlsx skill (if available) for best practices on editing Excel files.

Open the downloaded Excel file and read its contents. The spreadsheet has:
- Two sections: **Uncategorized Income** (top) and **Uncategorized Expense** (below)
- Columns: A (section label) | B (Date) | C (Name) | D (Memo/Description) | E (Split/bank account) | F (Amount)

**Add a new column G header "Category"** and fill in the category for each transaction using these rules:

**EXPENSE CATEGORIZATION RULES (by vendor name / memo):**
- `Coinbase` / `COINBASE` → "Owner's Draw / Personal"
- `Apple Cash` / `MONEY TRANSFER AUTHORIZED` / `APPLE CASH SENT` → "Owner's Draw / Personal"
- `Fortiva` / `AUTOFORTIVA` → "Owner's Draw / Personal"
- `U-Haul` / `U-HAUL` → "Automotive Expenses" (business use) — but add "⚠️ CONFIRM" if description mentions a personal-sounding location
- `Bravo` / `VSP*BRAVO STORE` → "Software & Apps"
- `Farmers and Marc` / `Farmers and Merc` → "Bank Charges & Fees"
- `Ten One Design` / `TENONEDESIGN` → "Office Supplies"
- `Minut` / `MINUT` → "Security Services"
- `Family Focus` → "Owner's Draw / Personal ⚠️ CONFIRM"
- `Great Outdoor Provision` → "Owner's Draw / Personal ⚠️ CONFIRM"
- `ZELLE` transfers → "Owner's Draw / Personal ⚠️ CONFIRM" (could be personal or business)
- `ApiPay` / `APIPAY` → "⚠️ NEEDS CATEGORY"
- `TWINALB` / `TWIN-ALB` → "⚠️ NEEDS CATEGORY"
- `TO MARLON` → "Owner's Draw / Personal ⚠️ CONFIRM"
- `Business Platinum Indeed Credit` (on income side) → "Advertising & Marketing Offset"

**For any vendor NOT in the rules above:** Try to infer the category from the memo/description and the expense categories used in the P&L (Advertising & Marketing, Automotive Expenses, Bank Charges & Fees, Equipment Rental, Gun Background Check, Insurance, Interest Paid, Legal & Professional Services, Licenses & Permits, Meals & Entertainment, Office Expenses, Office Supplies, Payment Processing Fees, Payroll Expenses, Rent & Lease, Repairs & Maintenance, Sales Tax, Security Services, Shipping & Postage, Software & Apps, Subcontractor, Telephone, Travel, Utilities). If you truly can't determine it, mark it "⚠️ NEEDS CATEGORY".

**Also add a column H "Notes"** for any flagged items — briefly explain why it was flagged (e.g., "Personal crypto purchase", "Unclear vendor — needs Joshua's input").

Save the edited spreadsheet to the outputs folder so Joshua can review it.

## Step 4: Send the edited spreadsheet to Joshua for review

Send a Slack DM to Joshua (user ID: U03BB52MDSA) with:

```
📋 *CPA Uncategorized Transactions — [Month Year]*

I've categorized the transactions from Liana's report. Here's the summary:

*[X] transactions auto-categorized*
*[Y] transactions flagged for your review* ⚠️

Flagged items:
- [vendor] — $[amount] — suggested: [category] — [reason]
...

The edited spreadsheet is ready for your review. Once you've looked it over and made any corrections, let me know and I'll send it back to Liana.
```

Also present the edited spreadsheet file to Joshua using the present_files tool so he can open and review it.

**STOP HERE AND WAIT.** Do not proceed to send anything to Liana. Joshua will review the spreadsheet and come back to tell you to send it. When Joshua says to send it (in a future conversation), reply to Liana's email with the edited spreadsheet attached.

## Step 5: Summarize the Management Report (secondary task)

Use Chrome browser tools to open the PDF attachment from the email in Gmail's preview. Screenshot each page to capture the financial data.

The report typically contains (~12 pages):
- Profit and Loss (total)
- Profit and Loss by Store
- Profit and Loss by Month
- Balance Sheet
- Statement of Cash Flows

Create a summary and send it as a Slack DM to Joshua (user ID: U03BB52MDSA):

```
📊 *Monthly Management Report — [Month Year]*
*Full Circle Finance Inc*

*Income:* $X (Pawn Service: $X | Sales: $X)
*COGS:* $X
*Gross Profit:* $X
*Total Expenses:* $X
*Net Operating Income:* $X

*Uncategorized Expenses:* $X ⚠️

*Notable Items:*
- [Any unusually high or significantly changed expenses]

*Balance Sheet:* Assets $X | Liabilities $X | Equity $X
*Cash Position:* $X

*By Store (Net Income):*
- Culpeper: $X
- Waynesboro: $X
- Harrisonburg: $X
- Lexington: $X
- Roanoke: $X

_Full report in your email from Liana._
```

## Important Notes
- Joshua's Slack user ID: U03BB52MDSA
- CPA: Liana Motel at Silverline Tax (liana@silverline.tax), phone 219-365-9520
- Gmail account: jdavis@fcfpawn.com
- NEVER send the spreadsheet to Liana without Joshua's explicit approval
- Save the edited spreadsheet to the outputs folder AND present it to Joshua
- The categorization rules above are a starting point — Joshua may correct categories over time
- If you encounter errors downloading or processing attachments, notify Joshua via Slack with details