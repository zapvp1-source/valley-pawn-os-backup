#!/usr/bin/env python3
"""
Lane C — vp-community-weekly manifest for the week of Sept 6-12, 2026.

Week chosen by Rule-12 verification against LIVE Publer output, not by assumption:
GET /posts?from=2026-08-31&to=2026-09-20&state=scheduled returned 57 posts, all of
them on Sept 1-5 and nothing after Sept 5. The prior Lane C batch
(manifest_2026-08-30.json) already owns this calendar week.

Formats were chosen by `creative_drift.py select --lane community --slots 4` run once
per store account. All 20 picks are NEW candidates added by the same-day registry
top-up (_lane_c/topup_candidates_2026-08-31.py) after the engine returned zero
eligible formats for every store.

Text-only by design. Community posts carry no product photo and never wait on the
image pipeline. No CTA, no product, no price. Distinct caption per channel.
Harrisonburg gets first pick and the earliest slots (parity rule).
"""
import json
from pathlib import Path

TZ = "-04:00"

# store, format_id, hook, date, HH:MM (FB), facebook caption, GBP caption
POSTS = [

    # ---------------- HARRISONBURG (first pick - parity rule) ----------------
    ("Harrisonburg", "com_park_hour", "Hillandale Park, the hour before dark",
     "2026-09-06", "08:30",
     "Hillandale Park is the gateway to Rocktown Trails, and the best hour there is not the "
     "middle of the day. It is the last hour before dark, when the light comes in sideways "
     "through the trees and the heat finally lets go. Rocktown in early September still runs "
     "warm at two in the afternoon. By seven it is perfect.",
     "Hillandale Park in Harrisonburg serves as the main gateway to the Rocktown Trails network. "
     "Late afternoon and early evening are the most comfortable times to visit in early "
     "September, when temperatures ease and the tree cover keeps the trails shaded."),

    ("Harrisonburg", "com_under_your_feet", "Court Square, fifth courthouse since 1778",
     "2026-09-08", "08:30",
     "When you walk across Court Square you are walking over the same ground that has held a "
     "Rockingham County courthouse since 1778. The one standing now, with the domed clock tower "
     "and Justice on top, went up in 1896 and 1897. It is the fifth. Four others stood on that "
     "exact square before it. Same ground, five buildings, two hundred and change years.",
     "The Rockingham County Courthouse on Court Square in Harrisonburg was built in 1896-97 and "
     "is the fifth courthouse to stand on that site since 1778. Its domed clock tower is topped "
     "by a figure of Justice, and a historic springhouse remains in the southwest corner of the "
     "square."),

    ("Harrisonburg", "com_the_tracks", "Chesapeake Western, the Crooked and Weedy",
     "2026-09-10", "08:30",
     "The Chesapeake Western opened out of Harrisonburg on March 23, 1896, running east and west, "
     "and it mostly hauled what the Valley grew. Twenty-six miles of it connected Bridgewater to "
     "Elkton. Locked out of Union Station, the line built its own passenger depot on West Bruce "
     "Street in 1913. It never got rich and it never went far, and people around here called it "
     "the Crooked and Weedy with real affection. Norfolk and Western took it over in the 1950s.",
     "The Chesapeake Western Railway opened in Harrisonburg on March 23, 1896, with a 26-mile "
     "line linking Bridgewater to Elkton. The company built its own passenger station at 141 West "
     "Bruce Street in 1913. Known locally as the \"Crooked and Weedy,\" the line primarily carried "
     "Shenandoah Valley agricultural freight and was acquired by the Norfolk & Western in the 1950s."),

    ("Harrisonburg", "com_the_water", "Blacks Run, six miles through downtown",
     "2026-09-12", "08:30",
     "Blacks Run covers about six miles and a good stretch of it runs right through downtown, "
     "which most people forget until they are standing next to it. The Northend Greenway follows "
     "part of it. September water is low and clear and you can see straight to the bottom in "
     "places. Not many towns this size have a creek running through the middle of them.",
     "Blacks Run is a six-mile creek that flows directly through downtown Harrisonburg, with the "
     "Northend Greenway following part of its course. Water levels typically run low and clear "
     "in early September."),

    # ---------------- CULPEPER ----------------
    ("Culpeper", "com_park_hour", "Yowell Meadow Park, early morning",
     "2026-09-07", "09:30",
     "Yowell Meadow Park is a morning place. Get there before eight, before the day warms up, "
     "and the field is still holding dew and Mountain Run is the loudest thing going. By noon it "
     "is a different park entirely. Piedmont Septembers stay warm well past when the mountain "
     "towns have cooled off, so the early hour is worth setting an alarm for.",
     "Yowell Meadow Park in Culpeper is at its most pleasant in the early morning, particularly "
     "in September when Piedmont afternoons remain warm. Mountain Run flows through the park."),

    ("Culpeper", "com_last_warm_evening", "Piedmont evenings run later here",
     "2026-09-09", "09:30",
     "Something people from the mountain towns do not always realize about Culpeper: our season "
     "runs later. We are Piedmont, not Valley, and the color here does not peak until late "
     "October into early November while Afton and Rocktown are already turning. It also means "
     "the warm evenings hang on longer. Porches, the Depot platform, the walk down Davis after "
     "supper. There are more of those left here than up the mountain.",
     "Culpeper sits in Virginia's Piedmont rather than the Shenandoah Valley, which means both "
     "warm evenings and fall foliage arrive later here than in the mountain towns. Peak color in "
     "Culpeper typically comes in late October into early November."),

    ("Culpeper", "com_under_your_feet", "Davis Street, surveyed by a teenage Washington",
     "2026-09-11", "09:30",
     "Davis Street was laid out in surveys done between 1749 and 1759 by George Washington, who "
     "was seventeen when he started. Every time you walk it you are following lines a teenager "
     "drew before there was a country. The National Trust named it a Great American Main Street "
     "in 2012, which is a nice piece of paper, but the older fact is the better one.",
     "Downtown Culpeper's Davis Street traces surveys conducted between 1749 and 1759 by a young "
     "George Washington, who began the work at age 17. Davis Street was named a National Trust "
     "Great American Main Street in 2012."),

    ("Culpeper", "com_the_water", "Mountain Run, from the fields to the Rappahannock",
     "2026-09-12", "09:30",
     "Mountain Run starts out in farm fields, comes down through town, goes under the bridges "
     "and through Yowell Meadow, and keeps going until it hands itself over to the Rappahannock. "
     "Most people in Culpeper cross it several times a week without ever thinking about it. It is "
     "the water this town was built around.",
     "Mountain Run flows from agricultural land west of Culpeper through the town, passing through "
     "Yowell Meadow Park, before joining the Rappahannock River."),

    # ---------------- WAYNESBORO ----------------
    ("Waynesboro", "com_school_colors", "Little Giants, purple and Vegas gold",
     "2026-09-07", "11:00",
     "Purple and Vegas gold, and the best mascot name in the Shenandoah District. Waynesboro "
     "High School, the Little Giants. School is back in and the fall season is underway. Good "
     "luck out there this year.",
     "Waynesboro High School's athletic teams are the Little Giants, competing in the Shenandoah "
     "District in purple and Vegas gold."),

    ("Waynesboro", "com_last_warm_evening", "The river before the mountain socks in",
     "2026-09-09", "11:00",
     "These are the last easy evenings down by the river. In a few weeks the mountain starts "
     "socking in, and anybody who drives I-64 over Afton knows exactly what that looks like. "
     "VDOT runs a whole fog warning system for it. But right now the South River Greenway after "
     "supper is about as good as Waynesboro gets, and there are not many of those nights left.",
     "The South River Greenway in Waynesboro is well suited to evening walks in early September. "
     "Fog and reduced visibility on Afton Mountain and I-64 become more frequent later in the fall."),

    ("Waynesboro", "com_under_your_feet", "Basic City, the boomtown that merged in",
     "2026-09-11", "11:00",
     "The east side of town has its own name and its own history. Basic City was a separate "
     "place, a steel boomtown that went up in the 1890s, and it did not merge into Waynesboro "
     "until 1923 into 1924. People still say Basic City, because it was one. If you are over "
     "there, the ground you are standing on used to belong to a different town.",
     "Basic City was an independent town founded during an 1890s steel boom on what is now the "
     "eastern side of Waynesboro. It merged with Waynesboro in 1923-24, and the name remains in "
     "local use."),

    ("Waynesboro", "com_the_water", "The river, which is what everyone calls it",
     "2026-09-12", "11:00",
     "Nobody here says the South River. They say the river, and everybody knows which one. It "
     "runs right through the middle of town with the Greenway alongside it, and it is the reason "
     "a working manufacturing town turned into a river-and-arts town without having to move an "
     "inch. September water is low and slow and about as friendly as it gets.",
     "The South River runs through the center of Waynesboro, with the South River Greenway "
     "following its course. Locals refer to it simply as \"the river.\""),

    # ---------------- LEXINGTON ----------------
    ("Lexington", "com_the_water", "The Maury, and the end of tubing season",
     "2026-09-06", "15:00",
     "Labor Day is the unofficial end of tubing on the Maury, so that page has turned for the "
     "year. The river is still right there though, and the Chessie runs about seven miles "
     "alongside it toward BV. September on the Maury is quieter than August and honestly better "
     "for it.",
     "The Maury River runs alongside Lexington, with the Chessie Nature Trail following roughly "
     "seven miles of its bank toward Buena Vista. River tubing season informally ends around "
     "Labor Day."),

    ("Lexington", "com_under_your_feet", "Textured brick, made for the hills",
     "2026-09-08", "15:00",
     "The brick sidewalks downtown are textured on purpose. They came out of the Chilhowie Brick "
     "Plant between 1880 and 1910, and the pattern is there so people could get traction walking "
     "these hills in the wet. Somebody a hundred and forty years ago thought about your footing "
     "on a rainy day and did something about it. You walk over that decision every time you go "
     "downtown.",
     "Lexington's downtown brick sidewalks were produced at the Chilhowie Brick Plant between "
     "1880 and 1910 and were deliberately textured to provide traction on the town's hills in "
     "wet weather."),

    ("Lexington", "com_the_tracks", "The Chessie, still going where the C&O went",
     "2026-09-10", "15:00",
     "The Chessie Nature Trail is a railroad. It runs about seven miles along the Maury to Buena "
     "Vista on the old C&O right-of-way, which is why it is so flat and so straight in a county "
     "that is neither. The grade a railroad needed is the same grade that makes for easy walking. "
     "The trains are gone and the route stayed.",
     "The Chessie Nature Trail follows roughly seven miles of the former Chesapeake & Ohio "
     "Railway right-of-way along the Maury River from Lexington to Buena Vista. The old rail "
     "grade makes it a flat, easy walking route."),

    ("Lexington", "com_trailhead", "Goshen Pass, twenty-odd minutes out",
     "2026-09-11", "15:00",
     "Locals just say Goshen. It is a gorge with the Maury running through it and a road that "
     "bends along with the water, and it is close enough that people go out there on an ordinary "
     "afternoon. Not a hard trip and not a hard walk. The color out there comes a little early "
     "because of the elevation, so the next few weeks are worth watching.",
     "Goshen Pass is a river gorge on the Maury River northwest of Lexington, accessible by a "
     "short drive. Higher elevation means fall color typically appears there earlier than in "
     "town."),

    # ---------------- ROANOKE ----------------
    ("Roanoke", "com_under_your_feet", "Big Lick, and the ground it was named for",
     "2026-09-07", "16:30",
     "Before it was the Star City it was Big Lick, and that name came from the ground itself. "
     "Salt licks here drew game, game drew people, and people stayed. The name is still used "
     "around town, usually with a grin. The literal salt in the dirt is why any of this is here "
     "at all.",
     "Roanoke was originally known as Big Lick, a name derived from natural salt licks in the "
     "area that attracted wildlife and, in turn, early settlement. The name remains in local use."),

    ("Roanoke", "com_the_tracks", "700 people to 5,000 in two years",
     "2026-09-09", "16:30",
     "In 1882 the Norfolk and Western came through and this place went from around seven hundred "
     "people to five thousand inside of two years. That is why they called it the Magic City "
     "before they ever called it the Star City. The old N&W passenger station is still standing "
     "and it houses the O. Winston Link Museum now. Every bit of the street grid downtown traces "
     "back to that railroad.",
     "The arrival of the Norfolk & Western Railway in 1882 grew Roanoke from roughly 700 residents "
     "to about 5,000 within two years, earning it the nickname the Magic City. The former N&W "
     "passenger station downtown now houses the O. Winston Link Museum."),

    ("Roanoke", "com_trailhead", "McAfee Knob, and the parking lot truth",
     "2026-09-10", "16:30",
     "McAfee Knob is the most photographed spot on the entire Appalachian Trail and better than "
     "fifty thousand people a year go up it. It is also a real climb, not a stroll, and the "
     "parking situation on a nice weekend is exactly what you would expect from that number. Go "
     "on a weekday, go early. With Tinker Cliffs and Dragon's Tooth it makes the Virginia Triple "
     "Crown, which is a serious piece of hiking to have twenty minutes from the house.",
     "McAfee Knob, northwest of Roanoke, is the most-photographed location on the Appalachian "
     "Trail and receives more than 50,000 hikers annually. It is a strenuous climb and parking "
     "fills early on weekends. Together with Tinker Cliffs and Dragon's Tooth it forms the "
     "Virginia Triple Crown."),

    ("Roanoke", "com_the_water", "The Roanoke River, and the greenway that follows it",
     "2026-09-12", "16:30",
     "The Roanoke River runs the length of the valley and the greenway runs with it, through "
     "Wasena and Vic Thomas and out to River's Edge. It is the one piece of the city almost "
     "everybody uses, whether they are running it, riding it, or just walking a dog on it in "
     "September when the evenings finally cool off.",
     "The Roanoke River Greenway follows the Roanoke River through Wasena Park, Vic Thomas Park "
     "and River's Edge, providing a continuous walking and cycling route through the city."),
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
        "batch_id": "vp-community-weekly-2026-09-06",
        "lane": "C-community",
        "generated": "2026-08-31",
        "note": "Week of Sept 6-12. Text-only by design. All 20 formats are NEW candidates "
                "selected by creative_drift after a same-day additive registry top-up; the "
                "community lane had returned zero eligible formats for all 5 stores because the "
                "7 season-agnostic formats were all inside the 21-day cooldown from the 2026-08-24 "
                "run and the remaining 3 are gated to early_fall/peak_fall.",
        "items": items,
    }
    out = Path(__file__).with_name("manifest_2026-09-06.json")
    out.write_text(json.dumps(manifest, indent=2))
    print(f"{len(items)} items -> {out}")


if __name__ == "__main__":
    build()
