# Valley Pawn Social — Canonical System Spec
**Version 1.0 · 2026-09-06 · supersedes every other spec in this folder for anything it covers.**

Five documents described five different systems (`REFINE_SOCIAL_MEDIA_INDEX.md` 7/7,
`Valley Pawn Studios/vp_fb_content_strategy.md` 7/6, `PILLAR_OVERLAY.md` 7/13, the BUSINESS_OS
6/19 addenda, the 8/22 rebuild plan) and none matched the code. This file is the one to trust.
Where it is silent, `PILLAR_OVERLAY.md` (pillars/lanes) and `vp-brand-studio` (visual identity)
still apply.

---

## 1. Publishing reality

- **Publer is the only publishing path.** Business tier, workspace `6a358d48fe216c70f7e65d4e`,
  15 accounts (`publer_accounts.json`). The Meta Graph API is dead — every Page token was
  invalidated 2026-08-21 and the app was disabled 2026-07-04. `facebook-post` and
  `reel-comment-alert` cannot run; do not revive them, and never open `developers.facebook.com`.
- **`vp_social/publish.py` is the only writer.** Nothing else may call `schedule_post()`.
- **`vp_social/reader.py` is the only reader.** Every count in every report comes from the ledger.

### Publer landmines (all found live, all handled inside the engine)
| Landmine | Symptom | Handled by |
|---|---|---|
| No browser User-Agent | Cloudflare `error code: 1010`, looks like a dead API key | `Publisher._headers` |
| `GET /posts` without `from`/`to` | silently returns a short default slice → 5-6× undercount | `reader.fetch_posts` |
| Job status is `"complete"` | base client waits for `"completed"` → phantom `JOB_timeout` | `Publisher.wait_for_job` |
| Bulk `DELETE /posts` | ignores the ids array and wipes the **entire** queue (63 posts, 8/22) | `Publisher._request` refuses all DELETE |
| Video by `url` | job says complete, no post is created | media uploaded via `upload_media()`, referenced by id |
| `type: "reel"` | job says complete, no post is created | always `type: "video"` |
| Caption location | `text` is top-level, not `content.text` | `reader.normalize` |

## 2. Accounts and routing (2026-08-04 redesign, current)

- **Brand items** → Brand FB + Brand IG + Brand X. (`BrandBlog` is retired as a social slot:
  24 posts, 0 engagement. `valley-pawn-blog-publisher` owns real blog content.)
- **Store-local items** → that store's FB + that store's GBP. **No IG, no X.**
- **Video/reels** → store FB + Brand IG; compilations and comedy add Brand FB + TikTok.
- **Harrisonburg's live page is `474248069342834`.** `795439020329931` is a 21-follower shell —
  never post to it, never delete it (unpublish/merge only). Three skills still have this
  inverted; `publer_accounts.json` and this file are correct.
- Store IG accounts exist but are not connected. YouTube is dormant (0 videos, 13 subs).

## 3. Cadence targets (`vp_social/plan.py: TARGETS`)

Brand 7/wk · BrandIG 10 · BrandTwitter 3 · BrandTikTok 3 · each store FB 7 · each store GBP 7.
The planner **fills to target**: it counts what is already scheduled for the week in the ledger
(whatever lane put it there) and only adds slots up to the target. That is what makes a
parallel run with the legacy lanes safe, and what stops three lanes stacking the same deal.

## 4. The week

| When | What | Who owns it today |
|---|---|---|
| Mon ≤12:00 | Managers post the Deal of the Week (photo + price) in `#deal-of-the-week` | humans (10/10 for a month — the healthiest input in the department) |
| Mon 9:40 | Weekly recap → `#social-media` | `weekly-social-media-recap` → `python3 -m vp_social recap` |
| Mon 11:00 | Preflight | `vp-content-batch-preflight` |
| Mon 12:30–13:05 | Deal pick → Brevo draft → website mirror | deal-of-week tasks (untouched) |
| Mon 13:40 | Product batch | `vp-content-batch-weekly` |
| Mon 14:30 | Deal reels | `vp-deal-reels-weekly` |
| Mon 15:10 / 15:45 | Community / engagement + reply sweep | `vp-community-weekly` / `vp-engagement-weekly` |
| Mon 16:40 | Postflight | `vp-content-batch-postflight` |
| Tue 10:00 | Quota check | `vp-content-batch-quota-watchdog` |
| Wed 18:00 / 18:30 | Deal social gap-fill / comedy reels | `vp-deals-social-wednesday` / `vp-comedy-reel-weekly` |
| Thu 10:00 | Deal email sends; deal photo posts go live | Brevo + the plan's Thursday slots |
| Fri 16:00 | Analytics digest | `vp-publer-analytics-friday` → `python3 -m vp_social digest` |
| every report/plan run | Ledger sync (inline, if >6 h stale) | `report._fresh_or_sync()` |

**Why there is no nightly sync agent.** `com.valleypawn.social-ledger-sync` was built and installed
on 2026-09-06 and then **deliberately backed out** (plist parked at
`~/Library/LaunchAgents/com.valleypawn.social-ledger-sync.plist.disabled-needs-fda`). A
launchd-spawned process cannot read `~/Documents` on this Mac — it can execute nothing from there
("Operation not permitted") and, even when the runner is moved to `$HOME`, `import vp_social`
fails with `ModuleNotFoundError` because the directory listing is refused by TCC. Appending to an
existing log file there does work, which is what makes the failure look confusing. Granting
`/usr/bin/python3` Full Disk Access would fix it and needs one click from Joshua. It is **not
needed**: every report and the planner call `_fresh_or_sync()` and pull from Publer themselves if
the ledger is more than 6 hours old, so no number is ever computed from stale data. Re-enable the
agent only after the FDA grant, and verify with `python3 ~/vp_social_boot.py status`.

## 5. Hard content rules (enforced in code where marked ✅)

✅ No firearms/guns/ammo anywhere on social · ✅ never "Dixie Pawn" · ✅ never "Full Circle Finance"
customer-facing · ✅ no "fast cash / instant cash / no credit check" · ✅ no empty captions ·
✅ no byte-identical caption across two accounts or within 7 days · ✅ GBP: no hashtags, no phone
numbers, ≤1500 chars, ≤2 emojis · ✅ Facebook: no hashtags · ✅ X ≤270 chars · ✅ humor ≤1/week
fleet-wide · ✅ one photo + one video per item per page per 14 days · ✅ a "reveal tomorrow" post
requires a scheduled reveal slot.

Not code-enforced, still binding: hours facts (Culpeper Mon–Sat 10–6; others Mon/Tue/Thu/Fri/Sat
10–6, closed Wed & Sun; nobody closes at 5), one concrete real detail per caption, community posts
carry no CTA/product/price, humor never mocks customers or money trouble, real photo (or `--cref`)
for any named make/model, no image reused across different stores, and the brand-studio palette,
type, six styles and forbidden-trope list.

## 6. Engine reference

```
cd "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media"
python3 -m vp_social sync   [--back 21 --forward 30]   # Publer -> ledger
python3 -m vp_social recap  [--days 7]                  # Slack body on stdout; exit 2 = withhold
python3 -m vp_social digest [--days 7]                  # Friday DM body
python3 -m vp_social month  2026-08                     # month in review
python3 -m vp_social quota                              # per-account 7-day counts (JSON)
python3 -m vp_social plan   --week 2026-09-07 --deals state/deals_2026-09-07.json
python3 -m vp_social validate state/plans/plan_2026-09-07.json
python3 -m vp_social publish state/plans/plan_2026-09-07.json [--dry-run|--live]
python3 -m vp_social postflight plan_2026-09-07
python3 -m vp_social status
```

- **Exit-code contract** (same as `format_aged_inventory.py`): 0 = stdout is the finished Slack
  message, post it verbatim; 2 = stdout empty, reason on stderr, **post nothing** (Rule 18).
- **Dry run:** `state/DRY_RUN` exists → `publish` never calls Publer. Delete that file (or pass
  `--live`) to go live. It is present now, on purpose.
- **Ledger:** `state/social_ledger.sqlite` (`posts`, `planned`, `runs`). SQLite needs real file
  locking, so it only works on the Mac — a Cowork sandbox mount returns "disk I/O error". Set
  `VP_SOCIAL_LEDGER=/tmp/x.sqlite` for sandbox experiments.
- **Idempotency:** a placement is keyed `(week, lane, item_key, account_key)`. A re-run of the
  same plan skips anything already scheduled or published. Publishing twice is structurally
  impossible, which is what makes catch-up runs safe.
- **Plans** live in `state/plans/plan_<monday>.json`; each slot carries a `contract` telling the
  model exactly what to write per channel, with `captions` left null for it to fill.

## 7. What the model still does (and only this)

Captions per channel from the slot contract · community copy from `CITY_COMMUNITY_KB.md` ·
comedy beat scripts · engagement formats and the reply sweep · picking heroes for brand slots ·
judgement calls the drift engine surfaces. Everything else — what to post, where, when, whether
it duplicates something, whether it published, and every number reported afterwards — is code.

## 8. Known open items

- Task consolidation (17 social tasks → 4) is designed in `SOCIAL_DEPT_REVIEW_AND_PLAN_2026-09-05.md`
  §5 Phase 3 and **not built** — it needs a one-week parallel proving run first.
- $100/month giveaway has never drawn a winner (public since June) — awaiting Joshua's call.
- X: 29 posts, ~1 reach each, 0 followers — awaiting Joshua's call.
- Meta: business verification, Harrisonburg shell-page merge, 2021 boosted post with hostile
  comments — all need Joshua's login.
- Staff-video lane produced 4 videos on 9/1 after 61 empty days; `#casual-video` still doesn't exist.
- Community formats run dry mid-November at current cooldowns — top up `creative_state.json`.
