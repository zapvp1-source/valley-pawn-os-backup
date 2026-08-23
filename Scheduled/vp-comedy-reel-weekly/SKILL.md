---
name: vp-comedy-reel-weekly
description: Wednesday 6:30 PM — write and render 2-3 deadpan comedy/story short-form videos (beat-timed card format, works muted) and publish to Brand FB/IG Reels + TikTok. Humor guardrails enforced in code.
---

---
model: claude-sonnet-5
---

# vp-comedy-reel-weekly — Lane B3, the engagement-driver videos

**Why this exists.** Joshua, 2026-08-22: *"we need comedy AI generated videos just to keep
engagement."* The 90-day audit backs it: median engagement is 0.0 on 8 of 9 accounts, the best post
in 90 days scored 9 interactions, and the whole brand received 18 comments in three months. Product
posts are not going to fix that. Something people actually want to watch might.

**Read first:** `vp-brand-studio`, `valley-pawn-context`, `PILLAR_OVERLAY` (humor section),
`CREATIVE_DRIFT.md`.

---

## The format, and why it's this format
There is no text-to-video model reachable from a headless scheduled run on this Mac. So this lane
renders **beat-timed text video over stills** via `vp_comedy_reel.py` — the deadpan card format
that carries most successful short-form humor.

Design it to work **MUTED.** Reels and TikTok autoplay silent and most viewers never turn sound on.
The joke lands in the typography and the cut timing. Voiceover (macOS `say`) is available via
`"voice": true` and is a bonus, never the delivery mechanism.

## Step 0 — File access
File tools first. If a Projects path is unreachable, do NOT call `request_cowork_directory` —
nobody is present to approve at 6:30 PM on a schedule. Fall back to
`mcp__Control_your_Mac__osascript` → `do shell script`. Working dir:
`~/Documents/Claude/Projects/Refine Social Media`

## Step 1 — Pick the bit format
    /usr/bin/python3 creative_drift.py select --lane humor --slots 1 --account Brand
    /usr/bin/python3 creative_drift.py select --lane video --slots 2 --account Brand

Ship **2–3 videos a week: at most 1 humor bit** (hard 10% pillar ceiling, 60-day cooldown per bit,
enforced by the engine) **plus 1–2 story videos** (`vid_walked_in`, `vid_one_object`) which are not
humor and carry no cap.

## Step 2 — Write from REAL material
The funniest thing Valley Pawn owns is what actually crossed the counter. Pull from this week's
`#deal-of-the-week`, `#in-store-inventory`, the eBay listings, or fresh Bravo inventory.
**Never invent an item to make a joke work** — that is a hard authenticity violation
(`PILLAR_OVERLAY` §6) and it is exactly how the toy-riding-mower incident happened.

**What good looks like — dry Shenandoah humor, `vp-brand-studio` STYLE-D:**
- *POV: the item.* "POV: you're a Cornwell toolbox / Same garage since 1998 / You've held every
  socket that ever went missing / You know exactly where they are / **You're not telling**"
- *What walked in this week.* A straight round-up, delivered deadpan. The comedy is in the
  understatement, not in a punchline.
- *The story of one object.* Not a joke at all — quiet, specific, a little reverent. These
  consistently outperform jokes and there is no cap on them.

**Beat discipline:** 4–6 beats, 2.0–3.0s each, 12–18s total. The last beat is the punch (set
`"punch": true` — it renders in gold Playfair with a rule under it). Every beat must earn its hold.

## Step 3 — GUARDRAILS (the engine enforces these; do not try to route around them)
`vp_comedy_reel.py` runs `check_script()` and **hard-blocks the render** on a violation:
- **Never mock a customer.**
- **Never joke about needing money, being broke, hard times, rent, or eviction** — that is our
  customers' actual life, and pawn is where people go when it gets hard.
- **Never firearms.** Not in a joke, not as a prop, not in the background.
- **Punch at objects, never at people.**

Check before you render:

    /usr/bin/python3 vp_comedy_reel.py --spec bit.json --check-only

If a bit gets blocked, **rewrite it — do not disable the check.** If a block looks like a false
positive (the word appears innocently), rewrite around the word anyway. A false positive costs one
bit; a false negative costs the brand.

## Step 4 — Render
    /usr/bin/python3 vp_comedy_reel.py --spec bits.json --outdir reels/

Spec format is in the module docstring. `"image"` is optional — pure card videos on the brand navy
field work fine, and a Midjourney still (via `~/.vp-studio/scripts/generate.py`, STYLE-D or
STYLE-F) or a real product photo both work as backdrops. The engine washes the backdrop heavily so
type always reads.

The renderer encodes to scratch and atomically moves the finished file into place, retrying once —
so **never treat the presence of a file as proof of success.** Read the run output.

## Step 5 — Captions and publishing
Route through `vp_social_publisher.py` / `PublerClient`, never a one-off script.
- Publer auth is `Authorization: Bearer-API {key}` **plus a browser User-Agent** or Cloudflare
  returns `error code: 1010`. A 403 does not mean the key is dead.
- Always pass explicit `from`/`to` when listing posts to verify — `GET /posts` silently caps at ~15.
- **No Meta Graph API** — every Page token died 2026-08-21.

Route to **Brand FB (Reel) + Brand IG (Reel) + BrandTikTok**. Rotate one store FB per week so the
humor doesn't live only on the brand page. TikTok published ZERO posts in its entire history —
this lane and the deal reels are what finally use it.

Caption rules, all violated in the audit: no empty captions ever; no byte-identical text across
accounts; end on a question so the bit has somewhere to go in the comments.

Schedule **Thursday–Saturday evening**. Nobody watches a comedy reel at 2 AM.

## Step 6 — Comment window
Short-form comedy lives or dies in the first hour. After each publishes, schedule a
`reel-comment-alert` one-shot for **publish time + 30 minutes**. Replying inside the first 60
minutes is the single biggest reach signal on Meta.

## Step 7 — Record and log
    /usr/bin/python3 creative_drift.py record --format-id <id> --account <Account> --engagement 0 --reach 0

Log to `#vp-studio-queue` (C0BHTEUPADB): bits rendered, bits blocked by guardrails (and why —
that's useful signal, not a failure), where they published.

Verify against Publer's real list, not your manifest (Rule 12). DM Joshua (`D03BHQH5VGT`) only if
zero videos shipped after remediation, in plain language. Never send failure notices to a team
channel or to a manager.

## Step 8 — Feed the drift engine
If a bit format is clearly working or clearly dying, that shows up automatically through
`creative_drift.py`'s scoring — **do not hand-promote or hand-retire a format.** The engine
deliberately ignores performance below 30 posts, because the old Friday loop was moving the whole
content mix on n=8 and single-digit engagement. Let it gather the sample.
