# BUSINESS_OS.md — Registration Delta (2026-06-19)

This file is an **additive patch** to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/BUSINESS_OS.md`. It registers every new domain, account, platform, script, file, and skill that landed during the 2026-06-19 social media build, per the enterprise-map rule (Joshua's directive).

**How to apply:** copy each section below into the corresponding section of BUSINESS_OS.md. All additions are additive — no existing entries are removed or modified (Rule #4).

---

## 1. New external domains / URLs to register

| Domain / URL | Purpose | Status | Owner | Notes |
|---|---|---|---|---|
| `follow.thevalleypawn.com` | Branded subdomain for Publer Linkie page (in-store QR card destination) | Planned (DNS task #48) | Valley Pawn | CNAME → Publer Linkie host (look up in Publer Linkie settings once page is built) |
| `x.com/valleypawnva` | Brand X (Twitter) account — display name "Joshua Davis," handle @valleypawnva, intentional conservative-demographic strategy | Live (logo + bio + first post live 2026-06-19) | Joshua | Posts as Joshua, not as a brand handle |
| `instagram.com/valley_pawn` | Brand Instagram account | Live (logo swapped 2026-06-19 from V-mark to full landscape) | Joshua | |
| `tiktok.com/@thevalleypawn` | Brand TikTok account (Phase 2 reel pipeline target) | Live (logo set 2026-06-19) | Joshua | Live-selling planned per giveaway-strategy memory |

## 2. New software platforms registered

| Platform | Role | Tier / Cost | Auth | Replaces |
|---|---|---|---|---|
| **Publer** | Social media publishing layer (all 9 accounts) + analytics + Linkie (Link-in-Bio) | Business tier, $50/mo (all pages included) | Bearer-API token in `publer_config.json` | Direct Meta Graph API path (now LEGACY); `facebook-post` skill (now LEGACY); 8 disabled scheduled tasks (now LEGACY — see vp-social-publisher SKILL) |
| **Publer Linkie** | One-page "follow Valley Pawn everywhere" hub at follow.thevalleypawn.com | Included in Publer Business | Same as Publer | New capability — no prior tool |

## 3. New connected social accounts (Publer workspace `6a358d48fe216c70f7e65d4e`)

All 9 accounts mapped in `publer_accounts.json`:

- **Brand FB** (`6a3596d6fe216c70f7e6726c`) — Valley Pawn brand Page
- **BrandIG** (`6a35979ebbd130d6e889c0bb`) — @valley_pawn
- **BrandTikTok** (`6a359ca0bbd130d6e889cb78`) — @thevalleypawn ⬅ NEW 2026-06-19
- **BrandTwitter** (`6a359c454dd914c27c77f9c5`) — @valleypawnva ⬅ NEW 2026-06-19
- **Culpeper** (`6a3596d3fe216c70f7e67261`)
- **Harrisonburg** (`6a3596d807e1b3bf83f1c379`)
- **Lexington** (`6a3596d4fe216c70f7e67266`)
- **Roanoke** (`6a3596d2bbd130d6e889bf58`)
- **Waynesboro** (`6a3596d789dea67771497918`)

## 4. New scripts / Python modules (in `/Refine Social Media/`)

| File | Role | Depends on |
|---|---|---|
| `publer_client.py` | Single source of truth for ALL Publer API calls. Bulk/networks payload structure (per Publer API docs). Includes `schedule_post`, `job_status`, `wait_for_job`, `post_insights` | `publer_config.json`, `publer_accounts.json`, `requests` |
| `vp_social_publisher.py` | Manifest executor — reads approved-manifest JSON, routes items to correct accounts via routing tier, calls Publer API hands-off | `publer_client.py` |
| `friday_close_engagement_publer.py` | Publer-routed engagement analytics for Friday close (replaces direct Meta Graph API path) | `publer_client.py` |
| `friday_close_engagement.py` | LEGACY — direct Meta Graph API version. Preserved as fallback. Not actively called. | — |

## 5. New skills / planned skill files

| Skill | Location | Status |
|---|---|---|
| `vp-social-publisher` | `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/vp-social-publisher_SKILL.md` | Drafted 2026-06-19. **Joshua: add this to Settings → Capabilities so it becomes a real skill.** Currently lives as a stub file. |
| `vp-brand-studio` | Existing | Needs additive update with X + TikTok voice notes (task #36) — Joshua to edit in Settings |
| `expert-review-board` | Existing | Needs PERMANENT seat: "Pawn shop executive/operator" on every Valley Pawn board (rule saved to memory, but skill file needs Joshua to add in Settings) |
| `valley-pawn-context` | Existing | Should reference the new X / IG / TikTok handles + Publer as publishing layer + $100/mo giveaway program |

## 6. New folder structure (`/Refine Social Media/`)

```
Refine Social Media/
├── brand_assets/                              # 2026-06-19 — for X/IG/TikTok profile setup
│   ├── valley_pawn_profile_1080.png           # 1080×1080 square logo (X/IG/TT profile)
│   └── valley_pawn_x_header_1500x500.png      # X header banner
├── Meta Business Verification/                # 2026-05-26 — for Meta business verification submission
├── publer_config.json                          # API auth + workspace_id
├── publer_accounts.json                        # store_key → Publer ID mapping (9 accounts)
├── publer_client.py                            # Publer API client (bulk/networks payload)
├── vp_social_publisher.py                      # Manifest executor
├── vp-social-publisher_SKILL.md                # Stub skill — install via Settings
├── friday_close_engagement.py                  # LEGACY direct-Meta
├── friday_close_engagement_publer.py           # Publer-routed engagement analytics
├── BUSINESS_OS_REGISTRATION_DELTA.md           # THIS FILE — additive patch for BUSINESS_OS.md
├── REFINE_SOCIAL_MEDIA_INDEX.md                # Folder index for future Claude sessions
└── (various playbook + report markdown files)
```

## 7. New scheduled tasks (planned, additive)

| Task | Cadence | Purpose | Status |
|---|---|---|---|
| `vp-content-batch-weekly` | Sun 8 PM | Generate weekly content + auto-publish via vp_social_publisher.py + Publer | Existing — needs verification it fires hands-off (task #45) |
| `vp-giveaway-monthly-draw` | Last day of each month | Draw random row from Brevo entries list, email winner, generate announcement post | NEW — to build (task #47) |
| `reel-comment-alert` | Trigger: 30 min after Meta post publish | DM Joshua + Lainie with comment digest + draft replies | Existing — keep using |

## 8. Strategic rules added (2026-06-19)

- **Rule 11** (existing): Social media publishing routes through Publer.
- **Rule 12** (NEW): Every expert-review-board panel for Valley Pawn must seat a pawn shop executive/operator as a permanent member.
- **Rule 13** (NEW): Social media adoption incentive is a $100/month giveaway with email-capture entry, not per-transaction discount. VA-compliant Official Rules required.
- **Rule 14** (NEW): All NEW domains, accounts, platforms, scripts, and folders must be registered additively in BUSINESS_OS.md the same session they're created.

## 9. Change log entry

```
2026-06-19 — Social media stack expansion + adoption infrastructure
  - Connected X @valleypawnva, TikTok @thevalleypawn to Publer workspace
  - Replaced direct Meta Graph API path with Publer (vp_social_publisher.py + publer_client.py)
  - Fixed Publer API payload (bulk/networks structure per Publer docs)
  - Set brand identity (logo + header + bio) on X, IG, TikTok
  - First X test post published successfully via Publer UI
  - Pawn shop operator added as permanent board seat (rule #12)
  - $100/month giveaway model adopted (rule #13)
  - Planned: follow.thevalleypawn.com subdomain → Publer Linkie page
  - Planned: in-store QR counter cards (5 stores, Amazon premade ~$50)
  - Deprecated 6 Meta-direct-API tasks (now obsolete via Publer)
```
