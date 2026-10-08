# PM loan-growth probe 3: reload handler (byamount/portfolio tokens), read criteria of two more existing saved reports on WAY.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth byamount WAY pm-loan-growth-byamount-WAY-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth portfolio WAY pm-loan-growth-portfolio-WAY-20261007
