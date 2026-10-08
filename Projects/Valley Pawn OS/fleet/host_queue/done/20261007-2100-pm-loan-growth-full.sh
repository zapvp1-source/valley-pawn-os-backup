# PM/jewelry/coin loan-growth list (Joshua 10/7): every LOAN ticket by create-date year via saved "Claude Loan Portfolio 2026" + FDP layout.
# Analysis keeps ON LOAN rows. Most recent year first (WAY smoke, then the other 4), then older years.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth p:2025-10-08..2026-10-07 WAY pmlg-y1-WAY-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth p:2025-10-08..2026-10-07 CUL,HAR,LEX,ROA pmlg-y1-4st-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth p:2024-10-08..2025-10-07 CUL,HAR,LEX,ROA,WAY pmlg-y2-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth p:2023-10-08..2024-10-07 CUL,HAR,LEX,ROA,WAY pmlg-y3-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth p:2021-01-01..2023-10-07 CUL,HAR,LEX,ROA,WAY pmlg-y4-20261007
