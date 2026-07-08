@echo off
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name = 'AutoHotkey64.exe'\" | Select-Object ProcessId, CommandLine | Format-List"
