# Bravo Warehouse smoke tests, Lexington only, read-only cells: sold ledger for the End of Month tie-out, then loans and buys written in Aug 2026.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" sold-inventory 2026-08-01..2026-08-27 LEX wh-sold-inventory-aug-LEX
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" loans-written 2026-08-01..2026-08-31 LEX wh-loans-written-smoke-LEX
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" buys-written 2026-08-01..2026-08-31 LEX wh-buys-written-smoke-LEX
