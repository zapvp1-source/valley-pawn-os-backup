---
name: ffl-transfer-email-responder
description: Daily check of Joshua's email/Chekkit inbox for FFL/firearm transfer requests that haven't been answered yet; replies with a link to thevalleypawn.com/ffl-transfer/
---

Domain: 1 — Valley Pawn. Load `enterprise-map` skill context first (light touch is fine).

GOAL (Joshua's standing instruction): anyone requesting an FFL (firearm) transfer needs to be directed to Valley Pawn's FFL Transfer page — https://thevalleypawn.com/ffl-transfer/ — with the link provided so it's easy for them. This task is the daily safety net that catches transfer inquiries which haven't gotten a reply yet. It does NOT replace store staff, who already handle most of these live via Chekkit texting — this task only acts on ones that are GENUINELY still unanswered.

DO NOT ask Joshua anything. Execute directly and silently unless you actually send a customer-facing reply (see reporting rule at the end) or hit a real blocker.

CONTEXT YOU NEED:
- Joshua's Gmail (jdavis@fcfpawn.com) is reachable via the Gmail MCP connector already available in this environment (search_threads, get_thread, reply, label_thread, create_label, list_labels tools).
- A Gmail label "FFL-Transfer-Checked" already exists — use `list_labels` to get its current ID (don't hardcode the ID, it was Label_3 as of 2026-08-22 but always re-look it up).
- Chekkit (dashboard.chekkit.io) is Valley Pawn's customer messaging platform (aggregates Google, Facebook, website chat widget, and "text our number" messages across all 5 stores). When a customer messages any store and no one replies within ~10 minutes, Chekkit emails jdavis@fcfpawn.com an alert with subject "Unanswered Message Alert: <name> (<phone>)". These alert emails explicitly say "REPLYING TO THIS EMAIL WILL NOT RESPOND TO YOUR CUSTOMER" and contain a dashboard link like `https://dashboard.chekkit.io/conversation/<id>?_locationdd...=<location_id>` — you must open that link in Chrome and reply from inside the Chekkit web app, not by replying to the Gmail alert.
- Chekkit login: use Claude in Chrome, navigate to https://dashboard.chekkit.io — it should already be logged in via saved Chrome session/password (jdavis@fcfpawn.com). If it prompts for login, use Chrome's saved password autofill — never ask Joshua to log in himself (standing rule).
- A canned template called "FFL Transfer Info" already exists in Chekkit's Message Templates (Manage Templates in the left sidebar / "Use template" button in any conversation's reply box) with this text: "Hi! Yes, we accept incoming firearm transfers. Full details (our FFL#, address, and a downloadable signed license copy for your seller) are here: https://thevalleypawn.com/ffl-transfer/ - Transfer fee is $25, due at pickup. Have it shipped to us with your name/order # on the package, and bring valid photo ID to complete the ATF Form 4473 when you pick it up. Let us know if you have any questions!" — prefer using this template via the UI where possible; if that's awkward, just type the equivalent message manually with the link included, adapted naturally to the conversation.

STEPS EACH RUN:
1. In Gmail, search `mcp__00007879-ef17-43e5-9d59-6325cd2f0a31__search_threads` (or whichever Gmail MCP id is live this session — search the tool list for a Gmail search_threads tool if the id differs) with a query like:
   `from:support@chekkit.io subject:"Unanswered Message Alert" newer_than:3d -label:FFL-Transfer-Checked`
   Read each matching thread's snippet/body. Keep only ones that plausibly mention an incoming firearm transfer — keywords like "FFL", "transfer", "ship", "shipped", "shipping", "Palmetto", "Brownells", "GunBroker", "PSA", "arrived", "delivery" IN COMBINATION with a firearm reference (gun, rifle, pistol, handgun, firearm) OR just explicitly says FFL/transfer. Skip ones that are clearly about buying/selling other merchandise, wanting to sell a gun outright (that's a buy inquiry, not a transfer-in — different topic, leave alone), reviews, or unrelated chatter.
   ALSO search organic (non-Chekkit) mail: `(firearm OR gun OR pistol OR rifle OR handgun) (transfer OR ship OR shipping OR FFL) newer_than:3d -from:support@chekkit.io -from:wordpress@thevalleypawn.com -from:gunbroker@masterffl.com -from:grabagun.com -label:FFL-Transfer-Checked` — for genuine direct customer emails to jdavis@fcfpawn.com asking about a transfer (rare, but check).

2. For each Chekkit alert candidate: extract the dashboard conversation link from the email body. Open it in Chrome (Claude in Chrome tools). Read the actual conversation. Rule 12 — verify against real output, not the stale alert: check whether a staff member (any name other than the customer) already replied after the customer's message. If YES already answered — do nothing to the conversation, just label the Gmail thread FFL-Transfer-Checked and move on (no customer-facing action, don't re-reply). If NO, it's genuinely still waiting — reply in the Chekkit conversation with the FFL Transfer Info template (or equivalent typed message with the https://thevalleypawn.com/ffl-transfer/ link), then label the Gmail thread FFL-Transfer-Checked.

3. For each organic-email candidate: read the full thread. If it's a genuine unanswered customer question about doing an FFL transfer with Valley Pawn, reply via Gmail `reply` (to the message, not a new email) with a warm, brief reply that answers their question and includes the https://thevalleypawn.com/ffl-transfer/ link (mention the $25 fee and that they should call/text the specific store first). Sign off naturally as Valley Pawn. Then label the thread FFL-Transfer-Checked. If it's already been answered by a human (check Sent messages / prior replies in the thread), just label it Checked and move on.

4. Do not process the same thread twice — the FFL-Transfer-Checked label is exactly for this; always exclude it in your search query per step 1.

5. Do not touch, reply to, or worry about the formal "Website FFL Transfer Request" emails (from wordpress@thevalleypawn.com) or the GunBroker/masterffl.com automated transfer-complete notifications — those are separate existing flows and out of scope for this task.

REPORTING:
- If this run sent zero customer-facing replies (nothing was genuinely unanswered), stay completely silent — no Slack post, no DM. This should be the common case since staff usually beat you to it.
- If this run actually sent one or more replies to a real customer, send Joshua ONE short plain-language Slack DM (search for the right DM channel the way other Valley Pawn tasks do, or use the Slack MCP) summarizing what was sent and to whom (name/phone, which store) — so he has visibility, not because he needs to approve anything after the fact.
- If Chekkit login fails or the Chrome session isn't available, don't loop forever — try once, and if it doesn't work, send Joshua one plain DM saying the FFL-transfer email check couldn't reach Chekkit this run, then stop (per Failure Alert Policy — DM only, no team channels).

Do not ask Joshua any questions. Do not wait for confirmation.