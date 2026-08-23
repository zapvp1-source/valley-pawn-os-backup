#!/usr/bin/env python3
"""Q4 2026 creative refresh — candidate invention + novelty gate.
Every candidate is seeded from measured evidence; the seed reasoning is carried
into CREATIVE_LEDGER.md so next quarter can judge the reasoning, not just the result."""
import sys, json
sys.path.insert(0, '.')
from creative_drift import DriftEngine, Format

CANDIDATES = [
# (lane, pillar, id, title, template, seasons, seed_reasoning)
("product", "Education", "pro_appraisal_explainer",
 "How we actually priced this",
 "One real item with its real tag. Name the three things that set the number: condition, "
 "what comparable units actually sold for, and what it costs us to stand behind it for 30 days. "
 "End by asking what they'd have guessed. Never defensive, never a rebuttal to anyone.",
 [],
 "Seeds untried_territory #1 (behind-the-counter appraisal explainers). Also the only "
 "constructive answer to the two unanswered 1-star Culpeper reviews alleging gold lowballing: "
 "show the arithmetic publicly instead of arguing privately. Ends on a question because "
 "485 posts produced 18 comments."),

("product", "Product", "pro_retro_shelf",
 "The retro shelf this week",
 "Recurring weekly. Whatever console, cartridge, controller or handheld came across the counter "
 "this week, with the real price on the tag. One line on why that one still gets picked up.",
 [],
 "Bravo sold ~49 console/game items in three August weeks (NES 9, PS4 games 8, PSP 8, Switch 12, "
 "PS3 6, controllers 6) and retro gaming has never once been content. Recurring by design: "
 "followers grew +6 in 28 days against 7K reach, so the registry needs formats that give a "
 "reason to come back, not just to look once."),

("product", "Education", "pro_storm_kit",
 "What's actually in a storm kit",
 "Generator, chainsaw, work light, batteries, fuel cans - what we have, what it costs, and "
 "honestly what you do not need to buy. Utility first; the price list is the proof, not the pitch.",
 ["early_fall", "peak_fall", "early_winter"],
 "Seeds untried_territory #5 (storm-prep checklists). Chainsaws are provably selling (5 units, "
 "$1,290 in three weeks) and batteries are the #8 category by unit. Utility content is the "
 "kind people forward, and forwarding is what produced the only reach outliers in the quarter."),

("product", "Education", "pro_price_ladder",
 "Three of the same thing, three prices",
 "Same category, three real units at three real prices, good/better/best. Explain precisely what "
 "the extra money buys and where it stops being worth it. Say plainly when the cheapest one is "
 "the right call.",
 [],
 "Distinct from eng_this_or_that (that one is pure preference between two items; this one "
 "teaches a purchase decision). Impact wrenches/drivers, drills and laptops all show 3+ "
 "simultaneous units in the pricing queue, so the ladder is real inventory, not a construct."),

("video", "Story", "vid_sixty_second_repair",
 "Sixty seconds of cleaning it up",
 "Silent before/after time-lapse of one item being cleaned, restrung, polished or tested. "
 "No narration, no music bed required, end card only. Built from a photo pair plus ffmpeg.",
 [],
 "Seeds untried_territory #2 and #3 at once. Video is the worst-performing type in the quarter "
 "(47 posts, median reach 1.0) - but 45 of those 47 were staff-posted straight to Facebook and "
 "the only two that went out through Publer drew 29 and 136 reach and 194 of the quarter's 216 "
 "total video views. The failure is the distribution path, not the medium."),

("video", "Product", "vid_case_walk",
 "Walk the case",
 "One slow, steady phone pan down a single case, prices legible on screen, no voiceover. "
 "Twenty to thirty seconds. One case per post, one store per post.",
 [],
 "The jewelry case-count photos are already captured at all five stores every week for the "
 "compliance count (2026-08-21 files present for CUL/HAR/LEX/ROA/WAY). This format costs the "
 "stores nothing new and turns an existing compliance artifact into publishable video, which "
 "is the only way a video lane survives an empty casual-video-inbox - 47 days and counting."),

("video", "Story", "vid_closing_time",
 "Closing time",
 "Fixed-camera time-lapse of the last ten minutes of a Saturday at one store, compressed to "
 "twenty seconds. No products named, no prices, no CTA. Just the lights going off.",
 [],
 "Seeds untried_territory #3 (counter POV time-lapses). The quarter's best-performing store "
 "photo was Walker Street before the shops open - a quiet, human, product-free scene. This is "
 "that, in motion, and it requires nobody to think of anything."),

("humor", "Humor", "hum_wrong_guess",
 "What people are sure this is worth",
 "The gap between an object's reputation and its actual market. Affectionate, aimed squarely at "
 "the object's mythology and never at the person holding it - and always followed by the one "
 "time the myth turned out to be true.",
 [],
 "Humor lane had only two formats against a 1-per-week quota, so it was structurally certain to "
 "violate the 60-day humor cooldown by week nine. Pairs with pro_retro_shelf: the console-worth-"
 "a-fortune belief is the single most common counter conversation and it is a joke about a "
 "market, not about a customer, which keeps it inside the PILLAR_OVERLAY 4 humor boundaries."),

("humor", "Humor", "hum_seasonal_arrival",
 "It is that season again",
 "The annual comedy of what walks in when - mowers in September, generators the morning after a "
 "storm warning, treadmills the first week of January. Observational, about the calendar, never "
 "about anyone's circumstances.",
 [],
 "Seasonal by construction, so it satisfies the season skin without a separate seasonal variant, "
 "and it cannot drift into joking about hard times because the subject is the weather and the "
 "calendar. Second humor format needed to make the 60-day cooldown survivable."),

("engagement", "Engagement", "eng_two_week_answer",
 "We asked, and here is what we did",
 "A deliberate two-parter. Week one asks a real question we intend to act on. Week two publishes "
 "what we actually changed because of the answers, naming the change. The second half ships even "
 "if the answer was inconvenient.",
 [],
 "Directly targets the follow gap Joshua flagged 2026-08-06: reach +937 percent and 74 QR/"
 "giveaway link clicks producing +6 net followers in 28 days. Nothing in the registry gives "
 "anyone a reason to be there next week. Distinct from eng_stock_poll, which asks once and "
 "promises follow-up as an afterthought; here the follow-up is the format."),

("engagement", "Engagement", "eng_hometown_bracket",
 "Town versus town",
 "A running bracket on something harmless and genuinely local - best fall drive, best breakfast, "
 "best field to watch a game from. Different entrants per town, one round per week, results "
 "posted. Never involves Valley Pawn and never names a competitor.",
 [],
 "Small-market local Facebook comments on almost nothing except civic rivalry. This is the one "
 "legitimate five-store same-week fan-out the drift rules permit (seasonal tentpole), because "
 "each town's bracket carries different entrants and therefore different text - it fans out "
 "without violating the byte-identical ban that produced 229 verbatim reposts last quarter."),

("community", "Community", "com_local_news_desk",
 "Something that happened here this week",
 "One verifiable, genuinely local thing that is not about us: a road reopening, a new business "
 "on the block, a school record, the Parkway closing for the season. Sourced, dated, no CTA, "
 "no product, no Valley Pawn mention above the address footer.",
 [],
 "The quarter's only real reach outliers were the 2026-07-23 hiring posts - 942, 469, 435, 295 "
 "and 162 reach against a 13-reach baseline, a 30 to 70x multiple. They did not win on craft; "
 "they won because they were local news people forwarded. Nothing else in the registry is built "
 "to be forwarded. This is."),
]

def main():
    e = DriftEngine()
    accepted, rejected = [], []
    for lane, pillar, fid, title, template, seasons, why in CANDIDATES:
        f = Format(id=fid, lane=lane, pillar=pillar, title=title,
                   template=template, seasons=seasons, hook_key=fid, notes=why)
        ok, reason = e.add_candidate(f)
        (accepted if ok else rejected).append((fid, title, reason))
        print(("ACCEPT  " if ok else "REJECT  ") + f"{fid:<26}{title}" + ("" if ok else f"   <- {reason}"))
    # widen untried territory for the NEXT quarter - what we still have not touched
    e.state["untried_territory"] = [
        "customer-submitted 'what is this' photos",
        "a standing Saturday live Q&A at one store",
        "long-form single-item写 write-ups on the blog with real provenance research",
        "audio only - a 60-second counter story with no video",
        "a printed zine/handout that gets photographed for social",
        "collaboration posts with a non-competing local business",
        "seasonal town bracket results as a recurring civic institution",
        "'we were wrong about this item' - public correction as content",
    ]
    e.state.setdefault("history", []).append({
        "date": "2026-08-22", "event": "quarterly_refresh_Q4_2026",
        "retired": [], "rested": [],
        "accepted": [a[0] for a in accepted], "rejected": [r[0] for r in rejected],
        "annual_pass": "n/a - registry created 2026-08-22, no same-season predecessor",
    })
    e.save()
    print(f"\nACCEPTED {len(accepted)}  REJECTED {len(rejected)}")

if __name__ == "__main__":
    sys.exit(main())
