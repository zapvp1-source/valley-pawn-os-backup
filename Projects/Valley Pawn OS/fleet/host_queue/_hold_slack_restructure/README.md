Slack Restructure (2026-11-09) — held jobs.
- `rerun-setup.sh`: re-runs `slack_restructure_phase2.py setup` (idempotent) once the Goldilocks app has channels:manage,
  channels:write.topic, groups:write, bookmarks:write, pins:write (HUMAN_QUEUE 2026-11-09). Drop it into fleet/host_queue/.
- `archive.sh`: archives the 23 merged-away channels. Drop it into fleet/host_queue/ after the parallel week (Mon 2026-11-16
  check does this automatically when the scopes are in place).
