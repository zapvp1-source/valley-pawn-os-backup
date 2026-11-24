#!/usr/bin/env python3
"""Rocket Pawn & Jewelry — build the publishable site from website_black_red/.

Source folder is never edited. Output: site_prelaunch/ (rebuilt from scratch every run).
Flip the CFG values below as facts become public, rerun, re-import:
  - address_public: True the day the lease is executed
  - phone: '(904) xxx-xxxx' once the store number exists
  - hours: the approved hours text once Joshua sets them
  - social: real handles once each account is created
"""
import json, os, re, shutil, sys, tempfile, zipfile, hashlib
from pathlib import Path
from bs4 import BeautifulSoup, Comment

HERE = Path(__file__).resolve().parent
SRC = HERE / 'website_black_red'
# Build in a scratch folder (the project folder does not allow deletes); the shippable
# result is the zip written to _preview/rocket_site_prelaunch.zip
OUT = Path(os.environ.get('RP_OUT', Path(tempfile.gettempdir()) / 'rocket_site_prelaunch'))
ZIP = HERE / '_preview' / 'rocket_site_prelaunch.zip'

CFG = dict(
    address_public=True,      # Joshua 11/22: use the lease address (2493-2495 US-1 S)
    street='2493-2495 US Highway 1 South', city='St. Augustine', zip='32086',
    phone=None,            # e.g. '(904) 555-0123'
    hours='Mon, Tue, Thu, Fri & Sat 10am–6pm · Closed Wed & Sun',   # Joshua 11/22
    email='hello@rocketpawnjewelry.com',
    social={},             # e.g. {'facebook': 'https://www.facebook.com/rocketpawnjewelry'}
    app=False,             # True once Bravo confirms store 6 is in the MobilePawn app
    opening='Opening early 2027',
)
SHORT_ADDR = 'US-1 South, St. Augustine, FL'
OPEN_DAYS = ['Monday', 'Tuesday', 'Thursday', 'Friday', 'Saturday']   # 10 AM–6 PM; closed Wednesday and Sunday
HOURS_SENTENCE = ('Once we open in early 2027, our hours are Monday, Tuesday, Thursday, Friday and Saturday, '
                  '10 AM–6 PM (closed Wednesday and Sunday).')
# Same feed the Mac updates every morning for the Virginia stores (CORS allows rocketpawnjewelry.com)
SPOT_FEED = 'https://thevalleypawn.com/wp-json/wp/v2/pages?slug=spot-prices-feed&_fields=content'
POST_IMPORT = HERE / 'post_import'   # page scripts WordPress strips on import; re-inserted as HTML blocks

def current_spot():
    """Fallback spot = today's value from the store feed, so a failed live fetch is never far off."""
    import urllib.request
    try:
        raw = urllib.request.urlopen(SPOT_FEED, timeout=15).read().decode()
        g = re.search(r'gold:\s*([0-9.]+)', raw); sv = re.search(r'silver:\s*([0-9.]+)', raw)
        return (float(g.group(1)), float(sv.group(1))) if g and sv else None
    except Exception:
        return None
SPOT = current_spot()

def is_post(html):
    m = re.search(r'<body[^>]*class="([^"]*)"', html)
    return bool(m and 'single-post' in m.group(1))

# ---------- decide which pages ship ----------
pages, dropped = {}, set()
for f in sorted(SRC.rglob('*.html')):
    rel = f.relative_to(SRC)
    top = rel.parts[0] if len(rel.parts) > 1 else ''
    html = f.read_text(encoding='utf8', errors='surrogateescape')
    if is_post(html) or top == 'blog' or (top == 'app' and not CFG['app']):
        dropped.add(top)
        continue
    pages[rel] = html
dropped.discard('')

# ---------- text-level fixes (body text AND attributes) ----------
HOURS_SENT = re.compile(
    r"(?:(?:We are|we are|We're|Our St\. Augustine store is|The St\. Augustine store is|Open)\s+open\s+|Open\s+)"
    r"[^.<\"]{0,40}?Monday[^.<\"]{0,120}?(?:Sunday|5 PM|5:00 PM|5pm)\)?\.?", re.I)
HOURS_LINES = [
    'Mon–Fri 10am–6pm<br/>Sat 10am–5pm<br/>Closed Sunday',
    'Mon–Fri 10–6, Sat 10–5, closed Sunday.',
    'Monday–Friday, 10:00 AM – 6:00 PM · Saturday, 10:00 AM – 5:00 PM · Closed Sunday',
    'Monday–Friday 10:00 AM – 6:00 PM · Saturday 10:00 AM – 5:00 PM · Closed Sunday',
    'Mon–Fri 10:00 AM – 6:00 PM · Sat 10:00 AM – 5:00 PM · Closed Sun',
    'Mon–Fri 10am–6pm · Sat 10am–5pm · Closed Sunday',
    'Mon–Fri 10am–6pm · Sat 10am–5pm · Closed Sun',
    'Mon–Fri 10am–6pm, Sat 10am–5pm. Closed Sunday.',
    'Mon–Fri 10am–6pm, Sat 10am–5pm',
    '🕐 Mon–Fri: 10am–6pm | Sat: 10am–5pm | Closed Sunday',
]

def text_fixes(h):
    h = h.replace('info@rocketpawnjewelry.com', CFG['email'])
    # 11/22: grammar fix + sell-* map iframe pointed at a Valley Pawn VA query
    h = h.replace('Yes. our St. Augustine store accept incoming', 'Yes. Our St. Augustine store accepts incoming')
    h = h.replace('store accept incoming', 'store accepts incoming')
    import re as _re
    h = _re.sub(r'maps\?q=Valley\+Pawn\+St\.(%20| )Augustine\+VA', 'maps?q=2493+US+Highway+1+S+St+Augustine+FL+32086', h)
    h = _re.sub(r'We buy (gold|silver|coins|jewelry) at every Rocket Pawn (&amp;|&) Jewelry store\.', r'We buy \1 at our St. Augustine store.', h)
    h = _re.sub(r'Find Your Nearest Rocket Pawn (&amp;|&) Jewelry →', 'Find Our St. Augustine Store →', h)
    h = h.replace('Send a quick photo to your nearest store.', 'Send us a quick photo.')
    h = h.replace('Coming to US-1 South in St. Augustine, early 2027.', 'Coming to 2493-2495 US Highway 1 South, St. Augustine, early 2027.')
    h = h.replace('Whats Right is RIGHT', 'What’s Right is RIGHT')
    # JSON-LD hygiene (11/22)
    h = h.replace('wp-content/uploads/2026/03/vp_logo_name-no-tag.png', 'wp-content/uploads/2026/11/logo_red.png').replace('https://i0.wp.com/rocketpawnjewelry.com/', 'https://rocketpawnjewelry.com/')
    h = _re.sub(r'/(sell-(?:gold|silver|coins|jewelry))-staugustine/', r'/\1/', h)
    h = h.replace(' — Our Store', '')
    h = h.replace('All 5 Rocket Pawn & Jewelry locations buy silver: St. Augustine.', 'Our St. Augustine store buys silver.')
    h = h.replace('Rocket Pawn & Jewelry is on US-1 South in St. Augustine and buys jewelry and you can walk in any time during business hours.', 'Rocket Pawn & Jewelry has one store, at 2493-2495 US Highway 1 South in St. Augustine. Walk in any time during business hours.')
    h = h.replace('then text or call Rocket Pawn & Jewelry', 'then email or visit Rocket Pawn & Jewelry')
    h = h.replace('?cc=jdavis%40fcfpawn.com&amp;subject=Valley%20Pawn%20Application', '?subject=Rocket%20Pawn%20Application')
    h = h.replace('Valley%20Pawn%20Culpeper', 'Rocket%20Pawn')
    h = h.replace('Part of the family that runs five Valley Pawn stores in Virginia.',
                  'From the family behind Valley Pawn, in the pawn business since 2014.')
    h = h.replace('Fifteen-plus years of pawn experience.', 'In the pawn business since 2014.')
    if not CFG['address_public']:
        s = CFG['street']
        h = h.replace(f'{s}<br/>St. Augustine, FL 32086', 'US-1 South<br/>St. Augustine, FL')
        h = h.replace(f'{s}, St. Augustine, FL 32086', SHORT_ADDR)
    hours_line = CFG['hours'] or CFG['opening']
    for line in HOURS_LINES:
        h = h.replace(line, hours_line)
    h = HOURS_SENT.sub(HOURS_SENTENCE if CFG['hours'] else 'We open on US-1 South in early 2027.', h)
    if not CFG['address_public']:
        h = h.replace(CFG['street'], 'US-1 South')
    h = re.sub(r'(\(closed Wednesday and Sunday\)\.)\s*(?:\(closed Sunday\)\.?|,?\s*closed Sunday\.)', r'\1', h)
    h = h.replace('Open Mon–Fri 10 AM–6 PM, Sat 10 AM–5 PM, closed Sunday.',
                  HOURS_SENTENCE if CFG['hours'] else 'We open in early 2027.')
    h = re.sub(r'Mon – Fri<br/><strong[^>]*>10 AM – 6 PM</strong><br/>Saturday<br/><strong[^>]*>10 AM – 5 PM</strong><br/><span[^>]*>Closed Sunday</span>',
               ('Mon, Tue, Thu, Fri &amp; Sat<br/><strong style="color:#0b0b0b;">10 AM – 6 PM</strong><br/>'
                '<span style="color:#999;font-size:13px;">Closed Wednesday &amp; Sunday · Opening early 2027</span>')
               if CFG['hours'] else '<strong style="color:#0b0b0b;">' + CFG['opening'] + '</strong>', h)
    if not CFG['phone']:
        h = re.sub(r'[Cc]all or text <a href="tel:[^"]+">[^<]*</a> or email ', 'Email ', h)
        h = re.sub(r'Call or text \(904\) 000-0000\.?', f"Email {CFG['email']}.", h)
        h = h.replace("'sms:+' + STORE_PHONE_RAW + '?&body='",
                      "'mailto:" + CFG['email'] + "?subject=' + encodeURIComponent('Quote request') + '&body='")
        h = h.replace("STORE_PHONE_RAW = '19040000000'", "STORE_PHONE_RAW = ''")
    for amp in ('&amp;', '&'):
        for a, b in [
            (f"at all 5 Rocket Pawn {amp} Jewelry locations across Florida", "at our St. Augustine store"),
            (f"at all 5 Rocket Pawn {amp} Jewelry locations", "at our St. Augustine store"),
            (f"at any of Rocket Pawn {amp} Jewelry's 5 Florida locations", f"at Rocket Pawn {amp} Jewelry in St. Augustine"),
            (f"at any of Rocket Pawn {amp} Jewelry’s 5 Florida locations", f"at Rocket Pawn {amp} Jewelry in St. Augustine"),
            (f"great deals on guns, tools {amp} electronics. Call or text any of our 5 Florida stores.",
             f"great deals on tools {amp} electronics. Opening early 2027 on US-1 South in St. Augustine."),
            (f"Call or text Rocket Pawn {amp} Jewelry on US-1 South.", f"Rocket Pawn {amp} Jewelry, opening early 2027 on US-1 South."),
            (f"any Rocket Pawn {amp} Jewelry location can help get the process started", "we’ll get the process started"),
        ]:
            h = h.replace(a, b)
    for a, b in [
        ('at any of our 5 Florida locations', 'at our St. Augustine store'),
        (' - free appraisals at 5 Florida locations.', ' - free appraisals in St. Augustine.'),
        (' across 5 Florida locations.', '.'),
        (' - 5 Florida locations.', ' in St. Augustine.'),
        ('See open roles across our 5 Florida stores and apply today.', 'Join the team opening our St. Augustine store in early 2027.'),
        ('Open Mon-Sat. Call or text before you come.', 'Opening early 2027.'),
        ('Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM (closed Sunday).',
         HOURS_SENTENCE if CFG['hours'] else 'We open on US-1 South in early 2027 and will post our hours before opening day.'),
        ("with our store across Florida's First Coast", "on US-1 South in St. Augustine, Florida,"),
        ('Just call or text the store', 'Just email us'),
        ('visit our stores,', 'visit our store,'),
        ('Phone, text and email for all 5 First Coast stores, plus addresses, hours and directions.',
         'Opening early 2027 on US-1 South in St. Augustine. Email us any time.'),
        ('has our store across Florida: St. Augustine. Each location buys jewelry', 'is on US-1 South in St. Augustine and buys jewelry'),
        ('You can now find addresses, hours, phone numbers, email and directions for our St. Augustine store in one place',
         'Contact details for our St. Augustine store are in one place'),
        ('Rocket Pawn Site — Black &amp; Red', 'Rocket Pawn &amp; Jewelry | Pawn Shop &amp; Gold Buyer in St. Augustine, FL'),
        ('Rocket Pawn Site — Black & Red', 'Rocket Pawn & Jewelry | Pawn Shop & Gold Buyer in St. Augustine, FL'),
        ('Contact Rocket Pawn &amp; Jewelry | Call or Text Any of Our St. Augustine, FL', 'Contact Rocket Pawn &amp; Jewelry | St. Augustine, FL'),
        ('Contact Rocket Pawn & Jewelry | Call or Text Any of Our St. Augustine, FL', 'Contact Rocket Pawn & Jewelry | St. Augustine, FL'),
        ('Rocket Pawn &amp; Jewelry Florida Locations', 'Rocket Pawn &amp; Jewelry St. Augustine'),
        ('Rocket Pawn & Jewelry Florida Locations', 'Rocket Pawn & Jewelry St. Augustine'),
        ("or get directions to our 5 First Coast locations. We're open Mon-Sat, no appointment needed.",
         "opening early 2027 on US-1 South in St. Augustine, FL. Email us any time."),
        ('Shop live inventory from Rocket Pawn &amp; Jewelry in St. Augustine, Florida — tools, electronics, jewelry, instruments and more, inspected, tested and backed by our 30-day warranty.',
         'Tools, electronics, jewelry, instruments and more from Rocket Pawn &amp; Jewelry in St. Augustine, Florida, every piece backed by our 30-day warranty. Our online shop opens with the store in early 2027.'),
        ('Now hiring at Rocket Pawn &amp; Jewelry. Competitive pay, real advancement, and a team that treats people right. ', ''),
        ('Now hiring at Rocket Pawn & Jewelry. Competitive pay, real advancement, and a team that treats people right. ', ''),
        ('locations/culpeper/', 'locations/'), ('%2Flocations%2Fculpeper%2F', '%2Flocations%2F'),
    ]:
        h = h.replace(a, b)
    h = re.sub(r'<h3>Is Rocket Pawn &amp; Jewelry St\. Augustine open on Wednesday\?</h3>\s*<p>.*?</p>', '', h, flags=re.S)
    if not CFG['phone']:
        for a, b in [('Call or text us first.', 'Email us first.'), ('Questions? Call or text us', 'Questions? Email us'),
                     ('>Call or text us<', '>Get in touch<'), ('just call or text the store', 'just email us'),
                     ('text or call us', 'email us')]:
            h = h.replace(a, b)
        h = re.sub(r'\bText us\b', 'Email us', h)
        h = re.sub(r'(?<![\w-])text us\b', 'email us', h)
    # pre-opening wording
    for a, b in [
        ('Now in St. Augustine. Your neighborhood pawn shop.', 'Coming to US-1 South in St. Augustine, early 2027. Your neighborhood pawn shop.'),
        ('Pick your nearest Rocket Pawn &amp; Jewelry location and walk in today.', 'Visit us on US-1 South when we open in early 2027.'),
        ('Pick the store nearest you. Every location buys', 'We buy'),
        ('Pick the store nearest you. Each location buys', 'We buy'),
        ('Every location buys', 'We buy'), ('Each location buys', 'We buy'),
        ('Stop by any Rocket Pawn &amp; Jewelry — no appointment needed.', 'No appointment needed.'),
        ('Walk out with cash today', 'Same-day cash'),
        ('walk in today', 'stop in'),
    ]:
        h = h.replace(a, b)
    if not CFG['phone']:
        h = re.sub(r'Texting works too — same number\.\s*<a href="([^"]+)">All addresses &amp; hours →</a>',
                   r'Opening early 2027 on US-1 South. <a href="\1">Store details →</a>', h)
        h = re.sub(r'(<div style="font-size:36px;margin-bottom:10px;">)📱(</div>\s*<h3[^>]*>)Text Us(</h3>\s*<p[^>]*>)Click the chat button<br/>in the bottom right corner<br/><strong([^>]*)>Quick answers, fast service</strong> ⚡',
                   r'\1✉️\2Email Us\3' + CFG['email'] + r'<br/><strong\4>A real person answers</strong>', h)
        h = h.replace('text a photo', 'email a photo').replace('Text a photo', 'Email a photo')
    h = re.sub(r"fetch\('(?:\.\./)*spot-prices\.json'", "fetch('" + SPOT_FEED + "'", h)
    if SPOT:
        h = re.sub(r'window\.VP_GOLD_SPOT = [0-9.]+;', f'window.VP_GOLD_SPOT = {SPOT[0]:.2f};', h)
        h = re.sub(r'window\.VP_SILVER_SPOT = [0-9.]+;', f'window.VP_SILVER_SPOT = {SPOT[1]:.2f};', h)
    h = re.sub(r'Shop live inventory from Rocket Pawn (&amp;|&) Jewelry in St\. Augustine, Florida[^"<]*?warranty\.',
               r'Tools, electronics, jewelry, instruments and more from Rocket Pawn \1 Jewelry in St. Augustine, Florida, every piece backed by our 30-day warranty. Our online shop opens with the store in early 2027.', h)
    h = h.replace("'culpeper'", "'staugustine'").replace('-culpeper', '-staugustine')
    # internal build notes left in HTML comments
    h = re.sub(r'<!--(?:(?!-->).)*?(?:Master Template|Category hub for).*?-->', '', h, flags=re.S)
    return h

# ---------- JSON-LD cleanup ----------
VA = ('lexington', 'roanoke', 'waynesboro', 'harrisonburg', 'culpeper')
def clean_ld(o):
    if isinstance(o, dict) and o.get('@type') == 'Question':
        nm = str(o.get('name', ''))
        if 'hours' in nm.lower():
            o['acceptedAnswer'] = {'@type': 'Answer', 'text': HOURS_SENTENCE if CFG['hours']
                                   else f"{CFG['opening']}. We'll post our hours before opening day."}
        elif nm == 'Where are your stores?':
            o['name'] = 'Where are you located?'
            o['acceptedAnswer'] = {'@type': 'Answer', 'text': (f"{CFG['street']}, St. Augustine, FL {CFG['zip']}. Opening early 2027."
                                   if CFG['address_public'] else 'One store, on US-1 South in St. Augustine, Florida. Opening early 2027.')}
    if isinstance(o, dict):
        for k in list(o):
            v = o[k]
            if k in ('aggregateRating', 'review'):
                del o[k]; continue
            if k == 'telephone' and not CFG['phone']:
                del o[k]; continue
            if k in ('openingHoursSpecification', 'openingHours'):
                if CFG['hours']:
                    o[k] = [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': OPEN_DAYS, 'opens': '10:00', 'closes': '18:00'}] \
                        if k == 'openingHoursSpecification' else 'Mo,Tu,Th,Fr,Sa 10:00-18:00'
                else:
                    del o[k]
                continue
            if k in ('streetAddress', 'postalCode', 'hasMap') and not CFG['address_public']:
                del o[k]; continue
            if k == 'addressRegion':
                o[k] = 'FL'; continue
            if k == 'sameAs':
                o[k] = list(CFG['social'].values())
                if not o[k]: del o[k]
                continue
            if isinstance(v, str) and any(f'/locations/{c}' in v for c in VA):
                del o[k]; continue
            o[k] = clean_ld(v)
        return o
    if isinstance(o, list):
        o = [x for x in o if not (isinstance(x, dict) and 'open on Wednesday' in str(x.get('name', '')))]
        return [clean_ld(x) for x in o
                if not (isinstance(x, dict) and any(f'/locations/{c}' in json.dumps(x) for c in VA) and len(x) <= 2)]
    if isinstance(o, str):
        return text_fixes(o) if not CFG['hours'] else o
    return o

# ---------- pages rewritten for a single, not-yet-open store ----------
BTN = ('display:inline-block;padding:12px 26px;border-radius:999px;background:#c8102e;color:#fff;'
       'font-weight:700;text-decoration:none')
WRAP = '<section style="max-width:780px;margin:56px auto;padding:0 20px;line-height:1.65;font-size:1.05rem">'
PAGE_BODY = {
 'ffl-transfer/index.html': WRAP + '''
<h1 style="font-size:2.2rem;margin:0 0 6px">FFL Transfers</h1>
<p style="color:#c8102e;font-weight:700;margin:0 0 22px">What’s Right Is Right</p>
<p>Buying a firearm online or from an out-of-state seller? Federal law requires it to ship to a licensed dealer
(an FFL) for pickup. Rocket Pawn &amp; Jewelry will accept incoming firearm transfers once our Federal Firearms
License is issued and the store opens on US-1 South in St. Augustine in early 2027. Our license application
is filed with the ATF; we will post our license number and a signed copy of the license here as soon as it is issued.</p>
<h2>How transfers will work</h2>
<ol>
<li><strong>Contact us first</strong> so we know a transfer is coming.</li>
<li><strong>Send your seller our FFL.</strong> We will provide a signed copy of our license for the shipping dealer.</li>
<li><strong>Have it shipped to the store</strong>, with your name and the order number on the package.</li>
<li><strong>Pick it up in person</strong> with a valid government-issued photo ID, complete ATF Form 4473 and pass the
background check. You must be 21 or older. Every transfer follows federal and Florida law.</li>
</ol>
<p>Our transfer fee will be posted before opening.</p>
<p><a href="mailto:{email}?subject=FFL%20transfer" style="''' + BTN + '''">✉️ Ask about a transfer</a></p>
</section>''',
 'careers/index.html': WRAP + '''
<h1 style="font-size:2.2rem;margin:0 0 10px">Come work where What’s Right Is Right</h1>
<p>Rocket Pawn &amp; Jewelry opens on US-1 South in St. Augustine in early 2027. We’re from the family behind
Valley Pawn, in the pawn business since 2014, and we run things the same way: fair, data-driven appraisals,
a 30-day warranty on everything we sell, and a team treated like family.</p>
<h2>What the job is</h2>
<p>You’ll help customers buy, sell, pawn and pick up — writing loans, evaluating jewelry, gold, tools and
electronics with our appraisal tools, keeping the showroom sharp and building the kind of regulars who ask for
you by name. We’ll teach you the pawn business.</p>
<h2>What we look for</h2>
<ul>
<li>Honest people who like people. Retail, sales, jewelry or customer-service experience helps; attitude matters more.</li>
<li>21 or older, able to work Saturdays and lift up to 50 lbs (with or without reasonable accommodation).</li>
<li>Able to pass the background screening required to work in a licensed pawn business.</li>
</ul>
<h2>How to apply</h2>
<p>We’ll be hiring ahead of opening. Email your résumé, or just a note about yourself, and we’ll be in touch.</p>
<p><a href="mailto:{email}?subject=Rocket%20Pawn%20Application" style="''' + BTN + '''">✉️ Apply by email</a></p>
<p style="font-size:.9rem;color:#666;margin-top:28px">Rocket Pawn &amp; Jewelry (Full Circle Finance Inc) is an equal
opportunity employer. All qualified applicants will receive consideration for employment without regard to race, color,
religion, sex, sexual orientation, gender identity, national origin, age, disability, veteran status, or any other
characteristic protected by law.</p>
</section>''',
 'contact/index.html': WRAP + '''
<h1 style="font-size:2.2rem;margin:0 0 12px">Contact Rocket Pawn &amp; Jewelry</h1>
<p>We open on US-1 South in St. Augustine, Florida, in early 2027. Until then, email is the fastest way to reach us
— questions about loans, selling gold or jewelry, firearm transfers or jobs all come to the same inbox, and a real
person answers.</p>
<p><a href="mailto:{email}" style="''' + BTN + '''">✉️ {email}</a></p>
<p>Our store phone number, hours and map will be posted here before opening day.</p>
</section>''',
 'retail/index.html': WRAP + '''
<h1 style="font-size:2.2rem;margin:0 0 12px">Weekly deals start on opening day</h1>
<p>Every week we’ll post hand-picked markdowns from the St. Augustine store — tools, jewelry, electronics,
instruments and more, priced well below retail and backed by our 30-day warranty. The first deals go up when
we open in early 2027.</p>
<p><a href="mailto:{email}?subject=Weekly%20deals" style="''' + BTN + '''">✉️ Send me the deals</a></p>
</section>''',
}

# ---------- structural fixes ----------
def target_top(href, rel):
    if not href or href.startswith(('http', 'mailto:', 'tel:', 'sms:', '#', 'javascript:')):
        return None
    p = os.path.normpath(os.path.join(os.path.dirname(str(rel)), href.split('#')[0].split('?')[0]))
    parts = Path(p).parts
    return parts[0] if parts and parts[0] not in ('.', '..') else None

def email_link(soup, like, label='✉️ Email us', subject=None):
    a = soup.new_tag('a', href=f"mailto:{CFG['email']}" + (f'?subject={subject}' if subject else ''))
    for att in ('class', 'style'):
        if like.get(att): a[att] = like.get(att)
    a.string = label
    return a

def fix_soup(soup, rel):
    # directions links to the street address
    if not CFG['address_public']:
        for a in soup.find_all('a', href=True):
            if '2493' in a['href']:
                a.decompose()
    # phone links
    if not CFG['phone']:
        for a in soup.find_all('a', href=re.compile(r'^tel:')):
            a.replace_with(email_link(soup, a))
        for a in soup.find_all('a', href=re.compile(r'^sms:')):
            body = re.search(r'body=([^&]+)', a['href'])
            prev = a.find_previous_sibling('a')
            if body:
                a.replace_with(email_link(soup, a, label=a.get_text(strip=True) or '✉️ Email us', subject=body.group(1)[:120]))
            elif prev is not None and prev.get('href', '').startswith('mailto:'):
                a.decompose()
            else:
                a.replace_with(email_link(soup, a))
        for el in soup.find_all(string=re.compile(r'\(904\) 000-0000')):
            par = el.parent
            if par and par.name == 'span':
                par.decompose()
            else:
                el.replace_with(el.replace('(904) 000-0000', ''))
    # per-day hours table
    for h2 in soup.find_all('h2'):
        if h2.get_text(strip=True) == 'Hours':
            t = h2.find_next_sibling()
            if t is not None and t.name == 'table':
                if CFG['hours']:
                    rows = ''.join(f"<tr><td>{d}</td><td>{'10:00 AM – 6:00 PM' if d in OPEN_DAYS else 'Closed'}</td></tr>"
                                   for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
                    t.replace_with(BeautifulSoup(f'<table>{rows}</table><p>Opening early 2027.</p>', 'html.parser'))
                else:
                    p = soup.new_tag('p'); p.string = f"{CFG['opening']}. We'll post our hours here before the doors open."
                    t.replace_with(p)
    # app card on locations page
    if not CFG['app']:
        for h3 in soup.find_all('h3'):
            if 'MobilePawn' in h3.get_text():
                h3.string = 'Free layaway'
                p = h3.find_next_sibling('p')
                if p is not None:
                    p.clear(); p.append('Put an item on free layaway and pay it off over time — no fees and no credit check.')
    # white landing-page header needs the light-background logo
    for img in soup.select('header.vp-header img'):
        if img.get('src', '').endswith('logo_red.png'):
            img['src'] = img['src'][:-len('logo_red.png')] + 'logo_light.png'
            for att in ('srcset', 'data-orig-file', 'data-large-file'):
                img.attrs.pop(att, None)
    # fake star rating
    for d in soup.select('.vp-hero-stars'):
        d.decompose()
    # social icon rows + the multi-page Facebook switcher block
    if not CFG['social']:
        for ul in soup.select('ul.wp-block-social-links'):
            ul.decompose()
        for h2 in soup.find_all('h2'):
            if h2.get_text(strip=True).startswith('Connect With'):
                box = h2.find_parent('div', style=re.compile('100vw'))
                inner = h2.parent
                for sib in list(inner.children):
                    if sib is not h2 and getattr(sib, 'name', None) != 'img':
                        sib.extract() if hasattr(sib, 'extract') else None
                h2.string = 'Be first through the door'
                p = soup.new_tag('p', style='color:#e0e0e0;font-size:15px;margin:0 0 25px;')
                p.string = f"{CFG['opening']} on US-1 South in St. Augustine. Email us for opening-day news and deals."
                btn = soup.new_tag('a', href=f"mailto:{CFG['email']}?subject=Opening%20day%20updates",
                                   style='display:inline-block;padding:12px 26px;border-radius:999px;background:#c8102e;color:#fff;font-weight:700;text-decoration:none')
                btn.string = '✉️ Keep me posted'
                h2.insert_after(p); p.insert_after(btn)
    # links to pages that no longer ship
    for a in soup.find_all('a', href=True):
        t = target_top(a['href'], rel)
        if t and t in dropped:
            li = a.find_parent('li')
            if li is not None and (li.find_parent('nav') or 'menu' in ' '.join(li.get('class', []))):
                li.decompose()
            else:
                a.unwrap()
    # map embed: city only until the address is public
    if not CFG['address_public']:
        for fr in soup.find_all('iframe', src=re.compile('maps')):
            fr['src'] = 'https://maps.google.com/maps?q=St+Augustine+FL&output=embed'
    # FAQ: hours + store list
    if True:
        for h3 in soup.find_all(['h3', 'h4']):
            q = h3.get_text(strip=True)
            if q in ('What are your hours?', 'Where are your stores?'):
                nxt = h3.find_next_sibling()
                while nxt is not None and nxt.name not in ('h2', 'h3', 'h4'):
                    dead, nxt = nxt, nxt.find_next_sibling()
                    dead.decompose()
                p = soup.new_tag('p')
                if q.startswith('What are'):
                    p.string = HOURS_SENTENCE if CFG['hours'] else f"{CFG['opening']}. We'll post our hours here before opening day."
                else:
                    h3.string = 'Where are you located?'
                    p.string = (f"{CFG['street']}, St. Augustine, FL {CFG['zip']}. Opening early 2027."
                                if CFG['address_public'] else 'One store, on US-1 South in St. Augustine, Florida. Opening early 2027.')
                h3.insert_after(p)
    if str(rel) in PAGE_BODY:
        main = soup.find('main')
        if main:
            main.clear()
            main.append(BeautifulSoup(PAGE_BODY[str(rel)].format(**CFG), 'html.parser'))
    # shop: no inventory until the store opens
    if str(rel) == 'shop/index.html':
        main = soup.find('main')
        if main:
            main.clear()
            sec = BeautifulSoup(
                f'<section style="max-width:760px;margin:60px auto;padding:0 20px;text-align:center">'
                f'<h1 style="font-size:2.2rem;margin:0 0 12px">Shop online — coming with our opening</h1>'
                f'<p style="font-size:1.1rem;line-height:1.6">Jewelry, tools, electronics, instruments and more, every piece '
                f'backed by our 30-day warranty. Our online shop goes live when the St. Augustine store opens in early 2027.</p>'
                f'<p><a href="mailto:{CFG["email"]}?subject=Shop%20updates" style="display:inline-block;padding:12px 26px;'
                f'border-radius:999px;background:#c8102e;color:#fff;font-weight:700;text-decoration:none">✉️ Tell me when it opens</a></p>'
                f'</section>', 'html.parser')
            main.append(sec)
    # JSON-LD
    for s in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(s.string or '')
        except Exception:
            continue
        s.string = json.dumps(clean_ld(data), ensure_ascii=False)

# ---------- build ----------
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT, ignore=lambda d, n: [x for x in n if x.startswith('.') or x == '_to_delete'
                                              or (Path(d) == SRC and x in dropped)])
for f in list(OUT.rglob('*.html')):
    if f.relative_to(OUT) not in pages:
        f.unlink()
for rel, html in pages.items():
    h = text_fixes(html)
    if not CFG['app']:
        h = re.sub(r'<!-- VP-APP-BANNER-START -->.*?<!-- VP-APP-BANNER-END -->', '', h, flags=re.S)
    soup = BeautifulSoup(h, 'lxml')
    fix_soup(soup, rel)
    (OUT / rel).write_text(str(soup), encoding='utf8', errors='surrogateescape')
# prune empty dirs left by removed pages
for d in sorted(OUT.rglob('*'), key=lambda p: -len(p.parts)):
    if d.is_dir() and not any(d.iterdir()):
        d.rmdir()
# WordPress removes <script> from imported page content: save each page's scripts (spot loader
# from <head> + the page's own calculator/FAQ code) for re-insertion as one Custom HTML block
POST_IMPORT.mkdir(exist_ok=True)
for rel in pages:
    soup = BeautifulSoup((OUT / rel).read_text(encoding='utf8'), 'lxml')
    main = soup.find('main')
    if not main:
        continue
    own = [x.get_text() for x in main.find_all('script') if not x.get('src') and x.get('type') in (None, 'text/javascript')]
    if not own:
        continue
    head = [x.get_text() for x in soup.find_all('script') if not x.get('src') and x.find_parent('main') is None
            and ('VP_GOLD_SPOT' in x.get_text() or 'VP_PAYOUT' in x.get_text())]
    slug = rel.parts[0] if len(rel.parts) > 1 else 'home'
    (POST_IMPORT / f'{slug}.html').write_text(
        '<!-- wp:html -->\n' + ''.join(f'<script>{t}</script>\n' for t in head)
        + ''.join("<script>document.addEventListener('DOMContentLoaded',function(){" + t + "});</script>\n" for t in own)
        + '<!-- /wp:html -->', encoding='utf8')
ZIP.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(OUT.rglob('*')):
        if f.is_file():
            z.write(f, f.relative_to(OUT))
print('pages shipped', len(pages), '| page folders dropped', len(dropped))
print('zip', ZIP, ZIP.stat().st_size, hashlib.sha256(ZIP.read_bytes()).hexdigest())
print('build dir', OUT)
