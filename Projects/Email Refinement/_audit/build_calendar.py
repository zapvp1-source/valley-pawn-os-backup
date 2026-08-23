#!/usr/bin/env python3
"""Build the Valley Pawn weekly email calendar Sep 10 -> Dec 31 2026 as Brevo drafts.

Each draft is named "<Theme> - <Month DD, YYYY>" because vp-deal-of-week-monday-pick
finds the week's campaign by matching that literal date string in the campaign name.
That name-matching is exactly why Aug 6 / 13 / 20 went dark: the drafts had been
re-dated forward, the lookup found nothing, and the task skipped silently.

Base HTML is cloned from campaign 28 (W13), the current production standard:
locked logo/trust/5-store directory/hours/footer, the {% if contact.STORE %}
personalised header and primary CTA, and the dashed DEAL OF THE WEEK placeholder
that the Monday picker fills.

Only three regions vary per send: HERO BAND, BODY CONTENT SLOT, PRIMARY CTA label.
"""
import json, urllib.request, os, re, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"
LISTS = [7, 10]           # engaged + internal seeds; waves added later as domain warms
DRY = "--apply" not in sys.argv


def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"api-key": KEY, "Content-Type": "application/json",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ---------------------------------------------------------------- calendar
# (date, campaign name, subject, utm slug, eyebrow, headline, subline,
#  [body paragraphs], notpawn line, cta label)
P = "Everything we sell carries a 30-day warranty."
CAL = [
 ("September 10, 2026", "Roanoke Spotlight",
  "What we stock at our Peters Creek Road store",
  "weekly_roanoke_2026-09-10", "STORE SPOTLIGHT — ROANOKE",
  "The biggest room we've got",
  "Peters Creek Road, Suite C. Our largest showroom of the five.",
  ["Roanoke is where we put the volume — tools, electronics, instruments, jewelry cases worth walking. If you have not been in since we took Suite C, it is a different store.",
   "Looking for something specific? Call ahead and we will hold it at the counter for you."],
  "Day trip: the Roanoke Star and the Mill Mountain overlook are ten minutes from the store.",
  "Get directions"),

 ("September 17, 2026", "Christmas Layaway Opens",
  "Christmas layaway is open. No fees, no interest, no credit check.",
  "weekly_layaway_open_2026-09-17", "LAYAWAY IS OPEN",
  "Put it away now. Take it home for Christmas.",
  "Free layaway, no holding fee, pay it off on your own schedule.",
  ["Here is how it works: pick anything in the store, put a little down, and we hold it. No interest, no credit check, no fee for holding it. Pay it off whenever you like between now and Christmas.",
   "People use it for the gift they could not otherwise get in one go — a ring, a guitar, a tool chest, a game console. Ninety-nine days until Christmas. Starting today beats starting in December."],
  "The earlier you start, the smaller the payments. That is the whole trick.",
  "Start a layaway"),

 ("September 24, 2026", "Fall Projects and Storm Prep",
  "Generators, chainsaws and pressure washers — before you need them",
  "weekly_storm_prep_2026-09-24", "FALL PROJECTS",
  "The tool you need in October is cheapest in September",
  "Generators, chainsaws, pressure washers, tool chests.",
  ["Every year the same thing happens: the power goes out, and generators disappear off every shelf in the valley at twice the price. We have them now, at pawn-shop prices, and they are checked before they go out.",
   "Same for chainsaws, pressure washers, ladders and tool chests. " + P],
  "First frost in Harrisonburg usually lands in the first half of October. Roanoke a few weeks later.",
  "See what's in stock"),

 ("October 1, 2026", "Culpeper Spotlight",
  "What's on the shelves at our James Madison Highway store",
  "weekly_culpeper_2026-10-01", "STORE SPOTLIGHT — CULPEPER",
  "Piedmont's pawn shop",
  "571 James Madison Highway. Tools, jewelry, electronics, and a fair look at whatever you bring in.",
  ["Culpeper sees a lot of tools and a lot of jewelry. If you are selling, we weigh and price gold and silver in front of you against the real-time spot price — you see the same number we do.",
   "If you are buying, the turnover is quick, so what is on the floor this week probably will not be there next week."],
  "Culpeper Fall Restaurant Week runs Sep 29 to Oct 5 — worth planning an evening around.",
  "Get directions"),

 ("October 8, 2026", "Layaway — What People Actually Buy",
  "The five things people put on layaway most",
  "weekly_layaway_what_2026-10-08", "LAYAWAY, WEEK 4",
  "What people actually put on layaway",
  "It is almost never what you would guess.",
  ["Rings and jewelry first, every year. Then guitars and instruments. Then game consoles and laptops. Then tool sets. Then the one big thing someone has wanted all year and finally has a way to get.",
   "No interest, no credit check, no fee to hold it. Put a little down today and pay it off before Christmas."],
  "Seventy-eight days to Christmas. Still plenty of runway.",
  "Start a layaway"),

 ("October 15, 2026", "Year-End Gold and Silver",
  "We weigh your gold in front of you, against live spot",
  "weekly_gold_2026-10-15", "WE BUY GOLD & SILVER",
  "Weighed at the counter. Priced against live spot.",
  "Chains, rings, coins, bars, dental, scrap — broken is fine.",
  ["Bring it in and watch it happen: we weigh it on a calibrated scale in front of you, test it in front of you, and price it against the spot price on the screen. No back room, no vague offer.",
   "Broken, tangled, single earrings, class rings you will never wear again — all of it has a number. Bring it and find out what it is."],
  "Gold does not need an appointment. Walk in any day we are open.",
  "Get a free appraisal"),

 ("October 22, 2026", "Waynesboro Spotlight",
  "What's new at our West Broad Street store",
  "weekly_waynesboro_2026-10-22", "STORE SPOTLIGHT — WAYNESBORO",
  "At the foot of the Blue Ridge",
  "1321 West Broad Street. Outdoor gear, tools, and a steady flow of good used electronics.",
  ["Waynesboro sits right where the valley meets the Parkway, and the inventory shows it — packs, optics, camp gear, and the kind of tools people actually use on a weekend project.",
   "We buy outright too. If you are cleaning out a garage before winter, bring it by and we will make you an offer on the spot."],
  "Shenandoah National Park's Rockfish Gap entrance is fifteen minutes up the road.",
  "Get directions"),

 ("October 29, 2026", "Halloween and Layaway",
  "Costume week, and a reminder about Christmas layaway",
  "weekly_halloween_2026-10-29", "HALLOWEEN WEEK",
  "Two months to Christmas. Yes, really.",
  "Halloween is Saturday, and layaway is still wide open.",
  ["Have a good Halloween — the farmers markets in Culpeper and Waynesboro close for the season this week, so it is properly fall now.",
   "And the practical note: Christmas is nine weeks out. Anything you put on layaway this week gets paid off in small pieces instead of one painful December swipe. No interest, no credit check."],
  "Trick-or-treat times vary by town — check with your town office.",
  "Start a layaway"),

 ("November 5, 2026", "Harrisonburg Spotlight",
  "What's on the floor at our East Market Street store",
  "weekly_harrisonburg_2026-11-05", "STORE SPOTLIGHT — HARRISONBURG",
  "A college town's pawn shop",
  "1790 East Market Street, Suite 22. Electronics, instruments, and a lot of good laptops.",
  ["Harrisonburg turns over more electronics than any of our stores — laptops, monitors, tablets, consoles, audio gear. A $400 laptop instead of a $1,200 one, with " + P.lower(),
   "We buy too. If you are upgrading, bring the old one in and put the money toward the new one."],
  "The Harrisonburg Veterans Celebration parade is this Sunday, Nov 8.",
  "Get directions"),

 ("November 12, 2026", "Veterans Week",
  "Thank you — from all five of our stores",
  "weekly_veterans_2026-11-12", "VETERANS DAY",
  "Thank you",
  "From Culpeper to Roanoke, and everywhere in between.",
  ["Veterans Day was yesterday. In our towns that means something specific — VMI in Lexington, the National Cemetery in Culpeper, and the families in every one of our five towns who have someone who served.",
   "No sale, no offer, no catch in this one. Just thank you. We will be back to business next week."],
  "",
  "Visit a store"),

 ("November 19, 2026", "Layaway vs the Credit Card",
  "The math: layaway vs putting Christmas on a card",
  "weekly_layaway_math_2026-11-19", "LAYAWAY, THE MATH",
  "Layaway costs nothing. A card costs plenty.",
  "Same gift, two very different January bills.",
  ["Put $600 of Christmas on a credit card at 24% and pay it off over six months, and you have paid roughly $43 in interest for the privilege. Put the same $600 on layaway here and you pay $600.",
   "No interest, no credit check, no fee for holding it. That is the entire pitch, and it is why layaway has been around longer than credit cards have."],
  "Five weeks to Christmas. Layaway pickup deadline is Dec 20.",
  "Start a layaway"),

 ("November 26, 2026", "Thanksgiving and Small Business Saturday",
  "Happy Thanksgiving — and Saturday is our day",
  "weekly_thanksgiving_2026-11-26", "THANKSGIVING",
  "Happy Thanksgiving from all five stores",
  "And a word about Saturday.",
  ["Happy Thanksgiving. If you are running the Turkey Trot in Harrisonburg or the Drumstick Dash in Roanoke, good luck out there.",
   "Small Business Saturday is this Saturday, and it is genuinely our day — five family-owned stores in five small Virginia towns. Black Friday doorbusters start Friday and the good ones go fast."],
  "Farmers markets close for the season this week in Harrisonburg and Lexington.",
  "See the doorbusters"),

 ("December 3, 2026", "Lexington Spotlight and Holiday Gifts",
  "Gift ideas from our Walker Street store",
  "weekly_lexington_2026-12-03", "STORE SPOTLIGHT — LEXINGTON",
  "Small store, good stuff",
  "125 Walker Street. Watches, knives, vintage audio and serious tools.",
  ["Lexington is our smallest room and probably our most interesting one — quality watches, knives and outdoor gear, turntables and vintage audio, and tools for the home-shop crowd.",
   "It is a good gift store for exactly that reason. And if Lexington does not have it, we will check the other four for you."],
  "Dickens of a Christmas is in Roanoke this week if you are travelling south.",
  "Get directions"),

 ("December 10, 2026", "Jewelry and Watches Gift Guide",
  "Real gold, real diamonds, not-retail prices",
  "weekly_jewelry_2026-12-10", "GIFT GUIDE",
  "The jewelry case is the best-kept secret in the store",
  "Real gold and real stones, at a fraction of mall pricing.",
  ["Everything in our cases is real and everything is tested. The difference between our price and a jewelry store's is not the gold — it is the markup, the mall rent and the advertising.",
   "Watches too: we see a lot of good mechanical and diver-style pieces come through. " + P],
  "Fifteen days to Christmas. Layaway pickup deadline is Dec 20.",
  "See what's in the case"),

 ("December 17, 2026", "Layaway Pickup Countdown",
  "Layaway pickup deadline is Sunday, December 20",
  "weekly_layaway_pickup_2026-12-17", "LAST CALL",
  "Layaway pickup closes Sunday",
  "If you have something on layaway, this is the week.",
  ["Christmas layaway pickup deadline is Sunday, December 20. If you have something waiting, come pay it off and take it home this week — do not leave it to the last two days.",
   "Not sure what your balance is? Call your store and we will tell you in about thirty seconds."],
  "Still shopping? There is time, and the shelves are still good.",
  "Call your store"),

 ("December 24, 2026", "Merry Christmas",
  "Merry Christmas from all five stores",
  "weekly_christmas_2026-12-24", "MERRY CHRISTMAS",
  "Merry Christmas",
  "From everyone at Valley Pawn, in all five towns.",
  ["Thank you for a good year. Whether you bought something, sold something, or needed a loan to get through a hard month, we appreciate you trusting us with it.",
   "Holiday hours vary by store — call ahead if you need us this week. Otherwise, we will see you after Christmas."],
  "",
  "Check store hours"),

 ("December 31, 2026", "New Year Gold Buy",
  "Start the year with cash for the gold you never wear",
  "weekly_newyear_gold_2026-12-31", "NEW YEAR",
  "That drawer of tangled chains is worth money",
  "January is the best month to sell gold you were never going to wear.",
  ["Every January people find the same drawer — broken chains, single earrings, a class ring, something from a relationship that ended. It is all worth something, and we will weigh and price it in front of you against live spot.",
   "Happy New Year from all five stores. We will be back to regular hours on January 2."],
  "No appointment needed. Walk in any day we are open.",
  "Get a free appraisal"),
]


def para(t):
    return ('<p style="margin:0 0 14px 0; font-size:16px; line-height:1.6; color:#1a1a1a;">'
            + t + '</p>')


def build(base, item):
    (date_s, theme, subject, utm, eyebrow, headline, subline,
     bodies, notpawn, cta_label) = item
    h = base

    # 1. utm_campaign everywhere (base is the Lexington Aug 27 send)
    h = h.replace("weekly_lexington_2026-08-27", utm)

    # 2. HERO BAND — eyebrow / headline / subline
    h = h.replace("STORE SPOTLIGHT — LEXINGTON + THIS WEEK'S DEAL", eyebrow)
    h = h.replace("What's new at our Lexington store", headline)
    h = h.replace("VMI / W&L territory. The military-and-academic mix runs through our inventory.",
                  subline)

    # 3. BODY CONTENT SLOT — keep the dashed deal placeholder, swap the prose
    start = h.find("BODY CONTENT SLOT")
    end = h.find("<!-- ============ LOCKED: TRUST STRIP")
    body_region = h[start:end]
    ph_end = body_region.find("</div>") + len("</div>")
    head = body_region[:ph_end]
    new_body = head + "\n" + "\n".join(para(b) for b in bodies)
    if notpawn:
        new_body += ('\n<p style="margin:18px 0 0 0;font-size:13px;line-height:1.6;color:#8a6a3a;">'
                     '<strong>NOTPAWN</strong> &middot; ' + notpawn + '</p>')
    new_body += "\n          </td>\n        </tr>\n\n        "
    h = h[:start] + new_body + h[end:]

    # 4. PRIMARY CTA labels
    for city in ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]:
        h = h.replace(f"Get directions to {city} &rarr;",
                      (f"{cta_label} to {city} &rarr;" if cta_label == "Get directions"
                       else f"{cta_label} &rarr;"))
    return h


st, w13 = req("GET", "/emailCampaigns/28")
assert st == 200, (st, w13)
BASEHTML = w13["htmlContent"]

# Only DRAFTS matter for the collision check — the picker filters status=draft,
# so an already-sent campaign carrying a future date (campaign 30 was sent Aug 21
# under the name "...September 10, 2026") must NOT suppress that week's draft.
st, existing = req("GET", "/emailCampaigns?status=draft&limit=100")
names = {c["name"] for c in existing.get("campaigns", [])}

created, skipped = [], []
for item in CAL:
    date_s, theme = item[0], item[1]
    name = f"{theme} — {date_s}"
    if any(date_s in n for n in names):
        skipped.append(f"{name}  (a campaign already carries {date_s})")
        continue
    html = build(BASEHTML, item)
    leftover = re.findall(r"\[\[[A-Z_]+\]\]", html)
    assert not leftover, (name, leftover)
    assert "/c/" in html and "/t/" in html, name
    assert "utm_content=primary_cta" in html, name
    payload = {
        "name": name, "subject": item[2], "sender": SENDER, "replyTo": REPLY_TO,
        "htmlContent": html, "recipients": {"listIds": LISTS},
        "inlineImageActivation": False, "mirrorActive": True,
    }
    if DRY:
        created.append(f"[dry] {name}  | subj: {item[2]}")
        continue
    st2, res = req("POST", "/emailCampaigns", payload)
    created.append(f"{'OK ' if st2 < 300 else 'FAIL'} {name}  -> {res}")

print(f"{'DRY RUN — pass --apply to create' if DRY else 'APPLIED'}")
print(f"\ncreated ({len(created)}):")
for c in created:
    print("  ", c)
print(f"\nskipped ({len(skipped)}):")
for s in skipped:
    print("  ", s)
