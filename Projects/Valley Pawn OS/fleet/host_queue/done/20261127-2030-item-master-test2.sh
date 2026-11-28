# restart the Bravo watcher to load the item-master row cap fix, then re-test (Bravo Warehouse)
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" item-master 2026-08-01..2026-08-31 LEX wh-item-master-test2-LEX-2026-08
