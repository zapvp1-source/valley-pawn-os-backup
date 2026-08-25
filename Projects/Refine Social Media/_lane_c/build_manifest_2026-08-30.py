#!/usr/bin/env python3
"""Lane C (Community) — build the approved manifest for week of 2026-08-30.

Context: vp-community-weekly ran 2026-08-24. Verified against LIVE Publer output
(Rule 12) that the previous batch (built 2026-08-22, manifest_2026-08-22.json,
20 items / 4 per store) is already scheduled and confirmed through 2026-08-29 —
every store, FB + GBP, distinct captions. Re-shipping this week would stack posts
and burn cooldown budget prematurely, so this run instead stages the NEXT slate
(week of Aug 30 - Sept 5) using hooks that were NOT used in the prior batch
(45-day hook cooldown respected — see creative_drift.py select output).

19 community posts this round (Harrisonburg under-filled 3/4 by the drift engine
registry, ships 3 not 4 — noted, not overridden). Text-only by design.
"""
import json
from pathlib import Path

TZ = "-04:00"  # EDT

# (store, format_id, hook_label, day, time, fb_caption, gbp_caption)
POSTS = [
    # ---------------- HARRISONBURG (parity-weighted, first pick; UNDER-FILL 3/4 per drift engine) ----------------
    ("Harrisonburg", "com_college_town", "JMU Edith J. Carrier Arboretum & the Quad",
     "2026-08-30", "08:30",
     "Twenty-five minutes off campus and most people never make the trip. JMU's Edith J. Carrier "
     "Arboretum runs 125 acres, and it sits right next to the Quad, the part of campus that never "
     "really empties out even in the quiet hours. Classes are a few days in now and the Friendly "
     "City has its second population back for the season. Worth a walk if you have never gone.",
     "The JMU Edith J. Carrier Arboretum spans 125 acres adjacent to the university's Quad. Fall "
     "semester classes began August 26, and downtown Harrisonburg is back to its full seasonal pace "
     "with students returned."),

    ("Harrisonburg", "com_local_news_desk", "Blacks Run and the Northend Greenway",
     "2026-09-01", "08:30",
     "Most people who live here have crossed Blacks Run a hundred times without knowing its name. "
     "It is the six-mile creek that runs straight through downtown, and the Northend Greenway "
     "follows it out past Turner Pavilion. Not flashy, just quietly doing the work of a small-town "
     "waterway that most cities paved over decades ago. This one is still visible, still walkable.",
     "Blacks Run is the six-mile creek running through downtown Harrisonburg, followed for part of "
     "its length by the Northend Greenway near Turner Pavilion. It remains an open, walkable "
     "waterway through the center of the city."),

    ("Harrisonburg", "com_small_detail", "Lucy Simms mural, downtown Art Walk",
     "2026-09-03", "08:30",
     "Downtown's Art Walk has roughly thirty murals and mosaics, and the one worth slowing down for "
     "is the Lucy Simms mural. She taught more than 1,800 students over 56 years in Harrisonburg. "
     "The mural is easy to walk past if you are not looking. Once you know the story, it is hard to "
     "walk past it again.",
     "The Lucy Simms mural is part of downtown Harrisonburg's Art Walk, honoring the educator who "
     "taught more than 1,800 students over a 56-year career. It is one of roughly thirty murals and "
     "mosaics along the walk."),

    # ---------------- CULPEPER ----------------
    ("Culpeper", "com_college_town", "Germanna CC Daniel Technology Center",
     "2026-08-30", "09:45",
     "Culpeper is not a big campus town the way some of our other stores are, but Germanna Community "
     "College's Daniel Technology Center sits right downtown, and late August brings its own quiet "
     "version of back-to-term energy. Smaller crowd than a university town, same feeling. New "
     "notebooks, new schedules, same Piedmont light.",
     "Germanna Community College's Daniel Technology Center is located in downtown Culpeper. Late "
     "August brings the start of the fall term there, adding to the town's back-to-school rhythm."),

    ("Culpeper", "com_local_news_desk", "Round Hill Farm pumpkin patch opens Sept 28",
     "2026-09-01", "09:45",
     "Still a month out, but Round Hill Farm's pumpkin patch opens September 28 and runs through "
     "Halloween. Worth knowing now if you plan your fall weekends ahead of everybody else. Piedmont "
     "color comes late here, later than the mountain towns west of us, so the patch tends to still "
     "be in full swing when other places are already done.",
     "Round Hill Farm's pumpkin patch opens Monday, September 28, and runs through Halloween, "
     "October 31. Culpeper's Piedmont location means fall color and the patch season both run later "
     "here than in the mountain towns to the west."),

    ("Culpeper", "com_then_now", "Culpeper County Courthouse, 1870-74",
     "2026-09-03", "09:45",
     "The county courthouse downtown went up in 1870, right after the war, finished by 1874. It has "
     "been the same building doing the same job for a hundred and fifty years, through a downtown "
     "that has completely rebuilt itself around it more than once. Some buildings get preserved. "
     "This one just never stopped working.",
     "The Culpeper County Courthouse was built 1870-1874 and has continuously served as the county's "
     "courthouse since, anchoring downtown through more than a century and a half of change around "
     "it."),

    ("Culpeper", "com_small_detail", "The Trailblazers mural, E. Davis St",
     "2026-09-05", "09:45",
     "On East Davis, there is a mural called The Trailblazers, and it honors the historic Black "
     "community that once thrived down in The Wharf and Fishtown. Easy to drive past on the way "
     "somewhere else. Worth stopping the car for. Culpeper has a lot of history on that stretch of "
     "street, and this is the piece of it that is actually on the wall for everyone to see.",
     "The Trailblazers mural on East Davis Street in Culpeper honors the historic Black community "
     "of The Wharf and Fishtown neighborhoods. It stands in the downtown district near the buildings "
     "those communities once occupied."),

    # ---------------- WAYNESBORO ----------------
    ("Waynesboro", "com_college_town", "BRCC Waynesboro Outpost, 1010 E. Main",
     "2026-08-30", "11:00",
     "Not a university town, but Blue Ridge Community College runs a Waynesboro Outpost right on "
     "East Main, and late August means a new semester there too. Smaller than the JMUs and VMIs of "
     "the world, same first-week feeling. New parking patterns downtown for a few weeks while "
     "everybody relearns their route.",
     "Blue Ridge Community College operates a Waynesboro Outpost at 1010 E. Main Street. The fall "
     "term begins in late August, adding student traffic to downtown for the first few weeks of the "
     "semester."),

    ("Waynesboro", "com_local_news_desk", "Appalachian Trail Community status, hiker season",
     "2026-09-01", "11:00",
     "Waynesboro is an official Appalachian Trail Community, one of the reasons being that hikers "
     "actually come down off the ridge and into town, not just past it. Free showers at the YMCA, a "
     "hiker campsite on Race Ave, hostels that know exactly what a thru-hiker needs by this point in "
     "the season. Late-season hikers are still coming through right now.",
     "Waynesboro holds an official Appalachian Trail Community designation. The town offers hiker "
     "services including free YMCA showers and a hiker campsite on Race Avenue, with thru-hikers "
     "still passing through in late summer."),

    ("Waynesboro", "com_then_now", "Wayne Theatre, 521 W. Main",
     "2026-09-03", "11:00",
     "The Wayne Theatre on West Main has its 2026-27 season lined up now, titled \"For the Love.\" "
     "It is the kind of venue a lot of towns this size lost decades ago and never got back. "
     "Waynesboro kept theirs, restored it, and it is still doing the job a downtown theater is "
     "supposed to do.",
     "The Wayne Theatre at 521 W. Main Street has announced its 2026-27 season, titled \"For the "
     "Love.\" The restored downtown venue continues to anchor Waynesboro's arts programming."),

    ("Waynesboro", "com_market_day", "Craft Sublime Harvest Market, Weds through Sept 30",
     "2026-09-05", "11:00",
     "Wednesdays through the end of September, the Craft Sublime Harvest Market is worth building an "
     "afternoon around. Late-summer produce, local makers, the kind of market that does not need a "
     "big production to be good. A few weeks left before it wraps for the season.",
     "The Craft Sublime Harvest Market runs Wednesdays through September 30 in Waynesboro, featuring "
     "local produce and makers. The market season is in its final weeks."),

    # ---------------- LEXINGTON ----------------
    ("Lexington", "com_college_town", "Two colleges, one walkable downtown",
     "2026-08-30", "14:00",
     "Seven thousand people, two colleges, one downtown you can walk end to end. VMI and W&L sit a "
     "few blocks apart and share the same Main Street businesses have built around for two centuries. "
     "Not many towns this size pull that off without one school swallowing the whole identity of the "
     "place.",
     "Lexington, population roughly 7,000, is home to both Virginia Military Institute and "
     "Washington and Lee University, a few blocks apart within one walkable historic downtown."),

    ("Lexington", "com_local_news_desk", "Hull's Drive-In, still running through late October",
     "2026-09-01", "14:00",
     "Hull's Drive-In is still running, 319 spaces, one of only two nonprofit community-owned "
     "drive-ins left in the entire country, and it has been since 1950. Season usually runs to the "
     "end of October. If you have never been, there are still weekends left before it closes for "
     "the year.",
     "Hull's Drive-In in Lexington, one of only two nonprofit community-owned drive-in theaters in "
     "the country, remains open with its season typically running through late October."),

    ("Lexington", "com_then_now", "Alexander-Withrow House, 1789",
     "2026-09-03", "14:00",
     "The Alexander-Withrow House has stood since 1789, which means it predates almost everything "
     "else standing in Lexington today. It is easy to walk past a building that old without clocking "
     "what it actually is. Main Street carries a lot of that kind of history, quietly, without much "
     "fanfare about it.",
     "The Alexander-Withrow House, built in 1789, is one of the oldest standing structures in "
     "downtown Lexington, located along Main Street."),

    ("Lexington", "com_market_day", "Lexington Farmers Market, Weds through Nov 26",
     "2026-09-05", "14:00",
     "Wednesdays, right through Thanksgiving week. Late summer is the market at its fullest: "
     "tomatoes, corn, the last of the peaches. Higher elevations around Lexington start turning "
     "before the town does, so market mornings are a good early read on how fall is coming along.",
     "The Lexington Farmers Market runs Wednesdays through November 26. Late summer brings peak "
     "produce, and the surrounding higher elevations typically show fall color before the town "
     "itself."),

    # ---------------- ROANOKE ----------------
    ("Roanoke", "com_college_town", "Hollins University",
     "2026-08-30", "16:30",
     "Roanoke is not a campus town the way Lexington or Harrisonburg are, but Hollins University "
     "sits right inside city limits, and Virginia Tech is close enough down the road that the whole "
     "Valley feels it on a Saturday. Two different kinds of college energy, same region, same time "
     "of year.",
     "Hollins University is located within Roanoke city limits. Virginia Tech, roughly 40 minutes "
     "away in Blacksburg, also contributes to the region's college-town rhythm each fall."),

    ("Roanoke", "com_local_news_desk", "Carvins Cove, 60+ miles of trail",
     "2026-09-01", "16:30",
     "Carvins Cove is the second-largest municipal park in the entire country, about twelve thousand "
     "acres and more than sixty miles of trail, and it sits right at the edge of the city. Locals "
     "just call it the Cove. Late summer mornings out there are still some of the best trail time of "
     "the year before it gets crowded for foliage season.",
     "Carvins Cove Natural Reserve covers roughly 12,000 acres with more than 60 miles of trail, and "
     "is the second-largest municipal park in the United States. It borders the city of Roanoke."),

    ("Roanoke", "com_then_now", "Hotel Roanoke, 1882 Tudor railroad hotel",
     "2026-09-03", "16:30",
     "Hotel Roanoke went up in 1882, the same year the railroad turned this place from about seven "
     "hundred people into five thousand in two years flat. Tudor-style, built by the railroad, still "
     "standing, still the same address it has always had. The whole Star City story basically starts "
     "at that building.",
     "Hotel Roanoke opened in 1882 as a Tudor-style railroad hotel, built the same year the Norfolk "
     "and Western Railway arrived and rapidly grew the town's population. It remains a landmark "
     "downtown."),

    ("Roanoke", "com_market_day", "Historic City Market, open year-round since 1882",
     "2026-09-05", "16:30",
     "The Historic City Market has been running since 1882, the oldest continuously operating "
     "open-air market in Virginia, open every day of the year except Christmas and New Year's. "
     "Friday and Saturday mornings are the ones locals actually plan around. If you have not been "
     "down there on a Saturday, that is the one to catch.",
     "Roanoke's Historic City Market has operated continuously since 1882, making it the oldest "
     "open-air market in Virginia. It is open year-round, closed only on Christmas and New Year's "
     "Day, with Friday and Saturday mornings drawing the heaviest crowds."),
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
        "batch_id": "vp-community-weekly-2026-08-30",
        "lane": "C-community",
        "generated": "2026-08-24",
        "note": "Text-only by design. Community posts carry no product photo and never wait on "
                "the image pipeline. No CTA, no product, no price. Distinct caption per channel. "
                "Staged for week of Aug 30 - Sept 5 because Rule-12 verification against live "
                "Publer output showed the prior batch (manifest_2026-08-22.json) already fully "
                "scheduled through 2026-08-29 across all 5 stores.",
        "items": items,
    }
    out = Path(__file__).with_name("manifest_2026-08-30.json")
    out.write_text(json.dumps(manifest, indent=2))
    print(f"{len(items)} items -> {out}")


if __name__ == "__main__":
    build()
