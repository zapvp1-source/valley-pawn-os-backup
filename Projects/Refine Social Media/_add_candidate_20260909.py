#!/usr/bin/env python3
"""
_add_candidate_20260909.py — register ONE new video-lane candidate through the
drift engine's own novelty gate.

WHY (2026-09-09, vp-comedy-reel-weekly run):
  `creative_drift.py select --lane video --slots 4` printed
  "UNDER-FILL: 3/4 — registry is thin for lane=video in season=late_summer.
   Run `refresh` to queue new candidates."
  ...but `DriftEngine.refresh()` only RETIRES/RESTS and reports how many
  candidates are OWED — it does not create any. So the engine's own remedy is a
  no-op for this symptom. (`refresh` was also NOT run: only vid_deal_reel clears
  MIN_POSTS_FOR_SIGNAL, and refresh's decline check could have rested the deal-reel
  lane as a side effect. Not worth it for a report that adds nothing.)

  Meanwhile the two top-ranked video picks are both asset-blocked and have been
  since 8/26: vid_sixty_second_repair needs a before/after PHOTO PAIR that does
  not exist, and vid_closing_time needs fixed-camera store footage nobody has
  shot. That left exactly one renderable eligible format (vid_case_walk) against
  a 2-3 video/week lane target.

  This is the same disease SOCIAL_SYSTEM_SPEC §8 already flags for the community
  lane ("formats run dry mid-November at current cooldowns — top up
  creative_state.json"), arriving early in the video lane.

WHAT: adds `vid_where_it_went` — the sell-through mirror of vid_walked_in, built
from `<date>_<STORE>_sold-discount-detail.csv`, which the Bravo pipeline produces
for all 5 stores every single day. Renderable every week with zero new assets.

This is add_candidate(), NOT hand-promotion. Step 8 of the lane spec forbids
hand-promoting or hand-retiring on PERFORMANCE; inventing a candidate is the
quarterly clock's documented mechanism and it still passes is_novel().

Additive: appends one record. Backs up creative_state.json first. Idempotent —
re-running is a no-op once the id exists.
"""
import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from creative_drift import DriftEngine, Format, STATE_PATH  # noqa: E402

NEW_ID = "vid_where_it_went"

engine = DriftEngine()
if any(f.id == NEW_ID for f in engine.state["formats"]):
    print(f"SKIP: {NEW_ID} already registered")
    sys.exit(0)

shutil.copy2(STATE_PATH, str(STATE_PATH) + f".bak-{date.today().isoformat()}")

fmt = Format(
    id=NEW_ID,
    lane="video",
    pillar="Story",
    title="Where it all went this week",
    template=(
        "The sell-through mirror of 'what walked in'. A deadpan count of what left the "
        "counters in the last seven days, then four or five of them named by object and "
        "town, closing on the fact that every one of them is in somebody's house now. "
        "Built entirely from the daily sold-discount-detail CSVs. Firearms, ammunition "
        "and magazines are filtered out before a single line is written."
    ),
    hook_key=NEW_ID,
    seasons=[],
)

ok, why = engine.add_candidate(fmt)
if not ok:
    print(f"REJECTED by novelty gate: {why}")
    sys.exit(1)

engine.save()
print(f"ADDED {NEW_ID} (candidate, lane=video, pillar=Story) — novelty gate passed")
