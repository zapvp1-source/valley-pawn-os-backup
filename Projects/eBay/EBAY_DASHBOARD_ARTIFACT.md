# eBay Channel Pulse — published artifact

URL: https://claude.ai/code/artifact/af5d1d69-a129-4d2a-8f06-5800b33e6195

This is Joshua's weekly-readable dashboard for the eBay channel (findings, action tracker, store
table). Source file for the current version lives in this session's outputs as `ebay_dashboard.html`
— the artifact itself is the durable copy.

**To refresh it:** after `ebay-weekly-channel-audit` runs (Mondays 11:45 AM ET) and writes its
summary to `Projects/eBay/audit_weekly/YYYY-MM-DD/`, rebuild the dashboard HTML with that week's
numbers (cards, top findings, store table, action tracker deltas) and republish with the Artifact
tool passing `url: "https://claude.ai/code/artifact/af5d1d69-a129-4d2a-8f06-5800b33e6195"` so it
updates in place rather than creating a new artifact. Keep the same favicon (📦) and title
("eBay Channel Pulse").

Created 2026-08-23, baseline data from the 2026-08-22 full audit.
