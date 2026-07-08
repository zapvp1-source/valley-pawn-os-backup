# _uia_dump.ps1 — dump UIA tree of the Bravo window (run in Session 1)
$out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_uia_dump.txt'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ClassNameProperty, 'HwndWrapper[DefaultDomain;;4a944666-4626-4555-87d0-94d16f1a9106]')
"=== searching for Bravo window ===" | Set-Content $out
$wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $wins) {
    $name = $w.Current.Name
    $cls  = $w.Current.ClassName
    ("WIN: [" + $cls + "] " + $name) | Add-Content $out
    if ($name -like '*Bravo*' -or $name -like '*VALLEY*') {
        "  --- descendants (3 levels) ---" | Add-Content $out
        $kids = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
        $i = 0
        foreach ($k in $kids) {
            ("  [" + $k.Current.ControlType.ProgrammaticName + "] '" + $k.Current.Name + "' class=" + $k.Current.ClassName) | Add-Content $out
            $i++
            if ($i -ge 80) { "  ...truncated" | Add-Content $out; break }
        }
    }
}
"done" | Add-Content $out
