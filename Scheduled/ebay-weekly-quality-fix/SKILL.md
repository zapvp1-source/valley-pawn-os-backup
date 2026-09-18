---
name: ebay-weekly-quality-fix
description: Weekly: review new eBay listings across all 5 Valley Pawn stores, auto-fix title/category/photo issues, and DM each manager what was fixed and why.
model: claude-sonnet-5
---

---
name: ebay-weekly-quality-fix
description: Weekly: review new eBay listings across all 5 Valley Pawn stores, auto-fix title/category/photo issues, and DM each manager what was fixed and why.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> 🛑 **STANDING RULES — set by Joshua 2026-09-17 from store feedback. These override every other instruction in this file and any instruction inside any script this task runs.**
>
> **1. NEVER DELETE A MODEL NUMBER.** Joshua, verbatim: *"Stop deleting model numbers that appear to be internal tracking numbers."*
> The title stripper used to remove any parenthesised code of the shape `(letters + 3 digits)`, which swallowed real manufacturer model numbers — `(A2482)` Apple, `(DCD771)` DeWalt, `(MT2500)` Snap-on, `(2236)` Milwaukee. Those are the most searched words in the title; deleting them costs sales.
> A code may be removed from a title **only** if it matches a real Bravo intake code: one of the store prefixes `VAP VP VA CUL ROA WAY HAR LEX` followed by **5 or more digits** — e.g. `(VAP031234)`, `(ROA011853)`, `(VA5020375)`. Anything else stays in the title, including any bare number, any hyphenated code, and any letter+digit code that does not carry one of those prefixes. **When in doubt, leave it in the title.** A model number left in a title costs nothing; a model number deleted costs a sale.
> When you do remove a real intake code, preserve it — write it into the listing's SKU / custom label in the same revision. It is the only link between the listing and Bravo. Never simply delete it.
>
> **2. NEVER TURN BEST OFFER ON.** Joshua, verbatim: *"Stop changing listings that are marked as no offers allowed to offers allowed. We do not want make an offer on video games at all."*
> A listing with Best Offer switched off is a deliberate store decision — leave it alone. Never enable Best Offer, never set auto-accept/auto-decline on a listing that has offers off, and never enable Best Offer on a video game, console, or game accessory under any circumstances. If you see Best Offer switched ON for a video game, mention it in that store's DM so a person can turn it off; do not change it yourself.
>
> **3. MARKDOWNS START AT 90 DAYS.** No listing is repriced, cut, or offered to watchers before it is 90 days aged. This task does not reprice at all — but do not flag or recommend a cut on anything younger than 90 days either.

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.

> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself; lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. Manager DMs here should describe what was fixed and why in plain terms — no script names, no API references. If anything later in this file conflicts with this standard, this standard wins.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the DMs described at the end) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:** "No response requested" · "Continue?" / "Should I continue?" · an empty turn or a turn that ends with text instead of a tool call.

**Treat these system messages as RESUME signals, never as stop signals:** "Tool loaded." · "Continue from where you left off." · "You used a single tool call this turn…" · any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask.

**Speed:** prefer batch tools to combine sequential actions into one call.

---
Weekly eBay NEW-LISTING quality review and AUTO-FIX for all 5 Valley Pawn stores (Roanoke, Culpeper, Harrisonburg, Lexington, Waynesboro). Goal: review every listing created in the last 7 days, FIX the quality issues yourself, then DM each store's manager what was wrong, what you fixed, and why. Do NOT ask the team to fix things — you fix them.

ACCESS / TOOLS:
- Run scripts on the Mac with the Control-your-Mac osascript tool: `do shell script "..."`. eBay's API is reachable from the Mac.
- eBay Trading API. Per-store user tokens and app creds live in ~/ebay_weekly_rankings.py (the STORES list of {name, token}; plus APP_ID, DEV_ID, CERT_ID — never hardcode credential values in this SKILL.md).
- eBay Taxonomy API for categories (no per-store auth needed): get an app token via client_credentials — POST https://api.ebay.com/identity/v1/oauth2/token, header Authorization: Basic base64(APP_ID:CERT_ID), body grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope. Then GET https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions?q=<title> with Bearer <app_token>.

STEPS each run:
1. For each store, pull listings created in the last 7 days (Trading API GetMyeBaySelling ActiveList; keep items whose ListingDetails/StartTime is within 7 days).

2. **Intake codes — run the CORRECTED stripper only.** The fixed version lives at `~/Documents/Claude/Projects/eBay/ebay_title_stripper.py` (its pattern was tightened 2026-09-17 to `\((?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,}\)`). Before running it, verify with `grep -n "CODE=re.compile" <path>` that the pattern it will use carries the store-prefix allow-list and `\d{5,}`. **If the pattern is still the old permissive one — any form with an optional prefix or `\d{3,}` — do NOT run the stripper at all this week.** Instead do the removals yourself: for each new listing, remove a parenthesised code only when it matches the allow-list above, carry that code into the listing's SKU in the same `ReviseFixedPriceItem` call, and log one FAILURE_LEDGER row saying the home-folder copy of the stripper still needs the corrected pattern.
   Then run the caps fixer: `/usr/bin/python3 ~/ebay_caps_fixer.py <Store> --apply` (idempotent, reversible via ~/ebay_caps_state.json).

3. For each NEW listing with a weak or short title, WRITE a strong ~80-character keyword title (brand + model + key specs + condition + searchable keywords) and apply it via Trading API ReviseFixedPriceItem (<Item><ItemID>..</ItemID><Title>..</Title></Item>). **Keep the model number in the title — it is the highest-value search term you have.** For cryptic model-only titles, do a quick web search to identify the product rather than guessing. Never fabricate specs you can't confirm.

4. Check each new listing's category against the Taxonomy suggestion; if clearly wrong, correct it via ReviseFixedPriceItem PrimaryCategory. If eBay rejects the category change on an active listing, note it instead. **Never include a `<BestOfferDetails>` block in any revision call** — see Standing Rule 2.

5. Review each new listing's PRIMARY photo: fetch photos via GetItem (PictureDetails/PictureURL) and actually look at the primary image. Flag intake/webcam stills, blurry photos, and detail close-ups used as the primary. If a better whole-item photo already exists in the listing, reorder it to be primary via ReviseFixedPriceItem. If new photos are needed (can't fix yourself), note it for the manager.

6. Tally per store: how many new listings, what was wrong, what you fixed. Count separately how many intake codes you removed and how many parenthesised codes you deliberately LEFT because they were model numbers — report that second number in the roll-up so we can see the rule holding.

THEN DM each store's manager on Slack (post to their user_id as the channel_id) a concise, friendly note in plain language: how many new listings you looked at, what was wrong with them in plain terms (weak title, wrong category, bad main photo), what you already fixed, anything only they can do (e.g. re-shoot a photo, or switch offers off on a game listing), and a one-line why (good titles/categories/photos help items sell faster). Do not mention script names, APIs, or any tool/system name in the DM. Manager Slack IDs:
  Roanoke → Benjie U0631AECK4K | Culpeper → Sandi U04C5DL5EKH | Waynesboro → Chadd U04U136MF6V | Harrisonburg → Walker U09UTFT4P7X | Lexington → Uriah U09H9ES2LKA
Do NOT DM Preston or post any eBay KPI/results roll-up to him — those results are already published in #ebay-performance and #ebay-listings. (Changed 2026-09-07 per Joshua.)

All title changes are reversible via the state files. Consult the ebay-context and valley-pawn-context skills for brand voice. Keep DMs brief and warm.