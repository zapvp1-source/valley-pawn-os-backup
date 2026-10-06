# Marketing restart plan — 2026-10-05

## Ground truth (checked 10/5, source of record)
- **Root cause:** every marketing producer read/wrote files through the Mac connector (osascript), which
  scheduled Claude sessions lost on 9/17. They were then parked (Batch 3 = external actions) pending the
  10/6 cloud move. Monitors (AI-search health, AI-visibility metrics, social recap, Publer analytics) kept running.
- **Email (Brevo API):** last sends 9/30 forfeiture win-back, 10/2 Roanoke hours. **October Gold & Silver (due 10/1) never sent.**
  Queued: "Shop Online" 10/6 10:00, Giveaway Ladder 10/24. 20 holiday drafts staged (Nov–Dec).
- **Social (Publer API — FB x6, Google Business x5, Instagram, TikTok, WordPress all connected):** published
  9/18–9/23, then only 4 posts on 10/2. Weekly content batch, deal-of-week social, deal reels, comedy reels dark since ~9/23.
- **Blog (thevalleypawn.com):** last post 9/10.
- **Native credentials present:** Brevo API key, Publer API key + account map, Anthropic API key (for copy), Slack bot (files:read for manager deal photos), ffmpeg.
  Missing: none required. (Old Meta page-token file is gone with the plugin cache; Publer replaces it.)

## Build order (each: render to #vp-ops-shadow → first live run verified → Cowork task stays off)
1. **Email (this week)** — native Brevo jobs:
   gold-silver monthly (1st, Template 11 duplicate + existing brevo_preflight gate), welcome-new-contacts (daily),
   Thursday deal-of-week draft guard + send, Bravo→Brevo attribute sync (Tue), engaged-v2 refresh (Wed).
2. **Social (live by Mon 10/12)** — native Publer jobs: Wednesday deal-of-week staging (real manager photos from
   #deal-of-the-week, captions from submission facts only), weekly content batch (FB/IG/GBP), deal reels (ffmpeg).
3. **Blog + website (by 10/15)** — twice-weekly blog via Publer's WordPress connection; website deals mirror.
4. **AI marketing (by 10/19)** — AI-search / AI-visibility autofix (website schema/llms.txt/NAP fixes).
5. **Customer texting** — Chekkit review requests + forfeiture win-back texts (Chekkit is browser-only; design TBD).

## Guardrails (unchanged rules)
Brand voice + CTA from valley-pawn-context / vp-brand-studio; firearms never on social; never post incomplete
data; fleet publish guard (DRY_RUN.json) honored; every send writes a receipt; one owner per send (Cowork task disabled
before native goes live — never both).
