---
name: daily-mail-unsubscribe
description: Daily scan of Mac Mail app across all inboxes to unsubscribe from commercial/marketing emails
---

You are cleaning up Joshua Davis's email inboxes by unsubscribing from commercial and marketing emails.

## Objective
Scan Joshua's email accounts for commercial/marketing emails and unsubscribe from them daily at 7 AM.

## Workflow

### 1. Gmail (jdavis@fcfpawn.com) — via Gmail API (always works unattended)
1. Use the Gmail MCP tools (gmail_search_messages) to search for promotional/marketing emails from the last 24 hours. Use queries like:
   - `category:promotions newer_than:1d`
   - `is:unread category:promotions newer_than:1d`
2. For each marketing email found, read it with gmail_read_message to check if it's genuinely commercial/promotional.
3. Look for List-Unsubscribe headers in the email. If present, use WebFetch to call the unsubscribe URL.
4. If WebFetch is blocked by the network proxy, save the unsubscribe link and include it in the Slack summary so Joshua can click it manually.

### 2. iCloud (zapvp1@me.com) — via browser (best effort)
1. Use Claude in Chrome tools to check if iCloud Mail is already open in a browser tab (use tabs_context_mcp to look for existing tabs).
2. If iCloud Mail IS open in a tab, scan the inbox for marketing emails and click unsubscribe links directly in the browser.
3. If iCloud Mail is NOT open, try navigating to https://www.icloud.com/mail/ — if it loads with an active session, scan it. If it requires login, skip iCloud for this run.
4. Do NOT use the Mac Mail app or computer-use tools — those require manual approval that fails when Joshua is away.

### 3. Summary — DM Joshua on Slack
Send a Slack DM to Joshua (U03BB52MDSA) summarizing:
- How many emails were unsubscribed from (by inbox)
- Which senders were unsubscribed
- Any unsubscribe links that were network-blocked (include clickable links)
- Which inboxes were scanned vs skipped

## What to unsubscribe from
Only unsubscribe from obvious commercial/marketing/promotional emails that are SELLING something or are bulk marketing blasts.

## Do NOT unsubscribe from
- Transactional emails (order confirmations, shipping notifications, receipts)
- Emails from known business contacts or colleagues
- Emails from services Joshua actively uses (Gusto, Slack, Chekkit, Amazon Business, Brevo, Elemetal, Zoom, etc.)
- Banking, insurance, or financial institution notifications
- Government or tax-related emails
- If unsure, skip it — err on the side of caution