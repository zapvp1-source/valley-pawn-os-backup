; ============================================================================
; reports/CompanyKpis.ahk
;
; Pulls the Bravo "Company Performance" (Company KPIs) SSRS report for a date
; window and saves it as a downloadable .xlsx.
;
; ---------------------------------------------------------------------------
; WHY THE DASHBOARD DATE-PICKER WALK (2026-07-03 rebuild)
; ---------------------------------------------------------------------------
; The raw-URL EXCELOPENXML export ("launch a fresh Edge/Chrome at the report
; URL with &rs:Format=EXCELOPENXML") RELIABLY FAILS for these matrix/date
; windows: the fetch either times out or the server returns rsProcessingAborted
; (see logs/company-kpis-june-recon-2026-07-02.log — every direct-URL attempt
; timed out with "No new CSV appeared in Downloads within 120s"). The old stub
; also hardcoded a STALE per-render GUID (r=43058c4d-...) that no longer maps
; to a valid cached instance.
;
; The path that WORKS (proven on the island 2026-07-03, June 2026 window, xlsx
; matches Bravo to the penny: company Net Revenue $230,094.28):
;   1. Bravo Dashboard -> click the "Company KPIs" button (Reporting Pro).
;   2. A "Select Date Range" modal opens with Start Date / End Date fields.
;      These fields are MASKED date edits — TYPING / ValuePattern is unreliable
;      (a typed value garbles to e.g. "6/3/2000" with a red validation error,
;      and an INVALID value BLOCKS BOTH Ok AND Cancel, wedging the dialog).
;      => We NEVER type. We drive the CALENDAR PICKER: open each field's
;         dropdown, read the "Month YYYY" header, click prev/next until it
;         matches, then click the day cell.
;   3. Click Ok. Bravo hands the report off to the DEFAULT BROWSER (Chrome on
;      this VM), which renders the interactive SSRS report AND establishes the
;      Forms-auth session (.ASPXAUTH cookie). The rendered URL carries a FRESH
;      per-session render GUID (r=...) — this is the piece the direct-URL
;      approach was missing.
;   4. We read the rendered URL from the browser's address bar (omnibox), swap
;      "Render?XXX" (or "&rs:Command=Render") for
;      "&rs:Command=Render&rs:Format=EXCELOPENXML", KEEP the fresh r= GUID and
;      the StartDate/EndDate/IsPawnOn params, and navigate the SAME
;      authenticated tab to it. The browser downloads the .xlsx (~35 KB) to
;      C:\Users\joshuadavis\Downloads.
;   5. Snapshot/wait/first-byte-'<' sanity check, then FileMove to
;      <END>_<STORE>_company-kpis.xlsx.
;
; The report is COMPANY-WIDE — one fetch produces one xlsx with all 5 stores
; as columns. Use store="ALL" so the orchestrator does not ask for 5 fetches.
;
; SKILL it will power (after proof + Joshua's sign-off): monthly-analytics-report
;
; Trigger schema:
;   { "reports": [ { "name":"company-kpis", "stores":["ALL"],
;                    "date":"YYYY-MM-DD..YYYY-MM-DD" } ] }
;
; Output filename: <END_DATE>_<STORE>_company-kpis.xlsx  (STORE defaults "ALL")
; ============================================================================
#Requires AutoHotkey v2.0

global COMPANY_KPIS_SSRS_HOST := "ssrs.bravoapplication.com:9176"
global COMPANY_KPIS_DOWNLOADS_DIR := "C:\Users\joshuadavis\Downloads"
global COMPANY_KPIS_DASH_BUTTON := "Company KPIs"

; Chrome's Downloads folder on this VM is REDIRECTED to the Mac's home
; Downloads over Parallels shared folders. VERIFIED 2026-07-03 via the file's
; Properties: Location = "\\Mac\Home\Downloads" (NOT C:\Users\joshuadavis\
; Downloads — a snapshot of that found 0 files while Chrome clearly saved
; there). \\Mac\Home is the Y: mapped drive the watcher launches from, so
; Y:\Downloads == \\Mac\Home\Downloads. We poll the UNC + Y: forms first, then
; fall back to the classic profile paths. CkDownloadDirs() returns existing ones.
CkDownloadDirs() {
    cands := []
    ; Primary: the Parallels shared Mac-home Downloads (where Chrome saves).
    ; Prefer the mapped Y: form (faster than raw UNC over SMB), then UNC.
    cands.Push("Y:\Downloads")
    cands.Push("\\Mac\Home\Downloads")
    ; Secondary: OneDrive-redirected, then classic profile Downloads.
    up := EnvGet("USERPROFILE")
    if (up = "")
        up := "C:\Users\joshuadavis"
    od := EnvGet("OneDrive")
    if (od != "")
        cands.Push(od . "\Downloads")
    cands.Push(up . "\OneDrive\Downloads")
    cands.Push(up . "\Downloads")
    cands.Push(COMPANY_KPIS_DOWNLOADS_DIR)
    ; De-dup + keep only existing dirs.
    out := []
    seen := Map()
    for c in cands {
        cl := StrLower(c)
        if seen.Has(cl)
            continue
        seen[cl] := true
        if DirExist(c)
            out.Push(c)
    }
    ; If none exist (shouldn't happen), fall back to the UNC form anyway so the
    ; poll at least targets the right place once it appears.
    if (out.Length = 0)
        out.Push("\\Mac\Home\Downloads")
    return out
}

PullCompanyKpis(store, dateOrRange, outputDir) {
    global CONFIG
    started := A_TickCount
    result := Map(
        "report",      "company-kpis",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse date range ---------------------------------------------------
    startDateIso := "", endDateIso := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return CkFail(result, started, "Malformed date range: " . dateOrRange)
        startDateIso := Trim(parts[1]), endDateIso := Trim(parts[2])
    } else {
        startDateIso := dateOrRange, endDateIso := dateOrRange
    }
    if (!RegExMatch(startDateIso, "^\d{4}-\d{2}-\d{2}$") || !RegExMatch(endDateIso, "^\d{4}-\d{2}-\d{2}$"))
        return CkFail(result, started, "Invalid date(s): start=" . startDateIso . " end=" . endDateIso)

    startSsrs := CkIsoToSsrs(startDateIso)   ; 2026/6/1
    endSsrs   := CkIsoToSsrs(endDateIso)     ; 2026/6/30

    LogMessage("[" . store . "] CompanyKpis range=" . startDateIso . ".." . endDateIso)
    LogMessage("  SSRS dates: start=" . startSsrs . " end=" . endSsrs)

    outputPath := outputDir . "\" . endDateIso . "_" . store . "_company-kpis.xlsx"
    LogMessage("  output -> " . outputPath)
    ResetOutputFile(outputPath)

    ; --- Bravo prep ---------------------------------------------------------
    if !WaitForBravoWindowExists(30)
        return CkFail(result, started, "Bravo window not found")
    ActivateBravo()
    Sleep(400)
    DismissPopups()

    ; Company-wide report; store is a label only. Confirm we are logged into
    ; SOME store (any). If a login/store-select screen is up, EnsureStore("CUL")
    ; recovers it; otherwise we stay on whatever store is active.
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if IsOnLoginScreen() {
        LogMessage("  login screen visible — recovering via EnsureStore(CUL)")
        if !EnsureStore("CUL", password)
            return CkFail(result, started, "EnsureStore(CUL) failed while recovering login")
    }
    LogMessage("  store confirmed: " . GetCurrentStoreCode())

    ; --- Downloads snapshot BEFORE we trigger anything ----------------------
    dlDirs := CkDownloadDirs()
    LogMessage("  Downloads dirs polled: " . CkJoin(dlDirs, " | "))
    snapBefore := CkSnapshotReportFilesMulti(dlDirs)
    LogMessage("  Downloads pre-snapshot: " . snapBefore.Count . " existing report files")

    ; --- Drive the Dashboard + date dialog ----------------------------------
    try {
        LogMessage("  step 0: BackToDashboard")
        if !BackToDashboard(8)
            return CkFail(result, started, "BackToDashboard failed")
        Sleep(600)
        DismissPopups()

        LogMessage("  step 1: click Dashboard '" . COMPANY_KPIS_DASH_BUTTON . "' button")
        ClickByName(COMPANY_KPIS_DASH_BUTTON, 8000)
        Sleep(1500)

        ; Wait for the "Select Date Range" dialog: its two masked date edits are
        ; UIA Edit elements. We detect readiness by finding >=2 date edits.
        if !CkWaitForDateDialog(10000)
            return CkFail(result, started, "Select Date Range dialog did not appear")

        LogMessage("  step 2a: set Start Date = " . startDateIso . " via calendar walk")
        if !CkSetDateByCalendar(1, startDateIso)
            return CkFail(result, started, "Failed to set Start Date via calendar")

        LogMessage("  step 2b: set End Date = " . endDateIso . " via calendar walk")
        if !CkSetDateByCalendar(2, endDateIso)
            return CkFail(result, started, "Failed to set End Date via calendar")

        ; Close any lingering "BRAVO Company Performance" browser windows from
        ; prior renders BEFORE Ok, so the tab that opens next is unambiguously
        ; THIS run's fresh render (correct dates + fresh r= GUID). Without this,
        ; a stale tab (e.g. EndDate=7/2, dead GUID) gets picked up and the export
        ; times out. (2026-07-03)
        LogMessage("  step 2c: close stale Company Performance browser windows")
        CkCloseStaleReportWindows()

        LogMessage("  step 3: click Ok to launch report in browser")
        ; Ok is only enabled when both fields are valid. If our calendar picks
        ; are clean it will be enabled. Never proceed on a wedged dialog.
        if !CkClickOk(6000)
            return CkFail(result, started, "Ok button not clickable (dialog may be wedged / dates invalid)")
    } catch as e {
        CkRecoverToDashboard()
        return CkFail(result, started, "UIA date-dialog sequence failed: " . e.Message)
    }

    ; --- Wait for the browser to render + establish auth --------------------
    LogMessage("  step 4: waiting for browser to render 'Company Performance' report")
    renderedUrl := CkWaitForRenderedUrl(startSsrs, endSsrs, 90000)
    if (renderedUrl = "")
        return CkFail(result, started, "Browser did not render the report / could not read a Company Performance URL from the address bar within 90s")
    LogMessage("    rendered url: " . renderedUrl)

    ; --- Build the EXCELOPENXML export URL from the rendered URL -------------
    exportUrl := CkBuildExportUrl(renderedUrl, startSsrs, endSsrs)
    LogMessage("  step 5: navigate browser to EXCELOPENXML export URL")
    LogMessage("    export url: " . exportUrl)
    if !CkNavigateBrowser(exportUrl)
        return CkFail(result, started, "Could not drive the browser omnibox to the export URL")

    ; --- Wait for the new xlsx ----------------------------------------------
    LogMessage("  step 6: waiting up to 120s for new xlsx in Downloads dir(s)")
    downloadedPath := CkWaitForNewFileMulti(dlDirs, snapBefore, 120000)
    if (downloadedPath = "")
        return CkFail(result, started, "No new xlsx appeared in Downloads within 120s — check browser for an auth/render error")
    LogMessage("    downloaded: " . downloadedPath)

    firstByte := PeekFirstByte(downloadedPath)
    if (firstByte = "<")
        return CkFail(result, started, "Downloaded file looks like HTML (first byte '<') — auth/render failed. File: " . downloadedPath)

    ; xlsx is a zip; first byte should be 'P' (PK zip magic). Warn if not.
    if (firstByte != "P")
        LogMessage("    WARN: first byte is '" . firstByte . "' (expected 'P' for xlsx zip) — proceeding but verify downstream")

    try FileMove(downloadedPath, outputPath, true)
    if !FileExist(outputPath)
        return CkFail(result, started, "FileMove to " . outputPath . " did not produce a file")
    LogMessage("    moved -> " . outputPath)

    sz := 0
    try sz := FileGetSize(outputPath)
    result["row_count"]   := sz            ; bytes (xlsx has no CSV rows to count)
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . sz . " bytes, " . result["duration_ms"] . "ms")

    ; Best-effort: return Bravo to a clean Dashboard so we never strand it.
    CkRecoverToDashboard()
    return result
}

; ============================================================================
; Date-dialog calendar walk
; ============================================================================

; True once the Select Date Range dialog is up (>= 2 masked date Edit fields
; named "BravoDateEdit", OR an Ok button present).
CkWaitForDateDialog(timeoutMs) {
    deadline := A_TickCount + timeoutMs
    loop {
        n := CkCountDateEdits()
        if (n >= 2)
            return true
        if ExistsByName("Ok") && (n >= 1)
            return true
        if (A_TickCount > deadline)
            return false
        Sleep(400)
    }
}

CkCountDateEdits() {
    cnt := 0
    try {
        root := GetBravoRoot()
        for e in root.FindElements({Type: "Edit"}) {
            nm := ""
            try nm := e.Name
            if (nm != "BravoDateEdit")
                continue
            aid := ""
            try aid := e.AutomationId
            ; Count only the modal's date wrappers: empty AutomationId and on
            ; screen. Excludes the inner PART_Editor and the Dashboard's
            ; bmtbDateOfBirth clone behind the modal (see CkFindDateWrapper).
            if (aid != "")
                continue
            off := false
            try off := e.IsOffscreen
            if off
                continue
            cnt++
        }
    }
    return cnt
}

; Return the outer wrapper Edit for the date field at visual position
; (1 = leftmost = Start, 2 = End), sorted by X. Mirrors EmployeeActivity's
; FindBravoDateEditByPosition but returns the WRAPPER (so we can find its
; calendar-toggle button sibling), not the inner PART_Editor.
CkFindDateWrapper(position) {
    wrappers := []
    try {
        root := GetBravoRoot()
        for e in root.FindElements({Type: "Edit"}) {
            nm := ""
            try nm := e.Name
            if (nm != "BravoDateEdit")
                continue
            aid := ""
            try aid := e.AutomationId
            ; Skip the inner PART_Editor child.
            if (aid = "PART_Editor")
                continue
            ; CRITICAL (verified 2026-07-03): the modal's two date fields have an
            ; EMPTY AutomationId. The Dashboard's own "Birth Date" edit that sits
            ; behind the modal is ALSO Name='BravoDateEdit' but has
            ; AutomationId='bmtbDateOfBirth' and a smaller X — if we included it,
            ; sort-by-X would make it position 1 and shift Start/End. Accept ONLY
            ; empty-AutomationId wrappers so we target the modal's fields alone.
            if (aid != "")
                continue
            ; Only consider on-screen wrappers (the modal fields are visible; the
            ; hidden dashboard clones are offscreen).
            off := false
            try off := e.IsOffscreen
            if off
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            wrappers.Push(Map("elem", e, "x", rect.l, "rect", rect))
        }
    } catch as ex {
        LogMessage("    WARN CkFindDateWrapper: " . ex.Message)
        return 0
    }
    ; sort ascending by x
    i := 2
    while (i <= wrappers.Length) {
        j := i
        while (j > 1 && wrappers[j]["x"] < wrappers[j-1]["x"]) {
            t := wrappers[j], wrappers[j] := wrappers[j-1], wrappers[j-1] := t
            j--
        }
        i++
    }
    if (position < 1 || position > wrappers.Length) {
        LogMessage("    WARN CkFindDateWrapper: position " . position . " out of range (have " . wrappers.Length . ")")
        return 0
    }
    return wrappers[position]
}

; Set a date field (1=Start, 2=End) to yyyy-mm-dd purely by clicking the
; calendar picker. Never types. Returns true on success.
CkSetDateByCalendar(position, yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3)
        return false
    targetYear  := Integer(parts[1])
    targetMonth := Integer(parts[2])
    targetDay   := Integer(parts[3])

    wrap := CkFindDateWrapper(position)
    if !wrap {
        LogMessage("    ERROR: date wrapper at position " . position . " not found")
        return false
    }
    rect := wrap["rect"]

    ; Open the field's calendar dropdown. The DevExpress date edit shows a
    ; calendar glyph button at the right edge of the field; clicking it toggles
    ; the dropdown. We click a point just inside the right edge of the wrapper.
    dropBtn := CkFindDropButton(wrap["elem"])
    if dropBtn {
        try dropBtn.Click("left")
        LogMessage("    [cal] pos=" . position . " opened dropdown via drop button (PART_Item)")
    } else {
        ; Fallback: physical click on the glyph at the right edge of the field.
        gx := rect.r - 12
        gy := rect.t + (rect.b - rect.t)//2
        CkPhysClick(gx, gy)
        LogMessage("    [cal] pos=" . position . " opened dropdown via edge click at " . gx . "," . gy)
    }
    Sleep(800)

    ; ----------------------------------------------------------------------
    ; Drive the popup GEOMETRICALLY (it is UIA-invisible — see CkWalkCalendarGeom
    ; for the rationale + calibrated screen offsets).
    ;
    ; MONTH-PROBE strategy (2026-07-03): month-nav arrow clicks are sometimes
    ; dropped by DevExpress even at 800ms on deep (e.g. 24-hop) navigations, so
    ; after navigating we may be on the WRONG month. If we clicked the target day
    ; directly and it landed on an empty leading/trailing cell, the field stays
    ; blank and we can't tell which month we're on. So instead we FIRST click the
    ; 15th — a cell that is ALWAYS the current display month (never a grey
    ; leading/trailing duplicate) — which forces a value we can read to learn the
    ; ACTUAL month. We then re-navigate the residual (with generous delays),
    ; re-probe, and only once the field shows the target month/year do we click
    ; the TRUE target day. Fully self-correcting against dropped nav clicks.
    ; ----------------------------------------------------------------------
    want := targetMonth . "/" . targetDay . "/" . targetYear
    targetIdx := targetYear * 12 + (targetMonth - 1)

    ; Step A: initial blind nav from today's anchor, then probe with the 15th.
    if !CkNavMonths(rect, 0, targetIdx) {
        LogMessage("    ERROR: initial month nav failed for pos=" . position)
        return false
    }
    ; Probe loop: click 15th, read month, correct residual, up to 5 rounds.
    onTarget := false
    round := 1
    loop 5 {
        CkClickProbeCell(rect)   ; fixed r2c3 — always a current-month day
        Sleep(450)
        pv := CkReadFieldValue(wrap["elem"])
        pm := 0, pd := 0, py := 0
        if !CkParseMdy(pv, &pm, &pd, &py) {
            LogMessage("    [cal] pos=" . position . " probe round " . round . " unreadable ('" . pv . "') — reopening")
        } else {
            curIdx := py * 12 + (pm - 1)
            LogMessage("    [cal] pos=" . position . " probe round " . round . " shows month " . pm . "/" . py
                     . " (idx " . curIdx . " vs target " . targetIdx . ")")
            if (curIdx = targetIdx) {
                onTarget := true
                ; fall through to reopen + click the true target day below
            }
        }
        ; Re-open the calendar (clicking the 15th closed it) to continue.
        CkReopenCalendar(wrap, rect)
        if onTarget
            break
        ; Navigate the residual from the observed month toward target.
        obsIdx := (CkParseMdy(pv, &pm, &pd, &py)) ? (py * 12 + (pm - 1)) : 0
        if !CkNavMonths(rect, obsIdx, targetIdx) {
            LogMessage("    ERROR: residual month nav failed for pos=" . position)
            return false
        }
        if (round >= 5)
            break
        round++
    }
    if !onTarget {
        LogMessage("    ERROR pos=" . position . " could not reach target month " . targetMonth . "/" . targetYear)
        return false
    }

    ; Step B: on the correct month — click the TRUE target day and confirm.
    ; The popup is OPEN here (reopened at the end of Step A, showing the target
    ; month with the probe day highlighted). Give it a moment to settle, then
    ; click the target day. A freshly-reopened DevExpress popup can swallow the
    ; very first click, so we always settle first and, on a miss, reopen+retry.
    attempt := 1
    loop 4 {
        Sleep(600)                                   ; let the popup settle
        CkClickDayCellGeom(rect, targetYear, targetMonth, targetDay)
        Sleep(500)
        val := CkReadFieldValue(wrap["elem"])
        LogMessage("    [cal] pos=" . position . " day attempt " . attempt . " field = '" . val . "'")
        pm := 0, pd := 0, py := 0
        if CkParseMdy(val, &pm, &pd, &py) {
            if (pm = targetMonth && pd = targetDay && py = targetYear) {
                LogMessage("    [cal] pos=" . position . " CONFIRMED " . want)
                return true
            }
            ; Wrong day (e.g. still the probe's 15th/17th, or month drifted).
            obsIdx := py * 12 + (pm - 1)
            CkReopenCalendar(wrap, rect)
            if (obsIdx != targetIdx)
                CkNavMonths(rect, obsIdx, targetIdx)
        } else {
            ; Empty/garbled — reopen, re-assert target month via a probe, retry.
            CkReopenCalendar(wrap, rect)
            CkNavMonths(rect, 0, targetIdx)
            CkClickProbeCell(rect)
            Sleep(400)
            pv2 := CkReadFieldValue(wrap["elem"])
            oi := 0
            m2:=0,d2:=0,y2:=0
            if CkParseMdy(pv2, &m2, &d2, &y2)
                oi := y2*12 + (m2-1)
            CkReopenCalendar(wrap, rect)
            if (oi != 0 && oi != targetIdx)
                CkNavMonths(rect, oi, targetIdx)
        }
        if (attempt >= 4)
            break
        attempt++
    }
    valFinal := CkReadFieldValue(wrap["elem"])
    LogMessage("    ERROR pos=" . position . " could not set date to " . want . " (last='" . valFinal . "')")
    return false
}

; Navigate month arrows from fromIdx to toIdx (year*12+month-1). If fromIdx=0,
; assumes today's month as the start. Clicks prev/next with generous 800ms
; spacing so DevExpress does not drop clicks on deep navigations. Returns true.
CkNavMonths(rect, fromIdx, toIdx) {
    fx := rect.l, fb := rect.b
    hdrY  := Round(fb + CK_CAL_HDR_DY)
    prevX := Round(fx + CK_CAL_PREV_DX)
    nextX := Round(fx + CK_CAL_NEXT_DX)
    if (fromIdx = 0) {
        ty := Integer(SubStr(A_Now, 1, 4)), tm := Integer(SubStr(A_Now, 5, 2))
        fromIdx := ty * 12 + (tm - 1)
    }
    hops := toIdx - fromIdx
    if (Abs(hops) > 60) {
        LogMessage("    ERROR CkNavMonths hop " . hops . " implausible")
        return false
    }
    LogMessage("    [cal] nav months from " . fromIdx . " to " . toIdx . " (hops=" . hops . ")")
    if (hops > 0) {
        loop hops {
            CkPhysClick(nextX, hdrY)
            Sleep(800)
        }
    } else if (hops < 0) {
        loop (-hops) {
            CkPhysClick(prevX, hdrY)
            Sleep(800)
        }
    }
    Sleep(300)
    return true
}

; Re-open a date field's calendar dropdown (used after a probe click closed it).
CkReopenCalendar(wrap, rect) {
    db := CkFindDropButton(wrap["elem"])
    if db {
        try db.Click("left")
    } else {
        CkPhysClick(rect.r - 12, rect.t + (rect.b - rect.t)//2)
    }
    Sleep(800)
}

; Click a FIXED grid cell (row 2, col 3 = cellIndex 17) which is ALWAYS a
; current-display-month day for any month layout (leading 1..7 => the day there
; is 11..17), never a grey leading/trailing duplicate. Used only to force a
; readable field value so we can learn which month the popup is showing.
CkClickProbeCell(rect) {
    row := 2, col := 3
    cx := Round(rect.l + CK_CAL_COL0_DX + col * CK_CAL_COL_PITCH)
    cy := Round(rect.b + CK_CAL_ROW1_DY + row * CK_CAL_ROW_PITCH)
    LogMessage("    [cal] probe cell r2c3 @ " . cx . "," . cy)
    CkPhysClick(cx, cy)
    Sleep(320)
}

; Read a date field wrapper's displayed Value (mm/dd/yyyy). Tries the inner
; PART_Editor Edit first, then the wrapper.
CkReadFieldValue(wrapElem) {
    val := ""
    try {
        inner := wrapElem.FindElement({Type: "Edit"})
        if inner
            try val := inner.Value
    }
    if (val = "")
        try val := wrapElem.Value
    return val
}

; Parse "M/D/YYYY" (or M/D/YY) into month/day/year by-ref. Returns true on a
; plausible date. Rejects the DevExpress "empty mask" and garbled values.
CkParseMdy(s, &m, &d, &y) {
    if (s = "")
        return false
    ; Accept "M/D/YYYY" optionally followed by a time (e.g. "7/2/2026 12:00:00 AM"),
    ; which is how the DevExpress editor sometimes reports a set value via UIA.
    if RegExMatch(s, "^\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\b", &mm) {
        m := Integer(mm[1]), d := Integer(mm[2]), y := Integer(mm[3])
        if (y < 100)
            y += 2000
        if (m >= 1 && m <= 12 && d >= 1 && d <= 31 && y >= 2000 && y <= 2100)
            return true
    }
    return false
}

; ============================================================================
; Geometric calendar-popup walk (popup is invisible to UIA — drive by pixels)
; ============================================================================
; IMPORTANT (verified 2026-07-03): the DevExpress calendar popup does NOT appear
; in the UIA tree at all — not as a Bravo child, not as a separate top-level
; window, nowhere (confirmed by a full desktop-root uia-discover dump with the
; popup OPEN: no month header, no day cells). So we CANNOT click popup elements
; by UIA. The ONLY viable method is pixel geometry in REAL SCREEN coordinates.
;
; The VM renders at 4096x1998 (high-DPI). All offsets below are in SCREEN px and
; are anchored to the date field's UIA BoundingRectangle (which IS readable):
;   Start field rect example: [1595,865,1879,928] (l,t,r,b) — width 284, h 63.
; Offsets calibrated live 2026-07-03 from the open popup (screenshot landmarks
; back-projected through the field-rect anchor to screen px):
;   * header/nav row  Y = field.bottom + 104
;   * ◄ prev arrow    X = field.left + 35
;   * ► next arrow    X = field.left + 746
;   * first day row   Y = field.bottom + 297
;   * row pitch          = 82 px ; col pitch = 101 px
;   * Su column        X = field.left + 91
; Each day cell is ~100x82 px, so ±15px calibration error is safe. After each
; date pick we VERIFY the field's Value updated (UIA-readable) — the ultimate
; check that the click landed on the intended cell.
; RE-CALIBRATED 2026-07-03 from a precise zoom of the live June-2026 grid
; (previous ROW_PITCH=82 was wrong — real is ~59 — which made row-4 day cells
; like June 30 land ~100px too low and miss the grid entirely).
global CK_CAL_HDR_DY      := 101   ; header/nav row Y = field.bottom + this
global CK_CAL_PREV_DX     := 35    ; ◄ prev arrow X = field.left + this
global CK_CAL_NEXT_DX     := 749   ; ► next arrow X = field.left + this
global CK_CAL_ROW1_DY     := 289   ; first day-grid row Y = field.bottom + this
global CK_CAL_ROW_PITCH   := 59    ; vertical px between day rows
global CK_CAL_COL0_DX     := 85    ; Su column center X = field.left + this
global CK_CAL_COL_PITCH   := 102   ; horizontal px between day columns

; Walk the open popup to (targetYear, targetMonth, targetDay) by pixel geometry.
; `rect` is the field wrapper's BoundingRectangle (l,t,r,b) in SCREEN px.
;
; The popup is UIA-invisible, so we CANNOT read the month header. Instead we
; rely on a KNOWN ANCHOR: on this build, opening a date field's calendar shows
; TODAY'S month by default (verified 2026-07-03 — an empty field opened on the
; current system month regardless of the other field). So the number of month
; hops = targetMonthIndex - todayMonthIndex; positive → click ► that many times,
; negative → click ◄. We then click the target day cell. The CALLER verifies
; via the field's UIA Value; if the month is off, CkSetDateByCalendar re-opens
; and calls us again with the observed month as the new anchor (see `anchorIdx`).
;
; anchorIdx: month index the popup is CURRENTLY showing (year*12 + month-1). If
; 0, we assume today's month.
CkWalkCalendarGeom(rect, targetYear, targetMonth, targetDay, anchorIdx := 0) {
    fx := rect.l
    fb := rect.b
    hdrY  := Round(fb + CK_CAL_HDR_DY)
    prevX := Round(fx + CK_CAL_PREV_DX)
    nextX := Round(fx + CK_CAL_NEXT_DX)
    targetIdx := targetYear * 12 + (targetMonth - 1)

    if (anchorIdx = 0) {
        ty := Integer(SubStr(A_Now, 1, 4))
        tm := Integer(SubStr(A_Now, 5, 2))
        anchorIdx := ty * 12 + (tm - 1)
    }
    hops := targetIdx - anchorIdx
    LogMessage("    [cal] month nav: anchorIdx=" . anchorIdx . " targetIdx=" . targetIdx
             . " hops=" . hops . " (prevX=" . prevX . " nextX=" . nextX . " hdrY=" . hdrY . ")")

    ; Guard against a runaway (Bravo floor is ~2024; anything beyond ±60 months
    ; from anchor is a bug, not a real window).
    if (Abs(hops) > 60) {
        LogMessage("    ERROR month hop count " . hops . " is implausible — aborting")
        return false
    }

    ; Navigate the (possibly large) hop count with a GENEROUS per-click delay so
    ; no clicks are dropped. VERIFIED live 2026-07-03: 24 clicks at ~280-450ms
    ; silently dropped ~4 (calendar can't keep up with its own arrow animation),
    ; landing short of target so the day cell was empty; at ~1000ms spacing all
    ; 24 registered and reached July 2024 exactly. We use 800ms as a safe margin
    ; (24 hops ~= 19s — acceptable; deep windows are rare). July 2024 is fully
    ; reachable (no calendar floor blocks it).
    if (hops > 0) {
        loop hops {
            CkPhysClick(nextX, hdrY)
            Sleep(800)
        }
    } else if (hops < 0) {
        loop (-hops) {
            CkPhysClick(prevX, hdrY)
            Sleep(800)
        }
    }
    Sleep(300)

    ; Click the target day cell (row/col computed from the weekday of the 1st).
    if !CkClickDayCellGeom(rect, targetYear, targetMonth, targetDay) {
        LogMessage("    WARN geometric day-cell click failed")
        return false
    }
    return true
}

; Read the "Month YYYY" header of the currently-open calendar popup via
; desktop-root UIA. The popup is a separate HWND, so we scan the desktop root
; for a Text/Button whose Name matches "<Month> <YYYY>" and whose vertical
; center is near hdrY (the geometrically-expected header row). Returns the
; matched string or "".
CkReadPopupMonthHeader(hdrY) {
    try {
        desktop := UIA.GetRootElement()
    } catch {
        return ""
    }
    if !desktop
        return ""
    best := ""
    bestDist := 99999
    for t in ["Text", "Button", "Header"] {
        elems := 0
        try elems := desktop.FindElements({Type: t})
        if !elems
            continue
        for e in elems {
            nm := ""
            try nm := e.Name
            if !RegExMatch(nm, "i)^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$")
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            cy := r.t + (r.b - r.t)//2
            d := Abs(cy - hdrY)
            if (d < bestDist) {
                bestDist := d
                best := nm
            }
        }
    }
    ; Only trust a header whose row is plausibly the popup header (within 60px).
    if (best != "" && bestDist <= 60)
        return best
    return ""
}

; Click a calendar month-nav arrow ("prev"/"next"). Prefers the real popup
; Button element nearest the expected arrow position (scale-safe); falls back
; to a physical click at the geometric (expX, hdrY). The arrows usually have
; empty Names, so we match by Type=Button and proximity to expX/hdrY.
CkClickCalArrow(dir, expX, hdrY) {
    desktop := 0
    try desktop := UIA.GetRootElement()
    if desktop {
        best := 0, bestDist := 99999
        btns := 0
        try btns := desktop.FindElements({Type: "Button"})
        if btns {
            for b in btns {
                r := 0
                try r := b.BoundingRectangle
                if !r
                    continue
                if (r.r <= r.l || r.b <= r.t)
                    continue
                cx := r.l + (r.r - r.l)//2
                cy := r.t + (r.b - r.t)//2
                ; must be on the header row (near hdrY) and near the arrow X
                if (Abs(cy - hdrY) > 40)
                    continue
                dist := Abs(cx - expX)
                if (dist < bestDist) {
                    bestDist := dist
                    best := b
                }
            }
        }
        if (best && bestDist <= 60) {
            clicked := false
            try {
                best.Click("left")
                clicked := true
            }
            if clicked {
                LogMessage("    [cal] nav " . dir . " via popup Button")
                return
            }
        }
    }
    CkPhysClick(expX, hdrY)
    LogMessage("    [cal] nav " . dir . " via geometry @ " . expX . "," . hdrY)
}

CkMonthHeaderToIdx(hdr) {
    if (hdr = "")
        return 0
    monthNames := Map("January",1,"February",2,"March",3,"April",4,"May",5,"June",6,
                      "July",7,"August",8,"September",9,"October",10,"November",11,"December",12)
    if RegExMatch(hdr, "i)([A-Za-z]+)\s+(\d{4})", &mm) {
        mn := mm[1], y := Integer(mm[2])
        if monthNames.Has(mn)
            return y * 12 + (monthNames[mn] - 1)
    }
    return 0
}

; Defensive fallback when the header can't be read: step from the current
; system month toward the target. Returns true if it clicked (so the loop
; re-checks), false if it can't help.
CkStepTowardByToday(prevX, nextX, hdrY, targetIdx) {
    ; A_Now is yyyyMMddHHmmss
    y := Integer(SubStr(A_Now, 1, 4))
    m := Integer(SubStr(A_Now, 5, 2))
    todayIdx := y * 12 + (m - 1)
    if (todayIdx = targetIdx)
        return false   ; already there in theory but header unread — give up
    if (todayIdx < targetIdx)
        CkPhysClick(nextX, hdrY)
    else
        CkPhysClick(prevX, hdrY)
    Sleep(320)
    return true
}

; Click the day cell for (year, month, day) by PURE PIXEL GEOMETRY (the popup is
; UIA-invisible — verified — so element lookups are pointless here).
; Grid model: Sunday-first, 7 cols, up to 6 rows.
;   * When the 1st is Mon..Sat (firstDOW 1..6): leading days from the prior
;     month fill row 0 before the 1st, so the 1st sits at row 0, col=firstDOW.
;   * When the 1st is SUNDAY (firstDOW 0): DevExpress inserts a FULL leading
;     week from the prior month (verified live 2026-07-03, Feb 2026 grid showed
;     "25 26 27 28 29 30 31" then "1 2 3 4 5 6 7"), so the 1st sits at ROW 1,
;     col 0 — NOT row 0. We model this by treating the leading offset as 7 when
;     firstDOW==0. Bug this fixes: June-2025 windows (June 1 = Sunday) landed a
;     whole row high (6/1 -> prior-month day, 6/30 -> 6/23).
; For a day D of the current month:
;   leading   = (firstDOW == 0) ? 7 : firstDOW
;   cellIndex = leading + (D - 1);  row = cellIndex // 7;  col = cellIndex % 7.
CkClickDayCellGeom(rect, year, month, day) {
    firstDOW := CkDayOfWeek(year, month, 1)   ; 0=Sun .. 6=Sat
    leading := (firstDOW = 0) ? 7 : firstDOW
    cellIndex := leading + (day - 1)
    row := cellIndex // 7
    col := Mod(cellIndex, 7)
    fx := rect.l
    fb := rect.b
    expCx := Round(fx + CK_CAL_COL0_DX + col * CK_CAL_COL_PITCH)
    expCy := Round(fb + CK_CAL_ROW1_DY + row * CK_CAL_ROW_PITCH)
    LogMessage("    [cal] day " . month . "/" . day . "/" . year . " firstDOW=" . firstDOW
             . " leading=" . leading . " -> grid r" . row . "c" . col . " @ " . expCx . "," . expCy)
    CkPhysClick(expCx, expCy)
    Sleep(320)
    return true
}

; Find the popup day-cell element whose Name/printed number == day and whose
; center is closest to (expCx,expCy). Searches the DESKTOP ROOT because the
; calendar popup is a separate top-level HWND. Rejects cells whose center is
; far (> ~60px) from the expected position, which filters out the duplicate
; grey day from an adjacent month. Returns the element or 0.
CkFindDayCellElem(day, expCx, expCy) {
    target := "" . day
    desktop := 0
    try desktop := UIA.GetRootElement()
    if !desktop
        return 0
    best := 0
    bestDist := 99999
    for t in ["ListItem", "Button", "DataItem", "Text"] {
        elems := 0
        try elems := desktop.FindElements({Type: t})
        if !elems
            continue
        for e in elems {
            nm := ""
            try nm := e.Name
            if (nm != target)
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            ; Ignore zero/degenerate or clearly off-popup rects.
            if (r.r <= r.l || r.b <= r.t)
                continue
            cx := r.l + (r.r - r.l)//2
            cy := r.t + (r.b - r.t)//2
            dist := Abs(cx - expCx) + Abs(cy - expCy)
            if (dist < bestDist) {
                bestDist := dist
                best := e
            }
        }
    }
    ; Accept only if reasonably near the expected cell (guards against the
    ; wrong-month duplicate and stray "day" texts elsewhere on screen).
    if (best && bestDist <= 80)
        return best
    if (best)
        LogMessage("    [cal] nearest day '" . target . "' elem is " . bestDist . "px from expected — rejecting, will use geometry")
    return 0
}

; Zeller-free day-of-week: returns 0=Sunday .. 6=Saturday for a given date.
CkDayOfWeek(y, m, d) {
    ; Build a yyyyMMdd and use AHK's FormatTime weekday (1=Sunday..7=Saturday).
    ymd := Format("{:04}{:02}{:02}000000", y, m, d)
    wd := FormatTime(ymd, "WDay")   ; 1=Sunday .. 7=Saturday
    return Integer(wd) - 1
}

; Find the dropdown/calendar toggle button that is a child of the date wrapper.
; VERIFIED LIVE (2026-07-03, Select Date Range dialog, uia-tree-2026-07-03-calopen):
; the BravoDateEdit wrapper's calendar toggle is a Button with
;   AutomationId = "PART_Item"
;   Name        = "DevExpress.Xpf.Editors.DateEditButtonInfo"
; (it has a child [image] AutoId='image'). There is NO "PART_DropDownButton"
; in this build. Try the verified AutoId+Name first, then any Button child.
CkFindDropButton(wrapElem) {
    try {
        b := wrapElem.FindElement({AutomationId: "PART_Item", Type: "Button"})
        if b
            return b
    }
    try {
        b := wrapElem.FindElement({Name: "DevExpress.Xpf.Editors.DateEditButtonInfo"})
        if b
            return b
    }
    try {
        for b in wrapElem.FindElements({Type: "Button"}) {
            return b   ; first button child = the glyph toggle
        }
    }
    return 0
}

; Read the calendar popup's month header and click prev/next until it shows the
; target year+month. Header text like "June 2026". Guards against runaway.
CkNavigateCalendarToMonth(targetYear, targetMonth) {
    monthNames := Map("January",1,"February",2,"March",3,"April",4,"May",5,"June",6,
                      "July",7,"August",8,"September",9,"October",10,"November",11,"December",12)
    targetIdx := targetYear * 12 + (targetMonth - 1)
    loop 60 {
        hdr := CkReadCalendarHeader()
        if (hdr = "") {
            LogMessage("    WARN calendar header unreadable")
            return false
        }
        ; parse "Month YYYY"
        m := 0, y := 0
        if RegExMatch(hdr, "i)([A-Za-z]+)\s+(\d{4})", &mm) {
            mn := mm[1]
            if monthNames.Has(mn)
                m := monthNames[mn]
            y := Integer(mm[2])
        }
        if (m = 0 || y = 0) {
            LogMessage("    WARN could not parse calendar header '" . hdr . "'")
            return false
        }
        curIdx := y * 12 + (m - 1)
        if (curIdx = targetIdx) {
            LogMessage("    [cal] on target month: " . hdr)
            return true
        }
        if (curIdx < targetIdx) {
            if !CkClickCalNav("next") {
                LogMessage("    WARN next-month nav failed at " . hdr)
                return false
            }
        } else {
            if !CkClickCalNav("prev") {
                LogMessage("    WARN prev-month nav failed at " . hdr)
                return false
            }
        }
        Sleep(300)
    }
    LogMessage("    WARN calendar month navigation exhausted 60 hops")
    return false
}

; Read the month/year header of the open calendar popup. It is typically a
; Button/Text element whose Name is "Month YYYY".
CkReadCalendarHeader() {
    try {
        root := GetBravoRoot()
        ; Look for a Button or Text whose name matches "<Month> <YYYY>"
        for t in ["Button", "Text", "Header"] {
            for e in root.FindElements({Type: t}) {
                nm := ""
                try nm := e.Name
                if RegExMatch(nm, "i)^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$")
                    return nm
            }
        }
    }
    return ""
}

; Click the calendar prev/next navigation button. Bravo exposes these as
; Buttons; names vary ("Previous"/"Next", or DevExpress AutoIds). Try several.
CkClickCalNav(dir) {
    root := 0
    try root := GetBravoRoot()
    if !root
        return false
    candNames := (dir = "next")
        ? ["Next", "Next Month", "PART_NextButton"]
        : ["Previous", "Prev", "Previous Month", "PART_PrevButton"]
    for nm in candNames {
        e := 0
        try e := root.FindElement({Name: nm})
        if e {
            try {
                e.Click("left")
                return true
            }
        }
    }
    ; AutomationId fallbacks
    aids := (dir = "next") ? ["PART_NextButton","NextButton","btnNext"] : ["PART_PrevButton","PrevButton","btnPrev"]
    for aid in aids {
        e := 0
        try e := root.FindElement({AutomationId: aid})
        if e {
            try {
                e.Click("left")
                return true
            }
        }
    }
    ; Last resort: physical click on the header arrows by geometry. The header
    ; row's leftmost ~24px is prev, rightmost ~24px is next.
    hdrRect := CkCalendarHeaderRect()
    if hdrRect {
        y := hdrRect.t + (hdrRect.b - hdrRect.t)//2
        x := (dir = "next") ? (hdrRect.r - 12) : (hdrRect.l + 12)
        CkPhysClick(x, y)
        return true
    }
    return false
}

CkCalendarHeaderRect() {
    try {
        root := GetBravoRoot()
        for t in ["Button", "Text", "Header"] {
            for e in root.FindElements({Type: t}) {
                nm := ""
                try nm := e.Name
                if RegExMatch(nm, "i)^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$") {
                    r := 0
                    try r := e.BoundingRectangle
                    if r
                        return r
                }
            }
        }
    }
    return 0
}

; Click the day cell for `day` in the currently-shown month. Day cells are
; Buttons/ListItems named by the day number. Adjacent-month days share names,
; so we choose the ENABLED, on-screen cell; if multiple, the one nearest the
; center of the grid (current month) wins over leading/trailing greys.
CkClickDayCell(day) {
    target := "" . day
    cands := []
    try {
        root := GetBravoRoot()
        for t in ["Button", "ListItem", "DataItem"] {
            for e in root.FindElements({Type: t}) {
                nm := ""
                try nm := e.Name
                if (nm != target)
                    continue
                r := 0
                try r := e.BoundingRectangle
                if !r
                    continue
                en := true
                try en := e.IsEnabled
                off := false
                try off := e.IsOffscreen
                if (off)
                    continue
                cands.Push(Map("elem", e, "rect", r, "enabled", en))
            }
        }
    }
    if (cands.Length = 0) {
        LogMessage("    WARN no day cell named '" . target . "' found")
        return false
    }
    ; Prefer enabled cells; among those, the first in reading order.
    pick := 0
    for c in cands {
        if c["enabled"] {
            pick := c
            break
        }
    }
    if !pick
        pick := cands[1]
    try {
        pick["elem"].Click("left")
        LogMessage("    [cal] clicked day cell '" . target . "'")
        return true
    } catch as e {
        r := pick["rect"]
        CkPhysClick(r.l + (r.r-r.l)//2, r.t + (r.b-r.t)//2)
        LogMessage("    [cal] phys-clicked day cell '" . target . "'")
        return true
    }
}

; Click Ok only if it exists and is ENABLED. Returns true if clicked.
; VERIFIED LIVE (2026-07-03): the Ok control is a [button] with an EMPTY Name
; whose child is a [text] Name='Ok'. A Name:"Ok" search therefore returns the
; TEXT node, and IsEnabled on the text node does NOT reflect the button's
; disabled state (it reads true even when Ok is greyed out because both dates
; aren't valid). So we resolve the actual Button (parent of the "Ok" text, or a
; Button whose descendant text is "Ok") and check ITS IsEnabled before clicking.
CkClickOk(timeoutMs) {
    deadline := A_TickCount + timeoutMs
    loop {
        btn := CkResolveOkButton()
        if btn {
            en := true
            try en := btn.IsEnabled
            if en {
                try {
                    btn.Click("left")
                    LogMessage("    [dialog] clicked Ok (enabled button)")
                    return true
                } catch {
                    ; physical click at button center as a fallback
                    r := 0
                    try r := btn.BoundingRectangle
                    if r {
                        CkPhysClick(r.l + (r.r - r.l)//2, r.t + (r.b - r.t)//2)
                        LogMessage("    [dialog] phys-clicked Ok button center")
                        return true
                    }
                }
            } else {
                LogMessage("    [dialog] Ok present but DISABLED — dates not both valid yet")
            }
        }
        if (A_TickCount > deadline)
            return false
        Sleep(300)
    }
}

; Resolve the actual Ok *button* element (not the child text). Strategy:
;   1. Find the "Ok"/"OK" text node; return its nearest Button ancestor.
;   2. Otherwise, scan Buttons for one whose subtree contains an "Ok" text.
; Returns the Button element or 0.
CkResolveOkButton() {
    root := 0
    try root := GetBravoRoot()
    if !root
        return 0
    ; Try: any Button whose own Name is Ok/OK (some builds label the button).
    for nm in ["Ok", "OK"] {
        b := 0
        try b := root.FindElement({Name: nm, Type: "Button"})
        if b
            return b
    }
    ; Find the "Ok" text node, then walk up to a Button ancestor.
    txt := 0
    for nm in ["Ok", "OK"] {
        try txt := root.FindElement({Name: nm, Type: "Text"})
        if txt
            break
    }
    if txt {
        p := txt
        loop 5 {
            try p := p.Parent
            if !p
                break
            ct := ""
            try ct := p.Type            ; numeric control type id
            lt := ""
            try lt := p.LocalizedType   ; "button", etc.
            if (lt = "button")
                return p
        }
    }
    ; Last resort: scan all buttons for one whose descendant text is Ok.
    btns := 0
    try btns := root.FindElements({Type: "Button"})
    if btns {
        for b in btns {
            t2 := 0
            try t2 := b.FindElement({Name: "Ok", Type: "Text"})
            if !t2
                try t2 := b.FindElement({Name: "OK", Type: "Text"})
            if t2
                return b
        }
    }
    return 0
}

; ============================================================================
; Browser handoff: read rendered URL, build export URL, navigate
; ============================================================================

; Poll the browser for a tab whose address bar shows the Company Performance
; report URL FOR OUR EXACT WINDOW. Returns the URL or "".
;
; CRITICAL (fixed 2026-07-03): stale "BRAVO Company Performance" tabs from prior
; renders linger in Chrome (different EndDate + old r= GUID). Accepting "any"
; Company Performance URL grabbed a STALE tab (e.g. EndDate=7/2 with a dead
; GUID) and the export then timed out. We now REQUIRE the URL to carry BOTH our
; StartDate=<startSsrs> AND EndDate=<endSsrs> so we only ever act on THIS run's
; fresh render. (We also proactively close stale report windows before Ok — see
; CkCloseStaleReportWindows — so the fresh tab is the only match.)
CkWaitForRenderedUrl(startSsrs, endSsrs, timeoutMs) {
    deadline := A_TickCount + timeoutMs
    loop {
        u := CkReadBrowserUrl(startSsrs, endSsrs)
        if (u != "")
            return u
        if (A_TickCount > deadline)
            return ""
        Sleep(700)
    }
}

; Scan ALL Chrome/Edge windows' omniboxes and return the first URL that is a
; Company Performance report AND matches our StartDate/EndDate AND has an r=
; GUID. If startSsrs/endSsrs are "", falls back to any Company Performance URL
; with r= (legacy behavior). Returns "" if none match.
CkReadBrowserUrl(startSsrs := "", endSsrs := "") {
    wantStart := (startSsrs != "") ? ("StartDate=" . startSsrs) : ""
    wantEnd   := (endSsrs   != "") ? ("EndDate="   . endSsrs)   : ""
    fallback := ""
    for exe in ["chrome.exe", "msedge.exe"] {
        for hwnd in WinGetList("ahk_exe " . exe) {
            try {
                t := WinGetTitle("ahk_id " . hwnd)
                if (t = "")
                    continue
                el := UIA.ElementFromHandle(hwnd)
                bar := 0
                for nm in ["Address and search bar", "Address bar", "Search or enter web address"] {
                    try bar := el.FindElement({Type: "Edit", Name: nm})
                    if bar
                        break
                }
                if !bar {
                    try {
                        for e in el.FindElements({Type: "Edit"}) {
                            v := ""
                            try v := e.Value
                            if InStr(v, "bravoapplication.com") {
                                bar := e
                                break
                            }
                        }
                    }
                }
                if !bar
                    continue
                v := ""
                try v := bar.Value
                if (v = "")
                    continue
                if !(InStr(v, "Company") && InStr(v, "Performance") && InStr(v, "r="))
                    continue
                ; Exact-window match required when dates are provided.
                if (wantStart != "" && wantEnd != "") {
                    if (InStr(v, wantStart) && InStr(v, wantEnd))
                        return v
                    ; remember as a last-resort fallback only if no exact match
                    ; is found anywhere (should not happen after stale cleanup)
                    if (fallback = "")
                        fallback := ""   ; do NOT fall back to a wrong-date URL
                    continue
                }
                return v
            }
        }
    }
    return fallback
}

; Close stale "BRAVO Company Performance" browser windows so that after Ok the
; freshly-rendered tab is the ONLY Company Performance tab. We only close report
; windows (title contains "Company Performance"), never other browsing windows.
CkCloseStaleReportWindows() {
    closed := 0
    for exe in ["chrome.exe", "msedge.exe"] {
        for hwnd in WinGetList("ahk_exe " . exe) {
            t := ""
            try t := WinGetTitle("ahk_id " . hwnd)
            if (t = "")
                continue
            if InStr(t, "Company Performance") {
                try {
                    WinClose("ahk_id " . hwnd)
                    closed++
                    Sleep(200)
                }
            }
        }
    }
    if (closed)
        LogMessage("    [browser] closed " . closed . " stale Company Performance window(s)")
    return closed
}

; Turn a rendered report URL into its EXCELOPENXML export equivalent, keeping
; the fresh r= GUID + params. Handles the "Render?XXX" literal Bravo injects.
CkBuildExportUrl(renderedUrl, startSsrs, endSsrs) {
    u := renderedUrl
    ; Ensure scheme
    if !InStr(u, "http")
        u := "https://" . u
    ; Replace the command segment with Render + EXCELOPENXML format.
    ; Bravo's dashboard produces "...&rs:Command=Render?XXX&rc:parameters=...".
    if InStr(u, "rs:Command=Render?XXX")
        u := StrReplace(u, "rs:Command=Render?XXX", "rs:Command=Render&rs:Format=EXCELOPENXML")
    else if InStr(u, "rs:Command=Render&rs:Format=")
        u := RegExReplace(u, "rs:Format=[A-Za-z]+", "rs:Format=EXCELOPENXML")
    else if InStr(u, "rs:Command=Render")
        u := StrReplace(u, "rs:Command=Render", "rs:Command=Render&rs:Format=EXCELOPENXML")
    else
        u := u . "&rs:Command=Render&rs:Format=EXCELOPENXML"
    return u
}

; Navigate the browser to the EXCELOPENXML export `url` so it downloads the
; xlsx using the already-established auth cookies.
;
; PRIMARY method (2026-07-03): Run(url) via the DEFAULT browser. The report was
; just rendered by the SAME default browser (Chrome) that Bravo handed off to,
; so its profile already holds the .ASPXAUTH cookie. Run(url) opens the export
; URL in that existing Chrome instance (reusing cookies); SSRS returns the file
; as an attachment and Chrome downloads it to C:\Users\joshuadavis\Downloads.
; This is far more reliable than driving the omnibox with keystrokes (which
; failed because the SSRS report body steals focus so Ctrl+L never reached the
; address bar — the tab stayed on the render URL and nothing downloaded).
;
; FALLBACK: the previous omnibox Ctrl+L + clipboard-paste + Enter approach, with
; a firmer activate, in case Run() is blocked.
CkNavigateBrowser(url) {
    ; --- PRIMARY: open export URL in the default browser (reuses cookies) ---
    launched := false
    try {
        Run(url)
        launched := true
        LogMessage("    [browser] Run(exportUrl) via default browser")
    } catch as e {
        LogMessage("    WARN Run(url) failed: " . e.Message . " — trying omnibox paste")
    }
    if launched {
        Sleep(1500)
        return true
    }

    ; --- FALLBACK: omnibox keystroke paste on the report window ------------
    hwnd := 0
    for exe in ["chrome.exe", "msedge.exe"] {
        for h in WinGetList("ahk_exe " . exe) {
            t := ""
            try t := WinGetTitle("ahk_id " . h)
            if InStr(t, "Company Performance") {
                hwnd := h
                break
            }
        }
        if hwnd
            break
    }
    if !hwnd {
        for exe in ["chrome.exe", "msedge.exe"] {
            list := WinGetList("ahk_exe " . exe)
            if (list.Length) {
                hwnd := list[1]
                break
            }
        }
    }
    if !hwnd {
        LogMessage("    ERROR no browser window to navigate")
        return false
    }
    try {
        WinActivate("ahk_id " . hwnd)
        WinWaitActive("ahk_id " . hwnd, , 5)
    }
    Sleep(600)
    Send("^l")
    Sleep(500)
    Send("^l")            ; twice — the first can be swallowed by the report body
    Sleep(400)
    prev := ""
    try prev := A_Clipboard
    A_Clipboard := url
    if !ClipWait(2) {
        LogMessage("    ERROR clipboard did not accept export URL")
        return false
    }
    Send("^a")
    Sleep(120)
    Send("^v")
    Sleep(400)
    Send("{Enter}")
    Sleep(400)
    try A_Clipboard := prev
    LogMessage("    [browser] navigated omnibox to export URL (fallback)")
    return true
}

; ============================================================================
; Downloads helpers
; ============================================================================

CkSnapshotReportFiles(dir) {
    m := Map()
    if !DirExist(dir)
        return m
    for pattern in ["*.xlsx", "*.xls", "*.csv"] {
        loop files, dir . "\" . pattern
            m[StrLower(A_LoopFileName)] := true
    }
    return m
}

CkWaitForNewFile(dir, priorSnapshot, timeoutMs) {
    deadline := A_TickCount + timeoutMs
    loop {
        for pattern in ["*.xlsx", "*.xls", "*.csv"] {
            loop files, dir . "\" . pattern {
                key := StrLower(A_LoopFileName)
                if !priorSnapshot.Has(key) {
                    ; skip Chrome's in-progress .crdownload sibling
                    if FileExist(A_LoopFileFullPath . ".crdownload")
                        continue
                    p := A_LoopFileFullPath
                    if WaitForFileSizeStable(p, 3)
                        return p
                }
            }
        }
        if (A_TickCount > deadline)
            return ""
        Sleep(500)
    }
}

; Snapshot report files across MULTIPLE directories. Keys are full lowercased
; paths so files with the same name in different dirs don't collide.
CkSnapshotReportFilesMulti(dirs) {
    m := Map()
    for dir in dirs {
        if !DirExist(dir)
            continue
        for pattern in ["*.xlsx", "*.xls", "*.csv"] {
            loop files, dir . "\" . pattern
                m[StrLower(A_LoopFileFullPath)] := true
        }
    }
    return m
}

; Poll MULTIPLE directories for a new report file not in priorSnapshot.
CkWaitForNewFileMulti(dirs, priorSnapshot, timeoutMs) {
    deadline := A_TickCount + timeoutMs
    loop {
        for dir in dirs {
            if !DirExist(dir)
                continue
            for pattern in ["*.xlsx", "*.xls", "*.csv"] {
                loop files, dir . "\" . pattern {
                    key := StrLower(A_LoopFileFullPath)
                    if !priorSnapshot.Has(key) {
                        if FileExist(A_LoopFileFullPath . ".crdownload")
                            continue
                        p := A_LoopFileFullPath
                        if WaitForFileSizeStable(p, 3)
                            return p
                    }
                }
            }
        }
        if (A_TickCount > deadline)
            return ""
        Sleep(500)
    }
}

; Join an array of strings with a separator.
CkJoin(arr, sep) {
    s := ""
    for i, v in arr
        s .= (i > 1 ? sep : "") . v
    return s
}

; ============================================================================
; Small utilities
; ============================================================================

; Convert "2026-06-01" -> "2026/6/1" (no zero padding) for SSRS.
CkIsoToSsrs(iso) {
    parts := StrSplit(iso, "-")
    if (parts.Length != 3)
        return iso
    return parts[1] . "/" . Integer(parts[2]) . "/" . Integer(parts[3])
}

; Physical screen click helper (CoordMode Screen is set in lib\Bravo.ahk).
CkPhysClick(x, y) {
    MouseMove(x, y, 2)
    Sleep(80)
    Click(x, y)
}

; Best-effort return to Dashboard so a failure never strands Bravo on a modal.
CkRecoverToDashboard() {
    try {
        ActivateBravo()
        Sleep(300)
        ; If the date dialog is still up with an invalid value it blocks Cancel;
        ; clearing the focused field first (Ctrl+A, Delete) unblocks it. This is
        ; NOT typing a value — it only clears.
        loop 2 {
            if ExistsByName("Cancel") {
                try {
                    Send("^a")
                    Sleep(80)
                    Send("{Delete}")
                    Sleep(150)
                    ClickByName("Cancel", 1500)
                    Sleep(600)
                }
            }
        }
        if !ExistsByName("Reports")
            BackToDashboard(6)
        DismissPopups()
    }
}

; Local Fail wrapper (mirrors the shared Fail contract).
CkFail(result, started, msg) {
    result["status"]      := "error"
    result["error"]       := msg
    result["duration_ms"] := A_TickCount - started
    LogMessage("  ERROR: " . msg)
    try CkRecoverToDashboard()
    return result
}

; --- Retained from prior stub (used by CkWaitForNewFile) --------------------
WaitForFileSizeStable(path, stableSec) {
    lastSize := -1
    stableSince := 0
    overallStart := A_TickCount
    loop {
        try {
            sz := FileGetSize(path)
        } catch {
            return false
        }
        if (sz = lastSize) {
            if (stableSince = 0)
                stableSince := A_TickCount
            if (A_TickCount - stableSince >= stableSec * 1000)
                return true
        } else {
            lastSize := sz
            stableSince := 0
        }
        Sleep(400)
        if (A_TickCount - overallStart > stableSec * 1000 * 10)
            return false
    }
}

PeekFirstByte(path) {
    try {
        f := FileOpen(path, "r")
        if !f
            return ""
        ch := f.Read(1)
        f.Close()
        return ch
    }
    return ""
}
