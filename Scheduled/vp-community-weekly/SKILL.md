---
name: vp-community-weekly
description: Monday 3:10 PM — stage the week's city-specific Community posts (3-4/week per store, each town in its own voice) from CITY_COMMUNITY_KB.md, selected by the creative drift engine. Zero product-photo dependency.
---

---
model: claude-sonnet-5
---

# vp-community-weekly — Lane C, city-specific community content

**Why this task exists and why it is SEPARATE.** The 2026-08-22 audit found that Community posts
are Valley Pawn's single best-performing organic content — Skyline Drive, Walker Street/VMI, and
named employees all landed in the top 5 of 554 posts — and that the Community pillar was skipped
entirely, week after week, because it was generated inside the same run as product posts and got
shed first whenever the photo pipeline broke. Verbatim from #vp-studio-queue 2026-08-10:
*"Community + Humor pillars — not attempted this run given the image-pipeline gap."*

Community content needs **no product photo**. It was never supposed to share that failure mode.
This task owns it, alone, and it must never be allowed to depend on product imagery again.

**Read first:** `~/Documents/Claude/Projects/Refine Social Media/CITY_COMMUNITY_KB.md` (the local
truth for all 5 towns), `CREATIVE_DRIFT.md`, `vp-brand-studio`, `valley-pawn-context`.

---

## THE THREE HARD RULES — a post that breaks any of these does not ship

1. **No CTA. No product. No price. No "come see us."** The voice test: *if a stranger would read it
   as "a local business that loves its town," it's right. If it reads as marketing, rewrite or kill
   it.*
2. **Never name a competitor. Never name a private individual. No politics, no crime.**
3. **A wrong local detail is worse than no post.** `CITY_COMMUNITY_KB.md` tags every date:
   `[C26]` = confirmed, safe to publish dated · `[PATTERN]` = the tradition is real but the 2026
   date is NOT published — write about the tradition and **never state a date** · `[VERIFY]` = do
   not publish without a fresh check.

Two named landmines the KB documents in detail, repeated here because they are unrecoverable:
- **Lexington:** stay entirely off Confederate memorial history, Lee Chapel, Lee-Jackson Day.
- **Waynesboro:** the circulating "Nov 21 tree lighting / Nov 22 parade" is **2025 data**. Publish
  no Waynesboro holiday date until mainstreetwaynesboro.org posts the 2026 one.

## Step 0 — File access
File tools first. If a Projects path is unreachable, do NOT call `request_cowork_directory` (nobody
is present to approve at 3 PM on a schedule). Fall back to `mcp__Control_your_Mac__osascript` →
`do shell script`. This is a hard requirement, not a preference.

## Step 1 — Ask the drift engine what to run
    cd ~/Documents/Claude/Projects/Refine Social Media
    /usr/bin/python3 creative_drift.py status
    /usr/bin/python3 creative_drift.py select --lane community --slots 4 --account <Store>

Run `select` **once per store** — cooldowns are tracked per account, so each town gets a different
slate. The engine enforces the 45-day hook cooldown and reserves a share of slots for formats that
have never run (currently 40%, because the audit showed volume without signal). **Do not override
its picks.** If it reports `⚠ UNDER-FILL`, ship what it gave you and note it in the log — that is
the signal that the registry needs new candidates at the next quarterly refresh.

## Step 2 — Write, town by town, in that town's own words
For each store, take the selected format and fill it from that town's section of
`CITY_COMMUNITY_KB.md`. Use the town's actual vocabulary — "Rocktown" and "the Burg" for
Harrisonburg, "the Depot" for Culpeper, "the Gap"/"Basic City" for Waynesboro, "the Institute" and
"Keydets" (never "Cadets") for Lexington, "the Star City"/"Big Lick"/"the Cove" for Roanoke.

**Priority order for the week's subject:**
1. A `[C26]` dated local event happening that week in that town — this always wins the slot.
2. The seasonal hook for the current season (the drift engine's `status` prints it).
3. An evergreen landmark or detail from the KB that is off cooldown.

**Regional accuracy is not optional and locals will notice:**
- Culpeper is **Piedmont, not Shenandoah Valley**, and its foliage peaks **later** than the
  mountain towns.
- Roanoke is **"Virginia's Blue Ridge," not Shenandoah Valley.**
- The Blue Ridge Parkway line belongs to **Waynesboro (Milepost 0) and Roanoke** — for Lexington
  it is "nearby," never "our Parkway."
- First frost genuinely differs: Harrisonburg Oct 1–15, Lexington Oct 16–31, Roanoke ~Oct 22.
  **A single "fall is here" post fanned to all five is exactly the byte-identical failure this
  whole rebuild exists to end.**

## Step 3 — Imagery
Community posts do NOT need a product photo, and must never wait on one.
- Best: a real photograph of the actual place.
- Acceptable: a Midjourney render per `vp-brand-studio` STYLE-B (Heritage Story) or STYLE-E
  (Documentary Real) that depicts the *kind* of place honestly.
- **Never** reuse the same image across two different towns' pages — `PILLAR_OVERLAY` §7 exists
  because generic AI "mood" renders were caught running pixel-identical across different stores'
  Google Business Profiles.
- If no image is reachable, **ship it as a text post.** A text-only community post is a completely
  legitimate post. Shipping nothing is not.

## Step 4 — Publish via Publer
Route through `vp_social_publisher.py` / `PublerClient` — never a one-off script.
- Auth is `Authorization: Bearer-API {key}` and **requires a browser User-Agent** or Cloudflare
  returns `error code: 1010`. A 403 does not mean the key is dead.
- Always pass explicit `from`/`to` when listing posts to verify — `GET /posts` silently caps at ~15
  results without them.
- **No Meta Graph API** — every Page token died 2026-08-21 with the password change.

Routing: each community post goes to **that store's FB page + that store's GBP**, with a
**genuinely different caption on each** — not the same string twice. Brand-tier community goes to
Brand FB + IG + X. Spread across the week; do not stack.

**Harrisonburg gets first pick every week until it reaches parity.** It published 13 posts in the
audited 90 days against Culpeper's 111 — one a week versus eight and a half — while having the
richest local event calendar of the five.

## Step 5 — Record and log
For each post published:

    /usr/bin/python3 creative_drift.py record --format-id <id> --account <Account> --engagement 0 --reach 0

Post a compact log to `#social-media` (C0BMRC2LN3D): how many community posts staged, per town,
which format each used. Verify against Publer's real scheduled list, not your own manifest (Rule 12).

DM Joshua (`D03BHQH5VGT`) ONLY if the lane shipped fewer than 5 posts total after remediation —
plain language, no technical detail. Never send a failure notice to a team channel or a manager.

## Step 6 — Keep the KB alive
If you verify a new local fact, or find one in the KB that turned out wrong, append it to
`CITY_COMMUNITY_KB.md` with a date and a confidence tag. **Strike and annotate wrong facts — never
silently delete them**, or a future run will rediscover and re-post the same error.
