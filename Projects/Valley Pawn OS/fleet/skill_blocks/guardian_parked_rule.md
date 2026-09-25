# PARKED IS NOT DARK (Step 1b rule, added 2026-09-24)

Before scoring ANY `expected_outputs.json` entry in Step 1b, check whether its task is currently
**enabled** in `list_scheduled_tasks`. If `enabled` is `false`, the task was deliberately parked by
the 2026-09-16 freeze (FLEET_FREEZE_2026-09-16.md) — its channel going quiet is the expected result
of that decision, not an outage. Do NOT write a ledger row, a HUMAN_QUEUE row, or a "dark streak"
finding for a parked task. If you mention it at all, the word is "parked", never "dark", "missed"
or "silent". (On 2026-09-24 three parked tasks — valley-pawn-blog-publisher, vp-website-shop-nightly,
shop-in-store-sync — were logged as multi-day outages and pushed into HUMAN_QUEUE. They were not
outages; they had been off since the freeze.) Native launchd agents (`com.valleypawn.*` entries and
the receipt-scored agents listed in `fleet/tier1_tasks.json` under `native_agents_measured`) are not
in the registry at all — score those from receipts/files as before; absence from the registry is
not "disabled".
