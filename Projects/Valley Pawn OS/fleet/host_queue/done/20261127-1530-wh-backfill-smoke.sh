# Warehouse backfill smoke test: one store, one missing sold window, existing read-only cell (no new Bravo objects).
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" sold-discount-detail 2026-05-18..2026-05-31 LEX wh-backfill-sold-2026-05b-LEX
