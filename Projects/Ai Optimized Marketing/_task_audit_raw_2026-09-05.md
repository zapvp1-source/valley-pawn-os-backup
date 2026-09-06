I read all 56 SKILL.md files. Findings below.

---

# PART 1 — Per-task rows

Format: `task | model | execution style | scripts/files | inputs | outputs | dup-guard | Rule-18 gate | failure routing | ~lines | fragility`

### Reviews / Chekkit

**chekkit-new-review-alert** | claude-sonnet-5 | pure API (Gmail MCP + Slack MCP) | none | Gmail `from:support@chekkit.io` last 1d | Slack #google-reviews C04NDE52U2G (post or `slack_schedule_message` 10 AM) | **Y** (slack_search_public by reviewer name before post) | N | Contradictory: DM banner (D03BHQH5VGT) *and* "DO NOT POST TO SLACK ON FAILURE" block — net effect ambiguous | 83 | Duplicate guard depends on Slack search indexing latency; store-name parsing from subject line ("Valley Pawn - X" vs "Valley Pawn-X"); hourly cadence = 13 runs/day.

**chekkit-weekly-review-requests** | claude-sonnet-5 | Chrome browser-driving (Chekkit UI + Brevo UI) + osascript pipeline trigger | `Bravo Data Extraction/triggers/*.json`, `output/{date}_{STORE}_chekkit-invites-range.csv`, `_shared-bravo-data/{date}/chekkit-inactives/*.csv`, `reports/ChekkitInactives.ahk` | monday-bravo-combined-run stash; Bravo pipeline; #deal N/A | Chekkit SMS campaigns (5 stores) + Slack #chekkit-updates C0B0FQZ4FS8 + #email-campaigns C0APR5WUL2Z + Brevo master list tag "monthly" | Partial (dedupe by email; no guard against re-sending a campaign) | N | Mixed: DM banner + "no Slack on failure", **but Phase 1 explicitly posts "⚠️ pipeline failure" to #chekkit-updates = VIOLATION** | 202 | Highest-fragility file in the set: dead-cell history (`chekkit-inactives` returned 0 rows silently for ~2 months), Chrome file_upload can only read session-sandbox paths, "Dixie Pawn" warning present, Harrisonburg template typo history, 8–9 min pipeline pull with 15 min timeout, Phase 3 silently skipped once.

**nightly-chekkit-review-responses** | claude-opus-4-8 | Chrome browser-driving (dashboard.chekkit.io, per-store × Google/Facebook, click "Generate Response") | `state.json` in task folder (low-star alert dedupe) | Chekkit reviews UI | Slack #chekkit-updates C0B0FQZ4FS8 + DM D03BHQH5VGT for ≤3★ | **Y** for the low-star DM (state.json keyed reviewer+store+date); **N** for the response posting itself | N | Contradictory (DM banner + no-Slack-on-failure) | 96 | Fully UI-driven, ~10 store×platform passes per night; star rating read by zooming a screenshot; store name list still has "Valley Pawn-Lexington" (no spaces) as a separate literal; opus tier on a click-loop task.

**review-obtained-last-week** | claude-sonnet-5 | Chrome browser-driving (Chekkit Leaderboard) | none | Chekkit "Last week" preset | Slack #google-reviews C04NDE52U2G, scheduled 9 AM Mon | **Y** ("do not schedule more than one post for the same Monday"; abort+DM if unverifiable) | N | Contradictory; abort path = DM only (correct) | 93 | Depends on Chekkit's "Last week" preset being Sun–Sat *and* the task firing Monday; hard-coded example date list (Apr/May 2026); `time_in_past` bug already bit 2026-06-15; overnight sleeping Mac causes late fire.

**google-reviews-post-watchdog** | claude-sonnet-5 | Chrome browser-driving (Chekkit) | none | Slack #google-reviews last ~20 msgs; Chekkit Leaderboard | Slack #google-reviews (self-heal post) or DM | **Y** (Step 1 mandatory check) | N | DM-only. Correct. | 69 | Duplicates review-obtained-last-week's entire Chekkit scrape; states primary fires "~1:25 AM" while the primary's own file says 3 AM — a real disagreement.

### Blog / website

**valley-pawn-blog-publisher** | claude-opus-4-8 | Primary = wpcom MCP API; Secondary = Chrome + `wp.apiFetch` + nonce | archives to `/Users/joshuadavis/Desktop/Claude Back Up/Claude 4 back up/blog-post-YYYY-MM-DD-slug.html` | wpcom posts.list (last 10, topic-overlap check) | thevalleypawn.com post + Slack #blog-posts C0APY6TE604 | **Y** (topic-overlap check vs last 10 posts) | N | Contradictory (DM banner + no-Slack) | 280 | Hard-coded media-ID list (17 IDs) that will drift; hard-coded hours "Monday-Saturday 10 AM to 6 PM" in the CTA template — **conflicts with the canonical NAP used by every other task (all stores except Culpeper are closed Wednesday)**; Chrome fallback needs chunked JS to dodge a safety filter; explicit "never Dixie Pawn".

**blog-publisher-watchdog** | claude-haiku-4-5 | pure API (curl + wpcom MCP) | none | public `/wp-json/wp/v2/posts`; authenticated wpcom posts.list | DM `U03BB52MDSA` only | **Y** (silent on success) | N | DM only. Correct. | 60 | Already produced one false-positive DM (WP.com REST cache lag ~5h); haiku tier doing a 3-branch verification ladder.

**weekly-website-health-audit** | claude-sonnet-5 | pure API/script (sitemap crawl + WP REST Basic auth) | `.wp_app_credentials`, `Website/AUDIT_2026-08-22/weekly-history.json`, WPCode snippet 1135 | sitemap-1.xml; CHANGELOG; OPEN_ITEMS_REGISTER | Slack #website C0ASE9C0GQ0 (always posts, even clean) + CHANGELOG + Open Items | **Y** (history file prevents re-flagging) | N | **Posts partial results to #website on failure = channel failure post (VIOLATION of the field standard, though deliberate here)**; DM only if truly broken | 61 | Auto-writes to live pages via REST; explicitly opts out of "silent on success"; WP REST 429 under sustained writes.

**vp-website-shop-nightly** | claude-sonnet-5 | Chrome browser-driving (primary) + curl/python fallback | `Website/shop-build/generate_shop_block.py`, `items.json`, `shop-block-wrapped.html`, `vp-shop-block.txt` | eBay public storefronts (5 slugs) | WP page **833** (`/shop/`) + Slack #website | **Y** (single `VP-SHOP-START` marker pair enforced; verify card count) | N | On any failure → DM U03BB52MDSA, no success post. Correct. | 198 | Worst known browser failure mode in the fleet: `/sch/i.html` with `_ipg=240` wedged the Chrome renderer for 30 min and required `pkill -9 Google Chrome`; 515 KB block must be smuggled in via a file input; localhost HTTP server to browser is documented as *not working*; hard-coded page id 833 and store slugs.

**vp-website-deals-weekly** | claude-sonnet-5 | Brevo API + Chrome (`Control_Chrome`) + WP REST via isolated-world fetch | `vp-website-deals-weekly/deal_store.json`, `last_block.html`, `publish_store_deals_2026-08-21.py` | Brevo Thursday campaign HTML; Slack #deal-of-the-week C0AVCANK7E3 | WP page 10/`/retail/` + Slack #website | **Y** (dedupe key store\|item\|price; 21-day prune; exactly-one marker check; live-Publer dup guard in the referenced script) | N | Contradictory (DM banner + "post NOTHING on failure") | 77+addendum | Localhost:8787 server needing `Access-Control-Allow-Private-Network`; Slack file-download URL construction (`T03BL4W1DCL-{FILE_ID}`) because the bot token lacks `files:read`; `execute_javascript` runs in an isolated world so `window.wp` is undefined; **this task also reaches into the Thursday email campaign** (cadence guard) — scope creep across two owners.

**vp-website-shop-weekly-report** | claude-sonnet-5 | pure API (wpcom MCP stats + WC REST curl + curl grep) | `.wp_app_credentials`, `METHOD_NOTES.md`, `RUN_LOG_2026-08-21_FAILURE.md` | wpcom statistics.get; WooCommerce totals; live /shop/ | DM D03BHQH5VGT only | **Y** ("check DM history for a report in last 5 days") | N | DM only. Correct. | 22 | Depends on vp-website-shop-nightly; WooCommerce shop-page hijack of `/shop/` is a known recurring break.

**vp-website-trend-daily-refresh** | claude-haiku-4-5 | Chrome browser-driving (GA4 UI scraping ×10 report loads) | writes `/Users/joshuadavis/Desktop/Claude Back Up/Claude 4 back up/website-trend-artifact.html`; `mcp__cowork__update_artifact` | GA4 property 353209303 | Cowork artifact `vp-website-trend` (no Slack) | N/A (idempotent overwrite) | N | **Contradictory** (DM banner + no-Slack block); artifact "Refreshed" line carries the failure reason | 108 | Scrapes GA4 UI with `get_page_text` and explicitly authorizes *fabricating* the trend series ("distribute the total proportionally… Approximate is acceptable") — model-generated numbers land in a dashboard; haiku tier; authuser=1 account-switch dance.

**weekly-analytics-summary** | claude-sonnet-5 | Chrome browser-driving (GA4 UI) | none | GA4 353209303, two report URLs | Slack #website C0ASE9C0GQ0 scheduled 9 AM | N (no explicit duplicate check) | N | **Explicitly silent, no DM** ("STOP SILENTLY… do not post, do not DM") — a genuine blind spot | 54 | Hand-built Slack table from scraped text; "#claude-updates does not exist" warning baked in; GA4 password-wall fallback tells the model to click an empty field to trigger autofill.

**shop-in-store-sync** | claude-sonnet-5 | WP/WC REST (curl, no browser) + Chrome only for Slack photo fetch | `Website/instore-sync/state.json`, `logs/`, `.wp_app_credentials`, `Bravo Data Extraction/output/*_sold-discount-detail.csv` | Slack #in-store-inventory C0BKM6AB0HE; Bravo sold CSVs; WC orders | WP page 867, WC products, Slack #in-store-inventory | **Y** (Slack ts high-water mark; live_items; pending_photo_retry) | N | DM only, plain language; channel silent on no-op. Correct. | 64 | Hard-coded page 867 / product 1064 / page 1110 / tag id 1379; explicit Bravo/Parallels contention window (10:10 & 4:10 to dodge 6:50–7:35 AM and 8:30 PM); WooCommerce `/shop/` hijack interaction with vp-website-shop-nightly.

### Email / Brevo

**monthly-we-buy-gold-silver-email** | **claude-opus-4-8** | pure API (Brevo REST via python) | inline `build.py`; `~/.config/valley-pawn/brevo_api_key` | Brevo Master Template 11 | Brevo campaign send to lists [3,10] + Slack #email-campaigns C0APR5WUL2Z | **Y** (preflight gate: 5 `/c/`, 5 `/t/`, ≥10 utm_content, seeds list 10) | N | **Posts failure notice to #email-campaigns = channel failure post (explicitly authorized here, still a standard violation)** | 146 | Sends to ~10K people; opus tier; key-bridging dance between Mac home and sandbox home; body copy is model-written each month.

**brevo-preflight-watchdog** | claude-sonnet-5 | pure API (python watchdog script, enforce mode) | inline `watchdog.py`; brevo key | Brevo queued/inProcess/draft campaigns | **Suspends** failing campaigns; auto-adds list 10; Slack #email-campaigns | **Y** (idempotent scan) | N | **Posts RED ALERTs and "could not reach Brevo" to #email-campaigns = channel failure post (deliberate, but a violation of the stated standard)** | 163 | Writes to live campaigns (PUT status=suspended) from a re-pasted inline script — no committed file; if the script text drifts between runs, behavior drifts.

**brevo-weekly-draft-guard** | claude-sonnet-5 | pure API (Brevo REST) | brevo key | Brevo drafts | Creates missing draft; renames dupes; Slack #email-campaigns only when it changed something | **Y** (dupe detection + rename `[DUPE - do not send]`) | N | DM only. Correct. | 65 | **Hard-coded staged calendar ending Dec 31 2026** — a documented cliff; date-string matching `Month DD, YYYY` with no leading zero is the single point of failure for the whole weekly email.

**vp-deal-of-week-monday-prompt** | claude-haiku-4-5 | Slack-only (+ optional Brevo lookup) | brevo key (optional) | none | Slack #deal-of-the-week + DM to Joshua | N | N | Contradictory | 92 | Hard-coded "~11,159 subscribers" and "~11K"; the DM's campaign-name lookup is non-blocking (good).

**vp-deal-of-week-monday-reminder** | claude-sonnet-5 | Slack-only | none | #deal-of-the-week thread | Slack #deal-of-the-week @-mentions | **Y** (freshness guard: only act on a prompt posted today) | N | Contradictory banner; silent skip path | 81 | Hard-coded manager names (Sandi/Chadd/Walker/Uriah/Benjie) with a documented "verify it still resolves" step.

**vp-deal-of-week-monday-pick** | claude-sonnet-5 | Brevo API + Chrome (image pipeline) | brevo key; WP media REST; `vp-hero-image` skill | Slack #deal-of-the-week thread; Brevo draft | Brevo campaign scheduled Thu 10 AM + Slack #deal-of-the-week + DM | **Y** (freshness guard on the Monday prompt; re-GET verify status ≠ draft and placeholder gone) | N | Contradictory; STEP 9 bailout DM is correct | 152 | **Caused a 3-week dark email outage** because STEP 5 used `POST /v3/media`, an endpoint that does not exist; the hardening addendum's replacement path is a 6-step Chrome/nonce/localhost chain; DST computed by the model by hand.

**vp-thursday-email-watchdog** | claude-sonnet-5 | Brevo API + Chrome (image pipeline, by reference) | reads `vp-website-deals-weekly/SKILL.md` HARDENING ADDENDUM v2 at runtime | Brevo sent/queued/draft; Slack #deal-of-the-week | Sends the campaign; posts one line to #deal-of-the-week; DM on failure | **Y** (Step 1 check before self-heal; re-GET verify sent) | N | DM only. Correct. | 16 | **Shortest file in the set (16 lines) carrying the heaviest action — an unattended send to the full list.** Its image pipeline is defined only by pointing at another task's SKILL.md; if that file is edited, this task's behavior silently changes.

**brevo-weekly-efficiency-audit** | claude-sonnet-5 | pure API (Brevo REST + `dig` via osascript) | `Email Refinement/EFFICIENCY_LOG.md`, `_audit/*.py`, `assign_waves.py`, `build_waves.py`, `CALENDAR_AUG_DEC_2026.md` | Brevo campaigns/lists/senders; DNS; prior log | Slack #email-campaigns + EFFICIENCY_LOG + CHANGELOG | **Y** (reads prior log; "don't re-propose declined items") | N | DM only. Correct. | 91 | Broad write authority (stages new drafts, cleans lists, renames campaigns) driven by model judgment; depends on a hand-maintained markdown log as its only memory.

**email-analytics-weekly** | claude-sonnet-5 | pure API (`brevo_helper.py` + `sheets_helper.py`) | `Scheduled/_shared/brevo_helper.py`, `Scheduled/_shared/sheets_helper.py`, OAuth token `~/.config/valley-pawn/google-oauth-token.json` | Brevo per-link clicks; master Sheet `1EPj22S1...` | Slack **`#email-campiagns`** (misspelled channel name in the description, ID C0APR5WUL2Z is correct) + Sheet upsert + Cowork artifact | **Y** (`upsert_by_key` on campaign_id; NEW/STALE/FROZEN diff) | N | Contradictory: banner says DM; Execution Contract says "post a `:warning:` line in the Slack channel" = **channel failure post** | 161 | **Misspelled channel `#email-campiagns` propagated into marketing-ceo-briefing-weekly's roll-up table too**; the north-star metric section is documented as STALE with a correction appended at the bottom rather than fixed in place; Google OAuth token expiry.

**brevo-welcome-new-contacts** | claude-sonnet-5 | pure API (Brevo REST) | brevo key; `Email Refinement/EFFICIENCY_LOG.md`, `_audit/build_welcome_and_giveaway.py` | Brevo contacts created <4d | Transactional template 72 to new contacts; log line only | **Y** (WELCOMED attribute set per-contact immediately after send; verify 5 by re-fetch) | N | DM only. Correct. | 56 | Sends real customer email daily with no human in the loop; hard-coded template id 72.

**bravo-brevo-attribute-sync** | claude-sonnet-5 | pure API/script (osascript + Brevo REST) | `Email Refinement/_audit/enrich_contacts.py`, `verify_enrichment.py`; `Bravo Data Extraction/output/*_chekkit-invites-range.csv` (117 files); `_shared-bravo-data/` stash | monday-bravo-combined-run stash; Bravo archive | Brevo contact attributes; EFFICIENCY_LOG; #email-campaigns only if material | **Y** (enrichment-only, never creates contacts; never overwrites non-empty) | N | DM only. Correct. | 141 | ~70 min runtime for 4,900 contacts at ~0.95 s each; three documented API gotchas (listIds side-effect, E.164 requirement, missing `email` key); has a **mandatory Bravo contention check** — the only marketing task that does.

### Social / content

**vp-content-batch-weekly** | **claude-opus-4-8** | Publer API + Chrome UI fallback + osascript | `Refine Social Media/publer_client.py` (`upload_media`, `schedule_post`), `PILLAR_OVERLAY.md`, `weekly-adjustments.json`, `hook-library/*.json`, `publer_accounts.json`, `publish_store_deals_2026-08-21.py`, `vp_fb_content_strategy.md`, Bravo `output/*_items-to-price.csv` | Slack #deal-of-the-week; Bravo exports; Friday digest adjustments; `vp-website-deals-weekly/deal_store.json` | 42 items / 91 platform posts scheduled in Publer; Slack #vp-studio-queue C0BHTEUPADB; manifest JSON | Partial (live-Publer duplicate guard exists only in the referenced catch-up script) | N | Contradictory (DM banner + "post NOTHING") | 217 | The single largest and most-patched file; shipped **2/26 items** on 8/10 and **0/35 store items** on 8/17; MJ fast-hours dependency; `GET /posts` silent 15-result cap; DOM-selector-by-provider-badge for Brand IG; the 2026-08-11 "immediate catch-up" of three specific items is now stale hard-coded content.

**vp-content-batch-preflight** | claude-sonnet-5 | Chrome (Publer, Midjourney) + osascript + Publer API | `~/.vp-studio/patches/*.py` + `MANIFEST.sha256`, `~/.vp-studio/publer-session.json`, `~/.vp-studio/scripts/compose_text_on_hero.py`, `vp_helper_setup.py`, `preflight_heal_ledger.jsonl`, writes `Valley Pawn Studios/output/preflight_{date}.json` | Bravo export freshness; Publer; MJ; skill files | preflight JSON flags (`bravo_skus`, `publer`, `mj_mode`, `slack`, `text_composite`, `batch_go`) | **Y** (SHA-256 verified patches; heal ledger) | N | DM Joshua only, and only after a remediation attempt. Best-designed failure model in the set. | 118 | Checks **absolute paths into the Claude skills-plugin session directory** (`.../skills-plugin/f6b75d02-…/823f6874-…/skills/…`) — session-scoped paths that will break; MJ balance scraping; 8 checks × 3 retries at Sun 9 PM.

**vp-content-batch-postflight** | claude-sonnet-5 | Chrome (Publer calendar) + Publer API | reads batch manifest; writes `output/{date}/postflight_result.json` / `postflight_FAILED.json` | vp-content-batch-weekly manifest; Publer | DM Joshua only on partial/failure | **Y** (silent on clean success by design) | N | DM only. Correct. | 91 | Hard-coded Publer IG account id `6a35979ebbd130d6e889c0bb`; requires per-platform verification across 13 accounts inside a 90-min window.

**vp-content-batch-quota-watchdog** | claude-sonnet-5 | pure script (osascript → `quota_watchdog.py`) | `Refine Social Media/quota_watchdog.py`, `publer_client.py`, `publer_accounts.json`, `Valley Pawn Studios/output/{date}/quota_watchdog_result.json` | Publer live posts; prior result file | DM Joshua only on 2-week shortfall | **Y** (dedupe by post id + account id; 2-week history comparison) | N | DM only. Correct. | 48 | Cleanest task in the set — all logic in a committed script. Model is the template the rest should follow.

**vp-publer-analytics-friday** | claude-sonnet-5 | pure script (osascript → python) | `Refine Social Media/publer_weekly_digest.py`; writes `friday_digests/*.md`, `weekly-adjustments.json`, `adjustments_log.jsonl`, `~/.vp-studio/lessons.md` | Publer analytics API | DM Joshua one line | N | N | **Silent on failure, no DM** ("stay silent on Slack; explain in run-summary only") — a blind spot | 67 | Publer analytics lag 24–48h; `weekly-adjustments.json` feeds Monday's batch, so a silent failure here degrades Monday silently.

**weekly-social-media-recap** | claude-sonnet-5 | pure script (osascript → python) | `Refine Social Media/weekly_social_recap.py` | Publer published posts, trailing 7d | Slack #social-media C0BMRC2LN3D (verbatim script output between RECAP_START/END) | N (posts every Monday by design; zero-result posts too) | N | DM only; explicitly forbids posting failure to the channel. Correct. | 68 | Good pattern — **deterministic formatter output, not model-rendered**. One of only a handful.

**vp-deals-social-wednesday** | claude-sonnet-5 | Chrome (Publer UI) + osascript | `vp-hero-image` skill; saves to `Valley Pawn Studios/asset-library/heroes/{YYYY-MM}/…`; manifest `output/{date}/deals_social_manifest_{date}.json` | Slack #deal-of-the-week (7d) | Publer scheduled posts (store FB + Brand IG + store GBP) + DM Joshua | N | N | Contradictory banner; DM on skips | 112 | **Hard-coded pixel coordinates** ("GBP compose: click Photo tab (166, 190)", "`.droparea` index 5") — guaranteed to break on any Publer UI change; hard-coded IG media id `17841405894186570`; DOM `.ACLI__provider` selector.

**vp-casual-video-daily** | claude-sonnet-5 | osascript → python; Chrome Publer UI as fallback | `Refine Social Media/casual_video_processor.py`; inbox `Valley Pawn Studios/casual-video-inbox/`, `outbox/` | staff video inbox (fed by vp-staff-video-chase) | Publer scheduled (Brand FB/IG/TikTok/X) + DM Joshua on success | N | N | **Silent on failure** ("stay completely silent on Slack") | 69 | Fired nightly against an empty folder for 47 days with nobody noticing — the canonical example of the silent-failure problem; whisper/faster-whisper may not be installed; ffmpeg PATH must be exported manually.

**vp-staff-video-prompt** | claude-haiku-4-5 | Slack-only | `ASK_LOG.md` in task folder | Slack #casual-video / #deal-of-the-week | Slack post (the ask) | **Y** (OPEN-ASK GUARD: skip if an ask with an unexpired deadline exists) | N | Silent on success, no DM by design | 70 | Posts as Joshua (uses `my-writing-style`); may need to *create* a Slack channel; haiku tier writing in a named person's voice.

**vp-staff-video-chase** | claude-sonnet-5 | Chrome (Slack web downloads) + Slack MCP | `casual_video_processor.py`; drops files in `casual-video-inbox/` | Slack channel since Tue 9 AM | Slack chase post; files to inbox; #vp-studio-queue log | **Y** (DEADLINE-WINDOW GUARD ±6h; "read the channel at run time, never carry a stale judgment") | N | DM only after 3 weeks of zero. Correct. | 94 | Whisper documented as not installed → instructs the model to hand-write burned-in captions from watching video; Slack web downloads via Chrome session.

**vp-deal-reels-weekly** | claude-sonnet-5 | osascript → python render; Publer API | `Refine Social Media/vp_deal_reel.py`, `vp_social_publisher.py`, `publer_client.py`, `creative_drift.py`, `deal_of_week_uploads/`, `reels/` | Slack #deal-of-the-week; `deal_store.json` image mirror | Publer reels (store FB + Brand IG; brand compilation to FB/IG/TikTok) + #vp-studio-queue | Partial (verify against Publer's real list) | N | DM only if <3 reels after remediation. Correct. | 129 | Truncated-mp4 failure mode documented ("never treat the presence of a file as proof"); Publer needs a browser User-Agent or Cloudflare 1010; `GET /posts` 15-cap.

**vp-community-weekly** | claude-sonnet-5 | osascript → python; Publer API | `creative_drift.py`, `CITY_COMMUNITY_KB.md`, `PILLAR_OVERLAY.md`, `CREATIVE_DRIFT.md` | KB + drift engine | Publer (store FB + store GBP, different caption each) + #social-media | **Y** (45-day hook cooldown enforced by engine) | N | DM only if <5 posts. Correct. | 117 | **Densest stale-fact risk in the fleet**: `[C26]`/`[PATTERN]`/`[VERIFY]` date tagging, the Waynesboro "Nov 21 tree lighting" 2025-data landmine, Lexington Confederate-memorial exclusion, per-town first-frost dates. All model-written free text into public GBP/FB.

**vp-engagement-weekly** | claude-sonnet-5 | osascript + Publer API + **Chrome on the Facebook Pages themselves** for the comment sweep | `creative_drift.py`, `vp_social_publisher.py` | this week's deals / in-store / eBay / Bravo inventory | Publer posts + #social-media log | Partial (drift-engine cooldowns) | N | DM only if nothing shipped. Correct. | 102 | **Directly contradicts the fleet-wide guardrail "NEVER open facebook.com/instagram.com in Chrome against Valley Pawn accounts"** that vp-content-batch-weekly, vp-deals-social-wednesday and vp-casual-video-daily all declare as a HARD GUARDRAIL — Step 6 requires reading comments through the Chrome session on the Page. Also owes a next-day answer reveal on "Guess the Price" games with no scheduling mechanism beyond "track open games in the run log."

**vp-comedy-reel-weekly** | **claude-opus-4-8** | osascript → python render; Publer API | `vp_comedy_reel.py` (`check_script()` hard-block), `creative_drift.py`, `~/.vp-studio/scripts/generate.py` | deals/in-store/eBay/Bravo | Publer reels (Brand FB/IG/TikTok + one rotating store FB) + #vp-studio-queue | Partial | N | DM only if zero shipped. Correct. | 122 | Renderer guardrails are in code (good); depends on macOS `say` and a MJ still generator; opus tier weekly.

**vp-creative-refresh-quarterly** | **claude-opus-4-8** | osascript → python; Publer API | `creative_drift.py`, `creative_state.json`, `CREATIVE_LEDGER.md`, `CREATIVE_DRIFT.md`, `weekly-adjustments.json` | Publer last quarter; #social-media, #vp-studio-queue | `CREATIVE_LEDGER.md` + registry updates + DM Joshua + short #social-media post | **Y** (`is_novel()` gate on every candidate) | N | (no explicit failure clause) — **effectively silent** | 111 | Fires 4×/yr at 7:40 AM; documents two API traps (15-result cap; zero-indexed `post_insights` pagination); if it under-delivers, "that lane will under-fill every week for 13 weeks."

**vp-follower-growth-monthly-check** | claude-sonnet-5 | Chrome browser-driving (Publer analytics UI, screenshot-read) | `Refine Social Media/follower_growth_log.csv` | Publer Overview dashboard | DM Joshua one line | N | N | DM only. Correct. | 46 | Name says "monthly", it runs weekly Mondays; **baseline numbers hard-coded from 2026-08-06** (6.3K total, Culpeper 884, Roanoke 36, IG 100, TikTok 2, X 0) and never refreshed; reads a metric card off a screenshot.

### eBay

**ebay-weekly-quality-fix** | claude-sonnet-5 | pure API/script via osascript (eBay Trading + Taxonomy) | `~/ebay_weekly_rankings.py` (STORES/tokens), `~/ebay_title_stripper.py`, `~/ebay_caps_fixer.py`, state files `~/ebay_title_state.json`, `~/ebay_caps_state.json` | eBay ActiveList last 7d | **Manager DMs** (5 hard-coded Slack user IDs) + Preston DM U03BWMEM9GR | **Y** (stripper/caps fixers are idempotent + reversible via state files) | N | DM banner; no channel posts | 72 | Five hard-coded manager Slack IDs; live `ReviseFixedPriceItem` writes; per-store OAuth token expiry is the standing risk.

**ebay-title-photo-accuracy-audit** | claude-sonnet-5 | pure API/script via osascript, plus **sub-agents reading PNG sheets** | `eBay/ebay_photos_pull.py`, `build_audit_sheets.py`, `ebay_title_revise.py` (`--apply`/`--revert`), `ebay_toolfix_apply.py`, `getitem_detail.py`, `WEEKLY_QUALITY_FIX_LOG.md` | eBay photos + full-res verification | DM Joshua U03BB52MDSA + category-(c) manager DMs | **Y** (title changes reversible; re-check live title before writing) | N | DM only; explicitly forbids #preston-claude C0BGXSTT4TY | 73 | ~20% thumbnail false-positive rate acknowledged; spawns one Sonnet subagent per store; two specific item IDs hard-coded as known-unfixed examples.

**ebay-weekly-channel-audit** | claude-sonnet-5 | pure API (Trading API, read-only) + Artifact publish | `~/ebay_weekly_rankings.py`, `~/.vp_secrets/ebay_store_tokens.py`, `~/ebay_markdown_state.json`, `eBay/audit_weekly/{date}/`, `EBAY_DASHBOARD_ARTIFACT.md` | eBay ×5 stores, 90-day windows | Slack #ebay-performance + CHANGELOG + "eBay Channel Pulse" artifact | **Y** (trend comparison vs prior dated folder; updates artifact in place via saved URL) | N | **Notes failures inside the Slack channel post** = channel failure surface (deliberate: "partial data must be labeled as partial") | 96 | Carries the **2026-08-22 incident rule**: never `exec()` any `~/ebay_*.py` to verify it, because those scripts have no `__main__` guard and perform live writes; artifact URL lives in a text file.

**weekly-online-store-audit** | claude-sonnet-5 | pure script via osascript | `~/vp_weekly_online_store_audit.py`, `~/vp_ebay_fix_state.json`, `eBay/weekly_audit/{date}/`, `latest.json` | eBay ×5 | Slack #ebay-performance (via `SLACK_WEBHOOK` in `~/ebay_weekly_rankings.py`) | **Y** (idempotent, additive; state file reversible) | N | DM only; but "fix_failures_this_run > 0" is called out **in the channel post** | 24 | Step 2's verification instructions tell the model to `exec ~/ebay_weekly_rankings.py` — **directly contradicts ebay-weekly-channel-audit's hard safety rule against exec'ing those files**.

**ebay-markdown-terminal-weekly** | claude-sonnet-5 | pure script via osascript | `eBay/ebay_markdown_terminal.py --apply`, `~/ebay_markdown_state.json`, `~/ebay_markdown_terminal_state.json`; reads `ebay-weekly-quality-fix/SKILL.md` for the manager map | markdown engine state | Slack #ebay-performance + manager DMs + CHANGELOG + Open Items | **Y** (two-stage state file with 14-day grace) | N | DM Joshua on failure. Correct. | 50 | Performs **real destructive eBay writes** (`EndFixedPriceItem`); manager mapping is by cross-reference to another task's file rather than a shared config; hard-coded "154 items projected 2026-09-01" is already stale.

**monthly-ebay-ratings-sweep** | claude-sonnet-5 | Chrome browser-driving (`mcp__Control_Chrome__open_url` + `execute_javascript` reading `document.body.innerText`) | saves `claude/ebay-ratings-sweep-<YYYY-MM>.md` in the "Online Store" project | eBay public feedback profiles ×5 + seller dashboard | Slack **#ebay-performance channel ID `C0ANVN5KX4Y`** | Partial (compares to prior month doc) | N | "Post whatever data you can get and note anything skipped" — no DM clause | 66 | **Channel ID mismatch:** this task uses `C0ANVN5KX4Y` for #ebay-performance while the other eBay tasks reach the channel via a webhook or by name — one of these is wrong and should be reconciled. WebFetch blocked by eBay robots.txt so it must use Chrome. Recently migrated from cloud; migration note still present.

**ebay-feedback-reply-weekly** | **none (no `model:` line)** | pure script via osascript | `eBay/ebay_feedback_replies.py`, `~/ebay_feedback_open.json`, `~/ebay_feedback_answered.json`, `feedback_replies_<date>.json`, `EBAY_ACCOUNT_HEALTH_2026-09-05.md` | eBay GetFeedback ×5 | **Permanent public eBay replies** + DM Joshua | **Y** (`ebay_feedback_answered.json` — "never delete that file") | **Y** — explicitly invokes Rule 18 ("never claim an internal process change… unless it actually happened") | DM only, no channel. Correct. | 62 | **No model pinned** on a task that writes permanent, uneditable public replies on behalf of the business; the entire dedupe guard is one local JSON file with no backup.

### AI-search / presence

**vp-ai-search-health-check** | claude-sonnet-5 | Chrome browser-driving (site JS eval + Google/Bing maps + Bing Places console) | none (all inline) | thevalleypawn.com, WPCode #738/#742, Bing Places console | Slack #ai-marketing C0BCEESUANM | N (no dup check; "always post") | N | **Posts partial results to the channel** ("⚠️ Completed Checks 1–2…") and explicitly says that does NOT require a DM = channel failure surface | 85 | Full canonical NAP hard-coded here **and separately in vp-presence-audit-weekly** (two copies that must be kept in sync); 5 hard-coded Bing Places bizids; "Dixie Pawn" legacy-name checks; three-bucket classification (LISTING DEFECT / RENDER MISMATCH / FOREIGN LISTING) that must be re-derived by the model each week.

**vp-ai-search-autofix** | claude-sonnet-5 | Chrome (`Control_Chrome`) + osascript + `sheets_helper` | `Scheduled/_shared/sheets_helper.py`, OAuth token; `directory-listing-push` skill | reads the health-check's own Slack post in #ai-marketing | Autofix Log Sheet `1A_gJuj5siq...` + Slack #ai-marketing | **Y** (skips clean weeks; detects a stale upstream post >8 days and DMs) | N | DM only for the upstream-missing case; otherwise channel post. Correct-ish | 94 | **Reads its input by parsing another task's free-text Slack post** — a model-rendered message is the machine interface. That is the most brittle coupling in the fleet.

**vp-ai-visibility-metrics** | claude-sonnet-5 | Chrome browser-driving (5 AI engines ×6 queries = 30 prompt runs + GA4 + Google Sheet) | AI Visibility Tracker Sheet `17gkCl9BpB8y...` | Perplexity/Google AIO/Gemini/ChatGPT/Copilot; GA4 353209303 | Slack #ai-marketing + Sheet append | Partial ("best-effort" sheet append) | N | Banner DM; "note it briefly and report what you did get rather than failing" | 74 | 30 logged-in browser sessions across five consumer AI products, each with its own login/anti-bot surface; hard-coded competitor names (The PawnShop, JBS Pawn, Pawn-Mart, Tobey's, Rockbridge); "Dixie Pawn" check.

**vp-ai-visibility-autofix** | claude-sonnet-5 | Chrome (`Control_Chrome`) + osascript + `sheets_helper` | same two Sheets; `facebook-post` skill (Graph token) | reads vp-ai-visibility-metrics' Slack post | Autofix Log Sheet + Slack #ai-marketing | Partial | N | Channel post only. | 90 | Same free-text-post-as-interface coupling; STEP 2B tells it to use the **Graph API token from the `facebook-post` skill** — but vp-deal-reels-weekly / vp-community-weekly / vp-engagement-weekly all record that **every Facebook Page token died 2026-08-21**. Stale and will fail.

**vp-presence-audit-weekly** | claude-sonnet-5 | pure API/curl (primary) + web search; osascript for creds | `.wp_app_credentials`, `Ai Optimized Marketing/AI-Search-GEO/presence/presence_scorecard_latest.json`, `presence_scorecard_<date>.json`, `PRESENCE_HISTORY.csv`, `Website/_backups_20260822/citypages/` | sitemap; off-site directories; Facebook via Googlebot UA; Google Maps embed | Slack #ai-marketing (must begin `WEEKLY PRESENCE AUDIT`) + scorecard + CSV | **Y** (literal first-line marker for the duplicate guard / Fleet Guardian; `resolved_do_not_reopen` array) | N | "A finding is NOT a failure" — DM only on total inability. Correct. | 154 | Second full copy of canonical NAP; large hard-coded fact table (review counts as of 2026-08-23, competitor ratings, Staunton ghost-listing count, BBB/Yelp/MapQuest IDs, FB page IDs, `$100,000` loan figure Joshua hasn't confirmed); WP REST 429 on sustained writes; several sources 403 automated fetching.

### Cross-channel roll-ups

**marketing-ceo-briefing-weekly** | claude-sonnet-5 | Slack-read + file-read + artifact publish | `Gold and Silver Markeitng/ceo-briefing/history.json`, `actions.json`, `artifact_url.txt`, `briefing-YYYY-MM-DD.md`; reads other tasks' SKILL.md files | 8 lane audits' Slack channels + scorecard files; QBO (optional) | Rolling artifact + DM Joshua + CHANGELOG + Open Items | **Y** (stable artifact URL updated in place; Rule 12 re-verification of every open item) | N | DM only. Correct. | 67 | **Folder name is misspelled: `Gold and Silver Markeitng`**; the lane table repeats the misspelled `#email-campiagns`; it reads *eight* other tasks' Slack posts as its data source, so any lane that changes its post format silently degrades this; "all eight complete before 11:30 AM" is an assumption, not a check.

**monthly-eom-recap** | **none (no `model:` line)** | delegated — reads a spec file via osascript | `Valley Pawn OS/pending-tasks/monthly-eom-recap/SKILL.md`; `Valley Pawn OS/monthly-analytics/2026-08 Month in Review.md` | each channel's own weekly/daily posts | Month in Review posts into multiple analytics/marketing channels | (per spec file) | **Y** — the spec is described as containing a "completeness gate" | (per spec file) | **5 lines** — the shortest file in the fleet | The entire task definition lives in a *different* file outside `Scheduled/`; no model pinned; it posts into many channels at once with no visible guard in this file.

---

# PART 2 — Summary

## (a) Chrome / computer-use — the fragile class

**Zero of these 56 drive computer-use/Parallels.** The marketing fleet's fragility is entirely **Chrome**. 26 of 56 depend on a live, logged-in Chrome session:

| Cluster | Tasks | What it drives | To go headless |
|---|---|---|---|
| Chekkit UI | chekkit-weekly-review-requests, nightly-chekkit-review-responses, review-obtained-last-week, google-reviews-post-watchdog | dashboard.chekkit.io campaigns, review replies, leaderboard | Chekkit API key + a `chekkit_client.py` in `Scheduled/_shared/`. This alone removes 4 tasks and ~2 hours of nightly clicking. Highest ROI in the audit. |
| GA4 UI scraping | weekly-analytics-summary, vp-website-trend-daily-refresh, vp-ai-visibility-metrics (Part B) | analytics.google.com report tables read via `get_page_text` | GA4 **Data API v1** (`analyticsdata.googleapis.com`) with the OAuth token already working in `sheets_helper.py`. Note: `analyticsdata` appears in **zero** files — the API path has never been attempted. Removes the authuser=1 dance, the password-wall autofill hack, and the "approximate is acceptable" fabricated series. |
| Publer UI fallback | vp-deals-social-wednesday, vp-casual-video-daily, vp-content-batch-weekly, vp-content-batch-postflight, vp-content-batch-preflight, vp-follower-growth-monthly-check | composer, account picker, calendar, analytics cards | `publer_client.py` already exists and `upload_media()` closed the last real gap. Delete the UI fallbacks outright; they are the source of the pixel coordinates `(166, 190)` and `.droparea` index 5. Follower counts need a Publer analytics endpoint or a per-account public-profile fetch. |
| WordPress publish | vp-website-shop-nightly, vp-website-deals-weekly, vp-deal-of-week-monday-pick (images), vp-thursday-email-watchdog (images), valley-pawn-blog-publisher (secondary) | nonce scraping, `wp.apiFetch`, isolated-world fetch, localhost:8787 with PNA headers, file-input smuggling | **The WP Application Password already exists** (`Website/shop-build/.wp_app_credentials`) and shop-in-store-sync / weekly-website-health-audit / vp-presence-audit-weekly already use it headlessly via curl Basic auth. Every Chrome+nonce path in this list is redundant with a credential the fleet already holds. This is the single largest unnecessary browser surface. |
| eBay public pages | monthly-ebay-ratings-sweep, vp-website-shop-nightly (primary path) | feedback profiles, seller search | Storefront endpoint `ebay.com/str/<slug>` already proven curl-able; feedback is available via Trading API `GetFeedback`, already used by ebay-feedback-reply-weekly and ebay-weekly-channel-audit. |
| AI engines | vp-ai-visibility-metrics | 30 logged-in prompt sessions | Genuinely not headless-able. Keep in Chrome, but isolate it — it should not share a run window with anything else. |
| Facebook Pages | vp-engagement-weekly (comment sweep) | reading comment bodies on the Page | No headless path since the Page tokens died 8/21. This is the one legitimate remaining browser need, and it violates every other task's stated guardrail. Needs an explicit carve-out or a re-issued token. |

## (b) Overlapping / duplicate work

- **GA4:** pulled by **3** tasks independently (weekly-analytics-summary Mon 2:30 AM, vp-website-trend-daily-refresh daily 2:40 AM, vp-ai-visibility-metrics Fri) — plus vp-ai-visibility-autofix editing GA4 channel-group config and marketing-ceo-briefing-weekly re-reading the numbers. **weekly-analytics-summary and vp-website-trend-daily-refresh fire 10 minutes apart on Monday against the same property and pull overlapping windows.** One collector writing a JSON file, three consumers.
- **Publer:** touched by **15** tasks; Publer *analytics* pulled independently by **6** (vp-publer-analytics-friday, weekly-social-media-recap, vp-content-batch-quota-watchdog, vp-content-batch-postflight, vp-follower-growth-monthly-check, vp-creative-refresh-quarterly). All six independently re-learn the `GET /posts` 15-result cap; three of them document it as a bug they were bitten by.
- **Brevo API:** **12** tasks. Every one re-implements the same key-bridging block (`base64 < ~/.config/valley-pawn/brevo_api_key`) inline — yet `Scheduled/_shared/brevo_helper.py` exists and only **email-analytics-weekly** uses it.
- **eBay Trading API:** **9** tasks, 4 of them (quality-fix, title-photo-audit, channel-audit, online-store-audit) pulling active listings for all 5 stores in the same Monday/Sunday window with overlapping fields.
- **Chekkit review data:** review-obtained-last-week and google-reviews-post-watchdog perform the **identical** Chekkit leaderboard scrape 7½ hours apart on Monday.
- **`#deal-of-the-week` submissions:** read by **10** tasks (prompt, reminder, pick, website-deals, deals-social, thursday-watchdog, deal-reels, content-batch-weekly, engagement-weekly, comedy-reel). Each re-parses "photo + price" qualification independently, with at least three different definitions of where submissions live (thread replies vs top-level channel messages — vp-website-deals-weekly's addendum explicitly corrects vp-deal-of-week-monday-pick's assumption).
- **Canonical NAP / store facts:** duplicated in full in vp-ai-search-health-check, vp-presence-audit-weekly, vp-website-deals-weekly, valley-pawn-blog-publisher (with a conflicting hours line), and vp-community-weekly.
- **Manager Slack IDs:** duplicated in ebay-weekly-quality-fix (canonical), ebay-title-photo-accuracy-audit, ebay-markdown-terminal-weekly (by file reference), vp-deal-of-week-monday-reminder (names only).

## (c) No watchdog / guardian coverage

Covered: blog-publisher → blog-publisher-watchdog; review-obtained-last-week → google-reviews-post-watchdog; Brevo sends → brevo-preflight-watchdog + brevo-weekly-draft-guard + vp-thursday-email-watchdog; content-batch → preflight + postflight + quota-watchdog; presence audit → Fleet Guardian (marker line).

**Uncovered, and several are silent-on-failure — the dangerous combination:**
- **vp-casual-video-daily** — silent on failure, ran against an empty folder for 47 days undetected.
- **vp-publer-analytics-friday** — silent on failure; its output (`weekly-adjustments.json`) feeds Monday's batch, so a silent Friday failure silently degrades Monday.
- **weekly-analytics-summary** — explicitly "no Slack, no DM" on failure. Fully invisible.
- **vp-website-trend-daily-refresh** — contradictory policy; the artifact just shows an old timestamp.
- **vp-website-shop-nightly** — no watchdog despite the documented Chrome-wedge failure mode.
- **chekkit-weekly-review-requests** — no watchdog; already had a run that silently skipped its core deliverable (Phase 3 sends).
- **nightly-chekkit-review-responses** — no watchdog on the 4/5-star response loop.
- **email-analytics-weekly**, **brevo-weekly-efficiency-audit**, **bravo-brevo-attribute-sync**, **brevo-welcome-new-contacts** — no watchdog.
- **vp-community-weekly / vp-engagement-weekly / vp-deal-reels-weekly / vp-comedy-reel-weekly** — the four new creative lanes have no coverage; quota-watchdog only checks the 13 accounts fed by vp-content-batch-weekly.
- **vp-creative-refresh-quarterly** — no failure clause at all, fires 4×/yr; a missed run degrades every lane for 13 weeks.
- **marketing-ceo-briefing-weekly** and **monthly-eom-recap** — the roll-ups themselves are unwatched.
- **ebay-feedback-reply-weekly** and **monthly-eom-recap** — no model pinned *and* no watchdog.

## (d) Model-rendered free text / hand-built tables into channels

**Deterministic (script writes the exact bytes) — only 3:**
- weekly-social-media-recap (verbatim between `RECAP_START`/`RECAP_END`)
- weekly-online-store-audit (posts `summary.md` from the script)
- ebay-markdown-terminal-weekly (script posts per-item; task adds a one-line rollup)

**Everything else is model-composed prose or hand-assembled tables posted to a channel.** The worst cases, where a hand-rendered post is also a *machine interface* for a downstream task:
- **vp-ai-search-health-check → vp-ai-search-autofix** and **vp-ai-visibility-metrics → vp-ai-visibility-autofix**: the autofix tasks parse the previous task's free-text Slack bullets to decide what to change on live listings.
- **8 lane audits → marketing-ceo-briefing-weekly**: the CEO briefing's primary input is eight model-written Slack posts.
- Hand-built numeric tables: weekly-analytics-summary (GA4 KPIs + top-8 pages + traffic mix, typed from scraped page text), vp-website-trend-daily-refresh (writes a JS `DATA` object by hand and is authorized to interpolate missing series), vp-ai-visibility-metrics (Visibility Index computed by the model across 30 cells), review-obtained-last-week / google-reviews-post-watchdog (ranked table), chekkit-weekly-review-requests (two per-store count blocks), email-analytics-weekly (5-line KPI block), monthly-ebay-ratings-sweep (per-store rating blocks), ebay-weekly-channel-audit (per-store table + a fully rebuilt HTML dashboard).

## (e) Hard-coded stale facts

1. **valley-pawn-blog-publisher**: CTA template says "*hours (Monday-Saturday 10 AM to 6 PM)*" — wrong; only Culpeper opens Wednesday. This ships in every published blog post.
2. **brevo-weekly-draft-guard**: staged draft calendar hard-stops at **Dec 31, 2026**.
3. **vp-follower-growth-monthly-check**: entire per-account baseline frozen at 2026-08-06 (6.3K, Culpeper 884, Harrisonburg 757, Lexington ~1,600, Roanoke 36, Waynesboro ~1,200, Brand 1,700, IG 100, TikTok 2, X 0); task name says "monthly", cadence is weekly.
4. **vp-deal-of-week-monday-prompt**: "~11,159 subscribers" / "~11K" hard-coded in the message posted to managers.
5. **vp-presence-audit-weekly**: review counts and competitor ratings frozen at 2026-08-23; `$100,000` loan figure flagged as *not yet confirmed by Joshua* but used as the correctness standard; Staunton ghost count "was 9".
6. **ebay-markdown-terminal-weekly**: "154 items projected to hit their final cut on 2026-09-01" — the date has passed.
7. **vp-content-batch-weekly**: the "immediate catch-up" of three specific 2026-08-10 items (Coach bag, Case knife set, Dolphin pool cleaner) is baked into the prompt permanently.
8. **vp-community-weekly**: Waynesboro "Nov 21 tree lighting / Nov 22 parade" documented as 2025 data that must never publish — mitigated but still a live landmine.
9. **review-obtained-last-week**: worked example dates hard-coded to Apr–May 2026.
10. **vp-ai-visibility-autofix**: instructs use of the `facebook-post` Graph API token, which four other tasks record as **dead since 2026-08-21**.
11. **Channel-ID / name defects:** `#email-campiagns` misspelled in email-analytics-weekly's description *and* propagated into marketing-ceo-briefing-weekly's lane table. **monthly-ebay-ratings-sweep uses `C0ANVN5KX4Y` for #ebay-performance** while no other eBay task cites that ID. weekly-analytics-summary and vp-website-trend-daily-refresh both carry a warning that `#claude-updates` does not exist.
12. **Path defects:** `Gold and Silver Markeitng` (misspelled folder, marketing-ceo-briefing-weekly); vp-content-batch-preflight checks **session-scoped skills-plugin paths** containing UUIDs `f6b75d02-…/823f6874-…` that will not survive a session change; two tasks archive to `/Users/joshuadavis/Desktop/Claude Back Up/Claude 4 back up/`.
13. **"Dixie Pawn"** appears as a hard-stop guard in 12 of the 56 — correct, but it also means the legacy name is still live somewhere (MapQuest listing 410128854, BBB, Yelp, Facebook `dixiepawnhburg`), tracked in vp-presence-audit-weekly with **root cause "a Yext feed only Joshua can cancel."**
14. **Roanoke Suite C vs Suite D** and **Harrisonburg "Ste 22"** are settled-fact carve-outs that must be restated identically in two separate files or one of them will start "fixing" the other's correct value.

## (f) Monday load

Roughly **28 firings** from this 56-task set land on a Monday. Serial-queue risk is concentrated 2–4 AM and 8 AM–1 PM.

| Time (ET) | Task | Notes |
|---|---|---|
| ~1:25–1:30 AM | valley-pawn-blog-publisher | opus; also Thu. Watchdog says 1:25, file says ~1:30 |
| 2:02 AM | **vp-content-batch-weekly** | opus; generates + schedules 42 items / 91 posts — the longest single run in the fleet |
| 2:30 AM | weekly-analytics-summary | Chrome/GA4 |
| 2:40 AM | vp-website-trend-daily-refresh | Chrome/GA4 — **10 min after the above, same property** |
| ~3:00 AM | review-obtained-last-week | Chrome/Chekkit |
| 3:30 AM | vp-content-batch-postflight | Chrome/Publer; assumes 2:02 AM finished |
| 5:15 AM | weekly-website-health-audit | full sitemap crawl + WP writes |
| 7:00 AM | vp-weekly-spot-price-update | daily; feeds intake valuation |
| ~8:00 AM | vp-ai-search-health-check | Chrome ×~15 page loads |
| 8:00 AM | vp-deal-of-week-monday-prompt | Slack |
| 8:30 AM | vp-ai-search-autofix | Chrome + Sheets; parses the 8:00 post |
| 9:00 AM | weekly-social-media-recap | script |
| ~9 AM | brevo-preflight-watchdog | daily |
| 10:00 AM | brevo-welcome-new-contacts | daily |
| 10:10 AM | shop-in-store-sync | WP/WC + Chrome photos |
| 10:30 AM | google-reviews-post-watchdog | Chrome/Chekkit — **re-scrapes exactly what ran at 3 AM** |
| 11:00 AM | vp-deal-of-week-monday-reminder | Slack |
| 11:30 AM | marketing-ceo-briefing-weekly | reads 8 lanes; assumes all 8 already posted |
| 11:50 AM | brevo-weekly-draft-guard | Brevo |
| 12:30 PM | vp-deal-of-week-monday-pick | Brevo + Chrome image pipeline |
| 1:05 PM | vp-website-deals-weekly | Chrome + WP + Brevo — **35 min after the pick, and depends on its output** |
| 2:00 PM | blog-publisher-watchdog | curl |
| ~2:30 PM | vp-deal-reels-weekly | render + Publer |
| ~3:00 PM | vp-community-weekly | render + Publer |
| 4:10 PM | shop-in-store-sync (2nd) | |
| 7:44 PM | vp-casual-video-daily | daily |
| nightly | vp-website-shop-nightly | Chrome, known wedge risk |
| weekly-Mon, time unspecified | ebay-weekly-quality-fix, ebay-weekly-channel-audit, vp-follower-growth-monthly-check, vp-engagement-weekly, ebay-markdown-terminal-weekly | **Unscheduled-in-file — these are the collision wildcards** |

Collision hotspots:
1. **2:02–3:30 AM**: content-batch (long) overlaps two Chrome/GA4 tasks and a Chrome/Chekkit task, then postflight assumes the batch finished. Four Chrome consumers in 90 minutes.
2. **11:30 AM briefing** reads eight lanes but two of them (brevo-weekly-draft-guard 11:50, vp-deal-of-week-monday-pick 12:30) haven't run yet, and the eBay/store-KPI lanes have no pinned time. The briefing's "all eight complete before 11:30 AM" is asserted, never verified.
3. **12:30 → 1:05 PM**: only 35 minutes between the pick populating the campaign and vp-website-deals-weekly parsing it — and vp-website-deals-weekly's own addendum says the pick has repeatedly produced nothing.
4. **3 AM vs 10:30 AM**: two full Chekkit browser scrapes for the same numbers.
5. **shop-in-store-sync is the only marketing task with an explicit Bravo/Parallels contention rule**; the other Monday Chrome tasks have no mutual-exclusion mechanism at all, and vp-website-shop-nightly has already wedged Chrome for 30 minutes once.

## (g) Model tier distribution (56 tasks)

| Tier | Count | Tasks |
|---|---|---|
| **claude-opus-4-8** | 6 | monthly-we-buy-gold-silver-email, nightly-chekkit-review-responses, valley-pawn-blog-publisher, vp-content-batch-weekly, vp-comedy-reel-weekly, vp-creative-refresh-quarterly |
| **claude-sonnet-5** | 43 | (default) |
| **claude-haiku-4-5** | 5 | vp-weekly-spot-price-update, vp-website-trend-daily-refresh, vp-deal-of-week-monday-prompt, blog-publisher-watchdog, vp-staff-video-prompt |
| **none** | 2 | ebay-feedback-reply-weekly, monthly-eom-recap |

Tier observations worth acting on:
- **nightly-chekkit-review-responses is opus** but its work is a deterministic click-loop (find button → Generate Response → Post). Sonnet or a Chekkit API would do it. This is the most expensive misallocation in the set given it runs nightly.
- **vp-creative-refresh-quarterly's opus pin is explicitly justified in-file** ("the one genuinely creative job in the fleet, runs four times a year") — that's the right reasoning and the right tier.
- **vp-website-trend-daily-refresh is haiku** but is asked to scrape 10 GA4 report tables, reconstruct a 5-horizon `DATA` object, and interpolate missing series. Under-tiered for the judgment it's authorized to exercise.
- **blog-publisher-watchdog is haiku** running a 3-branch verification ladder that already produced a false-positive DM.
- **ebay-feedback-reply-weekly has no model pinned** and writes **permanent, uneditable public replies** to buyers on the company's behalf. That is the highest-consequence unpinned task in the fleet and should be pinned explicitly.