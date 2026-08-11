Add-Type -AssemblyName System.Windows.Forms
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
Write-Host ("VirtualScreen: {0}x{1}" -f $b.Width, $b.Height)
foreach ($s in [System.Windows.Forms.Screen]::AllScreens) {
    Write-Host ("Screen: {0}x{1} primary={2}" -f $s.Bounds.Width, $s.Bounds.Height, $s.Primary)
}
try {
    $v = Get-CimInstance Win32_VideoController
    foreach ($c in $v) { Write-Host ("VideoController: current {0}x{1}" -f $c.CurrentHorizontalResolution, $c.CurrentVerticalResolution) }
} catch {}
