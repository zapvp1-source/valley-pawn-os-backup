# Culpeper Camera Pilot — Installer Quote Sourcing

> ⚠️ **Date correction:** earlier revisions of this file and `CAMERA_SYSTEM_OPTIONS.md` were dated
> 2026-08-13. That was wrong — the date was taken from the CHANGELOG's newest entry instead of the
> actual current date. Sourcing work happened **2026-08-15**; quote outreach was sent 2026-08-15;
> this update is **2026-08-21**.

## ✅ RESPONSES RECEIVED (as of 2026-08-21)

Joshua sent 3 of the 4 drafts on 2026-08-15 (fxbgtech, Cabling Systems, M3). Two replies in:

### 1. Fredericksburg Technology — **STRONG YES, quoting now** ⭐
**George Barnick, President** · george@fxbgtech.com · (540) 403-TECH ·
1011A Princess Anne St, Fredericksburg, VA 22401 (note: differs from the 306 Frederick St address
on their site — this is the current one from his signature). CC'd david.lee@ and kenny.gilbert@.

Replied 2026-08-17. Key line: **"we're happy to hear you're familiar with UniFi Protect as that's
the primary ecosystem we install."** They're a genuine UniFi Protect shop — this was the vendor
flagged as philosophically aligned (on-prem only, no cloud subscription), and it's confirmed.

**Their four questions, and the answers sent back 2026-08-21 (draft `r6476239541350659290`):**

| Their question | Answer given | Reasoning |
|---|---|---|
| G6 (latest) or G5 Turret Ultra to save cost? | **Quote both** — all-G6, and a mix using G5TU where image quality doesn't matter | The 3 counter cameras + front door must resolve a face; showroom/floor/safe-room are coverage only. Want the delta before choosing. |
| Minimum retention — 14 days? 30? (notes HDD prices inflated by scarcity, suggests starting modest + expanding) | **30 days floor, price 60** | Pawn-specific: stolen-property claims and transaction disputes surface 30–60 days out. Footage that aged off is worthless for exactly the cases we need it for. Took his headroom advice — UNVR's 4 bays let us start with 2 drives and add later. |
| Dedicated surveillance monitor, or browser/mobile only? | **Yes — one at the counter, customer-facing** | Visible-screen deterrence. Cheap, and it's half the loss-prevention value. |
| Photos of interior (layout, ceiling type) → can quote without a site survey | **Joshua/store to send interior shots this week** | ⬅️ **ACTION ON JOSHUA** — needs Bree/Sandi/Nelson at Culpeper to take them. Told him if photos fall short we'd rather he walk it than guess. |

Also re-confirmed the architecture requirement in the reply: everything recorded local on the NVR,
event clips backed up off-site to Google Drive.

### 2. Cabling Systems, Inc. — **DECLINED**
Glenn Duckworth replied 2026-08-17: *"We do not however install ubiquity cameras perhaps your alarm
company could help you out."* Office (540) 439-0101.

Worth noting: this is the closest vendor geographically and a traditional alarm/security shop —
and they don't touch UniFi. Confirms the earlier call that **UniFi is a network product and wants
an IT/network integrator, not an alarm company.** Close this vendor out.

### 3. M3 Technology Consultants — no response yet (sent 2026-08-15, 6 days)
Worth one follow-up, but fxbgtech is ahead on merit and M3 is 50 min away vs fxbgtech's ~40.

### Not yet contacted
Double Eagle (draft `r7142110221514032537` still unsent), Windstar Technologies (phone only,
1 mi from store — still worth a call purely for proximity/response time), The Network Installers.

---


**Created:** 2026-08-13. Companion to `CAMERA_SYSTEM_OPTIONS.md`.
**Scope:** labor-only quotes for the Culpeper pilot (571 James Madison Hwy, Culpeper, VA 22701).
Valley Pawn supplies the hardware; installer runs Cat6, mounts/terminates 7 cameras, sets the NVR
in the back office. **Nothing purchased — Joshua's instruction 2026-08-13: "do not buy right yet."**

---

## UPDATE 2026-08-13 — actual UniFi dealers (sells AND installs the brand)

Joshua asked specifically who sells *and* installs UniFi Protect. Two distinctions matter:

**You never need a dealer to BUY.** Ubiquiti sells direct at `store.ui.com` at list price — there's
no dealer-only pricing tier to unlock. A "UniFi dealer" adds install expertise and support, not a
better hardware price. So "who sells it" is only relevant if we choose turnkey.

| Company | Location | Contact | Note |
|---|---|---|---|
| **M3 Technology Consultants** ⭐ | 12700 Fair Lakes Cir Ste 105, Fairfax VA 22033 | (703) 738-4489 · info@m3tc.com | **The direct hit.** Self-described UniFi Partner / UniFi Dealer / UniFi Consultant, and their site explicitly names **UniFi Protect camera installation** plus UniFi Access. Only found vendor that both sells and installs exactly our stack. ~50 min from Culpeper — distance is the open question, asked directly in the draft. |
| **The Network Installers** | National | thenetworkinstallers.com | Certified Ubiquiti installer + authorized UniFi reseller, BICSI-certified crews, deploys the full UniFi stack incl. Protect. National coverage — confirm they actually service Culpeper. |
| **Windstar Technologies** | 451 James Madison Hwy Ste 108, Culpeper VA 22701 | (540) 317-1200 | **1 mile from the store**, same road. Woman-owned, 20+ yrs, Chamber gold sponsor, Microsoft/Intel partner. ⚠️ No cameras or UniFi listed anywhere on their site — managed IT/cyber/M365/VoIP only. Unconfirmed for this work but geographically ideal; phone call, not email (no address published). |

**Official directories** (search by zip 22701):
- `installers.ui.com` — Ubiquiti's certified installer directory
- `ui.com/partner-hub` — UniFi enterprise partner program
- `ui.com/distributors` — authorized distributors (hardware only, no install)
- `ubiquiti.directory` — independent list of UniFi installers/contractors

**Draft added:** M3 Technology Consultants — `r3119230320630674780`.

---

## The five (general low-voltage/camera contractors)

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
