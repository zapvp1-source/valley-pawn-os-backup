#!/usr/bin/env python3
"""Valley Pawn eBay — precious-metal detector. Pure, no network, no writes, stdlib only.

WHY THIS EXISTS
---------------
Joshua, 2026-09-17, from store feedback:

    "the managers are saying that they are pricing things at lowest possible for
     things like silver etc etc, so we likely shouldn't be repricing anything
     precious metals"

Precious metal is already priced off melt at intake. The counter prices a silver
chain or a gold charm at or just above its metal value — there is no retail margin
sitting on top to discount. A blind 10% markdown on one of those does not "move
aged inventory", it sells the metal for less than the metal is worth, three times
over as the cuts stack to 30%. Every other category has a retail markup that a cut
eats into; metal does not.

So: **anything priced off metal content is never auto-repriced.** It is still aged
and still surfaced at 90 and 150 days — a person decides to relist it, pull it, or
send it to the refiner. It just never gets a silent percentage cut.

HOW IT DECIDES
--------------
Keyword matching on "gold"/"silver" is badly wrong here and was tested against all
459 live listings before this shipped. These are NOT precious metal and must keep
getting marked down normally:

    McFarlane DC Multiverse ... Gold Label Exclusive     (an action figure)
    McFarlane ... Platinum Edition Batman                (a toy)
    Vionic Uptown Mary Jane in Gold Size 10M             (shoes)
    Vintage Crown Trifari ... Gold Tone Bracelet         (costume, base metal)
    Bulova Accutron ... Gold-toned Stainless             (plated watch case)
    14K Gold Plated Costume Chain                        (plated, not solid)
    Auto Meter ... Shift-Lite Tachometer 10k             ("10k" is RPM)
    Citizen Eco-Drive ... E110-K1675                     ("K1675" is a model number)

While these ARE, and must be protected:

    Mariners Anchor Charm14K 2 Tone Gold 2.1dwt          (no space before 14K)
    Pandora Silver Bracelet 925 Silver 11.3dwt           (Fashion Jewelry category!)
    Vintage Sterling "Diamond" by Reed & Barton          (Kitchen/Flatware category!)
    1989 VMI ... Sterling Silver Medal                   (Collectibles category!)
    .900 Polished Platinum Solitaire                     (Fine Jewelry)
    2023 1oz .999 Silver Niue $2 Coin                    (Bullion)

Two lessons are baked into the logic below, both learned from real misses:
  1. Category alone is useless in BOTH directions — real sterling turns up under
     Kitchen, Collectibles and Fashion Jewelry; fake gold turns up under Fine
     Jewelry. The fineness/weight mark in the TITLE is the reliable signal.
  2. A bare karat mark is ambiguous ("10k" RPM, "K1675" model) so it needs a metal
     word beside it. Every other signal — sterling, .925, dwt, bullion — stands alone.

Verified 2026-09-17 against all 459 active listings across the 5 stores:
29 excluded (6.3%), $10,280.56 of asking value protected, zero false positives and
zero false negatives in the reviewed set.

Usage:
    from ebay_precious import is_precious_metal
    hit, why = is_precious_metal(item.get("Title"), item.get("category_name"))

Run this file directly to self-test.
"""
import re

# STRONG — essentially never appear in a title that is not precious metal.
_STRONG = re.compile(r"""(?xi)
    \bsterling\b
  | \bfine\s+silver\b
  | \bbullion\b
  | \b(?:scrap|melt)\s+(?:gold|silver|platinum)\b
  | \bsolid\s+(?:gold|silver|platinum)\b
  | \.(?:375|417|585|750|800|900|916|925|950|958|999)\b        # dotted fineness: .925, .999
  | \d\s?-?\s?(?:dwt|ozt|oz\s?t|pennyweight)\b                 # weight-priced: 2.1dwt, 1 ozt
  | \btroy\s?(?:oz|ounce)\b
  | (?:9|10|12|14|18|21|22|24)\s?-?\s?k(?:t|arat)?(?![a-z0-9]) # 14K, Charm14K, 18kt
""")

# WEAK — needs corroboration from the category tree or a metal word in the title.
_WEAK = re.compile(r"(?i)\b(?:375|417|585|750|916|925|950|958|999)\b|\b(?:platinum|palladium)\b")

# A bare karat mark on its own is ambiguous; see the Auto Meter / Citizen cases above.
_KARAT_ONLY = re.compile(r"(?i)^\d{1,2}\s?-?\s?k(?:t|arat)?$")
_METALWORD = re.compile(r"(?i)\b(?:gold|silver|platinum|palladium)\b")

# Base-metal and product-name phrases. These VETO a match — unless a real melt
# signal is also present, in which case the melt signal wins ("14k Gold Plated"
# is vetoed; "Sterling Silver 14k Yellow Gold" is not).
_VETO = re.compile(r"""(?xi)
    \b(?:gold|silver|bronze|platinum|rose\s?gold)[\s-]?(?:tone|toned|plated|fill|filled|wash|colou?red)\b
  | \b(?:gold|silver|platinum|bronze)[\s-]?(?:label|edition|series|status|award)\b
  | \bgoldtone\b | \bsilvertone\b | \bgold\s?filled\b
""")
_MELT = re.compile(r"(?xi)\bsterling\b|\.(?:9\d\d|750|585|417|375)\b|\d\s?-?\s?(?:dwt|ozt)\b|\btroy\b|\bbullion\b")

_PM_CAT = ("bullion", "sterling silver", "precious metal", "scrap gold", "scrap silver")
_PM_TREE = ("jewelry & watches", "coins & paper money", "antiques:silver")


def is_precious_metal(title, category_name=""):
    """Return (bool, reason). True when the price is driven by metal content, so a
    blind percentage markdown could push it below melt. Never auto-reprice these."""
    t = title or ""
    c = (category_name or "").lower()

    for h in _PM_CAT:
        if h in c:
            return True, "category: %s" % h

    s = _STRONG.search(t)
    if s and _KARAT_ONLY.fullmatch(s.group(0).strip()) and not _METALWORD.search(t):
        s = None                                   # "Tachometer 10k" / "E110-K1675"
    if s:
        if _VETO.search(t) and not _MELT.search(t):
            return False, "decoy only (%s)" % _VETO.search(t).group(0).strip()
        return True, "melt signal: %s" % s.group(0).strip()

    w = _WEAK.search(t)
    if w and (any(c.startswith(x) for x in _PM_TREE) or _METALWORD.search(t)):
        if _VETO.search(t) and not _MELT.search(t):
            return False, "decoy only (%s)" % _VETO.search(t).group(0).strip()
        return True, "metal + %s" % w.group(0).strip()

    return False, "no melt signal"


# --- self-test: every case below is a REAL listing or a real near-miss ------------
_CASES = [
    # (title, category, expected)
    ("1989 VMI Virginia Military Institute Sterling Silver Medal", "Collectibles:Historical Memorabilia", True),
    ("Size: 7 .900 Polished Platinum Round Brilliant Cut Solitaire Diamond", "Jewelry & Watches:Fine Jewelry:Rings", True),
    ("David Yurman 20\" Sterling Silver 14k Yellow Gold Cable Oval Link", "Jewelry & Watches:Men's Jewelry", True),
    ("Mariners Anchor Charm14K 2 Tone Gold 2.1dwt", "Jewelry & Watches:Fine Jewelry:Necklaces", True),
    ("Pandora Silver Bracelet 925 Silver 11.3dwt", "Jewelry & Watches:Fashion Jewelry:Bracelets", True),
    ("Vintage Sterling \"Diamond\" by Reed & Barton 9\" Modern Hollow Handle", "Home & Garden:Kitchen:Flatware", True),
    ("2023 1oz .999 Silver Niue $2 Coin", "Coins & Paper Money:Bullion:Silver:Coins", True),
    ("Vintage Taxco .950 Silver Inlay Choker Collar Necklace", "Jewelry & Watches:Ethnic", True),
    ("John Hardy Large Heavy Oval .925 Sterling Silver Pendant 24.9G", "Jewelry & Watches:Fine Jewelry", True),
    # must KEEP getting marked down
    ("McFarlane DC Multiverse DC Rebirth: Kid Flash Gold Label Exclusive", "Toys & Hobbies:Action Figures", False),
    ("McFarlane DC Multiverse Platinum Edition Batman (Yellow Suit) 7\"", "Baby:Toys for Baby", False),
    ("Vionic Uptown Mary Jane in Gold Size 10M Womens Chunky Platform", "Clothing:Women's Shoes:Flats", False),
    ("Vintage Crown Trifari White Milk Glass 7.5\" Gold Tone Bracelet", "Jewelry & Watches:Vintage & Antique Jewelry", False),
    ("Napier Brown Marbled Gold-Tone Choker Necklace, Vintage Costume", "Jewelry & Watches:Vintage & Antique Jewelry", False),
    ("Bulova Accutron Oxford Watch Model 27B60 Gold- toned Stainless", "Jewelry & Watches:Watches", False),
    ("14K Gold Plated Costume Chain", "Jewelry & Watches:Fashion Jewelry", False),
    ("Auto Meter 3903 Sport-Comp Monster Shift-Lite Tachometer 10k", "eBay Motors:Parts", False),
    ("Vintage - Citizen Eco-Drive Men's Stainless Steel E110-K1675", "Jewelry & Watches:Watches:Wristwatches", False),
    ("WWII Hawaii Overprint 1935A $1 Silver Certificate Bill Note", "Coins & Paper Money:Paper Money: US", False),
]

if __name__ == "__main__":
    bad = 0
    for title, cat, want in _CASES:
        got, why = is_precious_metal(title, cat)
        ok = got == want
        bad += 0 if ok else 1
        print("%-4s %-11s %-30s %s" % ("OK" if ok else "FAIL",
              "protected" if got else "markdown", why[:30], title[:58]))
    print("\n%d case(s) failed of %d" % (bad, len(_CASES)))
    raise SystemExit(1 if bad else 0)
