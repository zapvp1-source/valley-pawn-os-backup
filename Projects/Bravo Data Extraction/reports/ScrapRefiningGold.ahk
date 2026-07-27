; ============================================================================
; reports/ScrapRefiningGold.ahk
;
; Pulls monthly Gold dwt (Combined Metal Weight) from Bravo's Scrap Refining
; Process screen for a single store across a target calendar year. Replaces
; the manual computer-use navigation used to pull Waynesboro's 2025 data
; for the Gold Weight YOY report (2025 vs 2026).
;
; SKILL it powers: Gold Weight YOY 2025 vs 2026 report (one-off project,
; see /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/ output
; workbook Gold_Weight_YOY_2025_vs_2026.xlsx).
;
; UI path:
;   Dashboard -> Inventory (sidebar)
;   -> "Scrap Refining Process"  (dialog opens, default view = Status:OPEN only)
;   -> click the funnel filter icon in the "Status" column header, check the
;      "CLOSED" checkbox (grid updates live) -> now shows OPEN+CLOSED buckets
;   -> a list/grid of scrap buckets (Created On, Name, Status, Status Date)
;   -> double-click a bucket row -> Ok -> Scrap Bucket Detail screen
;      -> "Combined Metal Weight" field holds the dwt value
;   -> Done -> back to Inventory (NOT back to the bucket list - the dialog
;      must be fully reopened, and the CLOSED filter reapplied, for every
;      single bucket read)
;
; CONFIRMED LIVE 2026-07-18 (WAY store) via direct computer-use inspection:
;   - The Status column header has a small funnel icon immediately to the
;     right of the "Status" text. Clicking it opens a checkbox popup with
;     three items: "(Select All)", "CLOSED", "OPEN" (OPEN checked by
;     default, CLOSED unchecked). Checking "CLOSED" updates the grid RIGHT
;     AWAY, while the popup is still open - no separate Apply/OK button.
;   - The popup can be dismissed safely by clicking on the dialog's own
;     maroon title bar (non-interactive chrome) - this preserves the
;     filter selection. Escape did NOT close the popup in live testing.
;   - Clicking the "Status" TEXT itself (rather than the funnel icon)
;     triggers a column sort instead of opening the filter - so the
;     funnel must be targeted precisely (computed from the "Status"
;     header element's own GetPos(), not eyeballed/hardcoded screen
;     pixels, since AHK runs inside the VM's own coordinate space).
;   - Buckets are named inconsistently across months but Created On is
;     reliable: a bucket for month M is created near the end of month M
;     (sometimes numbered a few days into M+1) and Status Date (closed
;     date) lands a few days later, often into M+1.
;
; WARNING - OTHER KNOWN UI QUIRKS (discovered manually 2026-07-18):
;   1. "Queued navigation" bug: double-click + Ok on a bucket row does not
;      always open the detail screen immediately. Sometimes it silently
;      queues the navigation, which then fires the NEXT time
;      "Scrap Refining Process" is clicked. This handler defends against
;      it by re-clicking "Scrap Refining Process" (fires the queued nav)
;      and retrying the Combined Metal Weight read up to 3x before giving
;      up on that bucket.
;   2. The grid is virtualized (rows only exist in the UIA tree once
;      scrolled into view) and re-filters to the OPEN-only default EVERY
;      time the dialog is reopened. Since "Done" always returns to
;      Inventory (never back to the bucket list), every single bucket
;      read requires: reopen dialog -> reapply CLOSED filter -> scroll
;      via PageDown until the target bucket name is found -> open it.
;   3. The grid's exact column AutomationIds were confirmed via a live
;      diagnostic dump on 2026-07-18: DateCreated, Name, StatusCodeText,
;      StatusDate. This handler still defensively logs the first captured
;      row's raw child AutomationId/Name pairs to a diagnostic CSV.
;   4. Bucket naming is highly inconsistent across stores/months, e.g.
;      "GOLD 1/25", "STONE-GOLD 1/25", "8/25 GOLD", "STONE/GOLD 10/25",
;
; KNOWN LIMITATION (confirmed via extensive live testing 2026-07-18): the
; Scrap Refining Process bucket-list grid appears to cap AutomationElement
; enumeration at ~50-52 realized DataItem rows per dialog-open, REGARDLESS
; of scroll mechanism (PgDn key, small WheelDown bursts, large WheelDown
; bursts) or pacing (300ms-1500ms between scrolls) - this was reproduced
; identically 5+ times. This is most likely a WPF virtualizing-panel
; container-recycling ceiling in the underlying DevExpress-style grid, not
; an AHK timing issue. Practical effect: PullScrapRefiningGold reliably
; captures the newest ~4-5 months of CLOSED+OPEN buckets per store per run.
; For a bucket further back than that (e.g. pulling a full prior calendar
; year on a store with heavy scrap volume), Step 4's per-bucket re-search
; (scroll-to-top then scroll-down-to-find) was ALSO unable to relocate a
; row already confirmed to exist (matched fine during the Step 2 walk) even
; after 150 large scroll bursts - so the same ~50-row ceiling applies to
; the search loop, not just the initial walk. Manual computer-use
; navigation (real mouse scroll wheel, not AHK-simulated) WAS able to
; reach arbitrarily old rows in live testing the same day, so this is
; specific to how AHK's simulated wheel/key events interact with this
; control, not a true data-access limit. Until this is solved (candidate
; next steps: try UIA ScrollItemPattern.ScrollIntoView on a found-but-
; unopened element instead of simulated wheel/key scrolling; try
; IUIAutomationScrollPattern on the grid container directly; or drive the
; scrollbar thumb via SetValue), this handler is reliable for RECENT data
; (last ~4-5 months) but not for deep historical pulls in one run.
;
;      "SILVER 12/25" (no "12/25" year token ambiguity vs "1/25" month -
;      always 2-digit year). Matching logic: name contains "GOLD"
;      (case-insensitive) AND does NOT contain "SILVER", AND the row's
;      Created On date falls inside [1st of target month, 10th of
;      month+1] (buckets are typically created during or shortly after
;      the month they cover). If Created On can't be parsed, fall back to
;      a month/year token match against the name (e.g. "1/25", "01/25").
;
; Trigger schema: dateOrRange is a 4-digit YEAR ("2025") meaning pull all
; 12 months of that year, OR an explicit month range
; "YYYY-MM..YYYY-MM" (e.g. "2025-01..2025-06").
;
; Output: ONE ROW PER MATCHED BUCKET (not pre-aggregated), so the result is
; fully auditable. Columns: Store, Month, BucketName, CreatedOn, Status,
; StatusDate, CombinedMetalWeightDwt. Emits a "NO BUCKET FOUND" row for any
; month with zero matches so gaps are explicit, not silently omitted.
; A companion "<...>_diagnostic.csv" captures the raw first-row element
; dump for troubleshooting if the grid shape doesn't match expectations.
; ============================================================================

#Requires AutoHotkey v2.0

global SCRAP_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "scrap_refining",       "Scrap Refining Process",
    "status_header",        "Status",
    "filter_closed",        "CLOSED",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "panel_done",           "Done",
    "combined_metal_weight","Combined Metal Weight"
)

PullScrapRefiningGold(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "scrap-refining-gold",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse target months -------------------------------------------
    months := []   ; array of {year, month, label}
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed range: " . dateOrRange . " (expected YYYY-MM..YYYY-MM)")
        startParts := StrSplit(Trim(parts[1]), "-")
        endParts   := StrSplit(Trim(parts[2]), "-")
        if (startParts.Length < 2 || endParts.Length < 2)
            return Fail(result, started, "Malformed range endpoints: " . dateOrRange)
        sy := Integer(startParts[1]), sm := Integer(startParts[2])
        ey := Integer(endParts[1]),   em := Integer(endParts[2])
        y := sy, m := sm
        Loop 240 {
            months.Push({year: y, month: m, label: Format("{:04}-{:02}", y, m)})
            if (y = ey && m = em)
                break
            m++
            if (m > 12) {
                m := 1
                y++
            }
        }
    } else if RegExMatch(Trim(dateOrRange), "^\d{4}$") {
        y := Integer(Trim(dateOrRange))
        Loop 12
            months.Push({year: y, month: A_Index, label: Format("{:04}-{:02}", y, A_Index)})
    } else {
        return Fail(result, started, "Unrecognized dateOrRange: " . dateOrRange . " (expected YYYY or YYYY-MM..YYYY-MM)")
    }

    LogMessage("[" . store . "] ScrapRefiningGold target months: " . months.Length)

    yearTag := months.Length ? months[1].year : "unknown"
    outputFileName := yearTag . "_" . store . "_scrap-refining-gold.csv"
    outputPath := outputDir . "\" . outputFileName
    diagPath := outputDir . "\" . yearTag . "_" . store . "_scrap-refining-gold_diagnostic.csv"
    LogMessage("  output -> " . outputPath)

    if !WinExist(BRAVO_WIN_TITLE) {
        deadline := A_TickCount + 30000
        while (!WinExist(BRAVO_WIN_TITLE) && A_TickCount < deadline)
            Sleep(500)
        if !WinExist(BRAVO_WIN_TITLE)
            return Fail(result, started, "Bravo window not found within 30s")
    }
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)
    ResetOutputFile(diagPath)
    WriteCsvRow(outputPath, "Store", "Month", "BucketName", "CreatedOn", "Status", "StatusDate", "CombinedMetalWeightDwt")

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        ; --- Step 1: open Inventory -> Scrap Refining Process, apply filter
        if !ScrapOpenFilteredBucketList()
            throw Error("Could not open Scrap Refining Process with CLOSED+OPEN filter applied")

        ; --- Step 2: walk the full (virtualized, now-unfiltered-by-status) list
        buckets := ScrapWalkBucketGrid(diagPath)

        ; Close the Scrap Refining Process dialog now that the full grid has
        ; been captured - Step 4 needs a clean Inventory sidebar to reopen it
        ; fresh for each bucket read (Cancel, not Done, to avoid side effects).
        try {
            if FindByName(SCRAP_ELEMENTS["panel_cancel"], 2000)
                ClickByName(SCRAP_ELEMENTS["panel_cancel"], 2000)
            Sleep(2000)
            DismissPopups()
            Sleep(500)
        }
        LogMessage("  [grid] captured " . buckets.Length . " total bucket rows")

        if (buckets.Length = 0) {
            LogMessage("    [diag-label] scrap-grid-empty")
            LogVisibleNames(80)
            throw Error("No bucket rows captured - see LogVisibleNames dump for actual element shape")
        }

        ; --- Step 3: match candidates per target month --------------------
        monthCandidates := Map()   ; label -> array of bucket row objects
        for mo in months
            monthCandidates[mo.label] := []

        for b in buckets {
            nameUpper := StrUpper(b.name)
            if !InStr(nameUpper, "GOLD")
                continue
            if InStr(nameUpper, "SILVER")
                continue
            for mo in months {
                if ScrapNameOrDateMatchesMonth(b, mo.year, mo.month) {
                    monthCandidates[mo.label].Push(b)
                }
            }
        }

        ; --- Step 4: for each month, open each candidate bucket and read --
        ; Every read requires a full dialog reopen (Done always exits to
        ; Inventory, never back to the bucket list) plus a fresh filter
        ; application and a fresh scroll-search for that bucket's name.
        rowCount := 0
        for mo in months {
            cands := monthCandidates[mo.label]
            if (cands.Length = 0) {
                LogMessage("    [" . mo.label . "] NO BUCKET FOUND")
                WriteCsvRow(outputPath, store, mo.label, "NO BUCKET FOUND", "", "", "", "")
                rowCount++
                continue
            }
            for b in cands {
                weight := ScrapOpenBucketAndReadWeight(b.name)
                LogMessage("    [" . mo.label . "] bucket='" . b.name . "' weight=" . weight)
                WriteCsvRow(outputPath, store, mo.label, b.name, b.createdOn, b.status, b.statusDate, weight)
                rowCount++
            }
        }

        result["row_count"] := rowCount
    } catch as e {
        return Fail(result, started, "UIA sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; Open Inventory -> Scrap Refining Process and apply the CLOSED status
; filter (grid defaults to OPEN-only). Handles the "queued navigation" bug
; on the initial click. Returns true on success (dialog open, filter
; applied or at least attempted), false if the dialog never opened.
; ----------------------------------------------------------------------------
ScrapOpenFilteredBucketList() {
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
        throw Error("'Scrap Refining Process' not found on Inventory panel - see log for LogVisibleNames dump")
    }
    ClickByName(SCRAP_ELEMENTS["scrap_refining"], 5000)
    Sleep(2000)

    ; Defend against the "queued navigation" bug: if we're still showing the
    ; Inventory panel (button still findable) after clicking, click again.
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
    ScrapApplyClosedFilter()
    return true
}

; ----------------------------------------------------------------------------
; Click the "Created On" column header twice so the grid sorts descending
; (newest first). Confirmed live: a fresh dialog open defaults to a Status-
; based sort; one click on "Created On" gives ascending, a second click
; gives descending. With descending sort applied BEFORE the CLOSED filter,
; the grid lands already showing the newest rows at the top after filtering
; - so a WheelDown-only walk (the one scroll direction AHK's Send reliably
; drives) moves chronologically backward through history in a deterministic
; order, instead of the arbitrary alphabetical-by-name order the unsorted
; grid uses. Best-effort: logs and continues on failure rather than
; aborting, since an unsorted walk still finds SOME buckets.
; ----------------------------------------------------------------------------
ScrapSortByCreatedOnDescending() {
    try {
        hdr := FindByName("Created On", 3000)
        if !hdr {
            LogMessage("    [sort] 'Created On' header not found - continuing unsorted")
            return false
        }
        hdr.Click("left")
        Sleep(400)
        hdr2 := FindByName("Created On", 2000)
        if hdr2
            hdr2.Click("left")
        else
            Click(hdr.GetPos("screen").x . "," . hdr.GetPos("screen").y)
        Sleep(400)
        LogMessage("    [sort] Created On sorted descending")
        return true
    } catch as e {
        LogMessage("    [sort] error: " . e.Message . " - continuing unsorted")
        return false
    }
}

; ----------------------------------------------------------------------------
; Click the Status-column funnel filter icon and check "CLOSED" so the
; bucket grid shows OPEN+CLOSED buckets (default is OPEN-only). Best-effort:
; ogs and returns false rather than throwing, so a filter miss degrades to
; "only see current OPEN buckets" instead of aborting the whole store pull.
; ----------------------------------------------------------------------------
ScrapApplyClosedFilter() {
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

        closedItem := FindByName(SCRAP_ELEMENTS["filter_closed"], 2500)
        if !closedItem {
            LogMessage("    [filter] CLOSED checkbox not found after opening dropdown - dumping names")
            LogVisibleNames(60)
            Send("{Escape}")
            Sleep(400)
            return false
        }
        closedItem.Click("left")
        Sleep(700)
        LogMessage("    [filter] CLOSED checked")

        ; Close the popup by clicking the dialog's title bar (non-interactive
        ; chrome, sits ~38px above the column header row). Escape did NOT
        ; close this popup in live testing.
        Click(pos.x . "," . (pos.y - 38))
        Sleep(500)
        return true
    } catch as fe {
        LogMessage("    [filter] exception: " . fe.Message . " - proceeding with default view")
        return false
    }
}

; ----------------------------------------------------------------------------
; Walk the (virtualized) Scrap Refining bucket list, same pattern as
; BuysFromPublic.ahk's WriteBuysGridToCsv, but tries BOTH a DevExpress-style
; DataItem grid (composite "Row N of TOTAL, Column LABEL: VALUE" child Names)
; AND a plain ListItem-style list (element's own Name IS the bucket line).
; Dumps the first row's raw children to diagPath for troubleshooting.
; Returns an array of {name, createdOn, status, statusDate, rowIdx}.
; ----------------------------------------------------------------------------
ScrapWalkBucketGrid(diagPath) {
    allRows := Map()
    totalRows := -1
    pagesNoNewRows := 0
    maxPages := 200
    pageIdx := 0
    diagWritten := false

    try {
        root := GetBravoRoot()
        firstDi := root.FindElement({Type: "DataItem"})
        if !firstDi
            firstDi := root.FindElement({Type: "ListItem"})
        if firstDi {
            try firstDi.Click("left")
            Sleep(200)
        }
    }

    Loop maxPages {
        pageIdx++
        items := 0
        itemType := ""
        try {
            root := GetBravoRoot()
            items := root.FindElements({Type: "DataItem"})
            itemType := "DataItem"
            if (!items || items.Length = 0) {
                items := root.FindElements({Type: "ListItem"})
                itemType := "ListItem"
            }
        } catch as e {
            LogMessage("    WARN scrap-grid pass " . pageIdx . " enumerate: " . e.Message)
            break
        }
        if (!items || items.Length = 0) {
            LogMessage("    [scrap-grid] no items on pass " . pageIdx . " (tried DataItem+ListItem)")
            break
        }

        newRowsThisPass := 0
        for it in items {
            if (!diagWritten) {
                try {
                    kids := 0
                    try kids := it.FindElements({Scope: 2})
                    WriteCsvRow(diagPath, "ItemType", itemType, "OwnName", it.Name)
                    if (kids && kids.Length) {
                        for k in kids {
                            kAutoId := "", kName := ""
                            try kAutoId := k.AutomationId
                            try kName := k.Name
                            WriteCsvRow(diagPath, "child", kAutoId, kName)
                        }
                    }
                    diagWritten := true
                }
            }

            rowIdx := -1
            kids := 0
            try kids := it.FindElements({Scope: 2})

            if (kids && kids.Length) {
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
            }
            if (rowIdx < 0) {
                ownName := ""
                try ownName := it.Name
                if (ownName = "")
                    continue
                key := "N:" . ownName
                if (allRows.Has(key))
                    continue
                allRows[key] := {name: ownName, createdOn: "", status: "", statusDate: "", rowIdx: allRows.Count}
                newRowsThisPass++
                continue
            }

            key := "R:" . rowIdx
            if (allRows.Has(key))
                continue

            fields := Map()
            for k in kids {
                kAutoId := "", kName := ""
                try kAutoId := k.AutomationId
                try kName := k.Name
                if (kAutoId = "")
                    continue
                v := kName
                colonPos := InStr(kName, ": ", false, -1)
                if (colonPos > 0)
                    v := SubStr(kName, colonPos + 2)
                fields[kAutoId] := v
            }
            bucketName := ScrapFirstOf(fields, ["Name", "BucketName", "Description"])
            createdOn  := ScrapFirstOf(fields, ["DateCreated", "CreatedOn", "Created On", "CreatedDate"])
            status     := ScrapFirstOf(fields, ["StatusCodeText", "Status"])
            statusDate := ScrapFirstOf(fields, ["StatusDate", "Status Date"])
            allRows[key] := {name: bucketName, createdOn: createdOn, status: status, statusDate: statusDate, rowIdx: rowIdx}
            newRowsThisPass++
        }

        LogMessage("    [scrap-grid pass " . pageIdx . "] new=" . newRowsThisPass . " seen=" . allRows.Count . "/" . (totalRows > 0 ? totalRows : "?"))

        if (totalRows > 0 && allRows.Count >= totalRows) {
            LogMessage("    [scrap-grid] captured all " . totalRows . " rows")
            break
        }
        if (newRowsThisPass = 0) {
            pagesNoNewRows++
            if (pagesNoNewRows >= 20) {
                LogMessage("    [scrap-grid] 8 consecutive pages with no new rows; stopping at " . allRows.Count)
                break
            }
        } else {
            pagesNoNewRows := 0
        }

        ; Scroll via mouse wheel over the grid instead of PgDn - PgDn was
        ; observed live to stop progressing virtualization past ~50 rows
        ; while mouse-wheel scrolling reliably continued in manual testing.
        try {
            if (items && items.Length) {
                ipos := items[1].GetPos("screen")
                MouseMove(ipos.x + Round(ipos.w / 2), ipos.y + Round(ipos.h / 2))
            }
        }
        Send("{WheelDown 15}")
        Sleep(1500)
    }

    out := []
    for _, r in allRows
        out.Push(r)
    return out
}

ScrapFirstOf(fields, keys) {
    for k in keys {
        if fields.Has(k) && fields[k] != ""
            return fields[k]
    }
    return ""
}

; ----------------------------------------------------------------------------
; True if a bucket row plausibly belongs to (year, month): prefer parsing
; CreatedOn as a date and checking it falls within
; [1st of month, 10th of month+1]; fall back to a month/year token match
; against the bucket name (handles rows where CreatedOn wasn't captured).
; ----------------------------------------------------------------------------
ScrapNameOrDateMatchesMonth(b, year, month) {
    if (b.createdOn != "") {
        if RegExMatch(b.createdOn, "(\d{1,2})/(\d{1,2})/(\d{4})", &m) {
            cm := Integer(m[1]), cd := Integer(m[2]), cy := Integer(m[3])
            createdOrdinal := cy * 372 + cm * 31 + cd
            monthStartOrdinal := year * 372 + month * 31 + 1
            nextMonth := month + 1, nextYear := year
            if (nextMonth > 12) {
                nextMonth := 1
                nextYear++
            }
            windowEndOrdinal := nextYear * 372 + nextMonth * 31 + 10
            if (createdOrdinal >= monthStartOrdinal && createdOrdinal <= windowEndOrdinal)
                return true
        }
    }
    yy := Mod(year, 100)
    tokens := [
        month . "/" . yy,
        Format("{:02}/{:02}", month, yy),
        month . "/" . year,
        Format("{:02}/{:04}", month, year)
    ]
    nameStr := b.name
    for t in tokens {
        if InStr(nameStr, t)
            return true
    }
    return false
}

; ----------------------------------------------------------------------------
; Full cycle for reading ONE bucket's Combined Metal Weight: reopen the
; Scrap Refining Process dialog fresh (Done always exits to Inventory, never
; back to the bucket list), reapply the CLOSED filter, scroll via PageDown
; until bucketName is found, double-click it, click Ok, and read Combined
; Metal Weight. Defends against the "queued navigation" bug: if the weight
; seld doesn't appear, re-click "Scrap Refining Process" (fires the queued
; nav) and retry, up to 3 attempts. Always exits via Done/Cancel afterward.
; Returns the numeric dwt value as a string, or "" if unreadable.
; ----------------------------------------------------------------------------
; ----------------------------------------------------------------------------
; Relocate a specific bucket by name using the SAME proven enumerate+scroll
; technique as ScrapWalkBucketGrid (mouse-wheel scroll, full child-field
; extraction), instead of a bare FindByName probe. FindByName alone proved
; unreliable against the virtualized grid; this walks pass-by-pass and opens
; the live element the instant a name match is seen, avoiding a second
; separate lookup against a possibly-recycled UIA reference.
;
; On a fresh dialog open the grid already shows the newest rows first, so
; this only ever scrolls DOWN (toward older rows) - no "scroll to top" step
; is needed or attempted.
; ----------------------------------------------------------------------------
ScrapRelocateAndOpenBucket(targetName) {
    allSeen := Map()
    pagesNoNewRows := 0
    maxPages := 150
    target := Trim(targetName)

    Loop maxPages {
        items := 0
        try {
            root := GetBravoRoot()
            items := root.FindElements({Type: "DataItem"})
            if (!items || items.Length = 0)
                items := root.FindElements({Type: "ListItem"})
        } catch as e {
            LogMessage("      [relocate] enumerate error: " . e.Message)
            break
        }
        if (!items || items.Length = 0) {
            LogMessage("      [relocate] no items visible")
            break
        }

        newRowsThisPass := 0
        for it in items {
            kids := 0
            try kids := it.FindElements({Scope: 2})
            rowIdx := -1
            if (kids && kids.Length) {
                for k in kids {
                    kName := ""
                    try kName := k.Name
                    if RegExMatch(kName, "Row (\d+) of (\d+)", &m) {
                        rowIdx := Integer(m[1])
                        break
                    }
                }
            }
            dedupKey := (rowIdx >= 0) ? ("R:" . rowIdx) : ("N:" . it.Name)
            if (allSeen.Has(dedupKey))
                continue
            allSeen[dedupKey] := true
            newRowsThisPass++

            fields := Map()
            if (kids && kids.Length) {
                for k in kids {
                    kAutoId := "", kName := ""
                    try kAutoId := k.AutomationId
                    try kName := k.Name
                    if (kAutoId = "")
                        continue
                    v := kName
                    colonPos := InStr(kName, ": ", false, -1)
                    if (colonPos > 0)
                        v := SubStr(kName, colonPos + 2)
                    fields[kAutoId] := v
                }
            }
            rowName := ScrapFirstOf(fields, ["Name", "BucketName", "Description"])
            if (rowName = "")
                rowName := it.Name

            if (Trim(rowName) = target) {
                LogMessage("      [relocate] found '" . target . "' on pass " . A_Index . " - opening")
                try {
                    ; Bravo's "queued navigation" quirk: a click fired right after a
                    ; scroll can register against stale internal state and open a
                    ; different row than the one on screen. Give Bravo's UI thread
                    ; extra time to fully commit the scrolled grid before clicking,
                    ; and re-fetch the element's position right at click time in case
                    ; the row shifted during the settle window.
                    Sleep(1200)
                    rpos := it.GetPos("screen")
                    cx := rpos.x + Round(rpos.w / 2)
                    cy := rpos.y + Round(rpos.h / 2)
                    Click(cx . "," . cy)
                    Sleep(400)
                    Click(cx . "," . cy)
                    return true
                } catch as ce {
                    LogMessage("      [relocate] click failed: " . ce.Message)
                    return false
                }
            }
        }

        if (newRowsThisPass = 0) {
            pagesNoNewRows++
            if (pagesNoNewRows >= 20) {
                LogMessage("      [relocate] 8 stalled passes, giving up - saw " . allSeen.Count . " rows, target not among them")
                break
            }
        } else {
            pagesNoNewRows := 0
        }

        try {
            if (items && items.Length) {
                ipos := items[1].GetPos("screen")
                MouseMove(ipos.x + Round(ipos.w / 2), ipos.y + Round(ipos.h / 2))
            }
        }
        Send("{WheelDown 10}")
        Sleep(2500)
    }
    return false
}

; ----------------------------------------------------------------------------
; The "Combined Metal Weight" text on the Scrap Bucket Detail screen is a
; LABEL - its own UIA Name is literally the fixed string "Combined Metal
; Weight" with no value embedded, confirmed via live inspection. The actual
; number (e.g. "113.70dwt") lives in a SEPARATE adjacent value control, not
; a child of the label. Locate it positionally: find the label, then among
; Edit/Text elements find the one vertically aligned with the label and to
; its right (the standard label->value layout used throughout this screen).
; ----------------------------------------------------------------------------
ScrapDumpWeightScreenElements() {
    try {
        root := GetBravoRoot()
        allEl := root.FindElements({})
        n := 0
        for e in allEl {
            n++
            if (n > 90)
                break
            nm := "", vl := "", ty := "", aid := "", py := ""
            try nm := e.Name
            try vl := e.Value
            try ty := e.Type
            try aid := e.AutomationId
            try {
                p := e.GetPos("screen")
                py := p.y
            }
            LogMessage("      [dump] #" . n . " ty=" . ty . " aid=" . aid . " y=" . py . " name='" . nm . "' value='" . vl . "'")
        }
    } catch as e {
        LogMessage("      [dump] error: " . e.Message)
    }
}

ScrapReadCombinedWeightValue() {
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
                if (nm = SCRAP_ELEMENTS["combined_metal_weight"])
                    foundLabel := true
                continue
            }
            checkedSince++
            if (checkedSince > 6)
                break
            val := ""
            try val := e.Value
            if (val != "" && val != SCRAP_ELEMENTS["combined_metal_weight"])
                return val
        }
        return ""
    } catch as e {
        LogMessage("      [weight-read] error: " . e.Message)
        return ""
    }
}



; ----------------------------------------------------------------------------
; Confirm the bucket detail screen actually showing on screen is the one we
; meant to open. Root cause of the earlier bad-data bug: a double-click +
; Ok on a freshly-scrolled-to row can silently open a DIFFERENT (stale /
; queued) record instead - Bravo's own "queued navigation" quirk. That
; wrong-but-real record's weight was getting written to the CSV under the
; TARGET bucket's name, producing plausible-looking but wrong data. This
; check reads the "Bucket Name" field back and compares it to what we
; expected before trusting anything else on the screen.
; ----------------------------------------------------------------------------
ScrapVerifyOpenBucketName(expectedName) {
    try {
        root := GetBravoRoot()
        allEl := ""
        try allEl := root.FindElements({})
        if !allEl
            return false
        foundLabel := false
        checkedSince := 0
        for e in allEl {
            if !foundLabel {
                nm := ""
                try nm := e.Name
                if (nm = "Bucket Name")
                    foundLabel := true
                continue
            }
            checkedSince++
            if (checkedSince > 4)
                break
            val := ""
            try val := e.Value
            if (val != "")
                return (Trim(val) = Trim(expectedName))
        }
        return false
    } catch as e {
        LogMessage("      [verify] error: " . e.Message)
        return false
    }
}

ScrapOpenBucketAndReadWeight(bucketName) {
    weight := ""

    Loop 3 {
        outerAttempt := A_Index

        if !ScrapOpenFilteredBucketList() {
            LogMessage("      [bucket-open] could not reopen filtered bucket list for '" . bucketName . "'")
            continue
        }

        if !ScrapRelocateAndOpenBucket(bucketName) {
            LogMessage("      [bucket-open] could not locate row '" . bucketName . "' via grid walk")
            return ""
        }

        Sleep(1500)
        ; TEST: skip the Ok click entirely - double-click alone may open directly
        Sleep(1000)

        if !ScrapVerifyOpenBucketName(bucketName) {
            LogMessage("      [bucket-open] WRONG BUCKET OPEN on outer attempt " . outerAttempt . " (expected '" . bucketName . "') - backing out and retrying")
            try {
                if FindByName(SCRAP_ELEMENTS["panel_cancel"], 2000)
                    ClickByName(SCRAP_ELEMENTS["panel_cancel"], 2000)
                else if FindByName(SCRAP_ELEMENTS["panel_done"], 2000)
                    ClickByName(SCRAP_ELEMENTS["panel_done"], 2000)
            }
            Sleep(1500)
            try BackToDashboard()
            continue
        }

        LogMessage("      [bucket-open] verified correct bucket open: '" . bucketName . "'")

        Loop 3 {
            attempt := A_Index
            raw := ScrapReadCombinedWeightValue()
            if (raw != "") {
                weight := RegExReplace(raw, "[^0-9.]", "")
                LogMessage("      [bucket-open] raw weight field: '" . raw . "' -> parsed '" . weight . "'")
                if (weight != "")
                    break
            } else {
                LogVisibleNames(60)
            }
            LogMessage("      [bucket-open] attempt " . attempt . " no weight yet for '" . bucketName . "'")
            Sleep(1000)
        }

        ; Exit the detail screen cleanly (Done, per observed flow), with a verify+retry
        ; guard: a Done click that doesn't register was observed to crash the NEXT
        ; bucket's "step 1: open Inventory" (element not found). Confirm we actually
        ; landed back on Inventory before moving on; force-recover via BackToDashboard
        ; if the Done/Cancel click doesn't take after 3 tries.
        exitOk := false
        Loop 3 {
            try {
                if FindByName(SCRAP_ELEMENTS["panel_done"], 2000)
                    ClickByName(SCRAP_ELEMENTS["panel_done"], 2000)
                else if FindByName(SCRAP_ELEMENTS["panel_cancel"], 2000)
                    ClickByName(SCRAP_ELEMENTS["panel_cancel"], 2000)
            }
            Sleep(1500)
            if ExistsByName("Inventory") {
                exitOk := true
                break
            }
            LogMessage("      [bucket-open] Done click did not land on Inventory - retrying exit")
        }
        if !exitOk {
            LogMessage("      [bucket-open] exit retries exhausted - forcing BackToDashboard recovery")
            try BackToDashboard()
        }

        return weight
    }

    LogMessage("      [bucket-open] gave up after 3 outer attempts for '" . bucketName . "' - wrong bucket kept opening")
    return ""
}
