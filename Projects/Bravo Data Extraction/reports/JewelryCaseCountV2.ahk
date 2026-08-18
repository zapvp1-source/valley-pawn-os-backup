; ============================================================================
; reports/JewelryCaseCountV2.ahk
;
; Jewelry Count Reconciliation v4 — COUNT-ONLY on-hand snapshot with
; STABLE-READ GUARD. Additive clone of JewelryCaseCount.ahk (v3), which stays
; registered and untouched (Rule #4).
;
; WHY V2 EXISTS (2026-08-16): the 2026-08-15 nightly recorded three
; clean-looking WRONG counts — CUL Rings 43 (truth ~639), HAR Pendants 173
; (truth ~115), HAR Necklaces 25 (truth ~47). Root cause (confirmed by
; Joshua): the combo-select fallback strategies can land on the WRONG SAVED
; REPORT — the click silently fails to commit or commits a different item,
; and the handler then runs whatever report is loaded and reads ITS row
; total. The number is well-formed, so nothing downstream can tell it's
; wrong. This is the same silent-commit regression that bit "Claude Pawn
; Walks" five times (BRAVO_KNOWN_ISSUES.md) and was ALREADY SOLVED in
; AgedJewelrySales.ahk / SalesDetail.ahk / IntakeDetail.ahk.
;
; GUARD 1 (the fix, ported from AgedJewelrySales.ahk step 3b): after
; selection, read the editor's BoxReportName and VERIFY it matches the
; wanted report; re-select once on mismatch; if still wrong, throw —
; "refusing to run and emit misleading data". The category retry loop and
; the all-or-nothing cell status handle the rest.
;
; GUARD 2 (belt-and-suspenders, ~6s/category): a positive TOTAL is accepted
; only after two reads 6s apart agree, so a still-settling grid can't have
; its partial TOTAL latched. Empty-category behavior is UNCHANGED from v3:
; no parseable total within the window -> ERROR, never 0 (no-false-zeros).
;
; Everything else is byte-for-byte the v3 logic. Reuses
; ReadGridTotalFromAccessibility(), SelectInventorySavedReport(), Fail(),
; BackToDashboard() etc. from the already-included v1 file / watcher.
;
; Trigger schema (new cell name):
;   {"name": "jewelry-case-counts-v2", "stores": ["WAY"], "date": "YYYY-MM-DD"}
;
; Output CSV: SAME path contract as v3 — output/<date>_<STORE>_jewelry-case-counts.csv
;   so the nightly reconciliation's STEP 4 path logic is unchanged.
; ============================================================================

#Requires AutoHotkey v2.0

global JEWELRY_CC_V2_REPORTS := Map(
    "Rings",     "Claude Jewelry Audit - Rings",
    "Pendants",  "Claude Jewelry Audit - Pendants",
    "Earrings",  "Claude Jewelry Audit - Earrings",
    "Chains",    "Claude Jewelry Audit - Chains",
    "Necklaces", "Claude Jewelry Audit - Necklaces",
    "Bracelets", "Claude Jewelry Audit - Bracelets",
    "Charms",    "Claude Jewelry Audit - Charms",
    "Brooches",  "Claude Jewelry Audit - Brooches"
)

global JEWELRY_CC_V2_ORDER := ["Rings", "Bracelets", "Pendants", "Charms", "Brooches", "Earrings", "Chains", "Necklaces"]

global JEWELRY_CC_V2_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel"
)

; ----------------------------------------------------------------------------
; GUID-first selection (added 2026-08-16 after the by-name selector ground to
; a halt on the fresh Bravo session — WAY Rings burned 20+ min failing).
;
; 2026-08-11 UIA recon (NicsTransfers.ahk): in this dialog the dropdown items'
; UIA Names are the report's "Object_Layout: <guid>" string, NEVER the display
; text. That is why ClickByName/type-ahead are structurally unreliable here.
; NicsSelectSavedReport(guid, verifyName) selects by stable layout GUID and
; returns true ONLY after BoxReportName confirms the display name — the
; deterministic path.
;
; We do not know a priori which GUID belongs to which jewelry report, so v2
; LEARNS the mapping: probe candidate GUIDs (seeded with every Object_Layout
; GUID observed in the 8/14-8/16 logs, then anything else in the live list),
; confirm via BoxReportName, and persist verified pairs to a cache file. After
; first discovery every selection is a single direct GUID commit.
; A re-saved report (new GUID) self-heals: cache miss -> re-probe -> re-cache.
; ----------------------------------------------------------------------------
global JEWELRY_CC_V2_SEED_GUIDS := [
    "a05ff530-edf3-4d0b-9ccd-8865b1c5a4e0",
    "cd1c5315-5c29-40ab-b0a9-2b169d152e20",
    "90e13375-b04a-4636-9dc1-1917c9ba57c5",
    "ed163275-2035-4004-9dbe-8c58c924b408",
    "cdd9900d-465f-4b69-9489-bf5960bef767",
    "3e039dcd-d682-4aed-b1e7-f84bfe3fa025",
    "f14f57dd-ea42-4212-955c-ee9d6d7817ad",
    "080dfd2f-94b0-46dc-a028-eeb943af7b89",
    "ba338093-91ec-4c5b-a30b-bb89f0f18df6",
    "05f639c3-4c58-4875-b42e-a3eab85364d1",
    "bccdfcfe-fd73-4182-b233-4d6b71009586",
    "0898b8bd-3446-405a-b373-091f1e8d98ab"
]

; Read the loaded report's display name from BoxReportName — .Value with a
; .Name fallback (AgedJewelrySales pattern; IntakeGetLoadedReportName reads
; only .Value, which can be empty in this dialog — observed 2026-08-16, six
; consecutive probes returning '' on WAY).
JewelryV2LoadedReportName() {
    try {
        root := GetBravoRoot()
        el := root.FindElement({AutomationId: "BoxReportName"})
        if el {
            v := ""
            try v := el.Value
            if (v = "")
                try v := el.Name
            return v
        }
    }
    return ""
}

; Read the currently-loaded report's layout GUID off the Object_Layout combo.
JewelryV2CurrentComboGuid() {
    try {
        root := GetBravoRoot()
        eds := root.FindElements({Type: "Edit"})
        if eds {
            for e in eds {
                nm := ""
                try nm := e.Name
                if (nm != "BravoComboBox")
                    continue
                val := ""
                try val := e.Value
                if RegExMatch(val, "Object_Layout:\s*([0-9a-f-]{36})", &mm)
                    return mm[1]
            }
        }
    }
    return ""
}

JewelryV2GuidCachePath() {
    global SCRIPT_DIR
    return SCRIPT_DIR . "\jewelry_v2_guid_cache.txt"
}

JewelryV2LoadGuidCache() {
    m := Map()
    try {
        txt := FileRead(JewelryV2GuidCachePath(), "UTF-8")
        Loop Parse, txt, "`n", "`r" {
            if !InStr(A_LoopField, "=")
                continue
            parts := StrSplit(A_LoopField, "=", , 2)
            if (parts.Length = 2 && parts[1] != "" && parts[2] != "")
                m[Trim(parts[1])] := Trim(parts[2])
        }
    }
    return m
}

JewelryV2SaveGuidCache(m) {
    out := ""
    for k, v in m
        out .= k . "=" . v . "`n"
    try {
        p := JewelryV2GuidCachePath()
        try FileDelete(p)
        FileAppend(out, p, "UTF-8")
    }
}

; Enumerate GUIDs currently visible in the open saved-report dropdown (window
; root + desktop root, same dual-scope trick as NicsSelectSavedReport).
JewelryV2EnumerateListGuids() {
    guids := []
    seen := Map()
    ; find + open the Object_Layout combo (positional fallback, per Nics)
    root := 0
    try root := GetBravoRoot()
    if !root
        return guids
    repCombo := 0, bestT := -1, fallback := 0
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    if eds {
        for e in eds {
            nm := ""
            try nm := e.Name
            if (nm != "BravoComboBox")
                continue
            val := ""
            try val := e.Value
            if (SubStr(val, 1, 14) = "Object_Layout:") {
                repCombo := e
                break
            }
            et := -1, ex := -1
            try et := e.BoundingRectangle.t
            try ex := e.BoundingRectangle.l
            if (ex > 700 && et > bestT) {
                bestT := et
                fallback := e
            }
        }
    }
    if !repCombo
        repCombo := fallback
    if !repCombo
        return guids
    try {
        repCombo.ExpandCollapsePattern.Expand()
    } catch {
        try repCombo.Click("left")
    }
    Sleep(1200)
    ; Bravo root only — see wedge note in JewelryV2CommitGuid.
    r2 := 0
    try r2 := GetBravoRoot()
    if r2 {
        lis := 0
        try lis := r2.FindElements({Type: "ListItem"})
        if lis {
            for li in lis {
                ln := ""
                try ln := li.Name
                if RegExMatch(ln, "Object_Layout:\s*([0-9a-f-]{36})", &mm) {
                    g := mm[1]
                    if !seen.Has(g) {
                        seen[g] := 1
                        guids.Push(g)
                    }
                }
            }
        }
    }
    try repCombo.ExpandCollapsePattern.Collapse()
    Sleep(400)
    return guids
}

; Commit a report by layout GUID: open the Object_Layout combo, click the
; ListItem whose Name carries the GUID, close the dropdown. Returns true if
; the item was found and clicked (NOT yet verified — caller reads
; BoxReportName). Condensed from NicsSelectSavedReport's proven mechanics.
JewelryV2CommitGuid(reportGuid) {
    root := 0
    try root := GetBravoRoot()
    if !root
        return false
    repCombo := 0, bestT := -1, fallback := 0
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    if eds {
        for e in eds {
            nm := ""
            try nm := e.Name
            if (nm != "BravoComboBox")
                continue
            val := ""
            try val := e.Value
            if (SubStr(val, 1, 14) = "Object_Layout:") {
                repCombo := e
                break
            }
            et := -1, ex := -1
            try et := e.BoundingRectangle.t
            try ex := e.BoundingRectangle.l
            if (ex > 700 && et > bestT) {
                bestT := et
                fallback := e
            }
        }
    }
    if !repCombo
        repCombo := fallback
    if !repCombo
        return false
    try {
        repCombo.ExpandCollapsePattern.Expand()
    } catch {
        try repCombo.Click("left")
    }
    Sleep(800)
    ; BRAVO ROOT ONLY (2026-08-16): desktop-root FindElements can block for
    ; minutes / indefinitely on this session — the wedge signature seen in
    ; both the by-name walker and the first probe iterations. Bravo-root
    ; scans have returned reliably all day.
    item := 0
    Loop 6 {
        r2 := 0
        try r2 := GetBravoRoot()
        if r2 {
            lis := 0
            try lis := r2.FindElements({Type: "ListItem"})
            if lis {
                for li in lis {
                    ln := ""
                    try ln := li.Name
                    if (InStr(ln, reportGuid)) {
                        item := li
                        break
                    }
                }
            }
        }
        if (item)
            break
        if (A_Index = 3) {
            try {
                repCombo.ExpandCollapsePattern.Expand()
            } catch {
                try repCombo.Click("left")
            }
        }
        Sleep(300)
    }
    if !item {
        try repCombo.ExpandCollapsePattern.Collapse()
        return false
    }
    committed := false
    try {
        item.Click("left")
        committed := true
    } catch {
        try {
            item.SelectionItemPattern.Select()
            Sleep(300)
            Send("{Enter}")
            committed := true
        }
    }
    Sleep(1200)
    try repCombo.ExpandCollapsePattern.Collapse()
    Sleep(400)
    return committed
}

; The v2 selector. GUIDs are PER-STORE (proven 2026-08-16: none of the
; HAR/LEX/WAY-observed GUIDs appear in CUL's live list), so the cache is
; keyed "STORE|Category". Discovery probes the LIVE list first and caches
; EVERY jewelry report it identifies along the way — the first category pays
; the discovery cost once per store, ever; the rest are direct GUID commits.
JewelryV2SelectReport(store, category, wantReport) {
    global JEWELRY_CC_V2_REPORTS, JEWELRY_CC_V2_SEED_GUIDS
    cache := JewelryV2LoadGuidCache()
    ckey := store . "|" . category

    if cache.Has(ckey) {
        LogMessage("      [guid-select] cached GUID for " . ckey . ": " . SubStr(cache[ckey], 1, 8) . "...")
        if JewelryV2CommitGuid(cache[ckey]) {
            lnc := ""
            Loop 6 {
                try lnc := JewelryV2LoadedReportName()
                if (lnc != "")
                    break
                Sleep(500)
            }
            if InStr(lnc, wantReport) {
                LogMessage("      [guid-select] cached GUID verified ('" . lnc . "')")
                return true
            }
            LogMessage("      [guid-select] cached GUID loaded '" . lnc . "' — mismatch")
        }
        LogMessage("      [guid-select] cached GUID failed — re-probing (report may have been re-saved)")
        cache.Delete(ckey)
        JewelryV2SaveGuidCache(cache)
    }

    ; ---- TIER 2 (2026-08-16 reorder): by-name selector FIRST. On a healthy
    ; Bravo it lands in seconds; on a sick Bravo nothing works and the health
    ; gate is the real fix. If the loaded name verifies, CAPTURE the loaded
    ; report's layout GUID off the combo and cache it — from then on this
    ; store+category selects via the direct cached-GUID path above.
    if SelectInventorySavedReport(wantReport) {
        lnn := ""
        Loop 6 {
            try lnn := JewelryV2LoadedReportName()
            if (lnn != "")
                break
            Sleep(500)
        }
        if InStr(lnn, wantReport) {
            g := JewelryV2CurrentComboGuid()
            if (g != "") {
                cache[ckey] := g
                JewelryV2SaveGuidCache(cache)
                LogMessage("      [guid-select] by-name verified ('" . lnn . "') — captured GUID " . SubStr(g, 1, 8) . "... and cached")
            } else {
                LogMessage("      [guid-select] by-name verified ('" . lnn . "') — no GUID readable, not cached")
            }
            return true
        }
        LogMessage("      [guid-select] by-name selected but loaded '" . lnn . "' — mismatch, falling to GUID probe")
    }

    ; GUIDs already mapped for THIS store are skipped during probing.
    claimed := Map()
    for k, v in cache
        if (SubStr(k, 1, StrLen(store) + 1) = store . "|")
            claimed[v] := k

    candidates := []
    tried := Map()
    for g in JewelryV2EnumerateListGuids() {          ; live list first — ground truth
        if (!claimed.Has(g) && !tried.Has(g)) {
            candidates.Push(g)
            tried[g] := 1
        }
    }
    for g in JEWELRY_CC_V2_SEED_GUIDS {               ; historical seeds as backstop
        if (!claimed.Has(g) && !tried.Has(g)) {
            candidates.Push(g)
            tried[g] := 1
        }
    }

    LogMessage("      [guid-select] probing " . candidates.Length . " candidate GUIDs for " . ckey)
    probeStart := A_TickCount
    for g in candidates {
        if (A_TickCount - probeStart > 300000) {
            LogMessage("      [guid-select] probe budget (300s) exhausted — giving up this attempt")
            return false
        }
        ok := JewelryV2CommitGuid(g)
        if !ok {
            LogMessage("      [guid-select] probe " . SubStr(g, 1, 8) . "... item-not-found/commit-failed")
            continue
        }
        ln := ""
        Loop 6 {
            try ln := JewelryV2LoadedReportName()
            if (ln != "")
                break
            Sleep(500)
        }
        LogMessage("      [guid-select] probe " . SubStr(g, 1, 8) . "... loaded='" . ln . "'")
        if (ln = "")
            continue
        ; opportunistic discovery: whatever jewelry report this GUID turned
        ; out to be, cache it now so later categories skip the hunt.
        for cat, rep in JEWELRY_CC_V2_REPORTS {
            if InStr(ln, rep) {
                cache[store . "|" . cat] := g
                JewelryV2SaveGuidCache(cache)
                LogMessage("      [guid-select] discovered " . store . "|" . cat . " = " . SubStr(g, 1, 8) . "... ('" . ln . "')")
                break
            }
        }
        if InStr(ln, wantReport) {
            LogMessage("      [guid-select] " . ckey . " resolved and VERIFIED via BoxReportName")
            return true
        }
    }

    LogMessage("      [guid-select] probe exhausted — falling back to by-name selector")
    return SelectInventorySavedReport(wantReport)
}

; ----------------------------------------------------------------------------
; RunOneJewelryCategoryCountV2()
;
; Identical to v3's RunOneJewelryCategoryCount except step 5, which now
; requires TWO consecutive identical positive reads 6s apart (stable-read
; guard) and extends the window 90s -> 120s to make room for the second read.
; Returns the count (>=1), or -1 on failure. NEVER returns 0.
; ----------------------------------------------------------------------------
RunOneJewelryCategoryCountV2(store, category, wantReport) {
    count := -1

    DismissPopups()
    LogMessage("    step 1: open Inventory")
    ClickByName(JEWELRY_CC_V2_ELEMENTS["sidebar_inventory"], 8000)
    Sleep(1500)
    DismissPopups()

    LogMessage("    step 2: click Custom Reports")
    ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_custom_reports"], 5000)
    Sleep(1500)

    LogMessage("    step 3: select saved report '" . wantReport . "' (GUID-first)")
    if !JewelryV2SelectReport(store, category, wantReport)
        throw Error("JewelryV2SelectReport: could not select " . wantReport)
    Sleep(1200)

    ; ---- step 3b: VERIFY the selection actually committed ------------------
    ; Ported verbatim from AgedJewelrySales.ahk (proven in production). The
    ; item click can silently fail to commit — or commit a DIFFERENT report —
    ; leaving the previous/wrong report loaded. Running it anyway produces a
    ; clean-looking wrong count (2026-08-15: CUL Rings 43, HAR Pendants 173,
    ; HAR Necklaces 25). Verify BoxReportName, re-select once if wrong.
    LogMessage("    step 3b: verify report name committed")
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
        LogMessage("      BoxReportName = '" . loadedName . "'")
        if (loadedName != "" && InStr(loadedName, wantReport)) {
            verified := true
            break
        }
        if (A_Index = 1) {
            LogMessage("      WARN: report name mismatch — re-selecting once")
            try SelectInventorySavedReport(wantReport)
            Sleep(1500)
        }
    }
    if (!verified)
        throw Error("Saved report '" . wantReport . "' did not load (wrong report still active) — refusing to run and emit misleading data")
    LogMessage("      verified OK")

    LogMessage("    step 4: click Ok to run")
    Sleep(2500)
    ActivateBravo()
    Sleep(500)
    try {
        ClickByName("Ok", 5000)
    } catch as okErr {
        Send("{Enter}")
        LogMessage("      Ok not found (" . okErr.Message . ") -- sent {Enter} fallback")
    }
    Sleep(2000)

    LogMessage("    step 5: wait for grid, read row total (v2 stable-read guard)")
    rendCheckStart := A_TickCount
    candidate := -1
    Loop {
        c := ReadGridTotalFromAccessibility()
        if (c > 0) {
            if (candidate > 0 && c = candidate) {
                count := c
                LogMessage("      [count] " . category . " = " . count
                         . " (STABLE across two reads 6s apart, after "
                         . ((A_TickCount - rendCheckStart) // 1000) . "s, no walk)")
                break
            }
            if (candidate > 0 && c != candidate)
                LogMessage("      [count] " . category . " UNSTABLE: " . candidate
                         . " -> " . c . " — grid still settling, waiting for agreement")
            candidate := c
        }
        if (A_TickCount - rendCheckStart > 120000) {
            LogMessage("      [count] " . category . " — no STABLE row total after 120s"
                     . (candidate > 0 ? " (last unconfirmed candidate " . candidate . ", NOT accepted)" : ""))
            break
        }
        Sleep(6000)
    }

    ; Leave the report editor cleanly regardless of outcome (stranded-editor
    ; defense, same as v3).
    try ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_cancel"], 3000)
    Sleep(800)
    try ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_cancel"], 3000)
    Sleep(800)
    if !BackToDashboard()
        throw Error("BackToDashboard failed after category " . category)
    Sleep(500)

    return count
}

; ----------------------------------------------------------------------------
; PullJewelryCaseCountsV2() — the cell entry point for jewelry-case-counts-v2.
; Identical to v3's PullJewelryCaseCounts apart from names and the report id.
; ----------------------------------------------------------------------------
PullJewelryCaseCountsV2(store, asOfDate, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "jewelry-case-counts-v2",
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    global JEWELRY_CC_V2_REPORTS, JEWELRY_CC_V2_ORDER

    LogMessage("[" . store . "] JewelryCaseCountV2 — 8 categories, count-only, stable-read guard, as-of=" . asOfDate)

    outputFileName := asOfDate . "_" . store . "_jewelry-case-counts.csv"
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

    ; Pre-dismiss stranded dialogs (same defense as v3).
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
        if (!dismissed)
            break
    }
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    counts   := Map()
    statuses := Map()
    okCount  := 0

    for category in JEWELRY_CC_V2_ORDER {
        wantReport := JEWELRY_CC_V2_REPORTS[category]
        LogMessage("  --- category " . category . " ('" . wantReport . "') ---")

        got := -1
        Loop 2 {   ; one retry per category before giving up on it
            attempt := A_Index
            try {
                got := RunOneJewelryCategoryCountV2(store, category, wantReport)
            } catch as e {
                LogMessage("    attempt " . attempt . " threw: " . e.Message)
                got := -1
                try {
                    Loop 2 {
                        try ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_cancel"], 2000)
                        Sleep(700)
                    }
                    BackToDashboard()
                }
                Sleep(1000)
            }
            if (got > 0)
                break
            if (attempt = 1)
                LogMessage("    retrying " . category . " once")
        }

        if (got > 0) {
            counts[category]   := got
            statuses[category] := "ok"
            okCount++
        } else {
            counts[category]   := ""
            statuses[category] := "error"
            LogMessage("    " . category . " FAILED after 2 attempts — recorded as error, NOT as zero")
        }
    }

    csv := "store,category,as_of,count,status`n"
    for category in JEWELRY_CC_V2_ORDER {
        csv .= store . "," . category . "," . asOfDate . ","
             . counts[category] . "," . statuses[category] . "`n"
    }

    try {
        ResetOutputFile(outputPath)
        FileAppend(csv, outputPath, "UTF-8")
    } catch as we {
        return Fail(result, started, "Could not write CSV: " . we.Message)
    }

    result["output_path"] := outputPath
    result["row_count"]   := okCount

    if (okCount < JEWELRY_CC_V2_ORDER.Length) {
        failed := ""
        for category in JEWELRY_CC_V2_ORDER
            if (statuses[category] != "ok")
                failed .= (failed = "" ? "" : ", ") . category
        return Fail(result, started
                  , "Only " . okCount . " of " . JEWELRY_CC_V2_ORDER.Length
                  . " categories returned a count. Failed: " . failed
                  . ". Refusing to report a partial jewelry count as success.")
    }

    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: all 8 category counts read (stable), " . result["duration_ms"] . "ms")
    return result
}
