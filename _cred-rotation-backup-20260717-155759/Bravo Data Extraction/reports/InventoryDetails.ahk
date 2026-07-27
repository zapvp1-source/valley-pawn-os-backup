; ============================================================================
; reports/InventoryDetails.ahk
;
; Autonomous handler for the "Claude Inventory Details" saved Custom Report
; in the Inventory sidebar. Pulls sold-inventory line items for a configurable
; Status Date range. Uses the proven grid-walker + Show More pattern.
;
; SKILL it powers: deep-kpi-buys (Phase 8+ — sold inventory performance)
;
; UI path:
;   Dashboard -> Inventory (sidebar)
;   -> right panel -> Custom Reports
;   -> Bravo Custom Inventory Report Generator dialog
;       -> Choose Saved Report -> "Claude Inventory Details"
;       -> Override Status Date Start/End (BravoDateEdit positions 1 and 2)
;       -> Click Ok (note: Ok is a TEXT element, not a Button — click via mouse
;          on the Text element's bounding rect center)
;   -> List renders (up to 180s for large stores)
;   -> Walk grid with PageDown + Show More
;   -> CSV per store: <start>_to_<end>_<STORE>_inventory-details.csv
;
; Trigger schema (single "date" field):
;   "date": "2025-05-17..2026-05-17"   — explicit Status Date range
;
; Default recommended window: trailing 12 months (refresh monthly)
; ============================================================================

#Requires AutoHotkey v2.0

global INVDTL_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Sold Inv Details",
    "panel_cancel",         "Cancel"
)

PullInventoryDetails(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "inventory-details",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; Parse date range
    startDate := ""
    endDate := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange)
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := dateOrRange
        endDate := dateOrRange
    }
    LogMessage("[" . store . "] InventoryDetails " . startDate . " to " . endDate)

    outputFileName := startDate . "_to_" . endDate . "_" . store . "_inventory-details.csv"
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

    ; Pre-dismiss any stuck modal dialogs
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
                } catch {
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
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
        ClickByName(INVDTL_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(INVDTL_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . INVDTL_ELEMENTS["saved_report_value"] . "'")
        Sleep(3000)  ; let inventory dialog render fully — it's heavier than loans/buys
        if !SelectInventorySavedReport(INVDTL_ELEMENTS["saved_report_value"])
            throw Error("Could not select '" . INVDTL_ELEMENTS["saved_report_value"] . "' from dropdown")
        Sleep(3000)  ; let criteria fully load after selection

        LogMessage("  step 4: set Status Date Start = " . startDate)
        try {
            SetReportDate(1, startDate)
        } catch as e {
            LogMessage("    WARN SetReportDate(1): " . e.Message)
            throw Error("Could not set Start Date")
        }
        Sleep(400)

        LogMessage("  step 5: set Status Date End = " . endDate)
        try {
            SetReportDate(2, endDate)
        } catch as e {
            LogMessage("    WARN SetReportDate(2): " . e.Message)
            throw Error("Could not set End Date")
        }
        Sleep(600)

        LogMessage("  step 6: click Ok text element to run report")
        if !ClickOkTextInDialog()
            throw Error("Could not find/click 'Ok' Text element")

        LogMessage("  step 7: wait for grid to render (up to 300s)")
        gridReady := false
        waitStart := A_TickCount
        Loop {
            try {
                root := GetBravoRoot()
                di := root.FindElements({Type: "DataItem"})
                if (di && di.Length > 0) {
                    LogMessage("    grid rendered with " . di.Length . " initial DataItems after " . ((A_TickCount - waitStart) // 1000) . "s")
                    gridReady := true
                    break
                }
            }
            if (A_TickCount - waitStart > 300000)
                break
            Sleep(3000)
        }
        if (!gridReady) {
            LogVisibleNames()
            throw Error("Grid did not render within 300s")
        }
        Sleep(2000)

        ; CRITICAL — scroll grid to TOP before walking. After Show More clicks
        ; mid-render or any prior interaction, scrollbar may be at bottom and
        ; PageDown becomes a no-op (got bit by this on CUL 2026-05-17).
        LogMessage("  step 7b: scroll grid to top (Ctrl+Home)")
        try {
            root := GetBravoRoot()
            firstDi := root.FindElement({Type: "DataItem"})
            if firstDi {
                try firstDi.Click("left")
                Sleep(500)
            }
            Send("^{Home}")
            Sleep(1500)
        }

        LogMessage("  step 8: walk grid with PageDown + Show More")
        rowsWritten := WriteInventoryGridWithShowMore(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Grid walk returned -1 (no rows captured)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(INVDTL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(INVDTL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; SelectInventorySavedReport — more patient variant of SelectSavedReport tuned
; for the Inventory Custom Reports dialog. Differences from lib version:
;   - Longer Sleep after combo click (1500ms vs 700ms)
;   - Polls for the item up to 15s with short-timeout ClickByName
;   - Retries the whole sequence up to 3 times if item never appears
;   - Falls back to keyboard down-arrow walk
; ----------------------------------------------------------------------------
SelectInventorySavedReport(valueName) {
    Loop 3 {
        attempt := A_Index
        LogMessage("    [inv-select] attempt " . attempt)

        combo := FindSavedReportCombo()
        if !combo {
            LogMessage("    [inv-select] combo not found — sleeping 2s and retrying")
            Sleep(2000)
            continue
        }

        ; Open dropdown — chain of strategies, with multiple openings to ensure
        ; the dropdown actually expanded:
        ;   1. Click the dropdown ARROW (right edge of combo, not center)
        ;   2. Focus + F4 (standard combo-expand key)
        ;   3. Focus + Alt+Down
        ;   4. ExpandCollapsePattern
        rect := 0
        try rect := combo.BoundingRectangle
        if rect {
            CoordMode "Mouse", "Screen"
            cy := Integer(rect.t + rect.b) // 2
            cx_arrow := Integer(rect.r - 20)  ; 20px from right edge = dropdown arrow
            LogMessage("    [inv-select] mouse-clicking dropdown arrow at (" . cx_arrow . "," . cy . ")")
            MouseClick("Left", cx_arrow, cy)
            Sleep(1500)
        }
        ; If item still not present, try keyboard
        item := FindByName(valueName, 500)
        if !item {
            LogMessage("    [inv-select] still no item — focus + F4")
            try combo.Focus()
            Sleep(300)
            Send("{F4}")
            Sleep(1500)
        }
        item := FindByName(valueName, 500)
        if !item {
            LogMessage("    [inv-select] still no item — Alt+Down")
            try combo.Focus()
            Sleep(300)
            Send("!{Down}")
            Sleep(1500)
        }
        Sleep(1000)  ; final settle — dropdown should be open now

        ; ============================================================
        ; CRITICAL: dropdown contains many saved reports. Target item may
        ; be offscreen. Must scroll within dropdown to find it. Strategies:
        ;   1. Type-ahead — Send the first chars of target name; combos
        ;      with type-ahead jump to first matching item.
        ;   2. Keyboard walk Down — Send {Down} up to 100x checking
        ;      combo.Value each time. If found, Send {Enter}.
        ;   3. Keyboard walk Up — same but {Up} (in case it's above).
        ; ============================================================

        ; Strategy 1 — Type-ahead. Type the target name char-by-char.
        ; Many DevExpress comboboxes support incremental search.
        LogMessage("    [inv-select] strategy 1 — type-ahead: '" . valueName . "'")
        try combo.Focus()
        Sleep(300)
        ; SendInput type-ahead, one char at a time so combo can react
        Loop Parse, valueName {
            Send(A_LoopField)
            Sleep(60)
        }
        Sleep(800)
        ; After typing, check if the highlighted item matches
        try {
            cur := ""
            try cur := combo.Value
            LogMessage("    [inv-select] combo.Value after type-ahead = '" . cur . "'")
            if InStr(cur, valueName) {
                Send("{Enter}")
                Sleep(500)
                LogMessage("    [inv-select] selected '" . valueName . "' via type-ahead + Enter")
                return true
            }
        }
        ; Also try ClickByName one more time (item may now be visible)
        try {
            ClickByName(valueName, 1500)
            LogMessage("    [inv-select] selected '" . valueName . "' via ClickByName after type-ahead")
            Sleep(500)
            return true
        }

        ; Strategy 2 — Keyboard walk Down 100x
        LogMessage("    [inv-select] strategy 2 — keyboard walk Down")
        ; First, send Home to go to top of list (so we walk from beginning)
        try combo.Focus()
        Sleep(200)
        Send("{Home}")
        Sleep(300)
        Loop 100 {
            try {
                cur := combo.Value
                if InStr(cur, valueName) {
                    Send("{Enter}")
                    Sleep(500)
                    LogMessage("    [inv-select] selected via Down walk after " . A_Index . " Downs (value='" . cur . "')")
                    return true
                }
            }
            ; Also try clicking if item visible
            try {
                ClickByName(valueName, 200)
                LogMessage("    [inv-select] selected via ClickByName mid-walk")
                Sleep(500)
                return true
            }
            Send("{Down}")
            Sleep(80)
        }

        ; Strategy 3 — go all the way up then back through (in case Home didn't work)
        LogMessage("    [inv-select] strategy 3 — Page-by-page from End")
        try combo.Focus()
        Sleep(200)
        Send("{End}")
        Sleep(300)
        try {
            cur := combo.Value
            if InStr(cur, valueName) {
                Send("{Enter}")
                Sleep(500)
                LogMessage("    [inv-select] selected by End jump (value='" . cur . "')")
                return true
            }
        }
        Loop 100 {
            try {
                cur := combo.Value
                if InStr(cur, valueName) {
                    Send("{Enter}")
                    Sleep(500)
                    LogMessage("    [inv-select] selected via Up walk after " . A_Index . " Ups (value='" . cur . "')")
                    return true
                }
            }
            try {
                ClickByName(valueName, 200)
                LogMessage("    [inv-select] selected via ClickByName during Up walk")
                Sleep(500)
                return true
            }
            Send("{Up}")
            Sleep(80)
        }

        ; Press Escape to close dropdown before next attempt
        LogMessage("    [inv-select] all 3 strategies failed on attempt " . attempt . " — Esc and retry")
        Send("{Escape}")
        Sleep(800)
    }
    LogMessage("    [inv-select] FAILED after 3 attempts")
    return false
}

; ----------------------------------------------------------------------------
; Click the "Ok" Text element in the dialog (not a Button — that's why
; ClickByName failed before). Find by Name='Ok' at Y > 1000 to skip column
; headers. Click at center of bounding rect via screen-coord mouse click.
; ----------------------------------------------------------------------------
ClickOkTextInDialog() {
    try {
        root := GetBravoRoot()
        texts := root.FindElements({Type: "Text"})
        for t in texts {
            n := ""
            try n := t.Name
            if (n != "Ok")
                continue
            rect := 0
            try rect := t.BoundingRectangle
            if !rect
                continue
            if (rect.t < 1000)
                continue  ; column headers, skip
            cx := Integer(rect.l + rect.r) // 2
            cy := Integer(rect.t + rect.b) // 2
            LogMessage("    Ok text at (" . cx . "," . cy . ")")
            CoordMode "Mouse", "Screen"
            MouseClick("Left", cx, cy)
            return true
        }
    } catch as e {
        LogMessage("    ClickOkTextInDialog: " . e.Message)
    }
    return false
}

; ----------------------------------------------------------------------------
; TryClickShowMore — find a "Show More" / "Load More" pagination button.
; ----------------------------------------------------------------------------
TryClickShowMore_Inv() {
    candidates := ["Show More", "Show more", "Load More", "Load more", "More Results", "Show all", "Show All"]
    try {
        root := GetBravoRoot()
        for label in candidates {
            try {
                el := root.FindElement({Name: label})
                if el {
                    try {
                        el.InvokePattern.Invoke()
                        LogMessage("    [show-more] invoked '" . label . "'")
                        return true
                    } catch {
                        try {
                            el.Click("left")
                            LogMessage("    [show-more] mouse-clicked '" . label . "'")
                            return true
                        }
                    }
                }
            }
        }
    }
    return false
}

; ----------------------------------------------------------------------------
; Walk the inventory grid via PageDown + Show More until total rows captured
; or 3 zero-new passes with no Show More available.
; ----------------------------------------------------------------------------
WriteInventoryGridWithShowMore(outputPath) {
    allRows := Map()
    columnAutoIds := []
    columnLabels := Map()
    totalRows := -1
    pagesNoNew := 0
    showMoreClicks := 0
    maxShowMore := 100
    maxPages := 5000
    pageIdx := 0
    scrollPct := 0
    scrollContainer := 0

    ; Focus first DataItem
    try {
        root := GetBravoRoot()
        firstDi := root.FindElement({Type: "DataItem"})
        if firstDi {
            try firstDi.Click("left")
            Sleep(300)
        }
    }

    ; Discover a focus-independent UIA scroll container for the grid. Virtualized
    ; Bravo grids (notably the dashboard "Price Items" worklist) ignore PgDn once
    ; the rendered window is full AND expose no reachable "Show More" button, so
    ; the PgDn+ShowMore walk capped at the first ~43 rendered rows. We drive
    ; ScrollPattern.SetScrollPercent like the proven IntakeDetail walker. This is
    ; additive: when no scroll container exists (e.g. Inventory Details' own grid)
    ; the original PgDn + Show More paths run unchanged. (2026-06-20)
    try {
        rootSC := GetBravoRoot()
        probe := rootSC.FindElement({Type: "DataItem"})
        anc := probe
        Loop 10 {
            anc := anc.Parent
            if !anc
                break
            if anc.IsScrollPatternAvailable {
                scrollContainer := anc
                break
            }
        }
    }
    LogMessage("    [grid] scroll container: " . (scrollContainer ? "ScrollPattern" : "none - PgDn/ShowMore only"))

    Loop maxPages {
        pageIdx++
        dataItems := 0
        try {
            root := GetBravoRoot()
            dataItems := root.FindElements({Type: "DataItem"})
        } catch as e {
            LogMessage("    WARN enumerate pass " . pageIdx . ": " . e.Message)
            break
        }

        ; If 0 DataItems mid-walk, try Show More first (recovery)
        if (allRows.Count > 0 && (!dataItems || dataItems.Length = 0)) {
            LogMessage("    pass " . pageIdx . ": 0 DataItems mid-walk, trying Show More")
            if TryClickShowMore_Inv() {
                Sleep(2500)
                showMoreClicks++
                continue
            }
            ; Recovery: re-focus
            try {
                WinActivate("Bravo ")
                Sleep(300)
                Send("{PgUp}")
                Sleep(600)
            }
            continue
        }

        if (!dataItems || dataItems.Length = 0) {
            LogMessage("    pass " . pageIdx . ": no DataItems and 0 rows captured yet; aborting")
            break
        }

        newRows := 0
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
            newRows++
        }

        LogMessage("    pass " . pageIdx . " new=" . newRows . " seen=" . allRows.Count . "/" . (totalRows > 0 ? totalRows : "?") . " showMore=" . showMoreClicks)

        if (totalRows > 0 && allRows.Count >= totalRows) {
            LogMessage("    captured all " . totalRows . " rows")
            break
        }

        if (newRows > 0) {
            pagesNoNew := 0
            ; Prefer the focus-independent scroll container when available; PgDn
            ; fights ScrollPattern and desyncs the virtualized viewport.
            if (scrollContainer && scrollPct < 100) {
                scrollPct += 10
                if (scrollPct > 100)
                    scrollPct := 100
                try scrollContainer.ScrollPattern.SetScrollPercent(scrollPct, -1)
                Sleep(500)
            } else {
                Send("{PgDn}")
                Sleep(400)
            }
            continue
        }

        ; --- Stalled: no new rows captured this pass ------------------------
        ; If the grid has a scroll container and we have not yet reached the
        ; bottom, push the viewport further and retry BEFORE counting this as a
        ; real stall. This is what unblocks virtualized grids with no Show More
        ; button; only once scrolling is exhausted do we fall back to
        ; End/Ctrl+End + Show More + give-up below. (additive 2026-06-20)
        if (scrollContainer && scrollPct < 100) {
            scrollPct += 10
            if (scrollPct > 100)
                scrollPct := 100
            try scrollContainer.ScrollPattern.SetScrollPercent(scrollPct, -1)
            Sleep(550)
            continue
        }

        pagesNoNew++

        ; Bring the tail of the virtualized grid (and the "Show More" button)
        ; into view before deciding we're done. Large grids (e.g. WAY ~260
        ; rows) load in batches and the Show More button only exists/clicks
        ; when the current bottom is scrolled into view — without this the walk
        ; bailed at the first batch boundary (44/262). Jump to the very bottom,
        ; then retry Show More.
        try {
            root := GetBravoRoot()
            dis := root.FindElements({Type: "DataItem"})
            if (dis && dis.Length > 0) {
                try dis[dis.Length].Click("left")
                Sleep(200)
            }
        }
        Send("{End}")
        Sleep(300)
        Send("^{End}")
        Sleep(600)

        if (showMoreClicks < maxShowMore && TryClickShowMore_Inv()) {
            showMoreClicks++
            Sleep(2500)
            try {
                root := GetBravoRoot()
                dis := root.FindElements({Type: "DataItem"})
                if (dis && dis.Length > 0) {
                    try dis[dis.Length].Click("left")
                    Sleep(300)
                }
            }
            pagesNoNew := 0
            continue
        }

        ; Only give up once we've actually reached the grid's reported total
        ; (or the total is unknown). While allRows.Count < totalRows there are
        ; still rows to load, so stay persistent — keep alternating PgDn/End +
        ; Show More for many more passes rather than bailing after 2.
        moreExpected := (totalRows > 0 && allRows.Count < totalRows)
        giveUpThreshold := moreExpected ? 8 : 2
        if (pagesNoNew >= giveUpThreshold) {
            if (moreExpected)
                LogMessage("    GAVE UP at " . allRows.Count . "/" . totalRows . " after " . pagesNoNew . " stalled passes (Show More unreachable)")
            else
                LogMessage("    no new rows + no Show More; stopping at " . allRows.Count)
            break
        }
        Send("{PgDn}")
        Sleep(600)
    }

    if (allRows.Count = 0 || columnAutoIds.Length = 0) {
        LogMessage("    no rows / columns captured")
        return -1
    }

    ; Write CSV
    headerLine := ""
    for i, autoId in columnAutoIds {
        if (i > 1)
            headerLine .= ","
        headerLine .= ToCsvField(columnLabels[autoId])
    }
    FileAppend(headerLine . "`r`n", outputPath, "UTF-8-RAW")

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

    count := 0
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
        count++
    }
    return count
}
