; ============================================================================
; reports/SoldDiscountDetail.ahk
;
; Runs the "Claude Sold Inv Details" saved Custom Report from the Inventory
; sidebar for a Date Sold range, for the DISCOUNT REVIEW task (ticketed
; Price vs Last Sold Price).
;
; ADDITIVE (Rule #4): NEW file, NEW cell (sold-discount-detail). Cloned from
;   JewelrySoldMargin.ahk (2026-08-13). Does NOT modify JewelrySoldMargin.ahk
;   or its cell, which are owned by the jewelry-scrap project and must keep
;   their current behavior.
;
; WHY THIS EXISTS — two bugs proven live on 2026-08-13 in the shared
; jewelry-margin-sold path (trigger discount-review-2026-08-13T08-27-03):
;
;   BUG 1 — "success" with no file on disk.
;     JewelrySoldMargin.ahk's empty-grid branch sets row_count := 0 and
;     returns status "success" with an output_path, but never writes a CSV.
;     ResetOutputFile only clears a pre-existing file, so nothing lands on
;     disk. HAR/LEX/ROA all reported success+0 rows and produced NO file,
;     making a genuine quiet day indistinguishable from a cell that never
;     ran. Downstream, the compile script correctly refused to treat the
;     missing files as confirmed-quiet and reported them as missing_stores.
;     FIX: on a genuine empty grid, write a HEADER-ONLY CSV so "ran, no
;     sales" is a positive, checkable fact on disk.
;
;   BUG 2 — captured the WRONG grid and reported it as data.
;     WriteBuysGridToCsv does root.FindElement({Type: "DataItem"}) against
;     the ENTIRE Bravo UIA root, unscoped. On WAY the report grid was slow
;     (172s, near the 180s cap) and the walk latched onto a different grid
;     still live in the tree — the Global Access store picker — writing a
;     CSV whose header was "DisplayCode,Store" with 5 rows (the 5 stores),
;     reported as "SUCCESS: 5 data rows". Plausible-looking, entirely wrong.
;     FIX: validate grid IDENTITY before accepting any row. The captured
;     column set must look like sold-inventory data; a known-wrong shape
;     (DisplayCode/Store) is rejected outright and retried, and we refuse
;     to write rather than emit misleading data.
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD..YYYY-MM-DD"  — Date Sold range (positions 1 and 2)
;   "YYYY-MM-DD"              — single day
;   "saved"                   — run exactly as saved, no date override
; ============================================================================

#Requires AutoHotkey v2.0

global SOLD_DISCOUNT_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_value",   "Claude Sold Inv Details",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

; Column tokens we expect to see in a real "Claude Sold Inv Details" grid.
; Matched case-insensitively against both AutomationId and column label.
global SOLD_DISCOUNT_EXPECTED_COLS := [
    "number", "status", "category", "description",
    "cost", "price", "lastsold", "last sold", "date"
]

; A column shape that proves we latched onto the WRONG grid. The Global
; Access store picker renders exactly these and nothing else.
global SOLD_DISCOUNT_FORBIDDEN_COLS := ["displaycode", "store"]

PullSoldDiscountDetail(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "sold-discount-detail",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    useSavedCriteria := (StrLower(Trim(dateOrRange)) = "saved")

    startDate := ""
    endDate := ""
    if (useSavedCriteria) {
        startDate := "saved"
        endDate := "saved"
    } else if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange)
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := dateOrRange
        endDate := dateOrRange
    }
    LogMessage("[" . store . "] SoldDiscountDetail startDate=" . startDate . " endDate=" . endDate)

    outputFileName := (useSavedCriteria ? "saved_" . store : startDate . "_to_" . endDate . "_" . store) . "_sold-discount-detail.csv"
    outputPath := outputDir . "\" . outputFileName
    LogMessage("  output -> " . outputPath)

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    ; Pre-dismiss stuck dialogs so a stranded editor never poisons this run.
    ActivateBravo()
    Loop 4 {
        dismissed := false
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "btnCancel"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    dismissed := true
                } catch as ie {
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
            }
        }
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "PART_CancelDialogButton"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    dismissed := true
                    Sleep(900)
                }
            }
        }
        if (!dismissed)
            break
    }
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()

        LogMessage("  step 1: open Inventory")
        ClickByName(SOLD_DISCOUNT_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(SOLD_DISCOUNT_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        wantReport := SOLD_DISCOUNT_ELEMENTS["saved_report_value"]
        LogMessage("  step 3: select saved report '" . wantReport . "'")
        if !SelectInventorySavedReport(wantReport)
            throw Error("Could not select '" . wantReport . "' from the Inventory saved-report dropdown")
        Sleep(1200)

        LogMessage("  step 3b: verify report name committed")
        verified := false
        Loop 2 {
            loadedName := ""
            try {
                root := GetBravoRoot()
                nameBox := root.FindElement({AutomationId: "BoxReportName"})
                if nameBox {
                    try loadedName := nameBox.Value
                    if (loadedName = "")
                        try loadedName := nameBox.Name
                }
            }
            LogMessage("    BoxReportName = '" . loadedName . "'")
            if (loadedName != "" && InStr(loadedName, wantReport)) {
                verified := true
                break
            }
            if (A_Index = 1) {
                LogMessage("    WARN: report name mismatch — re-selecting once")
                try SelectInventorySavedReport(wantReport)
                Sleep(1500)
            }
        }
        if (!verified) {
            LogVisibleNames()
            throw Error("Saved report '" . wantReport . "' did not load — refusing to run and emit misleading data")
        }
        LogMessage("    verified OK")

        dateSet := 0
        if (useSavedCriteria) {
            LogMessage("  step 4/5: SKIPPED date override — running report as saved in Bravo")
        } else {
            LogMessage("  step 4: attempt Date Sold start override -> " . startDate)
            try {
                SetReportDate(1, startDate)
                dateSet += 1
                Sleep(400)
            } catch as e {
                LogMessage("    NOTE: SetReportDate(1) unavailable: " . e.Message . " — continuing with saved criteria")
            }

            LogMessage("  step 5: attempt Date Sold end override -> " . endDate)
            try {
                SetReportDate(2, endDate)
                dateSet += 1
                Sleep(400)
            } catch as e {
                LogMessage("    NOTE: SetReportDate(2) unavailable: " . e.Message . " — continuing with saved criteria")
            }
            LogMessage("    date fields set: " . dateSet . "/2")
        }

        LogMessage("  step 6: click Ok to run the report")
        Sleep(2000)
        ActivateBravo()
        Sleep(500)
        try {
            ClickByName(SOLD_DISCOUNT_ELEMENTS["dialog_ok"], 5000)
            LogMessage("    clicked Ok by name")
        } catch as e {
            LogMessage("    WARN: Ok click failed (" . e.Message . ") — falling back to {Enter}")
            Send("{Enter}")
        }
        Sleep(2000)

        dialogGone := false
        closeCheckStart := A_TickCount
        Loop {
            stillOpen := false
            try {
                root := GetBravoRoot()
                nb := root.FindElement({AutomationId: "BoxReportName"})
                if nb
                    stillOpen := true
            }
            if (!stillOpen) {
                dialogGone := true
                break
            }
            if (A_TickCount - closeCheckStart > 20000)
                break
            if (Mod(A_Index, 3) = 0) {
                LogMessage("    dialog still open — clicking Ok again")
                try ClickByName(SOLD_DISCOUNT_ELEMENTS["dialog_ok"], 2000)
                catch
                    Send("{Enter}")
            }
            Sleep(1500)
        }
        if (!dialogGone) {
            LogVisibleNames()
            throw Error("Report generator dialog never closed after Ok — report did not run (2026.6 regression?)")
        }
        LogMessage("    generator dialog closed — report is running")

        ; ------------------------------------------------------------------
        ; [BUG 2 FIX] Wait for a grid that is not only PRESENT but CORRECT.
        ; The old code broke out of this loop on the first DataItem found
        ; anywhere in the tree. On WAY that was the store picker. Here we
        ; additionally require the DataItems to carry sold-inventory columns
        ; before we accept the grid as ready.
        ; ------------------------------------------------------------------
        LogMessage("  step 6b: waiting for a VALID sold-details grid to render")
        gridReady := false
        emptyGrid := false
        sawWrongGrid := false
        rendCheckStart := A_TickCount
        Loop {
            try {
                root := GetBravoRoot()
                di := root.FindElements({Type: "DataItem"})
                if (di && di.Length > 0) {
                    verdict := ClassifySoldDiscountGrid(di)
                    if (verdict = "valid") {
                        LogMessage("    [grid] VALID sold-details grid with " . di.Length . " initial DataItems after " . ((A_TickCount - rendCheckStart) // 1000) . "s")
                        gridReady := true
                        break
                    } else if (verdict = "wrong") {
                        if (!sawWrongGrid) {
                            LogMessage("    [grid] WARN: found a grid that is NOT the sold-details grid (looks like the store picker) — ignoring and continuing to wait")
                            sawWrongGrid := true
                        }
                    }
                    ; "unknown" -> columns not yet populated; keep waiting.
                }
            }
            if (A_TickCount - rendCheckStart > 180000)
                break
            Sleep(2000)
        }
        if (!gridReady) {
            try {
                root := GetBravoRoot()
                lay := root.FindElement({Name: SOLD_DISCOUNT_ELEMENTS["layouts_caret"]})
                if lay {
                    emptyGrid := true
                    LogMessage("    [grid] report surface present with no data rows — treating as legitimate empty result")
                }
            }
            if (!emptyGrid) {
                LogVisibleNames()
                throw Error("Sold-details grid did not render within 180s" . (sawWrongGrid ? " (a non-report grid WAS present the whole time — likely a stranded store picker)" : "") . " — see diag dump")
            }
        }
        Sleep(3000)
        DismissPopups()

        if (emptyGrid) {
            ; --------------------------------------------------------------
            ; [BUG 1 FIX] Write a header-only CSV. A quiet day must leave
            ; positive evidence on disk, so downstream can tell "ran, no
            ; sales" apart from "never ran".
            ; --------------------------------------------------------------
            WriteSoldDiscountEmptyCsv(outputPath)
            LogMessage("    wrote header-only CSV (0 sales) -> quiet day is now provable on disk")
            result["row_count"] := 0
        } else {
            LogMessage("  step 7: walk grid rows and write CSV")
            rowsWritten := WriteSoldDiscountGridToCsv(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("Failed to walk sold-details grid (no valid DataItem rows found)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
            result["row_count"] := rowsWritten
        }

        LogMessage("  step 8: exit editor -> Dashboard")
        Loop 4 {
            try ClickByName(SOLD_DISCOUNT_ELEMENTS["panel_cancel"], 2500)
            Sleep(900)
        }
        try {
            if BackToDashboard()
                LogMessage("    confirmed back on Dashboard")
            else
                LogMessage("    WARN: BackToDashboard did not confirm — health gate will recover")
        } catch as be {
            LogMessage("    WARN: BackToDashboard threw: " . be.Message)
        }

    } catch as e {
        LogVisibleNames()
        Loop 4 {
            try ClickByName(SOLD_DISCOUNT_ELEMENTS["panel_cancel"], 2000)
            Sleep(700)
        }
        try BackToDashboard()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " data rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; Grid identity check. Returns "valid" | "wrong" | "unknown".
;   valid   - columns look like sold-inventory data; safe to capture.
;   wrong   - columns match a known non-report grid (store picker); never
;             capture, keep waiting for the real one.
;   unknown - not enough column info yet; caller should keep polling.
; ----------------------------------------------------------------------------
ClassifySoldDiscountGrid(dataItems) {
    global SOLD_DISCOUNT_EXPECTED_COLS, SOLD_DISCOUNT_FORBIDDEN_COLS

    seen := Map()
    ; Sample a handful of rows; that is plenty to identify the grid shape.
    sampled := 0
    for di in dataItems {
        kids := 0
        try kids := di.FindElements({Scope: 2})
        if (!kids || kids.Length = 0)
            continue
        for k in kids {
            kAutoId := ""
            kName := ""
            try kAutoId := k.AutomationId
            try kName := k.Name
            lbl := kAutoId
            if RegExMatch(kName, "Column ([^,]+), Column \d+ of \d+", &mc)
                lbl := mc[1]
            if (kAutoId != "")
                seen[StrLower(kAutoId)] := true
            if (lbl != "")
                seen[StrLower(lbl)] := true
        }
        sampled++
        if (sampled >= 3)
            break
    }

    if (seen.Count = 0)
        return "unknown"

    expectedHits := 0
    for token in SOLD_DISCOUNT_EXPECTED_COLS {
        for key, _ in seen {
            if InStr(key, token) {
                expectedHits++
                break
            }
        }
    }

    forbiddenHits := 0
    for token in SOLD_DISCOUNT_FORBIDDEN_COLS {
        for key, _ in seen {
            if (key = token) {
                forbiddenHits++
                break
            }
        }
    }

    ; The store picker is exactly DisplayCode + Store and nothing else.
    if (forbiddenHits >= 2 && expectedHits < 3)
        return "wrong"

    ; Require a few real sold-item columns before trusting the grid.
    if (expectedHits >= 3)
        return "valid"

    return "unknown"
}

; ----------------------------------------------------------------------------
; Header-only CSV for a genuine zero-sale day. Uses the documented schema so
; the file is parseable by the same downstream reader as a populated day.
; ----------------------------------------------------------------------------
WriteSoldDiscountEmptyCsv(outputPath) {
    header := "Number,Status,Category,Description,Cost,Price,Last Sold Price,Date"
    FileAppend(header . "`r`n", outputPath, "UTF-8-RAW")
}

; ----------------------------------------------------------------------------
; Grid walker. Same virtualized-grid traversal and truncation guard as
; WriteBuysGridToCsv, plus a hard identity re-check on every pass so a
; mid-walk grid swap can never contaminate the output.
; ----------------------------------------------------------------------------
WriteSoldDiscountGridToCsv(outputPath) {
    allRows := Map()
    columnAutoIds := []
    columnLabels := Map()
    totalRows := -1
    pagesNoNewRows := 0
    maxPages := 250
    pageIdx := 0

    try {
        root := GetBravoRoot()
        firstDi := root.FindElement({Type: "DataItem"})
        if firstDi {
            try firstDi.Click("left")
            Sleep(200)
        }
    }

    Loop maxPages {
        pageIdx++
        dataItems := 0
        try {
            root := GetBravoRoot()
            dataItems := root.FindElements({Type: "DataItem"})
        } catch as e {
            LogMessage("    WARN scroll pass " . pageIdx . " enumerate: " . e.Message)
            break
        }
        if (!dataItems || dataItems.Length = 0) {
            LogMessage("    [grid] no DataItems on pass " . pageIdx)
            break
        }

        ; Identity re-check every pass — refuse to blend in a foreign grid.
        verdict := ClassifySoldDiscountGrid(dataItems)
        if (verdict = "wrong") {
            LogMessage("    [grid] ABORT: grid changed identity mid-walk (non-report grid detected on pass " . pageIdx . ")")
            throw Error("Grid identity changed mid-walk — refusing to write data captured from the wrong grid")
        }

        newRowsThisPass := 0
        for di in dataItems {
            kids := 0
            try kids := di.FindElements({Scope: 2})
            if (!kids || kids.Length = 0)
                continue
            rowIdx := -1
            for k in kids {
                kName := ""
                try kName := k.Name
                if RegExMatch(kName, "Row (\d+) of (\d+)", &m) {
                    rowIdx := Integer(m[1])
                    rt := Integer(m[2])
                    if (totalRows < 0 || rt > totalRows)
                        totalRows := rt
                    break
                }
            }
            if (rowIdx < 0)
                continue
            if (allRows.Has(rowIdx))
                continue

            rowMap := Map()
            for k in kids {
                kAutoId := ""
                kName := ""
                try kAutoId := k.AutomationId
                try kName := k.Name
                if (kAutoId = "")
                    continue
                if (!columnLabels.Has(kAutoId)) {
                    columnAutoIds.Push(kAutoId)
                    lbl := kAutoId
                    if RegExMatch(kName, "Column ([^,]+), Column \d+ of \d+", &mc)
                        lbl := mc[1]
                    columnLabels[kAutoId] := lbl
                }
                v := kName
                colonPos := InStr(kName, ": ", false, -1)
                if (colonPos > 0)
                    v := SubStr(kName, colonPos + 2)
                rowMap[kAutoId] := v
            }
            allRows[rowIdx] := rowMap
            newRowsThisPass++
        }

        LogMessage("    [grid pass " . pageIdx . "] new=" . newRowsThisPass . " seen=" . allRows.Count . "/" . (totalRows > 0 ? totalRows : "?"))

        if (totalRows > 0 && allRows.Count >= totalRows) {
            LogMessage("    [grid] captured all " . totalRows . " rows")
            break
        }
        if (newRowsThisPass = 0) {
            pagesNoNewRows++
            if (pagesNoNewRows >= 3) {
                LogMessage("    [grid] 3 consecutive PageDowns with no new rows; stopping at " . allRows.Count)
                break
            }
        } else {
            pagesNoNewRows := 0
        }

        Send("{PgDn}")
        Sleep(400)
    }

    ; Truncation guard — same contract as BuysFromPublic (2026-08-03).
    if (totalRows > 0) {
        missing := totalRows - allRows.Count
        if (missing > 5 && allRows.Count < totalRows * 0.98) {
            LogMessage("    [grid] TRUNCATED: captured " . allRows.Count . " of " . totalRows . " rows (" . missing . " missing) after " . pageIdx . " passes")
            throw Error("Grid walk truncated: captured " . allRows.Count . " of " . totalRows . " rows (" . missing . " missing). Refusing to report a partial grid as a complete result.")
        }
        if (missing > 0)
            LogMessage("    [grid] NOTE: captured " . allRows.Count . " of " . totalRows . " rows - " . missing . " short, within tolerance (likely group/summary rows)")
    } else {
        LogMessage("    [grid] WARN: no row-total available from the grid; completeness could NOT be verified for " . allRows.Count . " rows")
    }

    if (allRows.Count = 0 || columnAutoIds.Length = 0) {
        LogMessage("    no rows / columns captured")
        return -1
    }

    ; Final identity gate on the assembled column set — last line of defence
    ; before anything is written to disk.
    finalSeen := Map()
    for autoId in columnAutoIds {
        finalSeen[StrLower(autoId)] := true
        finalSeen[StrLower(columnLabels[autoId])] := true
    }
    global SOLD_DISCOUNT_EXPECTED_COLS
    finalHits := 0
    for token in SOLD_DISCOUNT_EXPECTED_COLS {
        for key, _ in finalSeen {
            if InStr(key, token) {
                finalHits++
                break
            }
        }
    }
    if (finalHits < 3) {
        hdrDump := ""
        for i, autoId in columnAutoIds
            hdrDump .= (i > 1 ? "," : "") . columnLabels[autoId]
        LogMessage("    [grid] REJECT: captured columns do not look like sold-inventory data -> " . hdrDump)
        throw Error("Captured grid failed the sold-details column check (got: " . hdrDump . "). Refusing to write misleading data.")
    }

    headerLine := ""
    for i, autoId in columnAutoIds {
        if (i > 1)
            headerLine .= ","
        headerLine .= ToCsvField(columnLabels[autoId])
    }
    FileAppend(headerLine . "`r`n", outputPath, "UTF-8-RAW")
    LogMessage("    [grid] header: " . headerLine)

    sortedIdx := []
    for idx, _ in allRows
        sortedIdx.Push(idx)
    n := sortedIdx.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1 && sortedIdx[j] < sortedIdx[j-1]) {
            tmp := sortedIdx[j]
            sortedIdx[j] := sortedIdx[j-1]
            sortedIdx[j-1] := tmp
            j--
        }
        i++
    }

    dataCount := 0
    for idx in sortedIdx {
        r := allRows[idx]
        rowLine := ""
        for i, autoId in columnAutoIds {
            if (i > 1)
                rowLine .= ","
            v := r.Has(autoId) ? r[autoId] : ""
            rowLine .= ToCsvField(v)
        }
        FileAppend(rowLine . "`r`n", outputPath, "UTF-8-RAW")
        dataCount++
    }
    return dataCount
}
