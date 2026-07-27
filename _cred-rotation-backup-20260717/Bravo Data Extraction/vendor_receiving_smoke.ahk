; ============================================================================
; vendor_receiving_smoke.ahk — first end-to-end test of the write-side pipeline
;
; PURPOSE: drive Bravo to create the vendor receiving for M&M Merchandisers
; order #31237 at CUL, exercising every step the new VendorReceiving.ahk
; handler implements. This script is STANDALONE — it bypasses the watcher so
; we can iterate on the handler without restarting bravo_watcher.ahk between
; test runs.
;
; HOW TO RUN (on the Windows VM, with Bravo open and reachable):
;   1) Ensure DRY_RUN is set the way you want (true for the first pass).
;   2) Bring Bravo to the front (or let the script's ActivateBravo do it).
;   3) Double-click this file, or from cmd:
;        AutoHotkey64.exe vendor_receiving_smoke.ahk
;   4) Watch the per-run log at logs\vendor-receiving-smoke-*.log
;   5) Watch the per-run result at results\vendor-receiving-smoke-*.result.json
;
; FIRST RUN PROTOCOL (Joshua):
;   - DRY_RUN := true (default in this file). Form fills end-to-end but
;     stops before clicking Save. Bravo will be left on the populated Add
;     Receiving form. Screenshot the form, eyeball every field, send to
;     Claude. Likely points of failure on the first dry-run:
;       * Bravo's Add Receiving form is not where SKILL.md says — UIA
;         lookup fails. The log will show LogVisibleNames dumps with
;         the actual element names. Update VR_ELEMENTS in
;         reports/VendorReceiving.ahk accordingly.
;       * Pixel-coord fallbacks miss because CUL renders at a different
;         resolution than WAY. We'll switch to UIA-only for those sites.
;       * Grid row 2/3 coords are off (VR_GRID_ROW_PITCH_Y wrong). Easy
;         tune once we see the dump.
;       * Vendor "M&M Merchandisers" isn't in CUL's Bravo vendor list
;         (it was created at WAY in the #31152 run; each store may have
;         its own vendor list). The vendor-selection step will fail; we
;         add it manually or extend the handler to call Add New Vendor.
;
;   - If dry-run looks clean, flip DRY_RUN := false and re-run. Bravo
;     will Save the receiving, dismiss the Print Tags dialog, and the
;     result JSON will capture the assigned RI-VAP number + bucket
;     numbers.
;
; ⚠️  SKUS BELOW ARE PLACEHOLDERS. The M&M order #31237 email has the real
;     vendor SKUs — update the `vendor_sku` field on each line before
;     running. Bucket numbers below (31237, 31238, 31239) are arbitrary
;     unique numbers; tweak if Bravo's bucket Number field has a 5-char cap
;     that would clash.
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Off
; Silence AHK's #Warn All popup — the modules cross-reference each other and
; the static analyzer can't see across files. Suppressing this matches what
; the watcher tolerates at startup.
#Warn All, Off
#Warn LocalSameAsGlobal, Off

#Include lib\Json.ahk
#Include lib\Bravo.ahk
; lib\Bravo.ahk transitively includes lib\UIA-v2\UIA.ahk
#Include lib\StoreCycle.ahk
; The handler references Fail() (in SafeRegisterJournal.ahk) and
; WaitForBravoWindowExists() (in BuysFromPublic.ahk). Include both so the
; smoke driver pulls in those helpers — same trick the watcher uses.
#Include reports\SafeRegisterJournal.ahk
#Include reports\BuysFromPublic.ahk
#Include reports\VendorReceiving.ahk

; ----- Config ----------------------------------------------------------------

global CONFIG := Map()
CONFIG["paths.project_root"] := A_ScriptDir
CONFIG["paths.triggers"]     := A_ScriptDir . "\triggers"
CONFIG["paths.output"]       := A_ScriptDir . "\output"
CONFIG["paths.results"]      := A_ScriptDir . "\results"
CONFIG["paths.logs"]         := A_ScriptDir . "\logs"
CONFIG["bravo.username"]     := "FREE1@WAY"
CONFIG["bravo.password"]     := "Health2035!"

; ----- TUNABLES --------------------------------------------------------------

; Flip to false ONLY after a clean dry-run.
global DRY_RUN := true

global TARGET_STORE := "CUL"

; ----- Payload --------------------------------------------------------------
;
; M&M Merchandisers order #31237, placed 2026-05-20, shipped to Sandi Cole at
; Valley Pawn Culpeper (571 James Madison Highway). 3 line items, 7 total
; units. Subtotal $97.93 + Shipping $10.05 + Tax $0.00 = $107.98.
;
; SKUs marked PLACEHOLDER — update from the actual M&M order email before
; flipping DRY_RUN := false.
;
BuildPayload() {
    payload := Map()
    payload["store"]          := TARGET_STORE
    payload["dry_run"]        := DRY_RUN
    payload["vendor"]         := "M&M Merchandisers"
    payload["invoice_number"] := "31237"
    payload["invoice_date"]   := "2026-05-20"
    payload["shipping"]       := 10.05
    payload["tax"]            := 0.00

    ; NOTE: category_path is FLAT in the Item Inventory flow (v2). Sporting
    ; Goods is a top-level category in that dialog — not nested under
    ; Manufactured Goods like it was in the old (wrong) Create Bucket flow.
    ; "qty" = number of individual Item Inventory rows to create for this SKU
    ; (each gets its own VP######### number at Save).
    payload["lines"] := [
        Map(
            "vendor_sku",        "S1005-BK",                      ; from M&M #31237
            "description_bravo", "SABRE 600K MINI STUN BLACK",    ; 26 chars
            "qty",               3,
            "unit_cost",         13.99,
            "msrp",              27.98,
            "price",             27.98,
            "category_path",     ["Sporting Goods"],
            "location",          "SALESFLOOR"
        ),
        Map(
            "vendor_sku",        "S1005-PK",                      ; from M&M #31237
            "description_bravo", "SABRE 600K MINI STUN PINK",     ; 25 chars
            "qty",               3,
            "unit_cost",         13.99,
            "msrp",              27.98,
            "price",             27.98,
            "category_path",     ["Sporting Goods"],
            "location",          "SALESFLOOR"
        ),
        Map(
            "vendor_sku",        "S1005-PR",                      ; from M&M #31237
            "description_bravo", "SABRE 600K MINI STUN PURPLE",   ; 27 chars
            "qty",               1,
            "unit_cost",         13.99,
            "msrp",              27.98,
            "price",             27.98,
            "category_path",     ["Sporting Goods"],
            "location",          "SALESFLOOR"
        )
    ]
    return payload
}

; ----- Entry ----------------------------------------------------------------

Main() {
    global CONFIG, DRY_RUN, TARGET_STORE, BRAVO_WIN_TITLE

    ; Override the Bravo window-title match to something that ONLY Bravo POS
    ; ever shows ("VALLEY PAWN" appears in its title bar). The default match
    ; in lib/Bravo.ahk is "Bravo " which collides with File Explorer windows
    ; whose folder name starts with "Bravo" (e.g. "Bravo Data Extraction").
    ; That collision sent EnsureStore to the wrong window during the first
    ; smoke launch (2026-05-22T07:56:36) and is reproducible whenever the
    ; project folder is open in File Explorer at script launch.
    BRAVO_WIN_TITLE := "VALLEY PAWN"

    ; Make sure output / results / logs dirs exist.
    for key in ["paths.output", "paths.results", "paths.logs"] {
        d := CONFIG[key]
        if !DirExist(d)
            DirCreate(d)
    }

    triggerId := "vendor-receiving-smoke-" . TARGET_STORE . "-" . FormatTime(, "yyyy-MM-ddTHH-mm-ss") . (DRY_RUN ? "_dry" : "_live")
    InitLog(CONFIG["paths.logs"], triggerId)
    LogMessage("=== Vendor Receiving smoke test ===")
    LogMessage("  store     = " . TARGET_STORE)
    LogMessage("  dry_run   = " . (DRY_RUN ? "true" : "false"))
    LogMessage("  trigger   = " . triggerId)

    payload := BuildPayload()

    cell := PullVendorReceiving(TARGET_STORE, payload, CONFIG["paths.output"])

    ; Write the result.json in the standard pipeline shape so any downstream
    ; tool (Cowork, the new-inv-intake skill, hand-eyeballing) reads it the
    ; same way it reads any other pipeline result.
    result := Map(
        "trigger_id",  triggerId,
        "started_at",  FormatTime(, "yyyy-MM-ddTHH:mm:ss"),
        "finished_at", FormatTime(, "yyyy-MM-ddTHH:mm:ss"),
        "status",      cell.Get("status", "error"),
        "cells",       [cell],
        "errors",      []
    )
    resultPath := CONFIG["paths.results"] . "\" . triggerId . ".result.json"
    WriteResult(resultPath, result)
    LogMessage("Result written: " . resultPath)

    ; Also write a richer JSON with the write-side-specific fields
    ; (receiving_number, bucket_numbers) since WriteResult uses the read-side
    ; schema and silently drops fields it doesn't know about.
    extPath := CONFIG["paths.results"] . "\" . triggerId . ".vendor.json"
    sb := "{`r`n"
    sb .= '  "trigger_id":       ' . JsonString(triggerId) . ",`r`n"
    sb .= '  "store":            ' . JsonString(TARGET_STORE) . ",`r`n"
    sb .= '  "dry_run":          ' . (DRY_RUN ? "true" : "false") . ",`r`n"
    sb .= '  "status":           ' . JsonString(cell.Get("status", "")) . ",`r`n"
    sb .= '  "receiving_number": ' . JsonString(cell.Get("receiving_number", "")) . ",`r`n"
    sb .= '  "duration_ms":      ' . cell.Get("duration_ms", 0) . ",`r`n"
    sb .= '  "row_count":        ' . cell.Get("row_count", 0) . ",`r`n"
    sb .= '  "error":            ' . JsonString(cell.Get("error", "")) . ",`r`n"
    sb .= '  "bucket_numbers": {'
    buckets := cell.Get("bucket_numbers", Map())
    bi := 0
    for sku, num in buckets {
        if (bi > 0)
            sb .= ","
        sb .= "`r`n    " . JsonString(sku) . ": " . JsonString(String(num))
        bi += 1
    }
    if (bi > 0)
        sb .= "`r`n  "
    sb .= "}`r`n}`r`n"
    if FileExist(extPath)
        FileDelete(extPath)
    FileAppend(sb, extPath, "UTF-8")
    LogMessage("Ext result written: " . extPath)

    ; Summary popup so the operator at the VM sees what happened without
    ; opening the JSON.
    summary := "Vendor Receiving Smoke`n"
    summary .= "Store: " . TARGET_STORE . "`n"
    summary .= "Dry run: " . (DRY_RUN ? "YES (form filled, NOT saved)" : "NO (live — receiving saved)") . "`n`n"
    summary .= "Status: " . cell.Get("status", "?") . "`n"
    summary .= "Duration: " . cell.Get("duration_ms", "?") . " ms`n"
    summary .= "Lines: " . cell.Get("row_count", 0) . "`n"
    if (cell.Get("receiving_number", "") != "")
        summary .= "Receiving #: " . cell["receiving_number"] . "`n"
    if (cell.Get("error", "") != "")
        summary .= "`nError: " . cell["error"] . "`n"
    summary .= "`nResult: " . resultPath . "`n"
    summary .= "Log: " . CONFIG["paths.logs"] . "\" . triggerId . ".log"
    MsgBox(summary, "Vendor Receiving Smoke", "OK")
}

Main()
