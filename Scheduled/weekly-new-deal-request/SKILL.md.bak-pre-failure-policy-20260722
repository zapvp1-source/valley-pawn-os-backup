---
name: weekly-new-deal-request
description: [DISABLED 2026-05-28 — superseded by vp-deal-of-week-monday-prompt running Mondays 8am in #deal-of-the-week.] Original: Tuesday DM to managers asking for deals.
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

You are running the Valley Pawn weekly Deals-of-the-Week request. Today is Monday, 9 AM ET. Your job is to set up the content pipeline for Thursday's weekly email so it features REAL items from REAL stores with REAL photos — not generic stock copy.

==============================
STEP 0 — LOAD CONTEXT
==============================
Read `valley-pawn-context` for the store list, the employee directory (each store's manager), and the current week's theme expectations.

Compute this week's email theme using the same ISO-week-mod-4 logic as `weekly-valley-pawn-email-campaign`:
  - mod 0 → Deals & Spotlights
  - mod 1 → Education / How It Works
  - mod 2 → New Arrivals
  - mod 3 → Community / Customer Stories

Store managers (DM each on Mondays):
- Harrisonburg → Andrew
- Culpeper → Sandi
- Lexington → Uriah
- Waynesboro → Chadd
- Roanoke → Benjie

==============================
STEP 1 — ENSURE THE SUBMISSION CHANNEL EXISTS
==============================
The collection channel is `#deals-of-the-week` (private, members = Joshua + Preston + the 5 store managers). If it doesn't exist yet, post a one-time setup message in `#claude-updates` (channel ID `C0ARGG65YQM`) asking Joshua to create it and add the managers — don't try to create channels yourself. Wait until it exists before continuing the run.

==============================
STEP 1.5 — FIRST-RUN KICKOFF (only on the very first run, or when a brand-new manager joins the channel)
==============================
Detect the first run by reading `#deals-of-the-week` history with slack_read_channel — if there are zero prior posts from this task, send the kickoff message below INSTEAD OF the normal weekly ask. After the kickoff, also DM each manager individually so they don't miss it. From the second run onward, skip Step 1.5 and go straight to Step 2.

Kickoff post to #deals-of-the-week (first run only):

> *Hey team — new program: "Deals of the Week" + weekly email* 👋
>
> *What we're doing:* Every Thursday Valley Pawn sends a weekly email to ~10,000 customers across all 5 stores. Going forward, that email is built from items YOU pick — real stuff actually sitting on your floor right now, with photos you take. No more generic stock content. The customers showing up for these items will be your customers, walking into your store.
>
> *What you need to do — every Monday through Wednesday:*
>
> Reply to my Monday post in this channel with *2–3 items per store* you want featured. For each item:
>
> 1. *Photo* — snap one with your phone. Well-lit, clean counter or display, item facing camera. Staff hand for scale is fine. Real and recent beats fancy and old.
> 2. *Item name* — like "DeWalt 20V Cordless Drill Kit" or "Gold Rope Chain, 22 inch"
> 3. *Category* — Tools / Electronics / Jewelry / Music / Outdoors / Other
> 4. *Price* — and the original price too if it's marked down
> 5. *One sentence on why it's a good pickup* — "barely used", "rare model", "great for jobsite", "in the case for $200 less than retail" — whatever's true
>
> *When:*
> - *Monday morning:* I post the request in this channel
> - *Mon → Wed 4 PM:* you reply in the thread with your items
> - *Wednesday 4 PM:* deadline. After that I build Thursday's email from whatever's in the thread
> - *Thursday 10 AM:* email sends with your items + photos to the customer list
>
> *If your store has nothing standout that week*, just reply "skip" so I know not to wait on you. Better to skip than send a weak item.
>
> *On community weeks* (one out of every four), instead of items I'll ask for *real local events in your town* (festival, parade, school event, charity, market) or *a customer story you have permission to share*. Same Wednesday 4 PM deadline.
>
> *Hard rules:* no firearms / guns / ammo in the email — Brevo and email providers flag those. Family-friendly events only on community weeks. If your item or event might bump up against either, ask Joshua first.
>
> Questions? Reply here or DM me. First weekly request goes out next Monday — get ready to start snapping photos. 📸

DM each manager (Andrew, Sandi, Uriah, Chadd, Benjie) individually with a short heads-up + the channel link. Use slack_search_users to look up each by first name (filter to Valley Pawn workspace), then slack_send_message:

> Hey [Name] — quick heads-up: I just posted a kickoff in #deals-of-the-week explaining a new program where the Thursday email gets built from real items + photos you submit. Take 2 min to read it when you have a sec, and let me know if anything's unclear. First weekly request goes out next Monday morning. Thanks for helping make these emails actually useful instead of generic.

==============================
STEP 2 — POST THE WEEKLY ASK (every Monday from the second run onward)
==============================
For Deals & Spotlights / New Arrivals / Education weeks (item submissions), post a single message to `#deals-of-the-week`:

> *Deals of the Week — submission request for <Theme> email (sending Thursday <YYYY-MM-DD>)*
>
> Hey team — for this Thursday's email I need *2–3 items per store* that you'd actually want to pitch this week. Reply in this thread by *Wednesday 4 PM* with:
>
> 1. *Photo* (just snap one with your phone, well-lit, on a clean counter — staff hand for scale is fine)
> 2. *Item name* (e.g., "DeWalt 20V Cordless Drill Kit")
> 3. *Category* (Tools / Electronics / Jewelry / Music / Outdoors / Other)
> 4. *Price* (and original price if it's marked down)
> 5. *Why it's a good pickup* (one sentence — "barely used", "rare model", "great for jobsite", whatever's true)
>
> One reply per item. Don't overthink the photo — real and recent beats fancy and old. If your store has nothing standout this week, just reply "skip" so I know.

DM the message thread link to each store's manager (Andrew/Sandi/Uriah/Chadd/Benjie) so they get a personal nudge.

For Community / Customer Stories weeks, post a different request:

> *Community email — submission request (sending Thursday <YYYY-MM-DD>)*
>
> This week's email is community-focused. Reply in this thread by *Wednesday 4 PM* with one of:
>
> - *A real upcoming event* in your store's town that customers might care about (festival, school event, parade, charity, market, etc.) — name + date + a one-line note on why it matters
> - *A staff highlight* — a teammate worth featuring (years with us, story, photo if they're cool with it)
> - *A short customer story* with permission — "the loan paid for the new transmission" / "the layaway is for her son's first guitar" — keep it tasteful, no last names

==============================
STEP 3 — IF IT'S A "DEALS"-TYPE WEEK, ALSO PULL FROM eBAY/BRAVO
==============================
Use Chrome MCP to scan the Valley Pawn eBay store for the 5–10 most recently listed items with strong photos. Save listing URLs + photo URLs to a working note in Google Drive (Valley Pawn Drive → Email Campaigns / Weekly Working Notes / <ISO-week>) so Thursday's run can use them as backup if a store doesn't submit by Wednesday 4 PM.

Same for Bravo POS — call the `bravo-store-cycle` skill to log into each store, pull the week's intake list, and note items with photos.

==============================
STEP 4 — IF IT'S A "COMMUNITY" WEEK, COLLECT REAL LOCAL EVENTS
==============================
For each Valley Pawn city, search for upcoming events the week the email will send (Thursday → following Sunday). WebFetch:
  - Culpeper: https://www.visitculpeperva.com/events / https://www.culpeperdowntown.com/events
  - Waynesboro: https://www.waynesboro.va.us/calendar / https://visitwaynesboro.org/events
  - Harrisonburg: https://www.visitharrisonburgva.com/events / https://hburgnews.com/events
  - Lexington: https://www.lexingtonvirginia.com/events / https://www.lexrocknews.com/events
  - Roanoke: https://www.visitroanokeva.com/events / https://downtownroanoke.org/events

Capture event name, date(s), short description, and a representative photo URL. Save to the same week's working note. Avoid firearms-adjacent events, partisan political events, anything with content concerns. Family-friendly + community-positive only.

==============================
STEP 5 — POST A SUMMARY TO #claude-updates
==============================
Post a brief Mon-morning status:
  - Which theme this week is
  - Slack thread link to the request post
  - Pre-pulled backups (eBay item count, Bravo intake count, # of events found)
  - The Wednesday 4 PM deadline reminder
  - Link to the working note in Drive

==============================
GUARDRAILS
==============================
- Never DM employees outside the 5 store managers list.
- Never include items in working notes that violate the no-firearms rule, even if a manager submits one — silently skip and DM Joshua a heads-up.
- Don't auto-DM Joshua or Preston about every submission — they're already in the channel.
- The Wednesday 4 PM deadline isn't enforceable by Claude — just post one polite reminder in the thread on Wednesday at noon if a store hasn't submitted.
- Slack file URLs require the workspace token to render in email — when copying photos from the thread, download via the Slack API, then upload to a public-readable Drive folder or Brevo's image library before referencing them in HTML.