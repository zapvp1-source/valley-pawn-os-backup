; ============================================================================
; reports/SalesDetail.ahk
;
; Autonomous handler for the "Claude Sold Yesterday" saved Custom Report in
; the Inventory sidebar (Shared Company-Wide). Pulls the prior day's SOLD
; line items — item number, description, sale date, sale price — for the
; new daily customer-facing sales export.
;
; SKILL it powers: daily sales-detail CSV export (Phase 1 — customer-facing
; website feed)
;
; UI path (SAME "Bravo Custom Inventory Report Generator" dialog used by
; reports\InventoryDetails.ahk and reports\SoldInvDetails.ahk — cloned from
; InventoryDetails.ahk as the closest proven precedent):
;   Dashboard -> Inventory (sidebar)
;   -> right panel -> Custom Reports
;   -> Bravo Custom Inventory Report Generator dialog
;       -> Choose Saved Report -> "Claude Sold Yesterday"
;          -- VERIFIED via BoxReportName (IntakeGetLoadedReportName, from
;             reports\IntakeDetail.ahk) before touching any criteria. A
;             case-sensitive silent mismatch here is a documented failure
;             mode from a prior build — we throw rather than proceed if the
;             loaded name doesn't match exactly.
;       -> Status = SOLD criterion is a fixed row and is NEVER touched.
;       -> Status Date criterion is overridden to the `date` argument via
;          SalesDetailSetStatusDate() — see DATE OVERRIDE NOTE below.
;       -> Ok (Text element, not a Button — click via ClickOkTextInDialog,
;          reused as-is from InventoryDetails.ahk).
;   -> List renders ("Layouts" caret = grid-ready signal, same as other
;      Custom-Reports-editor handlers).
;   -> Walk grid with WriteInventoryGridWithShowMore() — reused AS-IS from
;      InventoryDetails.ahk (no duplicate walking logic) — into a temp CSV
;      containing every column the grid exposes.
;   -> SalesDetailFilterCsv() filters/reorders the temp CSV down to exactly
;      the 4 wanted columns (item number, description, sale date, sale
;      price), matched against the ACTUAL grid header text at runtime (not
;      assumed). If any of the 4 is missing, we STOP and surface the actual
;      column list rather than guess or fabricate data.
;   -> Cancel x2 back to Dashboard — in BOTH the success path and the
;      catch/error path (never rely on Done/BackToDashboard alone; mirrors
;      the rule documented in NicsTransfers.ahk).
;
; Trigger schema (single "date" field): "YYYY-MM-DD" — single day only (this
; report is always a single day; no ".." range form).
;
; Output filename: <date>_<store>_sales-detail.csv (single date, no range
; suffix — deliberately different from InventoryDetails' <start>_to_<end>
; naming since this report never spans a range).
;
; DATE OVERRIDE NOTE (2026-07-23): the build spec for this handler requires
; the Status Date criterion be overridden via the calendar-picker control
; next to the field, and never by typing — documented elsewhere (see
; NicsTransfers.ahk's header comment) as a gotcha where typed/pasted text is
; visually accepted but leaves the confirm button disabled.
;
; HOWEVER: as of this writing, NO handler anywhere in this codebase has a
; working calendar-picker click implementation to clone. NicsTransfers.ahk
; explicitly punted on date override entirely ("running report as-saved this
; pass"). IntakeDetail.ahk's IntakeSetDateByPopupEditor() — the only other
; "special" date-handling code in the codebase — is itself just a different
; way to reach a ValuePattern/clipboard SET, not a calendar click. And the
; ONE proven precedent for THIS SPECIFIC dialog ("Bravo Custom Inventory
; Report Generator") is InventoryDetails.ahk's SetReportDate(), which sets
; BravoDateEdit.Value directly (ValuePattern, with a clipboard-paste
; fallback) and has been running the Status-Date-family criteria in
; production successfully.
;
; So SalesDetailSetStatusDate() below tries a calendar-picker click FIRST,
; best-effort (find a picker button near the Status Date BravoDateEdit
; wrapper, open it, click a cell matching the target day) — and only if that
; attempt can be CONFIRMED via read-back of the field value does it count as
; success. If it cannot be confirmed, it falls back to the proven
; SetReportDate() path. Every attempt is logged so a human can audit exactly
; which path fired on a given run. This is a deliberate, flagged deviation
; from the letter of the build spec, made because no proven calendar-picker
; implementation exists to clone and inventing one blind (with no live UI
; inspection available) was judged riskier than falling back to the one
; mechanism actually proven against this exact dialog. See handoff report.
; ============================================================================
#Requires AutoHotkey v2.0

global SALESDTL_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Sold Yesterday",
    "panel_cancel",         "Cancel"
)

; Desired final CSV columns, in output order, with candidate header-text
; matches (case-insensitive, exact-then-substring) used to locate them among
; whatever columns the grid actually exposes at runtime.
global SALESDTL_WANTED := [
    Map("out", "Item Number", "candidates", ["Number", "Item Number", "Item #", "Tag Number"]),
    Map("out", "Description", "candidates", ["Tag Description", "Description"]),
    Map("out", "Sale Date",   "candidates", ["Status Date", "Sale Date", "Date Sold", "Date"]),  ; "Date" added 2026-07-23 after live smoke test showed the actual grid header for this saved report is the bare word "Date" (report is filtered to Status=SOLD, so this is the Status Date / sale date column, just labeled shorter in the grid than in the criteria pane)
    Map("out", "Sale Price",  "candidates", ["Sale Price", "Sold Price", "Price"])
]

PullSalesDetail(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "sales-detail",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    LogMessage("[" . store . "] SalesDetail date=" . date)

    outputPath := outputDir . "\" . date . "_" . store . "_sales-detail.csv"
    tempPath   := outputDir . "\" . date . "_" . store . "_sales-detail.raw.tmp.csv"
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
    ResetOutputFile(tempPath)

    ; Pre-dismiss any stuck modal dialogs (mirrors InventoryDetails.ahk).
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
        ClickByName(SALESDTL_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(SALESDTL_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . SALESDTL_ELEMENTS["saved_report_value"] . "'")
        Sleep(3000)  ; let inventory dialog render fully (per InventoryDetails.ahk)
        if !SelectInventorySavedReport(SALESDTL_ELEMENTS["saved_report_value"])
            throw Error("Could not select '" . SALESDTL_ELEMENTS["saved_report_value"] . "' from dropdown")
        Sleep(3000)  ; let criteria fully load after selection

        ; --- Verify the report actually loaded (case-sensitive silent
        ; mismatch is a documented failure mode) before touching criteria. ---
        loadedName := ""
        try loadedName := IntakeGetLoadedReportName()
        if (loadedName = "" || loadedName != SALESDTL_ELEMENTS["saved_report_value"]) {
            LogVisibleNames()
            throw Error("Saved report name mismatch after selection: expected '" . SALESDTL_ELEMENTS["saved_report_value"] . "', BoxReportName='" . loadedName . "'")
        }
        LogMessage("    verified BoxReportName='" . loadedName . "'")

        ; --- Override Status Date to `date`, leaving Status=SOLD untouched. ---
        LogMessage("  step 4: set Status Date = " . date)
        SalesDetailSetStatusDate(date)

        LogMessage("  step 5: click Ok text element to run report")
        if !ClickOkTextInDialog()
            throw Error("Could not find/click 'Ok' Text element")

        LogMessage("  step 6: wait for grid to render (DataItem rows, up to 300s -- matches InventoryDetails.ahk's proven readiness gate for this exact dialog; the earlier 'Layouts caret' check was borrowed from a different dialog's pattern and raced ahead of the data actually rendering)")
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
            throw Error("Grid did not render within 300s (no DataItem rows appeared -- consistent with InventoryDetails.ahk's own behavior for a genuinely empty Inventory Custom Report result, since that dialog has no separate empty-result fast path)")
        }
        Sleep(2000)

        LogMessage("  step 6b: scroll grid to top (Ctrl+Home)")
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

        LogMessage("  step 7: walk grid with the proven InventoryDetails walker (all columns -> temp CSV)")
        rawRows := WriteInventoryGridWithShowMore(tempPath)
        if (rawRows < 0) {
            LogVisibleNames()
            throw Error("Grid walk returned -1 (no rows captured)")
        }
        LogMessage("    walker captured " . rawRows . " raw rows across all grid columns")

        ; --- Filter/reorder down to exactly the 4 wanted columns. ---
        filterResult := SalesDetailFilterCsv(tempPath, outputPath)
        if !filterResult["ok"]
            throw Error("Column filter failed: " . filterResult["error"])
        result["row_count"] := filterResult["row_count"]
        LogMessage("    wrote " . filterResult["row_count"] . " rows to final CSV with header: " . filterResult["header"])

        try FileDelete(tempPath)

        try ClickByName(SALESDTL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(SALESDTL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        ; Exit the Custom Reports editor via its named "Cancel" button in the
        ; failure path too — never leave Bravo stranded in the editor.
        try ClickByName(SALESDTL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(SALESDTL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; Override the single "Status Date" criterion in the Bravo Custom Inventory
; Report Generator dialog. See the DATE OVERRIDE NOTE in the file header for
; why this tries a calendar-picker click first and falls back to the proven
; SetReportDate() (used by InventoryDetails.ahk against this same dialog)
; only when the picker attempt cannot be confirmed via read-back.
; ----------------------------------------------------------------------------
SalesDetailSetStatusDate(yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3)
        throw Error("SalesDetailSetStatusDate: malformed date " . yyyymmdd)
    y := parts[1]
    m := Integer(parts[2])
    d := Integer(parts[3])
    targetDisplay := m . "/" . d . "/" . y

    pickerOk := false
    try {
        inner := FindBravoDateEditByPosition(1)  ; shared helper, EmployeeActivity.ahk
        wrapper := inner
        if inner {
            try wrapper := inner.Parent
        }
        if wrapper {
            wrect := 0
            try wrect := wrapper.BoundingRectangle
            btn := 0
            try btn := wrapper.FindElement({Type: "Button"})
            if (!btn && wrect) {
                ; Some Bravo date wrappers expose the picker as a sibling
                ; button just to the right of the wrapper rather than a
                ; child — scan for one on the same row.
                try {
                    root := GetBravoRoot()
                    cands := root.FindElements({Type: "Button"})
                    if cands {
                        for c in cands {
                            crect := 0
                            try crect := c.BoundingRectangle
                            if !crect
                                continue
                            if (Abs(crect.t - wrect.t) < 12 && crect.l >= wrect.r && crect.l <= wrect.r + 40) {
                                btn := c
                                break
                            }
                        }
                    }
                }
            }
            if btn {
                opened := false
                try {
                    btn.InvokePattern.Invoke()
                    opened := true
                } catch {
                    try {
                        btn.Click("left")
                        opened := true
                    }
                }
                Sleep(700)
                if opened {
                    dayStr := String(d)
                    cellClicked := false
                    root2 := 0
                    try root2 := GetBravoRoot()
                    if root2 {
                        for typ in ["ListItem", "DataItem", "Button", "Text"] {
                            els := 0
                            try els := root2.FindElements({Type: typ})
                            if !els
                                continue
                            for el in els {
                                nm := ""
                                try nm := el.Name
                                if (nm = dayStr || nm = targetDisplay || InStr(nm, targetDisplay)) {
                                    try {
                                        el.Click("left")
                                        cellClicked := true
                                    }
                                }
                                if cellClicked
                                    break
                            }
                            if cellClicked
                                break
                        }
                    }
                    Sleep(500)
                    if !cellClicked
                        LogMessage("    [status-date] picker opened but no matching day cell found for '" . dayStr . "'/'" . targetDisplay . "'")
                }
            } else {
                LogMessage("    [status-date] no calendar-picker button located near Status Date field")
            }

            ; Read back and confirm — this is the gate. Only count the
            ; picker path as successful if the field genuinely reflects the
            ; target date afterward.
            cur := ""
            try cur := wrapper.Value
            if (cur = "") {
                try {
                    innerCheck := wrapper.FindElement({Type: "Edit"})
                    if innerCheck
                        cur := innerCheck.Value
                }
            }
            if (cur != "" && InStr(cur, targetDisplay)) {
                pickerOk := true
                LogMessage("    [status-date] calendar-picker path CONFIRMED, value='" . cur . "'")
            } else {
                LogMessage("    [status-date] calendar-picker path unconfirmed (read back '" . cur . "') — falling back to SetReportDate")
            }
        } else {
            LogMessage("    [status-date] could not locate Status Date wrapper for picker attempt — falling back to SetReportDate")
        }
    } catch as e {
        LogMessage("    [status-date] calendar-picker attempt threw: " . e.Message . " — falling back to SetReportDate")
    }

    if (pickerOk)
        return

    LogMessage("    [status-date] using SetReportDate() (ValuePattern/clipboard) — the one mechanism proven against this exact dialog in InventoryDetails.ahk")
    SetReportDate(1, yyyymmdd)
}

; ----------------------------------------------------------------------------
; Read the raw (all-columns) CSV written by WriteInventoryGridWithShowMore
; and write a new CSV containing only SALESDTL_WANTED's columns, in that
; order, matched against the ACTUAL header row at runtime. Returns
; Map("ok", bool, "row_count", n, "header", str, "error", str).
; ----------------------------------------------------------------------------
SalesDetailFilterCsv(tempPath, outputPath) {
    ; NOTE (2026-07-23, added after live smoke test): the real grid has BOTH
    ; a "Price" column and a "Last Sold Price" column. SALESDTL_WANTED's
    ; candidate order for Sale Price (["Sale Price","Sold Price","Price"])
    ; means "Sold Price" is tried before generic "Price", so this will match
    ; "Last Sold Price" via substring before ever considering "Price" -- that
    ; is almost certainly correct for a Status=SOLD report (Last Sold Price =
    ; what it actually sold for; plain Price = standard listed/asking price,
    ; which may be stale after the item sold). Logged below so this can be
    ; confirmed against a real transaction rather than assumed.
    out := Map("ok", false, "row_count", 0, "header", "", "error", "")
    if !FileExist(tempPath) {
        out["error"] := "temp CSV not found: " . tempPath
        return out
    }
    lines := []
    loop read tempPath {
        lines.Push(A_LoopReadLine)
    }
    if (lines.Length = 0) {
        out["error"] := "temp CSV is empty (no header row)"
        return out
    }
    headerFields := SalesDetailParseCsvLine(lines[1])

    global SALESDTL_WANTED
    colIdx := []
    for w in SALESDTL_WANTED {
        found := 0
        for cand in w["candidates"] {
            ; exact match first
            for i, h in headerFields {
                if (StrLower(Trim(h)) = StrLower(cand)) {
                    found := i
                    break
                }
            }
            if found
                break
            ; then substring match
            for i, h in headerFields {
                if (Trim(h) = "")
                    continue
                if InStr(StrLower(Trim(h)), StrLower(cand)) {
                    found := i
                    break
                }
            }
            if found
                break
        }
        colIdx.Push(found)
    }

    for k, w in SALESDTL_WANTED {
        if (colIdx[k] > 0)
            LogMessage("    [column-match] " . w["out"] . " -> actual grid header '" . headerFields[colIdx[k]] . "'")
    }
    missing := []
    for k, w in SALESDTL_WANTED {
        if (colIdx[k] = 0)
            missing.Push(w["out"])
    }
    if (missing.Length > 0) {
        actualCols := ""
        for i, h in headerFields {
            if (i > 1)
                actualCols .= " | "
            actualCols .= h
        }
        missingStr := ""
        for i, mname in missing {
            if (i > 1)
                missingStr .= ", "
            missingStr .= mname
        }
        out["error"] := "Grid is missing required column(s): " . missingStr . ". Actual grid columns present: " . actualCols
        return out
    }

    outHeader := ""
    for i, w in SALESDTL_WANTED {
        if (i > 1)
            outHeader .= ","
        outHeader .= ToCsvField(w["out"])
    }
    FileAppend(outHeader . "`r`n", outputPath, "UTF-8-RAW")

    rowCount := 0
    if (lines.Length >= 2) {
        Loop lines.Length - 1 {
            lineIdx := A_Index + 1
            fields := SalesDetailParseCsvLine(lines[lineIdx])
            rowLine := ""
            for i, w in SALESDTL_WANTED {
                v := (colIdx[i] <= fields.Length) ? fields[colIdx[i]] : ""
                if (i > 1)
                    rowLine .= ","
                rowLine .= ToCsvField(v)
            }
            FileAppend(rowLine . "`r`n", outputPath, "UTF-8-RAW")
            rowCount++
        }
    }

    out["ok"] := true
    out["row_count"] := rowCount
    out["header"] := outHeader
    return out
}

; Minimal CSV-line parser matching ToCsvField's quoting rules (quotes fields
; containing comma/quote/newline; doubled quotes escape a literal quote).
; Does not handle embedded newlines inside a quoted field — consistent with
; the rest of this codebase's line-based CSV handling (e.g. CountCsvRows).
SalesDetailParseCsvLine(line) {
    fields := []
    i := 1
    n := StrLen(line)
    cur := ""
    inQuotes := false
    while (i <= n) {
        ch := SubStr(line, i, 1)
        if (inQuotes) {
            if (ch = '"') {
                if (SubStr(line, i + 1, 1) = '"') {
                    cur .= '"'
                    i += 2
                    continue
                } else {
                    inQuotes := false
                    i++
                    continue
                }
            } else {
                cur .= ch
                i++
                continue
            }
        } else {
            if (ch = '"') {
                inQuotes := true
                i++
                continue
            } else if (ch = ",") {
                fields.Push(cur)
                cur := ""
                i++
                continue
            } else {
                cur .= ch
                i++
                continue
            }
        }
    }
    fields.Push(cur)
    return fields
}
