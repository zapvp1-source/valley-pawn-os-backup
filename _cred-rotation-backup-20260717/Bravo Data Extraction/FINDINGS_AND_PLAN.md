# Bravo Data Extraction — Findings & Revised Plan

_Investigated 2026-05-12 by direct inspection of the Windows VM._

## TL;DR

- **UI automation is the only path.** No SQL shortcut, no API.
- **The toolchain is already in place.** AutoHotkey v2 is installed, Python is installed, and you already have a working AHK script (`BravoAutoLogin.ahk`) that logs into Bravo.
- **The Mac↔VM file bridge already works.** The VM's `Y:\` drive maps directly to your Mac home folder. Files I write at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` appear inside the VM at `Y:\Documents\Claude\Projects\Bravo Data Extraction\`. No share to set up.
- **Recommendation: switch language from Python+pywinauto to AutoHotkey v2 + UIA-v2 library.** Same end result, but builds on what you already have.
- **Ready to start Slice 1** once you approve.

## What I learned in the VM

### Bravo is fully cloud-backed — no local DB to read

Bravo's `Bravo.exe.config` makes the data path explicit:

```
<objectServer remoteBaseURL="https://bravoapplication.com"
              serverPort="21209"
              serviceName="BravoBOS/EntityService.svc">
```

So Bravo connects to `https://bravoapplication.com:21209/BravoBOS/EntityService.svc`, a WCF/SOAP service running on the IdeaBlade DevForce framework. There is no local connection string. SQL Server Express is installed but the engine service (`MSSQL$SQLEXPRESS`) is **stopped** — only `SQLWriter` (the VSS backup helper) is running, and that doesn't hold any Bravo data. Bravo is a thin .NET WPF client over a private SOAP API.

That means:
- The "read the local SQL DB" shortcut is dead.
- Theoretically we could replay Bravo's WCF calls directly, but it's an undocumented private API on a custom ORM with signed auth. Bravo support also said no. Not a productive path.
- **UI automation is the answer.** What you suspected is correct.

### The existing AHK script is a tiny but working foundation

`C:\Users\joshuadavis\BravoAutoLogin.ahk` (552 bytes, AutoHotkey v2):

```
#Requires AutoHotkey v2.0
BRAVO_USERNAME := "FREE1@WAY"
BRAVO_PASSWORD := "Health2035!"
^+l:: {  ; Ctrl+Shift+L
    Send("{Tab 10}") ... Send(BRAVO_USERNAME) ... Send(BRAVO_PASSWORD) ... Send("{Enter}")
}
```

It's Tab/Send-based (no UIA), so it's brittle to layout changes. But it tells us:
- AutoHotkey v2 is installed and you already use it for Bravo.
- The credentials and login flow are exactly what `bravo-store-cycle` documents.
- Building on AHK keeps continuity with how you already think about this app.

### Toolchain inventory on the VM

| Tool | Status | Path |
|---|---|---|
| AutoHotkey v2 | Installed | `C:\Program Files\AutoHotkey\` |
| Python | Installed | `C:\Users\joshuadavis\AppData\Local\Microsoft\WindowsApps\python.exe` (MS Store) |
| .NET SDK | Not installed | — |
| SQL Server Express | Installed but stopped | service `MSSQL$SQLEXPRESS` |
| SQL Server VSS Writer | Running | `sqlwriter.exe` — irrelevant to us |

### Mac↔VM shared folders are already mapped

Inside the VM:

| Drive | Maps to |
|---|---|
| `X:\` | `\\Mac\iCloud` (your iCloud Drive) |
| `Y:\` | `\\Mac\Home` (your Mac home folder, `~/`) |
| `Z:\` | `\\Mac\AllFiles` (entire Mac filesystem) |

I verified this by writing a probe script from the Mac side at `~/Documents/Claude/Projects/Bravo Data Extraction/probe.ps1` and running it from inside the VM via `Y:\Documents\Claude\Projects\Bravo Data Extraction\probe.ps1`. The bridge works in both directions, instantly.

This is a huge simplification: **no Parallels share to configure.** The folder you're already using for this project is the shared folder.

### Bravo's tech stack — informational

- WPF over .NET (multiple `Common.MVVM.dll`, `Common.Presentation.dll` etc — standard WPF MVVM)
- IdeaBlade DevForce ORM (older Telerik-era framework, no current public docs)
- SignalR for real-time updates at `http://bravoapplication.com:21208/BravoBOS/signalr`
- Cloud images at `images.buya.com`

The important detail for us: WPF apps expose a clean UI Automation tree, which means UIA-based automation (UIA-v2 in AHK or pywinauto in Python) will see Bravo's controls as proper named elements, not pixel coordinates. This is the *good* kind of native app for automation.

## Revised plan

### Language choice — AutoHotkey v2 + UIA-v2

I'm changing my earlier Python+pywinauto recommendation to **AutoHotkey v2 + UIA-v2**. Reasons:

1. AHK is already installed and you already use it for Bravo.
2. The community-maintained UIA-v2 library (Descolada/UIA-v2 on GitHub) gives AHK the same UI Automation tree access that pywinauto offers — find elements by name/class/automation-id, not by clicking pixels.
3. One fewer tool to learn and one fewer environment to maintain.
4. Smaller code footprint. The AHK script for one report ends up being ~50 lines, not the ~150 a pywinauto equivalent would need.
5. AHK can write CSV directly (`FileAppend`) — no Python needed for the slice-1 deliverable.

Python stays available if a specific task needs heavy data wrangling later (we already have it installed).

### Folder layout — everything lives on the Mac, accessed from VM via Y:

The whole project lives at:

- Mac side: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`
- VM side: `Y:\Documents\Claude\Projects\Bravo Data Extraction\`

Same files, two views.

```
Bravo Data Extraction/
├── bravo_export.ahk            ← entry point, dispatches reports
├── bravo_watcher.ahk           ← persistent script that polls triggers/
├── config.json                 ← credentials, paths (NOT committed if we ever git this)
├── lib/
│   ├── UIA.ahk                 ← Descolada UIA-v2 library (vendored)
│   ├── UIA_Browser.ahk
│   └── Bravo.ahk               ← our Bravo wrapper (login, store cycle, common controls)
├── reports/
│   ├── SafeRegisterJournal.ahk
│   ├── TillRegisterJournal.ahk
│   ├── Loans75DaysPastDue.ahk
│   ├── Layaways.ahk
│   ├── AgedJewelryMarkdown.ahk
│   ├── AgedGeneralMerchMarkdown.ahk
│   ├── EmployeeActivity.ahk
│   ├── CompanyKPIs.ahk
│   ├── SalesByVendor.ahk
│   └── ChekkitInactives.ahk
├── triggers/                   ← Mac writes JSON trigger files; VM watcher picks them up
├── output/                     ← VM writes CSVs here (Mac reads them)
├── results/                    ← VM writes per-run status JSON (Mac reads them)
└── logs/                       ← VM writes run logs
```

### Invocation contract

Cowork (Mac side) writes a trigger file:

```json
// triggers/2026-05-12T08-00-00_funds-verification.json
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

`bravo_watcher.ahk` runs persistently in the VM (auto-started at login), polls `triggers/` every 30 seconds, dispatches each `reports[]` entry to the matching `reports/*.ahk` module, and writes:

- `output/{date}_{STORE}_{report-slug}.csv` — one per (store, report) cell
- `results/{trigger_id}.result.json` — overall + per-cell status
- `logs/{trigger_id}.log` — full execution log

Cowork's side: drop a trigger, poll for the result.json, read the CSVs. Zero clicks, zero screenshots.

### Slice plan

**Slice 1 — End-to-end thinnest possible (1 day work):**
- Single store (CUL), single report (Safe Register Journal for one date)
- Trigger file → CSV in output/ → status in results/
- No store cycling yet, no other reports
- Proves the entire pipeline including Mac↔VM file roundtrip

**Slice 2 — Store cycling (½ day):**
- Add CUL → HAR → LEX → ROA → WAY loop using Bravo's Lock Session / Global Access flow
- Port the pixel-coordinate version from `bravo-store-cycle` skill into UIA-tree calls

**Slice 3+ — Reports, in order of computer-use minutes saved per week:**
1. 75-Day Past Due Loans (weekly, 5 stores, currently slowest)
2. Layaways (5 categories × 5 stores — also weekly)
3. Aged Jewelry & General Merch Markdown (weekly, 5 stores)
4. Employee Activity (weekly, 5 stores)
5. Company KPIs (cross-store, one-shot)
6. Sales by Vendor (weekly, for new-inv report)
7. Chekkit Inactives saved report (weekly, 5 stores)
8. Till Register Journal (when needed)

**Slice 4 — Re-point scheduled tasks:**
- Daily Funds Verification → trigger file instead of computer-use
- Weekly Loan & Layaway Review → trigger file
- Monday Bravo Combined Run → trigger file
- New Inventory Weekly Report → trigger file

End state: Cowork never touches Bravo's UI again. The VM does it locally, no screenshot round-trips.

## What I still need from you before I write code

1. **Approval to switch from Python+pywinauto to AutoHotkey v2 + UIA-v2.** Same outcome, simpler stack given what's already on your machine.
2. **The `project_funds_verification_report_location.md` memory contents** — or just tell me the menu path to Safe Register Journal in Bravo. I can also discover it during slice 1 development; it's not strictly blocking.
3. **Confirmation that `FREE1@WAY` / `Health2035!` has rights to pull Safe Register Journal at all 5 stores.** Not blocking slice 1 (CUL only), but worth knowing before slice 2.
4. **Whether to auto-launch `bravo_watcher.ahk` on Windows startup** so the VM is always ready to accept trigger files. (Default I'd pick: yes — add it to Task Scheduler "At log on of Joshua.")

Once you green-light those, I write Slice 1: `lib/UIA.ahk` (vendored library), `lib/Bravo.ahk` (Bravo wrapper), `reports/SafeRegisterJournal.ahk` (the actual report logic), and `bravo_export.ahk` (the entry point that ties it together). All four files live on the Mac side. We test it once together, then it's a permanent part of the toolchain.

## What I will NOT do without further approval

- Modify the existing `BravoAutoLogin.ahk` — that's your working tool and I won't touch it.
- Run any of the new automation against live store data without you watching the first run.
- Re-point any scheduled tasks to use the trigger files until the underlying script has been proven on at least one full run per report.
