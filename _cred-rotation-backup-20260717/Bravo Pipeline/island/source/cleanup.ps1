# cleanup.ps1 — remove the temporary island launch scheduled tasks left from
# the 2026-06-17 standalone-launch attempts (superseded by the watcher path).
Unregister-ScheduledTask -TaskName "ClaudeIslandGridread" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "ClaudeIslandMapY"     -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "ClaudeIslandMapY"     -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "island temp scheduled tasks removed"
