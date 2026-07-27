---
name: ebay-title-enrichment-backlog
description: Daily: work through the backlog of cryptic model-only eBay titles across all 5 stores — look up each product, write a proper keyword title, and apply. Runs until the backlog is clear.
model: claude-sonnet-5
---

Continue the eBay TITLE-ENRICHMENT BACKLOG for all 5 Valley Pawn stores until it is clear. Goal: rewrite the remaining genuinely-weak short titles — CRYPTIC brand+model-only tool/electronics listings with no product-type description (e.g. "Ryobi Tools P519VN", "Hitachi Dh 40FB", "Hart Tool HPCS01VN", "Eaton AHCL360C") — into proper ~80-character keyword titles, and apply them. LEAVE already-good titles alone: jewelry with karat/weight/size (e.g. "Gold Earrings 14K Yellow Gold 1dwt"), vinyl records with year+artist+album, and clearly-named games that already have a platform.

TOOLS: Run scripts on the Mac using the Control-your-Mac osascript tool (`do shell script "..."`). eBay tokens/creds live in ~/ebay_weekly_rankings.py. eBay API is reachable from the Mac.

STEPS each run:
1. Refresh the working list: `/usr/bin/python3 ~/ebay_short_titles_pull.py` — writes ~/ebay_short_titles.json (all current active titles under 50 chars, with id/store/title/price).
2. Read ~/ebay_title_enrich_state.json — these item IDs are already enriched; SKIP them.
3. From ~/ebay_short_titles.json, pick up to 20 titles that are CRYPTIC MODEL-ONLY (a brand plus a model number with no product-type word), not already enriched, and not jewelry/records/already-named-games. Prioritize higher-priced items first.
4. For each, WEB SEARCH "<brand> <model>" to identify the real product (type + key spec). Then write a clear ~80-char title: Brand + Product Type + Model + a key spec + condition only if known. NEVER fabricate specs you cannot confirm; if a model can't be identified, skip it (leave it for a human) rather than guess.
5. Save the {ItemID: new_title} pairs to ~/backlog.json (JSON object) and apply: `/usr/bin/python3 ~/ebay_title_apply.py ~/backlog.json --apply`. This records originals in ~/ebay_title_enrich_state.json so every change is reversible.
6. DM Preston on Slack (post to user_id U03BWMEM9GR as the channel_id) a one-line progress note: how many titles you enriched this run and roughly how many cryptic titles remain. When there are no cryptic model-only titles left to fix, DM "eBay title-enrichment backlog is clear ✅" and mention this task can be disabled.

All title changes are reversible via ~/ebay_title_apply.py <file> --revert. Consult the ebay-context and valley-pawn-context skills for brand voice. Keep going a batch per day until the backlog is clear.