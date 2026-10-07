; ============================================================================
; reports/JewelryCaseCountV3.ahk
;
; Jewelry case count v5: V2 + DUPLICATE RE-VERIFICATION. Additive: V2
; (JewelryCaseCountV2.ahk, cell jewelry-case-counts-v2) stays registered and
; byte-for-byte untouched. This file only CALLS V2's per-category reader
; (RunOneJewelryCategoryCountV2) and selector; it redefines nothing.
;
; WHY V3 EXISTS (2026-10-06): V2's GUARD 3 fails the WHOLE store whenever two
; categories share a count ("possible stale-grid contamination"). Since
; 2026-09-30 Culpeper genuinely has Charms 19 and Brooches 19 (history: Charms
; 20 -> 19 on 9/29 while Brooches was still 18, then Brooches 18 -> 19 on 9/30;
; both values moved independently). Every CUL log since shows each category
; selected by its own BoxReportName-verified pick and its own run, yet GUARD 3
; refused CUL every night (9/30, 10/1, 10/2, 10/5 x2) - a false positive, not
; a stale grid. GUARD 3 cannot tell a coincidence from contamination, so it
; will keep failing for as long as the real inventory matches.
;
; THE FIX: instead of refusing on sight, PROVE or DISPROVE the duplicate.
; For every duplicate group (value V shared by categories C1..Ck):
;   - pick a SEPARATOR category whose count is ok and != V (largest first,
;     normally Rings);
;   - in REVERSE order, re-run the separator and then Ci, back to back.
; A stale grid serves the PREVIOUS render's total. Because the separator ran
; immediately before Ci and rendered a different number, a stale read of Ci
; would show the separator's count, not V. So: Ci re-reads == V right after a
; separator read != V  ==> Ci's V was freshly rendered for Ci's own report.
; If every Ci confirms, the duplicate is real and the store succeeds. If any
; re-read disagrees (or the separator is unavailable), the store fails exactly
; as V2 did - same "Duplicate counts..." error text, plus the re-read detail.
; Nothing is ever written as a count that Bravo did not render.
;
; SECOND CHANGE (same day, after the first proving run wedged at 16:43 inside
; V2's selector): category selection tries a LEAN path first (one arrow click,
; type-ahead, ClickByName, BoxReportName verify) and only falls back to V2's
; full selector if that does not verify. See JewelryV3LeanSelect below.
;
; Everything else (BoxReportName verify, stable-read guard,
; no-false-zero rule, 8/8 all-or-nothing, CSV columns and path) is V2's.
;
; Cells:
;   jewelry-case-counts-v3         -> output/<date>_<STORE>_jewelry-case-counts.csv
;                                     (same path contract as v2 - the nightly reads it)
;   jewelry-case-counts-v3-verify  -> output/<date>_<STORE>_jewelry-case-counts-v3verify.csv
;                                     (daytime proving runs; never collides with the
;                                     nightly's file or its reuse check)
; ============================================================================

#Requires AutoHotkey v2.0

PullJewelryCaseCountsV3(store, asOfDate, outputDir) {
    return JewelryV3Core(store, asOfDate, outputDir, "jewelry-case-counts-v3", "_jewelry-case-counts.csv")
}

PullJewelryCaseCountsV3Verify(store, asOfDate, outputDir) {
    return JewelryV3Core(store, asOfDate, outputDir, "jewelry-case-counts-v3-verify", "_jewelry-case-counts-v3verify.csv")
}

; ----------------------------------------------------------------------------
; LEAN SELECTOR (2026-10-06, second half of the fix). Every V2 selection in
; every log since 9/21 goes: cached-GUID commit (expand/collapse, never finds
; the item, fails after ~6s) -> arrow click -> combo.Focus()+F4 -> combo.Focus()
; +Alt+Down -> combo.Focus()+type-ahead -> ClickByName. Only the LAST two steps
; ever select anything; the rest toggle the DevExpress popup open/closed/open
; with synchronous UIA Focus() calls in between. The nightly wedges (log stops
; dead for 40 min) sit exactly in that sequence or in the first grid read
; after it - including the 10/6 16:43 proving run, frozen right after
; "[inv-select] still no item — Alt+Down". V3 therefore tries the minimal
; proven path first: ONE physical arrow click (async mouse message, no UIA
; Focus), type-ahead, ClickByName, then BoxReportName must match. Only if
; that does not verify does it fall back to V2's full selector unchanged.
; ----------------------------------------------------------------------------
JewelryV3LeanSelect(wantReport) {
    combo := FindSavedReportCombo()
    if !combo
        return false
    rect := 0
    try rect := combo.BoundingRectangle
    if !rect
        return false
    CoordMode "Mouse", "Screen"
    cy := Integer(rect.t + rect.b) // 2
    cx := Integer(rect.r - 20)
    LogMessage("      [lean-select] arrow click at (" . cx . "," . cy . "), type-ahead '" . wantReport . "'")
    MouseClick("Left", cx, cy)
    Sleep(1500)
    Loop Parse, wantReport {
        SendText(A_LoopField)
        Sleep(60)
    }
    Sleep(800)
    try {
        ClickByName(wantReport, 2500)
    } catch {
        LogMessage("      [lean-select] item not clickable after type-ahead")
        return false
    }
    Sleep(700)
    ln := ""
    Loop 6 {
        try ln := JewelryV2LoadedReportName()
        if (ln != "")
            break
        Sleep(500)
    }
    if InStr(ln, wantReport) {
        LogMessage("      [lean-select] verified ('" . ln . "')")
        return true
    }
    LogMessage("      [lean-select] loaded '" . ln . "' — not verified")
    return false
}

; V2's RunOneJewelryCategoryCountV2 with ONE difference: step 3 tries the lean
; selector first (V2 selector as fallback), and the step-3b re-select uses the
; lean selector too. Steps 1, 2, 3b verify, 4, 5 (stable-read guard, 120s,
; never returns 0) and the exit path are V2's, verbatim.
RunOneJewelryCategoryCountV3(store, category, wantReport) {
    global JEWELRY_CC_V2_ELEMENTS
    count := -1

    DismissPopups()
    LogMessage("    step 1: open Inventory")
    ClickByName(JEWELRY_CC_V2_ELEMENTS["sidebar_inventory"], 8000)
    Sleep(1500)
    DismissPopups()

    LogMessage("    step 2: click Custom Reports")
    ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_custom_reports"], 5000)
    Sleep(1500)

    LogMessage("    step 3: select saved report '" . wantReport . "' (lean first, V2 fallback)")
    if !JewelryV3LeanSelect(wantReport) {
        LogMessage("      [lean-select] falling back to V2 selector")
        if !JewelryV2SelectReport(store, category, wantReport)
            throw Error("JewelryV2SelectReport: could not select " . wantReport)
    }
    Sleep(1200)

    LogMessage("    step 3b: verify report name committed")
    verified := false
    Loop 2 {
        loadedName := ""
        try loadedName := JewelryV2LoadedReportName()
        LogMessage("      BoxReportName = '" . loadedName . "'")
        if (loadedName != "" && InStr(loadedName, wantReport)) {
            verified := true
            break
        }
        if (A_Index = 1) {
            LogMessage("      WARN: report name mismatch — re-selecting once")
            try {
                if !JewelryV3LeanSelect(wantReport)
                    SelectInventorySavedReport(wantReport)
            }
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

    try ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_cancel"], 3000)
    Sleep(800)
    try ClickByName(JEWELRY_CC_V2_ELEMENTS["panel_cancel"], 3000)
    Sleep(800)
    if !BackToDashboard()
        throw Error("BackToDashboard failed after category " . category)
    Sleep(500)

    return count
}

; One category, V2's own two-attempt policy. Returns count >= 1 or -1.
JewelryV3ReadCategory(store, category) {
    global JEWELRY_CC_V2_REPORTS, JEWELRY_CC_V2_ELEMENTS
    wantReport := JEWELRY_CC_V2_REPORTS[category]
    got := -1
    Loop 2 {
        attempt := A_Index
        try {
            got := RunOneJewelryCategoryCountV3(store, category, wantReport)
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
    return got
}

JewelryV3Core(store, asOfDate, outputDir, cellName, fileSuffix) {
    started := A_TickCount
    result := Map(
        "report",      cellName,
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    global JEWELRY_CC_V2_REPORTS, JEWELRY_CC_V2_ORDER, CONFIG

    LogMessage("[" . store . "] JewelryCaseCountV3 (" . cellName . ") — 8 categories, stable-read + duplicate re-verification, as-of=" . asOfDate)

    outputPath := outputDir . "\" . asOfDate . "_" . store . fileSuffix
    LogMessage("  output -> " . outputPath)

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")

    ActivateBravo()
    DismissPopups()

    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ; Pre-dismiss stranded dialogs (same defense as v2/v3).
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

    counts   := Map()
    statuses := Map()
    okCount  := 0

    for category in JEWELRY_CC_V2_ORDER {
        LogMessage("  --- category " . category . " ('" . JEWELRY_CC_V2_REPORTS[category] . "') ---")
        got := JewelryV3ReadCategory(store, category)
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

    ; ---- duplicate detection (same grouping as V2 GUARD 3) ------------------
    dupGroups := Map()
    for category in JEWELRY_CC_V2_ORDER {
        if (statuses[category] != "ok")
            continue
        v := counts[category]
        if !dupGroups.Has(v)
            dupGroups[v] := []
        dupGroups[v].Push(category)
    }

    dupFail := ""        ; non-empty => refuse the store
    dupConfirmed := ""   ; log/summary of duplicates proven genuine
    for v, cats in dupGroups {
        if (cats.Length < 2)
            continue
        catList := ""
        for c in cats
            catList .= (catList = "" ? "" : ",") . c
        LogMessage("  [dup-verify] " . v . " shared by [" . catList . "] — re-verifying with a separator read before each")

        ; separator: ok category with count != v, largest count first
        sep := "", sepCount := -1
        for category in JEWELRY_CC_V2_ORDER {
            if (statuses[category] = "ok" && counts[category] != v && counts[category] > sepCount) {
                sep := category
                sepCount := counts[category]
            }
        }
        if (sep = "") {
            dupFail .= (dupFail = "" ? "" : "; ") . v . "=[" . catList . "] (no separator category available)"
            continue
        }

        groupOk := true
        detail := ""
        idx := cats.Length
        while (idx >= 1) {   ; reverse order
            c := cats[idx]
            idx--
            LogMessage("  [dup-verify] separator " . sep . " (was " . sepCount . ") then " . c)
            s2 := JewelryV3ReadCategory(store, sep)
            if (s2 <= 0 || s2 = v) {
                groupOk := false
                detail .= sep . "->" . (s2 > 0 ? s2 : "err") . " (separator unusable) "
                LogMessage("  [dup-verify] separator read " . (s2 > 0 ? s2 : "error") . " — cannot prove freshness")
                break
            }
            r := JewelryV3ReadCategory(store, c)
            detail .= sep . "=" . s2 . " then " . c . "=" . (r > 0 ? r : "err") . "; "
            LogMessage("  [dup-verify] " . c . " re-read = " . (r > 0 ? r : "error") . " right after " . sep . " = " . s2)
            if (r != v) {
                groupOk := false
                break
            }
        }
        if groupOk {
            dupConfirmed .= (dupConfirmed = "" ? "" : "; ") . v . "=[" . catList . "]"
            LogMessage("  [dup-verify] CONFIRMED genuine: " . v . "=[" . catList . "] (" . detail . ")")
        } else {
            dupFail .= (dupFail = "" ? "" : "; ") . v . "=[" . catList . "] re-verify: " . detail
            LogMessage("  [dup-verify] NOT confirmed: " . v . "=[" . catList . "] (" . detail . ")")
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
                  . ". Refusing to report a partial jewelry count as success."
                  . (dupFail != "" ? " Also unconfirmed duplicates: " . dupFail : ""))
    }

    if (dupFail != "") {
        return Fail(result, started
                  , "Duplicate counts across different categories (possible stale-grid contamination): "
                  . dupFail . ". Refusing to report a jewelry count that may be corrupted.")
    }

    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: all 8 category counts read (stable)"
             . (dupConfirmed != "" ? ", duplicates re-verified genuine: " . dupConfirmed : "")
             . ", " . result["duration_ms"] . "ms")
    return result
}
