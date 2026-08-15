# Valley Pawn — Physical Security Hardening Plan (Alarm + Camera)

**Created:** 2026-08-13 — in response to Joshua's ask for a hardened-security recommendation
covering both central-station alarm monitoring and video, current state = a local alarm group for
monitoring + Google Nest/Google Home cameras (WiFi) for video.

**Context loaded before this plan:** `enterprise-map`, `valley-pawn-context`, `BUSINESS_OS.md`,
`CHANGELOG.md`, `Open Items Register`, Slack (no security-related activity in last 7 days), Google
Drive (no alarm-company contract or camera-vendor doc found — only the Pandora Cloud Cover music
account, which is unrelated). This is a genuinely new area — no prior Claude work exists on it, so
nothing here duplicates or conflicts with anything already built.

**Correction while researching:** `valley-pawn-context`'s "Software & Tools" table lists
"CloudCover — Security / surveillance system." That's stale/wrong — CloudCover is **Pandora Cloud
Cover**, the in-store background-music service (`daily-cloudcover-check` checks music streaming
status, not video). The actual existing video system is **Google Home / Nest cameras**, currently
used only for `daily-dress-code-check`. Flagging for a future session to fix that skill line.

---

## Expert board

**Panel:** loss-prevention/physical-security consultant, low-voltage systems integrator, insurance
& compliance advisor.

### Cameras: WiFi (Nest/Google Home) vs. wired PoE + local NVR

- **Keep Nest/Google Home (status quo):** already installed, already wired into the dress-code
  automation. Against: WiFi cameras contend with store WiFi/POS/guest traffic and drop frames
  under load (matches what Joshua is already seeing); cloud retention is typically 30–60 days,
  often too short for a police hold or insurance claim on a pawn transaction under investigation;
  WiFi is trivially defeated — kill the router or jam the band and the cameras go dark. For a
  business holding cash, gold, and firearms, that's a real gap, not a nice-to-have fix.
- **Migrate to wired PoE cameras + local NVR, mirrored to cloud (hybrid):** cameras keep recording
  locally even if internet drops; retention is cheap and long (90+ days on a local NVR); cutting
  the wire doesn't work the way killing WiFi does since the NVR should live in a locked back-office
  or safe room, separate from the cameras themselves; cloud mirror still gives Joshua remote
  viewing from his phone and an off-site copy if a store is physically compromised. Cost is the
  real tradeoff — hardware, install, and possibly new low-voltage runs (coordinate with each
  store's landlord per `STORE_LEASES.md` before drilling/running cable in a leased space).

**Decision: migrate all 5 stores to wired PoE + local NVR with cloud mirroring**, and stop relying
on Nest/Google Home as the security system of record. (Google Home can stay for non-security use —
speakers, etc. — if Joshua wants it.)

**Camera coverage per store (minimum):** front entrance, each teller/counter station, the
vault/safe room, exterior (parking lot + back door/loading area), and — **Roanoke specifically** —
a dedicated angle on the firearms case/vault, since that's the FFL location. Not a strict ATF
mandate, but standard underwriting/insurance expectation for a store carrying firearms.

> **SUPERSEDED 2026-08-13 — read `CAMERA_SYSTEM_OPTIONS.md` instead for the camera decision.**
> The cloud-platform shortlist below (Eagle Eye / Rhombus / Verkada) was the wrong default for a
> 5-store operation that already stated a preference for local recording. Those platforms charge
> $18K–42K/yr in per-camera licensing to solve centralized multi-site cloud management — a problem
> Valley Pawn doesn't have at this size. The revised recommendation is a locally-recorded PoE
> system (UniFi Protect preferred) at $0/month, with off-site clip backup covering the one genuine
> advantage cloud had (footage survives if the NVR is stolen or the store burns). Table kept below
> for reference only.

**Platform shortlist — SUPERSEDED, reference only:**

| Vendor | Model | Fit |
|---|---|---|
| **Eagle Eye Networks** | Cloud-managed VMS, supports third-party PoE cameras | No camera lock-in; strong multi-site/franchise retail track record — good fit for one dashboard across 5 stores |
| **Rhombus Systems** | Cloud-native, cameras + NVR bundled | Cheaper entry point than Verkada, simple multi-site management, solid AI motion/person detection |
| **Verkada** | Premium, proprietary hardware | $500–3,000/camera + mandatory $199–1,799/camera/yr license — likely overkill for 5 small stores; only worth it if budget is open and Joshua wants best-in-class support |
| Local integrator, business-grade PoE (Axis, Hanwha, Uniview) + on-prem NVR, no cloud subscription | Lowest recurring cost, fully local | Good budget option if Joshua doesn't want an ongoing cloud bill |

**Avoid Hikvision and Dahua specifically** even though they're the cheapest PoE cameras on the
market — both are on the federal NDAA Section 889 prohibited-equipment list and are increasingly
flagged by insurers/underwriters; not worth the exposure for a marginal cost saving.

**Rough budget (for planning only, confirm with real quotes):** $3,000–6,000 hardware+install per
store (8–12 cameras) + $30–70/camera/month cloud licensing if going the Eagle Eye/Rhombus route —
roughly $15,000–30,000 upfront across all 5 stores, $1,500–3,500/month recurring. The local-NVR
no-subscription route cuts the recurring number to near zero at the cost of no cloud
redundancy/remote app unless self-hosted.

### Alarm / central station monitoring

Joshua already uses a local group for central-station monitoring — the recommendation here is to
**verify and harden what exists**, not necessarily replace it.

**Verification checklist to run against the current provider:**
1. **DCJS licensed** — Virginia legally requires any business providing central-station monitoring
   to Virginia sites to hold a Private Security Business License through DCJS, with registered
   dispatchers. Confirm the local group has this (baseline legal requirement, not a differentiator).
2. **UL 827 listed** (the real differentiator) — UL-listed central stations must have redundant
   power, redundant communications, a hardened facility, and are required to handle fire signals
   within 90 seconds. A non-UL station can legally operate out of one location with no redundancy.
   Ask the local group directly for their UL certificate; if they don't have one, that's the
   single biggest gap to close.
3. **Dual-path signaling** — cellular as primary or backup, not a plain phone line alone (a cut
   phone line is a 30-second bypass with a pair of wire cutters).
4. **Door contacts + interior motion + glass-break** on every entry point, with the vault/safe room
   as its own zone.
5. **Duress/panic buttons** at every teller station, wired to a silent alarm — given cash and
   firearms on-site, this is standard for pawn/jewelry retail and may not exist yet.
6. **Unique passcode per employee** (not one shared store code) so every arm/disarm is individually
   attributable — this also lets a future automation cross-check alarm open/close times against
   Bravo's own open/close logs for anomalies.
7. **Annual UL certificate + false-alarm report** on file for the insurance carrier.

**If the current provider passes 1–2 and fails 2 (no UL cert) or 3–6:** get two competing quotes
from a UL-listed regional/national provider (Rapid Response Monitoring, COPS Monitoring, Vector
Security, or a licensed VA dealer wholesaling Alarm.com) as a fallback — keeping the local company
is fine and often better for response-time/relationship reasons if they can actually meet the bar;
the goal is confirming they're hardened, not automatically switching.

---

## What this touches / future automation angle

Once cameras are on a real VMS with an API (Eagle Eye/Rhombus both have one) and the alarm
system's events are queryable, `daily-dress-code-check` and any future security-adjacent
automation get materially more reliable — right now dress-code checking scrapes Google Home,
which is the same fragile WiFi path this plan replaces. Worth revisiting once the camera migration
is done. Not in scope to build until the hardware decision is made.

## For Joshua

Recommendation and reasoning above — this is the additive, checked-against-current-state answer.
**The one thing that's genuinely your call:** which camera platform and which install budget to
commit to, and whether to get a UL certificate from the current alarm company or shop it against
UL-listed alternatives. I can request quotes from Eagle Eye Networks, Rhombus, and 1–2 local
integrators (and draft the alarm-provider ask for a UL cert) the moment you say go — just flag
which direction (cloud-hybrid vs. local-only NVR, and rough budget ceiling) you want me to shop
toward, or tell me to use my judgment and I'll pick the cloud-hybrid shortlist above by default.

---
*Logged in `Life OS/OPEN_ITEMS_REGISTER.md` per Rule 14.*
