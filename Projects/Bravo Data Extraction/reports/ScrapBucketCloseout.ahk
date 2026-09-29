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
    if manifest["listOnly"]
        return ListOpenBucketsOnly(manifest, result)

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

            ; 2026-09-28: a read-only dry run must not open the store/till either -
            ; that Save is a real write (and staff open their own tills at 10 AM).
            if !CLOSEOUT_READONLY
                EnsureStoreAndTillOpen(store)

            for b in byStore[store] {
                bucketResult := CloseoutOneBucket(store, b["bucketName"], b["amountPaid"], b["tenderType"], b["occurrence"], b["expectedWeightDwt"])
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
CloseoutOneBucket(store, bucketName, amountPaid, tenderType, occurrence := 0, expectedWeightDwt := "") {
    global CLOSEOUT_READONLY, CLOSEOUT_OCCURRENCE
    CLOSEOUT_OCCURRENCE := occurrence
    out := Map(
        "store", store, "bucketName", bucketName,
        "amountPaid", amountPaid, "tenderType", tenderType,
        "status", "error", "priorStatus", "", "verified", false, "error", ""
    )

    LogMessage("  --- bucket '" . bucketName . "' (" . store . ") ---")

    rawStatus := OpenBucketAndReadStatus(bucketName)
    ; 2026-09-28 (live-all, HAR): a same-named NEWER bucket can drop out of the
    ; list between the approval read and the posting run (e.g. staff move the
    ; September bucket to Shipping, which the list view hides), so the target
    ; occurrence index shifts down by one. Fall back one occurrence at a time -
    ; the weight gate below is what proves the right bucket is open, not the index.
    while (rawStatus = "" && CLOSEOUT_OCCURRENCE > 0) {
        CLOSEOUT_OCCURRENCE -= 1
        LogMessage("    [open] not found at occurrence " . (CLOSEOUT_OCCURRENCE + 1) . " - retrying at occurrence " . CLOSEOUT_OCCURRENCE . " (weight gate will decide)")
        rawStatus := OpenBucketAndReadStatus(bucketName)
    }
    if (rawStatus = "") {
        out["error"] := "could not locate/open bucket '" . bucketName . "'"
        LogMessage("    " . out["error"])
        return out
    }
    status := NormalizeStatus(rawStatus)
    RecordStatusCode(rawStatus, "initial")
    out["priorStatus"] := status
    LogMessage("    current status: " . status . " (raw '" . rawStatus . "') occurrence=" . CLOSEOUT_OCCURRENCE)

    ; Weight gate (2026-09-28): the approved split is only valid for the bucket
    ; it was computed from. Read the live weight and refuse to touch the bucket
    ; if it differs from the manifest's expectedWeightDwt.
    liveWeight := ReadFieldValue(CLOSEOUT_ELEMENTS["combined_metal_weight"])
    liveClean := RegExReplace(liveWeight, "[^0-9.]", "")
    out["liveWeightDwt"] := liveClean
    if (expectedWeightDwt != "") {
        if (liveClean = "") {
            out["error"] := "could not read Combined Metal Weight to check against expected " . expectedWeightDwt . " dwt - nothing touched"
            LogMessage("    " . out["error"])
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            return out
        }
        if (Abs(Float(liveClean) - Float(expectedWeightDwt)) > 0.05) {
            out["error"] := "WEIGHT MISMATCH - bucket shows " . liveClean . " dwt, approved split expects " . expectedWeightDwt . " dwt - nothing touched (wrong bucket, or bucket changed since approval)"
            LogMessage("    " . out["error"])
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            return out
        }
        LogMessage("    weight gate OK: live " . liveClean . " dwt vs expected " . expectedWeightDwt . " dwt")
    }

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
        ; 2026-09-28: dump every named element on the detail screen so the exact
        ; field labels for the later stages can be confirmed from a real screen.
        try LogVisibleNames(150)
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
        ; numeric compare - Bravo shows 4 decimals ('11706.2500'), verified live 2026-09-28
        out["verified"] := (postedClean != "" && Abs(Float(postedClean) - Float(expectClean)) < 0.005)
        if !out["verified"]
            out["error"] := "ALREADY CLOSED but amount mismatch: bucket shows " . posted . ", manifest expects $" . amountPaid
        LogMessage("    already closed - posted=" . posted . " expected=" . amountPaid . " verified=" . out["verified"])
        return out
    }

    ; --- Transition-driven state machine (2026-09-28) ------------------------
    ; stage = where we believe the bucket is. It starts from the translated
    ; status and advances only after a pass SAVES successfully. Each pass proves
    ; the screen it is on by finding its own fields (missing field -> throw ->
    ; pass returns false -> bucket aborted with nothing posted). Unknown status
    ; codes are logged and learned (see RecordStatusCode), never guessed.
    if InStr(status, "Open")
        stage := "Open"
    else if InStr(status, "Shipping")
        stage := "Shipping"
    else if (InStr(status, "Received") || InStr(status, "Assayed"))
        stage := "Assayed"
    else {
        out["error"] := "unknown starting status '" . rawStatus . "' - not in the code map yet, nothing touched"
        LogMessage("    " . out["error"])
        DoneOrCancelBucketDetail()
        try BackToDashboard()
        return out
    }

    ; --- Open -> Shipping ---------------------------------------------------
    if (stage = "Open") {
        if !AdvanceOpenToShipping() {
            out["error"] := "Open->Shipping pass failed"
            DoneOrCancelBucketDetail()
            ; See 2026-08-06 comment above (already-closed branch) - answer
            ; the Cancel-confirmation dialog so Bravo is not left stuck.
            try BackToDashboard()
            return out
        }
        stage := "Shipping"
        rawStatus := OpenBucketAndReadStatus(bucketName)
        if (rawStatus = "") {
            out["error"] := "lost bucket after Shipping save"
            return out
        }
        RecordStatusCode(rawStatus, "after-shipping-save")
        LogMessage("    status after Shipping save: " . NormalizeStatus(rawStatus) . " (raw '" . rawStatus . "')")
    }

    ; --- Shipping -> Received (Bravo shows it as Assayed once saved) ---------
    if (stage = "Shipping") {
        if !AdvanceShippingToAssayed() {
            out["error"] := "Shipping->Assayed pass failed"
            DoneOrCancelBucketDetail()
            try BackToDashboard()
            return out
        }
        stage := "Assayed"
        rawStatus := OpenBucketAndReadStatus(bucketName)
        if (rawStatus = "") {
            out["error"] := "lost bucket after Assayed save"
            return out
        }
        RecordStatusCode(rawStatus, "after-received-save")
        LogMessage("    status after Received save: " . NormalizeStatus(rawStatus) . " (raw '" . rawStatus . "')")
    }

    ; --- Assayed -> Close ------------------------------------------------
    tenderCode := ""
    closeOutcome := AdvanceAssayedToClose(amountPaid, tenderType, &tenderCode)
    if (closeOutcome != "ok") {
        out["error"] := closeOutcome
        DoneOrCancelBucketDetail()
        try BackToDashboard()
        return out
    }

    ; --- Post-approve verification: reopen and read back the locked record --
    ; Live 2026-09-28 (live-1g): after Approve, Bravo is still on a post-save
    ; screen (Done buttons, then the Overdue Task Reminder) - get back to the
    ; Dashboard FIRST, then reopen the bucket for the read-back.
    Sleep(1500)
    Loop 4 {
        DismissPopups()
        okBtn := FindByName(CLOSEOUT_ELEMENTS["ok"], 1000)
        if !okBtn
            break
        okBtn.Click("left")
        Sleep(800)
    }
    try DoneOrCancelBucketDetail()
    try BackToDashboard()
    DismissPopups()
    Sleep(1000)
    verifyRaw := OpenBucketAndReadStatus(bucketName)
    RecordStatusCode(verifyRaw, "after-close-approve")
    verifyStatus := NormalizeStatus(verifyRaw)
    postedAmount := ReadFieldValue(CLOSEOUT_ELEMENTS["amount_paid"])
    postedTender := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
    DoneOrCancelBucketDetail()
    try BackToDashboard()

    postedClean := RegExReplace(postedAmount, "[^0-9.]", "")
    expectClean := RegExReplace(amountPaid, "[^0-9.]", "")
    amountOk := (postedClean != "" && Abs(Float(postedClean) - Float(expectClean)) < 0.005)
    ; Tender reads back as the same UIA value it showed right after we picked
    ; it from the list by display name (a code or the name - either way it must
    ; be identical to what we saw before Save).
    tenderOk := (Trim(postedTender) = Trim(tenderCode)) || (Trim(postedTender) = Trim(tenderType))

    LogMessage("    post-approve read-back: status=" . verifyStatus . " (raw '" . verifyRaw . "') amount='" . postedAmount . "' tender='" . postedTender . "'")
    out["status"]   := "closed"
    out["verified"] := amountOk && tenderOk
    if !out["verified"] {
        out["error"] := "CRITICAL POST-SAVE MISMATCH - posted amount='" . postedAmount . "' (expected $" . amountPaid . "), posted tender='" . postedTender . "' (expected '" . tenderType . "' / code '" . tenderCode . "'). Transaction CANNOT be voided - flag for manual review."
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

global CLOSEOUT_OCCURRENCE := 0

OpenBucketAndReadStatus(bucketName) {
    global CLOSEOUT_OCCURRENCE
    Loop 3 {
        try {
            if !ScrapCloseoutOpenBucketList() {
                LogMessage("    [open] could not open filtered bucket list")
                continue
            }
        } catch as e {
            LogMessage("    [open] ScrapOpenFilteredBucketList error: " . e.Message)
            continue
        }
        if !ScrapRelocateAndOpenBucket(bucketName, CLOSEOUT_OCCURRENCE) {
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
        ; 2026-09-28: the row click often does not register on the first try
        ; (verify reports foundLabel=no = no detail screen at all). The list is
        ; still on screen, so just click the row again instead of backing all
        ; the way out to the Dashboard (saves ~1 min per miss).
        Loop 2 {
            if FindByName("Bucket Name", 800)
                break
            LogMessage("    [open] detail screen not open after row click - re-clicking (" . A_Index . "/2)")
            if !ScrapRelocateAndOpenBucket(bucketName, CLOSEOUT_OCCURRENCE)
                break
            Sleep(2500)
        }
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
            if !ScrapIsEditorControl(e)
                continue
            val := ""
            try val := e.Value
            if (val != "" && val != labelText && !InStr(val, "(Detached)"))
                return val
        }
        return ""
    } catch as e {
        LogMessage("    [read-after-label] '" . labelText . "' error: " . e.Message)
        return ""
    }
}

; 2026-09-28: Bravo's editor controls expose their CLASS as the UIA Name
; (dry-run dumps: BravoMaskedTextBox, BravoComboBox, SpinEdit, BravoSpinEdit,
; TextEdit, ButtonEdit, PopupBaseEdit, LookUpEdit). Buttons such as
; 'ZTI.Bravo.SharedViews.Views.DataLink' sit between labels and carry junk
; Values ('Receiving: 0000... (Detached)') - the sibling walk must skip them.
ScrapIsEditorControl(e) {
    nm := ""
    try nm := e.Name
    for cls in ["BravoMaskedTextBox", "BravoComboBox", "SpinEdit", "BravoSpinEdit", "TextEdit", "ButtonEdit", "PopupBaseEdit", "LookUpEdit", "MaskedTextBox", "ComboBox"]
        if (nm = cls)
            return true
    return false
}

ReadFieldValue(fieldName) {
    ; Proven sibling-walk ONLY. 2026-09-28 dry run: the old GetValueByName
    ; fallback returned junk ('Receiving: 0000...-0000 (Detached)') for fields
    ; that are simply not on screen in the current status (Amount Paid /
    ; Tender Type while a bucket is still Open). A field that is not on screen
    ; must read as "" so every caller's "could not read" guard fires honestly.
    return ScrapReadValueAfterLabel(fieldName)
}

; ----------------------------------------------------------------------------
; Status handling (2026-09-28). Bravo's "Select Status" combobox exposes only an
; INTERNAL CODE through UIA (dry run 2026-09-28: every Open bucket read
; 'SBKTOP'), never the display text. Known codes are translated here; every code
; observed is also appended to logs-scrap\_status_codes.txt together with the
; stage the state machine believed it was in, so the map grows from real runs.
; The state machine itself is TRANSITION-DRIVEN: after a successful Save the
; next stage is known, and each pass proves it is on the right screen by finding
; and setting that stage's own fields (SetAndVerifyField throws if a field is
; missing). The status code is a cross-check and a log, not the only gate.
; ----------------------------------------------------------------------------
global STATUS_CODE_MAP := Map("SBKTOP", "Open", "OPEN", "Open", "SBKTSH", "Shipping", "SBKTRC", "Received", "SBKTAS", "Assayed", "SBKTCL", "Close")

NormalizeStatus(raw) {
    global STATUS_CODE_MAP
    r := Trim(raw)
    if (r = "")
        return ""
    if STATUS_CODE_MAP.Has(r)
        return STATUS_CODE_MAP[r]
    for w in ["Open", "Shipping", "Received", "Assayed", "Close"] {
        if InStr(r, w)
            return w . " (" . r . ")"
    }
    return r
}

RecordStatusCode(code, stage) {
    global CONFIG
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`t" . code . "`t" . stage . "`r`n", CONFIG["paths.logs"] . "\_status_codes.txt", "UTF-8")
}

; Learned tender-type code map (display name -> UIA code), same idea.
global TENDER_CODE_MAP := Map()

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

        weightClean := SetNumericFieldWithPrecision(CLOSEOUT_ELEMENTS["total_weight_shipped"], weightClean, 2)

        ; --- Select vendor "SCRAP" (rewritten 2026-09-28 from the live-1 run) ---
        ; The vendor picker is opened by the BUTTON named 'Select Vendor' (a Text
        ; label of the same name sits right next to it - FindByName hit the label
        ; and nothing opened). The picker may be its own top-level Bravo window,
        ; so every lookup below searches ALL Bravo.exe windows.
        if !ScrapSelectScrapVendor()
            return false
        Sleep(600)
        vendorField := ReadFieldValue(CLOSEOUT_ELEMENTS["select_vendor"])
        if !InStr(vendorField, "SCRAP") {
            LogMessage("    [shipping] vendor field shows '" . vendorField . "', expected it to contain 'SCRAP' - aborting before save")
            try LogVisibleNames(80)
            return false
        }
        LogMessage("    [shipping] vendor field = '" . vendorField . "'")

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

        weightClean := SetNumericFieldWithPrecision(CLOSEOUT_ELEMENTS["confirmed_weight"], weightClean, 2)
        assayClean  := SetNumericFieldWithPrecision(CLOSEOUT_ELEMENTS["assay_from_vendor"], assayClean, 3)

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
; tenderCodeOut receives the UIA read-back of Tender Type right after the
; list item named tenderType was clicked (Bravo comboboxes expose codes, not
; display text - see NormalizeStatus) so the post-approve check can compare
; like with like.
AdvanceAssayedToClose(amountPaid, tenderType, &tenderCodeOut) {
    global CLOSEOUT_PRINT_REPORT
    tenderCodeOut := ""
    try {
        ; Print Scrap Report is informational (estimate vs actual). 2026-09-28:
        ; OFF by default for the native path - a "Done" click meant for the
        ; report preview could land on the bucket detail's own Done button and
        ; silently leave the screen. The money is decided by the manifest, not
        ; by the report. Flip CLOSEOUT_PRINT_REPORT to re-enable.
        if CLOSEOUT_PRINT_REPORT {
            printBtn := FindByName(CLOSEOUT_ELEMENTS["print_scrap_report"], 3000)
            if printBtn {
                printBtn.Click("left")
                Sleep(2500)
                doneBtn := FindByName("Done", 3000)
                if doneBtn {
                    doneBtn.Click("left")
                    Sleep(1000)
                }
            }
        }

        SelectNextStatus()  ; Assayed -> Close (Down, Return)

        ; The Close screen must expose Amount Paid + Tender Type. If either is
        ; missing we are NOT on the Close screen - stop before touching anything.
        if !FindByName(CLOSEOUT_ELEMENTS["amount_paid"], 4000)
            return "Amount Paid field not on screen after selecting Close status - ABORTED BEFORE SAVE (nothing posted)"
        if !FindByName(CLOSEOUT_ELEMENTS["tender_type"], 2000)
            return "Tender Type field not on screen after selecting Close status - ABORTED BEFORE SAVE (nothing posted)"

        amountClean := RegExReplace(amountPaid, "[^0-9.]", "")
        SetAndVerifyField(CLOSEOUT_ELEMENTS["amount_paid"], amountClean)

        code := SelectTenderType(tenderType)
        if (code = "")
            return "could not select Tender Type '" . tenderType . "' via UIA - ABORTED BEFORE SAVE (nothing posted)"
        tenderCodeOut := code

        ; Final pre-save read-back of both fields together.
        finalAmount := ReadFieldValue(CLOSEOUT_ELEMENTS["amount_paid"])
        finalTender := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
        finalAmountClean := RegExReplace(finalAmount, "[^0-9.]", "")
        if (finalAmountClean != amountClean) || (Trim(finalTender) != Trim(code)) {
            return "pre-save verification failed: amount='" . finalAmount . "' (want " . amountClean . ") tender='" . finalTender . "' (want '" . code . "') - ABORTED BEFORE SAVE"
        }
        LogMessage("    [close] pre-save verified: amount=" . finalAmount . " tender='" . finalTender . "' -> saving")

        SaveBucketDetail()
        Sleep(1000)

        ; Confirmation dialog: "IMPORTANT: Once Approved ... CANNOT BE VOIDED"
        approveBtn := FindByName(CLOSEOUT_ELEMENTS["approve"], 8000)
        if !approveBtn {
            return "Approve confirmation dialog did not appear - transaction NOT approved, needs manual check"
        }
        approveBtn.Click("left")
        Sleep(2500)
        ; Receipt-printer error ("Printer 'Receipts' does not exist") follows
        ; most saves - click Ok through it, harmless (BRAVO_BUCKET_CLOSEOUT.md).
        Loop 4 {
            DismissPopups()
            okBtn := FindByName(CLOSEOUT_ELEMENTS["ok"], 1200)
            if !okBtn
                break
            okBtn.Click("left")
            Sleep(800)
        }
        LogMessage("    [close] approved: amount=" . amountClean . " tender=" . tenderType . " (code '" . code . "')")
        return "ok"
    } catch as e {
        return "exception during close: " . e.Message
    }
}

global CLOSEOUT_PRINT_REPORT := false

; ----------------------------------------------------------------------------
; Select the NEXT status in the Open->Shipping->Assayed->Close sequence.
; Verified live 10/10 times (2026-08-05, 2026-08-06): from any current
; status, Bravo's "Select Status" dropdown always offers the current status
; plus exactly one next status, so Down-once + Return is reliable. Verifies
; the resulting value actually changed before returning (values are UIA
; codes - equality/inequality is all that matters here).
; ----------------------------------------------------------------------------
SelectNextStatus() {
    before := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
    if !FindByName(CLOSEOUT_ELEMENTS["select_status"], 4000)
        throw Error("Select Status control not found")
    elem := ScrapFindValueElementAfterLabel(CLOSEOUT_ELEMENTS["select_status"])
    if !elem
        elem := FindByName(CLOSEOUT_ELEMENTS["select_status"], 1000)
    elem.Click("left")
    Sleep(400)
    Send("{Down}")
    Sleep(200)
    Send("{Enter}")
    Sleep(700)
    after := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
    if (after = before) {
        ; One retry: the label click may have focused the label, not the box.
        LogMessage("    [status] Select Status did not change from '" . before . "' - retrying via the value box")
        box := ScrapFindValueElementAfterLabel(CLOSEOUT_ELEMENTS["select_status"])
        if box {
            box.Click("left")
            Sleep(400)
            Send("{Down}")
            Sleep(200)
            Send("{Enter}")
            Sleep(700)
            after := ReadFieldValue(CLOSEOUT_ELEMENTS["select_status"])
        }
    }
    if (after = before)
        throw Error("Select Status did not change from '" . before . "' after Down+Return")
    RecordStatusCode(after, "after-select-next")
    LogMessage("    [status] " . before . " -> " . after)
}

; The value control that follows a label (same sibling walk as
; ScrapReadValueAfterLabel, but returns the element instead of its value).
ScrapFindValueElementAfterLabel(labelText) {
    try {
        root := GetBravoRoot()
        allEl := root.FindElements({})
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
            if !ScrapIsEditorControl(e)
                continue
            return e
        }
    }
    return 0
}

; ----------------------------------------------------------------------------
; Select a Tender Type item by NAME, not by position - the list length
; varies by store (confirmed live: CUL/LEX have 'Personal Check', HAR does
; not), so counting Down presses is unsafe. The expanded popup's items ARE
; named by display text, so a direct UIA click on the item named exactly
; targetName selects that item. The field then reads back as Bravo's own UIA
; value for it (a code, or the name) - that read-back is returned so the
; caller can verify before Save and again after Approve against the SAME
; value. Returns "" (never guesses) if the item cannot be clicked or the
; field did not change.
; ----------------------------------------------------------------------------
SelectTenderType(targetName) {
    global TENDER_CODE_MAP, CONFIG
    before := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
    if !FindByName(CLOSEOUT_ELEMENTS["tender_type"], 4000) {
        LogMessage("    [tender] Tender Type control not found")
        return ""
    }
    combo := ScrapFindValueElementAfterLabel(CLOSEOUT_ELEMENTS["tender_type"])
    if !combo
        combo := FindByName(CLOSEOUT_ELEMENTS["tender_type"], 1000)
    combo.Click("left")
    Sleep(600)
    item := FindByName(targetName, 2500)
    if !item {
        ; Some WPF combos open on a second click / need the dropdown button.
        combo.Click("left")
        Sleep(600)
        item := FindByName(targetName, 2500)
    }
    if !item {
        LogMessage("    [tender] popup item '" . targetName . "' not found - dumping names")
        try LogVisibleNames(60)
        Send("{Escape}")
        return ""
    }
    try {
        item.Click("left")
    } catch as e {
        LogMessage("    [tender] click on '" . targetName . "' failed: " . e.Message)
        Send("{Escape}")
        return ""
    }
    Sleep(600)
    got := ReadFieldValue(CLOSEOUT_ELEMENTS["tender_type"])
    if (got = "" || got = before) {
        LogMessage("    [tender] field did not change after clicking '" . targetName . "' (before='" . before . "' after='" . got . "') - refusing")
        return ""
    }
    if TENDER_CODE_MAP.Has(targetName) && (TENDER_CODE_MAP[targetName] != Trim(got)) {
        LogMessage("    [tender] read-back '" . got . "' does not match the learned code '" . TENDER_CODE_MAP[targetName] . "' for '" . targetName . "' - refusing")
        return ""
    }
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`t" . targetName . "`t" . got . "`r`n", CONFIG["paths.logs"] . "\_tender_codes.txt", "UTF-8")
    LogMessage("    [tender] selected '" . targetName . "' via UIA item click - field now reads '" . got . "'")
    return Trim(got)
}

; ----------------------------------------------------------------------------
; Set a text/numeric field via clipboard paste and verify the exact string
; landed. Throws if verification fails (caller aborts the bucket - no save
; happens on an unverified field, by construction).
; ----------------------------------------------------------------------------
SetAndVerifyField(fieldName, value) {
    if !FindByName(fieldName, 4000)
        throw Error("field not found: " . fieldName)
    ; 2026-09-28: click the VALUE control (editor right after the label), not
    ; the label - a label click does not reliably focus the editor, and the
    ; paste below goes to whatever has focus.
    elem := ScrapFindValueElementAfterLabel(fieldName)
    if !elem
        throw Error("editor control not found next to label: " . fieldName)
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
    ; 2026-09-28b: compare numerically with a tight tolerance, not as strings -
    ; Bravo sometimes reads back a value with fewer trailing zeros than pasted
    ; (e.g. '0.44' vs '0.440', same number) which is not a real mismatch and
    ; was wrongly aborting the bucket (ROA GOLD WITH STONES, live-all-2 pass).
    okMatch := false
    if (gotClean != "" && wantClean != "") {
        try {
            if (Abs(Float(gotClean) - Float(wantClean)) < 0.0005)
                okMatch := true
        }
    }
    if (!okMatch && gotClean = wantClean)
        okMatch := true
    if (!okMatch)
        throw Error("verify failed for " . fieldName . ": got '" . got . "' expected '" . value . "'")
    LogMessage("    [set] " . fieldName . " = " . value . " (verified)")
}


; Bravo numeric fields keep a fixed number of decimals (live 2026-09-28: weight
; fields 2, assay 3). Paste the value at that precision - truncated first, then
; rounded - and let SetAndVerifyField prove which one Bravo kept.
SetNumericFieldWithPrecision(fieldName, valueStr, decimals) {
    v := Float(valueStr)
    scale := 10 ** decimals
    tTrunc := Format("{:." . decimals . "f}", Floor(v * scale) / scale)
    tRound := Format("{:." . decimals . "f}", Round(v, decimals))
    try {
        SetAndVerifyField(fieldName, tTrunc)
        return tTrunc
    } catch as e1 {
        if (tRound = tTrunc)
            throw e1
        LogMessage("    [set] " . fieldName . " truncated '" . tTrunc . "' did not verify (" . e1.Message . ") - trying rounded '" . tRound . "'")
        SetAndVerifyField(fieldName, tRound)
        return tRound
    }
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
        Sleep(2000)
        DismissPopups()
        ; 2026-08-06 live lesson: select the till (TILL 01) FIRST, then Use
        ; Expected Values - selecting a till can populate a prior close amount,
        ; so UEV must come after the selection, never before.
        tillRow := ScrapFindElementByNamePattern("i)^TILL\s*0*1\b")
        if !tillRow
            tillRow := ScrapFindElementByNamePattern("i)^TILL\s*\d+")
        if tillRow {
            tn := ""
            try tn := tillRow.Name
            LogMessage("  [till] selecting till row '" . tn . "'")
            try tillRow.Click("left")
            Sleep(1200)
        } else {
            LogMessage("  [till] no TILL row found to select - continuing with the default selection")
        }
        uev := FindByName(CLOSEOUT_ELEMENTS["use_expected_values"], 3000)
        if uev
            uev.Click("left")
        else
            LogMessage("  [till] 'Use Expected Values' not found - dumping names")
        if !uev
            try LogVisibleNames(60)
        Sleep(600)
        SaveBucketDetail()
        Sleep(2000)
        Loop 3 {
            okBtn := FindByName(CLOSEOUT_ELEMENTS["ok"], 1500)
            if !okBtn
                break
            okBtn.Click("left")
            Sleep(800)
        }
        try BackToDashboard()
        if FindByName(CLOSEOUT_ELEMENTS["open_till"], 1500)
            LogMessage("  [till] WARNING - 'Open Till' still showing after the open attempt")
        else
            LogMessage("  [till] till open confirmed ('Open Till' no longer on Dashboard)")
    }
}

; First element whose UIA Name matches the regex (document order).
ScrapFindElementByNamePattern(pattern) {
    try {
        root := GetBravoRoot()
        allEl := root.FindElements({})
        for e in allEl {
            nm := ""
            try nm := e.Name
            if (nm != "" && RegExMatch(nm, pattern))
                return e
        }
    }
    return 0
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
    m := Map("id", "", "buckets", [], "readOnly", false, "listOnly", false, "allStatus", false)
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
    ; "listOnly": true -> per store in the manifest, open the Scrap Refining
    ; Process list in its DEFAULT view (Status = OPEN only), walk the grid and
    ; write every open bucket (name, created, status) to
    ; results-scrap\<id>.buckets.csv. Reads nothing else, changes nothing.
    if RegExMatch(text, '"listOnly"\s*:\s*true')
        m["listOnly"] := true
    ; "allStatus": true (paired with listOnly, added 2026-09-28b) -> apply the
    ; full status filter (ScrapApplyAllStatusFilter) before walking the grid,
    ; so buckets sitting in Shipping/Received/Assayed are inventoried too, not
    ; just OPEN. Used to locate HAR's true August buckets across all statuses.
    if RegExMatch(text, '"allStatus"\s*:\s*true')
        m["allStatus"] := true

    pos := 1
    while RegExMatch(text, '\{[^{}]*"store"\s*:\s*"([^"]*)"[^{}]*\}', &bm, pos) {
        blockText := bm[0]
        b := Map("store", bm[1], "bucketName", "", "amountPaid", "", "tenderType", "Cashiers Check", "occurrence", 0, "expectedWeightDwt", "")
        ; "occurrence": which same-named row to open, counting from the top of
        ; the Created-On-descending list (0 = newest). HAR reuses bucket names
        ; month after month (2026-09-28: Sept and Aug buckets both named
        ; 'GOLD W/O STONES'), so the name alone is ambiguous there.
        if RegExMatch(blockText, '"occurrence"\s*:\s*"?(\d+)"?', &om)
            b["occurrence"] := Integer(om[1])
        ; "expectedWeightDwt": the Combined Metal Weight the approved split was
        ; built on. If present, the bucket is only closed when the live weight
        ; matches it (tolerance 0.05 dwt) - proves the right bucket is open AND
        ; that the split still matches what is in it.
        if RegExMatch(blockText, '"expectedWeightDwt"\s*:\s*"?([0-9.]+)"?', &wm)
            b["expectedWeightDwt"] := wm[1]
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
            sb .= '"status": "' . b["status"] . '", "priorStatus": "' . b["priorStatus"] . '", "liveWeightDwt": "' . b.Get("liveWeightDwt", "") . '", '
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


; ----------------------------------------------------------------------------
; listOnly mode (2026-09-28): inventory of OPEN buckets per store, read-only.
; Uses the default Scrap Refining Process view (OPEN only - confirmed in
; ScrapRefiningGold.ahk header) and the proven grid walker. Output:
;   results-scrap\<id>.buckets.csv  ->  Store,BucketName,CreatedOn,Status,StatusDate
; ----------------------------------------------------------------------------
ListOpenBucketsOnly(manifest, result) {
    global CONFIG
    csvPath := CONFIG["paths.scrap_results"] . "\" . manifest["id"] . ".buckets.csv"
    try FileDelete(csvPath)
    FileAppend("Store,BucketName,CreatedOn,Status,StatusDate`r`n", csvPath, "UTF-8")
    stores := []
    seen := Map()
    for b in manifest["buckets"] {
        if !seen.Has(b["store"]) {
            seen[b["store"]] := true
            stores.Push(b["store"])
        }
    }
    overall := "success"
    try {
        PauseMainWatcher()
        for store in stores {
            LogMessage("=== [list-only] Store " . store . " ===")
            if !EnsureStore(store, CONFIG.Get("bravo.password", "")) {
                LogMessage("  [list-only] EnsureStore failed for " . store)
                overall := "partial"
                continue
            }
            try BackToDashboard()
            DismissPopups()
            n := 0
            try {
                LogMessage("  step 1: open Inventory")
                if !FindByName(SCRAP_ELEMENTS["scrap_refining"], 600) {
                    ClickByName(SCRAP_ELEMENTS["sidebar_inventory"], 8000)
                    Sleep(3500)
                    DismissPopups()
                }
                LogMessage("  step 2: click Scrap Refining Process (default OPEN-only view, no CLOSED filter)")
                ClickByName(SCRAP_ELEMENTS["scrap_refining"], 5000)
                Sleep(2500)
                Loop 3 {
                    if !FindByName(SCRAP_ELEMENTS["dialog_ok"], 1200) && FindByName(SCRAP_ELEMENTS["scrap_refining"], 800) {
                        ClickByName(SCRAP_ELEMENTS["scrap_refining"], 5000)
                        Sleep(2000)
                    } else {
                        break
                    }
                }
                ScrapSortByCreatedOnDescending()
                if (manifest.Has("allStatus") && manifest["allStatus"] = true) {
                    LogMessage("  [list-only] allStatus requested - applying full status filter")
                    ScrapApplyAllStatusFilter()
                }
                rows := ScrapWalkBucketGrid(CONFIG["paths.logs"] . "\" . manifest["id"] . "_" . store . "_griddiag.csv")
                for r in rows {
                    n++
                    line := store . "," . ScrapCsvQ(r.name) . "," . ScrapCsvQ(r.createdOn) . "," . ScrapCsvQ(r.status) . "," . ScrapCsvQ(r.statusDate)
                    LogMessage("  [open-bucket] " . line)
                    FileAppend(line . "`r`n", csvPath, "UTF-8")
                }
                LogMessage("  [list-only] " . store . ": " . n . " open bucket row(s)")
            } catch as e {
                LogMessage("  [list-only] error at " . store . ": " . e.Message)
                overall := "partial"
            }
            try DoneOrCancelBucketDetail()
            try BackToDashboard()
            result["buckets"].Push(Map("store", store, "bucketName", "(list-only)", "amountPaid", "", "tenderType", "",
                "status", "listed", "priorStatus", "", "verified", (n > 0), "error", (n > 0 ? "" : "no open buckets read")))
        }
    } catch as e {
        LogMessage("ListOpenBucketsOnly: FATAL - " . e.Message)
        overall := "error"
    } finally {
        ResumeMainWatcher()
    }
    result["status"] := overall
    result["bucketCount"] := result["buckets"].Length
    result["finished_at"] := FormatTime(, "yyyy-MM-dd HH:mm:ss")
    WriteScrapResult(CONFIG["paths.scrap_results"] . "\" . result["trigger_id"] . ".result.json", result)
    LogMessage("ListOpenBucketsOnly: done - " . overall . " -> " . csvPath)
    return result
}

ScrapCsvQ(v) {
    v := StrReplace(v, '"', '""')
    return '"' . v . '"'
}


; ----------------------------------------------------------------------------
; Vendor picker helpers (2026-09-28).
; ----------------------------------------------------------------------------
ScrapBravoRoots() {
    roots := []
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        try roots.Push(UIA.ElementFromHandle(hwnd))
    }
    return roots
}

; Find an element by Name (and optional Type) in ANY Bravo.exe window.
ScrapFindAnyWindow(name, type := "", timeoutMs := 3000) {
    deadline := A_TickCount + timeoutMs
    loop {
        for r in ScrapBravoRoots() {
            el := 0
            try el := (type != "") ? r.FindElement({Type: type, Name: name}) : r.FindElement({Name: name})
            if el
                return el
        }
        if (A_TickCount > deadline)
            return 0
        Sleep(300)
    }
}

ScrapFindAnyWindowPattern(pattern, type := "", timeoutMs := 3000) {
    deadline := A_TickCount + timeoutMs
    loop {
        for r in ScrapBravoRoots() {
            els := 0
            try els := (type != "") ? r.FindElements({Type: type}) : r.FindElements({})
            if els {
                for e in els {
                    nm := ""
                    try nm := e.Name
                    if (nm != "" && RegExMatch(nm, pattern))
                        return e
                }
            }
        }
        if (A_TickCount > deadline)
            return 0
        Sleep(300)
    }
}

ScrapLogAllWindowNames(maxItems := 80) {
    LogMessage("    [diag-all] named elements across all Bravo windows:")
    for r in ScrapBravoRoots() {
        n := 0
        try {
            for e in r.FindElements({}) {
                nm := ""
                try nm := e.Name
                if (nm = "" || RegExMatch(nm, "^[\s0-9$.,%/-]*$"))
                    continue
                lt := ""
                try lt := e.LocalizedType
                LogMessage("    [diag-all] " . lt . ": '" . nm . "'")
                n++
                if (n >= maxItems)
                    break
            }
        }
        LogMessage("    [diag-all] --- end window (" . n . " shown) ---")
    }
}

ScrapSelectScrapVendor() {
    btn := ScrapFindAnyWindow(CLOSEOUT_ELEMENTS["select_vendor"], "Button", 4000)
    if !btn {
        LogMessage("    [shipping] 'Select Vendor' BUTTON not found")
        return false
    }
    btn.Click("left")
    Sleep(1500)
    DismissPopups()

    ; Search box: the editor after the 'E-mail address or business name' label
    ; (BRAVO_BUCKET_CLOSEOUT.md step 7), else a 'Filter'/'Search' named edit.
    box := 0
    lbl := ScrapFindAnyWindowPattern("i)e-?mail address or business name", "", 4000)
    if lbl {
        ; walk that window for the first editor after the label
        for r in ScrapBravoRoots() {
            try {
                found := false, k := 0
                for e in r.FindElements({}) {
                    nm := ""
                    try nm := e.Name
                    if !found {
                        if RegExMatch(nm, "i)e-?mail address or business name")
                            found := true
                        continue
                    }
                    k++
                    if (k > 8)
                        break
                    if ScrapIsEditorControl(e) {
                        box := e
                        break
                    }
                }
            }
            if box
                break
        }
    }
    if !box {
        ; Live 2026-09-28 (screenshot live-1b_vendor-picker.png): the vendor
        ; search panel is inline on the detail screen - a 'Search' button, then
        ; two placeholder-only edits ('Phone #' above, 'E-Mail Address or
        ; Business Name' below). Placeholders are not UIA Names, so take the two
        ; editors that follow the Search button in document order and use the
        ; LOWER one on screen (larger y) - the e-mail/business-name box.
        for r in ScrapBravoRoots() {
            try {
                seenSearch := false, cand := []
                for e in r.FindElements({}) {
                    nm := ""
                    try nm := e.Name
                    if !seenSearch {
                        if (nm = "Search")
                            seenSearch := true
                        continue
                    }
                    if ScrapIsEditorControl(e) {
                        cand.Push(e)
                        if (cand.Length >= 2)
                            break
                    }
                }
                if (cand.Length >= 2) {
                    p1 := cand[1].GetPos("screen"), p2 := cand[2].GetPos("screen")
                    box := (p2.y > p1.y) ? cand[2] : cand[1]
                    LogMessage("    [shipping] search box chosen below 'Search' button (y=" . ((p2.y > p1.y) ? p2.y : p1.y) . ")")
                } else if (cand.Length = 1) {
                    box := cand[1]
                }
            }
            if box
                break
        }
    }
    if !box
        box := ScrapFindAnyWindow("Filter", "Edit", 800)
    if !box {
        LogMessage("    [shipping] vendor search box not found after clicking Select Vendor - dumping all windows")
        ScrapLogAllWindowNames(80)
        try ScreenshotToFile("vendor-picker")
        return false
    }
    box.Click("left")
    Sleep(250)
    prevClip := ""
    try prevClip := A_Clipboard
    A_Clipboard := "scrap"
    ClipWait(2)
    Send("^a")
    Sleep(80)
    Send("^v")
    Sleep(300)
    A_Clipboard := prevClip
    searchBtn := ScrapFindAnyWindow("Search", "Button", 1500)
    if searchBtn
        searchBtn.Click("left")
    else
        Send("{Enter}")
    Sleep(2000)

    ; Diagnostic capture of the search results (2026-09-28: the first live
    ; attempt matched an INVENTORY row 'VP4032052 - SCRAP JEWELRY ...' instead
    ; of the vendor). Dump + screenshot every time until the vendor row's real
    ; UIA shape is known.

    ; the vendor row - exact 'SCRAP' (any case), never 'Scrap List', never an
    ; inventory item ('VP#######  - ...').
    ; Live 2026-09-28 (live-1d dump): the 'Vendors found' grid row is a DataItem
    ; named 'ZTI.Bravo.Customer.Views.Items.CustomerItem' whose Name cell reads
    ; 'Row 1 of 1, Column Name, Column 2 of 5: SCRAP'. Match that cell exactly.
    row := ScrapFindAnyWindowPattern("i)^Row \d+ of \d+, Column Name, Column \d+ of \d+:\s*SCRAP\s*$", "", 3000)
    if !row
        row := ScrapFindAnyWindowPattern("i)^\s*scrap\s*$", "", 1000)
    if !row {
        LogMessage("    [shipping] SCRAP vendor row not found after search - dumping all windows")
        ScrapLogAllWindowNames(80)
        try ScreenshotToFile("vendor-picker-nosrow")
        return false
    }
    rn := ""
    try rn := row.Name
    LogMessage("    [shipping] vendor row '" . rn . "' - selecting")
    try row.Click("left")
    Sleep(600)
    ok := ScrapFindAnyWindow("Ok", "Button", 2500)
    if !ok
        ok := ScrapFindAnyWindow("OK", "Button", 800)
    if !ok
        ok := ScrapFindAnyWindow("Ok", "Text", 800)   ; the Ok button exposes only its Text child
    if ok {
        ok.Click("left")
        Sleep(1000)
    } else {
        LogMessage("    [shipping] no Ok button on the vendor picker - trying double-click on the row")
        try row.Click("left", 2)
        Sleep(1000)
    }
    DismissPopups()
    ; Live 2026-09-28 (live-1e): after Ok the vendor panel stays on screen
    ; showing the chosen vendor ('SCRAP', AutoId textBusinessName) with a
    ; 'Scrap Bucket Detail' button to return to the bucket form. Confirm the
    ; chosen vendor there, then go back.
    chosen := 0
    try chosen := ScrapFindAnyWindowPattern("i)^\s*SCRAP\s*$", "Text", 2000)
    if chosen
        LogMessage("    [shipping] vendor panel shows chosen vendor 'SCRAP'")
    back := ScrapFindAnyWindow("Scrap Bucket Detail", "Button", 2000)
    if back {
        back.Click("left")
        Sleep(1500)
        LogMessage("    [shipping] returned to Scrap Bucket Detail")
    }
    DismissPopups()
    return true
}


; ----------------------------------------------------------------------------
; Bucket list with EVERY status visible (2026-09-28). ScrapApplyClosedFilter
; only adds CLOSED to the default OPEN-only view, so buckets a store has moved
; to Shipping/Received/Assayed vanish from the list (live-all at HAR: both
; same-named buckets disappeared and the occurrence index landed on an old
; closed bucket - caught by the weight gate). Open the funnel, tick every
; status checkbox that is not ticked, log what was there.
; ----------------------------------------------------------------------------
ScrapCloseoutOpenBucketList() {
    LogMessage("  step 1: open Inventory")
    if FindByName(SCRAP_ELEMENTS["scrap_refining"], 600) {
        LogMessage("    already on Inventory panel - skipping sidebar click")
    } else {
        ClickByName(SCRAP_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(3500)
        DismissPopups()
    }
    LogMessage("  step 2: click Scrap Refining Process")
    if !FindByName(SCRAP_ELEMENTS["scrap_refining"], 8000) {
        LogVisibleNames(80)
        throw Error("'Scrap Refining Process' not found on Inventory panel")
    }
    ClickByName(SCRAP_ELEMENTS["scrap_refining"], 5000)
    Sleep(2000)
    Loop 3 {
        if !FindByName(SCRAP_ELEMENTS["dialog_ok"], 1200) && FindByName(SCRAP_ELEMENTS["scrap_refining"], 800) {
            LogMessage("    [nav-retry] dialog not open yet - re-clicking Scrap Refining Process")
            ClickByName(SCRAP_ELEMENTS["scrap_refining"], 5000)
            Sleep(2000)
        } else {
            break
        }
    }
    ScrapSortByCreatedOnDescending()
    ScrapApplyAllStatusFilter()
    return true
}

ScrapApplyAllStatusFilter() {
    try {
        statusHeader := FindByName(SCRAP_ELEMENTS["status_header"], 5000)
        if !statusHeader {
            LogMessage("    [filter] Status header not found - proceeding with default (OPEN-only) view")
            return false
        }
        pos := statusHeader.GetPos("screen")
        funnelX := pos.x + pos.w + 12
        funnelY := pos.y + Round(pos.h / 2)
        LogMessage("    [filter] clicking funnel at " . funnelX . "," . funnelY)
        Click(funnelX . "," . funnelY)
        Sleep(700)
        ; 2026-09-28b: the funnel popup is its own floating window, not part of
        ; the main window's element tree - GetBravoRoot() (single-window) only
        ; ever saw the '(Select All)' tri-state box. Search ALL Bravo.exe
        ; windows (same pattern as the vendor picker) so the individual status
        ; checkboxes (OPEN/SHIPPING/RECEIVED/ASSAYED/CLOSED) are actually seen.
        boxes := []
        for r in ScrapBravoRoots() {
            try {
                for b in r.FindElements({Type: "CheckBox"})
                    boxes.Push(b)
            }
        }
        ticked := 0, names := ""
        for b in boxes {
            nm := ""
            try nm := b.Name
            if (nm = "" || nm = "Show summary panel" || nm = "(Select All)")
                continue
            st := -1
            try st := b.ToggleState
            names .= nm . "=" . st . "; "
            if (st = 0) {
                try b.Click("left")
                Sleep(350)
                ticked++
            }
        }
        LogMessage("    [filter] status boxes: " . names . " -> ticked " . ticked)
        if (ticked = 0 && !InStr(names, "CLOSED=1")) {
            ; nothing toggled and CLOSED not visibly on - fall back to the proven CLOSED click
            closedItem := FindByName(SCRAP_ELEMENTS["filter_closed"], 1500)
            if closedItem {
                closedItem.Click("left")
                Sleep(700)
                LogMessage("    [filter] CLOSED checked (fallback)")
            }
        }
        Click(pos.x . "," . (pos.y - 38))
        Sleep(500)
        return true
    } catch as fe {
        LogMessage("    [filter] exception: " . fe.Message . " - proceeding with default view")
        return false
    }
}
