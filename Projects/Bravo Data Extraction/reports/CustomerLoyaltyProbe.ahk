; ============================================================================
; reports/CustomerLoyaltyProbe.ahk   (ADDITIVE — 2026-09-30, discovery cell)
;
; Pipeline cell: customer-loyalty-probe
;   Trigger "date" field carries the CUSTOMER NAME to look up, e.g. "EMMETT LOONEY".
;
; Purpose: map Bravo's per-customer "Customer Loyalty" report WITHOUT anyone
; driving the screen (Joshua 9/30: look the customer up in the Customers search,
; open the account, there is a Customer Loyalty tile). Every step screenshots
; and dumps the visible UIA element names so the next handler can be written
; from the log. Nothing existing is modified.
;
; Steps: Customers sidebar -> search box = name -> Enter -> open the row ->
;        click "Customer Loyalty" -> dump everything on screen -> back out.
; ============================================================================
#Requires AutoHotkey v2.0

PullCustomerLoyaltyProbe(store, customerName, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "customer-loyalty-probe",
        "store",       store,
        "date",        customerName,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )
    slug := RegExReplace(StrLower(customerName), "[^a-z0-9]+", "-")
    outputPath := outputDir . "\" . OutputFilename(FormatTime(, "yyyy-MM-dd"), store, "customer-loyalty-probe-" . slug)
    LogMessage("[" . store . "] CustomerLoyaltyProbe name='" . customerName . "' -> " . outputPath)

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

    lines := "step,detail`r`n"
    try {
        LogMessage("  step 1: open Customers")
        ClickByName("Customers", 8000)
        Sleep(2500)
        DismissPopups()
        ScreenshotToFile("p1-customers")
        ClpDumpAll("p1-customers")

        ; --- step 2: find a search box. Prefer an Edit whose Name/AutomationId mentions search; else first Edit.
        LogMessage("  step 2: locate search box")
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        target := 0
        for el in edits {
            nm := "", aid := ""
            try nm := el.Name
            try aid := el.AutomationId
            LogMessage("    [edit] name='" . nm . "' aid='" . aid . "'")
            if (!target && (InStr(nm, "earch") || InStr(aid, "earch")))
                target := el
        }
        if (!target && edits.Length >= 1)
            target := edits[1]
        if !target
            throw Error("no Edit control found on the Customers screen")
        tn := "", ta := ""
        try tn := target.Name
        try ta := target.AutomationId
        LogMessage("    using edit name='" . tn . "' aid='" . ta . "'")
        try {
            target.Value := customerName
            LogMessage("    [UIA] set search = " . customerName)
        } catch {
            try target.Focus()
            Sleep(150)
            Send("^a")
            Sleep(50)
            prev := ""
            try prev := A_Clipboard
            A_Clipboard := customerName
            ClipWait(2)
            Send("^v")
            Sleep(200)
            A_Clipboard := prev
            LogMessage("    [UIA] pasted search = " . customerName)
        }
        Sleep(400)
        try target.Focus()
        Send("{Enter}")
        Sleep(3500)
        DismissPopups()
        ScreenshotToFile("p2-search")
        ClpDumpAll("p2-search")

        ; --- step 3: open the customer's row / account
        LogMessage("  step 3: open the account for '" . customerName . "'")
        opened := false
        try {
            DoubleClickByName(customerName, 4000)
            opened := true
            LogMessage("    double-clicked exact name")
        } catch as e {
            LogMessage("    exact-name double-click failed: " . e.Message)
        }
        if !opened {
            ; try the first DataItem row
            try {
                root := GetBravoRoot()
                rows := root.FindElements({Type: "DataItem"})
                if (rows && rows.Length >= 1) {
                    rows[1].Click()
                    Sleep(300)
                    rows[1].Click()
                    opened := true
                    LogMessage("    clicked first DataItem row (x2)")
                }
            } catch as e {
                LogMessage("    DataItem click failed: " . e.Message)
            }
        }
        Sleep(3500)
        DismissPopups()
        ScreenshotToFile("p3-account")
        ClpDumpAll("p3-account")

        ; --- step 4: click the Customer Loyalty tile
        LogMessage("  step 4: click Customer Loyalty")
        clicked := false
        for cand in ["Customer Loyalty", "Loyalty", "Customer Loyalty Report"] {
            try {
                ClickByName(cand, 3000)
                clicked := true
                LogMessage("    clicked '" . cand . "'")
                break
            } catch as e {
                LogMessage("    '" . cand . "' not found: " . e.Message)
            }
        }
        Sleep(6000)
        DismissPopups()
        ScreenshotToFile("p4-loyalty")
        ClpDumpAll("p4-loyalty")

        ; --- step 5: write everything visible to the CSV so it is data, not just log
        root := GetBravoRoot()
        n := 0
        for typ in ["Text", "Edit", "DataItem", "Button", "Hyperlink"] {
            els := 0
            try els := root.FindElements({Type: typ})
            if !els
                continue
            for el in els {
                nm := "", v := "", y := "", x := ""
                try nm := el.Name
                try v := el.Value
                try y := el.BoundingRectangle.t
                try x := el.BoundingRectangle.l
                if (nm = "" && v = "")
                    continue
                lines .= typ . "," . y . "," . x . "," . ClpCsv(nm) . "," . ClpCsv(v) . "`r`n"
                n++
                if (n > 600)
                    break
            }
        }
        FileAppend(lines, outputPath, "UTF-8-RAW")
        result["row_count"] := n
        LogMessage("    wrote " . n . " element rows")

        ; --- step 6: back out (Done / Cancel / logo) — best effort
        for b in ["Done", "Cancel", "Close", "Back"] {
            try ClickByName(b, 1500)
            Sleep(600)
        }
        try BackToDashboard()
    } catch as e {
        ScreenshotToFile("probe-error")
        LogVisibleNames(80)
        try ClickByName("Cancel", 1500)
        try ClickByName("Done", 1500)
        try BackToDashboard()
        FileAppend(lines, outputPath, "UTF-8-RAW")
        return Fail(result, started, "probe failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: probe wrote " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

ClpCsv(s) {
    s := StrReplace(s, "`r", " ")
    s := StrReplace(s, "`n", " ")
    return "`"" . StrReplace(s, "`"", "`"`"") . "`""
}

; Dump every named element of the common types with position + AutomationId (wider than LogVisibleNames).
ClpDumpAll(tag) {
    try {
        root := GetBravoRoot()
        cnt := 0
        for typ in ["Button", "Hyperlink", "Text", "Edit", "DataItem", "TabItem", "ListItem", "TreeViewItem", "Group", "Custom"] {
            els := 0
            try els := root.FindElements({Type: typ})
            if !els
                continue
            for el in els {
                nm := "", aid := "", v := "", y := "", x := ""
                try nm := el.Name
                try aid := el.AutomationId
                try v := el.Value
                if (nm = "" && aid = "" && v = "")
                    continue
                try y := el.BoundingRectangle.t
                try x := el.BoundingRectangle.l
                LogMessage("    [" . tag . "] " . typ . " y=" . y . " x=" . x . " name='" . nm . "' aid='" . aid . "' value='" . v . "'")
                cnt++
                if (cnt > 400)
                    return
            }
        }
    } catch as e {
        LogMessage("    [" . tag . "] dump failed: " . e.Message)
    }
}
