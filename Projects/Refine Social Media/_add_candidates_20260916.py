#!/usr/bin/env python3
"""
_add_candidates_20260916.py — register TWO new candidates through the drift
engine's own novelty gate (vp-comedy-reel-weekly, 2026-09-16 run).

WHY: `select --lane humor --slots 1 --account Brand` returned "no eligible
formats" (all 4 humor bits inside COOLDOWN_HUMOR_DAYS=60; earliest clears
~2026-10-21). `select --lane video --slots 2 --account Brand` returned ONLY the
two long-standing asset-blocked candidates (vid_sixty_second_repair needs a
before/after photo pair, vid_closing_time needs fixed-camera Saturday footage) —
both asked for in #vp-studio-queue on 8/26 and again 9/9, neither shot. Every
card-renderable video format (vid_walked_in 9/07, vid_one_object 9/02,
vid_case_walk 9/09, vid_where_it_went 9/09) is inside the 21-day per-account
format cooldown on Brand.

That is ZERO renderable formats against a 2-3 video/week lane target, and a
second consecutive week with no humor at all in a lane whose whole reason for
existing is comedy for engagement.

This is add_candidate(), NOT hand-promotion. Lane spec Step 8 forbids promoting
or retiring on PERFORMANCE; inventing candidates is the documented mechanism and
both still have to pass is_novel().

Additive. Backs up creative_state.json. Idempotent.
"""
import shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path("/sessions/serene-relaxed-cerf/mnt/Refine Social Media")
sys.path.insert(0, str(ROOT))
from creative_drift import DriftEngine, Format, STATE_PATH  # noqa: E402

NEW = [
    Format(
        id="hum_system_says",
        lane="humor",
        pillar="Humor",
        title="What the computer calls it",
        template=(
            "Deadpan roll-call of how our own point-of-sale system describes real "
            "inventory, quoted verbatim in its own all-caps shorthand -- WRENCHES "
            "WRENCH SET, CLAMP CRIMPERS, SONY MISC ITEM. The joke punches at the "
            "catalog and at the objects, never at a person. Built from any "
            "inventory CSV the Bravo pipeline already emits daily. Firearms, "
            "ammunition and magazines filtered out before a line is written."
        ),
        hook_key="hum_system_says",
        seasons=[],
    ),
    Format(
        id="vid_still_here",
        lane="video",
        pillar="Story",
        title="Longest resident on the shelf",
        template=(
            "Quiet count of the oldest things in the building -- items named by "
            "object, town and the year they came in, oldest last. No prices pushed, "
            "no CTA. Built from the daily markdown-verification CSVs, which carry "
            "an intake date per item for all five stores. Firearms, ammunition and "
            "magazines filtered out before a line is written."
        ),
        hook_key="vid_still_here",
        seasons=[],
    ),
]

engine = DriftEngine()
existing = {f.id for f in engine.state["formats"]}
todo = [f for f in NEW if f.id not in existing]
if not todo:
    print("SKIP: both already registered"); sys.exit(0)

shutil.copy2(STATE_PATH, str(STATE_PATH) + f".bak-{date.today().isoformat()}")
for fmt in todo:
    ok, why = engine.add_candidate(fmt)
    print(("ADDED " if ok else "REJECTED ") + fmt.id + ("" if ok else f" :: {why}"))
    if not ok:
        sys.exit(1)
engine.save()
print("saved")
