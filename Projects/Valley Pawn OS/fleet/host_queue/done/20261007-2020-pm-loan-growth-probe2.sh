# PM loan-growth probe 2: reload handler (added walkdesc/walkplain tokens), then CUL with FDP layout and WAY with the two fallback layouts.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth walk CUL pm-loan-growth-walk-CUL-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth walkplain WAY pm-loan-growth-walkplain-WAY-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth walkdesc WAY pm-loan-growth-walkdesc-WAY-20261007
