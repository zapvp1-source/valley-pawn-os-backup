# Valley Pawn — Gold & Silver SEO Deployment Log
## Waves 2, 3, 4 + Hub Pages

**Deployed:** 2026-06-09 / 2026-06-10  
**Deployed by:** Claude (Cowork)  
**WordPress site:** https://thevalleypawn.com  
**Total new pages:** 18 (15 store spoke pages + 3 hub pages)

---

## CRITICAL SECURITY NOTE
The following existing gold pages were **NOT modified** at any point during this deployment:
- `/sell-gold/` (hub)
- `/sell-gold-culpeper/`
- `/sell-gold-harrisonburg/`
- `/sell-gold-lexington/`
- `/sell-gold-roanoke/`
- `/sell-gold-waynesboro/`

---

## Wave 2 — Jewelry Spoke Pages (5 pages)

| WP ID | Slug | URL |
|-------|------|-----|
| 594 | sell-jewelry-culpeper | https://thevalleypawn.com/sell-jewelry-culpeper/ |
| 595 | sell-jewelry-waynesboro | https://thevalleypawn.com/sell-jewelry-waynesboro/ |
| 596 | sell-jewelry-harrisonburg | https://thevalleypawn.com/sell-jewelry-harrisonburg/ |
| 597 | sell-jewelry-lexington | https://thevalleypawn.com/sell-jewelry-lexington/ |
| 598 | sell-jewelry-roanoke | https://thevalleypawn.com/sell-jewelry-roanoke/ |

---

## Wave 3 — Silver Spoke Pages (5 pages)

| WP ID | Slug | URL |
|-------|------|-----|
| 599 | sell-silver-culpeper | https://thevalleypawn.com/sell-silver-culpeper/ |
| 600 | sell-silver-waynesboro | https://thevalleypawn.com/sell-silver-waynesboro/ |
| 601 | sell-silver-harrisonburg | https://thevalleypawn.com/sell-silver-harrisonburg/ |
| 602 | sell-silver-lexington | https://thevalleypawn.com/sell-silver-lexington/ |
| 603 | sell-silver-roanoke | https://thevalleypawn.com/sell-silver-roanoke/ |

---

## Wave 4 — Coins Spoke Pages (5 pages)

| WP ID | Slug | URL |
|-------|------|-----|
| 604 | sell-coins-culpeper | https://thevalleypawn.com/sell-coins-culpeper/ |
| 605 | sell-coins-waynesboro | https://thevalleypawn.com/sell-coins-waynesboro/ |
| 606 | sell-coins-harrisonburg | https://thevalleypawn.com/sell-coins-harrisonburg/ |
| 607 | sell-coins-lexington | https://thevalleypawn.com/sell-coins-lexington/ |
| 608 | sell-coins-roanoke | https://thevalleypawn.com/sell-coins-roanoke/ |

---

## Hub Pages (3 pages)

| WP ID | Slug | URL |
|-------|------|-----|
| 609 | hub-jewelry | https://thevalleypawn.com/hub-jewelry/ |
| 610 | hub-silver | https://thevalleypawn.com/hub-silver/ |
| 611 | hub-coins | https://thevalleypawn.com/hub-coins/ |

---

## WordPress Navigation Menu

**Updated:** Navigation block ID 350 ("Menu")  
**Added 3 new dropdown submenus** after the existing "Sell To Us" (gold) dropdown:

- **Sell Jewelry** → `/hub-jewelry/` with 5 store links (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke)
- **Sell Silver** → `/hub-silver/` with 5 store links
- **Sell Coins** → `/hub-coins/` with 5 store links

---

## Google Search Console / Indexing

- **Google sitemap ping sent:** `https://www.google.com/ping?sitemap=https://thevalleypawn.com/sitemap_index.xml`
- **All 18 new pages confirmed present in `/page-sitemap.xml`** (Yoast auto-includes all published pages)
- **Recommended follow-up:** Visit [GSC URL Inspection](https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fthevalleypawn.com%2F) and manually request indexing for the 3 hub pages to expedite:
  - https://thevalleypawn.com/hub-jewelry/
  - https://thevalleypawn.com/hub-silver/
  - https://thevalleypawn.com/hub-coins/

---

## Deployment Method

All pages deployed via WordPress REST API (`POST /wp-json/wp/v2/pages`) using:
- Self-contained HTML/CSS/JS wrapped in `<!-- wp:html -->` blocks
- Status: `publish`, comment_status: `closed`, ping_status: `closed`, template: `""`
- Injection pipeline: raw HTML → hex chunks → osascript file-read → Chrome execute_javascript

---

## All 18 URLs — Quick Reference

```
https://thevalleypawn.com/sell-jewelry-culpeper/
https://thevalleypawn.com/sell-jewelry-waynesboro/
https://thevalleypawn.com/sell-jewelry-harrisonburg/
https://thevalleypawn.com/sell-jewelry-lexington/
https://thevalleypawn.com/sell-jewelry-roanoke/
https://thevalleypawn.com/sell-silver-culpeper/
https://thevalleypawn.com/sell-silver-waynesboro/
https://thevalleypawn.com/sell-silver-harrisonburg/
https://thevalleypawn.com/sell-silver-lexington/
https://thevalleypawn.com/sell-silver-roanoke/
https://thevalleypawn.com/sell-coins-culpeper/
https://thevalleypawn.com/sell-coins-waynesboro/
https://thevalleypawn.com/sell-coins-harrisonburg/
https://thevalleypawn.com/sell-coins-lexington/
https://thevalleypawn.com/sell-coins-roanoke/
https://thevalleypawn.com/hub-jewelry/
https://thevalleypawn.com/hub-silver/
https://thevalleypawn.com/hub-coins/
```
