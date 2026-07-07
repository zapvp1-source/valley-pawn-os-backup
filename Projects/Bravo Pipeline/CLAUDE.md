# Bravo Pipeline — Project-level instructions

This project owns the shared infrastructure that moves data into and out of Bravo POS for Valley Pawn / Full Circle Finance Inc. Every Valley Pawn skill, scheduled task, and ad-hoc question that touches Bravo data depends on it.

## MANDATORY FIRST STEP for any Bravo-touching task

Before answering, proposing, or extracting anything Bravo-related, run **both** of these as your first tool calls:

```bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bin/bravo-preflight.sh"
cat  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bravo-pipeline-registry.md"
```

This is a contract, not a suggestion. Skipping it makes the entire system "useless" per Joshua. See `SESSION_PROTOCOL.md` for the full rationale and decision tree.

## Project layout

- `bravo-pipeline-registry.md` — the single source of truth catalog of every pipeline cell (OUT and IN). Read this every session.
- `SESSION_PROTOCOL.md` — the mandatory protocol, the why, and the failure path.
- `bin/bravo-preflight.sh` — runnable preflight script. Outputs CSV freshness, registry age, pipeline visibility.
- `bin/island-preflight.sh` — island-only preflight. Fails loud if any island path is missing.
- `island/` — the safe sandbox. All new/experimental pipeline work is built and proven here before any touching of prod. See `island/ISLAND.md`.

## Island Mode (for new or experimental pipeline work)

If the task is **building, testing, or proving a new cell, handler, or scheduled task**, work on the island — never on prod. The island lives entirely inside this folder, so any session that can see this folder can do island work end-to-end.

Required first calls for island work (in addition to the prod preflight + registry above):

```bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bin/island-preflight.sh"
cat  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/island-registry.md"
cat  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/ISLAND.md"
```

**Island isolation — do not violate:**

1. Never edit any file under `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` from island work. Read-reference only.
2. Never edit any file under `/Users/joshuadavis/Documents/Claude/Scheduled/` from island work. Read-reference only.
3. Island handlers write CSVs only to `island/output/`. Never to prod's `Bravo Data Extraction/output/`.
4. Island consumers post to a dedicated island Slack channel (or nowhere) until deployed.
5. Cells migrate island → prod only after the deployment checklist in `island/ISLAND.md` passes.

## Related projects on Joshua's Mac

- **Pipeline source code:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` — AHK watcher, dispatch tables, report handlers, CSV output folder.
- **Scheduled tasks:** `/Users/joshuadavis/Documents/Claude/Scheduled/` — every Cowork scheduled task; each task's `SKILL.md` documents the pipeline cells it depends on.

## Hard rules

1. **Additive only.** Never edit existing AHK handlers, dispatch entries, or saved Bravo reports. Clone and add. See `bravo-context` SKILL.md for the rationale.
2. **Reuse CSVs.** If a CSV from the last 30 days covers the requested window, use it.
3. **Never propose extracting from scratch** when the registry shows the cell exists.
4. **Update the registry** after any verification, status change, or new-cell add.
