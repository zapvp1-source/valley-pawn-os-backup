$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$script = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\ScrapBucketCloseoutWatcher.ahk'
$proc = Start-Process -FilePath $ahk -ArgumentList "`"$script`"" -PassThru
Start-Sleep -Seconds 5
$alive = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($alive) {
    Write-Output "LAUNCHED_OK PID=$($proc.Id)"
} else {
    Write-Output "LAUNCH_FAILED_OR_EXITED_IMMEDIATELY"
}
