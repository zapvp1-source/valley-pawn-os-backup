# _bravo_session.ps1 — handle SessionChooserView: list named controls, resume FREE1 session or reach login form
$out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_session.txt'
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

# Dump every named Button / Text / Hyperlink / DataItem (skip news noise)
$kids = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($k in $kids) {
    $n = $k.Current.Name
    $ct = $k.Current.ControlType.ProgrammaticName
    if ($n -and $n -notlike '*Bravo_News*' -and ($ct -match 'Button|Text|Hyperlink|DataItem|Edit|Custom') -and $n.Trim() -ne '') {
        if ($n.Length -gt 80) { $n = $n.Substring(0,80) }
        Log ('  [' + $ct + "] '" + $n + "' class=" + $k.Current.ClassName)
    }
}

# Try to act: prefer a FREE1 session row + Resume Session button
$free1 = $null
foreach ($k in $kids) {
    if ($k.Current.Name -like '*FREE1*' -or $k.Current.Name -like '*FREEDOM*') { $free1 = $k; break }
}
if ($free1) {
    Log ('found session row: ' + $free1.Current.Name + ' [' + $free1.Current.ControlType.ProgrammaticName + ']')
    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $node = $free1
    while ($node -and $node.Current.ControlType.ProgrammaticName -notmatch 'DataItem|ListItem') { $node = $walker.GetParent($node) }
    if ($node) {
        try { ($node.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)).Select(); Log 'session row selected' } catch { Log ('select failed: ' + $_.Exception.Message) }
        Start-Sleep -Milliseconds 800
    }
}
foreach ($label in @('Resume Session','Resume')) {
    $btn = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.AndCondition(
            (New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, $label)),
            (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)))))
    if ($btn) {
        try { ($btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); Log ($label + ' invoked') ; break } catch { Log ($label + ' invoke failed: ' + $_.Exception.Message) }
    }
}
Start-Sleep -Seconds 4

# If a password box is now present, log in
$win = FindBravoWin
$pwBox = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition($AE::ClassNameProperty, 'PasswordBox')))
if ($pwBox) {
    ($pwBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).SetValue('Healthy2024!')
    Log 'password set'
    Start-Sleep -Milliseconds 500
    $submit = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.AndCondition(
            (New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, 'Submit')),
            (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)))))
    if ($submit) { ($submit.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); Log 'Submit invoked' }
    else { Log 'no Submit button found' }
} else { Log 'no password box at this stage' }

for ($t = 0; $t -lt 10; $t++) {
    Start-Sleep -Seconds 3
    $win = FindBravoWin
    if ($win) {
        $n = $win.Current.Name
        Log ('title: ' + $n)
        if ($n -like '*VALLEY*' -and $n -notlike '*Bravo  *') { break }
    }
}
"end" | Add-Content $out
