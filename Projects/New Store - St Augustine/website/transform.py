#!/usr/bin/env python3
"""Turn the thevalleypawn.com mirror into two Rocket Pawn & Jewelry static sites.
usage: transform.py <variant: red|vp> <outdir>
"""
import os, re, sys, shutil, json, html
from pathlib import Path
from bs4 import BeautifulSoup

VARIANT, OUT = sys.argv[1], Path(sys.argv[2])
MIRROR = Path("/home/claude/staug/site/mirror")
SRC = MIRROR / "thevalleypawn.com"
ASSETS = Path("/home/claude/staug/site/assets")   # new logo / hero files live here

STORE = {
    "addr1": "2493-2495 US Highway 1 South", "city": "St. Augustine", "st": "FL", "zip": "32086",
    "phone": "(904) 000-0000", "tel": "+19040000000", "email": "info@rocketpawnjewelry.com",
    "maps": "https://www.google.com/maps/search/?api=1&query=2493+US+Highway+1+S+St+Augustine+FL+32086",
}
CITIES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
PHONES = ["(540) 445-5510", "(540) 221-6346", "(540) 574-4500", "(540) 461-8349", "(540) 562-0776",
          "540-445-5510", "540-221-6346", "540-574-4500", "540-461-8349", "540-562-0776"]
TELS = ["5404455510", "5402216346", "5405744500", "5404618349", "5405620776"]
ADDRS = [r"571 James Madison H(?:wy|ighway)(?:,? Suite C)?", r"1321 W(?:est|\.)? Broad St(?:reet)?", r"1790 E(?:ast|\.)? Market St(?:reet)?(?:,? (?:Unit|Suite) 22)?",
         r"125 Walker St(?:reet)?", r"2362(?:-D)? Peters Creek R(?:d|oad)(?:,? Suite C)?"]
ZIPS = ["22701", "22980", "22801", "24450", "24017"]

# phrase replacements run first (order matters), then generic ones
PHRASES = [
    (r"Serving the (?:Shenandoah )?Valley Since 1988", "From the family behind ⟪VP⟫ · Opening Spring 2027"),
    (r"Five locations\. Thirty-plus years\.", "One location. Fifteen-plus years of pawn experience."),
    (r"Five locations strong across (?:Virginia[’'`]s |the )?(?:Shenandoah Valley|First Coast)", "One location on Florida's First Coast"),
    (r"Expanding across the Valley!?", "Now in St. Augustine."),
    (r"Highest Rated Pawn Shop in the Valley", "St. Augustine's newest pawn shop"),
    (r"Average 4\.9 Stars Across All Locations", "30-day warranty on everything we sell"),
    (r"(?i)\bin the valley\b", "in St. Augustine"),

    (r"5 Virginia Stores", "St. Augustine, FL"),
    (r"5 Locations Across the Shenandoah Valley", "One location on US-1 South in St. Augustine"),
    (r"5 Locations", "Our Store"), (r"five locations", "our store"), (r"5 locations", "our store"),
    (r"All stores closed Sunday; closed Wednesday except Culpeper, Roanoke and Waynesboro\.?", "Closed Sunday."),
    (r"Call or text your store", "Call or text us"),
    (r"Five stores serving the Shenandoah Valley\.?", "Part of the family that runs five ⟪VP⟫ stores in ⟪VA⟫."),
    (r"All 5 Valley Pawn Locations", "Our Store"),
    (r"Live Inventory from All 5 Virginia Stores", "Live Inventory"),
    (r"FFL Transfers at 5 Virginia Locations", "FFL Transfers in St. Augustine, FL"),
    (r"· 5 Virginia Locations", "· St. Augustine, FL"),
    (r"\b5 Virginia Locations", "St. Augustine, FL"),
    (r"Our Locations \| 5 Valley Pawn Stores Across Virginia", "Our Store | Rocket Pawn & Jewelry, St. Augustine FL"),
    (r"\s*Rated 4\.9★ on Google\.", ""),
    (r"on James Madison Hwy", "on US-1 South"),
    (r"one of five (?:Shenandoah Valley|Valley|Virginia) locations", "on US-1 South"),
    (r"one of five Valley Pawn locations serving the (?:Shenandoah Valley|Valley)", "now open on US-1 South"),
    (r"Stop in at any of our five (?:Shenandoah Valley|Valley|Virginia) stores — [^—]+ — and", "Stop in at our St. Augustine store and"),
    (r"Stop by any of Valley Pawn’s five (?:Shenandoah Valley|Valley|Virginia) locations — [^—]+ — for", "Stop by our St. Augustine store for"),
    (r"reach any of our five stores", "reach us"),
    (r"from all five Valley Pawn stores in Virginia", "from Rocket Pawn & Jewelry in St. Augustine, Florida"),
    (r"across all five Virginia pawn shop locations", "at our St. Augustine, Florida pawn shop"),
    (r"at all five Virginia locations", "in St. Augustine, Florida"),
    (r"Valley Pawn's five Virginia stores", "Rocket Pawn & Jewelry in St. Augustine, Florida"),
    (r"Valley Pawn’s five Virginia stores", "Rocket Pawn & Jewelry in St. Augustine, Florida"),
    (r"(?i)\b(?:all )?five (?:Virginia |Shenandoah Valley |Valley |Valley Pawn )?(?:stores|locations)\b", "our St. Augustine store"),
    (r"Our \w+ stores are open", "Our St. Augustine store is open"),
    (r"All stores are closed Sunday\.", "We are closed Sunday."),
    (r"facebook\.com/thevalleypawn", "facebook.com/rocketpawnjewelry"),
    (r"Rated 4\.9 out of 5 from \d+ Google reviews\.?", ""),
    (r"all 5 of our \w+ locations", "our St. Augustine store"),
    (r"at 5 Valley Pawn Stores", "at Rocket Pawn & Jewelry"),
    (r"Pick your nearest store", "Our store"),
    (r"Open Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM \(closed Sunday\)", "Open Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM (closed Sunday)"),
    (r"Mon, Tue, Thu, Fri(?:,| &(?:amp;)?| and) Sat 10am–6pm \(closed Wed &(?:amp;)? Sun\)", "Mon–Fri 10am–6pm, Sat 10am–5pm (closed Sun)"),
    (r"Mon, Tue, Thu, Fri, Sat 10am–6pm", "Mon–Fri 10am–6pm, Sat 10am–5pm"),
    (r"Shenandoah Valley(?:'s)?", "First Coast"), (r"the Valley\b", "St. Augustine"),
    (r"Valley Pawn", "Rocket Pawn & Jewelry"), (r"VALLEY PAWN", "ROCKET PAWN & JEWELRY"), (r"ValleyPawn", "RocketPawn"),
    (r"thevalleypawn\.com", "rocketpawnjewelry.com"), (r"@valley_pawn", "@rocketpawnjewelry"), (r"valley_pawn", "rocketpawnjewelry"),
    (r"Full Circle Finance Inc\.?(?: DBA)?", "Full Circle Finance Inc"),
    (r"\bVirginia\b", "Florida"), (r"\bVA\b(?=[ ,.<])", "FL"),
]
# "From the family behind Valley Pawn" must keep the real name -> protect it
PROTECT = "⟪VP⟫"

def sub_text(s):
    s = s.replace("From the family behind Valley Pawn", f"From the family behind {PROTECT}")
    s = s.replace('Mon • Tue • Thu • Fri • Sat<br><strong style="color:#1a1a2e;">10 AM – 6 PM</strong><br><span style="color:#999;font-size:13px;">Closed Wed &amp; Sun — except Culpeper, Roanoke &amp; Waynesboro, open Wednesdays</span>',
                  'Mon – Fri<br><strong style="color:#1a1a2e;">10 AM – 6 PM</strong><br>Saturday<br><strong style="color:#1a1a2e;">10 AM – 5 PM</strong><br><span style="color:#999;font-size:13px;">Closed Sunday</span>')
    s = re.sub(r'<div style="background:#FFFFFF;[^"]*">\s*<div style="font-size:36px;margin-bottom:10px;">⭐</div>.*?</p>\s*</div>', "", s, flags=re.S)
    for pat, rep in PHRASES:
        s = re.sub(pat, rep, s)
    for a in ADDRS: s = re.sub(a, STORE["addr1"], s)
    for z in ZIPS: s = s.replace(z, STORE["zip"])
    for p in PHONES: s = s.replace(p, STORE["phone"])
    for t in TELS: s = s.replace("+1"+t, STORE["tel"]).replace(t, STORE["tel"][2:])
    for c in CITIES:
        s = re.sub(rf"\b{c}\b", STORE["city"], s)
        s = s.replace(c.lower()+"@fcfpawn.com", STORE["email"])
    s = s.replace("jdavis@fcfpawn.com", STORE["email"]).replace("preston@fcfpawn.com", STORE["email"])
    s = re.sub(r"Valley\+Pawn\+St\.?\+?Augustine\+FL", "2493+US+Highway+1+S+St+Augustine+FL+32086", s)
    # collapse repeated city lists produced by the 5→1 substitution
    s = re.sub(r"(?:St\. Augustine(?:,|,? and|,? &(?:amp;)?|, or| or)\s+){1,6}St\. Augustine", "St. Augustine", s)
    s = re.sub(r"across St\. Augustine", "in St. Augustine", s)
    s = re.sub(r"St\. Augustine: Mon[–-]Fri 10am[–-]6pm, Sat 10am[–-]5pm\. St\. Augustine: [^()]*\(closed Wed (?:&|&amp;) Sun\)\.?", "Mon–Fri 10am–6pm, Sat 10am–5pm. Closed Sunday.", s)
    s = re.sub(r"\s*St\. Augustine are open Monday, Tuesday, Thursday, Friday,? and Saturday[^.]*\.", "", s)
    s = re.sub(r"\s*St\. Augustine are open Monday[–-]Friday 10 AM[–-]6 PM and Saturday 10 AM[–-]5 PM;\s*St\. Augustine are open [^.]*\.", " Open Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM.", s)
    s = re.sub(r"St\. Augustine stores\b", "St. Augustine store", s)
    s = re.sub(r"St\. Augustine are open Monday[–-]Friday 10 AM[–-]6 PM and Saturday 10 AM[–-]5 PM; We are closed Sunday\.", "We are open Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM, closed Sunday.", s)
    s = re.sub(r"St\. Augustine are open Monday through Friday", "We are open Monday through Friday", s)
    s = re.sub(r"St\. Augustine are open", "We are open", s)
    s = re.sub(r"our St\. Augustine store — St\. Augustine — ", "our St. Augustine store ", s)
    s = re.sub(r"with stores in St\. Augustine\.", "now in St. Augustine.", s)
    s = re.sub(r"[Ff]ind your nearest store", "find us", s)
    s = s.replace("&#038;", "&amp;").replace("&#8212;", "—").replace("&#8217;", "’")
    s = re.sub(r"St\. Augustine, VA\b", "St. Augustine, FL", s)
    s = re.sub(r"All five stores are closed on Sundays, and some locations are closed Wednesdays too\.", "We are closed on Sundays.", s)
    s = re.sub(r"our St\. Augustine store are closed on Sundays, and some locations are closed Wednesdays too\.", "We are closed on Sundays.", s)
    s = re.sub(r"at all our store: St\. Augustine\.", "at our St. Augustine store.", s)
    s = re.sub(r"at any of our our St\. Augustine store — St\. Augustine\.", "at our St. Augustine store.", s)
    s = re.sub(r"Our St\. Augustine store are open", "Our St. Augustine store is open", s)
    s = re.sub(r"\bany of our our St\. Augustine store\b", "our St. Augustine store", s)
    s = re.sub(r"\bour our St\. Augustine store\b", "our St. Augustine store", s)
    s = re.sub(r"\ball our store\b", "our store", s)
    s = re.sub(r"\b(?:any of )?[Oo]ur our St\. Augustine store are\b", "Our St. Augustine store is", s)
    s = re.sub(r"\bany of our our store\b", "our store", s)
    s = re.sub(r"\b([Oo])ur our\b", r"\1ur", s)
    s = re.sub(r"with our store across Florida(?:’|'|&#8217;|&rsquo;)s First Coast — St\. Augustine\.", "on US-1 South in St. Augustine, Florida.", s)
    s = re.sub(r"St\. Augustine store are\b", "St. Augustine store is", s)
    s = re.sub(r"has five convenient locations across the First Coast — St\. Augustine\.", "is on US-1 South in St. Augustine.", s)
    s = re.sub(r"has our store across the First Coast — St\. Augustine\.", "is on US-1 South in St. Augustine.", s)
    s = re.sub(r"Stop by any of Rocket Pawn (?:&|&amp;) Jewelry(?:’|'|&#8217;)s our St\. Augustine store — St\. Augustine\.", "Stop by our St. Augustine store.", s)
    s = re.sub(r"Stop by our St\. Augustine store — St\. Augustine\.", "Stop by our St. Augustine store.", s)
    s = re.sub(r"Our store are in St\. Augustine\.", "Our store is in St. Augustine.", s)
    s = re.sub(r"We have five convenient locations across Florida — St\. Augustine\.", "We are on US-1 South in St. Augustine.", s)
    s = re.sub(r"\bfive convenient locations\b", "one convenient location", s)
    s = re.sub(r"We have one convenient location across Florida — St\. Augustine\.", "We are on US-1 South in St. Augustine.", s)
    s = re.sub(r"(?<=[a-z]) — St\. Augustine\. We are open", ". We are open", s)
    s = re.sub(r"The St\. Augustine store are open Monday through Friday, 10:00 AM to 6:00 PM, and Saturday, 10:00 AM to 5:00 PM\. The St\. Augustine store are open [^.]*\. We are open on Wednesdays\.", "We are open Monday through Friday, 10:00 AM to 6:00 PM, and Saturday, 10:00 AM to 5:00 PM. Closed Sunday.", s)
    s = re.sub(r"has our store across Florida's First Coast: (?:St\. Augustine \(2493-2495 US Highway 1 South\)(?:, |, and )?)+\.", "has one store, at 2493-2495 US Highway 1 South, St. Augustine, FL 32086.", s)
    s = re.sub(r"How many Rocket Pawn & Jewelry locations are there and where\?", "Where is Rocket Pawn & Jewelry located?", s)
    s = re.sub(r"Mon, Tue, Thu, Fri, Sat 10:00 AM – 6:00 PM · Closed Wed (?:&|&amp;) Sun", "Mon–Fri 10:00 AM – 6:00 PM · Sat 10:00 AM – 5:00 PM · Closed Sun", s)
    s = re.sub(r"Mon, Tue, Thu–Sat 10am–6pm · Closed Wed (?:&|&amp;) Sun", "Mon–Fri 10am–6pm · Sat 10am–5pm · Closed Sun", s)
    s = re.sub(r"St\. Augustine: Mon–Fri 10 AM–6 PM, Sat 10 AM–5 PM\. St\. Augustine: Mon, Tue, Thu, Fri (?:&|&amp;) Sat 10 AM–6 PM \(closed Wed (?:&|&amp;) Sun\)\.", "Open Mon–Fri 10 AM–6 PM, Sat 10 AM–5 PM, closed Sunday.", s)
    s = re.sub(r"query=Valley\+Pawn\+[A-Za-z. +]*?\+VA\b", "query=2493+US+Highway+1+S+St+Augustine+FL+32086", s)
    s = s.replace("Live Inventory from All St. Augustine, FL", "Live Inventory")
    s = s.replace("utm_source=thevalleypawn_site", "utm_source=rocketpawnjewelry_site")
    s = re.sub(r"(utm_content=\w+)_culpeper", r"\1_staugustine", s)
    s = re.sub(r"Locations serving St\. Augustine since 1988\.", "From the family behind ⟪VP⟫ — in the pawn business since 2014.", s)
    s = re.sub(r"with locations serving St\. Augustine since 1988", "from the family behind ⟪VP⟫, in the pawn business since 2014", s)
    s = re.sub(r"with our store across Florida’s First Coast — St\. Augustine\.", "on US-1 South in St. Augustine, Florida.", s)
    s = re.sub(r"maps\.google\.com/maps\?q=[^\"&]*", "maps.google.com/maps?q=2493+US+Highway+1+S+St+Augustine+FL+32086", s)
    s = re.sub(r"Locations have served St\. Augustine since 1988\.", "Opening spring 2027 — from the family behind ⟪VP⟫, serving pawn customers since 2014.", s)
    s = re.sub(r"Rocket Pawn &amp; Jewelry locations have served Florida communities since 1988, and the company", "The family behind Rocket Pawn &amp; Jewelry has run Valley Pawn in Virginia since 2014, and the company", s)
    s = re.sub(r"(?:Valley Pawn|Rocket Pawn (?:&|&amp;) Jewelry) locations have served (?:Virginia|Florida) communities since 1988, and the company", "The family behind Rocket Pawn & Jewelry has run ⟪VP⟫ in Virginia since 2014, and the company", s)
    s = re.sub(r" It is one of three (?:Valley Pawn|Rocket Pawn (?:&|&amp;) Jewelry) stores open on Wednesday \([^)]*\)\.", "", s)
    s = re.sub(r"All five (?:Valley Pawn|Rocket Pawn (?:&|&amp;) Jewelry) stores accept incoming FFL transfers", "We accept incoming FFL transfers", s)
    s = re.sub(r"See all five (?:Valley Pawn|Rocket Pawn (?:&|&amp;) Jewelry) locations →", "", s)
    s = re.sub(r"<h2>What \w[\w. ]* customers say</h2>\s*<p><span class=\"vp-rating\">[^<]*</span>[^<]*</p>\s*<p><a[^>]*>[^<]*</a></p>", "", s)
    s = re.sub(r"<h2>Other (?:Valley Pawn|Rocket Pawn (?:&|&amp;) Jewelry) locations</h2>\s*<ul>.*?</ul>\s*<p><a[^>]*>(?:See all five [^<]*→)?</a></p>", "", s, flags=re.S)
    s = re.sub(r"Hi%20Valley%20Pawn%20(?:Culpeper|Harrisonburg|Lexington|Roanoke|Waynesboro)%21", "Hi%20Rocket%20Pawn%21", s)
    s = re.sub(r"destination=[^\"&]*(?:Culpeper|Harrisonburg|Lexington|Roanoke|Waynesboro)[^\"&]*", "destination=2493%20US%20Highway%201%20S%2C%20St%20Augustine%2C%20FL%2032086", s)
    s = re.sub(r"facebook\.com/RocketPawn(?:Culpeper|Harrisonburg|Lexington|Roanoke|Waynesboro)", "facebook.com/rocketpawnjewelry", s)
    s = re.sub(r"facebook\.com/ValleyPawn(?:Culpeper|Harrisonburg|Lexington|Roanoke|Waynesboro)", "facebook.com/rocketpawnjewelry", s)
    s = re.sub(r"from in St\. Augustine County, Orange, Madison, Remington, Brandy Station, Rixeyville, Warrenton and Sperryville", "from across St. Johns County — St. Augustine Beach, Palencia, Nocatee, Ponte Vedra, Vilano Beach, Hastings and Palm Coast", s)
    s = re.sub(r'"St\. Augustine County", "Orange", "Madison", "Remington", "Brandy Station", "Rixeyville", "Warrenton", "Sperryville"', '"St. Johns County", "St. Augustine Beach", "Palencia", "Nocatee", "Ponte Vedra", "Vilano Beach", "Hastings", "Palm Coast"', s)
    s = re.sub(r"St\. Augustine County", "St. Johns County", s)
    s = re.sub(r"VMI, W&amp;L, Bridgewater, JMU, and EMU", "Flagler College, UNF, Jacksonville University and St. Johns River State College", s)
    s = re.sub(r"Brandy Station, Madison, Reva, Stevensburg, Rixeyville, Mitchells, Orange, and Sperryville", "St. Augustine Beach, Palencia, Nocatee, Ponte Vedra, Vilano Beach, Elkton, Hastings, and Palm Coast", s)
    s = re.sub(r"e\.g\. Brandy Station, Madison, Reva, Stevensburg, Orange", "e.g. St. Augustine Beach, Nocatee, Ponte Vedra, Palm Coast", s)
    s = re.sub(r"Also serving ZIPs: 32086(?:, \d{5})+", "Also serving ZIPs: 32080, 32084, 32092, 32095, 32033, 32145, 32137", s)
    s = re.sub(r"\s*Pick the one closest to you\.", "", s)
    s = re.sub(r"<strong>Hours:</strong>[^<]*", "<strong>Hours:</strong> Mon–Fri 10am–6pm, Sat 10am–5pm. Closed Sunday.", s)
    s = re.sub(r"Closed Wed (?:&|&amp;) Sun — except St\. Augustine, open Wednesdays", "Open Wednesdays; closed Sunday", s)
    s = re.sub(r"St\. Augustine Hours", "Our Hours", s)
    s = re.sub(r"Now in St\. Augustine\. St\. Augustine\. ", "Now in St. Augustine. ", s)
    s = re.sub(r"\bour St\. Augustine store strong across Florida’s First Coast", "One store, one standard, on Florida’s First Coast", s)
    s = s.replace(PROTECT, "Valley Pawn").replace("⟪VA⟫", "Virginia")
    return s

# color remap for the red variant (lowercase hex → hex)
RED_MAP = {"#2d1a5e": "#111111", "#1a0a5e": "#111111", "#1a1a2e": "#0b0b0b", "#0081be": "#c8102e", "#008ed1": "#c8102e",
           "#0099dd": "#c8102e", "#0693e3": "#c8102e", "#9ad9ff": "#f3c0c6", "#e8ddf5": "#eeeeee", "#e8e0f0": "#eeeeee",
           "#7a00df": "#c8102e", "#3858e9": "#c8102e", "#2145e6": "#c8102e", "#3db8e8": "#e23b4a", "#f58c8a": "#c8102e",
           "#3a2474": "#3a0a12", "#5b3d99": "#8c0c20", "#16213e": "#1a1a1a", "#0f3460": "#2a0a10",
           "#0074ad": "#a50d26", "#006ba1": "#9c0c24", "#00679a": "#9c0c24", "#005a87": "#7f0a1e", "#007cba": "#c8102e", "#183ad6": "#c8102e", "#2ea2cc": "#e23b4a"}
def recolor(s):
    if VARIANT != "red": return s
    def rep(m):
        h = m.group(0).lower()
        return RED_MAP.get(h, m.group(0))
    s = re.sub(r"#[0-9a-fA-F]{6}\b", rep, s)
    s = s.replace("rgba(45,26,94", "rgba(17,17,17").replace("rgba(75,55,130", "rgba(60,60,60").replace("rgba(218,165,32", "rgba(200,16,46")
    return s

def sanitize(name):
    # drop query strings from filenames, keep extension
    n = re.sub(r"[?%].*$", "", name)
    base, ext = os.path.splitext(n)
    if not ext:
        m = re.search(r"\.(png|jpg|jpeg|webp|gif|svg|css|js|woff2?|ttf|pdf|ico)", name, flags=re.I)
        ext = "." + m.group(1).lower() if m else ""
    return re.sub(r"[^A-Za-z0-9._-]", "_", base) + ext

copied = {}   # abs source → published relative path
def pub_path(src_abs: Path):
    rel = src_abs.relative_to(MIRROR)
    parts = list(rel.parts)
    host = parts[0]; rest = parts[1:]
    if host == "thevalleypawn.com": folder = "site"
    else: folder = "cdn"
    rest[-1] = sanitize(rest[-1])
    return str(Path(folder, *rest))

DROP_POSTS = ["fall-in-the-shenandoah-valley-what-to-look-forward-to","making-the-most-of-may-in-the-shenandoah-valley","spring-events-shenandoah-valley","summer-in-the-shenandoah-valley-make-the-most-of-it","summer-in-the-shenandoah-valley-your-june-guide"]
SKIP_DIR = re.compile(r"^(" + "|".join(map(re.escape, DROP_POSTS)) + r"|sell-(gold|silver|coins|jewelry)-(culpeper|waynesboro|harrisonburg|lexington|roanoke)|locations/(culpeper|waynesboro|harrisonburg|lexington|roanoke)|culpeper|waynesboro|harrisonburg|lexington|roanoke)$")

REMAP = {"sell-gold": "sell-gold-culpeper", "sell-silver": "sell-silver-culpeper", "sell-coins": "sell-coins-culpeper",
         "sell-jewelry": "sell-jewelry-culpeper", "locations": "locations/culpeper"}
def html_pages():
    for p in SRC.rglob("index.html"):
        rel = p.parent.relative_to(SRC).as_posix()
        if rel == ".": rel = ""
        if SKIP_DIR.match(rel): continue
        if "?" in rel or "%3F" in rel: continue
        if rel in REMAP:
            alt = SRC / REMAP[rel] / "index.html"
            if alt.exists(): p = alt
        yield p, rel
    for n in range(2, 10):
        bp = SRC / "blog" / f"index.html?query-146-page={n}.html"
        if bp.exists(): yield bp, f"blog/page/{n}"

def resolve(href, page_dir: Path):
    href = html.unescape(href).split("#")[0]
    if not href or href.startswith(("http:", "https:", "data:", "mailto:", "tel:", "sms:", "javascript:", "//")): return None
    cand = (page_dir / href).resolve()
    if cand.exists() and cand.is_file(): return cand
    # wget may have saved with %3F encoded
    alt = Path(str(cand).replace("%3F", "?"))
    if alt.exists() and alt.is_file(): return alt
    return None

OUT.mkdir(parents=True, exist_ok=True)
pages = list(html_pages())
print("pages:", len(pages))
ref_re = re.compile(r'''(?:src|href|poster|data-src)=["']([^"']+)["']''')
css_url_re = re.compile(r'''url\((['"]?)([^'")]+)\1\)''')

import base64, mimetypes
INLINE_MAX = 90_000
def data_uri(src_abs: Path):
    ext = re.search(r"\.(png|jpe?g|webp|gif|svg|woff2?|ttf)(?:[?%]|$)", src_abs.name, flags=re.I)
    if not ext: return None
    if src_abs.stat().st_size > INLINE_MAX: return None
    e = ext.group(1).lower()
    mt = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","webp":"image/webp","gif":"image/gif","svg":"image/svg+xml","woff":"font/woff","woff2":"font/woff2","ttf":"font/ttf"}[e]
    return f"data:{mt};base64," + base64.b64encode(src_abs.read_bytes()).decode()

def depth_prefix(rel): return "" if rel == "" else "../" * (rel.count("/") + 1)

def rewrite_city_links(soup):
    for a in soup.find_all("a", href=True):
        h = a["href"]
        m = re.search(r"(sell-(?:gold|silver|coins|jewelry))-(?:culpeper|waynesboro|harrisonburg|lexington|roanoke)/index\.html", h)
        if m: a["href"] = h[:m.start()] + m.group(1) + "/index.html"
        m2 = re.search(r"(?:^|/)(?:locations/)?(?:culpeper|waynesboro|harrisonburg|lexington|roanoke)/index\.html", h)
        if m2: a["href"] = h[:m2.start()] + ("/" if h[:m2.start()] and not h[:m2.start()].endswith("/") else "") + "locations/index.html"

def dedupe_siblings(soup):
    # remove consecutive sibling elements with identical text (5 store cards -> 1)
    for parent in list(soup.find_all(True)):
        kids = [k for k in parent.children if getattr(k, "name", None)]
        seen = set();
        for k in kids:
            txt = re.sub(r"\s+", " ", k.get_text(" ", strip=True))
            key = (k.name, txt, k.get("href") if k.name == "a" else None)
            short_ok = k.name in ("a", "li", "button") and len(txt) > 3
            if (len(txt) > 40 or short_ok) and key in seen:
                k.decompose()
            else:
                seen.add(key)
    # dedupe nav submenu items with identical labels
    for ul in soup.select("ul"):
        seen=set()
        for li in list(ul.find_all("li", recursive=False)):
            t=re.sub(r"\s+"," ",li.get_text(" ",strip=True))
            if t and t in seen: li.decompose()
            else: seen.add(t)

LOGO = {"red": "logo_red.png", "vp": "logo_vp.png"}[VARIANT]
HERO = {"red": "hero_red.jpg", "vp": "hero_vp.jpg"}[VARIANT]

for p, rel in pages:
    raw = p.read_text(encoding="utf-8", errors="ignore")
    raw = raw.replace("</script>script></script>", "</script>")   # live-site typo in an HFCM snippet
    raw = raw.replace('<div class="vp-hero-badge-num">5</div>', '<div class="vp-hero-badge-num">1</div>')
    raw = raw.replace('<div class="vp-hero-badge-lbl">Locations</div>', '<div class="vp-hero-badge-lbl">Location</div>')
    raw = raw.replace('<div class="vp-hero-badge-tag">Across the<br>Shenandoah Valley</div>', '<div class="vp-hero-badge-tag">US-1 South<br>St. Augustine, FL</div>')
    raw = raw.replace("Texting works too — same numbers.", "Texting works too — same number.")
    raw = sub_text(raw)
    raw = recolor(raw)
    soup = BeautifulSoup(raw, "html.parser")
    # strip srcset/sizes to cut image variants
    for t in soup.find_all(["img", "source"]):
        for attr in ("srcset", "sizes", "data-srcset"): t.attrs.pop(attr, None)
    for t in soup.find_all("link", attrs={"rel": "preload"}):
        if t.get("as") == "image": t.decompose()
    # remove external scripts/noise that cannot work statically
    for s_ in soup.find_all("script", src=True):
        if "thevalleypawn.com" not in s_["src"] and not s_["src"].startswith(("wp-", "../")): s_.decompose()
    for s_ in soup.find_all("script", src=False):
        if s_.string and ("spot-prices-feed" not in s_.string) and not re.search(r"VP_GOLD_SPOT|vp-weight|vp-calc|vp-result|STORE_ID", s_.string) and re.search(r"clarity|gtag|googletagmanager|wp\.stats|_stq|jetpack", s_.string): s_.decompose()
    lf = soup.find(id="vp-leaflet-wrap")
    if lf:
        card = BeautifulSoup('<div style="max-width:860px;margin:0 auto;background:#fff;color:#1a1a1a;border-radius:8px;padding:28px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.25)"><p style="font-size:22px;font-weight:700;margin:0 0 6px">Rocket Pawn &amp; Jewelry</p><p style="margin:0 0 14px">2493-2495 US Highway 1 South, St. Augustine, FL 32086</p><a href="https://www.google.com/maps/search/?api=1&amp;query=2493+US+Highway+1+S+St+Augustine+FL+32086" target="_blank" rel="noopener" style="display:inline-block;padding:12px 22px;border-radius:6px;background:#1a1a2e;color:#fff;font-weight:700;text-decoration:none">Get directions</a></div>', "html.parser")
        lf.replace_with(card)
        for sc in soup.find_all("script"):
            if sc.string and "vp-leaflet" in sc.string: sc.decompose()
        for lk in soup.find_all("link", href=True):
            if "leaflet" in lk["href"]: lk.decompose()
    grid = soup.find(class_="vp-nap-grid")
    if grid:
        cols = [c for c in grid.children if getattr(c, "name", None)]
        for c in cols[1:]: c.decompose()
        if cols:
            for note in cols[0].select(".vp-note"): note.decompose()
            hrs = cols[0].select_one(".vp-hrs")
            if hrs: hrs.clear(); hrs.append(BeautifulSoup("Mon–Fri 10am–6pm<br/>Sat 10am–5pm<br/>Closed Sunday", "html.parser"))
        grid["style"] = (grid.get("style") or "") + ";grid-template-columns:1fr;max-width:420px"
    legal = soup.find(class_="vp-foot-legal")
    if legal:
        links = legal.find_all("a")
        legal.clear(); legal.append("Rocket Pawn & Jewelry — 2493-2495 US Highway 1 South, St. Augustine, FL 32086. Mon–Fri 10–6, Sat 10–5, closed Sunday. ")
        for i, a in enumerate(links):
            if i: legal.append(" · ")
            legal.append(a)
    for hh in soup.find_all(["h2", "h3"]):
        if "Customers Say" in hh.get_text():
            sec = hh.find_parent("section") or hh.find_parent("div")
            if sec: sec.decompose()
    for hh in soup.find_all("h2"):
        if re.match(r"Other .*locations", hh.get_text().strip()):
            nxt = [hh]; e = hh
            for _ in range(2):
                e = e.find_next_sibling()
                if e is not None and e.name in ("ul", "p"): nxt.append(e)
            for e in nxt: e.decompose()
    ffl_cards = [c for c in soup.select(".vp-grid .vp-card") if c.select_one(".vp-ffl-num")]
    for c in ffl_cards[1:]: c.decompose()
    if ffl_cards:
        num = ffl_cards[0].select_one(".vp-ffl-num"); num.string = "Pending — ATF Form 7 filed; license number posted when issued"
        dl = ffl_cards[0].select_one(".vp-btn-dl")
        if dl: dl.decompose()
    for hh in soup.find_all("h2"):
        if hh.get_text().strip() == "Choose your pickup location": hh.string = "Your pickup location"
    chips = soup.select_one(".vp-chips")
    if chips: chips.decompose()
    for art in soup.select("article.vp-card"):
        if re.search(r"utm_content=\w+_(?:roanoke|waynesboro|harrisonburg|lexington)", str(art)): art.decompose()
    for para in soup.find_all("p"):
        if re.search(r"at another (?:Valley Pawn|Rocket Pawn & Jewelry) store", para.get_text()): para.decompose()
    sheet = soup.find(id="vp-store-sheet")
    if sheet:
        for li in sheet.find_all(["li", "button", "a"])[1:]:
            pass
    for a in list(soup.find_all("a", href=True)):
        if a.attrs is None or not a.get("href"): continue
        if any(d in a["href"] for d in DROP_POSTS):
            card = a.find_parent(["li", "article"]) or a.find_parent("div", class_=re.compile(r"card|post|wp-block-post\b")) or a
            card.decompose()
    rewrite_city_links(soup)
    dedupe_siblings(soup)
    pre = depth_prefix(rel)
    src_rel = p.parent.relative_to(SRC).as_posix(); src_rel = "" if src_rel == "." else src_rel
    if src_rel != rel:
        # rebase relative links from the source page's folder to the output folder
        def rebase(m):
            url = m.group(1)
            if url.startswith(("http", "data:", "mailto:", "tel:", "sms:", "#", "javascript:", "//")): return m.group(0)
            absu = os.path.normpath(os.path.join(src_rel, url))
            return m.group(0).replace(url, os.path.relpath(absu, start=(rel or ".")))
        out_tmp = re.sub(r'''(?:src|href)=["']([^"']+)["']''', rebase, str(soup))
        soup = BeautifulSoup(out_tmp, "html.parser")
    # logo images
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "vp_logo" in src or "logo" in (img.get("class") and " ".join(img.get("class")) or "").lower():
            img["src"] = pre + "brand/" + LOGO; img["srcset"] = ""; img["alt"] = "Rocket Pawn & Jewelry"
            for a in ("width", "height"): img.attrs.pop(a, None)
            if "vp-hero-logo" in (img.get("class") or []): img["style"] = "max-width:420px;width:100%;height:auto"
    out = str(soup)
    # hero background
    out = re.sub(r"url\(['\"]?[^'\")]*vp-hero-[^'\")]*['\"]?\)", f"url('{pre}brand/{HERO}')", out)
    # spot prices feed → static snapshot
    out = out.replace("'/wp-json/wp/v2/pages?slug=spot-prices-feed&_fields=content'", f"'{pre}spot-prices.json'")
    out = out.replace('"/wp-json/wp/v2/pages?slug=spot-prices-feed&_fields=content"', f'"{pre}spot-prices.json"')
    # rewrite asset references to sanitized paths and collect files
    def fix_ref(m):
        url = m.group(1)
        src_abs = resolve(url, SRC / rel if rel else SRC)
        if not src_abs: return m.group(0)
        if src_abs.suffix.lower() in (".html", ".htm") or src_abs.name.startswith("index.html"): return m.group(0)
        du = data_uri(src_abs)
        if du: return m.group(0).replace(url, du)
        pubp = pub_path(src_abs); copied[src_abs] = pubp
        # relative from this page
        relp = os.path.relpath(pubp, start=(rel or "."))
        return m.group(0).replace(url, relp)
    out = ref_re.sub(fix_ref, out)
    def fix_css(m):
        url = m.group(2)
        src_abs = resolve(url, SRC / rel if rel else SRC)
        if not src_abs: return m.group(0)
        du = data_uri(src_abs)
        if du: return f"url('{du}')"
        pubp = pub_path(src_abs); copied[src_abs] = pubp
        return f"url('{os.path.relpath(pubp, start=(rel or '.'))}')"
    out = css_url_re.sub(fix_css, out)
    def fix_pag(m):
        n = m.group(1)
        return 'href="' + os.path.relpath(f"blog/page/{n}", start=(rel or ".")) + '/index.html"'
    out = re.sub(r'href="(?:\.\./)*index\.html%3Fquery-146-page=(\d+)(?:&(?:amp;)?cst)?\.html(#[^"]*)?"', lambda m: fix_pag(m)[:-1] + (m.group(2) or "") + '"', out)
    out = re.sub(r'href="((?:\.\./)*)index\.html%3Fcst\.html(#[^"]*)?"', lambda m: f'href="{m.group(1)}index.html{m.group(2) or ""}"', out)
    out = re.sub(r"(sell-(?:gold|silver|coins|jewelry))-(?:culpeper|waynesboro|harrisonburg|lexington|roanoke)/index\.html", r"\1/index.html", out)
    out = re.sub(r'href="((?:\.\./)*)(?:locations/)?(?:culpeper|waynesboro|harrisonburg|lexington|roanoke)/index\.html', r'href="\1locations/index.html', out)
    out = re.sub(r'href="locations/index\.html', 'href="index.html', out) if rel == "locations" else out
    out = re.sub(r'href="\.\./1/index\.html', 'href="../../index.html', out) if rel.startswith("blog/page/") else out
    out = re.sub(r'href="((?:\.\./)*app/)index\.html%3Futm[^"]*"', r'href="\1index.html"', out)
    dest = OUT / rel / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")

# copy assets (and process css for nested urls + recolor)
for src_abs, pubp in list(copied.items()):
    d = OUT / pubp; d.mkdir if False else None
    d.parent.mkdir(parents=True, exist_ok=True)
    if src_abs.suffix.lower().startswith(".css") or ".css" in src_abs.name:
        css = src_abs.read_text(encoding="utf-8", errors="ignore")
        css = recolor(css)
        def fix_css2(m):
            url = m.group(2)
            s2 = resolve(url, src_abs.parent)
            if not s2: return m.group(0)
            pp = pub_path(s2)
            if s2 not in copied:
                copied[s2] = pp
                dd = OUT / pp; dd.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(s2, dd)
            return f"url('{os.path.relpath(pp, start=os.path.dirname(pubp))}')"
        css = css_url_re.sub(fix_css2, css)
        d.write_text(css, encoding="utf-8")
    else:
        shutil.copy2(src_abs, d)

# brand assets + spot snapshot
(OUT / "brand").mkdir(exist_ok=True)
for f in (LOGO, HERO):
    if (ASSETS / f).exists(): shutil.copy2(ASSETS / f, OUT / "brand" / f)
    else: print("MISSING asset", f)
(OUT / "spot-prices.json").write_text(json.dumps([{"content": {"rendered": "<p class=\"wp-block-paragraph\">gold: 3876.40<br>silver: 49.25<br>updated: 2026-11-01T07:00:04-05:00</p>", "protected": False}}]))
n = sum(1 for _ in OUT.rglob("*") if _.is_file())
print("files:", n, "size MB:", round(sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())/1e6, 1))
