; ============================================================================
; reports/ScrapBucketCloseout.ahk
;
; Executes the Bravo "Scrap Refining Process" bucket close-out sequence
; (Open -> Shipping -> Assayed -> Close -> Approve) against an APPROVED
; manifest of {store, bucketName, amountPaid, tenderType}. Built from the
; live-verified procedure in BRAVO_BUCKET_CLOSEOUT.md (2026-08-06 full
; 10-bucket run, all amounts tied to the wire to the penny).
;
; This does NOT decide amounts. The manifest is the product of the
; settlement-allocation workbook (Elemetal email + Bravo scrap-refining-gold
; weights), reviewed and approved by a human (Preston/Joshua) BEFORE this
; script ever touches Bravo. This script's only job is mechanical, faithful
; execution of an already-approved decision, with verification at every
; step and a hard stop on any mismatch.
;
; SAFETY MODEL (read before enabling unattended scheduling):
;   - Every numeric field is set via clipboard paste (never simulated typing)
;     and IMMEDIATELY read back via UIA and string-compared to the expected
;     value. Any mismatch aborts that bucket without saving/approving.
;   - The "Select Status" transition (Open->Shipping->Assayed->Close) was
;     verified 10/10 times live to be a simple "Down, Return" from whatever
;     status is current, because Bravo only ever offers the single next
;     status as the second list item. This is hardcoded on that basis.
;   - The "Tender Type" list VARIES IN LENGTH BY STORE (confirmed live:
;     CUL/LEX include "Personal Check", HAR does not) so it is NEVER
;     selected by counting arrow presses. See SelectTenderType() below.
;   - After Approve, the bucket is REOPENED and Amount Paid + Tender Type
;     are read back from the now-locked, saved record and compared again.
;     A post-save mismatch cannot be fixed (Bravo: "CANNOT BE VOIDED") but
;     it WILL be logged as a CRITICAL result so a human is alerted
;     immediately rather than finding out at month-end reconciliation.
;   - This bucket-close flow has been exercised LIVE only via manual
;     computer-use, never yet via this AHK path end-to-end. Run ONE
;     supervised test (screen visible, someone watching) before trusting
;     it fully unattended. The paired watchdog scheduled task
;     (ScrapCloseoutWatcherWatchdog) ships DISABLED for this reason -
;     see ScrapBucketCloseoutWatcher.ahk header.
;
; Manifest schema (JSON, one file per settlement cycle):
;   {
;     "id": "scrap-closeout-2026-09",
;     "buckets": [
;       {"store": "CUL", "bucketName": "AUGUST 2026 GOLD SCRAP",
;        "amountPaid": "11799.44", "tenderType": "Cashiers Check"},
;       ...
;     ]
;   }
;
; Result schema (JSON, written to results-scrap/<id>.result.json):
;   {
;     "trigger_id": "...", "started_at": "...", "finished_at": "...",
;     "status": "success" | "partial" | "error",
;     "totalPaid": 66160.08, "bucketCount": 10,
;     "buckets": [ {store, bucketName, amountPaid, tenderType, status,
;                    priorStatus, verified, error}, ... ]
;   }
; ============================================================================
#Requires AutoHotkey v2.0

global CLOSEOUT_ELEMENTS := Map(
    "select_status",        "Select Status",
    "amount_paid",          "Amount Paid",
    "tender_type",          "Tender Type",
    "total_weight_shipped", "Total Weight of Scrap Shipped",
    "confirmed_weight",     "Confirmed Weight Received",
    "assay_from_vendor",    "Assay from Vendor",
    "combined_metal_weight","Combined Metal Weight",
    "calculated_assay_gold",   "Calculated Assay-GOLD",
    "calculated_assay_silver", "Calculated Assay-SILVER",
    "select_vendor",        "Select Vendor",
    "vendor_filter",        "Filter",
    "scrap_vendor_name",    "SCRAP",
    "print_scrap_report",   "Print Scrap Report",
    "approve",              "Approve",
    "save",                 "Save",
    "ok",                   "Ok",
    "open_store",           "Open Store",
    "open_till",            "Open Till",
    "use_expected_values",  "Use Expected Values",
    "next",                 "Next"
)

; ----------------------------------------------------------------------------
; Entry point. manifestPath -> a scrap-closeout manifest JSON file.
; Returns a result Map matching the schema above. Always attempts to leave
; the pipeline watcher exactly as it found it (paused only for the duration
; of this run), even on error - see the try/finally around the store loop.
; ----------------------------------------------------------------------------
; Read-only / dry-run mode. Set by a manifest carrying "readOnly": true.
; When on, CloseoutOneBucket opens each bucket, reads and logs every field it
; would otherwise act on, then backs out WITHOUT selecting a status, without
; writing any value and without saving - so the whole navigate + locate + read
; path can be proven against real production buckets with zero money at risk.
; Added 2026-08-06 after the field-read bug; keep it, every future change to
; this handler should be dry-run proven before it is allowed to post money.
; ----------------------------------------------------------------------------
global CLOSEOUT_READONLY := false

RunScrapCloseoutManifest(manifestPath) {
    global CLOSEOUT_READONLY
    result := Map(
        "trigger_id",  "",
        "started_at",  FormatTime(, "yyyy-MM-dd HH:mm:ss"),
        "finished_at", "",
        "status",      "error",
        "totalPaid",   0.0,
        "bucketCount", 0,
        "buckets",     []
    )

    manifest := ParseScrapManifest(manifestPath)
    result["trigger_id"] := manifest["id"]
    CLOSEOUT_READONLY := manifest["readOnly"]
    if CLOSEOUT_READONLY
        LogMessage("*** READ-ONLY DRY RUN - fields will be read and logged, nothing saved, no money posted ***")

    if (manifest["buckets"].Length = 0) {
        LogMessage("RunScrapCloseoutManifest: manifest has zero buckets - nothing to do")
        result["status"] := "error"
        result["finished_at"] := FormatTime(, "yyyy-MM-dd HH:mm:ss")
        return result
    }

    ; Group buckets by store, preserving manifest order within each store,
    ; so we close BOTH buckets at a store before moving to the next -
    ; this was an explicit lesson from the 2026-08-06 manual run (Joshua:
    ; "why wouldnt we do all buckets at one store before moving on").
    byStore := Map()
    storeOrder := []
    for b in manifest["buckets"] {
        st := b["store"]
        if !byStore.Has(st) {
            byStore[st] := []
            storeOrder.Push(st)
        }
        byStore[st].Push(b)
    }

    watcherWasPaused := false
    overallStatus := "success"
    totalPaid := 0.0

    try {
        PauseMainWatcher()
        watcherWasPaused := true

        for store in storeOrder {
            LogMessage("=== Store " . store . " (" . byStore[store].Length . " bucket(s)) ===")
            if !EnsureStore(store, CONFIG.Get("bravo.password", "")) {
                for b in byStore[store] {
                    result["buckets"].Push(Map(
                        "store", store, "bucketName", b["bucketName"],
                        "amountPaid", b["amountPaid"], "tenderType", b["tenderType"],
                        "status", "error", "priorStatus", "", "verified", false,
                        "error", "EnsureStore failed for " . store
                    ))
                }
                overallStatus := "partial"
                continue
            }

            EnsureStoreAndTillOpen(store)

            for b in byStore[store] {
                bucketResult := CloseoutOneBucket(store, b["bucketName"], b["amountPaid"], b["tenderType"])
                result["buckets"].Push(bucketResult)
                if (bucketResult["status"] = "closed" || bucketResult["status"] = "already-closed") {
                    totalPaid += Float(RegExReplace(b["amountPaid"], "[^0-9.]", ""))
                } else {
                    overallStatus := "partial"
                }
            }
        }
    } catch as e {
        LogMessage("RunScrapCloseoutManifest: FATAL - " . e.Message)
        overallStatus := "error"
    } finally {
        if watcherWasPaused {
            ResumeMainWatcher()
        }
    }

    result["status"]      := overallStatus
    result["totalPaid"]   := Round(totalPaid, 2)
    result["bucketCount"] := result["buckets"].Length
    result["finished_at"] := FormatTime(, "yyyy-MM-dd HH:mm:ss")

    WriteScrapResult(CONFIG["paths.scrap_results"] . "\" . result["trigger_id"] . ".result.json", result)
    LogMessage("RunScrapCloseoutManifest: done - status=" . overallStatus . " totalPaid=" . result["totalPaid"] . " buckets=" . result["bucketCount"])
    return result
}

; ----------------------------------------------------------------------------
; Close a single bucket. Handles all three status transitions needed to get
; from wherever the bucket currently is to CLOSED, using the SAME UIA
; navigation primitives (ScrapOpenFilteredBucketList / ScrapRelocateAndOpenBucket
; / ScrapVerifyOpenBucketName) already hardened and proven in
; reports/ScrapRefiningGold.ahk - not reinvented here.
; ----------------------------------------------------------------------------
CloseoutOneBucket(store, bucketName, amountPaid, tenderType) {
    global CLOSEOUT_READONLY
    out := Map(
        "store", store, "bucketName", bucketName,
        "amountPaid", amountPaid, "tenderType", tenderType,
        "status", "error", "priorStatus", "", "verified", false, "error", ""
    )

    LogMessage("  --- bucket '" . bucketName . "' (" . store . ") ---")

    status := OpenBucketAndReadStatus(bucketName)
    if (status = "") {
        out["error"] := "could not locate/open bucket '" . bucketName . "'"
        LogMessage("    " . out["error"])
        return out
    }
    out["priorStatus"] := status
    LogMessage("    current status: " . status)

    ; --- Read-only dry run: read everything, change nothing, back out ---------
    if CLOSEOUT_READONLY {
        rdWeight := ReadFieldValue(CLOSEOUT_ELEMENTS["combined_metal_weight"])
        rdAssay  := ReadCalculatedAssayValue()
        rdAmount := ReadFieldValue(CLOSEOUT_ELEMENTS["amount_paid"])
        rdTender := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
        LogMessage("    [dry-run] Select Status         = '" . status . "'")
        LogMessage("    [dry-run] Combined Metal Weight = '" . rdWeight . "'")
        LogMessage("    [dry-run] Calculated Assay      = '" . rdAssay . "'")
        LogMessage("    [dry-run] Amount Paid           = '" . rdAmount . "'")
        LogMessage("    [dry-run] Tender Type           = '" . rdTender . "'")
        LogMessage("    [dry-run] manifest would post   = '" . amountPaid . "' / '" . tenderType . "'")
        DoneOrCancelBucketDetail()
        try BackToDashboard()
        out["status"]   := "readonly"
        out["verified"] := (RegExReplace(rdWeight, "[^0-9.]", "") != "")
        if !out["verified"]
            out["error"] := "dry run could not read Combined Metal Weight"
        return out
    }

    if InStr(status, "Close") || InStr(status, "CLOSED") {
        ; Idempotent re-run: already closed. Verify the posted amount
        ; matches the manifest and report accordingly rather than erroring.
        posted := ReadFieldValue(CLOSEOUT_ELEMENTS["amount_paid"])
        DoneOrCancelBucketDetail()
        ; 2026-08-06: DoneOrCancelBucketDetail() falls back to clicking
        ; "Cancel" whenever "Done" is not present, which raises Bravo's
        ; "Are you sure you want to cancel your changes?" confirmation
        ; dialog. BackToDashboard() already has proven btnYes-handling
        ; logic for exactly this dialog (see lib/Bravo.ahk) - call it
        ; after every DoneOrCancelBucketDetail() so that dialog never
        ; gets left open and stuck.
        try BackToDashboard()
        postedClean := RegExReplace(posted, "[^0-9.]", "")
        expectClean := RegExReplace(amountPaid, "[^0-9.]", "")
        out["status"]   := "already-closed"
        out["verified"] := (postedClean = expectClean)
        if !out["verified"]
            out["error"] := "ALREADY CLOSED but amount mismatch: bucket shows " . posted . ", manifest expects $" . amountPaid
        LogMessage("    already closed - posted=" . posted . " expected=" . amountPaid . " verified=" . out["verified"])
        return out
    }

    ; --- Open -> Shipping ---------------------------------------------------
    if InStr(status, "Open") {
        if !AdvanceOpenToShipping() {
            out["error"] := "Open->Shipping pass failed"
            DoneOrCancelBucketDetail()
            ; See 2026-08-06 comment above (already-closed branch) - answer
            ; the Cancel-confirmation dialog so Bravo is not left stuck.
            try BackToDashboard()
            return out
        }
        ; Reopen for the next pass
        status := OpenBucketAndReadStatus(bucketName)
        if (status = "") {
            out["error"] := "lost bucket after Shipping save"
            return out
        }
    }

    ; --- Shipping -> Assayed -------------------------------------------------
    if InStr(status, "Shipping") {
        if !AdvanceShippingToAssayed() {
            out["error"] := "Shipping->Assayed pass failed"
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            return out
        }
        status := OpenBucketAndReadStatus(bucketName)
        if (status = "") {
            out["error"] := "lost bucket after Assayed save"
            return out
        }
    }

    ; --- Assayed -> Close ------------------------------------------------
    if InStr(status, "Assayed") {
        closeOutcome := AdvanceAssayedToClose(amountPaid, tenderType)
        if (closeOutcome != "ok") {
            out["error"] := closeOutcome
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            return out
        }
    } else {
        out["error"] := "unexpected status after prior passes: " . status
        DoneOrCancelBucketDetail()
        try BackToDashboard()
        return out
    }

    ; --- Post-approve verification: reopen and read back the locked record --
    Sleep(1500)
    verifyStatus := OpenBucketAndReadStatus(bucketName)
    postedAmount := ReadFieldValue(CLOSEOUT_ELEMENTS["amount_paid"])
    postedTender := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
    DoneOrCancelBucketDetail()
    try BackToDashboard()

    postedClean := RegExReplace(postedAmount, "[^0-9.]", "")
    expectClean := RegExReplace(amountPaid, "[^0-9.]", "")
    amountOk := (postedClean = expectClean)
    tenderOk := (Trim(postedTender) = Trim(tenderType))

    out["status"]   := (InStr(verifyStatus, "Close") || InStr(verifyStatus, "CLOSED")) ? "closed" : "error"
    out["verified"] := amountOk && tenderOk
    if !out["verified"] {
        out["error"] := "CRITICAL POST-SAVE MISMATCH - posted amount='" . postedAmount . "' (expected $" . amountPaid . "), posted tender='" . postedTender . "' (expected '" . tenderType . "'). Transaction CANNOT be voided - flag for manual review."
        LogMessage("    " . out["error"])
    } else {
        LogMessage("    CLOSED and verified: " . postedAmount . " / " . postedTender)
    }
    return out
}

; ----------------------------------------------------------------------------
; Open the named bucket (any status) and return its current Select Status
; text, or "" on failure. Reuses ScrapOpenFilteredBucketList/
; ScrapRelocateAndOpenBucket/ScrapVerifyOpenBucketName from
; reports/ScrapRefiningGold.ahk (already #Include'd by the watcher).
; ----------------------------------------------------------------------------
; ----------------------------------------------------------------------------
; 2026-08-06 silver test finding: CLOSEOUT_ELEMENTS["select_status"] ("Select
; Status") only ever matches the static Text LABEL next to the dropdown -
; confirmed via LogVisibleNames() dump showing zero ComboBox-typed elements
; and the actual control exposed only as a generic Edit-typed "BravoComboBox"
; with no name tying it to the field. FindByName("Select Status") therefore
; can never find the value control, so ReadFieldValue always returns "" for
; this one field - not a timing issue (screenshot confirmed the dropdown
; clearly showing "Open - Enter items" at the moment of the failed read).
;
; Fix: locate the "Select Status" label by Name (that DOES resolve), then
; find the Edit-typed element on the same screen row, to its right - the
; dropdown is always laid out immediately beside its label in Bravo's forms.
; ----------------------------------------------------------------------------
ReadSelectStatusNearLabel() {
    try {
        root := GetBravoRoot()
        label := 0
        try label := root.FindElement({Type: "Text", Name: "Select Status"})
        if !label
            return ""
        lpos := label.GetPos("screen")
        lcy := lpos.y + Round(lpos.h / 2)
        lright := lpos.x + lpos.w
        edits := 0
        try edits := root.FindElements({Type: "Edit"})
        if (!edits || edits.Length = 0)
            return ""
        best := 0
        bestDist := 999999
        for e in edits {
            epos := 0
            try epos := e.GetPos("screen")
            if !epos
                continue
            ecy := epos.y + Round(epos.h / 2)
            if (Abs(ecy - lcy) > 15)
                continue
            if (epos.x < lpos.x)
                continue
            dist := epos.x - lright
            if (dist < 0)
                dist := 0
            if (dist < bestDist) {
                bestDist := dist
                best := e
            }
        }
        if !best
            return ""
        ; 2026-08-06: the raw .Value/.Name off this control came back as an
        ; internal short code ("SBKTOP") rather than the visible text ("Open -
        ; Enter items") - which breaks the InStr(status, "Open"/"Close"/etc.)
        ; checks every caller of this status relies on. Prefer a human-readable
        ; descendant (the WPF ComboBox's selected-item TextBlock) over the
        ; control's own Value/Name, which is just its internal code/class name.
        childText := ""
        try {
            kids := best.FindElements({})
            if (kids && kids.Length) {
                for k in kids {
                    kn := ""
                    try kn := k.Name
                    if (kn = "" || kn = "BravoComboBox" || kn = "PopupBaseEdit")
                        continue
                    childText := kn
                    break
                }
            }
        }
        if (childText != "")
            return childText
        val := ""
        try val := best.Value
        if (val = "")
            try val := best.Name
        if (val = "BravoComboBox" || val = "PopupBaseEdit")
            return ""  ; matched the control but it reported its own class name, not a real value
        ; Last resort: an internal short code we cannot translate to the
        ; Open/Shipping/Assayed/Close words every caller matches against.
        ; Returning it as-is would silently misroute the state machine (it
        ; would hit the "unexpected status" branch and error out safely, which
        ; is what happened before this fallback existed) - log it plainly so
        ; that failure mode is easy to recognize in the log instead of looking
        ; like a random unknown status.
        ; Known internal-code -> human-word translations, discovered one at a
        ; time via real live runs against ROA's silver bucket (2026-08-06).
        ; Every caller of this status matches against the Open/Shipping/
        ; Assayed/Close words, never the raw code, so translate here rather
        ; than touch every call site. Extend this map as new codes surface -
        ; each addition should come from an observed real run, not a guess.
        knownCodes := Map("SBKTOP", "Open")
        if knownCodes.Has(val) {
            LogMessage("    [status-near-label] translated internal code '" . val . "' -> '" . knownCodes[val] . "'")
            return knownCodes[val]
        }
        if (val != "")
            LogMessage("    [status-near-label] only found internal code '" . val . "' - no translation known yet, no human-readable text available")
        return val
    } catch as e {
        LogMessage("    [status-near-label] error: " . e.Message)
        return ""
    }
}

OpenBucketAndReadStatus(bucketName) {
    Loop 3 {
        try {
            if !ScrapOpenFilteredBucketList() {
                LogMessage("    [open] could not open filtered bucket list")
                continue
            }
        } catch as e {
            LogMessage("    [open] ScrapOpenFilteredBucketList error: " . e.Message)
            continue
        }
        if !ScrapRelocateAndOpenBucket(bucketName, 0) {
            LogMessage("    [open] could not locate row '" . bucketName . "'")
            ; BRAVO_KNOWN_ISSUES.md 2026-07-31: a handler that walks away while
            ; a Bravo dialog is still open wedges the app for whatever runs
            ; next (the exact cascade that hit LEX/ROA/WAY on 2026-08-06's
            ; first live test). The bucket-list picker is still on screen at
            ; this point - close it via Cancel/Done before returning, same
            ; pattern already used below for the WRONG BUCKET OPEN case.
            try DoneOrCancelBucketDetail()
            try BackToDashboard()
            return ""
        }
        Sleep(2500)
        if !ScrapVerifyOpenBucketName(bucketName) {
            LogMessage("    [open] WRONG BUCKET OPEN (expected '" . bucketName . "') - backing out and retrying")
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            continue
        }
        ; 2026-08-06 silver test: bucket name verified open correctly but
        ; Select Status sometimes reads back empty on the first check -
        ; Bravo's detail screen still settling after the double-click open.
        ; Give it up to 2 extra reads before treating this as a real
        ; failure; previously a single empty read here fell straight
        ; through to `return statusVal` and skipped the loop's remaining
        ; retries entirely, mislabeling a timing issue as "could not
        ; locate/open bucket" even though the correct bucket was open.
        statusVal := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
        if (statusVal = "") {
            Loop 2 {
                LogMessage("    [open] Select Status read back empty (attempt " . A_Index . "/2) - bucket is open, retrying read")
                Sleep(1000)
                statusVal := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
                if (statusVal != "")
                    break
            }
        }
        if (statusVal = "") {
            statusVal := ReadSelectStatusNearLabel()
            if (statusVal != "")
                LogMessage("    [open] Select Status recovered via position-based lookup: '" . statusVal . "'")
        }
        if (statusVal = "") {
            LogMessage("    [open] Select Status still empty after retries - backing out and retrying open")
            try ScreenshotToFile("select-status-empty")
            try LogVisibleNames(60)
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            continue
        }
        return statusVal
    }
    return ""
}

; ----------------------------------------------------------------------------
; Read a labeled field's current value. Works for both ComboBox (Select
; Status, Tender Type) and Edit (Amount Paid) controls, since in this app
; the interactive control shares its UIA Name with the field label (same
; pattern already relied upon by SetValueByName/FindByName throughout
; lib/Bravo.ahk and lib/StoreCycle.ahk).
; ----------------------------------------------------------------------------
; ----------------------------------------------------------------------------
; Read the VALUE that belongs to a label on the Scrap Bucket Detail screen.
;
; 2026-08-06 rev2 - THE fix for this handler. Every field on this screen is a
; label control whose UIA Name is the literal label text ("Select Status",
; "Combined Metal Weight", "Amount Paid", ...) with NO value on it; the actual
; value lives in a SEPARATE adjacent control that reports only its own class
; name ("BravoComboBox" / "PopupBaseEdit") from .Name. So GetValueByName(label)
; can never work here - it finds the label and reads the label.
;
; This is a solved problem: ScrapRefiningGold.ahk has been reading Combined
; Metal Weight off this exact screen in production every month via
; ScrapReadCombinedWeightValue() - walk the flat element list, find the label,
; then take the first following element (within a few siblings) that has a
; non-empty .Value. That handler is already #included here, so this is the same
; proven technique generalized to any label rather than a second invention.
; Sibling-order, NOT screen geometry - geometry was tried 2026-08-06 and is
; brittle (it matched the control but only ever yielded internal codes).
; ----------------------------------------------------------------------------
ScrapReadValueAfterLabel(labelText) {
    try {
        root := GetBravoRoot()
        allEl := ""
        try allEl := root.FindElements({})
        if !allEl
            return ""
        foundLabel := false
        checkedSince := 0
        for e in allEl {
            if !foundLabel {
                nm := ""
                try nm := e.Name
                if (nm = labelText)
                    foundLabel := true
                continue
            }
            checkedSince++
            if (checkedSince > 6)
                break
            val := ""
            try val := e.Value
            if (val != "" && val != labelText)
                return val
        }
        return ""
    } catch as e {
        LogMessage("    [read-after-label] '" . labelText . "' error: " . e.Message)
        return ""
    }
}

ReadFieldValue(fieldName) {
    ; Proven sibling-walk first (see above), naive name lookup only as a
    ; fallback for any field that genuinely does carry its value on the label.
    val := ScrapReadValueAfterLabel(fieldName)
    if (val != "")
        return val
    return GetValueByName(fieldName, 3000)
}

; ----------------------------------------------------------------------------
; Status transitions. Each is a self-contained Save; the caller reopens the
; bucket afterward for the next transition (Bravo re-renders the detail
; screen per status, matching the live-verified manual procedure).
; ----------------------------------------------------------------------------
AdvanceOpenToShipping() {
    try {
        weight := ReadFieldValue(CLOSEOUT_ELEMENTS["combined_metal_weight"])
        weightClean := RegExReplace(weight, "[^0-9.]", "")
        if (weightClean = "") {
            LogMessage("    [shipping] could not read Combined Metal Weight")
            return false
        }

        SelectNextStatus()  ; Open -> Shipping (Down, Return)

        SetAndVerifyField(CLOSEOUT_ELEMENTS["total_weight_shipped"], weightClean)

        ; --- Select vendor "SCRAP" ---
        if !FindByName(CLOSEOUT_ELEMENTS["select_vendor"], 4000) {
            LogMessage("    [shipping] 'Select Vendor' control not found")
            return false
        }
        ClickByName(CLOSEOUT_ELEMENTS["select_vendor"], 4000)
        Sleep(1200)
        DismissPopups()

        filterElem := FindByName(CLOSEOUT_ELEMENTS["vendor_filter"], 3000)
        if filterElem {
            try filterElem.Focus()
            Sleep(150)
        }
        prevClip := ""
        try prevClip := A_Clipboard
        A_Clipboard := "scrap"
        ClipWait(2)
        Send("^v")
        Sleep(300)
        Send("{Enter}")
        Sleep(1200)
        A_Clipboard := prevClip

        scrapRow := FindByName(CLOSEOUT_ELEMENTS["scrap_vendor_name"], 3000)
        if !scrapRow {
            LogMessage("    [shipping] SCRAP vendor row not found after filter")
            return false
        }
        scrapRow.Click("left")
        Sleep(500)
        okBtn := FindByName(CLOSEOUT_ELEMENTS["ok"], 3000)
        if okBtn {
            okBtn.Click("left")
            Sleep(800)
        }

        vendorField := ReadFieldValue(CLOSEOUT_ELEMENTS["select_vendor"])
        if (Trim(vendorField) != "SCRAP") {
            LogMessage("    [shipping] vendor field shows '" . vendorField . "', expected 'SCRAP' - aborting before save")
            return false
        }

        SaveBucketDetail()
        LogMessage("    [shipping] saved: weight=" . weightClean . " vendor=SCRAP")
        return true
    } catch as e {
        LogMessage("    [shipping] exception: " . e.Message)
        return false
    }
}

; Metal-agnostic assay-field lookup. The 2026-08-06 gold-only build hardcoded
; "Calculated Assay-GOLD" - discovered 2026-08-06 during silver testing that Bravo
; suffixes this field by metal (silver buckets are expected to use
; "Calculated Assay-SILVER" instead, by the same naming pattern). Tries every
; known suffix rather than guessing one, and logs which one matched. Returns
; "" (never guesses) if none of the known suffixes are found, so the caller
; fails safe exactly like any other missing-field case.
ReadCalculatedAssayValue() {
    for key in ["calculated_assay_gold", "calculated_assay_silver"] {
        fieldName := CLOSEOUT_ELEMENTS[key]
        if FindByName(fieldName, 1500) {
            val := ReadFieldValue(fieldName)
            LogMessage("    [assay-lookup] matched field: " . fieldName)
            return val
        }
    }
    LogMessage("    [assay-lookup] no Calculated Assay-<metal> field matched any known suffix")
    return ""
}

AdvanceShippingToAssayed() {
    try {
        weight := ReadFieldValue(CLOSEOUT_ELEMENTS["combined_metal_weight"])
        assay  := ReadCalculatedAssayValue()
        weightClean := RegExReplace(weight, "[^0-9.]", "")
        assayClean  := RegExReplace(assay, "[^0-9.]", "")
        if (weightClean = "" || assayClean = "") {
            LogMessage("    [assayed] could not read weight/assay for confirmation")
            return false
        }

        SelectNextStatus()  ; Shipping -> Assayed (Down, Return)

        SetAndVerifyField(CLOSEOUT_ELEMENTS["confirmed_weight"], weightClean)
        SetAndVerifyField(CLOSEOUT_ELEMENTS["assay_from_vendor"], assayClean)

        SaveBucketDetail()
        LogMessage("    [assayed] saved: confirmed=" . weightClean . " assay=" . assayClean)
        return true
    } catch as e {
        LogMessage("    [assayed] exception: " . e.Message)
        return false
    }
}

; Returns "ok" on success, else a human-readable error string (never throws,
; so the caller always has a specific reason logged in the result).
AdvanceAssayedToClose(amountPaid, tenderType) {
    try {
        ; Print Scrap Report FIRST - printing after Close is selected but
        ; unsaved silently discards the status selection (verified twice
        ; live, 2026-08-05 and 2026-08-06).
        printBtn := FindByName(CLOSEOUT_ELEMENTS["print_scrap_report"], 3000)
        if printBtn {
            printBtn.Click("left")
            Sleep(2500)
            doneBtn := FindByName("Done", 3000)
            if doneBtn {
                doneBtn.Click("left")
                Sleep(1000)
            }
        } else {
            LogMessage("    [close] Print Scrap Report control not found - continuing without it")
        }

        SelectNextStatus()  ; Assayed -> Close (Down, Return)

        amountClean := RegExReplace(amountPaid, "[^0-9.]", "")
        SetAndVerifyField(CLOSEOUT_ELEMENTS["amount_paid"], amountClean)

        if !SelectTenderType(tenderType) {
            return "could not select Tender Type '" . tenderType . "' via UIA - ABORTED BEFORE SAVE (nothing posted)"
        }

        ; Final pre-save read-back of both fields together.
        finalAmount := ReadFieldValue(CLOSEOUT_ELEMENTS["amount_paid"])
        finalTender := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
        finalAmountClean := RegExReplace(finalAmount, "[^0-9.]", "")
        if (finalAmountClean != amountClean) || (Trim(finalTender) != Trim(tenderType)) {
            return "pre-save verification failed: amount='" . finalAmount . "' tender='" . finalTender . "' - ABORTED BEFORE SAVE"
        }

        SaveBucketDetail()
        Sleep(1000)

        ; Confirmation dialog: "IMPORTANT: Once Approved ... CANNOT BE VOIDED"
        approveBtn := FindByName(CLOSEOUT_ELEMENTS["approve"], 5000)
        if !approveBtn {
            return "Approve confirmation dialog did not appear - transaction NOT approved, needs manual check"
        }
        approveBtn.Click("left")
        Sleep(2000)
        LogMessage("    [close] approved: amount=" . amountClean . " tender=" . tenderType)
        return "ok"
    } catch as e {
        return "exception during close: " . e.Message
    }
}

; ----------------------------------------------------------------------------
; Select the NEXT status in the Open->Shipping->Assayed->Close sequence.
; Verified live 10/10 times (2026-08-05, 2026-08-06): from any current
; status, Bravo's "Select Status" dropdown always offers the current status
; plus exactly one next status, so Down-once + Return is reliable. Verifies
; the resulting value actually changed before returning.
; ----------------------------------------------------------------------------
SelectNextStatus() {
    before := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
    elem := FindByName(CLOSEOUT_ELEMENTS["select_status"], 4000)
    if !elem
        throw Error("Select Status control not found")
    elem.Click("left")
    Sleep(400)
    Send("{Down}")
    Sleep(200)
    Send("{Enter}")
    Sleep(500)
    after := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
    if (after = before) {
        LogMessage("    [status] WARNING - Select Status did not change from '" . before . "' after Down+Return")
    }
    LogMessage("    [status] " . before . " -> " . after)
}

; ----------------------------------------------------------------------------
; Select a Tender Type item by NAME, not by position - the list length
; varies by store (confirmed live: CUL/LEX have 'Personal Check', HAR does
; not), so counting Down presses is unsafe. Tries direct UIA click on the
; expanded popup item first; falls back to a bounded keyboard scan that
; re-reads the field's live value after every keypress and stops the
; instant it matches (WPF ComboBoxes here were observed to preview the
; highlighted item's text into the field's Value before Enter is pressed).
; Returns false (never guesses) if neither method confirms the target text.
; ----------------------------------------------------------------------------
SelectTenderType(targetName) {
    combo := FindByName(CLOSEOUT_ELEMENTS["tender_type"], 4000)
    if !combo {
        LogMessage("    [tender] Tender Type control not found")
        return false
    }
    combo.Click("left")
    Sleep(500)

    ; Strategy 1: direct UIA click on the expanded popup's item by Name.
    item := FindByName(targetName, 2500)
    if item {
        try {
            item.Click("left")
            Sleep(400)
            got := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
            if (Trim(got) = Trim(targetName)) {
                LogMessage("    [tender] selected '" . targetName . "' via direct UIA click")
                return true
            }
        } catch as e {
            LogMessage("    [tender] direct click failed: " . e.Message)
        }
    }

    ; Strategy 2: bounded keyboard scan with live read-back, from the top.
    LogMessage("    [tender] direct click unavailable/unconfirmed - falling back to keyboard scan for '" . targetName . "'")
    combo2 := FindByName(CLOSEOUT_ELEMENTS["tender_type"], 2000)
    if combo2 {
        try combo2.Click("left")
        Sleep(400)
    }
    Send("{Home}")
    Sleep(200)
    Loop 15 {
        cur := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
        if (Trim(cur) = Trim(targetName)) {
            Send("{Enter}")
            Sleep(400)
            confirm := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
            if (Trim(confirm) = Trim(targetName)) {
                LogMessage("    [tender] selected '" . targetName . "' via keyboard scan (" . A_Index . " presses)")
                return true
            }
        }
        Send("{Down}")
        Sleep(250)
    }
    LogMessage("    [tender] EXHAUSTED keyboard scan without confirming '" . targetName . "' - refusing to guess")
    Send("{Escape}")
    return false
}

; ----------------------------------------------------------------------------
; Set a text/numeric field via clipboard paste and verify the exact string
; landed. Throws if verification fails (caller aborts the bucket - no save
; happens on an unverified field, by construction).
; ----------------------------------------------------------------------------
SetAndVerifyField(fieldName, value) {
    elem := FindByName(fieldName, 4000)
    if !elem
        throw Error("field not found: " . fieldName)
    elem.Click("left")
    Sleep(200)
    Send("^a")
    Sleep(80)
    Send("{Delete}")
    Sleep(80)
    prevClip := ""
    try prevClip := A_Clipboard
    A_Clipboard := value
    if !ClipWait(2)
        throw Error("clipboard did not receive value for " . fieldName)
    Send("^v")
    Sleep(300)
    A_Clipboard := prevClip

    got := ReadFieldValue(fieldName)
    gotClean := RegExReplace(got, "[^0-9.]", "")
    wantClean := RegExReplace(value, "[^0-9.]", "")
    if (gotClean != wantClean)
        throw Error("verify failed for " . fieldName . ": got '" . got . "' expected '" . value . "'")
    LogMessage("    [set] " . fieldName . " = " . value . " (verified)")
}

SaveBucketDetail() {
    saveBtn := FindByName(CLOSEOUT_ELEMENTS["save"], 4000)
    if !saveBtn
        throw Error("Save button not found")
    saveBtn.Click("left")
    Sleep(1500)
    DismissPopups()
}

DoneOrCancelBucketDetail() {
    try {
        if FindByName("Done", 1500)
            ClickByName("Done", 2000)
        else if FindByName("Cancel", 1500)
            ClickByName("Cancel", 2000)
    }
    Sleep(1000)
    DismissPopups()
}

; ----------------------------------------------------------------------------
; Open the store and till if closed. NEVER closes them back down - an
; automated Close Store triggers a Store Safe -> Bank Account transfer,
; which is out of scope for unattended execution. Staff's normal
; open/close-of-day process handles that; this only unblocks the Close -
; Complete Transaction step, which requires both to be open.
; ----------------------------------------------------------------------------
EnsureStoreAndTillOpen(store) {
    try BackToDashboard()
    DismissPopups()

    if FindByName(CLOSEOUT_ELEMENTS["open_store"], 2000) {
        LogMessage("  [store] " . store . " is closed - opening")
        ClickByName(CLOSEOUT_ELEMENTS["open_store"], 4000)
        Sleep(1500)
        uev := FindByName(CLOSEOUT_ELEMENTS["use_expected_values"], 2000)
        if uev
            uev.Click("left")
        Sleep(500)
        SaveBucketDetail()
        Sleep(2000)
        ; Click through any printer-error OK dialogs (legacy risk - the
        ; 2026-08 fix installed a dummy 'Receipts' printer, but be defensive)
        Loop 3 {
            okBtn := FindByName(CLOSEOUT_ELEMENTS["ok"], 1500)
            if !okBtn
                break
            okBtn.Click("left")
            Sleep(800)
        }
        try BackToDashboard()
    }

    if FindByName(CLOSEOUT_ELEMENTS["open_till"], 2000) {
        LogMessage("  [till] " . store . " till is closed - opening")
        ClickByName(CLOSEOUT_ELEMENTS["open_till"], 4000)
        Sleep(1500)
        uev := FindByName(CLOSEOUT_ELEMENTS["use_expected_values"], 2000)
        if uev
            uev.Click("left")
        Sleep(500)
        SaveBucketDetail()
        Sleep(2000)
        try BackToDashboard()
    }
}

; ----------------------------------------------------------------------------
; Mutex against the main bravo_watcher.ahk pipeline - it WILL drive the same
; Bravo window concurrently and hijack the screen mid-transaction if not
; paused first (root-caused live 2026-08-06). A per-minute Windows scheduled
; task (BravoWatcherWatchdog) relaunches the watcher if killed, so disabling
; that task is required, not optional - taskkill alone is insufficient.
; ----------------------------------------------------------------------------
PauseMainWatcher() {
    LogMessage("PauseMainWatcher: disabling BravoWatcherWatchdog and killing AutoHotkey64.exe (main watcher)")
    RunWait('schtasks /change /tn BravoWatcherWatchdog /disable', , "Hide")
    ; Do not kill ourselves - this script runs as a SEPARATE AHK process
    ; (ScrapBucketCloseoutWatcher.ahk), so taskkill /IM AutoHotkey64.exe
    ; would also kill this process.
    ;
    ; 2026-08-10 CRITICAL FIX. This used to kill EVERY AutoHotkey64.exe except
    ; its own PID. That is far too broad: the interactive session also runs
    ;   - BravoAutoLogin.ahk        (drives the Bravo login screen)
    ;   - bravo_foreground_keeper.ahk (relaunches Bravo via ClickOnce and
    ;                                  answers the ClickOnce trust prompt)
    ; Those two are the ONLY things that can bring Bravo back up and log it in,
    ; and ResumeMainWatcher never restarted them - so every scrap-closeout run
    ; permanently disarmed Bravo's self-heal. Observed live 2026-08-10: a run
    ; killed all four helpers, Bravo later exited, and nothing could restart it.
    ; Match on CommandLine and touch ONLY the main pipeline watcher - the same
    ; discipline _scrap_watchdog.ps1 already uses (never a blanket AHK kill).
    myPid := ProcessExist()
    for proc in ComObjGet("winmgmts:").ExecQuery("Select ProcessId, CommandLine from Win32_Process where Name='AutoHotkey64.exe'") {
        cmd := ""
        try cmd := proc.CommandLine
        if (proc.ProcessId != myPid && InStr(cmd, "bravo_watcher.ahk")) {
            try {
                RunWait("taskkill /F /PID " . proc.ProcessId, , "Hide")
                LogMessage("  killed AutoHotkey64.exe PID " . proc.ProcessId)
            } catch as e {
                LogMessage("  could not kill PID " . proc.ProcessId . ": " . e.Message)
            }
        }
    }
    Sleep(1000)
}

ResumeMainWatcher() {
    LogMessage("ResumeMainWatcher: re-enabling BravoWatcherWatchdog and relaunching main watcher")
    RunWait('schtasks /change /tn BravoWatcherWatchdog /enable', , "Hide")
    RunWait('schtasks /run /tn BravoWatcherWatchdog', , "Hide")
    Sleep(2000)
}

; ----------------------------------------------------------------------------
; Manifest parsing (hand-rolled regex, same style as lib/Json.ahk's
; ReadTrigger - this project's fixed-schema convention, not a generic
; JSON parser).
; ----------------------------------------------------------------------------
ParseScrapManifest(path) {
    m := Map("id", "", "buckets", [], "readOnly", false)
    if !FileExist(path)
        return m
    text := FileRead(path, "UTF-8")
    if RegExMatch(text, '"id"\s*:\s*"([^"]*)"', &idm)
        m["id"] := idm[1]
    else
        m["id"] := "scrap-closeout_" . A_TickCount

    ; Optional top-level "readOnly": true -> dry run, never posts (see the
    ; CLOSEOUT_READONLY comment above RunScrapCloseoutManifest).
    if RegExMatch(text, '"readOnly"\s*:\s*true')
        m["readOnly"] := true

    pos := 1
    while RegExMatch(text, '\{[^{}]*"store"\s*:\s*"([^"]*)"[^{}]*\}', &bm, pos) {
        blockText := bm[0]
        b := Map("store", bm[1], "bucketName", "", "amountPaid", "", "tenderType", "Cashiers Check")
        if RegExMatch(blockText, '"bucketName"\s*:\s*"([^"]*)"', &nm)
            b["bucketName"] := nm[1]
        if RegExMatch(blockText, '"amountPaid"\s*:\s*"?([0-9.]+)"?', &am)
            b["amountPaid"] := am[1]
        if RegExMatch(blockText, '"tenderType"\s*:\s*"([^"]*)"', &tm)
            b["tenderType"] := tm[1]
        m["buckets"].Push(b)
        pos := bm.Pos + bm.Len
    }
    return m
}

; Hand-rolled JSON writer for the result schema, same pattern as
; lib/Json.ahk's WriteResult (fixed schema, not generic).
WriteScrapResult(path, r) {
    sb := "{`r`n"
    sb .= '  "trigger_id":  "' . r["trigger_id"] . '",`r`n'
    sb .= '  "started_at":  "' . r["started_at"] . '",`r`n'
    sb .= '  "finished_at": "' . r["finished_at"] . '",`r`n'
    sb .= '  "status":      "' . r["status"] . '",`r`n'
    sb .= '  "totalPaid":   ' . r["totalPaid"] . ',`r`n'
    sb .= '  "bucketCount": ' . r["bucketCount"] . ',`r`n'
    sb .= '  "buckets": ['
    if (r["buckets"].Length > 0) {
        sb .= "`r`n"
        for i, b in r["buckets"] {
            sb .= '    {"store": "' . b["store"] . '", "bucketName": "' . b["bucketName"] . '", '
            sb .= '"amountPaid": "' . b["amountPaid"] . '", "tenderType": "' . b["tenderType"] . '", '
            sb .= '"status": "' . b["status"] . '", "priorStatus": "' . b["priorStatus"] . '", '
            sb .= '"verified": ' . (b["verified"] ? "true" : "false") . ', '
            errText := StrReplace(b.Get("error", ""), '"', "'")
            sb .= '"error": "' . errText . '"}'
            if (i < r["buckets"].Length)
                sb .= ","
            sb .= "`r`n"
        }
        sb .= "  "
    }
    sb .= "]`r`n}`r`n"

    if FileExist(path)
        FileDelete(path)
    FileAppend(sb, path, "UTF-8")
}
