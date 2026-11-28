# validate and restart the Bravo watcher after adding the item-master cell (Bravo Warehouse)
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
# first test pull: Lexington, August 2026, every item by status date
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" item-master 2026-08-01..2026-08-31 LEX wh-item-master-test-LEX-2026-08
