---
name: vp-deal-of-week-monday-pick
description: Every Monday 12:30pm ET — compile ALL qualifying Deal of the Week submissions (one per store), fill the campaign draft with every deal block, and schedule it for Thursday 10am ET
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
You are running Valley Pawn's Deal of the Week compiler — the work that turns Monday's Slack submissions into a scheduled Thursday email. EVERY qualifying store submission is featured, not just one winner.

CONTEXT:
- Companion task `vp-deal-of-week-monday-prompt` ran at 8 AM today and posted the submission prompt in Slack `#deal-of-the-week`.
- Companion task `vp-deal-of-week-monday-reminder` runs at 11 AM today and pings any store that hasn't submitted yet.
- Up to 5 store managers (one per store) had until 12 PM to reply in that thread with: photo, item name+brand, price, store+name, one-sentence pitch.
- This task compiles ALL qualifying submissions, fills the placeholder block in the upcoming Thursday's Brevo campaign draft with one deal block per store, and schedules the campaign to send Thursday 10:00 AM ET.

STEP 0 — ENSURE BREVO CREDENTIALS ARE AVAILABLE (SELF-HEAL)
This task runs in an isolated sandbox whose home directory is NOT the Mac's home, so `~/.config/valley-pawn/brevo_api_key` can be empty or missing even though the real key exists on the Mac at that path. Before any Brevo call, guarantee the key is present:
1. In bash: `KEY=$(cat ~/.config/valley-pawn/brevo_api_key 2>/dev/null); echo ${#KEY}`. If the length is roughly 80+ characters, the key is already present — skip to STEP 1.
2. If empty/missing, bridge it from the Mac using the Control-your-Mac osascript tool: run `do shell script "base64 < ~/.config/valley-pawn/brevo_api_key"` to read the key as base64. Then in bash: `mkdir -p ~/.config/valley-pawn && echo "<BASE64_FROM_OSASCRIPT>" | base64 -d > ~/.config/valley-pawn/brevo_api_key && chmod 600 ~/.config/valley-pawn/brevo_api_key`.
3. Verify: `curl -s -o /dev/null -w "%{http_code}" -H "api-key: $(cat ~/.config/valley-pawn/brevo_api_key)" https://api.brevo.com/v3/account` must return `200`. If it does not return 200 after the bridge attempt, treat this as irrecoverable: stay completely silent on Slack (per the failure policy) and report the blocker in your final message only. Do NOT proceed.

STEP 1 — DETERMINE THE TARGET THURSDAY
Today is Monday. The target send date is THIS Thursday at 10:00 AM EDT (use UTC-4 in Mar–early Nov DST window; UTC-5 (EST) otherwise; figure out DST yourself based on today's date). Compute the ISO timestamp for that Thursday.

STEP 2 — FIND THE UPCOMING THURSDAY'S CAMPAIGN DRAFT
- Brevo API base: `https://api.brevo.com/v3`
- API key file: `~/.config/valley-pawn/brevo_api_key`
- GET `/emailCampaigns?status=draft&limit=50` and find a draft whose name contains the target Thursday's date in the form `Month DD, YYYY` (e.g. "June 11, 2026"). The drafts use names like `W2 — Gold Pulse + First Deal — June 11, 2026`.
- If no draft matches, STOP and DM Joshua (zapvp1@me.com): "No Brevo draft staged for this Thursday — Deal of the Week skipped this week." Then exit.
- If matched, record the campaign ID and current htmlContent. Also fetch the existing recipients block so we don't overwrite it on PUT.

STEP 3 — READ THE THREAD REPLIES
- Find the original 8 AM submission prompt in `#deal-of-the-week` (the most recent post by the bot/automation containing "Deal of the Week submissions open now").
- CRITICAL FRESHNESS GUARD: Only act on a prompt posted TODAY (this same Monday). Check the prompt message's timestamp. If the most recent "Deal of the Week submissions open now" post is from a PRIOR week (not today's date), the companion prompt did NOT run this week — do NOT reuse last week's thread or its submissions. Treat this as ZERO submissions and follow the zero-submissions path in STEP 4 (post the "No qualifying submissions this week" note and send theme-only).
- Read the thread replies using `slack_read_thread` (load via ToolSearch if not loaded).
- Each reply should contain photo + item name + price + store + manager name + pitch. Parse the structured info from each reply.

STEP 4 — VALIDATE & ORDER ALL SUBMISSIONS (NO PICKING ONE WINNER)
Build the list of submissions to feature. Include EVERY submission that has BOTH a photo AND a price — these are "qualifying." 
- A submission missing a photo OR a price is NOT renderable; skip it (do not feature it) and note it for the Slack/DM summary.
- If a store submitted more than once, keep that store's most recent qualifying reply (still one block per store).
- Order the qualifying submissions by store in this fixed order: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke. (Stores with no qualifying submission are simply absent.)
- Do NOT score, rank, or pick a single winner. All qualifying deals are featured equally, using the same block design.
- If ZERO submissions qualify: do not force anything. Post in `#deal-of-the-week`: "No qualifying submissions this week — Thursday's send will run with the theme content only." Then proceed to STEP 6 with an empty deal list.
- Let N = the count of qualifying submissions (0 to 5). N drives the section header wording in STEP 6 — never claim more coverage than actually qualified.

STEP 5 — DOWNLOAD EVERY QUALIFYING PHOTO AND UPLOAD TO BREVO MEDIA LIBRARY
For EACH qualifying submission:
- Download the photo from Slack (use the file's `url_private` with `Authorization: Bearer <slack-bot-token>` if available, OR use the `slack_read_thread` file URLs).
- Upload to Brevo via POST `/v3/media` (multipart form). Record the permanent CDN URL for that submission.
- If a single photo retrieval fails, fall back to vp-hero-image skill to generate a cinematic-premium product render from that item's description. If even that fails for one submission, drop only that submission (skip its block) — do not abort the whole run.

STEP 6 — FILL THE PLACEHOLDER BLOCK IN THE DRAFT WITH ALL DEAL BLOCKS
The draft contains a single marker `<div style="border: 2px dashed #c97b3a; ...">DEAL OF THE WEEK — POPULATED MONDAY ...</div>` (the styled placeholder block).

If the deal list is empty: remove this entire placeholder div from the HTML (replace with empty string).

If there are qualifying deals: replace the single placeholder div with a small section header followed by ONE deal block per qualifying submission, concatenated in the store order from STEP 4. Use the EXISTING deal-block design — do NOT redesign it — just repeat it once per store.

Section header (insert once, above the first block) — the wording MUST match how many stores actually qualified (N from STEP 4). Never claim "each store" unless every store is actually featured:
- If N == 5 (all five stores qualified): use `THIS WEEK'S DEALS — ONE FROM EACH STORE`
- If N < 5 (one or more stores didn't submit or didn't qualify): use `THIS WEEK'S DEALS — {N} STORES FEATURED THIS WEEK` (e.g. "THIS WEEK'S DEALS — 4 STORES FEATURED THIS WEEK")

```html
<p style="margin: 0 0 24px 0; font-size: 12px; letter-spacing: 2px; color: #c97b3a; font-weight: bold;">{HEADER_TEXT_PER_RULE_ABOVE}</p>
```

Per-submission deal block (repeat for each qualifying submission, substituting the variables):
```html
<div style="margin: 0 0 32px 0;">
  <p style="margin: 0 0 8px 0; font-size: 12px; letter-spacing: 2px; color: #c97b3a; font-weight: bold;">{STORE_UPPER}</p>
  <h2 style="margin: 0 0 12px 0; font-size: 24px; line-height: 1.3; color: #1a1a1a;">{ITEM_NAME}</h2>
  <p style="margin: 0 0 16px 0; font-size: 16px; line-height: 1.5; color: #444;">{PITCH_ONE_LINE}</p>
  <p style="margin: 0 0 20px 0; font-size: 32px; line-height: 1; color: #1a1a1a; font-weight: bold;">${PRICE}</p>
  <img src="{HERO_URL}" alt="{ITEM_NAME}" style="width: 100%; max-width: 540px; height: auto; display: block; margin: 0 0 16px 0;" />
  <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+{STORE}+VA&utm_source=brevo&utm_medium=email&utm_campaign={CAMPAIGN_SLUG}&utm_content=deal_of_week_{store_lower}" style="display: inline-block; padding: 14px 28px; background: #c97b3a; color: #fff; text-decoration: none; font-weight: bold; font-size: 16px; border-radius: 4px;">See it at our {Store} store</a>
  <p style="margin: 12px 0 0 0; font-size: 13px; color: #777;">Submitted by {MANAGER_NAME}. While supplies last — usually one of a kind.</p>
</div>
```

Between consecutive deal blocks, insert a thin divider so the stacked deals read cleanly:
```html
<hr style="border: none; border-top: 1px solid #e5e5e5; margin: 0 0 32px 0;" />
```
(Place a divider before every block except the first.)

Use the existing `[[CAMPAIGN_SLUG]]` value already in the rest of the email — find any existing `utm_campaign=` parameter in the htmlContent to copy the slug. Keep `utm_content=deal_of_week_{store_lower}` distinct per block so per-store clicks are trackable.

STEP 7 — UPDATE THE DRAFT AND SCHEDULE
PUT `/emailCampaigns/{id}` with:
- `htmlContent`: the modified HTML (single placeholder replaced by header + all deal blocks)
- `scheduledAt`: this Thursday's 10:00:00 with the right timezone offset (e.g. "2026-06-11T10:00:00.000-04:00")

Verify by GETting the campaign back and checking status is `queued`.

STEP 8 — POST CONFIRMATION TO SLACK AND DM JOSHUA
Post in `#deal-of-the-week`:
"This week's email features {N} deals — {comma-separated list of "ITEM_NAME ({STORE})"}. Drafting Thursday's send now." If any store was skipped for missing photo/price, add: "Skipped (incomplete): {store(s)}."

DM Joshua (zapvp1@me.com):
"Thursday email is scheduled with {N} store deals: {list each as ITEM_NAME — $PRICE — STORE}. Campaign: {campaign name}. Subject: {subject}. Preview: https://my.brevo.com/camp/edit/{campaign_id}/email-template. Skipped: {any incomplete stores, or 'none'}. Anything to tweak?"

STEP 9 — BAILOUT BEHAVIOR
If ANY step fails irrecoverably, DM Joshua with a clear short summary: "Deal of the Week automation failed at [step]. Reason: [one line]. The Brevo draft is still in [status]. You'll need to fix it manually." Do not leave a scheduled send in an inconsistent state.

Report a brief outcome line in your final message.

<!-- migrated to working model 2026-06-15 -->
<!-- updated 2026-07-16: header wording now reflects actual store count (N) instead of always claiming "one from each store" -->

---

## HARDENING ADDENDUM (2026-08-21) — THIS SECTION SUPERSEDES STEP 5 AND ANY CONFLICTING STEP ABOVE.

**WHY:** STEP 5's image upload endpoint `POST /v3/media` DOES NOT EXIST in the Brevo API (returns `{"code":"not_found"}`). Every run since 2026-07-27 died silently there: campaigns W10, W11, W12 were never populated and never scheduled — the Thursday email went dark for 3 weeks with no DM. Two rules fix this permanently:

**RULE 1 — IMAGE UPLOAD, PROVEN PATH (do this instead of Brevo /v3/media):** upload photos to the WEBSITE media library and use those URLs in the email. Full pipeline (executed successfully 2026-08-21): Slack file → Chrome `open_url` on `https://files.slack.com/files-pri/T03BL4W1DCL-{FILE_ID}/download/{lowercased_filename}` (lands in ~/Downloads; the Keychain bot token has no files:read, don't try files.info) → `sips -Z 1200 -s format jpeg` → localhost:8787 server WITH `Access-Control-Allow-Private-Network: true` + OPTIONS 204 → in Chrome on `https://thevalleypawn.com/wp-admin/post.php?post=10&action=edit`, scrape nonce (`createNonceMiddleware\("([a-f0-9]+)"`), plain fetch POST blobs to `https://thevalleypawn.com/wp-json/wp/v2/media` (execute_javascript is an isolated world — window.wp undefined is NORMAL; return async results via body data-attributes). Optionally ALSO import to Brevo gallery afterwards via `POST /v3/emailCampaigns/images` with `{"imageUrl": "<the public WP URL>"}` — that endpoint only accepts real public URLs, never data: URIs.

**RULE 2 — THE CAMPAIGN MUST NEVER STAY UNSCHEDULED.** Whatever happens with images or submissions, this task's run is NOT complete until the Thursday campaign is status queued/scheduled (or sent). If every image fails, schedule theme-only (existing zero-submission path). If even scheduling fails, the failure DM to Joshua is mandatory. A run that leaves the campaign in draft is the defect that caused the 3-week outage — never repeat it.

**VERIFY AGAINST OUTPUT:** after scheduling, re-GET the campaign and confirm status != draft AND htmlContent no longer contains 'POPULATED MONDAY'. Only then post the summary to #deal-of-the-week.
