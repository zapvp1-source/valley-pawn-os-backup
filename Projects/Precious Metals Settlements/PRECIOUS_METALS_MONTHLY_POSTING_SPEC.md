# Valley Pawn — Precious Metals Monthly Settlement & Posting (Master Spec)

**Purpose of this document:** the single, complete instruction set for the recurring monthly job of turning an Elemetal settlement email into money posted in Bravo, for **gold (2 buckets/store) and silver (1 bucket/store)**. Hand this whole document to any future session — cloud or on-computer — instead of re-explaining from scratch. It supersedes/merges two previously-separate specs (`OPERATING_GUIDE.md` for the email→workbook piece, `BRAVO_BUCKET_CLOSEOUT.md` for the Bravo-posting piece) and adds silver, which neither covered as a routine bucket before today.

---

## 1. Scope

Every month, each of Valley Pawn's 5 stores (CUL, HAR, LEX, ROA, WAY) accumulates scrap in **3 Bravo buckets**:

| Bucket type | Bravo bucket (per store) | Count |
|---|---|---|
| Gold, no stones | `<name> GOLD SCRAP` | 1 |
| Gold, with stones | `<name> GOLD W/STONES SCRAP` | 1 |
| Silver | `<name> SILVER SCRAP` | 1 |

= **3 buckets × 5 stores = 15 Bravo buckets closed out per month**, once Elemetal pays.

Elemetal ships back settlement money in 2–3 separate emails/PDFs per month (gold, gold-with-stones, silver — silver sometimes arrives later or gets blended with a prior month, same as gold has). Each store's share of each settlement is proportional to the weight (dwt) that store contributed.

**Bucket naming is NOT standardized across stores** — confirmed live 2026-08-06. Gold bucket names have looked like `JULY 2026 GOLD SCRAP` (CUL, no store name) and `GOLD W/O STONES 7/31/26` (HAR, different format again). ROA's July silver bucket is named `ROANOKE JULY SILVER SCRAP` (includes city name, unlike CUL's gold buckets). **Never assume a naming pattern — always confirm the exact bucket name before building a manifest**, either by looking at Bravo directly or by having the close-out automation's own lookup report back which names it could/couldn't find.

---

## 2. Two-phase architecture — read this before doing anything

This job has two phases with **very different risk profiles and must run in different places**:

### Phase A — Email → Allocation Workbook (safe to run in the cloud)
Reads Gmail, downloads/reads PDFs, calculates dollar allocations, writes a CSV for Joshua to review and approve. **Never touches Bravo, never moves money.** This is fine to run as a cloud-based scheduled task (Gmail search + Claude in Chrome + PDF reading are all cloud-native tools).

### Phase B — Posting into Bravo (MUST run natively on Joshua's machine — never cloud)
Takes Joshua's approved dollar amounts and actually posts them into Bravo, ending in an **irreversible** Approve step ("CANNOT BE VOIDED"). This must run as an on-computer Cowork task or a native AutoHotkey (AHK) scheduled task on the Windows VM — **never via cloud computer-use/screen-driving**. Reason, proven live 2026-08-06: the cloud session's remote-devices bridge to the Mac dropped repeatedly (~4-6 times in one run) during a manual close-out. Every drop is recoverable with no corrupted transactions (Bravo discards unsaved state on disconnect), but it's slow, error-prone, and exactly the failure mode native execution eliminates. Joshua's explicit standing instruction (2026-08-06): *"build it and make it run through the machine, not cloud, nothing should run in cloud."*

**Rule of thumb:** if the step reads information, cloud is fine. If the step clicks Save/Approve inside Bravo, it must be on-computer/native.

---

## 3. Phase A — Email → Allocation Workbook

Full detail lives in `Projects/Precious Metals Settlements/OPERATING_GUIDE.md` — read it in full before running Phase A. Summary:

- **Source:** Gmail account `jdavis@fcfpawn.com`, sender `noreply@elemetal.com`, PDF attachments.
- **Bucket classification from the PDF:** description/metal "Gold" only → `gold`; mentions "Stone" → `gold_stones`; mentions "Silver" → `silver`. Now that silver is a routine monthly bucket (not "if sent"), treat it exactly like gold/gold_stones in every step below — don't special-case it as optional anymore.
- **Blended settlements:** Elemetal sometimes pays out a stones lot + no-stones lot (or, going forward, possibly silver + gold) as ONE settlement instead of separate ones. Use Bravo's own bucket `Status == OPEN` as source of truth for which buckets a blended settlement is actually closing — never guess from the PDF description alone. See OPERATING_GUIDE.md §7 for the full blended-settlement procedure.
- **Money to allocate:** the net `PAYMENT` section `Amount` (after shipping/processing/wire fees) — not the gross LOT amount.
- **Weight source:** `Projects/Bravo Data Extraction/output/<YYYY>_<STORE>_scrap-refining-gold.csv`. **Note the filename says "gold" but the underlying pipeline cell may need a silver-aware pull too** — verify whether this CSV already includes SILVER-named rows (it's the same "Scrap Refining Process" report, metal-agnostic) or whether a new/extended pull is needed. If the existing CSV only shows GOLD rows (unconfirmed either way as of this writing), that's a gap to close before Phase A can allocate silver automatically — flag it rather than guessing.
- **Output:** `Projects/Precious Metals Settlements/reviews/<YYYY-MM>_allocations_REVIEW.csv` — Joshua reviews, adjusts if needed, renames to `_CLOSED.csv` to approve.
- **Archive + Slack notify:** once CLOSED, archive to Drive and post to `#gold-trend-`. Full detail in OPERATING_GUIDE.md §3.

**Output this phase must hand to Phase B:** for every bucket being closed, the exact `{store, bucketName, amountPaid}` triple. Tender type is a fixed policy value (see §4), not something Phase A calculates.

---

## 4. Phase B — Posting into Bravo (native, on-computer only)

### 4.1 What's already built (as of 2026-08-06)

All files live under `Projects/Bravo Data Extraction/` on Joshua's Mac, additive-only (no existing production pipeline files touched):

- **`reports/ScrapBucketCloseout.ahk`** — the handler. Drives one bucket through Open → Shipping → Assayed → Close → Approve. Reuses the already-hardened bucket-list navigation from `ScrapRefiningGold.ahk`.
- **`ScrapBucketCloseoutWatcher.ahk`** — persistent poller watching `triggers-scrap\` for manifest JSON files, independent from the main data-extraction pipeline's own watcher so the two can't collide (each pauses the other's watchdog before touching Bravo).
- **`_scrap_watchdog.ps1` / `restart_scrap_watcher.bat`** — self-healing watchdog, targets only this watcher by CommandLine match (never a blanket AutoHotkey kill).
- **`setup_scrap_watcher.bat`** — registers the `ScrapCloseoutWatcherWatchdog` scheduled task. **Currently registered but DISABLED** pending a fully successful supervised live test (today's silver test is that test).
- **`triggers-scrap\`, `results-scrap\`, `logs-scrap\`** — new working folders.

### 4.2 Manifest schema (what Phase A's approved workbook becomes)

Drop a file into `triggers-scrap\<id>.json`:

```json
{
  "id": "scrap-closeout-<label>-<YYYY-MM>",
  "buckets": [
    {"store": "CUL", "bucketName": "<exact Bravo bucket name>", "amountPaid": "614.23", "tenderType": "Cashiers Check"},
    {"store": "HAR", "bucketName": "<exact Bravo bucket name>", "amountPaid": "502.62", "tenderType": "Cashiers Check"}
  ]
}
```

`tenderType` is always `"Cashiers Check"` per Joshua's standing policy (avoids throwing off till/credit-card numbers). A full month's manifest has up to 15 entries (3 buckets × 5 stores) — buckets can be combined into one manifest or split by metal type; the handler processes store-by-store, closing every bucket at a store before moving to the next (this ordering was an explicit lesson from the 2026-08-06 gold run).

### 4.3 How to run it

1. Confirm the manifest's `bucketName` values are exact (see §1 — never assume a naming pattern). If unconfirmed, either look them up in Bravo first or accept that the automation will safely report "could not locate bucket" for any wrong name (no money moved, no partial state) and let you correct just those.
2. Drop the manifest JSON into `triggers-scrap\`.
3. Launch `ScrapBucketCloseoutWatcher.ahk` (from an on-computer Cowork task, or manually via AutoHotkey64.exe with the VM screen visible for supervised runs). It polls every 60s and picks up new manifests automatically; it also runs continuously once the watchdog task is enabled (currently disabled — see §4.1).
4. It automatically pauses the main pipeline watcher (`BravoWatcherWatchdog`) for the duration of the run and resumes it afterward — don't do this manually, it's built in.
5. Read `results-scrap\<id>.result.json` when done. Each bucket reports `status` (`closed` / `already-closed` / `error`), `verified` (bool — did the post-Approve read-back match the manifest exactly), and `error` (human-readable reason, empty on success).
6. **Any `verified: false` entry is CRITICAL and needs immediate manual review in Bravo** — the transaction cannot be voided, so a mismatch there means Bravo has money posted that doesn't match the approved allocation. This has never happened in testing but the code path exists and logs loudly if it does.

### 4.4 Safety model / gotchas already built in (don't rebuild these — they're solved)

- **Every numeric field** is set via clipboard paste (never simulated typing) and immediately read back via UIA and string-compared to the expected value before proceeding. A mismatch aborts that bucket without saving/approving.
- **Tender Type is selected by exact name match, never by counting arrow-key presses** — confirmed live that the dropdown list length varies by store (CUL/LEX include "Personal Check", HAR doesn't).
- **Scrap Report is printed BEFORE the Close status is selected** — printing after silently discards the status selection (verified twice live).
- **Store/Till are opened if closed, never closed back down** by this automation — an automated Close Store triggers a Store Safe → Bank Account transfer, which is out of scope for unattended execution. Staff's normal end-of-day process handles closing.
- **Post-Approve verification**: the bucket is reopened after Approve and the posted Amount Paid + Tender Type are read back and compared to the manifest. See §4.3 step 6.
- **Idempotent re-runs**: if a bucket is already closed, re-running the same manifest entry just verifies the posted amount matches and reports `already-closed` — it does not error or attempt to re-post.

### 4.5 Known fix applied today (2026-08-06, during silver testing)

The original build hardcoded the "Calculated Assay" field name as `"Calculated Assay-GOLD"` (only ever tested against gold buckets). This would have silently failed every silver bucket at the Shipping→Assayed step. **Fixed**: the handler now tries `Calculated Assay-GOLD` then `Calculated Assay-SILVER` and uses whichever field actually exists on screen, logging which one matched. This has been patched in `reports/ScrapBucketCloseout.ahk` but **has not yet been exercised live** — today's silver test is also the first real exercise of this fix. Watch the log (`logs-scrap\<id>.log`) for the `[assay-lookup]` line to confirm it matched `Calculated Assay-SILVER` as expected.

---

## 5. TODAY'S TEST — July 2026 silver buckets

Joshua is supplying the dollar amounts directly this time (bypassing Phase A / the Elemetal email) specifically to test whether the Phase B handler — built and verified only against gold so far — also works correctly for silver. This is the **first-ever live exercise of this handler through the native AHK path**, and the first-ever exercise of the GOLD/SILVER assay-field fix.

**Amounts supplied by Joshua (2026-08-06), for July 2026 silver scrap:**

| Store | Amount |
|---|---|
| WAY (Waynesboro) | $1,097.41 |
| CUL (Culpeper) | $614.23 |
| HAR (Harrisonburg) | $502.62 |
| LEX (Lexington) | $427.27 |
| ROA (Roanoke) | $122.40 |
| **Total** | **$2,763.93** |

**Bucket names:** only ROA's is confirmed (`ROANOKE JULY SILVER SCRAP`, seen live). CUL/HAR/LEX/WAY names in the manifest currently sitting in `triggers-scrap\scrap-closeout-silver-2026-07.json` are **guesses** following the `<CITY> JULY SILVER SCRAP` pattern — **not confirmed**. Given §1's finding that bucket naming isn't standardized, expect some of these four to fail lookup. That's fine and safe (no money moves on a bad name) — correct the manifest with the real name from Bravo's own bucket list and re-run just the failed entries; already-closed buckets from the same run are skipped idempotently.

**Tender type:** `Cashiers Check` for all 5, per standing policy (§4.2).

**Steps for this run:**
1. On-computer Cowork task (or Joshua directly) launches `ScrapBucketCloseoutWatcher.ahk` with the manifest already in `triggers-scrap\`.
2. Watch the VM screen for the first bucket at minimum, to confirm the Open→Shipping→Assayed transition correctly finds `Calculated Assay-SILVER` (the fix in §4.5).
3. Read `results-scrap\scrap-closeout-silver-2026-07.result.json` when done.
4. For any bucket with a "could not locate bucket" error, look up the real bucket name in Bravo (Inventory → Scrap Refining Process, for that store) and re-run with a corrected single-entry manifest.
5. Confirm final total posted equals $2,763.93 across the 5 buckets (allow for entries fixed on a second pass).
6. Report back: which stores succeeded on the first pass, which needed a name correction, and whether the assay-field fix worked as expected.

**If this test succeeds cleanly:** that satisfies the "one supervised test" requirement in `setup_scrap_watcher.bat` — enable `ScrapCloseoutWatcherWatchdog` (`schtasks /change /tn ScrapCloseoutWatcherWatchdog /enable`) so future months run unattended.

---

## 6. Open items / not yet built

- **Phase A doesn't yet treat silver as a routine bucket** — OPERATING_GUIDE.md currently says "silver (if sent; silver is often held back)," treating it as occasional. Now that silver is a routine monthly bucket, that guide should be updated to search for and process silver settlement emails with the same rigor as gold, every month — not opportunistically.
- **Unconfirmed whether the Bravo weight-pull CSVs (`<YYYY>_<STORE>_scrap-refining-gold.csv`) already include silver bucket rows.** If not, Phase A's automatic weight-based allocation for silver needs a pipeline extension before it can run unattended (today's test sidesteps this entirely since Joshua supplied the dollar amounts directly).
- **No manifest-generation step yet exists connecting Phase A's approved CLOSED workbook to Phase B's manifest JSON automatically** — today this is a manual/assisted step. Worth automating once both phases have been proven independently (Phase A for silver is unproven; Phase B for silver is being proven today).
- **`ScrapCloseoutWatcherWatchdog` stays disabled** until today's test succeeds cleanly end-to-end.

---

*Source documents this spec consolidates: `Projects/Precious Metals Settlements/OPERATING_GUIDE.md` (Phase A), `Projects/Precious Metals Settlements/BRAVO_BUCKET_CLOSEOUT.md` (Phase B procedure + live-run lessons), and `Projects/Valley Pawn OS/BUSINESS_OS.md` 2026-08-06 addendum (Phase B build status). Written 2026-08-06.*
