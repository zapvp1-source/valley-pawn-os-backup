# Daily Funds Verification — 2026-05-27

**Status: COULD NOT VERIFY — Bravo Data Extraction pipeline failed for all 5 stores.**

## Slack ledger (what Joshua sent today)

| Store | Channel | Amounts sent | Net expected |
|---|---|---|---|
| CUL (Pepper) | #pepper-funds | $3,000 @ 15:03, $2,000 @ 15:04 | **$5,000** |
| HAR | #harrisonburg-funds | — | $0 |
| LEX | #lex-funds | — | $0 |
| ROA | #roanoke-funds | — | $0 |
| WAY (Boro) | #boro-funds | — | $0 |

Context for CUL: Sandi asked for $2k ops cash plus a lot purchase. Joshua sent $3k, then $2k after she clarified "both". Sandi confirmed $5k total → Joshua: "yes".

## Bravo verification

Trigger: `daily-funds-verification-2026-05-27T18-04-30`
Result: `partial` — all 5 cells errored with `EnsureStore failed for <STORE>` (~35s each).

| Store | Status | Bravo total | Variance |
|---|---|---|---|
| CUL | Could not verify | — | — |
| HAR | Could not verify | — | — |
| LEX | Could not verify | — | — |
| ROA | Could not verify | — | — |
| WAY | Could not verify | — | — |

## Action

Per project memory, `EnsureStore failed` on all 5 cells points to either:
1. StoreCycle post-dblclick timeout (check ROA first as canary), or
2. Bravo stuck pre-login (ClickOnce relaunch unreliable — needs UI access to fix).

CUL has $5,000 of unverified sends from today. Joshua needs to manually verify in Bravo Safe Register Journal, or restart the watcher on the Windows VM and re-run.
