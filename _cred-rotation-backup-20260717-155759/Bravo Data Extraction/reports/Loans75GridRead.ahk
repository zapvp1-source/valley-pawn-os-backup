; ============================================================================
; reports/Loans75GridRead.ahk
;
; Pipeline cell: loans75-gridread  (Phase 0 of the Reliable-Extraction program)
;
; PROVES THE GRID-READ APPROACH: renders the "75 Days Past Due" saved Ad Hoc
; loan report and reads the FULL ROWS straight off the on-screen grid via UIA,
; then writes the CSV itself. It NEVER opens Bravo's Export Document dialog —
; so the Continuous-Scrolling / export hang (the #1 failure class) cannot occur.
;
; ADDITIVE: a NEW handler + NEW cell name. Does NOT touch the existing
; loans-75-days-past-due cell / Loans75DaysPastDue.ahk (which reads count+sum).
;
; Output CSV: <date>_<STORE>_loans75-gridread.csv  (header + one row per grid row)
; ============================================================================

#Requires AutoHotkey v2.0

PullLoans75GridRead(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "loans75-gridread",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "loans75-gridread")
    LogMessage("[" . store . "] Loans75GridRead date=" . date . " -> " . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    rowCount := 0
    written  := 0

    try {
        LogMessage("  step 1: open Loans/Buys")
        ClickByName("Loans/Buys", 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName("Custom Reports", 6000)
        Sleep(1500)

        LogMessage("  step 3: select '75 Days Past Due' saved report (proven routine)")
        SelectSavedReport("Choose Saved Report", "75 Days Past Due")
        Sleep(900)

        LogMessage("  step 4: click Ok")
        ClickByName("Ok", 5000)
        Sleep(3500)
        DismissPopups()

        ; ---- READ the grid rows (no export) ----
        root := GetBravoRoot()
        rows := []
        try rows := root.FindElements({Type: "DataItem"})
        rowCount := (rows) ? rows.Length : 0
        LogMessage("  DataItem rows found: " . rowCount)

        ; Discovery: if 0 rows, dump type counts so we can see where the data lives.
        if (rowCount = 0) {
            LogMessage("  0 DataItem rows — dumping UIA type counts for inspection")
            try DumpAllUiaTypeCounts()
        }

        ; Dump the first row's Custom cells (name+value) so we can verify the layout.
        if (rowCount >= 1) {
            first := rows[1]
            try {
                cc := first.FindElements({Type: "Custom"})
                LogMessage("  row[1] Custom cells=" . (cc ? cc.Length : 0))
                i := 0
                for c in cc {
                    i += 1
                    if (i > 12)
                        break
                    nm := "", vl := ""
                    try nm := c.Name
                    try vl := c.Value
                    LogMessage("    cust[" . i . "] name='" . nm . "' value='" . vl . "'")
                }
            }
        }

        ; Derive column headers from row[1]'s Custom cells — the cell .Name encodes
        ; "... Column <Header>, Column N of M: <value>". Produces a real columned CSV.
        headers := []
        if (rowCount >= 1) {
            try {
                hc := rows[1].FindElements({Type: "Custom"})
                for c in hc {
                    nm := ""
                    try nm := c.Name
                    h := "col" . (headers.Length + 1)
                    if RegExMatch(nm, "Column\s+(.+?),\s+Column\s+\d+\s+of\s+\d+", &mh)
                        h := Trim(mh[1])
                    headers.Push(h)
                }
            }
            LogMessage("  headers: " . CsvJoinGR(headers))
        }
        hdr := "store,date"
        for h in headers
            hdr .= "," . ToCsvField(h)
        FileAppend(hdr . "`r`n", outputPath, "UTF-8-RAW")

        ; One CSV line per grid row, one column per cell value.
        for row in rows {
            vals := HarvestRowValuesGR(row)
            line := ToCsvField(store) . "," . ToCsvField(date)
            for v in vals
                line .= "," . ToCsvField(v)
            FileAppend(line . "`r`n", outputPath, "UTF-8-RAW")
            written += 1
            if (written <= 2)
                LogMessage("  row " . written . " cols=" . vals.Length . ": " . CsvJoinGR(vals))
        }
        LogMessage("  rows written: " . written)

        ; ---- clean exit, no export ----
        try ClickByName("Cancel", 3000)
        Sleep(700)
        try ClickByName("Cancel", 3000)
        Sleep(700)
        try BackToDashboard()

    } catch as e {
        try LogVisibleNames()
        try BackToDashboard()
        return Fail(result, started, "grid-read sequence failed: " . e.Message)
    }

    result["row_count"]   := written
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: DataItem rows=" . rowCount . " written=" . written . ", " . result["duration_ms"] . "ms")
    return result
}

; Return an array of cell values for one grid row. DevExpress grid cells are
; exposed as "Custom" controls; the value lives in .Value (clean) with a
; fallback to the trailing text of the verbose .Name. Falls back to Edit cells.
HarvestRowValuesGR(row) {
    vals := []
    cells := ""
    try cells := row.FindElements({Type: "Custom"})
    if (!cells || cells.Length = 0) {
        try cells := row.FindElements({Type: "Edit"})
    }
    if (!cells)
        return vals
    for k in cells {
        v := ""
        try v := k.Value
        if (v = "") {
            try v := k.Name
            if RegExMatch(v, "of\s+\d+:\s+(.*)$", &mv)
                v := Trim(mv[1])
            if (v = "TextEdit" || v = "BaseEdit" || v = "ButtonEdit")
                v := ""
        }
        vals.Push(v)
    }
    return vals
}

; Join an array into a " | " preview string (logging only).
CsvJoinGR(arr) {
    out := ""
    for a in arr
        out := (out = "") ? a : out . " | " . a
    return out
}
