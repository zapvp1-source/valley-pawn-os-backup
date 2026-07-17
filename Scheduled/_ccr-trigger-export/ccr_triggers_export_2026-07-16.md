# CCR Trigger Export — 2026-07-16

JSON export of all Claude Code Remote scheduled trigger definitions (schedule + prompt), wrapped in a fenced block so it rides the nightly GitHub backup (whitelist covers .md only, .json is git-ignored).

```json
{
  "exported_at": "2026-07-16T21:15:00Z",
  "source": "Claude Code Remote list_triggers export",
  "note": "These trigger definitions (schedule + prompt) previously existed ONLY in Claude's cloud. This export makes them recoverable if Claude/CCR becomes unavailable. The SKILL.md files they reference are already on local disk under Documents/Claude/Scheduled/. NOTE: the dashboard-data-collector CCR trigger listed here was deleted 2026-07-16 and replaced by a native launchd job (com.valleypawn.dashboarddatacollector).",
  "trigger_count": 17,
  "triggers": [
    {
      "id": "trig_01PHMgnKdFvQMjEEoHqNL5Dv",
      "name": "send_later 2026-07-17T11:50Z #87f569",
      "cron_expression": null,
      "run_once_at": "2026-07-17T11:50:00Z",
      "enabled": true,
      "prompt": "Daily safety-net delivery for daily-loan-inventory-text (2026-07-17). The permanent scheduler decision may still be pending. Via the Control-your-Mac osascript bridge: run /Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/daily_run.sh detached, poll latest_status.txt until OK/FAIL (cap ~30 min), then send latest_message.txt via send_imessage to BOTH +18049304221 (Joshua) and +15408364200 (Preston). If FAIL, text both a one-line couldn't-pull note. Then: if Joshua has approved a permanent scheduler (launchd or app-scheduler) and it's confirmed working, stop re-arming this safety net; otherwise re-arm another send_later for the next morning ~11:50 UTC so deliveries continue."
    },
    {
      "id": "trig_01JyqNmFeK1ggS66e7XLqVsc",
      "name": "dashboard-data-collector (DELETED 2026-07-16 — replaced by native launchd job)",
      "cron_expression": "15 * * * *",
      "run_once_at": null,
      "enabled": false,
      "prompt": "(historical) Read the SKILL.md at /Users/joshuadavis/Documents/Claude/Scheduled/dashboard-data-collector/SKILL.md and execute. Replaced by com.valleypawn.dashboarddatacollector launchd job running collect.sh natively — the CCR sandbox had no network or Keychain access so this trigger could never complete."
    },
    {
      "id": "trig_018gSpHajorxNZik4VbnqKus",
      "name": "daily-loan-inventory-text",
      "cron_expression": "30 11 * * *",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Unattended scheduled run — execute end to end, do NOT ask questions. Task: text the Valley Pawn company Loan Balance and Inventory Balance (all 5 stores combined) plus growth since the last day of the previous month, to BOTH recipients defined in the SKILL.md. Read and follow /Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/SKILL.md exactly, via the Control-your-Mac osascript bridge — it is the authoritative source for the steps AND the recipient list. Flow: 1. Launch the detached pull: daily_run.sh. 2. Poll latest_status.txt in <=18s sleeps across SEPARATE osascript calls, cap ~25 min, until OK or FAIL. 3. On OK: cat latest_message.txt and send that exact text via send_imessage to Joshua (804) 930-4221 AND Preston (540) 836-4200 (one call each). If Messages times out, launch the Messages app and retry once. If Joshua's iMessage still errors, Slack-DM the same text to user U03BB52MDSA. Send to each recipient independently. 4. On FAIL: iMessage both recipients a one-line note that the Bravo pull failed this morning and will retry tomorrow. Data comes from the Bravo company-kpis pipeline cell. Runs on claude-sonnet-5 per the SKILL.md frontmatter."
    },
    {
      "id": "trig_01V6bYoh9dy2SeeTk5pm7zFX",
      "name": "vp-website-trend-daily-refresh",
      "cron_expression": "30 10 * * *",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Refresh the Vp Website Trend Cowork artifact (id: vp-website-trend) with today's live GA4 numbers for thevalleypawn.com. CRITICAL: the GA4 property (id 353209303, Valley Pawn) is owned by fullcirclepawn@gmail.com — NOT jdavis@fcfpawn.com. Use claude-in-chrome to open analytics.google.com, switch to fullcirclepawn@gmail.com (authuser=1, property a256872788p353209303). Read Engagement > Pages and screens for Daily/Weekly/Monthly/Quarterly/Annual horizons with period-over-period comparison (set comparison via in-UI picker, not URL). Also Traffic acquisition channel grouping. BY-STORE ROLLUP: on Pages and screens trailing 28 days, filter for culpeper, waynesboro, harrisonburg, lexington, roanoke one at a time and read the filtered Total row Views/Active users for each. Stage the current artifact HTML via device_stage_files artifact_ids [vp-website-trend], preserve structure, update DATA + STORE_DATA objects and Refreshed timestamp. Never fabricate numbers — if a horizon can't be read, leave prior data and note in an HTML comment. Write updated HTML, SendUserFile, update_artifact id vp-website-trend. On login failure or UI change: STOP, post to Slack #claude-notifications, leave artifact untouched. Do not touch vp-website-kpis."
    },
    {
      "id": "trig_01BvZe5s47iVGx95e9mqDTGP",
      "name": "vp-casual-video-daily",
      "cron_expression": "0 23 * * 1,3,5",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Run Valley Pawn's casual-video pipeline. Read project memory (vp-* topics re casual video, pillar overlay, content review) then /Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/PILLAR_OVERLAY.md Sections 5 and 8 (authoritative). Steps: 1. List /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/casual-video-inbox/ — if unreachable or no new clips (mp4/mov not in processed/), log and stop (normal no-op, no DM). 2. For each new clip, check optional sidecar {samebasename}.txt (line 1 = lower-third title, rest = caption). Process per PILLAR_OVERLAY Section 5: burn in captions/lower-third/end-card, 9:16. 3. Captions must pass Section 6 authenticity bar — concrete real detail, no fabricated claims, X gets separate <=270-char version. 4. Publish ONLY via python3 vp_social_publisher.py <manifest.json> in Refine Social Media/ — never PublerClient directly. Route brand tier: Brand FB + BrandIG + BrandTikTok + BrandTwitter, evening slot 5-8 PM ET. 5. Move processed originals to processed/; failures stay in place + logged to failed.log. Only DM Joshua on full-batch failure or structural blocker. 6. If published, one-line summary to Slack #vp-studio-queue. 3x/week phased re-enable — do not escalate cadence."
    },
    {
      "id": "trig_01JbKVdL8f9dk7Gx6zVcXP7d",
      "name": "vp-content-batch-weekly",
      "cron_expression": "0 0 * * 1",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Run Valley Pawn's weekly social content batch. Read in order: project memory (Publer, pillar overlay, content review, authenticity topics), Skills vp-content-batch, vp-brand-studio, valley-pawn-context, bravo-context, then /Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/PILLAR_OVERLAY.md (AUTHORITATIVE, esp Sections 6, 7, 8). Hard rules: 1. NEVER call PublerClient.schedule_post() directly — ONLY python3 vp_social_publisher.py <manifest.json> (has qa_check_caption + qa_check_image_diversity gates). 2. Every caption non-empty with at least one concrete real detail. 3. FB and GBP: no hashtags; GBP: no phone numbers or ALL-CAPS; IG may have hashtags; distinct caption per platform. 4. GBP store_keys: GBP_Lexington, GBP_Waynesboro, GBP_Harrisonburg, GBP_Roanoke, GBP_Culpeper. 5. Imagery genuinely specific per store — never reuse one generic image across stores. 6. Weekly Reels quota 4; rotate store coverage; default to video. 7. Build manifest per PILLAR_OVERLAY Section 3 pillar mix, --dry-run first, fix QA failures, then run for real. 8. Summary to #vp-studio-queue + DM Joshua (U03BB52MDSA) one paragraph. 9. Stale Bravo data: use most recent, note staleness. 10. Blocked >half: DM Joshua, don't silently skip. Sundays 8 PM ET."
    },
    {
      "id": "trig_01Mdrt66qbEC9Pi8ddWL5Rba",
      "name": "vp-publer-analytics-friday",
      "cron_expression": "0 20 * * 5",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Run Valley Pawn's weekly Publer performance digest. Read project memory (Publer/content review/pillar overlay). 1. cd /Users/joshuadavis/Documents/Claude/Projects/Refine Social Media, run: python3 publer_weekly_digest.py --days 7. 2. Script fixed 2026-07-11 (from/to params) — if it errors, investigate the actual error and DM Joshua if unresolvable; a broken measurement loop let bad content ship undetected before. 3. Script writes friday_digests/friday_digest_{date}.md, weekly-adjustments.json, adjustments_log.jsonl. Read the digest. 4. DM Joshua (U03BB52MDSA) the one-line digest plus one sentence of your own read. 5. Spot-check 3-5 published post captions via publer_client — none blank, no factual errors (store hours, Dixie Pawn — see STORE_FACTS/qa_check_caption). Flag violations in the DM. Fridays 4 PM ET."
    },
    {
      "id": "trig_01X5VvBp4SxFPpCA77UBvGEM",
      "name": "Salt Run Landscape — Weekly Analytics Check",
      "cron_expression": "0 13 * * 1",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Check traffic on saltrunlandscape.com and report a concise weekly summary. Use Claude in Chrome to open analytics.google.com, switch to fullcirclepawn@gmail.com. Salt Run Landscape GA4 property (account Valley Pawn 256872788, property ID 536416720, URL pattern .../a256872788p536416720/reports/intelligenthome). Read Home report last 7 days. Report: sessions/active users, new users, top channels (flag if Organic Search still 0), pages viewed, engagement signals beyond bare page_view. Compare to prior week. Keep short — early-stage traction test; call out plainly if still just bots vs. real change (first organic visit, referral, engaged session)."
    },
    {
      "id": "trig_01RnL93Y6URsJE1aJYxQKsZt",
      "name": "vp-ai-visibility-autofix",
      "cron_expression": "30 13 * * 5",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Run vp-ai-visibility-autofix — self-healing companion to vp-ai-visibility-metrics. Read /Users/joshuadavis/Documents/Claude/Scheduled/vp-ai-visibility-autofix/SKILL.md (authoritative) and execute. Fallback summary: read latest AI Visibility Scorecard in Slack #ai-marketing (C0BCEESUANM). Whitelist fixes: (A) GA4 AI Assistants Tracking channel regex repair (add tokens only, never remove) — GA4 Admin authuser=1 a256872788/p353209303 fullcirclepawn@gmail.com; (B) legacy Dixie Pawn brand in owned content (company FB posts via Graph API token, WordPress pages via WP MCP) — edit to Valley Pawn; never touch customer review text; (C) Copilot blocked -> substitute Bing local pack as proxy, label Copilot (via Bing proxy). Do NOT touch third-party listing claims or review-volume mechanisms. Log to AI Search Autofix Log sheet (1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY). Post summary to #ai-marketing, sign Sent using Claude."
    },
    {
      "id": "trig_01QMmNVXRHix4svQ1ZsA9BUD",
      "name": "vp-ai-search-autofix",
      "cron_expression": "30 12 * * 1",
      "run_once_at": null,
      "enabled": true,
      "prompt": "Run vp-ai-search-autofix — self-healing companion to vp-ai-search-health-check. Read /Users/joshuadavis/Documents/Claude/Scheduled/vp-ai-search-autofix/SKILL.md (authoritative) and execute. Fallback summary: read latest health-check post in #ai-marketing (C0BCEESUANM). If clean week: one log row, no Slack post. Whitelist: (A) WPCode snippet #738 (schema) or #742 (llms.txt) inactive -> reactivate toggle only via WordPress.com MCP, verify live; (B) Bing Places NAP drift on owned listing -> directory-listing-push scoped to that store+field, verify, log submitted-pending if not yet reflected; (C) Google NAP drift same pattern. Never touch unowned listings, account signups, or content copy beyond canonical valley-pawn-context. Log every action to AI Search Autofix Log sheet (1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY). Needs-Joshua queue for everything else. Post to #ai-marketing only if something acted on."
    },
    {
      "id": "trig_01ALDeEwMDumyXwA2ke2mVCH",
      "name": "AWB Campaign — Week 3 Send (Jul 21)",
      "cron_expression": null,
      "run_once_at": "2026-07-21T13:00:00Z",
      "enabled": true,
      "prompt": "Send Week 3 (final) of the 3-part Valley Pawn AWB legal-status email series. Weeks 1 (#44, 7/08) and 2 (7/15) went to Brevo lists 3+10 (~11,930 recipients). Fully autonomous. 1. Load brevo-context + valley-pawn-context, read project memory awb-campaign.md. 2. RESEARCH FIRST (WebSearch) current VA assault weapons ban status: Lancaster County injunction, Washington County (Santolla v. Katz), Spotsylvania (Curtis v. Katz), Fauquier, VA Supreme Court handling, DOJ federal suit, AG Jay Jones. Only say business-as-usual if genuinely true — do not fabricate resolution. 3. Bridge Brevo API key (~/.config/valley-pawn/brevo_api_key, base64 via osascript per brevo-key-sandbox-bridge.md), verify GET /v3/account = 200. 4. Build Week 3 HTML on VP Master Template 11 (logo, hero, body, trust strip, CTA, 5-store directory Call+Text+Directions, hours, DBA-only footer — never Full Circle Finance Inc). Subject 35-55 chars calm/factual. Eyebrow: LEGAL UPDATE — WEEK 3 OF 3. utm_campaign awb_update_2026-07-21_wk3. 5. POST /v3/emailCampaigns recipients listIds [3,10], sender Valley Pawn jdavis@fcfpawn.com, name AWB Update Week 3 - 2026-07-21. 6. GATE: python3 brevo_preflight.py <id> (5 Call + 5 Text buttons, >=10 utm_content, no Full Circle Finance Inc). Fail -> fix; unresolvable -> leave draft + alert #email-campaigns or DM U03BB52MDSA. 7. PASS -> sendNow, verify queued. 8. Summary to #email-campaigns; update awb-campaign.md."
    }
  ],
  "expired_one_shots_omitted": "7 already-fired send_later verification one-shots omitted from this export (historical, non-recurring). Full raw export retained in the Claude session that produced this file."
}
```
