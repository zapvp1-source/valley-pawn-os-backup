#!/usr/bin/env python3
"""
Lane C registry top-up — 2026-08-31.

WHY: `creative_drift.py select --lane community` returned ZERO eligible formats for
all 5 stores this week. Diagnosis (verified against creative_state.json + the engine
source, not inferred):

  - The community lane holds 10 formats.
  - 7 are season-agnostic; all 7 were used on all 5 store accounts on 2026-08-24.
    COOLDOWN_FORMAT_DAYS = 21, so they are ineligible until ~2026-09-14.
  - The other 3 (com_friday_lights, com_first_cold, com_foliage_timing) are gated to
    early_fall / peak_fall. Today's season is late_summer.

  => 7 in-season formats cannot sustain a weekly 4-slot lane against a 21-day
     cooldown. The lane needs >= 12 in-season community formats to never run dry.

FIX (additive only, per Rule 4): append NEW candidate formats to the registry.
Nothing existing is edited, and creative_drift.py is not touched. The engine still
does all the selecting — this only gives it something legal to select.
"""
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path("/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media")
STATE = ROOT / "creative_state.json"
TODAY = date.today().isoformat()

# id, title, template, seasons
NEW = [
    ("com_under_your_feet", "Under your feet",
     "One true thing about the ground downtown - brick, cobble, a curb stone, an old "
     "rail spur - and why it is there. No CTA, no product.", []),
    ("com_the_water", "The water that runs through it",
     "The creek or river that runs through this specific town, and what it is doing "
     "this week. Name it the way locals name it.", []),
    ("com_the_tracks", "Where the tracks go",
     "This town's railroad line, past or present, and what it built here. One "
     "verifiable detail, no romance beyond the facts.", []),
    ("com_trailhead", "The trailhead nearest us",
     "The closest real trail to this store, described honestly - distance, difficulty, "
     "what you actually see. Never oversell it.", []),
    ("com_early_shift", "Who is up first",
     "The 6am version of this town. Respectful, no names, no product. Punch at nothing.", []),
    ("com_school_colors", "Our colors",
     "The local high school's mascot and colors and one true thing about the school. "
     "Wish them a good season. Nothing else.", []),
    ("com_mural_corner", "One corner of one mural",
     "A single detail from one specific local mural or public artwork, and who made it.", []),
    ("com_park_hour", "The good hour at the park",
     "One local park and the hour of day it is best. Weather and light, not amenities.", []),
    ("com_last_warm_evening", "Last warm evenings",
     "What people in this town do with the last warm evenings before the season turns.",
     ["late_summer"]),
]


def main() -> int:
    bak = STATE.with_suffix(f".json.bak-pre-topup-{TODAY}")
    shutil.copy2(STATE, bak)

    state = json.loads(STATE.read_text())
    existing = {f["id"] for f in state["formats"]}

    added = []
    for fid, title, template, seasons in NEW:
        if fid in existing:
            continue
        state["formats"].append({
            "id": fid,
            "lane": "community",
            "pillar": "Community",
            "title": title,
            "template": template,
            "status": "candidate",
            "seasons": seasons,
            "hook_key": fid,
            "created": TODAY,
            "posts": 0,
            "engagement_total": 0.0,
            "reach_total": 0.0,
            "peak_index": 0.0,
            "last_used": {},
            "notes": f"[topup]{TODAY} added because the community lane returned zero "
                     f"eligible formats for all 5 stores (21-day cooldown + seasonal gating).",
        })
        added.append(fid)

    tmp = STATE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE)

    print(f"backup: {bak.name}")
    print(f"added {len(added)}: {', '.join(added)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
