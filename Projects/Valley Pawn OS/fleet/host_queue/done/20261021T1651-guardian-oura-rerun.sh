#!/bin/bash
# Fleet Guardian 2026-10-21: rerun-safe retry of oura-daily-import (rerun_manifest: rerun_safe).
# Ledger row 2026-10-21 08:30 ET flagged "readiness latest 2026-10-17 is 4 days old" -- confirming
# whether this is a transient import bug or genuinely stale upstream Oura data.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/oura_import.sh"
