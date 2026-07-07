# Island Pipeline Registry

**Source of truth for pipeline cells that live on the island.** Mirrors the schema of `../bravo-pipeline-registry.md` (prod) so cells port over cleanly when proven.

Read this BEFORE proposing any island work. See `ISLAND.md` for the protocol.

- **Last full audit:** 2026-06-17 — board approved the **grid-read extraction** direction (skip Bravo's Export dialog; read the rendered grid via UIA). Two PoC cells added below. See `proof-of-concept/gridread-poc.md`. (2026-06-08: first cell added — `safe-register-journal` CS-toggle patch.)
- **Island source code:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/source/`
- **Island CSV output:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/output/`
- **Island scheduled tasks:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/scheduled/`
- **Island PoC:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/proof-of-concept/`

---

## Status legend

- ✅ Proven on the island (verified working end-to-end)
- ⚙️ Built on the island, not yet proven
- 🔨 Proposed cell — name only
- 🚀 Deployed to prod (cell lives on island as regression rig; live version is in prod registry)
- ❌ Tried and failed — keep the row for history

---

## How to use this registry

1. **Pick a cell to build.** Add a 🔨 row with name, source report, intended consumer, intended channel.
2. **Build it.** Move to ⚙️ once handler and consumer exist on the island.
3. **Prove it.** Run the PoC end-to-end. Move to ✅ with today's "Last verified."
4. **Deploy it.** Follow `ISLAND.md` → Deployment checklist. Move to 🚀 once live in prod.
5. **Never delete a row.** Audit history matters.

---

## OUT — Island data extraction (Bravo → island CSV)

### Financial / GL

| Cell | Saved report (Bravo path) | Handler (island) | CSV pattern | Consumer (island task) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `safe-register-journal` (patched clone) | Dashboard → Reports → Closing Reports → Safe Register Journal | `SafeRegisterJournal_island.ahk` | `<date>_<STORE>_safe-register-journal.csv` | `daily-funds-verification` (prod) | `#daily-funds-reconcilation` (prod) | ⚙️ built, not yet proven on island | 2026-06-08 |
| `safe-register-journal-gridread` (PoC Step A) | Dashboard → Reports → Closing Reports → Safe Register Journal | `SafeRegisterJournal_gridread_island.ahk` | `<date>_<STORE>_safe-register-journal.csv` | `daily-funds-verification` (prod) | `#island-test` / none | 🔨 planned 2026-06-17 — grid-read mechanism check (narrow report) | 2026-06-17 |
| `end-of-month-gridread` (PoC Step B) | Dashboard → Reports → Closing Reports → End of Month | `EndOfMonth_gridread_island.ahk` | `<END_DATE>_<STORE>_end-of-month.csv` | `asset-recovery`, `monthly-analytics`, `eom-gl` (prod) | `#island-test` / none | 🔨 planned 2026-06-17 — grid-read virtualization check (wide report, ROA/WAY wedge case) | 2026-06-17 |

### Loans

| Cell | Saved report | Handler (island) | CSV pattern | Consumer (island task) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | |

### Layaways

| Cell | Saved report | Handler (island) | CSV pattern | Consumer (island task) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | |

### Inventory

| Cell | Saved report | Handler (island) | CSV pattern | Consumer (island task) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | |

### Sales & Employees

| Cell | Saved report | Handler (island) | CSV pattern | Consumer (island task) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | |

### Customer

| Cell | Saved report | Handler (island) | CSV pattern | Consumer (island task) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | |

---

## IN — Island data push (island → Bravo)

| Action | Trigger / Skill (island) | Mechanism | Status |
|---|---|---|---|
| _(none yet)_ | | | |

---

## Candidate first cells (suggested PoC targets — pick one)

These are good first-cell candidates because they're isolated, low-risk to prove, and demonstrate the island pattern in different shapes:

1. **`end-of-month` clone** — the cell is ✅ in prod, well-understood, single CSV output. Ideal "prove the wiring" target.
2. **`dormant-customer` (net-new)** — currently 🔨 in prod. Building it on the island first means we never expose a half-built cell to live ops.
3. **`customer-segmentation` (net-new)** — also 🔨 in prod. Most strategic, but needs Joshua-defined thresholds before it can be built.

Recommendation: start with #1 (proves the wiring with zero scope risk), then move to #2 once the pattern is locked.
