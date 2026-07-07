# Bravo Data Extraction

Local Windows-side automation that replaces Cowork's computer-use UI driving of Bravo POS. Cowork drops a trigger file, the VM does the Bravo work, Cowork reads the CSV. No clicks across the Mac↔Windows boundary.

## How it works (one paragraph)

The whole project lives on the Mac at `~/Documents/Claude/Projects/Bravo Data Extraction/`. Inside the Parallels Windows VM, the same folder is reachable as `Y:\Documents\Claude\Projects\Bravo Data Extraction\` because Parallels already maps `Y:` to your Mac home folder. A single AutoHotkey v2 script (`bravo_watcher.ahk`) runs persistently inside the VM and watches the `triggers/` folder. When Cowork wants Bravo data, it writes a small JSON file into `triggers/`. The watcher picks it up, drives Bravo, exports the requested reports as CSV into `output/`, and writes a status JSON into `results/`. Cowork reads the result + CSVs — never touches Bravo itself.

## Folder layout

```
Bravo Data Extraction/
├── bravo_watcher.ahk           Persistent watcher (run this on Windows login)
├── bravo_export.ahk            Manual one-shot runner (for dev/testing)
├── config.json                 Credentials + paths (NOT committed; create from example)
├── config.example.json         Safe-to-share template
├── .gitignore
├── FINDINGS_AND_PLAN.md        Investigation log + plan
├── README.md                   This file
│
├── lib/
│   ├── Bravo.ahk               Bravo wrapper (login, store, popups, logging, CSV)
│   └── Json.ahk                JSON I/O via PowerShell
│
├── reports/                    One AHK module per report type
│   ├── SafeRegisterJournal.ahk (Slice 1 — partially implemented; needs nav path)
│   ├── ... (added in later slices)
│
├── triggers/                   Cowork drops <id>.json here. Watcher consumes them.
│   └── processed/              Processed triggers archived here (kept for audit)
│
├── output/                     CSV exports land here: YYYY-MM-DD_STORE_report-slug.csv
├── results/                    Per-trigger status JSONs: <id>.result.json
└── logs/                       Per-trigger logs: <id>.log
```

## First-time setup (on the Windows VM)

1. **Verify AutoHotkey v2 is installed.** Should already be there — it's at `C:\Program Files\AutoHotkey\`. You also already have a working `C:\Users\joshuadavis\BravoAutoLogin.ahk`, which confirms AHK runs.

2. **Make sure config.json is in place.** It should already be at the project root. If not, copy `config.example.json` to `config.json` and fill in the password.

3. **Start the watcher (one-time per Windows session):**
   - Open `Y:\Documents\Claude\Projects\Bravo Data Extraction\` in File Explorer
   - Double-click `bravo_watcher.ahk`
   - You should see a tray-icon notification: "Bravo Watcher started"
   - Hotkeys while running: `Ctrl+Alt+W` exits cleanly, `Ctrl+Alt+R` forces an immediate poll.

4. **Auto-start at Windows login (recommended, set up once):**
   - Press `Win+R`, type `shell:startup`, press Enter
   - Drag a shortcut to `bravo_watcher.ahk` into that folder
   - Reboot to verify it auto-starts

## Invoking from Cowork (the new pattern)

Instead of computer-use to click through Bravo, Cowork writes a trigger file:

```json
{
  "id": "2026-05-12T08-00-00_funds-verification",
  "requested_at": "2026-05-12T08:00:00-04:00",
  "reports": [
    {
      "name": "safe-register-journal",
      "stores": ["CUL", "HAR", "LEX", "ROA", "WAY"],
      "date": "2026-05-11"
    }
  ]
}
```

…to `~/Documents/Claude/Projects/Bravo Data Extraction/triggers/2026-05-12T08-00-00_funds-verification.json`.

Within ~30 seconds (the poll interval) the watcher picks it up. Cowork polls for the result file at `results/<id>.result.json` and reads the CSVs at `output/<date>_<STORE>_<report-slug>.csv`.

The result JSON looks like:

```json
{
  "trigger_id": "2026-05-12T08-00-00_funds-verification",
  "started_at": "2026-05-12T08:00:03",
  "finished_at": "2026-05-12T08:04:12",
  "status": "success",
  "cells": [
    {
      "report": "safe-register-journal",
      "store": "CUL",
      "date": "2026-05-11",
      "status": "success",
      "output_path": "Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\output\\2026-05-11_CUL_safe-register-journal.csv",
      "row_count": 42,
      "duration_ms": 38000,
      "error": ""
    }
  ],
  "errors": []
}
```

Overall `status` is `success` when every cell succeeded, `partial` when at least one failed, `error` when the trigger itself was invalid.

## Manual testing (during dev)

The `bravo_export.ahk` script invokes a single report by hand:

```cmd
AutoHotkey64.exe bravo_export.ahk safe-register-journal CUL 2026-05-11
```

Double-clicking the file with no args prompts you for the three inputs.

The output, result file, and log are written exactly as if the watcher had picked up a trigger — same folders, same naming.

## How report modules work

Every report under `reports/` exports one function:

```ahk
Pull<ReportName>(store, date, outputDir) -> Map
```

Returning a Map with the cell-result fields (`status`, `output_path`, `row_count`, `duration_ms`, `error`). The watcher and the manual runner both call these the same way.

### Adding a new report

1. Copy `reports/SafeRegisterJournal.ahk` to `reports/<YourReport>.ahk`.
2. Rename the function to `Pull<YourReport>` and fill in the Bravo navigation in the body.
3. Add a `#Include reports\<YourReport>.ahk` line to **both** `bravo_watcher.ahk` and `bravo_export.ahk`.
4. Register the handler: in both files add a line like `REPORT_HANDLERS["your-report-slug"] := PullYourReport`.
5. Add the slug + relative path under `report_handlers` in `config.example.json` and `config.json` (the path field is documentation today; the runtime registration is via the AHK Map above).

That's it. The trigger-file contract is identical for the new report.

## Slice 1 status (in progress)

| Component | Status |
|---|---|
| Folder layout | Done |
| `config.json` / `.gitignore` | Done |
| `lib/Json.ahk` (JSON I/O via PowerShell) | Done |
| `lib/Bravo.ahk` (wrappers) | Done |
| `bravo_watcher.ahk` | Done |
| `bravo_export.ahk` | Done |
| `reports/SafeRegisterJournal.ahk` — wrapper, error handling | Done |
| `reports/SafeRegisterJournal.ahk` — actual Bravo nav | **TODO** (needs the menu path) |
| Verify slice-1 end-to-end with a real trigger | After nav is wired |

The only remaining slice-1 work is filling in the navigation block in `reports/SafeRegisterJournal.ahk`. Look for the `TODO:NAV` markers in that file. Joshua needs to confirm the exact menu path (Dashboard / Reporting Pro / etc.) before I can wire it up correctly.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Watcher doesn't pick up a trigger | Check the file is `.json`, not `.json.txt`. Check tray icon shows watcher is running. Press `Ctrl+Alt+R` to force a poll. |
| "Bravo window not found" in logs | Bravo isn't running. Launch it in Parallels first. |
| "Wrong store: Bravo is on X, need Y" | Slice 1 assumes you're on the right store. Slice 2 adds store cycling. For now, switch stores manually before triggering. |
| Trigger keeps re-firing | Should be impossible — watcher moves processed triggers into `triggers/processed/`. If you see this, check whether you accidentally re-dropped the same file. |
| CSV is empty | Bravo's export may have produced 0 rows for that date. Confirm with a manual run in the UI for the same date. |
| Watcher crashes | Check the latest file in `logs/` — last line will say what blew up. |

## Security notes

- `config.json` contains the Bravo password. It lives on your Mac home folder (same trust boundary as your Keychain), gitignored. Never push it to a public/shared repo or upload it anywhere.
- The Mac↔VM share is your already-existing `\\Mac\Home` mount — same security boundary you've had since you set up Parallels.
- No credentials are sent anywhere outside your machine. Bravo's own cloud session (which the UI handles) is unaffected.
