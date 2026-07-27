; ============================================================================
; reports/PostToAccountingPost.ahk
;
; Clicks the per-day Post buttons on the Bravo Post to Accounting screen for
; every UNPOSTED day whose date is on or before the trigger end date.
; NEW FILE (additive). Login/nav/result plumbing cloned from
; reports/PostToAccountingGL.ahk (same screen, same entry button).
;
; AUTHORIZED STATE CHANGE (Joshua, 2026-07-06): unlike PostToAccountingGL
; (which must never post), this handler is EXPLICITLY authorized to click
; Post. Joshua: its not subjective, its bravo reporting up to the GL, there
; is no risk or danger here. These need to be posted.
;
; HARD SAFETY RULES:
;   - NEVER post a day AFTER the trigger end date. PtaPostScan filters
;     serial > endSerial and PtaPostClickPostFor re-checks before clicking.
;   - Post OLDEST FIRST. Bravo refuses out-of-order posting with the popup
;     text: There are dates that need to be posted first.
;   - If a day errors, capture the popup message, skip it, continue.
;
; Screen map (output/uia-pta-CUL-20260706-132118.txt, Bravo 2026.6.0.79):
;   datagrid AutoId=itemsGrid  >  pane AutoId=dataPresenter  >
;   [dataitem] rows (newest-first), each row:
;     cell Column Posted  -> [button] Name=Post   (only on UNPOSTED days)
;     cell Column Date    -> AutoId=CalendarDay, Name ends with: M/D/YYYY
;   Already-posted rows have no Post button.
;
; Trigger schema:
;   name:   post-to-accounting-post
;   stores: [CUL, HAR, LEX, ROA, WAY]
;   date:   YYYY-MM-DD..YYYY-MM-DD   (only the END date is the guard)
;           or discover[-label] -> dump UIA tree + row scan, click NOTHING.
;
; Result extras: days_posted / days_skipped / post_errors, plus a summary
; txt in output as END_STORE_post-to-accounting-post.txt
; ============================================================================
#Requires AutoHotkey v2.0

; ---------------------------------------------------------------------------
; Date helpers: grid dates are M/D/YYYY, trigger dates are YYYY-MM-DD.
; Serial form yyyymmdd (Integer) for comparisons.
; ---------------------------------------------------------------------------
PtaPostDateSerial(mdy) {
    parts := StrSplit(Trim(mdy), '/')
    if (parts.Length != 3)
        return 0
    ser := 0
    try ser := Integer(parts[3]) * 10000 + Integer(parts[1]) * 100 + Integer(parts[2])
    return ser
}

PtaPostIsoSerial(iso) {
    parts := StrSplit(Trim(iso), '-')
    if (parts.Length != 3)
        return 0
    ser := 0
    try ser := Integer(parts[1]) * 10000 + Integer(parts[2]) * 100 + Integer(parts[3])
    return ser
}

PtaPostJoin(arr, sep) {
    out := ''
    for v in arr
        out .= (out = '' ? '' : sep) . v
    return out
}

; ---------------------------------------------------------------------------
; Scan itemsGrid for UNPOSTED rows (rows that still show a Post button).
; Returns an Array of Maps: serial (yyyymmdd Integer), text (M/D/YYYY).
; ---------------------------------------------------------------------------
PtaPostScanRows() {
    rows := []
    grid := 0
    try grid := GetBravoRoot().FindElement({AutomationId: 'itemsGrid'})
    if !grid
        return rows
    items := 0
    try items := grid.FindElements({Type: 'DataItem'})
    if !items
        return rows
    for it in items {
        dateCell := 0
        try dateCell := it.FindElement({AutomationId: 'CalendarDay'})
        if !dateCell
            continue
        nm := ''
        try nm := dateCell.Name
        p := InStr(nm, ':', , -1)
        if !p
            continue
        dtxt := Trim(SubStr(nm, p + 1))
        ser := PtaPostDateSerial(dtxt)
        if !ser
            continue
        hasPost := false
        try {
            pb := it.FindElement({Type: 'Button', Name: 'Post'})
            if pb
                hasPost := true
        }
        if !hasPost
            continue
        rows.Push(Map('serial', ser, 'text', dtxt))
    }
    return rows
}

; ---------------------------------------------------------------------------
; Real-click the Post button for one specific day. Re-resolves the row fresh
; every call (the grid re-renders after each post, stale refs are useless).
; Re-verifies the end-date guard immediately before clicking.
; ---------------------------------------------------------------------------
PtaPostClickPostFor(serial, endSerial) {
    if (serial > endSerial) {
        LogMessage('    [post] GUARD: refusing to post ' . serial . ' > end ' . endSerial)
        return false
    }
    ; The grid virtualizes rows: UIA exposes every row with a rect that can
    ; extend BELOW the visible viewport (first build clicked y=1985 which is
    ; the Windows taskbar - ScrollIntoView on this DevExpress grid is a
    ; no-op). Fix: wheel-scroll over the grid until the target Post button
    ; rect sits INSIDE the grid viewport band, then real-click it.
    CoordMode('Mouse', 'Screen')
    ActivateBravo()
    grid := 0
    try grid := GetBravoRoot().FindElement({AutomationId: 'itemsGrid'})
    if !grid
        return false
    gr := 0
    try gr := grid.BoundingRectangle
    if !(gr && gr.b > gr.t)
        return false
    bandTop := gr.t + 90
    bandBot := gr.b - 70
    gcx := (gr.l + gr.r) // 2
    gcy := (gr.t + gr.b) // 2
    Loop 30 {
        pb := 0
        items := 0
        try items := grid.FindElements({Type: 'DataItem'})
        if !items {
            try grid := GetBravoRoot().FindElement({AutomationId: 'itemsGrid'})
            Sleep(500)
            continue
        }
        for it in items {
            dateCell := 0
            try dateCell := it.FindElement({AutomationId: 'CalendarDay'})
            if !dateCell
                continue
            nm := ''
            try nm := dateCell.Name
            p := InStr(nm, ':', , -1)
            if !p
                continue
            if (PtaPostDateSerial(Trim(SubStr(nm, p + 1))) != serial)
                continue
            try pb := it.FindElement({Type: 'Button', Name: 'Post'})
            break
        }
        if !pb {
            LogMessage('    [post] no Post button yet for ' . serial . ' (pass ' . A_Index . ')')
            if (A_Index >= 5)
                return false
            Sleep(1500)
            continue
        }
        r := 0
        try r := pb.BoundingRectangle
        if (r && r.r > r.l && r.t >= bandTop && r.b <= bandBot) {
            cx := (r.l + r.r) // 2
            cy := (r.t + r.b) // 2
            MouseMove(cx, cy, 10)
            Sleep(150)
            Click(cx, cy)
            LogMessage('    [post] real-clicked Post for ' . serial . ' at ' . cx . ',' . cy . ' (pass ' . A_Index . ')')
            return true
        }
        ; Not in view: wheel the grid. Older dates live at the BOTTOM.
        dir := 'down'
        if (r && r.r > r.l && r.b < bandTop + 1)
            dir := 'up'
        MouseMove(gcx, gcy, 10)
        Sleep(120)
        if (dir = 'down')
            Send('{WheelDown 3}')
        else
            Send('{WheelUp 3}')
        Sleep(600)
        if (Mod(A_Index, 8) = 0)
            LogMessage('    [post] scrolling ' . dir . ' for ' . serial . ' (pass ' . A_Index . ', rect=' . (r ? r.t . '-' . r.b : 'none') . ' band=' . bandTop . '-' . bandBot . ')')
    }
    LogMessage('    [post] could not bring ' . serial . ' into view after 30 scroll passes')
    return false
}

; ---------------------------------------------------------------------------
; Handle whatever pops up after a Post click. Confirms Yes-style dialogs,
; dismisses btnOk message boxes, captures the message text (txtMessage).
; Returns: empty string (nothing), confirmed, or message (msgOut has text).
; ---------------------------------------------------------------------------
PtaPostHandlePopup(&msgOut) {
    msgOut := ''
    acted := ''
    ; Native Save As dialog: Bravo pops this right after a successful post
    ; (offers to export the just-posted day in the ribbon Export Format,
    ; default Netsuite). We do NOT want that file - the GL CSV comes from
    ; post-to-accounting-gl. Escape cancels it; the day stays posted.
    ; (Observed 2026-07-06 17:02: 6/11 posted, Save As opened, and the modal
    ; dialog swallowed every later Post click in the run.)
    if WinExist('Save As') {
        try {
            WinActivate('Save As')
            Sleep(300)
            Send('{Escape}')
            Sleep(800)
            LogMessage('    [popup] dismissed Save As export dialog via Escape')
            acted := 'saveas'
        }
    }
    root := 0
    try root := GetBravoRoot()
    if !root
        return acted
    yes := 0
    try yes := root.FindElement({AutomationId: 'btnYes'})
    if !yes
        try yes := root.FindElement({Type: 'Button', Name: 'Yes'})
    if yes {
        try {
            yes.Click('left')
            Sleep(700)
            LogMessage('    [popup] confirmed via Yes')
            if (acted = '')
                acted := 'confirmed'
        }
    }
    okBtn := 0
    try okBtn := root.FindElement({AutomationId: 'btnOk'})
    if okBtn {
        m := ''
        try {
            t := root.FindElement({AutomationId: 'txtMessage'})
            if t {
                try m := t.Name
                if (m = '')
                    try m := t.Value
            }
        }
        try {
            okBtn.Click('left')
            Sleep(700)
            msgOut := m
            LogMessage('    [popup] btnOk dismissed; message=' . m)
            if (acted = '')
                acted := 'message'
        }
    }
    return acted
}

; ---------------------------------------------------------------------------
; Main handler.
; ---------------------------------------------------------------------------
PullPostToAccountingPost(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        'report',       'post-to-accounting-post',
        'store',        store,
        'date',         dateOrRange,
        'status',       'error',
        'output_path',  '',
        'row_count',    0,
        'duration_ms',  0,
        'error',        '',
        'days_posted',  '',
        'days_skipped', '',
        'post_errors',  ''
    )

    isDiscover := InStr(dateOrRange, 'discover')

    endDateIso := ''
    if !isDiscover {
        if InStr(dateOrRange, '..') {
            parts := StrSplit(dateOrRange, '..')
            if (parts.Length != 2)
                return Fail(result, started, 'Malformed date range: ' . dateOrRange . ' (expected YYYY-MM-DD..YYYY-MM-DD)')
            endDateIso := Trim(parts[2])
        } else {
            endDateIso := Trim(dateOrRange)
        }
    }
    endSerial := isDiscover ? 0 : PtaPostIsoSerial(endDateIso)
    if (!isDiscover && !endSerial)
        return Fail(result, started, 'Could not parse end date from: ' . dateOrRange)

    outputPath := isDiscover
        ? outputDir . '\uia-ptapost-' . store . '-' . FormatTime(, 'yyyyMMdd-HHmmss') . '.txt'
        : outputDir . '\' . endDateIso . '_' . store . '_post-to-accounting-post.txt'
    LogMessage('[' . store . '] PostToAccountingPost end=' . endDateIso . ' output -> ' . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, 'Bravo window not found/ready within 30s')
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has('bravo.password') ? CONFIG['bravo.password'] : ''
    if !EnsureStore(store, password)
        return Fail(result, started, 'EnsureStore failed for ' . store)
    LogMessage('  store confirmed: ' . store)

    if !isDiscover
        ResetOutputFile(outputPath)

    if !BackToDashboard()
        return Fail(result, started, 'BackToDashboard could not return Bravo to Dashboard')
    Sleep(500)
    DismissPopups()

    posted := []
    errs := []
    skipped := Map()

    try {
        LogMessage('  step 1: click Dashboard Post to Accounting button')
        ClickByName('Post to Accounting', 8000)
        Sleep(3500)
        DismissPopups()

        rows := PtaPostScanRows()
        LogMessage('  scan: ' . rows.Length . ' unposted rows visible')
        for rw in rows
            LogMessage('    unposted: ' . rw['text'] . ((!isDiscover && rw['serial'] > endSerial) ? '  (AFTER end date - will NOT post)' : ''))

        if isDiscover {
            PtaGlDump(outputPath, 'ptapost-screen')
            section := 'PTAPOST scan: ' . rows.Length . ' unposted rows`r`n'
            for rw in rows
                section .= '  ' . rw['text'] . '  serial=' . rw['serial'] . '`r`n'
            FileAppend(section, outputPath, 'UTF-8')
            PtaGlExitToDashboard()
            result['output_path'] := outputPath
            result['row_count']   := rows.Length
            result['status']      := 'success'
            result['duration_ms'] := A_TickCount - started
            LogMessage('  DISCOVER SUCCESS: ' . result['duration_ms'] . 'ms')
            return result
        }

        ; Post OLDEST FIRST until nothing on or before endSerial remains.
        Loop 60 {
            m0 := ''
            PtaPostHandlePopup(&m0)
            rows := PtaPostScanRows()
            best := 0
            bestTxt := ''
            for rw in rows {
                if (rw['serial'] > endSerial || skipped.Has(rw['serial']))
                    continue
                if (!best || rw['serial'] < best) {
                    best := rw['serial']
                    bestTxt := rw['text']
                }
            }
            if !best {
                ; Grid refreshes right after a post can return a PARTIAL
                ; row set (observed 2026-07-06 17:42: 6/27-6/30 invisible
                ; for ~5s after posting 6/26). Re-verify before quitting.
                Sleep(4000)
                rows2 := PtaPostScanRows()
                best2 := 0
                for rw in rows2 {
                    if (rw['serial'] > endSerial || skipped.Has(rw['serial']))
                        continue
                    if (!best2 || rw['serial'] < best2)
                        best2 := rw['serial']
                }
                if best2 {
                    LogMessage('  rescan found ' . best2 . ' after transient empty scan - continuing')
                    continue
                }
                LogMessage('  no postable days on/before ' . endDateIso . ' remain (iteration ' . A_Index . ')')
                break
            }
            LogMessage('  posting day ' . bestTxt . ' (' . posted.Length . ' done so far)')
            if !PtaPostClickPostFor(best, endSerial) {
                errs.Push(bestTxt . ': could not click Post button')
                skipped[best] := 1
                continue
            }
            Sleep(1500)
            firstMsg := ''
            PtaPostHandlePopup(&firstMsg)
            okDone := false
            deadline := A_TickCount + 90000
            while (A_TickCount < deadline) {
                Sleep(2500)
                m2 := ''
                PtaPostHandlePopup(&m2)
                if (m2 != '' && firstMsg = '')
                    firstMsg := m2
                nowRows := PtaPostScanRows()
                if (nowRows.Length = 0)
                    continue
                still := false
                for rw in nowRows
                    if (rw['serial'] = best)
                        still := true
                if !still {
                    okDone := true
                    break
                }
            }
            if okDone {
                posted.Push(bestTxt)
                LogMessage('  [post] ' . bestTxt . ' POSTED' . (firstMsg != '' ? ' (popup: ' . firstMsg . ')' : ''))
            } else {
                emsg := bestTxt . ': still unposted after 90s' . (firstMsg != '' ? ' - popup: ' . firstMsg : '')
                errs.Push(emsg)
                skipped[best] := 1
                LogMessage('  [post] FAILED ' . emsg)
            }
            Sleep(800)
        }

        LogMessage('  done posting: exit to Dashboard')
        PtaGlExitToDashboard()
    } catch as e {
        try {
            LogMessage('    [recovery] best-effort exit to Dashboard')
            PtaGlExitToDashboard()
        }
        result['days_posted'] := PtaPostJoin(posted, ', ')
        result['post_errors'] := PtaPostJoin(errs, ' | ')
        result['row_count']   := posted.Length
        return Fail(result, started, 'Post sequence failed: ' . e.Message)
    }

    skippedTxt := ''
    for ser, unused in skipped
        skippedTxt .= (skippedTxt = '' ? '' : ', ') . ser
    summary := 'post-to-accounting-post ' . store . ' end=' . endDateIso . '`r`n'
    summary .= 'posted (' . posted.Length . '): ' . PtaPostJoin(posted, ', ') . '`r`n'
    summary .= 'skipped-serials: ' . skippedTxt . '`r`n'
    summary .= 'errors (' . errs.Length . '): ' . PtaPostJoin(errs, ' | ') . '`r`n'
    try FileAppend(summary, outputPath, 'UTF-8')

    result['days_posted']  := PtaPostJoin(posted, ', ')
    result['days_skipped'] := skippedTxt
    result['post_errors']  := PtaPostJoin(errs, ' | ')
    result['row_count']    := posted.Length
    result['output_path']  := outputPath
    result['duration_ms']  := A_TickCount - started
    if (errs.Length = 0) {
        result['status'] := 'success'
        LogMessage('  SUCCESS: posted ' . posted.Length . ' day(s), ' . result['duration_ms'] . 'ms')
    } else {
        result['status'] := 'error'
        result['error']  := errs.Length . ' day(s) failed: ' . PtaPostJoin(errs, ' | ')
        LogMessage('  PARTIAL: posted ' . posted.Length . ', failed ' . errs.Length)
    }
    return result
}
