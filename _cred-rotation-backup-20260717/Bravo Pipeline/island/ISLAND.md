# Island — the safe sandbox for Bravo pipeline work

**Status:** scaffolding live, awaiting first PoC.
**Created:** 2026-05-27.
**Why this exists:** Joshua wants every new pipeline cell, handler, or scheduled task built and proven in isolation before it touches anything that's running. The prod side (`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` and `/Users/joshuadavis/Documents/Claude/Scheduled/`) is frozen from this folder's perspective — additive-only is enforced by physical separation, not by hope.

---

## What the island is

A self-contained, fully reachable-from-any-session copy of the pipeline pattern, living entirely inside `/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/`:

```
island/
├── ISLAND.md            ← this file
├── island-registry.md   ← island's own registry of cells, mirrors prod schema
├── source/              ← island handlers (clones or net-new), write to ../output/
├── output/              ← island CSVs only
├── scheduled/           ← island scheduled task definitions (SKILL.md per task)
└── proof-of-concept/    ← the one task that proves the island works end-to-end
```

Because all of this lives inside `Bravo Pipeline/`, **any Cowork session that opens this folder sees the entire island**. That kills the "session is blind to source + output" failure mode that prod has today.

---

## What the island is NOT

- It is **not** a replacement for prod. Nothing in prod changes because of work done here.
- It is **not** a place to run live business operations. Don't post island output to real channels until the cell is deployed to prod.
- It is **not** a fork that diverges forever. The deployment checklist below moves proven cells back to prod.

---

## Hard rules (additive-only, restated)

1. **Never edit any file under `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`** from island work. Read-reference only.
2. **Never edit any file under `/Users/joshuadavis/Documents/Claude/Scheduled/`** from island work. Read-reference only.
3. **Never write a CSV to `Bravo Data Extraction/output/`** from an island handler.
4. **Never re-use a prod Slack channel** for island output. Use a dedicated island channel (e.g. `#island-test`) or no channel at all while proving.
5. **Update `island-registry.md`** every time a cell is added, changed, verified, or retired on the island.

---

## How to build a new cell on the island

1. **Confirm preflight.** Run `bin/island-preflight.sh`. Must be all-green before touching anything.
2. **Define the cell.** Add a row to `island-registry.md` with status 🔨 (gap) — pick a name, the Bravo saved report it draws from, the consumer task it feeds, and the channel it would post to in prod.
3. **Build the handler.** Place it in `island/source/`. If cloning a prod handler, copy with a `_island` suffix on the filename so it's unmistakable.
4. **Produce a CSV.** Run the handler. The CSV must land in `island/output/` with the prod naming convention.
5. **Build the consumer task.** Place its SKILL.md in `island/scheduled/<task-name>/SKILL.md`. The task reads from `island/output/` only.
6. **Prove it end-to-end.** Use `island/proof-of-concept/` to script the run that demonstrates the cell works in a fresh session.
7. **Bump status to ✅** in `island-registry.md` with today's date.

---

## Deployment checklist (island → prod)

Only after the cell is ✅ on the island AND has run cleanly through one full PoC.

1. **Snapshot the island cell.** Note exact handler filename, saved-report name, CSV pattern, consumer task SKILL.md.
2. **Read prod's `bravo-pipeline-registry.md`** to confirm the cell name doesn't already exist (collision check).
3. **Copy the handler** from `island/source/` into `Bravo Data Extraction/reports/` with its prod filename (drop `_island` suffix).
4. **Add a dispatch entry** in `bravo_watcher.ahk` and `bravo_export.ahk` — additive, never editing existing rows.
5. **Copy the consumer task** from `island/scheduled/` into `/Users/joshuadavis/Documents/Claude/Scheduled/`. Update its SKILL.md to read from `Bravo Data Extraction/output/` instead of `island/output/`.
6. **Add a row to `bravo-pipeline-registry.md`** with status ✅ and today's "Last verified."
7. **Schedule the task** in Cowork (cron expression, real Slack channel).
8. **Watch the first prod run.** If it fails, fix on the island, not in prod — re-deploy from island.
9. **Leave the island cell in place** as a regression rig. Don't delete it.

---

## How a future session uses the island

A Cowork session opened against `Bravo Pipeline/` only — exactly the failure case today — can do all island work, because the island lives inside this folder. The session's first two tool calls remain the same as the prod protocol:

```bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bin/bravo-preflight.sh"
cat  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bravo-pipeline-registry.md"
```

If the session's intent is island work (building, testing, proving), add a third:

```bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bin/island-preflight.sh"
cat  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/island-registry.md"
```

If both registries are reachable and both preflights are green, the session can build on the island without risk of touching prod.

---

## What is needed from Joshua to populate the island the first time

The island scaffolding is complete. To put **real handler code** on the island, one of the following is required (this session cannot do it alone — `Bravo Data Extraction/` is not mounted here):

- **Option A — Mount `Projects/` once.** Open a single Cowork session against the parent `Projects/` folder. From there I can copy specific handlers into `island/source/` with the `_island` suffix, leaving prod untouched. After the copy, sessions can re-scope to `Bravo Pipeline/` only.
- **Option B — osascript copy with approval.** Grant computer-use osascript and approve a `cp` from `Bravo Data Extraction/reports/<file>.ahk` → `island/source/<file>_island.ahk` for the specific handlers we want to start with.
- **Option C — Paste inline.** For a small first PoC, paste one handler's source into chat and I write it into `island/source/`.

The first PoC doesn't need every handler — pick the simplest one (likely `EndOfMonth.ahk` or a known-good Loan handler) and we prove the pattern with one cell before going wider.
