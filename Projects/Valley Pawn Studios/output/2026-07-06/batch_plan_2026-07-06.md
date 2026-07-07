# Valley Pawn — Weekly Content — Week of 2026-07-06 (reconciled state)

Generated 2026-07-06 (recovery after the 2 AM `vp-content-batch-weekly` run failed on missing folder access). **This file was corrected after discovering existing manual batches for this week — do not duplicate them.**

## Already produced this week (DO NOT re-create)

**Brand batch** — `batch_manifest_2026-07-06.json` — 4 Brand posts (Brand FB + @valley_pawn IG), heroes generated:
1. Warranty / "What's Right Is Right" — Tue 7/8 6:00 PM
2. Gold-buy / fair appraisals — Wed 7/9 10:00 AM
3. How pawn works (modern pawn) — Wed 7/9 6:00 PM
4. Heritage / Shenandoah since 2014 — Thu 7/10 12:00 PM

**Community-GBP batch** — `community_gbp_manifest_2026-07-08.json` — 5 GBP-only posts, one per store (Lexington 7/8, Culpeper 7/9, Waynesboro 7/10, Harrisonburg 7/11, Roanoke 7/12), heroes assigned.

So the **Brand tier and the store-local Community/GBP tier are done.** Publer publishing status not confirmed in files (no publish-result artifacts found) — verify in Publer.

---

## The genuine gap: Deals-of-the-Week (5) — NOT in either manifest above

Source: `#deal-of-the-week` (Mon 7/6, deadline noon). Value pillar, store-local, target `{Store} FB + @valley_pawn IG + {Store} GBP`, schedule Thursday 7/9 10 AM–4 PM (Value window), heroes from managers' submitted photos via `vp-hero-image --cref`. Captions are drafted and ready below.

### D1 — Harrisonburg — VOX Guitar Amp — $199 (Walker)
- **IG:** `Plug in and play. This VOX guitar amp just hit the floor at Valley Pawn Harrisonburg — classic VOX tone, clean condition, and ready to go for $199. Every purchase is backed by our 30-day warranty, because what's right is right. 📍 1790 E Market St, Ste 22, Harrisonburg  #ValleyPawn #WhatsRightIsRight #TheValleyPawn #Harrisonburg #GuitarGear #VOX`
- **FB:** (IG body, no hashtags)
- **GMP:** `A clean VOX guitar amp just came in at our Harrisonburg store — classic VOX tone and ready to play for $199, backed by our 30-day warranty. Stop by and give it a listen.`
- Slot: Thu 7/9 10:00 AM

### D2 — Culpeper — ASUS ROG Strix XG43UQ 43" Monitor — $499.99 (new $1,399) (Sandi)
- **IG:** `It's hot outside — let's game. This ASUS ROG Strix XG43UQ 43" gaming monitor is at Valley Pawn Culpeper for $499.99 — a new price of $1,399, so you're saving nearly $900. Backed by our 30-day warranty. 📍 571 James Madison Hwy, Culpeper  #ValleyPawn #WhatsRightIsRight #TheValleyPawn #Culpeper #PCGaming #ROG`
- **FB:** (IG body, no hashtags)
- **GMP:** `Beat the summer heat with a screen upgrade. We've got an ASUS ROG Strix 43" gaming monitor at our Culpeper store for $499.99 — well under new price — backed by our 30-day warranty. Come take a look.`
- Slot: Thu 7/9 11:30 AM

### D3 — Waynesboro — Tru Hone LC Knife Sharpener (+ wheels) — $599.99 (MSRP $1,300+) (Chadd)
- **IG:** `Restaurant-grade edge, half the price. This Tru Hone LC commercial knife sharpener — with a full bag of wheels — is at Valley Pawn Waynesboro for $599.99, against an MSRP north of $1,300. Backed by our 30-day warranty. 📍 1321 W Broad St, Waynesboro  #ValleyPawn #WhatsRightIsRight #TheValleyPawn #Waynesboro #KnifeSharpening #ChefTools`
- **FB:** (IG body, no hashtags)
- **GMP:** `A commercial Tru Hone knife sharpener with a full set of wheels just came in at our Waynesboro store — $599.99, a fraction of retail, backed by our 30-day warranty. Great for a restaurant or a serious home cook.`
- Slot: Thu 7/9 1:00 PM

### D4 — Lexington — Taylor 710-CE Acoustic-Electric + Hard Case — $1,399.99 (comparable retail $3,898) (Uriah)
- **IG:** `USA-made Taylor tone for less than half. This Taylor 710-CE acoustic-electric — with its original Taylor hard case — is at Valley Pawn Lexington for $1,399.99, against a comparable-new price near $3,900. Minor cosmetic flaws, incredible sound, backed by our 30-day warranty. 📍 125 Walker St, Lexington  #ValleyPawn #WhatsRightIsRight #TheValleyPawn #Lexington #Taylor710 #AcousticGuitar`
- **FB:** (IG body, no hashtags)
- **GMP:** `A USA-made Taylor 710-CE acoustic-electric with its original hard case is at our Lexington store for $1,399.99 — well under comparable new pricing — backed by our 30-day warranty. Come play it.`
- Slot: Thu 7/9 2:30 PM

### D5 — Roanoke — ⏳ NOT SUBMITTED (deadline noon 7/6; Benjie last submitted 6/29)
Per Step 3c-bis: DM Benjie a reminder; if not in by Wed EOD, skip Roanoke's Deal slot this week. Slot held Thu 7/9 3:30 PM.

---

## Optional (not yet built, not blocking): Find statics + Reels
The default footprint also includes store-local **Find** statics and 2 **Reels**. This week already has 9 posts scheduled (Brand 4 + Community 5) plus these 4–5 Deals = 13–14 placements, which is a healthy week. Find statics + Reels can be added if desired but are not the gap. Fresh Find candidates exist in Bravo (LEX Snap-on impact wrench; HAR Bosch Bulldog hammer drill + diamond solitaire ring; WAY retro-gaming haul). CUL/ROA had no fresh items-to-price inventory this week. The 2026-07-04 Brand warranty Reel is available for reuse.

---

## Two structural blockers to clear (both need Joshua)
1. **`#vp-studio-queue` does not exist** in Slack — the strategy's approval-card staging channel. No channel-create tool is available in this session. Create it (or name an existing channel to stage into).
2. **Deals visuals + publish:** heroes-from-photos via Midjourney (Chrome + fast hours) and Publer scheduling are a live browser run, not executed in this recovery session. Either run it now, or let next Monday's now-fixed 2 AM job handle deals end-to-end. Note: the 4 deals also flow into Thursday's email via `weekly-valley-pawn-email-campaign` independently.
