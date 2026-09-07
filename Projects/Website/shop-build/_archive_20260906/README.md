# Archived 2026-09-06 — superseded by the native runner

Everything in this folder was scratch from the old `vp-website-shop-nightly` method, where each run
copied the previous run's fetch script to a new dated filename and hand-edited a session-specific
`BASE` path. That method is retired: `Website/analytics/bin/shop_refresh.py` now owns fetch → filter →
build → publish → verify → post, deterministically, with a same-slot guard and a Rule-18 gate.

Kept live in `shop-build/`:
- `generate_shop_block.py`  — the block generator (called by shop_refresh.py, unchanged, do not edit)
- `.wp_app_credentials`     — WP Application Password (`vp-shop-nightly`)
- `items.json`, `shop-block.html`, `shop-block-wrapped.html` — the current run's working files
- `METHOD_NOTES.md`, `RUN_LOG_2026-08-21_FAILURE.md` — the history and the WooCommerce-hijack fix

Archived here: 20+ one-off `fetch_*.py` / `publish_nightly_*.py` copies, their logs, the abandoned
compact generator, stale wrapped blocks, cookie jars, old items.json backups, and ~38 MB of raw eBay
HTML dumps (`raw/`, `raw2/`, `raw_now/`, `chunks*`, `b64chunks`).

Safe to delete entirely after 2026-12-01. Nothing references it.
