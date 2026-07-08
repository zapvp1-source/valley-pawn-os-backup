; reports/ChekkitGridOnly.ahk
; Grid-only reader with SCROLL + ACCUMULATE. Assumes the Chekkit Invites report
; grid is ALREADY showing on the active store. Bravo's grid is virtualized
; (only ~visible rows are in the UIA tree), so this scrolls from top to bottom,
; reads the visible TextEdit cells at each step, and de-duplicates by phone|email
; to assemble the full list. Reuses no fragile navigation.
;
; Usage: manually run the "Chekkit Invites 2" report on the target store so the
; grid is on screen, then drop a chekkit-gridonly trigger for that store.
#Requires AutoHotkey v2.0

PullChekkitGridOnly(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "chekkit-gridonly",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )
    outputPath := outputDir . "\" . OutputFilename(date, store, "chekkit-gridonly")
    LogMessage("[" . store . "] ChekkitGridOnly (scroll+accumulate) -> " . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")

    ActivateBravo()
    DismissPopups()
    ResetOutputFile(outputPath)

    try {
        rows := ScrollAndCollectChekkitRows()
        FileAppend("first_name,last_name,phone,email,dnt,last_visit`r`n", outputPath, "UTF-8-RAW")
        count := 0
        for r in rows {
            dntStr := r["dnt"] ? "DNT" : ""
            WriteCsvRow(outputPath, r.Has("name") ? r["name"] : "", "", r["phone"], r["email"], dntStr, "")
            count++
        }
        LogMessage("    wrote " . count . " rows to CSV")
        result["row_count"] := count
    } catch as e {
        return Fail(result, started, "ChekkitGridOnly failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; Read the currently-visible Chekkit grid rows. Returns an array of
; Map("phone","email","dnt").
ReadVisibleChekkitRows() {
    rows := []
    cells := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            try {
                n := ""
                try n := e.Name
                if (n != "TextEdit")
                    continue
                autoId := ""
                try autoId := e.AutomationId
                if (autoId = "PART_Editor")
                    continue
                rect := 0
                try rect := e.BoundingRectangle
                if !rect
                    continue
                val := ""
                try val := e.Value
                if (val = "")
                    continue
                cells.Push(Map("val", val, "x", rect.l, "y", rect.t))
            }
        }
    } catch as ex {
        return rows
    }
    if (cells.Length = 0)
        return rows

    ; insertion sort by y then x
    n := cells.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1) {
            a := cells[j]
            b := cells[j - 1]
            if (a["y"] < b["y"] || (a["y"] = b["y"] && a["x"] < b["x"])) {
                cells[j] := b
                cells[j - 1] := a
                j--
            } else {
                break
            }
        }
        i++
    }

    ; group into rows by y proximity
    grouped := []
    currentRow := []
    currentY := -99999
    yTol := 12
    for c in cells {
        if (Abs(c["y"] - currentY) > yTol) {
            if (currentRow.Length > 0)
                grouped.Push(currentRow)
            currentRow := []
            currentY := c["y"]
        }
        currentRow.Push(c["val"])
    }
    if (currentRow.Length > 0)
        grouped.Push(currentRow)

    nameMap := BuildVisibleNameMapByPhone()
    for g in grouped {
        phone := ""
        email := ""
        isDnt := false
        for cell in g {
            c := Trim(cell)
            if (c = "")
                continue
            if (InStr(c, "@")) {
                if (email = "")
                    email := c
                continue
            }
            if (c = "DNT") {
                isDnt := true
                continue
            }
            if ((SubStr(c, 1, 1) = "(" || SubStr(c, 1, 4) = "+1-(") && InStr(c, "-")) {
                if (phone = "")
                    phone := c
                continue
            }
        }
        if (phone = "" && email = "")
            continue
        nm := (phone != "" && nameMap.Has(phone)) ? nameMap[phone] : ""
        rows.Push(Map("phone", phone, "email", email, "dnt", isDnt, "name", nm))
    }
    return rows
}

; Scroll from top to bottom, accumulating unique rows (key = phone|email).
ScrollAndCollectChekkitRows() {
    seen := Map()
    out := []

    ; focus the grid by clicking the first visible data cell
    fc := ReadFirstCellCenter()
    if fc {
        try {
            MouseClick("Left", fc["cx"], fc["cy"])
            Sleep(200)
        }
    }
    try Send("^{Home}")
    Sleep(450)

    stable := 0
    loop 80 {
        vis := ReadVisibleChekkitRows()
        added := 0
        for r in vis {
            key := r["phone"] . "|" . r["email"]
            if (key = "|")
                continue
            if !seen.Has(key) {
                seen[key] := true
                out.Push(r)
                added++
            }
        }
        LogMessage("    [scroll] pass rows=" . vis.Length . " new=" . added . " total=" . out.Length)
        if (added = 0)
            stable++
        else
            stable := 0
        if (stable >= 2)
            break
        Send("{PgDn}")
        Sleep(400)
    }
    return out
}

; Center coords of the topmost visible TextEdit cell (to click for grid focus).
ReadFirstCellCenter() {
    best := 0
    bestY := 99999999
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            try {
                n := ""
                try n := e.Name
                if (n != "TextEdit")
                    continue
                rect := 0
                try rect := e.BoundingRectangle
                if !rect
                    continue
                val := ""
                try val := e.Value
                if (val = "")
                    continue
                if (rect.t < bestY) {
                    bestY := rect.t
                    best := Map("cx", Integer((rect.l + rect.r) // 2), "cy", Integer((rect.t + rect.b) // 2))
                }
            }
        }
    } catch as ex {
        return 0
    }
    return best
}

; ---- Name lookup from DataItem grid rows (aid=FullName / PublicPhone) -------
; Bravo's customer grid rows are DataItem elements; children carry the display
; value in .Name as "Row N of T, Column L, Column X of Y: VALUE", keyed by
; AutomationId. TextEdit cells only expose phone/DNT, not the name, so we build
; a phone->name map here and attach it to each assembled row by phone.
BuildVisibleNameMapByPhone() {
    m := Map()
    try {
        root := GetBravoRoot()
        dis := root.FindElements({Type: "DataItem"})
        for di in dis {
            kids := 0
            try kids := di.FindElements({Scope: 2})
            if (!kids)
                continue
            nm := "", ph := ""
            for k in kids {
                aid := ""
                try aid := k.AutomationId
                if (aid != "FullName" && aid != "PublicPhone")
                    continue
                kn := ""
                try kn := k.Name
                val := ExtractDiValue(kn)
                if (aid = "FullName")
                    nm := val
                else if (aid = "PublicPhone")
                    ph := val
            }
            if (ph != "" && nm != "")
                m[ph] := nm
        }
    }
    return m
}

; Extract the value after the last ": " (e.g. "... Column 1 of 4: JOHN SMITH").
ExtractDiValue(s) {
    p := InStr(s, ": ", true, -1)
    if (p)
        return Trim(SubStr(s, p + 2))
    return Trim(s)
}
