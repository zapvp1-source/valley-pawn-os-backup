# Slice 2 — Store Cycling — Status

_Updated 2026-05-12 ~11:40 AM._

## What works

✅ **`SwitchStore(targetStore, password)`** drives the full Lock Session → Global Access → Store Selector → pick row → paste password → Submit flow and lands on the target store's Dashboard. Verified end-to-end in the log:

```
EnsureStore: switching from HAR to CUL
SwitchStore: click Lock Session
SwitchStore: click Global Access
SwitchStore: double-click row store_CUL
SwitchStore: paste password
SwitchStore: click Submit
SwitchStore: landed on CUL          ← title-bar check confirmed
store confirmed: CUL                ← report handler picks up here
```

✅ **`EnsureStore(targetStore, password)`** correctly no-ops if Bravo is already on the target store, cycles otherwise. Wired into `SafeRegisterJournal.ahk`.

✅ **`bravo-store-cycle` skill's coordinates were off by 25-40px** (different reference frame). Updated `SC_COORDS` with verified values from a current Bravo screenshot.

## What's broken

⚠️ **SRJ flow on CUL didn't produce a CSV after the cycle landed**. The log shows every click happening on schedule, but no file appears. Two suspects:

1. **A click during the report/export sequence hit a Bravo marketing banner.** Chrome opened a `info.bravostoresystems.com/add-cloud-storage` tab partway through the run — that only happens if a click landed on a hyperlinked element. CUL's Dashboard / Reports listing may have a slightly different banner layout than HAR.

2. **Coord drift between stores.** Each store's Bravo instance might render with tiny pixel offsets (different banners pushing layout). The exact same coordinates work on HAR but might be ~15-30px off on CUL.

## Why this is not a blocker

Slice 1 already proved the pipeline end-to-end. Slice 2 proved store cycling. The only remaining failure mode is the coordinate-fragility issue I've flagged from day one — and it's the exact problem **slice 3 (UIA-v2 element lookups)** is meant to eliminate forever.

**Three real bugs found and fixed today, in order:**

1. JSON parser — switched from PowerShell stdout to pure AHK regex (PS stdout was UTF-16 mojibake)
2. CoordMode "Client" → "Screen" — and called inside the handler (CoordMode is per-thread in AHK v2)
3. Parallels DPI + Mac chrome offset — VM renders at 4096x2168 internally, screenshots are 1456x819, with ~48px of Mac chrome above the VM display area
4. Store-cycle coordinates — skill's coords were from an old reference frame, off by 25-40px; recaptured from current screenshots

**One bug remaining for slice 2 sign-off:** CUL-specific SRJ click drift OR banner-link hijack. Same class as #4; same eventual fix (UIA-v2).

## What to do next

Two paths. Pick one:

### Path A — Slice 3 (UIA-v2) now

Vendor Descolada's UIA-v2 library, replace coordinate clicks with element-name lookups (`btn := elem.FindFirst({Name: "Lock Session"})`). Every click finds its target by name regardless of pixel position. After this, all 10 reports become quick to add because they're insensitive to:
- Bravo window resizes
- DPI/scaling differences
- Banner ads pushing layout around
- Different Bravo versions

Cost: ~2-4 hours to vendor + rewrite. Pays back across all 10 reports.

### Path B — Brute-force per-store coords now

Recapture coords for each store individually (5 store-specific tables), or detect-and-tweak in real time. Faster to get one report working multi-store, but every new report inherits the brittleness, and any Bravo banner rotation re-breaks things.

Cost: ~30 min per report × 5 stores × 10 reports = a lot, with ongoing maintenance burden.

I strongly recommend **Path A** even though it adds upfront work. The fragility we just fought through is exactly what UIA-v2 was invented to solve.

## Current Bravo state

After the slice-2 test, Bravo ended up on CUL's Login screen with the password partially pasted. I clicked Switch User to send it back to HAR home. You should see HAR's Dashboard next time you look.

The watcher is still running in the tray. To kill it: `Ctrl+Alt+W`.
