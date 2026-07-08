@echo off
REM Run AHK from Session 0 just to surface any syntax/runtime error to stderr.
REM Uses UNC path because Y: isn't mapped in Session 0.
set "AHK=C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
set "SCRIPT=\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\bravo_watcher.ahk"
set "ERRLOG=\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\ahk_stderr_check.txt"
del "%ERRLOG%" 2>nul
echo running... 1>&2
"%AHK%" /ErrorStdOut "%SCRIPT%" 2> "%ERRLOG%"
echo exit=%ERRORLEVEL%
