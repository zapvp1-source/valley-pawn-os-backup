; ============================================================================
; reports/CustomerLoyalty.ahk   (ADDITIVE — 2026-09-30, v2 same day)
;
; Pipeline cell: customer-loyalty
;   Trigger "date" field carries the CUSTOMER NAME exactly as Bravo shows it,
;   e.g. "EMMETT LOONEY". Optional "|report=<saved Customers report>" and
;   "|since=YYYY-MM-DD" (date criterion for that report; default 2024-01-01).
;
; WHAT IT DOES (Joshua 9/30: "look up the customer, open the account, there is a
; Customer Loyalty tile"):
;   Customers -> Custom Reports -> saved report that lists the customer
;   ("Claude Forfeiture Winback Comparison", Last Time In > since) -> Ok ->
;   grid header auto-filter on Name = the customer -> click the row ->
;   customer detail view -> button "Customer Loyalty Report" (proven name,
;   see chekkit-invites-fix-2026-06-08 diag) -> Report Preview -> Continuous
;   Scrolling OFF -> Export... -> CSV -> Done.
;
; v1 (earlier today) cloned the Reports-sidebar pattern; the tile is NOT in the
; Reports sidebar, so it failed. Reuses helpers already loaded by the watcher:
;   IntakeSelectSavedReportCommitted / IntakeGetLoadedReportName /
;   IntakeClickOkVerified (IntakeDetail.ahk), SetReportDate (EmployeeActivity),
;   SetExportFormatCsv / SetExportFilePath / UncheckOpenAfterExport / WaitForFile,
;   FwbResolveSavedName (ForfeitureWinback.ahk), EnsureStore, BackToDashboard.
; Output: <today>_<STORE>_customer-loyalty-<name-slug>.csv
; ============================================================================
#Requires AutoHotkey v2.0

PullCustomerLoyalty(store, spec, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "customer-loyalty",
        "store",       store,
        "date",        spec,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )
    customerName := ""
    reportName := "Claude Forfeiture Winback Comparison"
    since := "2024-01-01"
    buttonName := "Customer Loyalty Report"
    urlToken := "Knowledge"
    tag := "customer-loyalty"
    for part in StrSplit(spec, "|") {
        part := Trim(part)
        if RegExMatch(part, "i)^report=(.+)$", &mr)
            reportName := Trim(mr[1])
        else if RegExMatch(part, "i)^since=(\d{4}-\d{2}-\d{2})$", &ms)
            since := ms[1]
        else if RegExMatch(part, "i)^button=(.+)$", &mb)
            buttonName := Trim(mb[1])
        else if RegExMatch(part, "i)^url=(.+)$", &mu)
            urlToken := Trim(mu[1])
        else if RegExMatch(part, "i)^tag=([A-Za-z0-9_-]+)$", &mt)
            tag := Trim(mt[1])
        else if (part != "" && customerName = "")
            customerName := part
    }
    if (customerName = "")
        return Fail(result, started, "customer name missing (put it in the trigger date field)")
    slug := RegExReplace(StrLower(customerName), "[^a-z0-9]+", "-")
    outputPath := outputDir . "\" . OutputFilename(FormatTime(, "yyyy-MM-dd"), store, tag . "-" . slug)
    LogMessage("[" . store . "] CustomerLoyalty name='" . customerName . "' via '" . reportName . "' since " . since . " -> " . outputPath)

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

    try {
        ; ---- 1. Customers -> Custom Reports -> saved report -> Ok --------------
        LogMessage("  step 1: open Customers")
        ClickByName("Customers", 8000)
        Sleep(1500)
        DismissPopups()
        LogMessage("  step 2: Custom Reports")
        ClickByName("Custom Reports", 5000)
        Sleep(2000)
        realName := FwbResolveSavedName(reportName)
        if (realName = "")
            realName := reportName
        selected := false
        Loop 3 {
            IntakeSelectSavedReportCommitted("Choose Saved Report", realName)
            Sleep(1500)
            loaded := Trim(IntakeGetLoadedReportName())
            LogMessage("    [saved-report] BoxReportName='" . loaded . "'")
            if (loaded = realName || loaded = "") {
                selected := true
                break
            }
            Sleep(800)
        }
        if !selected
            throw Error("Could not commit saved report '" . realName . "'")
        try SetReportDate(1, since)
        Sleep(800)
        LogMessage("  step 3: Ok (verified)")
        IntakeClickOkVerified()
        if !FindByName("Layouts", 60000)
            throw Error("Customers list did not render within 60s")
        Sleep(4000)

        ; ---- 2+3. Find the customer's row in the (virtualized) grid and click it ----
        ; Cell names look like "Row N of TOTAL, Column <Label>, Column i of n: <value>".
        ; The grid is sorted by name; we scroll through it with the ScrollPattern
        ; (same technique as FwbWriteGrid) until a cell value equals the name.
        LogMessage("  step 4: locate row for '" . customerName . "'")
        anyRows := false
        Loop 60 {
            try {
                root := GetBravoRoot()
                items := root.FindElements({Type: "DataItem"})
                anyRows := (items && items.Length > 0)
            }
            if anyRows
                break
            Sleep(1000)
        }
        if !anyRows
            throw Error("Customers grid never rendered rows for '" . reportName . "'")
        scrollContainer := 0
        totalRows := 0
        try {
            root := GetBravoRoot()
            probe := root.FindElement({Type: "DataItem"})
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
        target := 0
        ecx := 0
        ecy := 0
        pct := 0.0
        passes := 0
        want := StrUpper(Trim(customerName))
        Loop 400 {
            passes++
            visible := 0
            root := GetBravoRoot()
            items := root.FindElements({Type: "DataItem"})
            for di in items {
                kids := 0
                try kids := di.FindElements({Scope: 2})
                if (!kids || kids.Length = 0)
                    continue
                visible++
                for k in kids {
                    kn := ""
                    try kn := k.Name
                    if RegExMatch(kn, "Row (\d+) of (\d+)", &m) {
                        if (Integer(m[2]) > totalRows)
                            totalRows := Integer(m[2])
                    }
                    cp := InStr(kn, ": ", false, -1)
                    if (cp > 0 && StrUpper(Trim(SubStr(kn, cp + 2))) = want) {
                        target := di
                        break
                    }
                }
                if target
                    break
            }
            if target
                break
            if (totalRows <= 0 || visible <= 0)
                throw Error("grid rows unreadable")
            step := (visible * 0.85 / totalRows) * 100
            if (step < 0.2)
                step := 0.2
            if (pct >= 100)
                break
            pct := pct + step
            if (pct > 100)
                pct := 100
            if scrollContainer {
                try scrollContainer.ScrollPattern.SetScrollPercent(pct, -1)
            } else {
                Send("{PgDn}")
            }
            Sleep(350)
        }
        LogMessage("    grid total=" . totalRows . " passes=" . passes . " found=" . (target ? "yes" : "no"))
        if !target
            throw Error("'" . customerName . "' not found in " . totalRows . " rows of '" . reportName . "'")
        LogMessage("  step 5: select the customer row (real mouse click on the row cell)")
        try target.ScrollIntoView()
        Sleep(450)
        r := 0
        try r := target.BoundingRectangle
        if (r && r.b > r.t) {
            ecx := (r.l + r.r) // 2
            ecy := (r.t + r.b) // 2
            MouseMove(ecx, ecy, 10)
            Sleep(150)
            Click(ecx, ecy)
            LogMessage("    REAL-clicked row at " . ecx . "," . ecy)
        } else {
            try target.SelectionItemPattern.Select()
            LogMessage("    SelectionItemPattern.Select() (no rect)")
        }
        Sleep(2500)
        DismissPopups()
        fullName := ""
        try {
            root := GetBravoRoot()
            for t in root.FindElements({Type: "Text"}) {
                aid := ""
                try aid := t.AutomationId
                if (aid = "textFullName") {
                    try fullName := t.Name
                    break
                }
            }
        }
        LogMessage("    detail view textFullName='" . fullName . "'")
        if (fullName = "" || StrUpper(fullName) != want) {
            ; selection may lag one click behind; click the same spot once more
            try Click(ecx, ecy)
            Sleep(2500)
            try {
                root := GetBravoRoot()
                for t in root.FindElements({Type: "Text"}) {
                    aid := ""
                    try aid := t.AutomationId
                    if (aid = "textFullName") {
                        try fullName := t.Name
                        break
                    }
                }
            }
            LogMessage("    detail view (2nd click) textFullName='" . fullName . "'")
        }
        if (fullName != "" && StrUpper(fullName) != want)
            throw Error("detail view shows '" . fullName . "', expected '" . customerName . "'")
        ScreenshotToFile("detail")

        ; ---- 4. Customer Loyalty Report -> (optional date dialog) -> BROWSER (SSRS) -> xlsx ----
        ; "Customer Loyalty Report" is a Bravo Business Intelligence (SSRS) report: like
        ; Company KPIs it opens in the VM's default browser. Reuse the CompanyKpis.ahk
        ; helpers: date dialog by calendar walk, read the rendered URL from the omnibox,
        ; swap to EXCELOPENXML, download, move.
        outputPath := RegExReplace(outputPath, "\.csv$", ".xlsx")
        dlDirs := CkDownloadDirs()
        snapBefore := CkSnapshotReportFilesMulti(dlDirs)
        ClCloseStaleLoyaltyWindows()
        LogMessage("  step 6: click '" . buttonName . "' (real mouse click)")
        btn := FindByName(buttonName, 8000)
        if !btn
            throw Error("'" . buttonName . "' button not found on the detail view")
        br := 0
        try br := btn.BoundingRectangle
        if (br && br.b > br.t) {
            bx := (br.l + br.r) // 2
            by := (br.t + br.b) // 2
            MouseMove(bx, by, 10)
            Sleep(150)
            Click(bx, by)
            LogMessage("    REAL-clicked button at " . bx . "," . by)
        } else {
            btn.Click()
            LogMessage("    UIA-clicked button (no rect)")
        }
        Sleep(2500)
        if CkWaitForDateDialog(4000) {
            LogMessage("    date dialog present -> calendar walk " . since . " .. yesterday")
            yday := FormatTime(DateAdd(A_Now, -1, "Days"), "yyyy-MM-dd")
            if !CkSetDateByCalendar(1, since)
                throw Error("Failed to set Start Date via calendar")
            if !CkSetDateByCalendar(2, yday)
                throw Error("Failed to set End Date via calendar")
            if !CkClickOk(6000)
                throw Error("Ok not clickable on the loyalty date dialog")
        } else {
            LogMessage("    no date dialog (report launched directly)")
        }
        LogMessage("  step 7: wait for the browser to render the report")
        renderedUrl := ""
        try {
            for exe in ["chrome.exe", "msedge.exe"] {
                for hwnd in WinGetList("ahk_exe " . exe) {
                    t := ""
                    try t := WinGetTitle("ahk_id " . hwnd)
                    LogMessage("    [browser-win] " . exe . " '" . t . "'")
                }
            }
        }
        deadline := A_TickCount + 90000
        loop {
            renderedUrl := ClReadLoyaltyUrl(urlToken)
            if (renderedUrl != "" || A_TickCount > deadline)
                break
            Sleep(3000)
        }
        if (renderedUrl = "") {
            ScreenshotToFile("no-browser-url")
            throw Error("no Loyalty report URL appeared in a browser address bar within 90s")
        }
        LogMessage("    rendered url: " . renderedUrl)
        exportUrl := CkBuildExportUrl(renderedUrl, "", "")
        LogMessage("    export url: " . exportUrl)
        if !CkNavigateBrowser(exportUrl)
            throw Error("could not drive the browser to the export URL")
        downloadedPath := CkWaitForNewFileMulti(dlDirs, snapBefore, 120000)
        if (downloadedPath = "")
            throw Error("no new xlsx appeared in Downloads within 120s")
        firstByte := PeekFirstByte(downloadedPath)
        if (firstByte = "<")
            throw Error("downloaded file is HTML (auth/render failed): " . downloadedPath)
        try FileMove(downloadedPath, outputPath, true)
        if !FileExist(outputPath)
            throw Error("FileMove to " . outputPath . " did not produce a file")
        sz := 0
        try sz := FileGetSize(outputPath)
        LogMessage("    xlsx " . sz . " bytes -> " . outputPath)
        result["row_count"] := sz
        ClCloseStaleLoyaltyWindows()

        ; ---- 5. exit: Esc, Done x N, then out of Customers -------------------------
        LogMessage("  step 8: exit")
        try ActivateBravo()
        Sleep(400)
        try ClickByName("Done", 3000)
        Sleep(800)
        try BackToDashboard(8)
        Sleep(500)
        DismissPopups()
    } catch as e {
        ScreenshotToFile("customer-loyalty-error")
        LogVisibleNames(80)
        try Send("{Escape}")
        Sleep(400)
        try ClickByName("Done", 2000)
        Sleep(400)
        try ClickByName("Cancel", 2000)
        Sleep(400)
        try ClickByName("Cancel", 2000)
        Sleep(400)
        try BackToDashboard(8)
        return Fail(result, started, "customer-loyalty failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . outputPath . ", " . result["duration_ms"] . "ms")
    return result
}

; Read a rendered Customer Loyalty SSRS URL from any Chrome/Edge omnibox (needs r= GUID).
ClReadLoyaltyUrl(token := "") {
    for exe in ["chrome.exe", "msedge.exe"] {
        for hwnd in WinGetList("ahk_exe " . exe) {
            try {
                el := UIA.ElementFromHandle(hwnd)
                bar := 0
                for nm in ["Address and search bar", "Address bar", "Search or enter web address"] {
                    try bar := el.FindElement({Type: "Edit", Name: nm})
                    if bar
                        break
                }
                if !bar {
                    for e in el.FindElements({Type: "Edit"}) {
                        v := ""
                        try v := e.Value
                        if InStr(v, "bravoapplication.com") {
                            bar := e
                            break
                        }
                    }
                }
                if !bar
                    continue
                v := ""
                try v := bar.Value
                if (v = "")
                    continue
                LogMessage("    [omnibox] " . exe . " '" . SubStr(v, 1, 160) . "'")
                if (InStr(v, "bravoapplication.com") && InStr(v, "r=") && !InStr(v, "Company") && (token = "" || InStr(v, token)))
                    return v
            }
        }
    }
    return ""
}

ClCloseStaleLoyaltyWindows() {
    closed := 0
    for exe in ["chrome.exe", "msedge.exe"] {
        for hwnd in WinGetList("ahk_exe " . exe) {
            t := ""
            try t := WinGetTitle("ahk_id " . hwnd)
            if (t != "" && (InStr(t, "Loyalty") || InStr(t, "BRAVO "))) {
                try {
                    WinClose("ahk_id " . hwnd)
                    closed++
                    Sleep(200)
                }
            }
        }
    }
    if (closed)
        LogMessage("    [browser] closed " . closed . " stale Loyalty window(s)")
    return closed
}
