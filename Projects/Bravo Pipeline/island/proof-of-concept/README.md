# Island — proof-of-concept/

Holds the **first** end-to-end run that proves the island works.

The PoC has to demonstrate, in one new task with zero impact on prod:

1. A handler in `../source/` runs, produces a CSV in `../output/`.
2. A consumer task in `../scheduled/` reads that CSV and produces a deliverable (Slack post, artifact, file, etc.).
3. A fresh Cowork session, opened only against `Bravo Pipeline/`, can run `bin/island-preflight.sh` → see everything green → reproduce the run.

Only after the PoC passes do we touch any prod task. See `../ISLAND.md` → Deployment checklist.
