#!/bin/bash
# HOST JOB 2026-09-17 — give the 4 model-needing Bravo tasks the host-queue path (HOST ACCESS block).
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_skill.sh" daily-funds-verification "/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/a109d110/outputs/daily-funds-verification/SKILL.md"
bash "$BIN/install_skill.sh" funds-verification-watchdog "/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/a109d110/outputs/funds-verification-watchdog/SKILL.md"
bash "$BIN/install_skill.sh" jewelry-onhand-nightly-pull "/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/a109d110/outputs/jewelry-onhand-nightly-pull/SKILL.md"
bash "$BIN/install_skill.sh" jewelry-onhand-catchup "/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/a109d110/outputs/jewelry-onhand-catchup/SKILL.md"
