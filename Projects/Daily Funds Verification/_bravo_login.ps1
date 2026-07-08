# _bravo_login.ps1 — drive Bravo from Store Selector through login via UIA (Session 1)
# Picks WAY (FREE1 home store), enters password, submits, verifies dashboard.
$out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_login.txt'
function Log($m) { ((Get-Date -Format 'HH:mm:ss') + ' ' + $m) | Add-Content $out }
"start" | Set-Content $out
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$AE   = [System.Windows.Automation.AutomationElement]
$root = $AE::RootElement

function FindBravoWin {
    $wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($w in $wins) { if ($w.Current.Name -like '*Bravo*' -or $w.Current.Name -like '*VALLEY*') { return $w } }
    return $null
}

$win = FindBravoWin
if (-not $win) { Log 'ERROR: no Bravo window'; exit 1 }
Log ('window: ' + $win.Current.Name)

# --- 1. If store selector present, select WAY and click Select ----------
$wayText = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, 'VALLEY PAWN - WAYNESBORO')))
if ($wayText) {
    Log 'store selector detected; locating WAY row'
    # walk up to the DataItem ancestor
    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $node = $wayText
    while ($node -and $node.Current.ControlType.ProgrammaticName -ne 'ControlType.DataItem') { $node = $walker.GetParent($node) }
    if (-not $node) { Log 'ERROR: WAY DataItem not found'; exit 1 }
    $sel = $node.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
    $sel.Select()
    Log 'WAY row selected'
    Start-Sleep -Milliseconds 800
    $btn = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.AndCondition(
            (New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, 'Select')),
            (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)))))
    if (-not $btn) { Log 'ERROR: Select button not found'; exit 1 }
    ($btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke()
    Log 'Select invoked'
    Start-Sleep -Seconds 4
} else { Log 'no store selector (maybe already at login)' }

# --- 2. Login form: set password, submit --------------------------------
$win = FindBravoWin
$pwBox = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition($AE::ClassNameProperty, 'PasswordBox')))
if (-not $pwBox) {
    # fallback: any Edit that is a password
    $edits = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)))
    foreach ($e in $edits) { if ($e.Current.IsPassword) { $pwBox = $e; break } }
}
if (-not $pwBox) {
    Log 'ERROR: password box not found; dumping window children'
    $kids = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    $i = 0
    foreach ($k in $kids) { Log ('  [' + $k.Current.ControlType.ProgrammaticName + "] '" + $k.Current.Name + "' class=" + $k.Current.ClassName); $i++; if ($i -ge 60) { break } }
    exit 1
}
Log 'password box found'
($pwBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).SetValue('Healthy2024!')
Log 'password set'
Start-Sleep -Milliseconds 500
$submit = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.AndCondition(
        (New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, 'Submit')),
        (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)))))
if (-not $submit) { Log 'ERROR: Submit button not found'; exit 1 }
($submit.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke()
Log 'Submit invoked'

# --- 3. Verify dashboard --------------------------------------------------
for ($t = 0; $t -lt 12; $t++) {
    Start-Sleep -Seconds 3
    $win = FindBravoWin
    if ($win -and $win.Current.Name -like '*VALLEY*') { Log ('SUCCESS: ' + $win.Current.Name); exit 0 }
}
$win = FindBravoWin
if ($win) { Log ('final window: ' + $win.Current.Name) } else { Log 'final window: none' }
"end" | Add-Content $out
