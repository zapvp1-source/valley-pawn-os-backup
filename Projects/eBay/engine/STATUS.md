# eBay Engine — build status

Additive build alongside the existing 4 launchd agents + 9 Cowork tasks. **Nothing existing has been
changed, retired, or disabled.** Design and sequence: `../EBAY_DEPARTMENT_PLAN_2026-09-05.md` §5–6.

Runs on `/usr/bin/python3`, stdlib only, so it works from launchd with the Claude app closed.
Credentials come only from `~/.vp_secrets/`. **Never `exec()` or import an operational `~/ebay_*.py`
to "verify" it** — those run live eBay writes at module level (2026-08-22 incident); use `py_compile`.

## Modules

| File | Layer | State |
|---|---|---|
| `ebay_common.py` | shared | ✅ Trading API call/retry, per-store tokens, ledger append, engine lock |
| `ebay_snapshot.py` | 1 — snapshot | ✅ **proven on all 5 stores** — read-only; `data/YYYY-MM-DD/<Store>.json` + `data/latest/`; `item_cache.json` refreshes only new / >7-day-old / changed items |
| `ebay_rules.py` | 2 — rules | ✅ **proven** — pure, no network; `data/latest/queue.json`, AUTO vs FLAG with a reason per row |
| `ebay_apply.py` | 3 — apply | ✅ built, **dry-run proven**; live `--apply` blocked by the desktop permission gate |
| `ebay_publish.py` | 4 — publish | ✅ **proven** — deterministic Slack bodies; exit 2 = withhold, nothing printed |
| `sku_link.py` | Bravo link | ✅ dry-run proven; superseded by `ebay_apply.py --kind sku_set` (kept for the state-file backfill) |
| `probe_bravo_link.py` | probe | ✅ done → `data/probe_bravo_link_2026-09-06.json` |
| `com.valleypawn.ebay-engine-nightly.plist` | schedule | ⬜ **staged, not installed** — 5:00 AM snapshot + rules |

## First full run — 2026-09-06

```
Culpeper     266 listings | 100% detail (266 GetItem) | 236 sold/90d | COMPLETE | 248s
Roanoke       98          | 100% ( 98)                | 155          | COMPLETE | 106s
Waynesboro    36          | 100% ( 36)                |  61          | COMPLETE |  40s
Harrisonburg  32          | 100% ( 32)                |  53          | COMPLETE |  38s
Lexington     27          | 100% ( 27)                |  60          | COMPLETE |  36s
```
Channel: **459 listings, $72,597 listed · 565 sold / $86,137 in 90 days · 202 aged past 90 days
holding $20,249.** Queue: 28 AUTO, 1,550 FLAG.

## Three accuracy bugs found and fixed by verifying the engine's own output (Rule 12)

1. **`GetItem` needs `IncludeItemSpecifics`.** Without it eBay returns no ItemSpecifics node at all
   and every listing reads as zero specifics. First run reported 459 of 459 "specifics_low";
   after the fix, **252 of 459** — which matches the 8/22 audit's independently measured median of 4.
2. **"Unread return/refund messages" was counting eBay's own status mail.** 25 of the 32 unread
   messages are `Return approved` / `Refund issued` / `We sent your payout` from sender `eBay` —
   informational, nobody is waiting on us. Only **7 are real buyer messages**. Every prior audit
   reported the inflated figure (22–26). Rules now split `buyer_msg_unread` from `return_notice_unread`.
3. **"Unanswered feedback" ignored the answered ledger.** `GetFeedback` does not reliably return our
   own reply (proven 2026-09-05), so `response` being empty proves nothing. Rules now check
   `~/ebay_feedback_answered.json` first — the 8 flagged items were exactly the 8 replies posted on
   9/5, so the honest count for the last 12 months is **0 outstanding**, not 8.

Also fixed before it could ever post: the weekly formatter was going to report fixes from the
*queue* (planned) rather than the *ledger* (actually applied) — a Rule 18 violation. It now reads
only `ledger.jsonl`, so it can never announce a change that did not happen.

## Real findings the first run surfaced

- **Roanoke's listing template still creates 14-day returns.** 8 listings are on `Days_14`; **6 of
  them were listed 2026-09-05**. The 8/22 remediation fixed the existing listings but never changed
  the source, so the weekly audit has been re-patching new ones ever since. The durable fix is
  Roanoke's Seller Hub **business policy default**, not another sweep.
- **3 Best Offers expire within 48 hours, unanswered:** Roanoke $40 from `reivys` (~20 h),
  Harrisonburg $80 from `hetultank` (~9.5 h), Lexington $10 from `mjo0727` (~20 h).
- **Bravo link:** SKU empty on 100% of listings; the code survives in the title on 20, and is
  recoverable from `~/ebay_title_state.json` for 434 more.

## Open

1. **`ebay_apply.py --apply`** — 28 changes ready (8 Roanoke returns → 30 days, 20 SKU links),
   dry-run verified, fully reversible via `--revert <run_id>`. **Blocked by the desktop permission
   classifier**, which refuses any eBay write from an autonomous run. Needs Joshua's approval once.
2. **`sku_link.py --apply`** — the wider state-file backfill (175 listings). Same block.
3. **Install the nightly plist** — `cp com.valleypawn.ebay-engine-nightly.plist ~/Library/LaunchAgents/`
   then `launchctl load ...`. Read-only; safe to install today.
4. **OAuth refresh tokens for the 4 remaining stores** — until then: no seller standards, no
   Promoted Listings management, no impressions/CTR/conversion.
5. **Shadow week** — run rules alongside the existing Sunday/Monday tasks and diff before retiring
   anything.
