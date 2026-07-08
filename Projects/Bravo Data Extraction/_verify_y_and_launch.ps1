# Verify Y: in joshuadavis session and launch Bravo
$drives = Get-PSDrive -PSProvider FileSystem | Select-Object Name,DisplayRoot
$drives | Out-File C:\Users\Public\post_reboot_drives.txt
$bravoPath = "C:\Program Files (x86)\Bravo Store Systems\Bravo\Bravo.exe"
if (Test-Path $bravoPath) {
    Start-Process $bravoPath
    Add-Content C:\Users\Public\post_reboot_drives.txt "`nBravo launch attempted from: $bravoPath"
} else {
    # try alternate paths
    $candidates = @(
        "C:\Program Files\Bravo Store Systems\Bravo\Bravo.exe",
        "C:\Program Files\Bravo\Bravo.exe",
        "C:\Program Files (x86)\Bravo\Bravo.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) {
            Start-Process $p
            Add-Content C:\Users\Public\post_reboot_drives.txt "`nBravo launch attempted from: $p"
            break
        }
    }
}
