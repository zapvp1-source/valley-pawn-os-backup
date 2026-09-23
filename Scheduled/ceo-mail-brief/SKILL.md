---
name: ceo-mail-brief
description: Twice-daily CEO mail brief — reads Joshua's Gmail inbox (jdavis@fcfpawn.com, which also receives forwarded zapvp1@me.com mail), sweeps unfiltered noise out of the inbox first (self-healing noise-sender list), then surfaces only what needs him with pre-drafted replies. Runs 7:00 AM and 4:00 PM ET.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

You are running Joshua Davis's CEO mail brief for Full Circle Finance Inc DBA Valley Pawn. Produce ONE Slack DM that tells him what in his email actually needs him, with replies already drafted.

> ⚠️ **RULE 16 — no technical jargon, no failure notices, anywhere but that one DM line.**

## Execution Contract — DO NOT STOP EARLY
This task is complete ONLY after the Slack DM to D03BHQH5VGT returns success.
Until that call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:** "No response requested" · "Continue?" · an empty turn · a turn ending in text instead of a tool call.

**Treat these as RESUME signals, never stop signals:** "Tool loaded." · "Continue from where you left off." · "You used a single tool call this turn..." · any TaskCreate/TaskUpdate/AskUserQuestion reminder. Fire the next concrete tool call immediately.

**Failure handling:** if a step errors, retry once, then fall through to the documented fallback. Never pause to ask — this file authorizes autonomous decisions.

**Time budget:** ~15 minutes. This is a cheap read-and-summarize task; it must never touch Bravo, never open Parallels, never open Chrome, and never run computer-use.

---

## Context you need

Joshua has 9 mail accounts in Apple Mail but only TWO are his:
- `jdavis@fcfpawn.com` — work (Gmail MCP is connected to this account)
- `zapvp1@me.com` — personal (iCloud). **Since 2026-08-27 iCloud forwards every personal message into the jdavis Gmail inbox**, so the Gmail inbox is the single place both accounts land. A message whose `toRecipients` is zapvp1@me.com is Joshua's personal mail that arrived via the forward — it is his, never a store's. Read everything through the Gmail MCP; the Unified Search index is a backup only.

The other five (`culpeper@` `waynesboro@` `harrisonburg@` `lexington@` `roanoke@fcfpawn.com`) are STORE STAFF mailboxes. **Never include store-mailbox content in this brief.**

Server-side Gmail filters (9 set 2026-08-26, 11 added 2026-09-22) route jdavis@fcfpawn.com automatically:
- `1-Action` — team, DocuSign, government, banking, legal, insurance (JM Partners), lessors (Silver Bears), RSR, courts, contractors, teachers — stays in inbox
- `2-FYI` — account/security notices, Plaid/Venmo, Apple/Google account mail, Comcast voicemail notices — stays in inbox, low priority
- `3-Vendor`, `4-Auto`, `4-Auto/Already-in-Slack`, `4-Auto/Marketing`, `4-Auto/Receipts-Shipping`, `5-Personal/Bills-Statements`, `5-Personal/Rental-Platforms`, `5-Personal/School` — all skip the inbox

So **anything still in the jdavis INBOX is, by construction, either real mail or a sender no filter knows about yet.**

Label IDs for `label_thread` / `unlabel_thread`: 1-Action=Label_4, 2-FYI=Label_5, 3-Vendor=Label_6, 4-Auto=Label_7, 4-Auto/Already-in-Slack=Label_8, 4-Auto/Marketing=Label_9, 4-Auto/Receipts-Shipping=Label_10, 5-Personal/Bills-Statements=Label_12, 5-Personal/Rental-Platforms=Label_13, 5-Personal/School=Label_14. System label to remove when filing: `INBOX`.

---

## Step 0 — Connector readiness gate
Load the Gmail tools (`ToolSearch select:` the `search_threads`, `get_message`, `label_thread`, `unlabel_thread`, `list_labels` tools of the Gmail connector) and the Slack tools. If a connector errors with not-connected, wait 30 s and re-probe, up to 8 times. A warming connector is NOT a failure. Optionally probe `mcp__Control_your_Mac__osascript` with `do shell script "echo READY"` — if it is absent, skip every osascript step below and use the Read/Write file tools instead; if those can't reach the path either, keep going without the file (the DM is the deliverable).

## Step 0.5 — Noise sweep (self-healing, every run)
Gmail filters only catch senders they already know. Before classifying, sweep automated mail the filters missed and file it with the Gmail MCP: `label_thread` with the target label, then `unlabel_thread` with `INBOX`. Hard limits: never touch a thread containing a message from jdavis@, preston@, scole@ or any @fcfpawn.com person; never file a named human, a bank, a government domain, DocuSign, insurance, a landlord/lessor, a school teacher, or the team. When unsure, leave it in the inbox.

1. Read `/Users/joshuadavis/Documents/Claude/Projects/Communcations/mail-brief/noise-senders.txt` (create it if missing; format: `<sender domain or address>\t<label id>` one per line). For every line, run `in:inbox from:<sender>` and file every matching thread to that label. This keeps the inbox clean between filter updates with no Chrome and no Gmail login.
2. Run `in:inbox newer_than:2d` (pageSize 50, page through). Any thread whose sender is clearly automated — local part noreply / no-reply / donotreply / newsletter / marketing / promo / hello@ or info@ a retail or SaaS brand, or a promo/newsletter/digest/statement subject with no reply expected — gets filed: marketing → Label_9; receipts, shipping, reservations → Label_10; statements or bills with no past-due / declined / failed language → Label_12; rental-platform payout, deposit or sensor notices with no failure / booking / request / message language → Label_13; school broadcast systems (never a teacher) → Label_14. Append each newly filed sender to noise-senders.txt if not already there.
3. Count what you filed and fold it into the "Filed automatically" number in the DM — never its own section, never a sender list.

## Step 1 — Read the inbox
Gmail MCP `search_threads`, query `in:inbox newer_than:1d` (morning run) or `in:inbox newer_than:12h` (afternoon run), pageSize 50, page through. Pull the full message with `get_message` (`messageFormat: PLAIN_TEXT`) only for things that look like they need a reply — never for obvious noise. Personal mail (to zapvp1@me.com) is in this same result set.

## Step 2 — Backup read of personal mail (only if the forward looks broken)
If the inbox shows zero messages addressed to zapvp1@me.com in the last 24 h, the iCloud forward may have stopped. Cross-check the Unified Search index if osascript is available: `sqlite3 "/Users/joshuadavis/Documents/Claude/Projects/Unified Search/index.db"` — `mail` table (`subject, sender, recipients, body, path, mailbox, account, ts`), personal account UUID `7A4E2AF3-C209-4334-B7E1-2A9AD491D2D4`. If the index shows personal mail the Gmail inbox does not, add one FYI line: "Personal mail forwarding looks stopped — worth re-saving the forward in iCloud Mail settings." Otherwise skip this step.

## Step 3 — Classify
Three buckets only:

**NEEDS YOU** — a named human is waiting on a decision, an answer, a signature, or money. Real people, banks, government, landlords, attorneys, insurance, contractors, teachers, the team. Anything carrying 1-Action that is unread. Cap at 8; if there are more, take the 8 most consequential and say how many others there were.

**FYI** — real but no reply needed. 3–5 bullets max.

**FILED** — everything the filters and the noise sweep archived since the last run. A COUNT, never a list.

When unsure whether something needs him, put it in NEEDS YOU.

## Step 4 — Draft the replies
For every NEEDS YOU item, write a ready-to-send reply. **Read the `my-writing-style` skill first and match Joshua's voice.** 2–4 sentences each. If an item can't be answered without information only Joshua has, say what's missing in one line instead of inventing an answer.

Do NOT send anything. Draft only. Joshua sends.

## Step 5 — Anomaly check
Catch the CDNN class of problem (a sender jumping from ~45/day to ~330/day across the store boxes). If osascript is available, query the Unified Search index: last 24 hours, messages per sender domain across ALL accounts, versus that domain's trailing 30-day daily average; flag any domain both above 50/day and more than 3× its baseline. Report at most the top 3 as one plain line each. If osascript is absent or the index is stale (max ts older than 48 h), skip this step silently — do not write "no anomalies" and do not log it as a failure.

## Step 6 — Post ONE Slack DM to D03BHQH5VGT

Dedupe first: read the DM channel and check whether a brief for this same date AND same half-day already posted. If yes, stop — do not double-post.

Format exactly this shape. Plain language. No system names, no label names, no file paths, no counts of tool calls.

```
📬 Mail brief — {Wed Aug 26, morning|afternoon}

NEEDS YOU ({n})
1. {Who} — {the ask in one line}
   Draft: "{ready-to-send reply}"
2. ...

FYI
• {bullet}
• {bullet}

Filed automatically: {n} since {last run}
```

Then, only if Step 5 tripped, add:
```
Worth a look
• {plain-language anomaly line}
```

If NEEDS YOU is empty, say `NEEDS YOU — nothing.` and keep the rest. A quiet brief is a good brief and still ships.

## Step 7 — Save the run record
Write a short STATUS file to `/Users/joshuadavis/Documents/Claude/Projects/Communcations/mail-brief/STATUS-{YYYY-MM-DD}-{am|pm}.md` (Write tool, or osascript heredoc if the file tools can't reach it) with counts by bucket, senders filed by the noise sweep, senders that appeared in the inbox that no filter covers, and anything that failed. Create the folder if needed. This file is the technical record — the DM never is.

## Step 8 — Filter candidates (Monday morning run only)
List any sender that appeared in the inbox 3+ times in the past week and is not matched by an existing filter or the noise list. Append them to the STATUS file under "Filter candidates" and, if they are clearly automated, add them straight to noise-senders.txt so the next run sweeps them. Human senders never go on the noise list. Mention it in the DM as one line only if there are 3 or more automated candidates: "A few new senders are now being filed automatically."

---

## Hard rules
- **Never send, reply to, trash, or spam any email.** Filing (label + remove from inbox) is the only write this task performs, and only on automated mail.
- **Never include store-mailbox content.**
- **Never post to any channel other than Joshua's DM D03BHQH5VGT.**
- **Never touch Bravo, Parallels, Chrome, or computer-use.**
- If the brief would be empty in every bucket, still post it — silence is indistinguishable from failure.