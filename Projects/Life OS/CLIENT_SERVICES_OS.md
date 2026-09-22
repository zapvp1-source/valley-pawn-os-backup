# Client Digital Footprint Services — Master File (Domain 4)

**Created:** 2026-09-21
**Owner:** Joshua Davis, personally — a side service where Joshua helps other small-business
owners (often friends/family, e.g. a brother-in-law) get their business set up online: a website,
Google Business Profile, and the other directories/socials that make a local business findable.

**This is its own domain — never Full Circle Finance Inc / Valley Pawn, never a Farming Infinity
real-estate entity, never Joshua's personal life admin.** Per the Life Map hard-separation rule,
keep these client builds off `fcfpawn.com` branding, off Valley Pawn's Slack channels, and off
Valley Pawn's Google Drive. Each client gets its own contact record and lives on its own
domain/hosting — never Valley Pawn's.

---

## Known clients (as of 2026-09-21)

### 1. Solaterra LLC
- **Owner:** Chris Marney
- **Industry:** Stump grinding, forestry mulching (East Tennessee)
- **Site:** https://solaterrallc.com (Cloudflare Pages project `solaterra-llc`)
- **Contact record:** `Solaterra Site/public/Contacts/Solaterra_LLC_Contact.md`
- **Status (updated 2026-09-21):** Site live, DNS cutover to Cloudflare confirmed complete. GBP
  live but had wrong hours (7am-9pm daily instead of Mon-Sat 7-7/Sun closed) — submitted a Google
  Maps "suggest an edit" fix, pending Google's review (not instant, since Joshua doesn't have
  Chris's GBP login). Zero GBP reviews yet. Bing Places is now LIVE (was pending as of 9/4).
  **Yelp still NOT live** after 3+ weeks pending — needs Chris to check his Yelp for Business
  account for a stuck step. Facebook linked. Email DNS preservation post-cutover never explicitly
  re-verified. See the contact record for full detail and the access-gap note (no saved password
  for chrismarney@solaterrallc.com blocks direct GBP dashboard access).

### 2. First Coast Tile
- **Industry:** Custom tile installation, Jacksonville FL
- **Site:** https://firstcoasttile.com (WordPress.com, custom domain attached)
- **Legal:** Fictitious name registered with FL DOS 7/15/2026 (reg #G26000096429)
- **Status:** Live, but traffic is low (20 visitors / 28 views in August) and the domain was at
  one point listed for sale on GoDaddy's Afternic marketplace — worth checking with the owner
  whether this one is still active/wanted before doing more work on it.
- **Note:** No local project folder / contact record found yet for this one — worth building one
  to match the Solaterra pattern (see intake form below).

*(Add a new client here — name, owner, industry, site URL, contact record path, status — every
time a new one starts. Don't let this list go stale; it's the fast way for a future session to
know who's a client without re-searching email.)*

---

## The repeatable process

See the skill **`client-digital-footprint-setup`** for the full step-by-step (intake → site build →
GMB/GBP → directories → socials → DNS/hosting cutover → QA). This file is the roster and status
board; the skill is the how-to.

## Client contact record — standard location & format

Every client gets a contact record at:
`Documents/Claude/Projects/Client Sites/<Client Name>/CONTACT.md`

(Solaterra's currently lives at the older path `Solaterra Site/public/Contacts/...` — leave it
there rather than moving it, per the additive-not-destructive rule; just point to it from here.
New clients should use the `Client Sites/<Client Name>/CONTACT.md` path going forward so they're
easy to find in one place.)

Use the intake form (see the skill, or `Life OS/CLIENT_INTAKE_TEMPLATE.md`) to fill this out during
onboarding — it mirrors the Solaterra contact record: business info, contact info, hours,
services, service area, online-presence status table, and infrastructure (hosting, registrar,
DNS, email).

## How to extend this file

New client → add a row above. Client goes inactive/churns → mark status, don't delete (history is
useful — e.g. don't accidentally re-pitch someone who already declined). New recurring step in the
process → update the skill, not this file — this file stays a roster + pointer.
