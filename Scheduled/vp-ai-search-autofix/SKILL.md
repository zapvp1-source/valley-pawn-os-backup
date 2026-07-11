---
name: vp-ai-search-autofix
description: Self-healing companion to vp-ai-search-health-check — applies whitelisted, reversible fixes for schema/llms.txt/NAP drift Valley Pawn owns, verifies each fix, logs to the Autofix Log, and posts a Fixed/Needs-you digest to #ai-marketing
model: claude-sonnet-5
---

Runs Mondays 8:30am ET, ~30 minutes after `vp-ai-search-health-check` posts its findings to Slack #ai-marketing (private, ID C0BCEESUANM). Each run starts fresh — everything needed is below. Device for any local/browser work: "mac-studio-2-local".

CONTEXT: vp-ai-search-health-check checks three things weekly: (1) site-wide JSON-LD schema via WPCode snippet #738, (2) /llms.txt via WPCode snippet #742, (3) Google+Bing NAP for all 5 stores. When it finds drift, THIS task attempts the fix, verifies it landed, logs it, and reports. It never touches anything outside the whitelist below — everything else goes to Joshua by name, with the specific reason it can't be automated.

STEP 1 — READ THIS WEEK'S FINDINGS.
Read the most recent message posted by vp-ai-search-health-check in Slack #ai-marketing (C0BCEESUANM) — it starts with "Valley Pawn AI-search health check." Parse what's flagged: schema status, llms.txt status, and per-store NAP drift (Google/Bing).

If everything was reported clean (schema 7/7, llms.txt live, listings 10/10 clean), skip to STEP 3, log one row ("no drift this run"), and stop — do not post to Slack for a clean week (avoid noise on top of the health-check's own clean-week post).

STEP 2 — WHITELIST FIXES (apply only these; each is reversible):
A. Schema (WPCode #738) or llms.txt (WPCode #742) reported missing/broken/inactive → log into thevalleypawn.com WP Admin (WordPress.com MCP connector) → Plugins → WPCode → Snippets, find snippet #738 or #742, and if it shows Inactive, re-activate it (toggle only — do not edit the snippet body). Re-check the live page / https://thevalleypawn.com/llms.txt afterward to confirm the fix actually took.
B. Bing Places NAP drift on a listing Valley Pawn owns (e.g. Harrisonburg wrong street/missing suite, Roanoke missing "Suite C") → invoke the `directory-listing-push` skill SCOPED to just the specific store + field that's wrong ("push the Harrisonburg Bing Places address correction only" — not a full 15-directory blast). Re-check https://www.bing.com/maps?q=valley+pawn+<city>+va yourself afterward. Bing edits can take minutes to a day to reflect — if it hasn't updated yet, log it as "submitted, pending Bing review," not "fixed."
C. Google-side NAP drift on a listing Valley Pawn owns → same pattern via `directory-listing-push` scoped to Google only, then re-verify via Google Maps.

Do NOT touch: any listing Valley Pawn doesn't demonstrably own/administer (duplicate/legacy listings, third-party directories requiring a new claim), anything requiring a new account signup, or any homepage/content copy change beyond what's already documented as canonical in `valley-pawn-context`. Those go to STEP 4.

STEP 3 — LOG EVERY ACTION.
Append one row per finding to the "Valley Pawn — AI Search Autofix Log" Google Sheet (ID 1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY, Valley Pawn Drive > Weekly KPIS) — columns: Date, Source Task, Finding, Category (auto-fixed / submitted-pending / needs-Joshua), Action Taken, Verification Result, Status, Notes/Link. Log this whether the fix succeeded, is pending, or wasn't attempted — the point is a complete audit trail of anything touching live systems.

STEP 4 — NEEDS-JOSHUA QUEUE.
Anything outside the whitelist, or a whitelisted fix that failed verification after one retry, gets named specifically — not "some drift remains." State what it is and the one concrete reason it needs a human call (new account, ownership/claim required, judgment call).

STEP 5 — POST TO SLACK #ai-marketing (ID C0BCEESUANM; do NOT DM anyone).
Only if there was something to act on (see Step 1). Post once:
"🔧 _Valley Pawn — AI-search autofix (week of <date>)_ — Fixed: <n> · Pending: <n> · Needs you: <n>"
Then one skimmable line per item under Fixed / Pending / Needs-you (skip empty sections). Keep it phone-readable.
*Sent using Claude*
