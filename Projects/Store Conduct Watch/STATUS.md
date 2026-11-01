# Store Conduct Watch — STATUS
Started 2026-10-31 (Joshua: "sure set it up" — daily camera watch for all 5 stores, morning report of the worst moments with clips).

## What it is
- **Recorder** `watch.py` per store (native `com.valleypawn.conductwatch-<store>`, Mon–Sat 09:55 → close+5, KeepAlive):
  streams each counter camera over the Nest SDM API (reuses `Store Traffic Counter/nest_stream.py`, read-only import),
  saves a still every 20 s and records 1280x720 @ 8 fps video + mono audio in 10-min .mkv segments.
  Data: `~/.vp-studio/conduct-watch/{frames,rec,transcripts,state}` (NOT in Projects — large). Retention: video 3 days, stills 14.
- **Nightly** `analyze.py` (`com.valleypawn.conductwatch-nightly`, Mon–Sat 19:20): screen (Haiku, 1 still/min contact sheets)
  → verify every flag (Sonnet, all 20-s stills) → local audio transcription (faster-whisper base.en) → cussing candidates judged
  with context → captioned clips with sound for severity ≥2. Output `reports/<date>/`.
- **Report** `report.py` (`com.valleypawn.conductwatch-report`, daily 07:35): one DM to Joshua, worst first, + up to 6 clips.
  Catch-up 3 days, duplicate guard, never posts an incomplete analysis.
- Wrappers: `Valley Pawn OS/bin/conduct_watch_{run,nightly,report,setup,probe}.sh`. Plists in `Valley Pawn OS/fleet/`.
- Go-live switches: `fleet/state/native_live/conductwatch-<store|nightly|report>`.

## Status
- 2026-10-31 14:10 LIVE (15-day trial to 2026-11-15, review 11/16). All 12 cameras recording; pipeline tested end-to-end (see CHANGELOG 2026-10-31).
- Health check any time: host queue job `bash ".../bin/conduct_watch_probe.sh" status` (per-camera stills/segments/reconnects, disk free).
- Test a store without touching the real nightly: `conduct_watch_nightly.sh <date> --store <S> [--no-audio] [--clip-test]` writes run.test-<S>.json only.
- 2026-10-31 18:50 Joshua: "we should be listening for cussing and abuse or bad customer service in the store as well". analyze.py now reads each store's whole-day transcript (both counter mics merged/deduped) in 150-line chunks with the fast model (CUSSING / RUDE TO CUSTOMER / ABUSE / BAD SERVICE / ARGUMENT / TALKING ABOUT CUSTOMER) + a profanity keyword net, then verifies each flag with ±90 s of transcript + the still (strong model). Caps: 300 screens, 30 visual verifies, 20 speech verifies per day.
- Roanoke test (10/31 PM): 7 audio findings (staff cussing during casual talk; 1 with a possible customer present = severity 2). Fixed: max_tokens raised (answers were truncated/empty → JSON errors); OpenCV person filter moved to its own process (people_filter.py) to avoid two FFmpeg copies in one process.
- LESSON: never edit a .sh wrapper while it is running (bash reads scripts incrementally — the 10/31 test run executed a garbled mix and kicked off the full nightly early). Edit .py files instead, or wait for the run to end.
- cleanup.py only deletes a day's raw video when run.json has version >= 2 (current code).
- 2026-10-31 21:20 v3 analyze: screen ALL cameras first, then verify round-robin across cameras (cap 36) and speech-verify round-robin across stores (cap 20) — v2 spent the whole budget on Culpeper and left 8 cameras unverified. Screener now requires a problem in 2+ consecutive tiles (except customer left alone / child behind counter / cash out); windows merged within 5 min. Clip fallback: photo slideshow from the 20-s stills when the raw video is gone. Re-ran 10/31: complete, 19 visual + 20 speech verifies, 1 finding (Lexington 2:13 PM cussing with a customer at the counter), est $1.02. 07:35 DM previewed with --render.
