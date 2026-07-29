; ============================================================================
; reports/AgedJewelrySales.ahk
;
; Runs the "Aged Jewelry Sales" saved Custom Report from the Inventory
; sidebar — jewelry items SOLD within a date range, carrying age-at-sale,
; for one store.
;
; PURPOSE: answers the 12-month vs 18-month scrap-threshold policy question.
;   We need to know how much jewelry that was ALREADY 12+ months old actually
;   sold in a recent window, and at what recovery vs cost — so we can compare
;   holding it against scrapping it at melt.
;
; ADDITIVE (valley-pawn-context Rule #4): this is a NEW handler pointing at a
;   NEW saved report. It does not modify SoldInvDetails.ahk, InventoryDetails.ahk,
;   or any existing pipeline cell. Cloned from reports/SoldInvDetails.ahk
;   (2026-07-28) because that handler drives the identical Inventory-module
;   Custom Reports dialog.
;
; UI path:
;   Dashboard -> Inventory (sidebar)
;   -> right panel -> Custom Reports
;   -> Bravo Custom Inventory Report Generator dialog
;       -> Choose Saved Report -> "Aged Jewelry Sales"
;       -> VERIFY the report name actually committed (bravo-context gotcha #2)
;       -> Override date range (positions 1 and 2) — NON-FATAL if absent
;       -> Ok
;   -> List renders
;   -> Walk grid via UIA, write CSV
;   -> Cancel x2 back to Dashboard (bravo-context gotcha #3 — never rely on Done)
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD"                       — single day
;   "YYYY-MM-DD..YYYY-MM-DD"           — explicit range
;
; Output CSV columns: whatever the saved report exports. Written verbatim so
;   the first run tells us the real schema.
; ============================================================================

#Requires AutoHotkey v2.0

global AGED_JEWELRY_SALES_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Aged Jewelry Sales",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullAgedJewelrySales(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "aged-jewelry-sales",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; "saved" => run the report EXACTLY as saved in Bravo, with no date
    ; override at all. Needed because we do not yet know what the two date
    ; criteria at positions 1/2 actually filter on. If they are ACQUISITION
    ; dates rather than SALE dates, forcing a recent window returns 0 rows by
    ; construction (nothing acquired in the last 90 days can be 12+ months
    ; old). Running as-saved reveals the true schema and row shape.
    ; "saved"                  -> run 'Aged Jewelry Sales' as saved
    ; "saved:<Report Name>"     -> run ANY saved Inventory report as saved
    ;                              (probe mode — lets us inspect each report's
    ;                              columns without a code edit + watcher restart)
    ; "saved:<Report>"                  -> any report, as saved
    ; "saved:<Report>|<from>..<to>"     -> any report, WITH date override
    ; "columns:<Report>"                -> column-picker probe
    ; "age:<N>|<from>..<to>"           -> run the DEFAULT report but override the
    ;                                      'Inventory Age >' spinner to N for THIS
    ;                                      RUN ONLY (never saved). age:0 = all
    ;                                      jewelry sold in the window.
    reportOverride := ""
    probeColumns := false
    ageOverride := ""
    trimmed := Trim(dateOrRange)
    if (StrLower(SubStr(trimmed, 1, 4)) = "age:") {
        rest := SubStr(trimmed, 5)
        parts3 := StrSplit(rest, "|", , 2)   ; MaxParts=2: rest may itself contain '|'
        if (parts3.Length = 2) {
            ageOverride := Trim(parts3[1])
            dateOrRange := Trim(parts3[2])
            trimmed := dateOrRange
        }
    }
    if (StrLower(SubStr(trimmed, 1, 6)) = "saved:") {
        reportOverride := Trim(SubStr(trimmed, 7))
        dateOrRange := "saved"
        if InStr(reportOverride, "|") {
            parts2 := StrSplit(reportOverride, "|")
            reportOverride := Trim(parts2[1])
            dateOrRange := Trim(parts2[2])
        }
    } else if (StrLower(SubStr(trimmed, 1, 8)) = "columns:") {
        reportOverride := Trim(SubStr(trimmed, 9))
        probeColumns := true
        dateOrRange := "saved"
    }
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
    LogMessage("[" . store . "] AgedJewelrySales startDate=" . startDate . " endDate=" . endDate)

    reportSlug := "aged-jewelry-sales"
    if (ageOverride != "")
        reportSlug := "jewelry-sold-age" . ageOverride
    if (reportOverride != "") {
        reportSlug := StrLower(reportOverride)
        reportSlug := StrReplace(reportSlug, " ", "-")
        reportSlug := RegExReplace(reportSlug, "[^a-z0-9\-]", "")
    }
    outputFileName := (useSavedCriteria ? "saved_" . store : startDate . "_to_" . endDate . "_" . store) . "_" . reportSlug . ".csv"
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

    ; Pre-dismiss stuck dialogs. A stranded Custom Reports editor from a prior
    ; failed run will otherwise poison this run too (bravo-context gotcha #3).
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
        ClickByName(AGED_JEWELRY_SALES_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(AGED_JEWELRY_SALES_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        wantReport := (reportOverride != "") ? reportOverride : AGED_JEWELRY_SALES_ELEMENTS["saved_report_value"]
        LogMessage("  step 3: select saved report '" . wantReport . "'")
        ; MUST use SelectInventorySavedReport (not the generic SelectSavedReport).
        ; The Inventory module's Custom Reports dialog needs its own selector:
        ; the generic one updates BoxReportName WITHOUT committing the report
        ; definition, so the name verifies while the grid stays empty. Both
        ; working Inventory handlers (InventoryDetails.ahk, SalesDetail.ahk)
        ; use this function; SoldInvDetails.ahk uses the generic one and fails.
        if !SelectInventorySavedReport(wantReport)
            throw Error("Could not select '" . wantReport . "' from the Inventory saved-report dropdown")
        Sleep(1200)

        ; ---- step 3b: VERIFY the selection actually committed -----------------
        ; bravo-context gotcha #2: the item click can silently fail to commit,
        ; leaving the PREVIOUS report's criteria/columns loaded. This is the
        ; exact regression that has bitten "Claude Pawn Walks" five times
        ; (see BRAVO_KNOWN_ISSUES.md). Verify, and re-select once if wrong.
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
            throw Error("Saved report '" . wantReport . "' did not load (wrong report still active) — refusing to run and emit misleading data")
        }
        LogMessage("    verified OK")

        ; ---- step 3c: select the column format (Joshua, 2026-07-28) ----------
        ; After choosing the report you must choose the 'Aged Jewelry Sold'
        ; format in the columns box (BoxColumns) or the report runs with the
        ; default 7-column layout. Only applies to the default report — probe
        ; runs of other reports keep their own saved layouts.
        ; Apply the format to the default report AND to 'Aged Monthly Sales'
        ; (the all-jewelry-sold comparison cohort) — both need Last Sold Price.
        wantFormat := (reportOverride = "" || reportOverride = "Aged Monthly Sales" || reportOverride = "Claude Aged Sold")
        if (wantFormat && !probeColumns) {
            ; NOTE: never include the report's own name here — on WAY (2026-07-28)
            ; the format item rendered slowly, the fallback matched the report
            ; name text, and the run silently produced the default 7-col layout.
            fmtCandidates := ["Aged Jewelry Sold", "Aged jewelry sold", "aged jewelry sold"]
            LogMessage("  step 3c: select column format (candidates: Aged Jewelry Sold...)")
            colBox := ""
            try {
                root := GetBravoRoot()
                colBox := root.FindElement({AutomationId: "BoxColumns"})
            }
            if colBox {
                valBefore := ""
                try valBefore := colBox.Value
                LogMessage("    [fmt] BoxColumns before: '" . valBefore . "'")
                ; open the dropdown — arrow click at right edge, F4 fallback
                rect := 0
                try rect := colBox.BoundingRectangle
                if rect {
                    CoordMode "Mouse", "Screen"
                    cy := Integer(rect.t + rect.b) // 2
                    cx_arrow := Integer(rect.r - 20)
                    LogMessage("    [fmt] arrow click at (" . cx_arrow . "," . cy . ")")
                    MouseClick("Left", cx_arrow, cy)
                    Sleep(1500)
                }
                fmtClicked := ""
                for , cand in fmtCandidates {
                    try {
                        ClickByName(cand, 1500)
                        fmtClicked := cand
                        break
                    }
                }
                attempts := 0
                while (fmtClicked = "" && attempts < 3) {
                    attempts += 1
                    LogMessage("    [fmt] not found — retry " . attempts . " (F4 + longer settle)")
                    try colBox.Focus()
                    Sleep(400)
                    Send("{F4}")
                    Sleep(2500)
                    for , cand in fmtCandidates {
                        try {
                            ClickByName(cand, 2000)
                            fmtClicked := cand
                            break
                        }
                    }
                }
                Sleep(900)
                valAfter := ""
                try valAfter := colBox.Value
                LogMessage("    [fmt] clicked='" . fmtClicked . "' BoxColumns after: '" . valAfter . "'")
                if (fmtClicked = "") {
                    LogVisibleNames()
                    LogMessage("    WARN: could not select column format — running with report's current layout")
                    Send("{Esc}")
                    Sleep(500)
                }
            } else {
                LogMessage("    WARN: BoxColumns not found — running with report's current layout")
            }
        }

        ; ---- step 3d: Inventory Age spinner override (run-only, never saved) --
        if (ageOverride != "") {
            LogMessage("  step 3d: set Inventory Age spinner -> " . ageOverride)
            ageSet := false
            try {
                root := GetBravoRoot()
                spin := root.FindElement({Name: "SpinEdit"})
                if spin {
                    ; [commit-fix 2026-07-28] keyboard path FIRST — ValuePattern sets the
                    ; UIA value but does NOT commit to the criteria model (proven: age:0
                    ; sweep returned sets identical to the saved >365 runs at 4/5 stores)
                    ; [commit-fix v2 2026-07-28] focus the control, set text via
                    ; ValuePattern (reliable), then Tab out so DevExpress validation
                    ; parses the text and commits it to the criteria model.
                    try {
                        try spin.SetFocus()
                        catch
                            spin.Click("left")
                        Sleep(400)
                        spin.Value := ageOverride
                        Sleep(250)
                        vPre := ""
                        try vPre := spin.Value
                        LogMessage("    [age] after ValuePattern set (focused): '" . vPre . "'")
                        Send("{Tab}")
                        Sleep(400)
                        ageSet := true
                        LogMessage("    [age] set via focus+ValuePattern+Tab (commit path)")
                    } catch as kbe {
                        LogMessage("    [age] commit path failed: " . kbe.Message)
                    }
                    v := ""
                    try v := spin.Value
                    LogMessage("    [age] spinner value now: '" . v . "'")
                    if (ageSet && Trim(v) != Trim(ageOverride)) {
                        LogMessage("    [age] WARN: readback '" . v . "' != requested '" . ageOverride . "' — treating as not set")
                        ageSet := false
                    }
                } else {
                    LogMessage("    [age] SpinEdit not found")
                    LogVisibleNames()
                }
            } catch as e {
                LogMessage("    [age] error: " . e.Message)
            }
            if (!ageSet)
                throw Error("Could not set Inventory Age spinner to " . ageOverride . " — refusing to run with wrong cohort definition")
        }

        ; ---- step 4/5: date override. NON-FATAL by design ---------------------
        ; We do not yet know whether this saved report exposes a date range at
        ; criteria positions 1/2. If it does not, we still want the run to
        ; proceed using the report's own saved criteria rather than aborting —
        ; the Date Sold column in the output tells us the true window.
        ; "columns:" probe mode: open the BoxColumns picker, dump every visible
        ; element name to the log, then cancel out WITHOUT running the report.
        dateSet := 0
        if (probeColumns) {
            LogMessage("  step 4-PROBE: opening BoxColumns picker and dumping names")
            try {
                root := GetBravoRoot()
                colBox := root.FindElement({AutomationId: "BoxColumns"})
                if colBox {
                    ; Same open chain as SelectInventorySavedReport: arrow click
                    ; at right edge, then F4, then Alt+Down.
                    rect := 0
                    try rect := colBox.BoundingRectangle
                    if rect {
                        CoordMode "Mouse", "Screen"
                        cy := Integer(rect.t + rect.b) // 2
                        cx_arrow := Integer(rect.r - 20)
                        LogMessage("    [col-probe] arrow click at (" . cx_arrow . "," . cy . ")")
                        MouseClick("Left", cx_arrow, cy)
                        Sleep(1800)
                    }
                    LogMessage("    [col-probe] dump after arrow click:")
                    LogVisibleNames()
                    try colBox.Focus()
                    Sleep(300)
                    Send("{F4}")
                    Sleep(1800)
                    LogMessage("    [col-probe] dump after F4:")
                    LogVisibleNames()
                    Send("{Esc}")
                    Sleep(800)
                } else {
                    LogMessage("    BoxColumns not found")
                    LogVisibleNames()
                }
            } catch as e {
                LogMessage("    probe error: " . e.Message)
                LogVisibleNames()
            }
            ; exit without running
            Loop 4 {
                try ClickByName(AGED_JEWELRY_SALES_ELEMENTS["panel_cancel"], 2000)
                Sleep(800)
            }
            try BackToDashboard()
            result["status"] := "success"
            result["row_count"] := 0
            result["duration_ms"] := A_TickCount - started
            LogMessage("  PROBE COMPLETE — column names dumped to log")
            return result
        }
        if (useSavedCriteria) {
            LogMessage("  step 4/5: SKIPPED date override — running report as saved in Bravo")
        } else {
            LogMessage("  step 4: attempt Start Date override -> " . startDate)
            try {
                SetReportDate(1, startDate)
                dateSet += 1
                Sleep(400)
            } catch as e {
                LogMessage("    NOTE: SetReportDate(1) unavailable: " . e.Message . " — continuing with saved criteria")
            }

            LogMessage("  step 5: attempt End Date override -> " . endDate)
            try {
                SetReportDate(2, endDate)
                dateSet += 1
                Sleep(400)
            } catch as e {
                LogMessage("    NOTE: SetReportDate(2) unavailable: " . e.Message . " — continuing with saved criteria")
            }
            LogMessage("    date fields set: " . dateSet . "/2")
        }

        ; 2026.6.0.79: Enter no longer reliably fires the generator's Ok.
        ; Click Ok explicitly; verify the dialog actually closed before
        ; trusting any result (a 0-row read with the dialog still open is a lie).
        LogMessage("  step 6: click Ok to run the report")
        Sleep(2000)
        ActivateBravo()
        Sleep(500)
        try {
            ClickByName(AGED_JEWELRY_SALES_ELEMENTS["dialog_ok"], 5000)
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
                try ClickByName(AGED_JEWELRY_SALES_ELEMENTS["dialog_ok"], 2000)
                catch
                    Send("{Enter}")
            }
            Sleep(1500)
        }
        if (!dialogGone) {
            LogVisibleNames()
            throw Error("Report generator dialog never closed after Ok — report did not run")
        }
        LogMessage("    generator dialog closed — report is running")

        LogMessage("  step 6b: waiting for DataItem rows to render")
        gridReady := false
        emptyGrid := false
        rendCheckStart := A_TickCount
        Loop {
            try {
                root := GetBravoRoot()
                di := root.FindElements({Type: "DataItem"})
                if (di && di.Length > 0) {
                    LogMessage("    [grid] rendered with " . di.Length . " initial DataItems after " . ((A_TickCount - rendCheckStart) // 1000) . "s")
                    gridReady := true
                    break
                }
            }
            if (A_TickCount - rendCheckStart > 120000)
                break
            Sleep(2000)
        }
        if (!gridReady) {
            ; A legitimately empty result set is a real answer, not a failure —
            ; but only if the grid surface itself is present. Probe for the
            ; Layouts caret, which only exists once a list view has rendered.
            try {
                root := GetBravoRoot()
                lay := root.FindElement({Name: AGED_JEWELRY_SALES_ELEMENTS["layouts_caret"]})
                if lay {
                    emptyGrid := true
                    LogMessage("    [grid] rendered but returned 0 rows — treating as legitimate empty result")
                }
            }
            if (!emptyGrid) {
                LogVisibleNames()
                throw Error("Aged jewelry sales grid did not render within 120s — see diag dump")
            }
        }
        Sleep(3000)
        DismissPopups()

        if (emptyGrid) {
            result["row_count"] := 0
        } else {
            LogMessage("  step 7: walk grid rows and write CSV")
            ; Reuse WriteBuysGridToCsv — generic DevExpress DataItem walker.
            rowsWritten := WriteBuysGridToCsv(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("Failed to walk aged jewelry sales grid (no DataItem rows found)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
            result["row_count"] := rowsWritten
        }

        ; ---- exit: get Bravo genuinely back to the Dashboard -----------------
        ; bravo-context gotcha #3: a stranded Custom Reports editor poisons the
        ; NEXT run and even the health gate's recover-to-dashboard. Two blind
        ; Cancel clicks are not enough — Cancel until the editor is actually
        ; gone, then confirm with BackToDashboard.
        LogMessage("  step 8: exit editor -> Dashboard")
        Loop 4 {
            try ClickByName(AGED_JEWELRY_SALES_ELEMENTS["panel_cancel"], 2500)
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
        ; Always try to unwind the editor even on failure, so the NEXT run and
        ; the health gate are not poisoned by a stranded dialog.
        Loop 4 {
            try ClickByName(AGED_JEWELRY_SALES_ELEMENTS["panel_cancel"], 2000)
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
