# Culpeper Camera Pilot — Installer Quote Sourcing

**Created:** 2026-08-13. Companion to `CAMERA_SYSTEM_OPTIONS.md`.
**Scope:** labor-only quotes for the Culpeper pilot (571 James Madison Hwy, Culpeper, VA 22701).
Valley Pawn supplies the hardware; installer runs Cat6, mounts/terminates 7 cameras, sets the NVR
in the back office. **Nothing purchased — Joshua's instruction 2026-08-13: "do not buy right yet."**

---

## The five

| # | Company | Location / distance | Contact | DCJS | Why they're on the list |
|---|---|---|---|---|---|
| 1 | **Cabling Systems, Inc.** | Remington, VA — 13 mi from Culpeper | (540) 439-0101 · info@cablingsystemsonline.com | 11-3918 | Closest to the store. Family-owned (Glenn & Sissy Duckworth), operating since 2002, Culpeper Chamber member. ⚠️ Also sells alarm monitoring — expect an upsell attempt; the draft email heads it off explicitly. |
| 2 | **Double Eagle Voice & Data Systems** | Manassas, VA | (703) 392-1400 · info@dbl-eagle.com | — | Pure structured-cabling shop, 30+ years, meets TIA/BICSI standards. **No competing system to sell**, so the cleanest labor-only quote of the group. |
| 3 | **Fredericksburg Technology** | 306 Frederick St Ste 201, Fredericksburg, VA 22401 | (540) 403-8324 · info@fxbgtech.com | 11-30648 | Explicitly lists Culpeper County as a service area. BICSI corporate member, SWaM certified. **Their site states they deploy on-prem NVR only, no cloud subscriptions** — philosophically aligned with the architecture we chose. |
| 4 | **Premium Power Electrical** | Fredericksburg / Culpeper / Bealeton | premiumpowerelectric.com — *contact page did not load; number needs lookup* | — | Electrical contractor that also does camera installs and explicitly serves Culpeper. Cheapest-labor candidate, but least camera-specialized. |
| 5 | **Nova ITS** | Virginia / Maryland | novaits.com | — | Named in search results as primarily a **Ubiquiti installer** — the UniFi specialist of the group. Worth a call if the others are unfamiliar with UniFi Protect. |

**Also:** Ubiquiti's own certified-installer directory at **installers.ui.com** — search by zip 22701.
Worth pulling one certified name from there as a benchmark quote, but note the practical point:
this job is ordinary Cat6 and camera mounting. UniFi certification is nice-to-have, not required.
Restricting to certified shops in this market shrinks the pool and raises the price.

---

## Quote-request email (drafted in Gmail, NOT sent)

Three drafts are sitting in Joshua's Gmail, ready to send:

| Vendor | Draft ID |
|---|---|
| Cabling Systems | `r2884062485017438794` |
| Double Eagle | `r7142110221514032537` |
| Fredericksburg Technology | `r6808378288353764477` |

Premium Power and Nova ITS have no confirmed email address yet — phone or web form.

**Body used (same for all three, minor per-vendor tailoring):**

> Hi - need a quote on a camera install at our pawn shop, 571 James Madison Hwy, Culpeper.
>
> We're buying the equipment ourselves (Ubiquiti UniFi Protect - 7 cameras, NVR, PoE switch).
> Just need the labor. Cat6 runs, mount and terminate the cameras, get the recorder set in the
> back office.
>
> 7 drops. 1 exterior at the front entrance, 6 inside - entry, 3 at the counter, showroom floor,
> safe room. Strip center space, single story.
>
> If it goes well we'll do the same at our other 4 stores - Waynesboro, Harrisonburg, Lexington,
> Roanoke.
>
> Can you give me a labor number and when you could get out to look at it?

The Cabling Systems version adds a line stating we're not changing alarm systems or adding
monitoring, since they sell it. The fxbgtech version notes their on-prem-only stance matches what
we want.

---

## What to watch for in the responses

- **Labor-only should land $1,400–2,000** for 7 drops in a single-story strip-center space.
  Anything materially above that is either padding or they're quoting a turnkey system.
- **The upsell tell:** a quote that itemizes cameras/NVR after we said we're supplying hardware,
  or that arrives bundled with a monitoring contract. Not disqualifying, but re-state the scope.
- **Landlord/permit:** confirm who pulls any low-voltage permit and get the landlord's written OK
  before cable is run in the leased space — see `STORE_LEASES.md`. Culpeper is the one store with
  a populated lease record.
- **Ask each for a per-store number for the other four** so the rollout can be budgeted now.

## Next

1. Joshua sends the 3 Gmail drafts (or says go and they get sent).
2. Look up Premium Power's number and call Nova ITS — no email path confirmed for either.
3. Collect quotes, compare, pick one; hardware order stays on hold until then.
