# Website Analytics — the data layer and its formatters

Built 2026-09-06 from `../WEBSITE_ANALYTICS_AUTOMATION_PLAN_2026-09-05.md`. Everything here is
native, stdlib-only Python. **Claude launches and verifies; it does not compute or render.**

```
bin/google_auth.py            access tokens from the cached OAuth refresh token (stdlib refresh)
bin/google_grant.py           ONE-TIME re-consent adding analytics + search-console read scopes
bin/ga4_pull.py               GA4 → JSON (KPIs, channels, pages, LEAD EVENTS BY STORE)
bin/gsc_pull.py               Search Console → JSON (clicks, impressions, position, tracked ranks)
bin/wp_client.py              WordPress REST via the existing App Password (CDN-lag aware)
bin/shop_refresh.py           /shop/ end to end: fetch → gate → build → publish → verify → post
bin/format_weekly_website.py  the ONLY renderer of the Monday #website post
data/{ga4,gsc,shop}/          single source of truth, one file per run
logs/                         one log per script per day
```

## The two rules
1. **Nothing renders a Slack post except a formatter.** A model re-rendering a table each week is
   what produced the illegible, mis-mapped 8/31 aged-inventory post. Post stdout verbatim.
2. **Exit 2 means post nothing.** Never caveat a partial number into a channel (Rule 18); never put
   the technical reason in Slack (Rule 16) — it goes in `logs/`, and Joshua gets one plain DM line.

## Health check
```
cd bin
python3 shop_refresh.py --dry-run      # fetch + build + gate, no publish, no post
python3 ga4_pull.py --check            # exits 1 until Phase 0 (GOOGLE_API_SETUP.md)
python3 gsc_pull.py --check
python3 format_weekly_website.py ../data/ga4/week_latest.json
```

## What is still pending
- **Phase 0** — 3 minutes of Joshua's time: `GOOGLE_API_SETUP.md`. Until then GA4 comes from the
  Chrome scrape and Search Console is dark.
- **launchd** — `../../Valley Pawn OS/fleet/com.valleypawn.shop-refresh.plist` staged, not installed.
- **Phase 3/4** — conversion instrumentation, and the carried items (55 zero-H1 pages, page weight,
  the 26-page duplicate cluster, the max-loan-amount contradiction).
