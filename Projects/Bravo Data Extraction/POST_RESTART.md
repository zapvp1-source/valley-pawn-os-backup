# After you restart the VM — what happens, what to do

## What runs automatically

When Windows logs you back in, the Startup shortcut launches `bravo_watcher.ahk`. You should see a small notification (lower-right) saying **"Bravo Watcher started — Polling … every 30s"** and a tray icon. From that moment, the watcher checks the `triggers/` folder every 30 seconds.

If you don't see that notification, the shortcut didn't fire. Open File Explorer to `Y:\Documents\Claude\Projects\Bravo Data Extraction\` and double-click `bravo_watcher.ahk` to start it manually.

## What to do before the first test

The slice-1 script assumes Bravo is on the **HAR Dashboard**. Get there first:

1. Open Bravo if it isn't already.
2. Log in if it asks (your existing `BravoAutoLogin.ahk` Ctrl+Shift+L still works for this).
3. Title bar should read `Bravo  2026.2.2.3  VALLEY PAWN - HARRISONBURG (HAR)`.
4. If a "Till must be opened…" popup shows up, click Ok (the script now dismisses these automatically, but it's cleaner if you start without one).

You don't need to do anything else. Just leave Bravo at the Dashboard.

## Run the test

Tell me you're ready, and I'll drop `test_trigger.json` into the `triggers/` folder from the Mac. The watcher will pick it up within 30 seconds and run the whole Safe Register Journal flow autonomously.

Alternatively, you can run it yourself by moving the file:
- Drag `test_trigger.json` from the project root into the `triggers/` subfolder.

## What I'll do after the test fires

- Read `results/slice1-smoke-test-2026-05-12.result.json` from the Mac.
- Read `logs/slice1-smoke-test-2026-05-12.log` to see every click the script made.
- Read the CSV at `output/2026-05-12_HAR_safe-register-journal.csv` to verify the data.

If anything failed, the log tells me exactly which step. I fix the AHK from the Mac and drop another trigger. No more clicking through Bravo by hand.

## To kill the watcher

If you ever want to stop the watcher:
- `Ctrl+Alt+W` while Windows has focus (clean exit)
- Or right-click the tray icon → Exit

Next launch happens automatically the next time you log in.
