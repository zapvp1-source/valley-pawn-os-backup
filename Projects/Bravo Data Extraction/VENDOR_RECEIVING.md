# Vendor Receiving — write-side pipeline

First write-side module in the Bravo Data Extraction pipeline. Drives Bravo's
Inventory → Stock Management → Add Receiving flow to record a wholesale
purchase end-to-end, no Parallels-from-Mac required.

## Files

| File | Role |
|------|------|
| `reports/VendorReceiving.ahk` | Handler module — drives the Bravo UI. Two entry points: `PullVendorReceiving(store, payload, outputDir)` (used by the smoke driver) and `PullVendorReceivingFromSidecar(store, payloadKey, outputDir)` (registered with the watcher as `vendor-receiving`). |
| `vendor_receiving_smoke.ahk` | Standalone driver. Hard-codes the M&M #31237 payload. Bypasses the watcher so the handler can be tested without restarting `bravo_watcher.ahk`. |
| `triggers/staging/vendor-receiving-31237-cul.json` | Example trigger JSON (held in `staging/` so the watcher doesn't pick it up before it's loaded the new code). |
| `triggers/payloads/CUL_31237.payload.json` | Payload sidecar referenced by the trigger's `date` field. |
| `bravo_watcher.ahk`, `bravo_export.ahk` | Updated additively — new `vendor-receiving` entry in `REPORT_HANDLERS`, new `#Include` line. Existing reports untouched. |

## Two ways to run

### A — Smoke driver (recommended for iteration)

No watcher restart. Edit `vendor_receiving_smoke.ahk` if you need to flip
`DRY_RUN` or change SKUs, then double-click the file in the Windows VM (or
`AutoHotkey64.exe vendor_receiving_smoke.ahk` from cmd). The script writes
its result to `results/vendor-receiving-smoke-*.result.json` and a richer
JSON with `receiving_number` + `bucket_numbers` to
`results/vendor-receiving-smoke-*.vendor.json`. A summary MsgBox pops up at
the end.

### B — Watcher-driven (recommended once the handler is proven)

1. Restart the watcher to pick up the new code: `Ctrl+Alt+W` to exit, then
   re-launch `bravo_watcher.ahk`. Confirm the boot marker at
   `logs/watcher.last_started.txt` lists `vendor-receiving` in the handler
   list.
2. Move (or copy) the trigger from `triggers/staging/` into `triggers/`.
   The watcher picks it up within the poll interval (30s default).
3. Result lands at `results/<trigger-id>.result.json`.

The watcher uses the 3-arg dispatch and reads the payload from
`triggers/payloads/<STORE>_<payloadKey>.payload.json` where `<payloadKey>`
is whatever the trigger's `date` field carries (the vendor invoice number
by convention).

## First-run protocol — #31237 at CUL

Order #31237 (M&M Merchandisers, placed 2026-05-20) shipped Sabre 600k Mini
Stun Guns to Sandi at Culpeper: Black ×3, Pink ×3, Purple ×1 @ $13.99 each;
shipping $10.05; subtotal $97.93; total $107.98.

1. **Update SKUs.** The smoke driver currently has `SAB-MS600-BK`,
   `SAB-MS600-PK`, `SAB-MS600-PR` as placeholders. The actual M&M order
   email has the real SKUs — paste them into the `vendor_sku` field of
   each line in `vendor_receiving_smoke.ahk` before running. Bravo's
   bucket Number is independent and is already set to 31237 / 31238 /
   31239.
2. **Dry run.** `DRY_RUN := true` is the default. Run the smoke driver.
   Bravo fills the Add Receiving form completely, then stops before
   clicking Save. Screenshot the form and skim every field. Check the
   per-run log at `logs/vendor-receiving-smoke-CUL-*_dry.log` for any
   `WARN` lines or `LogVisibleNames` dumps — those flag UIA Name
   mismatches and category-tree miss-clicks.
3. **Tune if needed.** Common first-run issues:
   - **UIA Names off**: the log shows `LogVisibleNames` dumps with the
     real element names. Update `VR_ELEMENTS` in
     `reports/VendorReceiving.ahk`.
   - **Grid row 2/3 cells miss**: `VR_GRID_ROW_PITCH_Y` (default 25) is
     wrong for CUL's display. Eyeball the screenshot and adjust.
   - **Vendor not found**: M&M Merchandisers may not exist in CUL's
     Bravo vendor list (each store has its own). Add it manually in
     Bravo first, or extend the handler to call Add New Vendor. The
     vendor name in Bravo MUST exactly match the Wholesale Vendors
     registry in the New Inventory Tracker.
4. **Live run.** Flip `DRY_RUN := false` and re-run. Bravo Saves the
   receiving, dismisses the Print Tags dialog, and the script captures
   the assigned RI-VAP number. Confirm in
   `results/vendor-receiving-smoke-*.vendor.json`.

## After a successful live run

The result JSON has `receiving_number` (e.g. `RI-VAP000357`) and a
`bucket_numbers` map (sku → bucket). Hand both back to Claude — Claude
finishes the intake flow:

- Procurement Log row in `New Inventory Tracker.xlsx` (Step 1 of the
  `new-inv-intake` skill)
- Column L populated with `CUL-<bucket> (<RI-VAP>)`
- DM update to Sandi with the RI-VAP number
- `#new-inventory` Slack post with full detail

## Schema reference

Payload (Map at the handler boundary, JSON in sidecar):

```json
{
  "store":          "CUL",
  "dry_run":        false,
  "vendor":         "M&M Merchandisers",
  "invoice_number": "31237",
  "invoice_date":   "2026-05-20",
  "shipping":       10.05,
  "tax":            0.00,
  "lines": [
    {
      "vendor_sku":        "...",
      "description_bravo": "...",       // <=32 chars
      "qty":               3,
      "unit_cost":         13.99,
      "msrp":              27.98,
      "price":             27.98,
      "category_path":     ["Manufactured Goods", "Sporting Goods"],
      "bucket_number":     "31237"      // numeric, unique per line
    }
  ]
}
```

Result cell (per call, written into the standard pipeline result.json):

| field | type | notes |
|-------|------|-------|
| `report` | string | always `"vendor-receiving"` |
| `store` | string | e.g. `"CUL"` |
| `date` | string | mirrors `payload.invoice_number` |
| `status` | string | `"success"` \| `"dry_run"` \| `"skipped_idempotent"` \| `"error"` |
| `output_path` | string | empty — write op |
| `row_count` | int | number of line items processed |
| `duration_ms` | int | wall-clock |
| `error` | string | empty on success |
| `receiving_number` | string | `"RI-VAP000357"` on live success |
| `bucket_numbers` | Map | `{ sku -> bucket }` |
| `dry_run` | bool | mirrors the input flag |

## Known gaps (Phase 6+)

- **Idempotency** — handler does not yet walk the existing receivings
  list before Save. Before the second-ever live run, wire this in:
  on match by vendor + invoice_number, short-circuit with
  `status="skipped_idempotent"` and the existing RI-VAP. Prevents
  duplicate receivings if a trigger fires twice.
- **Auto-create unknown vendor** — currently fails if the vendor isn't
  already in Bravo. Discovery layer (`mm-merchandisers-daily-scan`,
  PDF-invoice scanner) flags unknown vendors. Handler should call Add
  New Vendor with the payload-provided business details when the
  vendor lookup returns no results.
- **Auto-create unknown bucket** — handler currently assumes every SKU
  needs Create Bucket. For repeat purchases of a previously-stocked
  SKU, the SKU search will find the existing bucket and we should
  select it instead of creating a new one. (For Joshua's current
  workflow this is rare — most M&M orders are net-new SKUs.)
- **Bucket-number readback** — on live save, the handler trusts the
  payload's `bucket_number` value. If Bravo truncates or rejects it,
  the value in the result `bucket_numbers` map is wrong. Add a UIA
  readback of the Number field after Create Bucket Ok.
- **Watcher integration smoke** — Path B above has not been exercised
  yet. After Path A succeeds for #31237, move the staging trigger and
  confirm the watcher path also works.
