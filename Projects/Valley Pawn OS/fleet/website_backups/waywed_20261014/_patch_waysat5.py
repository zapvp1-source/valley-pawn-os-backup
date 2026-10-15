#!/usr/bin/env python3
"""Waynesboro 6-day hours (Joshua 2026-10-14): open Wed, Sat 10-5. Builds new content for every WP item from the
_full/ backups. Writes _new/<key>.raw.html for changed items + _new/changes.json. Push is a separate step."""
import re, glob, os, json
D = os.path.dirname(os.path.abspath(__file__))
FULL, NEW = os.path.join(D, "_full"), os.path.join(D, "_new")
os.makedirs(NEW, exist_ok=True)
A = r"(?:&amp;|&#038;|&)"  # ampersand forms

WAY_FILES = {"pages_420", "pages_510", "pages_595", "pages_600", "pages_605"}  # Waynesboro-only pages

GLOBAL = [
  # canonical footer line (spokes, retail)
  (re.compile(r"Culpeper ("+A+r") Roanoke: Mon–Fri 10(\s?)(am|AM)–6(\s?)(pm|PM), Sat 10\s?(?:am|AM)–5\s?(?:pm|PM)\. Harrisonburg, Waynesboro "+A+r" Lexington: "),
   lambda m: "Culpeper, Roanoke %s Waynesboro: Mon–Fri 10%s%s–6%s%s, Sat 10%s%s–5%s%s. Harrisonburg %s Lexington: " % (
       m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(2), m.group(3), m.group(4), m.group(5), m.group(1))),
  # blog sign-offs
  (re.compile(r"(Our )?Culpeper and Roanoke( stores)? are open (Monday[^.;<]*?5 PM)([.;]) (?:Harrisonburg, Waynesboro,? and Lexington|Waynesboro, Harrisonburg,? and Lexington) are open"),
   lambda m: "%sCulpeper, Roanoke and Waynesboro%s are open %s%s Harrisonburg and Lexington are open" % (m.group(1) or "", m.group(2) or "", m.group(3), m.group(4))),
  # footer legal line
  (re.compile(r"closed Wednesday except Culpeper and Roanoke\. Culpeper and Roanoke close at 5 PM on Saturdays\."),
   lambda m: "closed Wednesday except Culpeper, Roanoke and Waynesboro. Culpeper, Roanoke and Waynesboro close at 5 PM on Saturdays."),
  # homepage
  (re.compile(r"Closed Wed ("+A+r") Sun — except Culpeper "+A+r" Roanoke, open Wednesdays"),
   lambda m: "Closed Wed %s Sun — except Culpeper, Roanoke %s Waynesboro, open Wednesdays" % (m.group(1), m.group(1))),
  (re.compile(r"Culpeper ("+A+r") Roanoke Hours"), lambda m: "Culpeper, Roanoke %s Waynesboro Hours" % m.group(1)),
  # location FAQ (CUL/ROA pages)
  (re.compile(r"It is one of two Valley Pawn stores open on Wednesday \(Culpeper and Roanoke\)\."),
   lambda m: "It is one of three Valley Pawn stores open on Wednesday (Culpeper, Roanoke and Waynesboro)."),
  # HAR/LEX location FAQ suggestion
  (re.compile(r"If you need a store on a Wednesday, our Culpeper and Roanoke locations are open 10 AM–6 PM\."),
   lambda m: "If you need a store on a Wednesday, our Culpeper, Roanoke and Waynesboro locations are open 10 AM–6 PM."),
  # FAQ page 739
  (re.compile(r"Culpeper ("+A+r") Roanoke:(\s*</strong>|\s*</b>)?"), None),  # handled specially below
  # careers
  (re.compile(r"most locations are closed Wednesdays too"), lambda m: "some locations are closed Wednesdays too"),
]

def way_after(s, anchor_re, old_re, new, window=700):
    """Replace the first old_re match within `window` chars after each anchor match."""
    out, pos, n = [], 0, 0
    for am in re.finditer(anchor_re, s):
        if am.start() < pos: continue
        seg = s[am.end(): am.end() + window]
        om = re.search(old_re, seg)
        if not om: continue
        a, b = am.end() + om.start(), am.end() + om.end()
        out.append(s[pos:a]); out.append(new(om) if callable(new) else new); pos = b; n += 1
    out.append(s[pos:])
    return "".join(out), n

def patch(key, s):
    o = s; notes = []
    if key in WAY_FILES:
        reps = [
          (r"<tr><td>Wednesday</td><td>Closed</td></tr>", "<tr><td>Wednesday</td><td>10:00 AM – 6:00 PM</td></tr>"),
          (r"<tr><td>Saturday</td><td>10:00 AM – 6:00 PM</td></tr>", "<tr><td>Saturday</td><td>10:00 AM – 5:00 PM</td></tr>"),
          (r"Monday, Tuesday, Thursday, Friday and Saturday 10 AM–6 PM \(closed Wednesday and Sunday\)", "Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM (closed Sunday)"),
          (r"Open Monday, Tuesday, Thursday, Friday and Saturday 10 AM–6 PM \(closed Wednesday and Sunday\)", "Open Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM (closed Sunday)"),
          (r"Mon, Tue, Thu, Fri ("+A+r") Sat 10:00 AM – 6:00 PM · Closed Wednesday "+A+r" Sunday", "Monday–Friday, 10:00 AM – 6:00 PM · Saturday, 10:00 AM – 5:00 PM · Closed Sunday"),
          (r"No\. Valley Pawn Waynesboro is closed on Wednesdays and Sundays\. If you need a store on a Wednesday, our Culpeper and Roanoke locations are open 10 AM–6 PM\.",
           "Yes. Valley Pawn Waynesboro is open Wednesdays, 10 AM–6 PM. It is one of three Valley Pawn stores open on Wednesday (Culpeper, Roanoke and Waynesboro). On Saturday, Waynesboro is open 10 AM–5 PM."),
          # JSON-LD (both compact and spaced forms)
          (r'"dayOfWeek": \["Monday", "Tuesday", "Thursday", "Friday", "Saturday"\], "opens": "10:00", "closes": "18:00"\}',
           '"dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "10:00", "closes": "18:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday"], "opens": "10:00", "closes": "17:00"}'),
          (r'"dayOfWeek": \["Monday","Tuesday","Thursday","Friday","Saturday"\], "opens": "10:00", "closes": "18:00" \}',
           '"dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "10:00", "closes": "18:00" }, { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday"], "opens": "10:00", "closes": "17:00" }'),
        ]
        for a, b in reps:
            s, k = re.subn(a, b, s)
            if k: notes.append("WAY %s x%d" % (a[:30], k))
    for rx, fn in GLOBAL:
        if fn is None: continue
        s, k = rx.subn(fn, s)
        if k: notes.append("%s x%d" % (rx.pattern[:40], k))
    # FAQ page 739 hours answer
    if key == "pages_739":
        s2 = re.sub(r"Culpeper ("+A+r") Roanoke:", lambda m: "Culpeper, Roanoke %s Waynesboro:" % m.group(1), s, count=1)
        s2 = s2.replace("Waynesboro, Harrisonburg, Lexington:", "Harrisonburg, Lexington:", 1)
        if s2 != s: notes.append("739 hours answer"); s = s2
    # Waynesboro-specific blocks (anchor = Waynesboro address)
    WADDR = r"1321 West Broad St(?:reet)?(?:<br>|, )Waynesboro, VA 22980"
    rules = [
      # footer card
      (r"<h2>Waynesboro</h2>\s*<p class=\"vp-addr\">1321 West Broad St<br>Waynesboro, VA 22980</p>\s*",
       r"<p class=\"vp-hrs\">Mon, Tue, Thu, Fri, Sat<br>10am&ndash;6pm</p>",
       '<p class="vp-hrs">Mon&ndash;Fri 10am&ndash;6pm<br>Sat 10am&ndash;5pm<br><span class="vp-note">Open Wednesdays</span></p>'),
      # hub cards
      (WADDR + r"</p>", r"Mon, Tue, Thu–Sat 10am–6pm · Closed Wed "+A+r" Sun", "Mon–Fri 10am–6pm · Sat 10am–5pm · Closed Sunday"),
      # contact
      (WADDR + r"<br>", r"Mon, Tue, Thu, Fri, Sat 10:00 AM – 6:00 PM · Closed Wed "+A+r" Sun", "Monday–Friday 10:00 AM – 6:00 PM · Saturday 10:00 AM – 5:00 PM · Closed Sunday"),
      # /locations/ and /locations/waynesboro/
      (WADDR + r"</p>", r"🕐 Mon, Tue, Thu, Fri, Sat: 10am–6pm(?: \| Closed Wed "+A+r" Sun)?", "🕐 Mon–Fri: 10am–6pm | Sat: 10am–5pm | Closed Sunday"),
      # ffl transfer
      (r"mailto:waynesboro@fcfpawn\.com", r"Mon, Tue, Thu, Fri "+A+r" Sat 10am&ndash;6pm \(closed Wed "+A+r" Sun\)", "Mon&ndash;Fri 10am&ndash;6pm, Sat 10am&ndash;5pm"),
    ]
    for anchor, old, new in rules:
        s, k = way_after(s, anchor, old, new)
        if k: notes.append("WAY block %s x%d" % (old[:30], k))
    return s, notes

changes = {}
for f in sorted(glob.glob(os.path.join(FULL, "*.raw.html"))):
    key = os.path.basename(f)[:-9]
    s = open(f).read()
    n, notes = patch(key, s)
    if n != s:
        open(os.path.join(NEW, key + ".raw.html"), "w").write(n)
        changes[key] = notes
json.dump(changes, open(os.path.join(NEW, "changes.json"), "w"), indent=1)
print(len(changes), "items changed")
for k, v in changes.items(): print(k, "; ".join(v))
