# Valley Pawn — 5 Locally-Recorded Camera Systems, Priced

**Created:** 2026-08-13. Companion to `SECURITY_HARDENING_PLAN.md`.
**Ask:** five local (on-premise NVR, wired PoE) camera systems, priced, that beat the current
Nest/Google Home WiFi cameras at the stores.

**Why any of these beats what's in the stores now:** all five record to a box sitting in the store,
over Ethernet cable that also powers the camera. No WiFi contention with the POS or guest network,
no dropped frames under load, no 30–60 day cloud retention ceiling, and footage keeps recording
even if the internet is completely down. Killing WiFi no longer blinds the store.

**Sizing — REVISED 2026-08-13 per Joshua:** all 5 stores are in strip centers, so only **one
exterior camera** is needed per store (front entrance), not the 2–3 a standalone building would
take. Revised count is **7 cameras per store**, 8 at Roanoke:

| Position | Qty | Camera |
|---|---|---|
| Exterior — front entrance | 1 | G5 Bullet |
| Interior entry / door watch | 1 | G5 Dome |
| Counter / teller stations | 3 | G5 Dome |
| Showroom floor | 1 | G5 Dome |
| Vault / safe room | 1 | G5 Dome |
| **Roanoke only** — firearms case | +1 | G5 Pro |

Older figures in this doc assumed 10 cameras/store; the 7-camera count below is the current one.
Confirm against an actual walkthrough before ordering — counter count may vary by store.

---

## The five systems

### 1. Ubiquiti UniFi Protect — *best overall fit for 5 stores*

| | |
|---|---|
| Recorder | UNVR (4-bay) **$399** · UNVR Pro (7-bay, 10GbE) **$799** |
| Cameras | G5 Bullet / G5 Dome **$199–230 each** |
| Licensing | **$0 forever** — no per-camera fee, AI/analytics run locally |
| **Per store (10 cams + UNVR + 4TB)** | **≈ $2,600–2,900** hardware |
| **All 5 stores** | **≈ $13,000–14,500** hardware |

Why it wins for Valley Pawn specifically: one cloud dashboard shows all 5 stores from Joshua's
phone without any subscription, because the remote access is free and the recording still happens
locally in each store. That's the exact hybrid the security plan called for, at roughly a tenth of
the recurring cost of Eagle Eye or Rhombus. It also has a real API, which matters for eventually
rebuilding `daily-dress-code-check` off the fragile Google Home path.
Buy direct: [store.ui.com](https://store.ui.com/us/en/category/all-cameras-nvrs)

### 2. Hanwha Vision (Wisenet) — *commercial-grade, NDAA-compliant*

| | |
|---|---|
| 8ch kit | ARN-810S NVR + 6× 4MP dome + 2TB — **$1,699.99** |
| 16ch kit | ARN-1610S NVR + 12× 4MP dome + 4TB — **$2,999.00** |
| **Per store (16ch kit)** | **$2,999** |
| **All 5 stores** | **≈ $15,000** |

Korean-made, NDAA-compliant, genuine commercial line — this is what a professional integrator
installs in a jewelry store. Better low-light and warranty than the consumer brands, and it will
satisfy any insurance underwriter question about equipment grade. Costs about the same as UniFi
but with a more dated management interface and no free remote-viewing story.
Dealers: [cctvsupply.us](https://cctvsupply.us/en-us/collections/hanwha) ·
[nellyssecurity.com](https://nellyssecurity.com/collections/hanwha)

### 3. Speco Technologies — *NDAA-compliant, most cameras per dollar*

| | |
|---|---|
| Kit | N16NRE 16ch 4K NVR + **12×** O4VT2 4MP PoE dome + 4TB — **$2,799.00** |
| **Per store** | **$2,799** |
| **All 5 stores** | **≈ $14,000** |

Twelve cameras in the box instead of eight — the best coverage-per-dollar of the NDAA-compliant
options, with facial recognition and smart analytics built into the recorder. US company, widely
carried, strong dealer support. Alternative in the same tier: Digital Watchdog VMAX IP Plus 16ch
NVR (~$1,101 recorder-only, 5-year warranty) if you'd rather pick cameras separately.
[cctvsupply.us Speco kit](https://cctvsupply.us/products/speco-technologies-16-channel-ip-camera-system-ndaa-compliant-n16nre-16-ch-nvr-with-12-pcs-o4vt2-4mp-ip-turret-cameras-4tb-hard-drive) ·
[Amazon listing](https://www.amazon.com/Speco-Technologies-Channel-Camera-System-Weatherproof/dp/B0CTWGC8NX)

### 4. Lorex — *cheapest credible commercial-ish option*

| | |
|---|---|
| NVR only | N4K3 16ch 4K, 4TB, dual SATA (60-day retention) — **$649** |
| Bundle | N4K2-86CK 16ch NVR + 8 cams + 4TB — **$899** |
| Full 16-cam 4K kit | **$2,200–2,700** |
| **Per store (~10 cams)** | **≈ $1,400–1,800** |
| **All 5 stores** | **≈ $7,000–9,000** |

Real 4K PoE with local recording and no subscription, at roughly half the price of the commercial
brands. Consumer-line hardware and support, so expect a shorter service life — but it is a
categorical improvement over WiFi Nest cameras at every store for well under $10K.
[lorex.com](https://www.lorex.com)

### 5. Reolink — *lowest cost per store, budget floor*

| | |
|---|---|
| Kit | RLK16-800D8 — 16ch NVR + 8× 4K dome + 4TB — **$1,099.99** (street ~$986) |
| **Per store** | **≈ $1,100–1,400** (add 2 cameras ≈ $90–120 ea) |
| **All 5 stores** | **≈ $5,500–7,000** |

The absolute cheapest way to get all 5 stores off WiFi and onto wired local recording. No monthly
fees at all. **Two caveats worth knowing:** the RLK16-800D8 is showing as discontinued at some
retailers so check stock before committing, and Reolink is a Chinese-owned brand — it is *not* on
the federal NDAA Section 889 prohibited list the way Hikvision and Dahua are, but if an insurer or
future FFL audit ever asks about equipment provenance, Hanwha or Speco is the cleaner answer.
[reolink.com](https://reolink.com/us/product/rlk16-800d8/)

---

## Costs the hardware price doesn't include

- **Installation / cable runs:** $150–300 per camera installed for a low-voltage contractor in
  Virginia — call it **$1,500–3,000 per store**, or **$7,500–15,000 across all 5**. This is the
  real driver of total cost, not the hardware. It also needs landlord sign-off before drilling or
  running cable in a leased space — check `STORE_LEASES.md` per store first.
- **Extra storage:** budget $100–200/store if you want 90+ day retention instead of 30.
- **A locked location for the NVR** — back office or safe room, not behind the counter. A recorder
  a thief can grab defeats the whole point.

## Realistic all-in, all 5 stores

| Route | Hardware | + Install | **All-in** | Recurring |
|---|---|---|---|---|
| Reolink (budget floor) | ~$6,000 | ~$10,000 | **~$16,000** | $0 |
| Lorex | ~$8,000 | ~$10,000 | **~$18,000** | $0 |
| **UniFi Protect (recommended)** | ~$14,000 | ~$11,000 | **~$25,000** | **$0** |
| Speco (NDAA) | ~$14,000 | ~$11,000 | **~$25,000** | $0 |
| Hanwha (NDAA, commercial) | ~$15,000 | ~$12,000 | **~$27,000** | $0 |
| *(for contrast)* Eagle Eye / Rhombus cloud | ~$20,000 | ~$11,000 | ~$31,000 | **$1,500–3,500/mo** |

Every one of the five local options is **$0/month recurring**, versus $18,000–42,000 a year for
the cloud-subscription platforms. Over three years the cloud route costs more than the entire
local buildout twice over.

## Board recommendation

**UniFi Protect.** It's the only option that gives multi-store remote viewing on Joshua's phone
with zero recurring cost, keeps every frame recorded locally in each store, and exposes an API for
future automation. Speco is the pick instead if NDAA compliance on paper matters more than the
management experience. Reolink is the pick if the goal is simply "get off WiFi everywhere this
quarter for under $16K all-in" — it is still a large upgrade over what's installed today.

**Sequencing:** pilot one store first, run it 30 days, then roll the other four. Do not buy for
5 stores before proving 1. **Pilot store = CULPEPER** (Joshua's call, 2026-08-13 — supersedes the
earlier Roanoke suggestion). Culpeper is also the only store open Wednesday, so it gets an extra
day per week of real-world runtime during the pilot.

### CULPEPER PILOT — build sheet

571 James Madison Highway, Culpeper, VA 22701. No firearms case here (Roanoke is the FFL store),
so no G5 Pro on this build.

| Item | Qty | Each | Line | Link |
|---|---|---|---|---|
| Network Video Recorder (UNVR), 4-bay | 1 | $299 | $299 | store.ui.com/us/en/products/unvr |
| Camera G5 Bullet — front exterior | 1 | ~$230 | ~$230 | store.ui.com/us/en/products/uvc-g5-bullet |
| Camera G5 Dome — entry, 3× counter, floor, vault | 6 | ~$230 | ~$1,380 | store.ui.com/us/en/products/uvc-g5-dome |
| Switch Pro 8 PoE (120W) — or any 8-port PoE+ ≥120W | 1 | $349 | $349 | store.ui.com/us/en/products/usw-pro-8-poe |
| 8TB surveillance HDD (SkyHawk / WD Purple) | 2 | ~$175 | ~$350 | Amazon Business |
| | | **Hardware** | **≈ $2,610** | |
| Install labor, 7 drops | | | ~$1,400–1,800 | local low-voltage contractor |
| | | **All-in** | **≈ $4,000–4,400** | |

Recurring: **$0.** Google Drive event archiving uses the existing Valley Pawn Workspace.

**Pilot success criteria (evaluate at 30 days):**
1. Live view works reliably from Joshua's phone, off-site, without a subscription.
2. Zero measurable impact on Culpeper's POS/network performance (the Nest problem).
3. Smart Events reliably landing in the Valley Pawn Drive folder.
4. Retention actually hitting 30+ days on 2× 8TB with 7 cameras at 4K.
5. Faces readable at the counter and the front door in real store lighting — the whole point.

If all five hold, replicate to Waynesboro, Harrisonburg, Lexington, Roanoke (Roanoke adds the
G5 Pro on the firearms case). If retention or image quality disappoints, adjust the spec before
buying 4 more sets — that's what the pilot is for.

---

## Build-it-ourselves: local NVR + cloud backup (replaces Eagle Eye entirely)

Joshua's question 2026-08-13: *"couldn't we create something similar with a local camera setup and
get it to back up to the cloud?"* — **Yes, and UniFi Protect does most of it natively for free.**
This is the architecture that gets everything Eagle Eye sells, minus the $100K.

### What Eagle Eye actually sells you, and how each piece gets covered locally

| Eagle Eye feature | Local equivalent | Cost |
|---|---|---|
| All sites on one dashboard, viewable anywhere | UniFi Protect's free cloud portal — all 5 NVRs under one account | **$0/mo** |
| Wired PoE cameras (no WiFi contention) | Same — every option here is PoE | included |
| Footage survives if NVR is stolen / store burns | Off-site archiving, three ways (below) | **$0–30/mo** |
| AI person/vehicle/motion detection | Runs locally on the UNVR, no cloud round-trip | **$0** |
| Mobile alerts | Built in | **$0** |
| Long retention | Bigger local drives — a 12TB drive is ~$180 once | one-time |

### Off-site backup — three layers, cheapest first

**Layer 1 — Google Drive archiving (free, already paid for).** UniFi Protect has native off-site
archiving to Google Drive, OneDrive, Dropbox, or a NAS with **no subscription**. Smart Events
(person/vehicle detections) upload instantly; scheduled continuous upload is on Ubiquiti's roadmap.
Valley Pawn already runs Google Workspace on `jdavis@fcfpawn.com` with the Valley Pawn Shared Drive
— **the backup target already exists and is already paid for.** Create a `Security Footage` folder
per store and point each NVR at it. Every detection event at every store is off-site within
seconds, at zero added cost.

**Layer 2 — cross-store replication (free, and Valley Pawn is unusually well-suited to it).**
Five stores means five buildings on five different power grids and internet circuits. Each store's
NVR rsyncs its footage to a peer store's drive overnight (Culpeper→Waynesboro→Harrisonburg→
Lexington→Roanoke→Culpeper). A thief who takes the Roanoke recorder has taken nothing — the
footage is already sitting in Lexington. Geographic redundancy for the cost of a hard drive.
**$0/month recurring.**

**Layer 3 — full continuous cloud archive (only if wanted).** For belt-and-suspenders, sync
everything to object storage: Backblaze B2 at **$6.95/TB/month** or Wasabi at **$7.99/TB/month**
(Wasabi has a 90-day minimum retention, which actually suits surveillance archives, and zero
egress fees).
- Smart-event clips only, all 5 stores, 90 days ≈ 2 TB ≈ **$14–16/month**
- Everything, continuous, all 5 stores, 90 days ≈ 40 TB ≈ **$280–320/month**

Layer 3 at the event-clip tier is the sweet spot: ~$15/month for a fully independent third copy of
everything that matters.

### The number

| | Eagle Eye, 5 stores | Local + cloud backup, 5 stores |
|---|---|---|
| Upfront (hardware + install) | $25,000–40,000 | **~$25,000** |
| Recurring | **$1,600–2,400/mo** | **$0–15/mo** |
| **3-year total** | **$85,000–125,000** | **~$25,500** |

Same wired cameras. Same one-dashboard remote viewing. Same off-site copy. Better local retention
(the footage never leaves the store unless you ask for it, so no upstream bandwidth cost at all).
**Roughly $75,000–100,000 cheaper over three years.**

### What we give up honestly

- **Support.** Eagle Eye/Brivo has a support line and a certified integrator on the hook. UniFi is
  self-supported plus community forums. Mitigated by using a local integrator for install and
  keeping a spare UNVR on the shelf ($399) so a failed recorder is a same-day swap.
- **Continuous cloud upload isn't native yet** in UniFi Protect — Smart Events upload instantly,
  full continuous upload is "coming soon" per Ubiquiti. Layers 2 and 3 close this gap today.
- **Uptime monitoring.** Eagle Eye watches your cameras for you. We'd build this — a scheduled task
  polling each NVR's API and posting to Slack when a camera goes offline, same pattern as the
  existing `controlio-offline-agent-check` and `daily-cloudcover-check`. That's a few hours of
  work, not a $100K/3yr line item.

### Board decision

**Build it.** UniFi Protect + Google Drive event archiving (Layer 1) + cross-store replication
(Layer 2), with Backblaze B2 event-clip archive (Layer 3, ~$15/mo) as cheap insurance. Pilot at
Roanoke, prove for 30 days, then roll to the other four. Add the camera-offline Slack watchdog
once the pilot is stable.

---

*Prices sourced 2026-08-13 from manufacturer and authorized-dealer listings; hardware pricing moves
and install labor is quote-dependent — treat these as planning numbers, not quotes.*
