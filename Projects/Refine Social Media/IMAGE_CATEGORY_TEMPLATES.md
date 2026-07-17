# Valley Pawn — Image Category Templates (created 2026-07-13)

**Why this file exists:** `vp-brand-studio/SKILL.md` repeatedly instructs `vp-hero-image`
to read `vp-brand-studio/references/prompt-templates.md` for "per-category prompt
templates" (the thing that's supposed to make a watch shoot differently than a guitar
than a pile of scrap gold than a riding lawn mower). **That file does not exist.** Neither
does `references/channel-specs.md`. Confirmed by direct filesystem check 2026-07-13 —
`vp-brand-studio`'s skill directory contains only `SKILL.md`, no `references/` folder at
all. Every hero-image generation has been running with zero category guidance and
falling back to one generic small-object "collector's desk" composition (leather desk,
brass compass, antique map, magnifying glass — the STYLE-B "Heritage Story" look)
regardless of what the actual item is or how big it is.

**The proof:** Joshua flagged a live Waynesboro post 2026-07-13 — a Troy-Bilt Super
Bronco XP 50 **riding lawn mower** (a ~5-6 foot outdoor vehicle) rendered as a toy-scale
model sitting on a leather desktop next to a brass compass with an antique map behind it.
It looks like a die-cast toy, not a real machine — because the generator used the same
tabletop-collectible staging it uses for a pocket watch or a gold chain. Joshua's words:
"this does not represent the product at all... AI should be enhancing our posts not
making them look like AI." **On follow-up, Joshua flagged something even more basic:
the rendered machine doesn't even look like a Troy-Bilt mower at all** — it's a
generically-invented red-and-black tractor with knobby tires and a tined attachment,
nothing like the real Super Bronco XP 50's actual deck/body design. So this item had
TWO separate failures stacked: wrong scale/setting (toy-on-a-desk) AND wrong product
identity (doesn't resemble the real make/model being sold at all). The identity failure
is the more serious one — a customer who walks into Waynesboro expecting to see what
they saw in the ad will find a completely different-looking machine. This is a distinct,
separate problem from the image-reuse issue fixed earlier the same day (Section 7 of
`PILLAR_OVERLAY.md`) — that one was about the SAME image reused across different stores;
this one is about a render that never matched the real item at all, even the first
time it's used, in either size or appearance.

**Until `vp-brand-studio`'s real `references/prompt-templates.md` gets built, treat this
file as the authoritative category-template substitute.** `vp-hero-image` and
`vp-content-batch` must read this file whenever `vp-brand-studio/references/
prompt-templates.md` is missing (it is, as of 2026-07-13).

---

## Rule 0 — product identity comes before scale (read this first, applies to every bucket)

Pawn shop inventory is used, one-of-a-kind, specific physical units — not a generic
archetype. "A gold chain" can be stock-rendered and still read as honest, because one
gold chain looks reasonably like another. **"A Troy-Bilt Super Bronco XP 50" cannot** —
it has a specific real design, and a customer expects the ad to show that actual design,
not an AI's generic idea of "a tractor." The same applies to anything with a real
brand/model identity: power tools, appliances, electronics, instruments, vehicles,
named-model equipment of any kind.

**Hard rule: any post advertising a specific real inventory item with a recognizable
brand/model MUST use one of these, in priority order:**
1. **A real photo of the actual unit** (from Bravo's item photos if the SKU has one, or
   a phone photo a manager takes) — always the first choice for named-model equipment,
   tools, electronics, and anything where the real design matters to the buyer.
2. **An MJ render generated with `--cref` against a real photo of that specific unit**
   (per `vp-hero-image`'s own documented "Local item photo" input — this capability
   already exists in the skill, it just wasn't used for the mower post). This is
   acceptable when a fully real photo isn't available but a reference photo is.
3. **A fully generic AI render with no photo reference at all is ONLY acceptable for
   generic, non-brand-specific categories** where one example of the category looks
   like any other — loose gold/jewelry by weight, generic coins, unbranded small
   accessories. It is NOT acceptable for anything with a specific make/model in the
   caption (a named mower, a named guitar model, a named appliance brand, a named gun
   safe, etc.) — if the caption names a specific model, the image must actually be (or
   be referenced from) that model, not an invented stand-in.

If neither a real photo nor a reference photo is available for a named-model item, the
correct move is to hold that item out of the batch and flag it for a manager to snap a
quick photo — not to publish a generic invention under a specific product's name.

---

## The scale/setting rule: composition must match the real item's size

Before rendering, classify the item into one of these buckets. **Never use a tabletop/
desk/compass/map composition for anything that wouldn't actually fit on a real desk.**
If in doubt, ask: "would this item realistically sit on a leather-topped writing desk
next to a compass?" If no, use the large-item treatment instead.

### Bucket 1 — Small valuables (desk/tabletop staging is correct here)
Jewelry, watches, coins, currency, small firearms accessories (non-firearm), pocket
knives, small electronics (phones, handheld gaming), small musical accessories, medals,
antique small objects. **This is the ONLY bucket where the leather-desk/compass/map
"Heritage Story" (STYLE-B) treatment belongs.** Real scale: fits in a hand or on a small
tray.

### Bucket 2 — Mid-size items (counter/case staging, STYLE-C showroom catalog)
Guitars, amps (small-to-combo size), handheld power tools (drills, saws), cameras,
laptops, mid-size electronics, handbags, smaller collectibles displayed upright.
Staging: an oak counter or showroom case, item upright at true scale, soft-focus store
interior behind it — NOT a flat desk with tabletop props sized for jewelry. (The Taylor
guitar and VOX amp posts in the 2026-07-11 imagery audit are good examples of this
bucket done right — keep using that same real-scale-showroom approach for this bucket.)

### Bucket 3 — Large equipment (NEVER desk/tabletop staging)
Riding mowers, generators, tillers, ATVs/UTVs, pressure washers, air compressors, large
power tools, appliances (washers/dryers/refrigerators), furniture, anything with wheels
a person would ride or push. **Hard rule: render at true scale in a realistic setting —
a garage bay, a showroom floor, an outdoor driveway/lot, or the store's actual sales
floor — with a real scale reference in frame (a person partially in shot, a door frame,
a floor tile grid) so the proportions read as genuine.** Never place on a leather desk,
never pair with a compass/map/magnifying-glass prop, never let the item look smaller
than a piece of furniture would in real life. If a realistic MJ render can't be produced
reliably for this bucket, **prefer a real store/inventory photo over any AI render** —
a slightly less polished real photo beats a scale-broken fake every time.

### Bucket 4 — Firearms
Per `vp-brand-studio`'s existing hard rule: never rendered for any social-tier channel.
Substitute a different item from the same store's inventory. This rule is unchanged and
still enforced in `vp-hero-image` — do not touch it.

---

## Pre-publish sanity check (add to whatever QA step runs before scheduling)

Before a hero image ships, ask TWO questions, in order:
1. **"If the caption names a specific brand/model, does the image actually look like
   that brand/model?"** (Rule 0.) If it's a generic invented stand-in for a named
   product, it fails — real photo or cref-referenced render only.
2. **"Does this image look like a photo/render of the actual real-world item at its
   actual real-world size, in a plausible real-world setting?"** If the honest answer
   is "no, it looks like a toy / miniature / diorama," it fails and must be regenerated
   in the correct bucket's staging or replaced with a real photo.

This is a simple, cheap gut-check any agent (or Joshua) can apply by eye — it doesn't
require automated image analysis, just looking at the result and asking whether it
represents the product honestly. Flag any failure back to this file so the rules above
can grow.

---

*Created 2026-07-13 after Joshua flagged a toy-scale riding-mower render. Referenced
from `PILLAR_OVERLAY.md` Section 9. Supersedes the missing
`vp-brand-studio/references/prompt-templates.md` until that file is actually built —
if a future session finds that file now exists and is populated, defer to it instead
and fold any still-relevant rules from this file in.*
