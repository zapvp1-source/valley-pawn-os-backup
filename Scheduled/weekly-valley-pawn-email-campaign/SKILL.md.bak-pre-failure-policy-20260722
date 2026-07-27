---
name: weekly-valley-pawn-email-campaign
description: [DISABLED 2026-05-28 — superseded by the 12-week pre-staged calendar in Brevo (campaigns 19-30) and the vp-deal-of-week-monday-prompt/-pick tasks.] Original: weekly Brevo send.
---

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

You are running the Valley Pawn weekly email campaign. Today is Thursday at 10 AM ET — send day. The campaign goes to the same Brevo subscriber list used by the monthly We Buy Gold & Silver email. Tools: Brevo (web UI via Claude in Chrome), Google Drive (for asset lookups if needed), Slack (for the post-send summary).

==============================
STEP 0 — LOAD CONTEXT
==============================
Read these skills before doing anything else:
1. `valley-pawn-context` — brand voice, colors, store list, phone numbers, addresses, Instagram handle, marketing goals, the "What's Right Is Right" tagline, the 30-day warranty promise, the rule against firearms language, and the 8 standard Brevo template categories.
2. The monthly campaign skill `monthly-we-buy-gold-silver-email` (located at /Users/joshuadavis/Documents/Claude/Scheduled/monthly-we-buy-gold-silver-email/SKILL.md) — mirror its Brevo flow, sender identity, footer, unsubscribe wiring, and UTM convention.

==============================
STEP 1 — PICK THIS WEEK'S THEME (4-week rotation)
==============================
Compute ISO week number of today, then modulo 4:
  - mod 0 → **Deals & Spotlights** — 3–5 hot in-store items or a featured category, tap-to-call CTAs to the store carrying each item.
  - mod 1 → **Education / How It Works** — pawn loans 101, mobile app, free layaway, 30-day warranty, or "how we appraise" — written warmly, no judgment.
  - mod 2 → **New Arrivals** — what just came in this week (electronics, tools, jewelry, instruments). Cycle which store gets the spotlight (round-robin Culpeper → Waynesboro → Harrisonburg → Lexington → Roanoke).
  - mod 3 → **Community / Customer Stories** — staff highlight, local-event tie-in, or a pawn-loan-helped-the-family kind of story (tasteful, never voyeuristic). Family-owned-since-2014 framing.

Never duplicate the monthly gold-and-silver email's pitch. If the date is within 7 days of the 1st of the month, lean further away from gold/silver topics.

==============================
STEP 1.5 — PULL MANAGER SUBMISSIONS FROM SLACK
==============================
On **Deals**, **New Arrivals**, and **Community** weeks the email's content is sourced from a Slack channel where the 5 store managers submit items / events / stories. Pull these BEFORE writing copy — they ARE the copy.

**Source channel:** `#deal-of-the-week` (channel ID `C0AVCANK7E3`). All 5 managers + Preston are members. Managers submit Tuesday morning through Wednesday 4 PM in response to the `weekly-new-deal-request` task's Tuesday post (a separate scheduled task that fires Tue 9:03 AM).

**How to pull:**
1. Call `slack_read_channel` with `channel_id=C0AVCANK7E3` and `limit=30`.
2. Filter to messages posted **since the most recent "submission request" post by Joshua** (the parent of this week's thread). One submission per manager per item; usually 5–10 total messages.
3. Each submission should have: photo (Slack file attachment), item name, category, price, one-sentence pitch. Treat any missing field as a quality flag (see Step 5.5).

**Education-theme weeks (mod 1):** no manager submissions needed — the agent writes the educational piece directly.

**File ID handling — REQUIRED photo pipeline (do not ship placeholder cards):**

Slack file IDs (e.g. `F0B3D5ABX7B`) are NOT email-loadable. Every item must render as a real `<img src="https://...">`. Walk this pipeline for each submission:

1. For each submission message, the Slack file payload has `permalink` (auth-required) and `permalink_public` (no-auth, only if "Get a link" was toggled).
2. **Preferred path — Brevo image library:**
   a. Use Chrome MCP to navigate to `https://app.brevo.com/gallery/list` (Brevo's media library).
   b. For each Slack file, fetch the binary via the workspace bash sandbox (`curl` with the `permalink_public` URL, or via `osascript` shelling out to `curl` with the Slack auth token if private).
   c. Upload via Brevo's gallery "Upload" button — `file_upload` Chrome tool.
   d. Brevo returns a permanent `https://img.brevo.com/...` URL — use that as `<img src>`.
3. **Fallback path — Google Drive public link:**
   a. Save each image to a public folder in Valley Pawn Drive → "Email Campaigns / Weekly / images".
   b. Right-click → Get link → "Anyone with the link can view".
   c. Convert the share URL to a direct-image URL: `https://drive.google.com/uc?export=view&id=<FILE_ID>`.
   d. Note: Drive direct-view URLs throttle under high load. Brevo's library is more reliable.
4. **Last-resort fallback:** if both above fail and there's no time, ship the email **without that store's photo** — use a styled gradient card with the item name and price overlaid, NOT a "[PHOTO: ...]" placeholder. The send must look intentional; placeholders look broken to customers.

If the agent can't get any photo working in time, STOP and DM Joshua. Do not send an email with literal `[PHOTO: ...]` placeholder text — that is broken-looking and worse than no image.

==============================
STEP 2 — WRITE THE COPY
==============================
Voice = warm, confident, honest, community-focused. Tagline "What's Right Is Right" appears once (footer or signoff). 30-day warranty is mentioned at least once.

Subject line: 30–55 characters, specific to this week's theme. Use a preheader (60–90 chars) that adds info, not repetition. Examples per theme:
  - Deals: "5 picks under $200 this week" / preheader "Hand-picked from all 5 Valley Pawn stores."
  - Education: "How a pawn loan actually works" / preheader "No credit check, no judgment — just a fair look at your stuff."
  - New Arrivals: "Just in at Valley Pawn — Lexington edition" / preheader "Tools, electronics, and one piece you have to see."
  - Community: "Meet the Roanoke crew" / preheader "Eight years of doing right by the Valley."

Hard rules:
  - Never mention firearms, guns, ammo, NICS — anywhere, ever. This is a Brevo deliverability + retailer policy issue.
  - Never use the legacy "Dixie Pawn" name — Harrisonburg is Valley Pawn.
  - One clear primary CTA per email (a button). Secondary CTAs are tap-to-call and "Get directions."
  - Honor unsubscribes — Brevo's standard unsubscribe block must be in the footer.

==============================
STEP 3 — BUILD IMMERSIVE BRANDED HTML
==============================
Write the email as a single self-contained HTML file. Mobile-first, max width 600px, table-based layout for email-client compatibility (no flexbox/grid). Inline CSS only.

Brand palette (from valley-pawn-context):
  - Primary Blue:  #0099DD
  - Dark Purple:   #2D1A5E
  - Coral accent:  #F58C8A
  - Light Blue:    #3DB8E8
  - Background:    #FFFFFF / #F7F9FC

Layout:
  1. Hero band (dark purple #2D1A5E background, Valley Pawn logo, week's theme title in bright cyan #0099DD, one-line preheader).
  2. Big editorial photo or illustrated graphic — branded, not stock-cheap. Pull from Canva/Drive if available; otherwise generate a clean styled card.
  3. Body — short, scannable. One headline, 2–4 short paragraphs, bullet rows for items/tips when relevant.
  4. Primary CTA button — coral #F58C8A on dark purple background OR cyan #0099DD on white. Pill-shaped, big tap target (44px+).
  5. Five-store "Find your nearest Valley Pawn" block — name, address, click-to-call (`tel:`), and Google Maps link. Use the canonical phone numbers and addresses from valley-pawn-context.
  6. Footer — Instagram follow link (@valley_pawn → https://instagram.com/valley_pawn), website button (thevalleypawn.com), tagline "What's Right Is Right", legal address (Full Circle Finance Inc, Virginia), Brevo unsubscribe + view-in-browser links.

UTM convention (mirror the monthly):
  All links → `?utm_source=brevo&utm_medium=email&utm_campaign=weekly_<theme>_<YYYY-MM-DD>&utm_content=<slot>`
  where <theme> ∈ {deals, education, newarrivals, community} and <slot> identifies the link (hero, primary_cta, store_culpeper, store_waynesboro, etc.).

Phone links use `tel:+15404455510` format (no spaces, +1 prefix).

**Maps links — use the canonical place URL, NOT a raw-address search.** Searching by address alone (`...query=571+James+Madison+Highway+Culpeper+VA+22701`) lets Google's matcher pick the closest listing, which can land on stale or legacy entries (Harrisonburg in particular pulls Dixie Pawn's legacy GBP photos this way; Culpeper can land on the strip-mall block instead of the storefront). Searching by **business name + city** forces Maps to filter to the verified Valley Pawn GBP — current signage, current photos, current address & suite.

Use this format:
`https://www.google.com/maps/search/?api=1&query=Valley+Pawn+<City>+VA`

Per-store maps URLs:
- Culpeper:      `https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Culpeper+VA`
- Waynesboro:    `https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Waynesboro+VA`
- Harrisonburg:  `https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Harrisonburg+VA`
- Lexington:     `https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Lexington+VA`
- Roanoke:       `https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Roanoke+VA`

(Verified 2026-05-07 against live Google Maps — all 5 resolve to the correct, current Valley Pawn listing with up-to-date storefront photos. Do NOT revert to address-string queries even if the address looks more "specific" — it isn't, because Google indexes legacy listings at the same address.)

UTM still appended after the query, e.g. `&utm_source=brevo&utm_medium=email&utm_campaign=...&utm_content=store_culpeper_map`.

==============================
STEP 4 — SEND VIA BREVO
==============================
Use Claude in Chrome to navigate Brevo. Log in via saved Chrome passwords — never ask Joshua to log in.
  1. Brevo → Campaigns → Create new email campaign.
  2. Campaign name: `Weekly — <Theme> — <YYYY-MM-DD>` (e.g., `Weekly — Deals — 2026-04-30`).
  3. Sender: same sender identity used by the monthly campaign (do not change it).
  4. Subject + preheader from Step 2.
  5. Recipients: same list/segment as the monthly We Buy Gold & Silver campaign.
  6. Content: paste the HTML from Step 3 into the HTML editor (not the drag-and-drop builder — we want pixel control).
  7. Run Brevo's spam/preview check. Fix any flags before scheduling.
  8. Send a test to jdavis@fcfpawn.com first; verify it renders correctly on Gmail mobile + desktop preview.
  9. Schedule or send immediately for 10:00 AM ET today.

==============================
STEP 5 — POST-SEND SUMMARY TO SLACK
==============================
Post to Slack `#email-campiagns` (channel ID `C0APR5WUL2Z` — yes, "campiagns" is the literal channel name; same channel the monthly Gold & Silver campaign posts to). The legacy spec said `#claude-updates` but that channel does not exist in the workspace — always use `#email-campiagns`. Do NOT DM Joshua unless something failed.

**Format — concise, mirroring the `#blog-posts` weekly blog-update style.** Joshua prefers a tight 4-line post, NOT a verbose dump of every UTM slot or KPI target. Use this template exactly:

```
:incoming_envelope: New email is live — *<subject line>*
<one or two warm sentences: theme, hook, recipient count, send time>
:link: <brevo_campaign_url|Weekly — <Theme> — <YYYY-MM-DD> in Brevo>
What's Right Is Right.
```

- Lead emoji is `:incoming_envelope:` and the subject line is bold.
- Body sentence(s) carry the substance: the theme/angle, the audience size, the send time. Don't list UTM slots, don't list KPI targets — those live in the campaign itself and the Drive copy.
- Link line uses `:link:` and a single hyperlinked label (the campaign name from Brevo).
- Sign off with `What's Right Is Right.` — the standing tagline used in `#blog-posts` updates.
- Only add a follow-up line if Brevo flagged a deliverability warning or if a step failed. In that case, add ONE line starting with `:warning:` describing what to look at.

Example (week of 2026-05-07, Community theme):
```
:incoming_envelope: New email is live — *From our Valley Pawn family to yours*
A warm Mother's Day weekend note marking 12 years of doing right by the Valley. One Mother's Day gift CTA, the five-store directory, and our standing 30-day warranty promise. Sent to 9,816 customers at 10:18 AM ET.
:link: <https://app.brevo.com/campaigns/listing/email|Weekly — Community — 2026-05-07 in Brevo>
What's Right Is Right.
```

==============================
STEP 5.5 — MANAGER FEEDBACK DMs (Deals / New Arrivals / Community weeks only)
==============================
After the send, DM each store manager whose submission had something **off or worth notating**. Joshua's rule: only DM if there's a real coaching note — don't spam thank-yous on perfect submissions.

**Send a DM when:**
- Missing required field (photo, item name, price, category, or one-line pitch)
- Submitted a category or sale callout instead of one specific hero item (the format is one item per submission)
- Item description is too vague to drive a click ("nice ring" with no carat / metal / size)
- Submitted after Wednesday 4 PM deadline (note for future, but include the item if there was room)
- Multiple submissions and we only ran one (let them know which made the cut and why)
- Submission triggered a guardrail (firearm-adjacent, brand we don't want to feature, etc.) and was dropped — explain so they don't repeat

**Skip the DM when:** submission was complete, on time, and used in the email as submitted. Silence is good news here — Joshua doesn't want a "great job" boilerplate going to managers every Thursday.

**Tone:** warm, direct, coaching, never scolding. One short paragraph max. Always close with the kind of submission you'd like to see next week (one concrete example). Sign with thanks if appropriate.

**Manager Slack user IDs (DM targets):**
- Culpeper: Sandi `U04C5DL5EKH`
- Waynesboro: Chadd `U04U136MF6V`
- Harrisonburg: Walker `U09UTFT4P7X` / Andrew `U03BFDJH31B`
- Lexington: Uriah `U09H9ES2LKA`
- Roanoke: Benjie `U0631AECK4K`

Example (week of 2026-05-14, Sandi's category-not-item submission):
```
Hey Sandi — quick note on your designer-bags submission. Works as a sale callout, but for future weeks the format is one specific item per submission — like "Coach Willis 1941 crossbody, was $250 now $179." That way each customer who clicks knows exactly what's waiting at Culpeper instead of showing up to a whole case. Keep the bag-sale running in store though — that's a winner.
```

If a submission was missing critical info needed for THIS week's send (e.g. price), DM **before** the send, not after — the email needs the info to go out. See: 2026-05-14 Benjie pre-send DM about the DeWalt DWS779 price.

==============================
STEP 1.6 — CHECK FOR MANAGER REPLIES TO PRE-SEND DMs
==============================
Any pre-send DM you fired in Step 1.5 (missing-info ping to a manager) MUST be followed up. Don't assemble the email without checking for the reply.

**Protocol (executed before STEP 2 copywriting):**
1. Build a list of DMs you sent during pre-send pings: for each, store `{manager_user_id, dm_channel_id, question_summary, item_being_held}`. You get the DM channel_id from the `slack_send_message` response (`message_context.channel_id`).
2. **Wait up to 20 minutes** for replies. If the cron is firing in <20 min, wait until 2 minutes before scheduled send time. (Cron jitter is ±514s — plan for ~5 min slack.)
3. For each DM channel, call `slack_read_channel` with `limit=5` and look for the most recent message from the manager *after* your pre-send DM's `message_ts`. Parse out the answer:
   - Missing price → extract the dollar figure (regex `\$?\d+(\.\d{2})?`)
   - Missing photo → check for an image attachment in the reply
   - Vague description → use the manager's clarifying sentence verbatim
4. If the manager replied with the info: **use it in the email** and proceed.
5. If the manager replied "skip" / "pull it" / "next week": **drop the item from this week's email** and DM Joshua a one-liner FYI.
6. If no reply by the 2-min-before-send cutoff: fall back per the original DM ("stop in for our price" if price was missing, drop the item if photo was missing, etc.) and DM Joshua a one-liner noting the silent miss.

**DM channel IDs (cache for future runs — populate as you discover them):**
- Benjie / Roanoke → `D062UPQEV54`
- Sandi / Culpeper → `D04C5DL5MBR`
- (Add others as their first DM goes out)

**Verified working 2026-05-14:** DM'd Benjie at 9:40 AM about missing price → replied at 9:42 with `$359.99` → cron at 10:08 picks it up. Loop confirmed end-to-end.

==============================
STEP 6 — RECORD-KEEPING
==============================
Save a copy of the rendered HTML and a screenshot of the rendered preview to Google Drive under Valley Pawn Drive → an "Email Campaigns / Weekly" folder (create it if it doesn't exist; record its folder ID by updating valley-pawn-context's Drive folder table afterward).

==============================
GUARDRAILS
==============================
- If the Brevo list is missing or the sender identity has changed, STOP and DM Joshua before sending — don't guess.
- If the rendered email exceeds 100KB or contains broken links, STOP and fix. Gmail clips emails over ~102KB.
- If today is the 1st of the month (gold-and-silver day), shift the weekly send to Friday instead so the two campaigns don't land in the same inbox the same day.
- Do not pull or feature firearm inventory under any condition.
- Open rate target >25%, click rate >3%, unsubscribe rate <0.5% — note these in the Slack summary so we can trend them.

==============================
HARD REQUIREMENTS — EVERY EMAIL (mirrors valley-pawn-context "Email Hard Requirements")
==============================
Three blocks are non-negotiable. If any is missing or broken at the pre-send preview, STOP and fix:

1. **Valley Pawn logo in the header** — `https://i0.wp.com/thevalleypawn.com/wp-content/uploads/2026/03/vp_logo_name-no-tag.png?fit=600%2C67&ssl=1` (served by Jetpack CDN from thevalleypawn.com; verified 200 OK, 7.6KB PNG). Max-width 280px, centered, wrapped in `<a href="https://thevalleypawn.com?utm_source=brevo&utm_medium=email&utm_campaign=...&utm_content=logo">`. **Do not use the legacy `img1.wsimg.com` URL** — that's the old GoDaddy/wsimg CDN path and it now returns HTTP 204 (no content), which is why the logo silently disappeared from the email until 2026-05-14.

2. **Call AND Text — two separate buttons per store, with the phone number visible on BOTH.** Customers text as much as they call. Some email clients silently strip `sms:` links — when that happens, the customer needs to see the number ON the Text button to copy-paste it manually. Use:
   - `<a href="tel:+1<10digits>">📞 Call (XXX) XXX-XXXX</a>`
   - `<a href="sms:+1<10digits>">💬 Text (XXX) XXX-XXXX</a>`
   - Same number on both — Valley Pawn store lines are SMS-enabled.
   - Both buttons within each store's CTA block, AND both within the bottom 5-store directory.
   - Never use "Text Us" or "📱 Message" without the visible number — same dropped-sms-link failure mode.

3. **Full 5-store directory at the bottom** — Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke. Every email. Name + address + Directions (canonical Maps URL) + Call + Text. No exceptions even for single-store-spotlight emails.

Verify all three at the pre-send Brevo preview. Missing any of these blocks = not sendable.

---

## 🔄 STEP 3 IS NOW DUPLICATE-FROM-TEMPLATE (updated 2026-05-27)

The previous version of this skill said to "build immersive branded HTML" from scratch every Thursday. That created instrumentation drift — each send had different UTMs, missing per-store directories, etc. (Confirmed by the 2026-05-27 audit: only the Education send had per-store Maps links; Deals and Memorial Day didn't.)

**Going forward:** every weekly send duplicates from `VP Master Template` (ID 11) and replaces the 10 placeholder markers. See `brevo-context` → "VP Master Template" section for the full marker table.

### Per-send replacements for the weekly rotation

For each Thursday send, fill in:

- `[[CAMPAIGN_SLUG]]` → `weekly_<theme>_<YYYY-MM-DD>` (e.g. `weekly_deals_2026-05-28`)
- `[[HERO_EYEBROW]]` → theme keyword (e.g. `THIS WEEK'S DEALS`, `JUST IN`, `PAWN LOANS 101`, `COMMUNITY`)
- `[[HERO_HEADLINE]]` → 30-55 char headline (same as subject line, or a variant)
- `[[HERO_SUBLINE]]` → 1-sentence warm intro
- `[[BODY_HTML]]` → theme-specific body content:
  - **Deals weeks:** item cards pulled from manager submissions in `#deal-of-the-week`
  - **Education weeks:** numbered-steps explainer (see the Pawn Loans 101 send as reference)
  - **New Arrivals weeks:** item cards from manager submissions, with store callout
  - **Community weeks:** team photo, family-owned story, local-event tie-in
- `[[PRIMARY_CTA_LABEL]]` → action verb appropriate to the theme
- `[[PRIMARY_CTA_URL]]` → `https://thevalleypawn.com` (or a deeplink)
- `[[PRIMARY_CTA_SUB]]` → small text below button
- `[[SUBJECT_FALLBACK]]` → same as subject line

### Don't rebuild

The 5-store directory, hours line, footer, Instagram link, DBA-only legal block, and 30-day warranty trust strip are LOCKED inside the master template. Don't reinvent them per send. If you find a real bug or need a structural change, update the master template (ID 11) once — every future send inherits the fix automatically.