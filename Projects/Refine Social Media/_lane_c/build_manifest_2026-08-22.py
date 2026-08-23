#!/usr/bin/env python3
"""Lane C (Community) — build the approved manifest for week of 2026-08-23.

20 community posts (4 per store), each routed to that store's FB page AND that
store's GBP with a genuinely different caption. Text-only by design: community
posts carry no product photo and must never wait on the image pipeline.
"""
import json
from pathlib import Path

TZ = "-04:00"  # EDT

# (store, format_id, hook_label, day, time, fb_caption, gbp_caption)
POSTS = [
    # ---------------- HARRISONBURG (parity-weighted, first pick) ----------------
    ("Harrisonburg", "com_landmark_morning", "Rockingham County Courthouse / Court Square",
     "2026-08-23", "08:30",
     "The clock tower on Court Square has been keeping time since 1897, and the figure standing up "
     "top is Justice. Here's the part most people never hear: it's the fifth courthouse to stand on "
     "that same square, and there's been one there since 1778. Walk to the southwest corner and the "
     "old springhouse is still tucked in behind the hedge. Late August light hits that dome around "
     "eight in the morning and it is worth being downtown for.",
     "The Rockingham County Courthouse has anchored Court Square since 1896-97, with a figure of "
     "Justice above the clock tower. It is the fifth courthouse to stand on that site since 1778, "
     "and the historic springhouse still sits in the southwest corner of the square."),

    ("Harrisonburg", "com_local_calendar", "JMU fall classes begin Wed Aug 26",
     "2026-08-25", "08:30",
     "Rocktown gets its second population back tomorrow. JMU's fall classes start Wednesday, which "
     "means Port Republic Road turns into a parking lot, every coffee shop downtown grows a line, "
     "and the Quad stops being quiet. Some folks dread the week. We have always kind of liked it. "
     "The Friendly City is at its friendliest when it is full. Welcome back, Dukes.",
     "JMU fall semester classes begin Wednesday, August 26. Downtown Harrisonburg and the Court "
     "Square area get noticeably busier this week as students return, with heavier traffic along "
     "Port Republic Road and East Market Street."),

    ("Harrisonburg", "com_local_word", "Rocktown / the Friendly City",
     "2026-08-27", "08:30",
     "Two nicknames, and locals use both without thinking about it. Rocktown comes from the "
     "limestone this whole valley floor sits on, the same rock that gave Rockingham County its name "
     "and gives the Rocktown Trails out at Hillandale their bite. The Friendly City is the older "
     "one, and it is the one people move here skeptical about and then quietly find out is true. "
     "You will hear both in the same conversation.",
     "Harrisonburg answers to two names. Rocktown comes from the limestone bedrock beneath the "
     "city, the same rock behind Rockingham County's name and the Rocktown Trails at Hillandale "
     "Park. The Friendly City is the older nickname and still the one used with visitors."),

    ("Harrisonburg", "com_market_day", "Harrisonburg Farmers Market, Tue + Sat through Nov 26",
     "2026-08-29", "08:30",
     "Saturday morning at the market is the best hour of the Harrisonburg week and it is not close. "
     "Late August is the peak of it: tomatoes, peppers, sweet corn, and the first quiet hint that "
     "apples are coming. It runs Tuesdays and Saturdays and keeps going all the way to "
     "Thanksgiving, so there is no rush. Go early anyway. The good stuff moves.",
     "The Harrisonburg Farmers Market runs Tuesdays and Saturdays through Thanksgiving, November "
     "26. Late August is peak season, with sweet corn, tomatoes and peppers now and early apples "
     "not far behind. Mornings are the busiest stretch."),

    # ---------------- CULPEPER ----------------
    ("Culpeper", "com_landmark_morning", "the Depot, 111 Commerce St (1904)",
     "2026-08-23", "09:45",
     "The Depot at 111 Commerce has been standing since 1904, and here is the part that surprises "
     "people who move here: it is not a museum. Amtrak still stops there. Trains still pull in, "
     "people still step off with bags, and the building is doing in 2026 exactly what Southern "
     "Railway put it up to do in 1904. Culpeper has a lot of old buildings. That is the one still "
     "working.",
     "The Culpeper Depot at 111 Commerce Street was built in 1904 as a Southern Railway station and "
     "remains an active Amtrak stop today, not a preserved museum. It anchors the east end of the "
     "downtown district."),

    ("Culpeper", "com_local_word", "Tin Cup Alley, Slabtown, The Wharf, Fishtown",
     "2026-08-25", "09:45",
     "Ask somebody who grew up here where Tin Cup Alley is and they will point you to East Spencer "
     "without missing a beat. Ask a map and you will get nothing. Culpeper is full of those: "
     "Slabtown, The Wharf, and Fishtown down on lower East Davis, named for the Friday fish fries. "
     "One more thing you learn fast around here. The Town of Culpeper and Culpeper County are two "
     "different things, and people will tell you so.",
     "Culpeper carries a set of names you will not find on a map: Tin Cup Alley for East Spencer "
     "Street, Slabtown, and The Wharf and Fishtown on lower East Davis, the last named for its "
     "Friday fish fries. Locals also draw a firm line between the Town of Culpeper and Culpeper "
     "County."),

    ("Culpeper", "com_local_calendar", "Fall Restaurant Week Sept 29 - Oct 5",
     "2026-08-27", "09:45",
     "Worth getting on the calendar now: Culpeper Fall Restaurant Week runs September 29 through "
     "October 5. Davis Street did not win Great American Main Street back in 2012 on architecture "
     "alone. The food is a real part of why downtown works. Still a month out, but that week fills "
     "up, and the people who plan ahead eat better.",
     "Culpeper Fall Restaurant Week runs September 29 through October 5, 2026 across the downtown "
     "Davis Street district, the same district recognized as a Great American Main Street in 2012."),

    ("Culpeper", "com_market_day", "Culpeper Farmers Market, Saturdays through Oct 31",
     "2026-08-29", "09:45",
     "Saturday mornings downtown, right through the end of October. The late-summer tables are the "
     "good ones: tomatoes still going, peppers, squash. And a Piedmont thing worth knowing if you "
     "moved here from the mountains. Our season runs later. Culpeper is not the Valley. Our color "
     "comes late October into November, and the market hangs on longer too. Last day is Halloween.",
     "The Culpeper Farmers Market runs Saturday mornings downtown through its final day on "
     "Saturday, October 31. Culpeper sits in the Piedmont rather than the mountains, so both the "
     "growing season and fall color arrive later here than in the Valley towns to the west."),

    # ---------------- WAYNESBORO ----------------
    ("Waynesboro", "com_landmark_morning", "Rockfish Gap / Parkway Milepost 0",
     "2026-08-23", "11:00",
     "Up at the Gap, 1,903 feet, there is a spot where three of the most famous routes in the "
     "country all touch. Skyline Drive ends. The Blue Ridge Parkway begins, Milepost 0, right "
     "there. And the Appalachian Trail crosses through. Not near Waynesboro. In it. Every "
     "thru-hiker walking Georgia to Maine comes down off that ridge and into this town, and has for "
     "decades.",
     "Rockfish Gap sits at 1,903 feet above Waynesboro, where Skyline Drive ends and the Blue Ridge "
     "Parkway begins at Milepost 0. The Appalachian Trail crosses at the same point, which is part "
     "of why Waynesboro is a designated Appalachian Trail Community."),

    ("Waynesboro", "com_small_detail", "Kaiya with Tulips mural, old ice factory",
     "2026-08-25", "11:00",
     "The old ice factory wall carries a mural most people drive past without looking up. It is "
     "Nils Westergard's Kaiya with Tulips, and it has been ranked among the best murals in the "
     "world. On a former ice plant. In a town of twenty-two thousand. The Street Arts Trail has "
     "more where that came from: Poochie, and Julia Chon's The Lovers over at the YMCA. Waynesboro "
     "made things here for a century. It still does.",
     "Nils Westergard's mural Kaiya with Tulips covers the wall of Waynesboro's former ice factory "
     "and has been ranked among the best murals in the world. It is one stop on the city's Street "
     "Arts Trail, alongside Poochie and Julia Chon's The Lovers at the YMCA."),

    ("Waynesboro", "com_local_word", "Basic City",
     "2026-08-27", "11:00",
     "If you hear somebody say Basic City, they are not being vague. It was a real place: an 1890s "
     "steel boomtown on the east side of the river that ran itself as its own city until Waynesboro "
     "absorbed it in the early 1920s. The name never left. A hundred years on, people still use it "
     "to mean that side of town, which tells you how long a name can outlive a city limit.",
     "Basic City was a separate 1890s industrial town east of the South River that merged into "
     "Waynesboro in 1923-24. More than a century later, locals still use the name for that part of "
     "the city."),

    ("Waynesboro", "com_local_calendar", "Boro Fiddlen' Folk Festival Sat Sept 12",
     "2026-08-29", "11:00",
     "Circle September 12: the Boro Fiddlen' Folk Festival. It is the kind of thing this town does "
     "well. Old-time and folk music, outdoors, no pretense about any of it. Three weeks out, which "
     "is about the right amount of notice for the people who would want to know.",
     "The Boro Fiddlen' Folk Festival takes place Saturday, September 12, 2026 in Waynesboro, a day "
     "of old-time and folk music."),

    # ---------------- LEXINGTON ----------------
    ("Lexington", "com_landmark_morning", "Chessie Nature Trail",
     "2026-08-23", "14:00",
     "The Chessie runs about seven miles along the Maury out to Buena Vista, on ground the C&O laid "
     "track on. That is why it is so flat and so straight. You are walking a railroad right-of-way, "
     "not a path somebody cut. Late August it stays shaded most of the way and the river is loud "
     "enough to hear the whole time. BV and back makes a good morning.",
     "The Chessie Nature Trail follows the Maury River roughly seven miles from Lexington to Buena "
     "Vista along the old C&O Railway right-of-way. It is flat and level the entire distance "
     "because it was originally graded for trains."),

    ("Lexington", "com_small_detail", "textured brick sidewalks, Chilhowie Brick Plant 1880-1910",
     "2026-08-25", "14:00",
     "Look down next time you are on Main. The brick sidewalks are not smooth, and that is not age "
     "or neglect. They were made textured on purpose. Chilhowie Brick Plant turned them out between "
     "1880 and 1910, ridged so people and horses could hold traction on Lexington's hills in the "
     "wet. A hundred and forty years later they are still doing the job they were designed for. Not "
     "many towns have a detail that good underfoot.",
     "Lexington's downtown brick sidewalks were made at the Chilhowie Brick Plant between 1880 and "
     "1910 and were deliberately textured. The ridges gave people and horses traction on the town's "
     "steep grades in wet weather, and they still serve that purpose today."),

    ("Lexington", "com_local_word", "Keydets / the Institute",
     "2026-08-27", "14:00",
     "Get this one right and you sound like you are from here. VMI's teams are the Keydets. Not "
     "Cadets. Keydets. It started as an old phonetic spelling, stuck, and became the actual name, "
     "and locals say the Institute about as often as they say VMI. Same downtown, a few blocks "
     "over, W&L's Generals. Two colleges, one walkable town of about seven thousand. It works "
     "better than it sounds like it should.",
     "VMI's athletic teams are the Keydets, an old phonetic spelling that became the official name. "
     "Locals also refer to VMI simply as the Institute. Washington and Lee's teams, a few blocks "
     "away, are the Generals."),

    ("Lexington", "com_local_calendar", "Rockbridge Regional Fair & Expo Sept 10-13",
     "2026-08-29", "14:00",
     "The Rockbridge Regional Fair and Expo runs September 10 through 13, and this year's theme is "
     "Stars and Stripes Over Carnival Lights. County fair in the truest sense: livestock, midway, "
     "the whole thing. Two weeks out. A good one to get on the calendar before fall gets away from "
     "everybody.",
     "The Rockbridge Regional Fair and Expo runs September 10-13, 2026, with this year's theme "
     "Stars and Stripes Over Carnival Lights."),

    # ---------------- ROANOKE ----------------
    ("Roanoke", "com_landmark_morning", "Mill Mountain Star",
     "2026-08-23", "16:30",
     "It went up in 1949, first lit on the twenty-third of November that year, and it is still the "
     "largest freestanding illuminated man-made star anywhere. Roanoke was the Magic City before it "
     "was the Star City. The N&W railroad took this place from about seven hundred people to five "
     "thousand in two years after 1882. The star came later and took over the name. Get up the "
     "mountain early enough and you get the Valley before the haze does.",
     "The Mill Mountain Star was first lit on November 23, 1949 and remains the largest "
     "freestanding illuminated man-made star in the world. It is the source of Roanoke's Star City "
     "nickname and overlooks the entire Roanoke Valley."),

    ("Roanoke", "com_local_word", "Big Lick",
     "2026-08-25", "16:30",
     "Before it was Roanoke, and long before it was the Star City, this was Big Lick. Named for the "
     "salt licks along the river that pulled game in, and the people who came after them. The "
     "railroad renamed the town in 1882. The old name never actually left. You will still hear it, "
     "always affectionately, usually from somebody whose family has been here longer than the N&W "
     "has.",
     "Roanoke was originally called Big Lick, after the natural salt licks along the river that drew "
     "game to the area. The name changed in 1882 with the arrival of the Norfolk and Western "
     "Railway, but locals still use the original affectionately."),

    ("Roanoke", "com_small_detail", "Grandin Theatre marquee, Grandin Village",
     "2026-08-27", "16:30",
     "The marquee in Grandin Village has been lit since 1932. That is the Grandin Theatre: Art "
     "Deco, restored, and run as a nonprofit, which is the part that actually matters. It did not "
     "survive because a chain kept it open. It survived because the neighborhood would not let it "
     "close. Walk Grandin at dusk and that sign is still the best-looking thing on the street.",
     "The Grandin Theatre opened in 1932 and still anchors Grandin Village. The restored Art Deco "
     "cinema operates as a nonprofit, kept running by the surrounding neighborhood rather than a "
     "commercial chain."),

    ("Roanoke", "com_local_calendar", "Virginia Tech home opener Sat Sept 5",
     "2026-08-29", "16:30",
     "Two weeks out: the Hokies open at home September 5 against VMI. Blacksburg is forty minutes "
     "down the road, close enough that Roanoke feels every home Saturday. The Valley empties out in "
     "one direction in the morning and refills at night. Fall around here really starts with that "
     "first home game, not with the calendar.",
     "Virginia Tech opens its 2026 home football season on Saturday, September 5 against VMI. "
     "Roanoke sits roughly forty minutes from Blacksburg, and home game days are felt across the "
     "Roanoke Valley."),
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
        # GBP goes out 90 minutes later with its own distinct caption
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
        "batch_id": "vp-community-weekly-2026-08-22",
        "lane": "C-community",
        "generated": "2026-08-22",
        "note": "Text-only by design. Community posts carry no product photo and never wait on "
                "the image pipeline. No CTA, no product, no price. Distinct caption per channel.",
        "items": items,
    }
    out = Path(__file__).with_name("manifest_2026-08-22.json")
    out.write_text(json.dumps(manifest, indent=2))
    print(f"{len(items)} items -> {out}")


if __name__ == "__main__":
    build()
