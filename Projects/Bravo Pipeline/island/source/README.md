# Island — source/

This is where the island's own copies of pipeline handlers live.

**Rules:**
- Files in this folder are **island clones** of handlers — never the originals from `Bravo Data Extraction/`.
- A handler lands here only by deliberate copy or by being written net-new for an island-only cell.
- Island handlers write CSVs to `../output/` only. Never to the prod output folder.
- Until a handler is copied or written here, the island has no pipeline source — that is expected and intentional.

When a new cell is built and proven on the island, the migration playbook in `../ISLAND.md` covers how (and whether) it ports to prod.
