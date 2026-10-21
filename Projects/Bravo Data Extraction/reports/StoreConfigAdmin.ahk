; =============================================================================
; StoreConfigAdmin.ahk — System Configuration WRITE handlers (additive, 2026-10-20)
;
;   employee-status : set an employee's Status (CURRENT / TERMINATED / UNKNOWN)
;   store-hours     : set a store's "Store Hours" text
;
; WHY: offboarding and hours changes used to need a human (or a screen takeover)
; driving Bravo in Parallels. System Configuration is company-wide from ANY
; store, so these cells never call EnsureStore / never cycle stores — they act
; on whichever store Bravo is currently logged into.
;
; TRIGGER (drop as triggers/<id>.json; "stores" is a LABEL only, use one entry):
;   {"id":"empstat-20261020-1","requested_at":"...",
;    "reports":[{"name":"employee-status","stores":["ROA"],
;                "date":"store=ROA~name=JACOB COX~status=TERMINATED~mode=live"}]}
;   {"id":"hours-20261020-1","requested_at":"...",
;    "reports":[{"name":"store-hours","stores":["WAY"],
;                "date":"store=WAY~hours=Mon - Fri: 10am - 6pm | Sat: 10am - 5pm | Sun: Closed~mode=live"}]}
;
; The "date" string carries the parameters, '~'-delimited (the hours text itself
; contains '|', so '|' is NOT the delimiter here). mode defaults to PROBE:
;   mode=probe → navigate + read + dump UIA names, NO Edit, NO Save (safe default)
;   mode=live  → perform the edit, Save, Approve the exception, verify on screen
;   mode=dryedit (employee-status only) → Edit, pick the status, then CANCEL — proves the
;                dropdown works without saving anything
;
; SAFETY
;   * Blocklist: FREE1 / BACKUP / APPROVAL / SYSTEM accounts are never touched.
;   * Live employee-status records the BEFORE value, verifies the record is the
;     named person (first + last name fields), and verifies AFTER save.
;   * Live store-hours verifies the field reads the new text after save.
;   * A screenshot (<trigger>_<tag>.png in logs/) is saved before and after Save.
;   * Any failure returns status=error with a plain reason; nothing is retried
;     blindly. BackToDashboard() answers "cancel changes?" with Yes, so an
;     aborted edit is discarded, never half-saved.
;   * Pause switch: a file reports\StoreConfigAdmin.PAUSED disables both cells.
;
; Result map keys follow the pipeline contract (report/store/date/status/
; output_path/row_count/duration_ms/error). output_path = a small text file in
; output\ recording before/after values; row_count = 1 when a change was made.
; =============================================================================
#Requires AutoHotkey v2.0

global SCA_BLOCKLIST := ["FREE1", "BACKUP", "APPROVAL", "SYSTEM"]

; ----- parameter parsing ------------------------------------------------------
ScaParseParams(s) {
    p := Map("store", "", "name", "", "status", "", "hours", "", "mode", "probe")
    for tok in StrSplit(s, "~") {
        eq := InStr(tok, "=")
        if (eq < 2)
            continue
        k := StrLower(Trim(SubStr(tok, 1, eq - 1)))
        v := Trim(SubStr(tok, eq + 1))
        if p.Has(k)
            p[k] := v
    }
    p["mode"] := StrLower(p["mode"])
    return p
}

ScaIsBlocked(name) {
    u := StrUpper(name)
    for b in SCA_BLOCKLIST
        if InStr(u, b)
            return true
    return false
}

; ----- UIA helpers (local to this module) -------------------------------------

; Return the Text/TreeItem element named `label` whose top edge is the smallest
; value greater than `belowTop` (i.e. the first one visually below a reference).
ScaFindTextBelow(label, belowTop := -1) {
    root := GetBravoRoot()
    best := 0, bestTop := 999999
    for typeName in ["Text", "TreeItem"] {
        els := 0
        try els := root.FindElements({Type: typeName, Name: label})
        if !els
            continue
        for el in els {
            t := 0
            try t := el.BoundingRectangle.t
            try {
                if el.IsOffscreen
                    continue
            }
            if (t > belowTop && t < bestTop) {
                best := el, bestTop := t
            }
        }
        if best
            break
    }
    return best
}

; Walk up from an element to its owning TreeItem (max 6 hops). Returns 0 if none.
ScaOwningTreeItem(el) {
    cur := el
    Loop 6 {
        try {
            if (cur.ControlType = UIA.Type.TreeItem)
                return cur
        }
        nxt := 0
        try nxt := UIA.TreeWalkerTrue.GetParentElement(cur)
        if !nxt
            return 0
        cur := nxt
    }
    return 0
}

; Expand the tree node whose label Text is `label` (first one below belowTop).
; Returns the label element on success (so callers can anchor the next search).
ScaExpandNode(label, belowTop := -1) {
    el := ScaFindTextBelow(label, belowTop)
    if !el
        throw Error("tree node '" . label . "' not found")
    ti := ScaOwningTreeItem(el)
    expanded := false
    if ti {
        try {
            st := ti.ExpandCollapsePattern.ExpandCollapseState
            if (st = 3)
                throw Error("leaf node")
            if (st = 1) {
                expanded := true
                LogMessage("    [tree] '" . label . "' already expanded")
            } else {
                ti.ExpandCollapsePattern.Expand()
                Sleep(1200)
                try expanded := (ti.ExpandCollapsePattern.ExpandCollapseState = 1)
                LogMessage("    [tree] '" . label . "' Expand() -> " . (expanded ? "expanded" : "not expanded"))
            }
        } catch as e {
            LogMessage("    [tree] ExpandCollapsePattern unavailable for '" . label . "': " . e.Message)
        }
    }
    if !expanded {
        ; Fallback 1: select the label, press Right (WPF TreeView expands on Right)
        try {
            el.Click("left")
            Sleep(700)
            Send("{Right}")
            Sleep(1200)
            if ti
                try expanded := (ti.ExpandCollapsePattern.ExpandCollapseState = 1)
            LogMessage("    [tree] click+Right -> " . (expanded ? "expanded" : "unknown"))
        }
    }
    if (!expanded && ti) {
        ; Fallback 2: physical click on the expander arrow just left of the label
        try {
            r := el.BoundingRectangle
            x := r.l - 28, y := (r.t + r.b) // 2
            MouseClick("left", x, y)
            Sleep(1200)
            try expanded := (ti.ExpandCollapsePattern.ExpandCollapseState = 1)
            LogMessage("    [tree] arrow click @" . x . "," . y . " -> " . (expanded ? "expanded" : "unknown"))
        }
    }
    return el
}

; Click a tree label Text (selects the node and loads its right-hand form).
ScaSelectNode(label, belowTop := -1) {
    el := ScaFindTextBelow(label, belowTop)
    if !el
        throw Error("tree node '" . label . "' not found")
    el.Click("left")
    Sleep(1500)
    return el
}

; All Edit controls under the Bravo root, as an array of {el, value, aid}.
ScaEdits() {
    out := []
    root := GetBravoRoot()
    els := 0
    try els := root.FindElements({Type: "Edit"})
    if !els
        return out
    for el in els {
        v := "", a := ""
        try v := el.Value
        try a := el.AutomationId
        out.Push({el: el, value: v, aid: a})
    }
    return out
}

ScaHasEditWithValue(wantUpper) {
    for e in ScaEdits() {
        if (StrUpper(Trim(e.value)) = wantUpper)
            return true
    }
    return false
}

; Find the Status combo/edit: the control whose current value is one of the
; three known statuses. Returns {el, value, type} or 0.
; NOTE (2026-10-20 dryedit run): Bravo's status dropdown is exposed to UIA as
; Type=Edit with Name "BravoComboBox" (not Type=ComboBox), before AND after Edit.
; So `type` here is "combo" when the control looks like a dropdown, else "edit".
ScaFindStatusControl() {
    root := GetBravoRoot()
    for typeName in ["ComboBox", "Edit"] {
        els := 0
        try els := root.FindElements({Type: typeName})
        if !els
            continue
        for el in els {
            v := ""
            try v := StrUpper(Trim(el.Value))
            if (v = "CURRENT" || v = "TERMINATED" || v = "UNKNOWN") {
                nm := ""
                try nm := el.Name
                isCombo := (typeName = "ComboBox") || InStr(nm, "ComboBox")
                if !isCombo
                    try isCombo := el.IsExpandCollapsePatternAvailable
                return {el: el, value: v, type: (isCombo ? "combo" : "edit")}
            }
        }
    }
    return 0
}


; Pick an item in Bravo's (DevExpress) status dropdown by PHYSICAL click.
; SelectionItemPattern.Select() highlights the row but does not commit the value
; (seen 2026-10-20 dryedit: TERMINATED highlighted, combo still read CURRENT).
; Mirrors FwbPickComboItem: open the combo, find the ListItem whose text == want,
; click its centre, then verify the combo value.
ScaPickStatus(comboEl, want) {
    CoordMode("Mouse", "Screen")
    opened := false
    try {
        comboEl.ExpandCollapsePattern.Expand()
        opened := true
    }
    if !opened
        try comboEl.Click("left")
    Sleep(1000)
    Loop 3 {
        try {
            for li in GetBravoRoot().FindElements({Type: "ListItem"}) {
                lbl := ""
                try lbl := StrUpper(Trim(li.Name))
                if (lbl = "") {
                    try {
                        for t in li.FindElements({Type: "Text"}) {
                            tn := ""
                            try tn := t.Name
                            if (tn != "")
                                lbl .= (lbl = "" ? "" : " ") . StrUpper(Trim(tn))
                        }
                    }
                }
                if (lbl != want)
                    continue
                er := li.BoundingRectangle
                if (er.b > er.t && er.t > 0) {
                    x := (er.l + er.r) // 2, y := (er.t + er.b) // 2
                    MouseMove(x, y, 5)
                    Sleep(150)
                    Click(x, y)
                    Sleep(1000)
                    LogMessage("    [status] clicked '" . want . "' @" . x . "," . y)
                    break
                }
            }
        }
        v := ""
        try v := StrUpper(Trim(comboEl.Value))
        if (v = want)
            return true
        ; not committed yet — try keyboard commit on the highlighted row, then re-open
        Send("{Enter}")
        Sleep(600)
        try v := StrUpper(Trim(comboEl.Value))
        if (v = want)
            return true
        try comboEl.Click("left")
        Sleep(900)
    }
    Send("{Escape}")
    return false
}

; Find the Store Hours edit box: the Edit nearest BELOW the "Store Hours" label.
ScaFindHoursEdit() {
    root := GetBravoRoot()
    label := 0
    try label := root.FindElement({Type: "Text", Name: "Store Hours"})
    if !label
        throw Error("'Store Hours' label not found")
    lr := label.BoundingRectangle
    best := 0, bestTop := 999999
    for e in ScaEdits() {
        r := 0
        try r := e.el.BoundingRectangle
        if !r
            continue
        ; below the label, horizontally overlapping it
        if (r.t >= lr.b - 2 && r.t < bestTop && r.r > lr.l && r.l < lr.r + 400) {
            best := e.el, bestTop := r.t
        }
    }
    if !best
        throw Error("Store Hours edit box not found under its label")
    return best
}

; Click a button by name, searching the Bravo window first, then the desktop
; (DevExpress exception dialogs can be top-level windows).
ScaClickButtonAnywhere(name, timeoutMs := 8000) {
    start := A_TickCount
    Loop {
        try {
            root := GetBravoRoot()
            b := root.FindElement({Type: "Button", Name: name})
            if b {
                b.Click("left")
                return "bravo"
            }
        }
        try {
            d := UIA.GetRootElement()
            b := d.FindElement({Type: "Button", Name: name})
            if b {
                b.Click("left")
                return "desktop"
            }
        }
        if (A_TickCount - start > timeoutMs)
            return ""
        Sleep(500)
    }
}

; Open System Configuration from the Dashboard and wait for the config tree.
ScaOpenSystemConfig() {
    if !BackToDashboard()
        throw Error("BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()
    LogMessage("  open System Configuration")
    ClickByName("System Configuration", 8000)
    Sleep(2000)
    DismissPopups()
    if (WaitForAnyByName(["VALPAW Company", "Stores"], 15000) = "")
        throw Error("System Configuration tree did not appear")
    ; Make sure the Stores branch is open (it normally is).
    try ScaExpandNode("Stores")
    Sleep(600)
}

; Leave System Configuration cleanly.
ScaCloseSystemConfig() {
    try ClickByName("Done", 5000)
    Sleep(1500)
    DismissPopups()          ; "Till must be opened to complete a transaction" → Ok
    Sleep(500)
    try BackToDashboard()
}

ScaWriteNote(outputDir, slug, lines) {
    path := outputDir . "\" . FormatTime(, "yyyyMMdd-HHmmss") . "_" . slug . ".txt"
    try FileAppend(lines, path, "UTF-8")
    return path
}

; Handle the "Approval required to edit store information" exception dialog.
; Returns true if Approve was clicked (or no dialog appeared within the wait).
ScaApproveIfAsked() {
    where := ScaClickButtonAnywhere("Approve", 6000)
    if (where != "") {
        LogMessage("    [approve] clicked Approve (" . where . ")")
        Sleep(1500)
        return true
    }
    LogMessage("    [approve] no Approve dialog appeared")
    return true
}

; =============================================================================
; employee-status
; =============================================================================
PullEmployeeStatus(store, params, outputDir) {
    started := A_TickCount
    result := Map("report", "employee-status", "store", store, "date", params,
                  "status", "error", "output_path", "", "row_count", 0,
                  "duration_ms", 0, "error", "")
    if FileExist(A_ScriptDir . "\reports\StoreConfigAdmin.PAUSED")
        return Fail(result, started, "paused (reports\StoreConfigAdmin.PAUSED exists)")

    p := ScaParseParams(params)
    targetStore := (p["store"] != "") ? StrUpper(p["store"]) : StrUpper(store)
    name := StrUpper(Trim(p["name"]))
    want := StrUpper(Trim(p["status"]))
    live := (p["mode"] = "live")
    LogMessage("[" . targetStore . "] employee-status name='" . name . "' want='" . want . "' mode=" . p["mode"])

    if (name = "")
        return Fail(result, started, "name= is required")
    if ScaIsBlocked(name)
        return Fail(result, started, "refusing to touch protected account '" . name . "'")
    if (live && !(want = "TERMINATED" || want = "CURRENT" || want = "UNKNOWN"))
        return Fail(result, started, "status must be TERMINATED, CURRENT or UNKNOWN (got '" . want . "')")

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()
    LogMessage("  running on store currently logged in: " . GetCurrentStoreCode())

    before := "", after := "", stillListed := "", personOk := false
    try {
        ScaOpenSystemConfig()

        LogMessage("  expand store " . targetStore)
        storeEl := ScaExpandNode(targetStore)
        storeTop := storeEl.BoundingRectangle.t

        LogMessage("  expand Employees under " . targetStore)
        empEl := ScaExpandNode("Employees", storeTop)
        empTop := empEl.BoundingRectangle.t

        ; Is the person listed at all?
        personEl := ScaFindTextBelow(name, empTop)
        if !personEl {
            LogVisibleNames(60)
            throw Error("employee '" . name . "' not listed under " . targetStore . " Employees (already inactive, or name differs — tree names are LAST/FIRST as shown)")
        }
        LogMessage("  select employee " . name)
        personEl.Click("left")
        Sleep(1800)

        ; Verify the loaded record is this person (first + last name edits).
        parts := StrSplit(name, " ")
        lastName := parts[parts.Length], firstName := parts[1]
        personOk := ScaHasEditWithValue(lastName) && ScaHasEditWithValue(firstName)
        LogMessage("  record check: first='" . firstName . "' last='" . lastName . "' -> " . (personOk ? "MATCH" : "NO MATCH"))
        if !personOk {
            LogVisibleNames(60)
            throw Error("loaded record does not show first/last name " . firstName . " " . lastName)
        }

        sc := ScaFindStatusControl()
        before := sc ? sc.value : "(not found)"
        LogMessage("  status BEFORE = " . before)
        ScreenshotToFile("empstat-" . StrReplace(name, " ", "_") . "-before")

        if (!live && p["mode"] != "dryedit") {
            LogMessage("  PROBE mode — dumping names, no edit")
            LogVisibleNames(80)
            ScaCloseSystemConfig()
            result["output_path"] := ScaWriteNote(outputDir, "employee-status-probe",
                "store=" . targetStore . "`nname=" . name . "`nstatus_before=" . before . "`nmode=probe`n")
            result["status"] := "success"
            result["duration_ms"] := A_TickCount - started
            return result
        }

        if (p["mode"] = "dryedit") {
            ; Exercise Edit → Status pick → Cancel (discard). Never saves.
            LogMessage("  DRYEDIT mode — Edit, pick '" . want . "', then Cancel")
            ClickByName("Edit", 6000)
            Sleep(1500)
            scd := ScaFindStatusControl()
            if (!scd || scd.type != "combo") {
                LogVisibleNames(80)
                throw Error("Status dropdown not found after Edit (dryedit) — found: " . (scd ? scd.type . "/" . scd.value : "nothing"))
            }
            picked := ScaPickStatus(scd.el, want)
            Sleep(800)
            scd2 := ScaFindStatusControl()
            reads := scd2 ? scd2.value : "?"
            LogMessage("  dryedit: pick=" . (picked ? "ok" : "FAILED") . " combo now reads '" . reads . "'")
            ScreenshotToFile("empstat-dryedit")
            try ClickByName("Cancel", 5000)
            Sleep(1200)
            try ClickByName("Yes", 4000)      ; "Discard changes?" confirm
            Sleep(1200)
            scd3 := ScaFindStatusControl()
            LogMessage("  dryedit: after Cancel the record reads '" . (scd3 ? scd3.value : "?") . "'")
            if (scd3 && scd3.value != before)
                throw Error("dryedit: record did not revert to '" . before . "'")
            ScaCloseSystemConfig()
            result["output_path"] := ScaWriteNote(outputDir, "employee-status-dryedit",
                "store=" . targetStore . "`nname=" . name . "`nstatus_before=" . before . "`ncombo_read_after_pick=" . reads . "`nsaved=no`n")
            result["status"] := (picked && reads = want) ? "success" : "error"
            if (result["status"] = "error")
                result["error"] := "dryedit: combo pick did not read '" . want . "' (read '" . reads . "')"
            result["duration_ms"] := A_TickCount - started
            return result
        }

        if (before = want) {
            LogMessage("  already " . want . " — nothing to change")
            ScaCloseSystemConfig()
            result["output_path"] := ScaWriteNote(outputDir, "employee-status",
                "store=" . targetStore . "`nname=" . name . "`nstatus_before=" . before . "`nstatus_after=" . before . "`nchanged=no`n")
            result["status"] := "success"
            result["duration_ms"] := A_TickCount - started
            return result
        }

        LogMessage("  click Edit")
        ClickByName("Edit", 6000)
        Sleep(1500)

        sc := ScaFindStatusControl()
        if (!sc || sc.type != "combo") {
            LogVisibleNames(80)
            throw Error("Status dropdown not found after Edit — found: " . (sc ? sc.type . "/" . sc.value : "nothing"))
        }
        LogMessage("  pick '" . want . "' in Status combo")
        if !ScaPickStatus(sc.el, want)
            throw Error("could not select '" . want . "' in Status combo")
        Sleep(800)
        sc2 := ScaFindStatusControl()
        if (!sc2 || sc2.value != want)
            throw Error("Status combo did not take '" . want . "' (reads '" . (sc2 ? sc2.value : "?") . "')")

        LogMessage("  click Save")
        ClickByName("Save", 6000)
        Sleep(1500)
        ScaApproveIfAsked()
        Sleep(1500)
        DismissPopups()

        ; Verify: record reads new status, and (for TERMINATED) person left the tree.
        sc3 := ScaFindStatusControl()
        after := sc3 ? sc3.value : "(not found)"
        LogMessage("  status AFTER = " . after)
        if (after != want)
            throw Error("after Save the record reads '" . after . "', expected '" . want . "'")
        if (want = "TERMINATED") {
            still := ScaFindTextBelow(name, empTop)
            stillListed := still ? "yes" : "no"
            LogMessage("  still listed in active Employees tree: " . stillListed)
            if still
                throw Error("record reads TERMINATED but '" . name . "' is still in the active Employees tree")
        }
        ScreenshotToFile("empstat-" . StrReplace(name, " ", "_") . "-after")

        ScaCloseSystemConfig()
    } catch as e {
        try ScreenshotToFile("empstat-failed")
        try ScaCloseSystemConfig()
        return Fail(result, started, "employee-status failed: " . e.Message)
    }

    result["output_path"] := ScaWriteNote(outputDir, "employee-status",
        "store=" . targetStore . "`nname=" . name . "`nstatus_before=" . before . "`nstatus_after=" . after . "`nchanged=yes`nverified_on_screen=" . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`n")
    result["row_count"]   := 1
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . name . " " . before . " -> " . after . " (" . result["duration_ms"] . "ms)")
    return result
}

; =============================================================================
; store-hours
; =============================================================================
PullStoreHours(store, params, outputDir) {
    started := A_TickCount
    result := Map("report", "store-hours", "store", store, "date", params,
                  "status", "error", "output_path", "", "row_count", 0,
                  "duration_ms", 0, "error", "")
    if FileExist(A_ScriptDir . "\reports\StoreConfigAdmin.PAUSED")
        return Fail(result, started, "paused (reports\StoreConfigAdmin.PAUSED exists)")

    p := ScaParseParams(params)
    targetStore := (p["store"] != "") ? StrUpper(p["store"]) : StrUpper(store)
    hours := Trim(p["hours"])
    live := (p["mode"] = "live")
    LogMessage("[" . targetStore . "] store-hours mode=" . p["mode"] . " hours='" . hours . "'")
    if (live && hours = "")
        return Fail(result, started, "hours= is required in live mode")
    if (StrLen(hours) > 100)
        return Fail(result, started, "hours text exceeds Bravo's 100-character limit")

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()

    before := "", after := ""
    try {
        ScaOpenSystemConfig()
        LogMessage("  select store " . targetStore)
        ScaSelectNode(targetStore)
        Sleep(800)

        ; Confirm the right store form loaded (Short Name edit = store code).
        if !ScaHasEditWithValue(targetStore)
            throw Error("store form for " . targetStore . " did not load (no edit reads '" . targetStore . "')")

        hb := ScaFindHoursEdit()
        try before := hb.Value
        LogMessage("  hours BEFORE = '" . before . "'")

        if !live {
            LogMessage("  PROBE mode — dumping names, no edit")
            LogVisibleNames(80)
            ScaCloseSystemConfig()
            result["output_path"] := ScaWriteNote(outputDir, "store-hours-probe",
                "store=" . targetStore . "`nhours_before=" . before . "`nmode=probe`n")
            result["status"] := "success"
            result["duration_ms"] := A_TickCount - started
            return result
        }
        if (before = hours) {
            LogMessage("  already set — nothing to change")
            ScaCloseSystemConfig()
            result["output_path"] := ScaWriteNote(outputDir, "store-hours",
                "store=" . targetStore . "`nhours_before=" . before . "`nhours_after=" . before . "`nchanged=no`n")
            result["status"] := "success"
            result["duration_ms"] := A_TickCount - started
            return result
        }

        LogMessage("  click Edit")
        ClickByName("Edit", 6000)
        Sleep(1500)
        hb := ScaFindHoursEdit()
        set := false
        try {
            hb.Value := hours
            Sleep(400)
            set := (hb.Value = hours)
        }
        if !set {
            ; Fallback: focus, select-all, paste from clipboard (never Send text —
            ; typing fires Windows Sticky Keys on repeated Shift).
            A_Clipboard := hours
            Sleep(200)
            hb.Click("left")
            Sleep(300)
            Send("^a")
            Sleep(150)
            Send("^v")
            Sleep(600)
            try set := (hb.Value = hours)
        }
        if !set
            throw Error("could not set Store Hours text (reads '" . hb.Value . "')")
        ScreenshotToFile("hours-" . targetStore . "-before-save")

        LogMessage("  click Save")
        ClickByName("Save", 6000)
        Sleep(1500)
        ScaApproveIfAsked()
        Sleep(1500)
        DismissPopups()

        hb2 := ScaFindHoursEdit()
        try after := hb2.Value
        LogMessage("  hours AFTER = '" . after . "'")
        if (after != hours)
            throw Error("after Save the field reads '" . after . "'")
        ScreenshotToFile("hours-" . targetStore . "-after")

        ScaCloseSystemConfig()
    } catch as e {
        try ScreenshotToFile("hours-failed")
        try ScaCloseSystemConfig()
        return Fail(result, started, "store-hours failed: " . e.Message)
    }

    result["output_path"] := ScaWriteNote(outputDir, "store-hours",
        "store=" . targetStore . "`nhours_before=" . before . "`nhours_after=" . after . "`nchanged=yes`nverified_on_screen=" . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`n")
    result["row_count"]   := 1
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . targetStore . " hours updated (" . result["duration_ms"] . "ms)")
    return result
}
