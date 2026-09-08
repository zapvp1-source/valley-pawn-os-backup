#!/usr/bin/env python3
"""
Lane C — vp-community-weekly manifest for the week of Sept 13-19, 2026.

Rule-12 check before building: GET /posts?from=2026-09-06&to=2026-09-21&state=scheduled
returned 76 posts, every one of them on Sept 7-12. Nothing scheduled Sept 13 onward across
any lane. The prior Lane C batch (manifest_2026-09-06.json, generated 2026-08-31) already
owns the week of Sept 6-12 in full (40 items, all published, corroborated independently by
the 2026-09-07 vp-deal-reels-weekly run finding a live Waynesboro FB collision at 11:00am
9/9 against this exact batch). This batch is the next one in sequence, built on the
established ~1-week-ahead cadence (each Monday's Lane C run builds the following
not-yet-covered week).

Formats chosen by `creative_drift.py select --lane community --slots 4` run once per store
account on 2026-09-07:
  Harrisonburg: com_early_shift (NEW), com_mural_corner (NEW), com_school_colors (n=1), com_trailhead (n=2)
  Culpeper:     com_mural_corner (NEW), com_early_shift (NEW), com_school_colors (n=1), com_trailhead (n=2)
  Waynesboro:   com_early_shift (NEW), com_mural_corner (NEW), com_trailhead (n=2), com_park_hour (n=2)
  Lexington:    com_mural_corner (NEW), com_early_shift (NEW), com_school_colors (n=1), com_park_hour (n=2)
  Roanoke:      com_mural_corner (NEW), com_early_shift (NEW), com_school_colors (n=1), com_park_hour (n=2)

Landmark-level 45-day check done by hand against all three prior manifests (08-22, 08-30,
09-06) before writing captions -- every specific landmark below is NEW to its store within
the last 45 days. Where the KB had no second mural on file (Culpeper, Lexington, Roanoke all
had only one mural each, already used), fresh ones were verified via web search against
official/tourism sources (never a generic search hit) and appended to CITY_COMMUNITY_KB.md:
  - Culpeper: "The Surveyor" mural, W. Cameron & Main (culpeperdowntown.com)
  - Lexington: "Millinery De Rousselot" mural, Main & Washington -- deliberately framed
    around the film-location angle only, no Civil War/Reconstruction detail, per the
    hard exclusion on Lexington Confederate-adjacent content (explore.lexingtonvirginia.com)
  - Roanoke: "Greetings from Roanoke" postcard mural, S Jefferson St (downtownroanoke.org)
Also verified and rejected: Lake Culpeper has NO trail/bank access (VA DWR) -- would have
been a wrong-detail post for Culpeper's com_trailhead. Used Old Rag (~20 mi via Sperryville
Pike, multiple hiking-guide sources) instead, framed honestly as a real drive, not a stroll.

Text-only by design, same as every Lane C batch. No CTA, no product, no price, no
competitor or private-individual names. Distinct caption per channel. Harrisonburg gets
first pick and the earliest slots (parity rule) -- still not at parity with Culpeper, so it
keeps first pick again this round.
"""
import json
from pathlib import Path

TZ = "-04:00"

# store, format_id, hook, date, HH:MM (FB), facebook caption, GBP caption
POSTS = [

    # ---------------- HARRISONBURG (first pick - parity rule) ----------------
    ("Harrisonburg", "com_early_shift", "Poultry trucks and the Dayton Market",
     "2026-09-13", "08:30",
     "Rockingham County leads the state in poultry production, and that means the trucks "
     "are moving through here well before most of Harrisonburg is awake. By the time "
     "downtown Court Square stirs, the vendors out at the Dayton Market have already been "
     "open for hours. Two different versions of the same morning, running on two different "
     "clocks.",
     "Rockingham County leads Virginia in poultry production, with truck traffic moving "
     "through the area well before sunrise. The Dayton Farmers Market, west of Harrisonburg, "
     "is typically open and active well ahead of downtown's own morning start."),

    ("Harrisonburg", "com_mural_corner", "The chess-player mural, downtown Art Walk",
     "2026-09-15", "08:30",
     "One corner of the downtown Art Walk gets overlooked because it's four stories up: a "
     "mural of a chess player, towering over the block. Harrisonburg's Art Walk runs to "
     "about thirty pieces total, and this is the one that makes people stop mid-step and "
     "actually look up.",
     "Harrisonburg's downtown Art Walk includes roughly 30 murals, mosaics, and sculptures, "
     "among them a four-story mural depicting a chess player, visible above street level in "
     "the downtown core."),

    ("Harrisonburg", "com_school_colors", "Blue Streaks",
     "2026-09-17", "08:30",
     "Navy, red and white, and the Blue Streaks are back at it this fall. Harrisonburg High "
     "School, out doing what Friday nights in this town are built around. Good luck out "
     "there this season.",
     "Harrisonburg High School's athletic teams are the Blue Streaks, competing in navy, "
     "red, and white."),

    ("Harrisonburg", "com_trailhead", "Reddish Knob, the drive worth taking",
     "2026-09-19", "08:30",
     "Reddish Knob isn't a walk from anywhere near the store. It's a real drive, up a "
     "one-lane road called Briery Branch, and the last stretch is gravel. But at 4,397 feet "
     "it's the highest point around, and it is genuinely the spot people in this town mean "
     "when they talk about going up the mountain for sunrise or to see the stars. Not a "
     "stroll. Worth the drive anyway.",
     "Reddish Knob, at 4,397 feet, is accessible via the one-lane Briery Branch Road outside "
     "Harrisonburg. It is a popular local destination for sunrise, sunset, and stargazing, "
     "though the final approach includes unpaved sections."),

    # ---------------- CULPEPER ----------------
    ("Culpeper", "com_early_shift", "Piedmont fields before the shops open",
     "2026-09-14", "09:30",
     "Piedmont fog sits low over the fields outside Culpeper longer than people expect, and "
     "it is usually still holding when the first farm trucks head into town on Route 29. By "
     "the time Davis Street's shops unlock their doors, that fog has already burned off and "
     "the morning feels like a different day entirely.",
     "Fields surrounding Culpeper, part of Virginia's Piedmont region, often hold morning "
     "fog later than downtown, which typically clears well before local shops open."),

    ("Culpeper", "com_mural_corner", "The Surveyor, West Cameron and Main",
     "2026-09-16", "09:30",
     "There's a mural at West Cameron and Main of George Washington as a young surveyor, "
     "larger than life on the side of a building. It's the first one of Culpeper's downtown "
     "mural program, painted back in 2017, and it ties right back to the same surveys "
     "Washington ran through this county as a teenager. The town remembered that fact and "
     "put it on a wall.",
     "\"The Surveyor,\" a mural depicting a young George Washington, is located at the "
     "corner of West Cameron and Main Streets in downtown Culpeper. Completed in 2017 by "
     "artists Tom and Kerri Mullany, it references Washington's early surveying work in the "
     "area."),

    ("Culpeper", "com_school_colors", "Blue Devils",
     "2026-09-18", "09:30",
     "Blue and gold, and the Culpeper County Blue Devils are into the season. Fall Fridays "
     "around here mean the lights are on at the stadium. Good luck this year, Blue Devils.",
     "Culpeper County High School's athletic teams are the Blue Devils, competing in blue "
     "and gold."),

    ("Culpeper", "com_trailhead", "Old Rag, about 20 miles out",
     "2026-09-19", "09:30",
     "The closest real hiking most people in Culpeper actually do is about 20 miles out, up "
     "the Sperryville Pike, at Old Rag. It's not a walk. It's a real scramble over rock near "
     "the summit, and it draws people from all over, not just here. But when somebody from "
     "Culpeper says they're going hiking this weekend, there's a good chance that's where "
     "they mean.",
     "Old Rag Mountain, a popular hiking destination in Shenandoah National Park, is located "
     "approximately 20 miles from Culpeper via the Sperryville Pike. The hike includes a "
     "rock scramble near the summit and is considered strenuous."),

    # ---------------- WAYNESBORO ----------------
    ("Waynesboro", "com_early_shift", "The hiker campsite on Race Ave",
     "2026-09-14", "11:15",
     "Before six most mornings, the thru-hikers who spent the night at the free campsite on "
     "Race Ave are already breaking down their tents. Waynesboro is an official Appalachian "
     "Trail Community, and that hiker rhythm, tents down before the town's even up, is a "
     "real part of what that means here.",
     "Waynesboro is a designated Appalachian Trail Community and maintains a free hiker "
     "campsite on Race Avenue, used by thru-hikers passing through the area."),

    ("Waynesboro", "com_mural_corner", "The Lovers, at the YMCA",
     "2026-09-16", "11:15",
     "Part of Waynesboro's Street Arts Trail lives on a wall at the YMCA: a piece called The "
     "Lovers, by artist Julia Chon. It doesn't get the attention Kaiya with Tulips gets "
     "downtown, but it's one more reason this became a genuine arts-trail town instead of "
     "just a former manufacturing one.",
     "\"The Lovers,\" a mural by artist Julia Chon, is located at the YMCA in Waynesboro as "
     "part of the city's Street Arts Trail."),

    ("Waynesboro", "com_trailhead", "Humpback Rocks, Parkway Milepost 5.8",
     "2026-09-18", "11:15",
     "The closest real trail out of Waynesboro is Humpback Rocks, right where the Blue Ridge "
     "Parkway starts at Milepost 0 and climbs from there. It's a genuine climb to the "
     "outcrop at around 3,080 feet, not a flat walk, but the view at the top is the kind "
     "that makes people who complained on the way up go quiet for a minute.",
     "Humpback Rocks, located near Blue Ridge Parkway Milepost 5.8 close to Waynesboro, "
     "features a rock outcrop at approximately 3,080 feet with a moderately strenuous trail "
     "to the summit."),

    ("Waynesboro", "com_park_hour", "Constitution Park, the quiet option",
     "2026-09-19", "11:15",
     "Constitution Park doesn't get talked about the way the Greenway does, but it's worth "
     "knowing about for the same reason: somewhere in this town to be outside without a "
     "plan. Early evening, once the heat of the day lets go, is the right time for it.",
     "Constitution Park in Waynesboro offers a quieter alternative to the South River "
     "Greenway, particularly in the early evening hours."),

    # ---------------- LEXINGTON ----------------
    ("Lexington", "com_early_shift", "The Keydets, before six",
     "2026-09-13", "15:00",
     "By six most mornings, the Keydets are already outside. Early physical training is "
     "just part of life at the Institute, and it means Lexington has a version of itself "
     "that most of the town never sees: cadets moving through the dark well before the "
     "coffee shops on Main Street unlock.",
     "Early morning physical training is a standard part of cadet life at Virginia Military "
     "Institute (VMI) in Lexington, typically beginning well before sunrise."),

    ("Lexington", "com_mural_corner", "Millinery De Rousselot, Main and Washington",
     "2026-09-15", "15:00",
     "There's a mural on the corner of Main and Washington that most people walk past "
     "without knowing the story: it was painted for a movie shot right here in 1992, and "
     "downtown Lexington barely had to change a thing to stand in for the past. The mural "
     "stayed long after the film crews left.",
     "The Millinery De Rousselot mural, at the corner of Main and Washington Streets in "
     "downtown Lexington, was created in 1992 for a film production that used the town's "
     "historic downtown as a filming location."),

    ("Lexington", "com_school_colors", "Wildcats",
     "2026-09-17", "15:00",
     "Blue, silver and white, and the Rockbridge County Wildcats are underway this fall. "
     "One of two football programs this town follows closely, and Friday nights make that "
     "clear. Good luck this season, Wildcats.",
     "Rockbridge County High School's athletic teams are the Wildcats, competing in blue, "
     "silver, and white."),

    ("Lexington", "com_park_hour", "Woods Creek Trail, the other option",
     "2026-09-18", "15:00",
     "Woods Creek Trail doesn't get the attention the Chessie does, but it's the quieter "
     "walk, closer to town, and it holds its own kind of good hour. Late afternoon, when "
     "the light gets long, is when it's at its best.",
     "Woods Creek Trail in Lexington offers a walking route closer to downtown than the "
     "Chessie Nature Trail, with late afternoon typically providing the most favorable "
     "light and temperature."),

    # ---------------- ROANOKE ----------------
    ("Roanoke", "com_early_shift", "The fog the valley holds onto",
     "2026-09-14", "16:30",
     "The Roanoke Valley holds its morning fog longer than towns out on flatter ground, "
     "ringed the way it is by mountains on every side. By the time it burns off, downtown "
     "is already awake, but for a little while it's just the mountains and the quiet.",
     "The Roanoke Valley, surrounded by mountains on multiple sides, is known for morning "
     "fog that typically persists longer than in surrounding flatter areas before clearing."),

    ("Roanoke", "com_mural_corner", "Greetings from Roanoke, S Jefferson St",
     "2026-09-16", "16:30",
     "There's a postcard painted on the side of a building on South Jefferson Street, and "
     "the letters spelling out ROANOKE are filled in with the actual landmarks: the Star, "
     "the Market building, the Taubman, Hotel Roanoke. It is one of the most photographed "
     "walls in the city, and it earns it.",
     "\"Greetings from Roanoke,\" a postcard-style mural on South Jefferson Street in "
     "downtown Roanoke, depicts local landmarks including Mill Mountain Star, the City "
     "Market Building, the Taubman Museum of Art, and Hotel Roanoke."),

    ("Roanoke", "com_school_colors", "Patriots",
     "2026-09-17", "16:30",
     "Purple and gold, and Patrick Henry is back at it this fall. It's the PH side of the "
     "oldest rivalry in the city, and this time of year that rivalry is most of what people "
     "are talking about on Friday. Good luck out there this season.",
     "Patrick Henry High School's athletic teams are the Patriots, competing in purple and "
     "gold."),

    ("Roanoke", "com_park_hour", "Elmwood Park, downtown's best hour",
     "2026-09-19", "16:30",
     "Elmwood Park sits right in the middle of downtown, and early evening is when it earns "
     "that spot. The heat breaks, the market crowd thins out, and it turns into the kind of "
     "park you'd actually want to sit in instead of just walk through.",
     "Elmwood Park, located in downtown Roanoke, is well suited to early evening visits "
     "once daytime temperatures ease."),
]


def build():
    items = []
    for store, fmt, hook, day, hhmm, fb, gbp in POSTS:
        base = f"{day.replace('-', '')}-{store.lower()}-{fmt}"
        items.append({
            "id": f"{base}-fb",
            "routing_tier": "store-local",
            "store_keys": [store],
            "caption": fb,
            "scheduled_at": f"{day}T{hhmm}:00{TZ}",
            "status": "approved",
            "_lane": "community",
            "_format_id": fmt,
            "_hook": hook,
        })
        h, m = int(hhmm[:2]), int(hhmm[3:])
        m += 90
        h += m // 60
        m %= 60
        items.append({
            "id": f"{base}-gbp",
            "routing_tier": "store-local",
            "store_keys": [f"GBP_{store}"],
            "caption": gbp,
            "scheduled_at": f"{day}T{h:02d}:{m:02d}:00{TZ}",
            "status": "approved",
            "_lane": "community",
            "_format_id": fmt,
            "_hook": hook,
        })
    manifest = {
        "batch_id": "vp-community-weekly-2026-09-13",
        "lane": "C-community",
        "generated": "2026-09-07",
        "note": "Week of Sept 13-19. Text-only by design. Formats from creative_drift.py select "
                "(4 slots/store). Three stores' mural_corner picks required a freshly verified "
                "second mural (Culpeper, Lexington, Roanoke each had only one mural on file in "
                "CITY_COMMUNITY_KB.md and it was already used within the 45-day window) -- new "
                "ones sourced from official/tourism sites and appended to the KB. Lake Culpeper "
                "was checked and rejected for com_trailhead (VA DWR confirms no trail/bank "
                "access) in favor of Old Rag, correctly distanced at ~20 mi via Sperryville Pike.",
        "items": items,
    }
    out = Path(__file__).with_name("manifest_2026-09-13.json")
    out.write_text(json.dumps(manifest, indent=2))
    print(f"{len(items)} items -> {out}")


if __name__ == "__main__":
    build()
