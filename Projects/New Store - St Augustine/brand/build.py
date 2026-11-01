#!/usr/bin/env python3
"""Builds three artifact pages: brand review, Rocket Pawn site, Lighthouse Pawn site."""
import os
OUT = "/home/claude/staug/brand"

# ---------- LOGOS (original SVG) ----------
# Rocket palette
RN, RO, RG, RS = "#0B1E3A", "#F26B1D", "#D4A62A", "#EAF2FA"
# Lighthouse palette
LN, LA, LT, LSAND = "#10263F", "#F2B134", "#2A8C9E", "#F3EBDD"

def rocket1(w=420, n=RN, o=RO, g=RG, font="Saira, 'Arial Narrow', sans-serif"):
    """Launch mark: rocket on a 45° climb inside a diamond, wordmark right."""
    return f'''<svg viewBox="0 0 420 150" width="{w}" role="img" aria-label="Rocket Pawn &amp; Jewelry logo concept 1" style="max-width:100%;height:auto">
<g transform="translate(20,10)">
 <polygon points="65,0 130,65 65,130 0,65" fill="{n}"/>
 <polygon points="65,14 116,65 65,116 14,65" fill="none" stroke="{g}" stroke-width="3"/>
 <g transform="translate(65,65) rotate(-45)">
  <path d="M0,-44 C12,-30 14,-6 10,18 L-10,18 C-14,-6 -12,-30 0,-44 Z" fill="#fff"/>
  <circle cx="0" cy="-14" r="6" fill="{n}"/>
  <path d="M-10,8 L-22,24 L-8,20 Z" fill="{o}"/><path d="M10,8 L22,24 L8,20 Z" fill="{o}"/>
  <path d="M-7,20 L0,42 L7,20 Z" fill="{o}"/><path d="M-3,20 L0,32 L3,20 Z" fill="{g}"/>
 </g>
</g>
<text x="170" y="62" font-family="{font}" font-weight="800" font-size="46" letter-spacing="1" fill="{n}">ROCKET</text>
<text x="170" y="106" font-family="{font}" font-weight="800" font-size="46" letter-spacing="1" fill="{o}">PAWN</text>
<text x="172" y="130" font-family="Saira, Arial, sans-serif" font-weight="600" font-size="15" letter-spacing="5" fill="{g}">&amp; JEWELRY</text>
</svg>'''

def rocket2(w=260, n=RN, o=RO, g=RG):
    """Orbit badge: round seal, orbit ring, gem at apogee."""
    return f'''<svg viewBox="0 0 260 260" width="{w}" role="img" aria-label="Rocket Pawn &amp; Jewelry logo concept 2" style="max-width:100%;height:auto">
<circle cx="130" cy="130" r="124" fill="{n}"/>
<circle cx="130" cy="130" r="112" fill="none" stroke="{g}" stroke-width="2"/>
<ellipse cx="130" cy="130" rx="92" ry="34" fill="none" stroke="{o}" stroke-width="4" transform="rotate(-28 130 130)"/>
<g transform="translate(130,118) rotate(-20)">
 <path d="M0,-40 C11,-27 13,-5 9,17 L-9,17 C-13,-5 -11,-27 0,-40 Z" fill="#fff"/>
 <circle cx="0" cy="-12" r="5.5" fill="{n}"/>
 <path d="M-9,8 L-20,22 L-7,19 Z" fill="{o}"/><path d="M9,8 L20,22 L7,19 Z" fill="{o}"/>
 <path d="M-6,19 L0,38 L6,19 Z" fill="{o}"/>
</g>
<g transform="translate(205,86)"><polygon points="0,-11 9,-3 0,13 -9,-3" fill="{g}"/><polygon points="-9,-3 9,-3 0,-11" fill="#fff" opacity=".7"/></g>
<text x="130" y="188" text-anchor="middle" font-family="Saira, 'Arial Narrow', sans-serif" font-weight="800" font-size="26" letter-spacing="1" textLength="190" lengthAdjust="spacingAndGlyphs" fill="#fff">ROCKET PAWN</text>
<text x="130" y="212" text-anchor="middle" font-family="Saira, Arial, sans-serif" font-weight="600" font-size="11" letter-spacing="3" textLength="170" lengthAdjust="spacingAndGlyphs" fill="{g}">&amp; JEWELRY · ST. AUGUSTINE</text>
</svg>'''

def rocket3(w=440, n=RN, o=RO, g=RG, font="Saira, 'Arial Narrow', sans-serif"):
    """Wordmark: condensed type with a fin on the R and an exhaust underline."""
    return f'''<svg viewBox="0 0 440 130" width="{w}" role="img" aria-label="Rocket Pawn &amp; Jewelry logo concept 3" style="max-width:100%;height:auto">
<text x="10" y="74" font-family="{font}" font-weight="900" font-size="74" textLength="268" lengthAdjust="spacingAndGlyphs" fill="{n}">ROCKET</text>
<text x="288" y="74" font-family="{font}" font-weight="900" font-size="74" textLength="142" lengthAdjust="spacingAndGlyphs" fill="{o}">PAWN</text>
<path d="M10,88 L300,88" stroke="{o}" stroke-width="6" stroke-linecap="round"/>
<path d="M300,88 L340,88" stroke="{g}" stroke-width="6" stroke-linecap="round" opacity=".8"/>
<path d="M340,88 L368,88" stroke="{g}" stroke-width="6" stroke-linecap="round" opacity=".4"/>
<polygon points="378,80 408,88 378,96 384,88" fill="{n}"/>
<text x="12" y="118" font-family="Saira, Arial, sans-serif" font-weight="600" font-size="16" letter-spacing="5" textLength="400" lengthAdjust="spacingAndGlyphs" fill="{n}">&amp; JEWELRY  ·  LOANS  ·  GOLD</text>
</svg>'''

def rocket4(w=300, n=RN, o=RO, g=RG, font="Saira, 'Arial Narrow', sans-serif", fg=None):
    """Shield crest: vertical rocket with a gem nose inside a shield, wordmark below."""
    fg = fg or n
    return f'''<svg viewBox="0 0 300 300" width="{w}" role="img" aria-label="Rocket Pawn &amp; Jewelry logo concept 4" style="max-width:100%;height:auto">
<path d="M150,14 L252,44 L244,150 C240,200 200,236 150,254 C100,236 60,200 56,150 L48,44 Z" fill="{n}"/>
<path d="M150,32 L234,57 L227,148 C223,190 190,220 150,235 C110,220 77,190 73,148 L66,57 Z" fill="none" stroke="{o}" stroke-width="4"/>
<g transform="translate(150,135)">
 <path d="M0,-78 C20,-56 24,-16 16,34 L-16,34 C-24,-16 -20,-56 0,-78 Z" fill="#fff"/>
 <polygon points="0,-78 10,-62 -10,-62" fill="{g}"/>
 <circle cx="0" cy="-26" r="9" fill="{n}"/>
 <path d="M-16,8 L-38,40 L-14,34 Z" fill="{o}"/><path d="M16,8 L38,40 L14,34 Z" fill="{o}"/>
 <path d="M-11,34 L0,72 L11,34 Z" fill="{o}"/><path d="M-5,34 L0,54 L5,34 Z" fill="{g}"/>
</g>
<text x="150" y="282" text-anchor="middle" font-family="{font}" font-weight="900" font-size="30" textLength="236" lengthAdjust="spacingAndGlyphs" fill="{fg}">ROCKET PAWN</text>
</svg>'''

def rocket5(w=300, n=RN, o=RO, g=RG, font="Saira, 'Arial Narrow', sans-serif", fg=None):
    """Monogram: a bold R whose leg is a rocket exhaust, inside a ring; name set around the base."""
    fg = fg or n
    return f'''<svg viewBox="0 0 300 300" width="{w}" role="img" aria-label="Rocket Pawn &amp; Jewelry logo concept 5" style="max-width:100%;height:auto">
<circle cx="150" cy="150" r="140" fill="{n}"/>
<circle cx="150" cy="150" r="126" fill="none" stroke="{o}" stroke-width="5"/>
<text x="140" y="196" text-anchor="middle" font-family="{font}" font-weight="900" font-size="150" fill="#fff">R</text>
<g transform="translate(184,150) rotate(35)">
 <path d="M0,-30 C9,-20 10,-4 7,14 L-7,14 C-10,-4 -9,-20 0,-30 Z" fill="{g}"/>
 <path d="M-7,6 L-16,18 L-6,16 Z" fill="{o}"/><path d="M7,6 L16,18 L6,16 Z" fill="{o}"/>
 <path d="M-5,16 L0,40 L5,16 Z" fill="{o}"/>
</g>
<path d="M70,226 Q150,276 230,226" fill="none" stroke="{o}" stroke-width="3" opacity=".6"/>
<text x="150" y="250" text-anchor="middle" font-family="{font}" font-weight="700" font-size="17" letter-spacing="4" textLength="180" lengthAdjust="spacingAndGlyphs" fill="#fff">ROCKET PAWN</text>
<text x="150" y="266" text-anchor="middle" font-family="{font}" font-weight="600" font-size="10" letter-spacing="3" textLength="110" lengthAdjust="spacingAndGlyphs" fill="{g}">&amp; JEWELRY</text>
</svg>'''

def rocket6(w=440, n=RN, o=RO, g=RG, font="Saira, 'Arial Narrow', sans-serif", fg=None):
    """Trail arc: rocket crossing above the name, its trail sweeping under the letters and looping the ampersand."""
    fg = fg or n
    return f'''<svg viewBox="0 0 500 150" width="{w}" role="img" aria-label="Rocket Pawn &amp; Jewelry logo concept 6" style="max-width:100%;height:auto">
<path d="M18,118 C140,140 340,136 452,48" fill="none" stroke="{o}" stroke-width="5" stroke-linecap="round"/>
<path d="M18,118 C90,128 160,132 230,130" fill="none" stroke="{g}" stroke-width="5" stroke-linecap="round" opacity=".55"/>
<g transform="translate(458,42) rotate(45)">
 <path d="M0,-34 C10,-23 12,-5 8,16 L-8,16 C-12,-5 -10,-23 0,-34 Z" fill="{fg}"/>
 <circle cx="0" cy="-11" r="5" fill="{o}"/>
 <path d="M-8,6 L-18,20 L-6,18 Z" fill="{o}"/><path d="M8,6 L18,20 L6,18 Z" fill="{o}"/>
 <path d="M-5,18 L0,36 L5,18 Z" fill="{g}"/>
</g>
<text x="18" y="92" font-family="{font}" font-weight="900" font-size="66" textLength="238" lengthAdjust="spacingAndGlyphs" fill="{fg}">ROCKET</text>
<text x="262" y="92" font-family="{font}" font-weight="900" font-size="66" textLength="122" lengthAdjust="spacingAndGlyphs" fill="{o}">PAWN</text>
<text x="20" y="36" font-family="{font}" font-weight="600" font-size="15" letter-spacing="6" textLength="200" lengthAdjust="spacingAndGlyphs" fill="{g}">&amp; JEWELRY · ST. AUGUSTINE</text>
</svg>'''

def light1(w=440):
    """Beacon tower: spiral-striped tower (the St. Augustine light) with beam rays, wordmark right."""
    stripes = "".join(f'<path d="M{44-i*2},{30+i*22} l44,-8 l0,10 l-44,8 z" fill="{LN}"/>' for i in range(5))
    return f'''<svg viewBox="0 0 440 150" width="{w}" role="img" aria-label="Lighthouse Pawn &amp; Jewelry logo concept 1" style="max-width:100%;height:auto">
<g transform="translate(14,4)">
 <path d="M60,8 L86,22 L60,36 L34,22 Z" fill="{LA}"/>
 <circle cx="60" cy="22" r="7" fill="#fff"/>
 <path d="M86,16 L120,4 M86,22 L124,22 M86,28 L120,40" stroke="{LA}" stroke-width="4" stroke-linecap="round"/>
 <path d="M34,16 L0,4 M34,22 L-4,22 M34,28 L0,40" stroke="{LA}" stroke-width="4" stroke-linecap="round"/>
 <polygon points="42,36 78,36 88,136 32,136" fill="#fff" stroke="{LN}" stroke-width="3"/>
 <clipPath id="tower1"><polygon points="42,36 78,36 88,136 32,136"/></clipPath>
 <g clip-path="url(#tower1)">{stripes}</g>
 <rect x="26" y="134" width="68" height="10" rx="2" fill="{LT}"/>
</g>
<text x="160" y="60" font-family="'Alfa Slab One', Georgia, serif" font-size="40" textLength="262" lengthAdjust="spacingAndGlyphs" fill="{LN}">LIGHTHOUSE</text>
<text x="160" y="104" font-family="'Alfa Slab One', Georgia, serif" font-size="40" fill="{LT}">PAWN</text>
<text x="162" y="130" font-family="Mulish, Arial, sans-serif" font-weight="700" font-size="14" letter-spacing="3" textLength="262" lengthAdjust="spacingAndGlyphs" fill="{LA}">&amp; JEWELRY · ST. AUGUSTINE</text>
</svg>'''

def light2(w=260):
    """Beam seal: round badge, beam cone lighting a diamond."""
    return f'''<svg viewBox="0 0 260 260" width="{w}" role="img" aria-label="Lighthouse Pawn &amp; Jewelry logo concept 2" style="max-width:100%;height:auto">
<circle cx="130" cy="130" r="124" fill="{LN}"/>
<circle cx="130" cy="130" r="113" fill="none" stroke="{LSAND}" stroke-width="2" stroke-dasharray="4 6"/>
<path d="M78,70 L236,30 L236,110 Z" fill="{LA}" opacity=".9"/>
<path d="M78,70 L236,30 L236,70 Z" fill="#fff" opacity=".25"/>
<polygon points="70,52 86,52 90,150 66,150" fill="#fff"/>
<rect x="70" y="52" width="16" height="14" fill="{LN}"/><rect x="69" y="92" width="18" height="14" fill="{LN}"/><rect x="68" y="130" width="20" height="14" fill="{LN}"/>
<path d="M64,52 L92,52 L78,36 Z" fill="{LA}"/>
<g transform="translate(192,70)"><polygon points="0,-14 12,-4 0,16 -12,-4" fill="#fff"/><polygon points="-12,-4 12,-4 0,-14" fill="{LA}"/></g>
<text x="130" y="186" text-anchor="middle" font-family="'Alfa Slab One', Georgia, serif" font-size="22" textLength="196" lengthAdjust="spacingAndGlyphs" fill="#fff">LIGHTHOUSE PAWN</text>
<text x="130" y="210" text-anchor="middle" font-family="Mulish, Arial, sans-serif" font-weight="700" font-size="11" letter-spacing="3" textLength="150" lengthAdjust="spacingAndGlyphs" fill="{LA}">&amp; JEWELRY · ST. AUGUSTINE</text>
</svg>'''

def light3(w=440):
    """Wordmark: the L is a striped tower; a single beam underlines the name."""
    return f'''<svg viewBox="0 0 440 130" width="{w}" role="img" aria-label="Lighthouse Pawn &amp; Jewelry logo concept 3" style="max-width:100%;height:auto">
<g transform="translate(12,10)">
 <polygon points="12,14 30,14 36,78 6,78" fill="{LN}"/>
 <rect x="13" y="26" width="16" height="9" fill="{LA}"/><rect x="11" y="48" width="20" height="9" fill="{LA}"/>
 <path d="M6,14 L36,14 L21,0 Z" fill="{LA}"/>
 <rect x="30" y="66" width="30" height="12" fill="{LN}"/>
</g>
<text x="74" y="86" font-family="'Alfa Slab One', Georgia, serif" font-size="56" textLength="352" lengthAdjust="spacingAndGlyphs" fill="{LN}">IGHTHOUSE</text>
<text x="12" y="118" font-family="Mulish, Arial, sans-serif" font-weight="800" font-size="19" letter-spacing="6" textLength="220" lengthAdjust="spacingAndGlyphs" fill="{LT}">PAWN &amp; JEWELRY</text>
<path d="M240,112 L432,112" stroke="{LA}" stroke-width="5" stroke-linecap="round"/>
</svg>'''

ROCKET = [
 ("Launch Mark", rocket1, "Fair deals, lightning fast.", "Diamond badge (jewelry) with the rocket on a 45° climb. Works as an app icon, a pylon panel and an embroidered polo. Primary recommendation."),
 ("Orbit Seal", rocket2, "Where your money takes off.", "Round seal with an orbit ring and a gem at apogee. Strong on a window decal, a receipt header and social avatars."),
 ("Exhaust Wordmark", rocket3, "St. Augustine's launchpad for loans, gold and great finds.", "Type-only with an exhaust underline. Reads at highway speed on a fascia sign and needs no icon to carry it."),
]
LIGHT = [
 ("Beacon Tower", light1, "Your guiding light on the First Coast.", "The spiral-striped tower is a direct nod to the St. Augustine Light, the most recognized landmark in the county. Primary recommendation."),
 ("Beam Seal", light2, "Steady. Honest. Here when you need us.", "Round seal: the beam lights a diamond. Reads as a trust mark on receipts, decals and review-request cards."),
 ("Tower Wordmark", light3, "A fair deal you can see from anywhere.", "The L is the tower. Type-only, one color if needed, built for the fascia sign and embroidery."),
]

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira:wght@600;800;900&family=Russo+One&family=Bebas+Neue&family=Chakra+Petch:wght@600;700&family=Source+Sans+3:wght@400;600;700&family=Alfa+Slab+One&family=Mulish:wght@400;700;800&display=swap">'

# ---------- BRAND REVIEW PAGE ----------
def card(name, fn, tag, note):
    return f'''<article class="concept"><div class="art">{fn()}</div><h3>{name}</h3><p class="tag">“{tag}”</p><p class="note">{note}</p></article>'''

review = f'''<title>St. Augustine Brand Concepts</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}
<style>
/* Layout: two brand chapters, each a three-up gallery of logo concepts; a comparison table closes the page. */
:root{{--bg:#F7F8FA;--fg:#14202E;--muted:#5B6B7C;--card:#FFFFFF;--line:#D9E0E8;--rocket:{RO};--rnavy:{RN};--gold:{RG};--lamber:{LA};--lnavy:{LN};--lteal:{LT}}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:'Source Sans 3',system-ui,sans-serif;font-size:17px;line-height:1.55;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:1100px;margin:0 auto}}
h1{{font-family:Saira,sans-serif;font-weight:800;font-size:clamp(28px,4vw,40px);letter-spacing:.5px;margin:0 0 6px;text-wrap:balance}}
.lead{{color:var(--muted);max-width:70ch;margin:0 0 36px}}
h2{{font-size:clamp(22px,3vw,28px);margin:48px 0 4px;text-wrap:balance}}
h2 small{{display:block;font-size:13px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:6px}}
.chapter p.intro{{color:var(--muted);max-width:70ch;margin:0 0 20px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}
.concept{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px;display:flex;flex-direction:column;gap:8px;min-width:0}}
.art{{background:#fff;border-radius:6px;padding:16px;display:flex;align-items:center;justify-content:center;min-height:200px}}
.concept h3{{margin:8px 0 0;font-size:19px}}
.tag{{font-size:20px;font-weight:700;margin:0;line-height:1.3}}
.rocket .tag{{color:var(--rocket)}} .light .tag{{color:var(--lteal)}}
.note{{color:var(--muted);font-size:15px;margin:0}}
table{{border-collapse:collapse;width:100%;font-size:15px;margin-top:12px}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--muted)}}
.wrap{{overflow-x:auto}}
.verdict{{background:var(--card);border-left:6px solid var(--rocket);padding:18px 22px;border-radius:0 10px 10px 0;margin:28px 0 0}}
.verdict strong{{font-size:18px}}
a{{color:var(--lteal)}}
</style>
<main>
<h1>St. Augustine store — name &amp; logo concepts</h1>
<p class="lead">Two finalists, three logo directions each, with a tagline per direction. Every mark is original vector art drawn for this review; the first concept in each set is the one the website mockups use.</p>

<section class="chapter rocket">
<h2><small>Finalist 1</small>Rocket Pawn &amp; Jewelry</h2>
<p class="intro">Distinctive, fast to say, nothing like it on the First Coast. Navy, rocket orange and a gold accent for the jewelry side of the business.</p>
<div class="gallery">{''.join(card(*c) for c in ROCKET)}</div>
</section>

<section class="chapter light">
<h2><small>Finalist 2</small>Lighthouse Pawn &amp; Jewelry</h2>
<p class="intro">Borrows the county's most recognized landmark. Deep sea navy, beacon amber, coastal teal. Reads as steady and local before a customer ever walks in.</p>
<div class="gallery">{''.join(card(*c) for c in LIGHT)}</div>
</section>

<h2><small>Why these two</small>Name scorecard</h2>
<div class="wrap"><table>
<tr><th>Name</th><th>Local search conflicts</th><th>Domain</th><th>USPTO (class 036, live marks, checked 10/31)</th><th>Read</th></tr>
<tr><td><strong>Rocket Pawn &amp; Jewelry</strong></td><td>None in Florida. One unrelated shop in Lawton, OK.</td><td>rocketpawn.com is for sale on Atom at $4,299 (sale price, ends ~11/3; lease-to-own $237/mo). rocketpawnjewelry.com, rocketpawnandjewelry.com, rocketpawnfl.com open at $13.</td><td>No “ROCKET PAWN” mark exists. But Rocket Mortgage LLC holds registrations for ROCKET alone (financial services, lending), ROCKET LOANS (consumer lending) and ROCKET MONEY (loan financing, consumer lending), all live in class 036. A pawn loan is consumer lending in the same class, so a federal registration for Rocket Pawn would likely be refused and Rocket Companies could object to the use. A local DBA is still usable; it just can't be owned.</td><td>Best marketing name; carries a real trademark exposure that an IP attorney should price before signage is ordered.</td></tr>
<tr><td><strong>Lighthouse Pawn &amp; Jewelry</strong></td><td>No pawn shop by this name found in FL/GA. The St. Augustine Lighthouse &amp; Maritime Museum is a nonprofit, not a competitor.</td><td>lighthousepawn.com and lighthousepawnjewelry.com both open at $13.</td><td>44 live LIGHTHOUSE marks in class 036, none for pawn shops or consumer lending to the public (investment managers, insurers, a commercial lender, realtors). “Lighthouse” is a crowded, weak word in finance, which cuts both ways: low risk of a challenge, low ability to stop others.</td><td>Strongest local identity; safest to use; harder to own nationally (irrelevant for one store).</td></tr>
<tr><td>Coastal Pawn &amp; Jewelry</td><td>Coastal Pawn in Kingsland GA (1 hr north), Hinesville, Jesup, Latta SC; Palm Coast Pawn &amp; Jewelry 30 min south; Space Coast Pawn in Titusville.</td><td>coastalpawn.com taken.</td><td>No pawn mark, but the name is generic.</td><td>Dropped: map-pack confusion and misrouted reviews from day one.</td></tr>
<tr><td>Anchor / Pelican / Seaside / Ancient City / First Coast</td><td>Ancient City and First Coast are used by competitors (ancientcitypawn.com registered; First Coast Pawn &amp; More, Callahan).</td><td>anchorpawn.com, pelicanpawn.com, seasidepawn.com taken.</td><td>Not searched.</td><td>Dropped.</td></tr>
<tr><td>Compass / Matanzas / Castillo / Harbor / North Star / Surf City / Tidal / Driftwood</td><td>Not checked for local use.</td><td>All .com open at $13.</td><td>Not searched.</td><td>Bench: usable if both finalists fall.</td></tr>
</table></div>

<div class="verdict"><strong>Recommendation:</strong> run Rocket through a one-hour trademark clearance. If counsel clears it, buy rocketpawn.com before the sale ends and go. If counsel says the Rocket Companies marks are a problem, Lighthouse is the pick and loses nothing on the local marketing side.</div>
</main>
'''

# ---------- SITE PAGES ----------
def site(brand, logo_svg, logo_small, tagline, palette, fonts_display, fonts_body, slug, hero_badge, intro, accent_word, palette_css='', switcher=''):
    bg, fg, navy, accent, gold, soft = palette
    return f'''<title>{brand}</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}
<style>
/* Layout mirrors thevalleypawn.com: sticky nav, hero with call/text CTAs, services cards, we-buy-gold band, family section, store card, hours, footer. */
:root{{--bg:{bg};--fg:{fg};--navy:{navy};--accent:{accent};--gold:{gold};--soft:{soft};--card:#FFFFFF;--line:#DCE3EA;--muted:#5B6B7C}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0D1520;--fg:#EEF2F6;--soft:#152033;--card:#18233A;--line:#2A3A52;--muted:#AAB7C6;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0D1520;--fg:#EEF2F6;--soft:#152033;--card:#18233A;--line:#2A3A52;--muted:#AAB7C6;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:{fonts_body};font-size:17px;line-height:1.55;margin:0}}
body::before{{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--navy)}}
.in{{max-width:1120px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
header{{position:sticky;top:env(safe-area-inset-top,0px);z-index:9;background:var(--navy);color:#fff}}
header .in{{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:10px;flex-wrap:wrap}}
nav{{display:flex;gap:18px;flex-wrap:wrap;font-weight:700;font-size:15px}}
nav a{{color:#fff;text-decoration:none;opacity:.9}} nav a:hover,nav a:focus-visible{{opacity:1;text-decoration:underline;outline:none}}
.hero{{background:var(--navy);color:#fff}}
.hero .in{{display:grid;grid-template-columns:1.2fr 1fr;gap:32px;padding-block:40px 48px;align-items:center}}
.hero h1{{font-family:{fonts_display};font-size:clamp(30px,4.6vw,52px);line-height:1.05;margin:0 0 14px;text-wrap:balance}}
.hero h1 em{{font-style:normal;color:var(--accent)}}
.badges{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 16px}}
.badge{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.3);border-radius:999px;padding:5px 12px;font-size:13px;font-weight:700;letter-spacing:.5px}}
.sub{{font-size:20px;margin:0 0 20px;opacity:.95}}
.cta{{display:flex;gap:12px;flex-wrap:wrap}}
.btn{{display:inline-block;padding:13px 20px;border-radius:8px;font-weight:800;text-decoration:none;font-size:16px;letter-spacing:.3px}}
.btn.p{{background:var(--accent);color:#fff}} .btn.s{{background:#fff;color:var(--navy)}} .btn.o{{border:2px solid #fff;color:#fff}}
.btn:focus-visible{{outline:3px solid var(--gold);outline-offset:2px}}
.hero .logo{{background:#fff;border-radius:12px;padding:22px;display:flex;align-items:center;justify-content:center}}
.app{{background:var(--gold);color:var(--navy);text-align:center;font-weight:800;padding-block:10px}}
.app .in{{padding-block:0}}
section{{padding-block:44px}}
section.soft{{background:var(--soft)}}
h2{{font-family:{fonts_display};font-size:clamp(24px,3.4vw,36px);margin:0 0 10px;text-wrap:balance}}
.tagline{{text-align:center;font-family:{fonts_display};font-size:clamp(22px,3.6vw,38px);color:var(--accent);margin:0}}
.grid3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:22px;min-width:0}}
.card h3{{margin:0 0 6px;font-size:20px;color:var(--accent)}}
.card p{{margin:0;color:var(--muted)}}
.gold{{background:var(--navy);color:#fff}}
.gold h2{{color:var(--gold)}}
.gold .in{{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:center}}
ul.items{{columns:2;gap:24px;margin:0;padding-left:18px}} ul.items li{{break-inside:avoid;margin-bottom:4px}}
.store{{display:grid;grid-template-columns:1.1fr 1fr;gap:28px;align-items:start}}
.hours{{display:grid;grid-template-columns:auto 1fr;gap:4px 18px;font-variant-numeric:tabular-nums}}
.hours b{{font-weight:800}}
.phone{{font-family:{fonts_display};font-size:30px;color:var(--accent);user-select:all}}
.social{{display:flex;gap:12px;flex-wrap:wrap}} .social a{{color:var(--accent);font-weight:700}}
footer{{background:var(--navy);color:#fff;font-size:14px}}
footer .in{{padding-block:26px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
footer a{{color:#fff}}
.note{{font-size:13px;color:var(--muted)}}
@media (max-width:760px){{.hero .in,.gold .in,.store{{grid-template-columns:1fr}} ul.items{{columns:1}}}}
{palette_css}
.switch{{position:sticky;top:calc(env(safe-area-inset-top,0px) + 58px);z-index:8;background:var(--card);border-bottom:1px solid var(--line)}}
.switch .in{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding-block:8px;font-size:14px}}
.switch button{{border:2px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:5px 12px;font-weight:700;cursor:pointer;display:inline-flex;gap:6px;align-items:center}}
.switch button i{{width:12px;height:12px;border-radius:50%;display:inline-block}}
.switch button[aria-pressed="true"]{{border-color:var(--accent);background:var(--soft)}}
.switch button:focus-visible{{outline:3px solid var(--gold)}}
@media (prefers-reduced-motion:no-preference){{.btn{{transition:transform .15s}} .btn:hover{{transform:translateY(-1px)}}}}
</style>
<header><div class="in">
 <div style="display:flex;align-items:center;gap:10px">{logo_small}</div>
 <nav><a href="#loans">Loans</a><a href="#shop">Shop</a><a href="#gold">Sell Gold</a><a href="#jewelry">Sell Jewelry</a><a href="#ffl">FFL Transfer</a><a href="#visit">Visit</a></nav>
</div></header>
{switcher}
<section class="hero"><div class="in">
 <div>
  <h1>Pawn Shop &amp; Gold Buyer in St. Augustine · <em>Pawn Loans up to $25K</em></h1>
  <div class="badges"><span class="badge">{hero_badge}</span><span class="badge">30-day warranty on everything we sell</span><span class="badge">Family owned</span></div>
  <p class="sub">Need money? We can help. Need cool stuff? We've got you.</p>
  <div class="cta"><a class="btn p" href="#visit">Call or text us</a><a class="btn s" href="#visit">Get directions</a><a class="btn o" href="#loans">How pawn loans work</a></div>
  <p class="note" style="color:rgba(255,255,255,.75);margin:14px 0 0">2493–2495 US Highway 1 South, St. Augustine, FL 32086 · Opening spring 2027</p>
 </div>
 <div class="logo">{logo_svg}</div>
</div></section>
<div class="app"><div class="in">GET THE FREE APP · Pay or extend your loan, make layaway payments and check due dates from your phone</div></div>

<section><div class="in"><p class="tagline">{tagline}</p></div></section>

<section class="soft" id="loans"><div class="in">
 <h2>{accent_word} loans, no credit check</h2>
 <p style="max-width:70ch">{intro}</p>
 <div class="grid3">
  <div class="card"><h3>Pawn Loans</h3><p>Bring in anything of value. We appraise it with real market data, make you a fair offer, and hold your item safely. Pay it back in 30 days or extend. No credit check, no effect on your credit.</p></div>
  <div class="card" id="shop"><h3>Shop</h3><p>Quality new and pre-owned tools, electronics, jewelry, instruments and more at up to 25% less than the big-box price, and every item carries our 30-day warranty.</p></div>
  <div class="card" id="jewelry"><h3>Sell Jewelry &amp; Gold</h3><p>Gold, silver, platinum, diamonds, coins and bullion. We weigh and test in front of you and pay on the spot. No appointment needed.</p></div>
 </div>
</div></section>

<section class="gold" id="gold"><div class="in">
 <div><h2>We buy gold, silver and bullion</h2><p>Broken chains, single earrings, class rings, dental gold, coins, bars. If it's precious metal, we'll make you an offer, and we'll show you the scale and the price we're working from.</p></div>
 <div><h3 style="margin:0 0 8px">What we loan on and buy</h3><ul class="items"><li>Gold &amp; silver jewelry</li><li>Diamonds &amp; watches</li><li>Coins &amp; bullion</li><li>Power tools</li><li>Phones, tablets, laptops</li><li>Game consoles</li><li>TVs &amp; audio</li><li>Guitars &amp; instruments</li><li>Firearms (FFL)</li><li>Outdoor &amp; sporting gear</li></ul></div>
</div></section>

<section id="ffl"><div class="in">
 <h2>Family-owned. NPA member. Your neighbor.</h2>
 <p style="max-width:70ch">We're the family behind Valley Pawn, five stores in Virginia with a 4.9-star average, and St. Augustine is home now. Same rules here: we do what's right, we stand behind what we sell, and we treat you like a neighbor, because you are one. Licensed Florida pawnbroker. Federal firearms licensee with FFL transfers available.</p>
</div></section>

<section class="soft" id="visit"><div class="in">
 <h2>Come see us</h2>
 <div class="store">
  <div class="card">
   <h3>{brand} · St. Augustine</h3>
   <p>2493–2495 US Highway 1 South<br>St. Augustine, FL 32086</p>
   <p class="phone">(904) 000-0000</p>
   <p class="note">Call or text the same number. Store line is being provisioned; this number is a placeholder.</p>
   <div class="cta" style="margin-top:12px"><a class="btn p" href="#visit">Call</a><a class="btn p" href="#visit">Text</a><a class="btn s" style="background:var(--navy);color:#fff" href="https://www.google.com/maps/search/?api=1&amp;query=2493+US+Highway+1+S+St+Augustine+FL+32086" target="_blank" rel="noopener">Directions</a></div>
  </div>
  <div>
   <h3 style="margin:0 0 8px">Store hours</h3>
   <div class="hours"><b>Mon–Fri</b><span>10:00 AM – 6:00 PM</span><b>Saturday</b><span>10:00 AM – 5:00 PM</span><b>Sunday</b><span>Closed</span></div>
   <h3 style="margin:22px 0 8px">Connect</h3>
   <div class="social"><a href="#visit">Facebook</a><a href="#visit">Instagram</a><a href="#visit">TikTok</a><a href="#visit">Google reviews</a></div>
   <p class="note" style="margin-top:18px">Walk in anytime during business hours. No appointment needed.</p>
  </div>
 </div>
</div></section>

<footer><div class="in">
 <div><strong>{brand}</strong> · 2493–2495 US Hwy 1 S, St. Augustine, FL 32086</div>
 <div><a href="#visit">FAQ</a> · <a href="#visit">Returns &amp; Refunds</a> · <a href="#visit">Careers</a> · <a href="#visit">Privacy</a></div>
 <div class="note" style="color:rgba(255,255,255,.7)">Mockup for review. Phone number, social links and photos to be added when the lease is executed.</div>
</div></footer>
'''

PALETTES = [
 ("A", "Launch", "Navy, rocket orange, gold. Classic and confident; closest to the Valley Pawn family look.", "#0B1E3A", "#F26B1D", "#D4A62A", "#EAF2FA", "#F7F8FA"),
 ("B", "Midnight Mint", "Charcoal, electric teal, warm gold. Modern and tech-forward; stands out against every other pawn sign on US-1.", "#15181D", "#19B5A3", "#E6B84A", "#E8F4F2", "#F6F8F8"),
 ("C", "Sunset Coast", "Deep plum, coral, sunset yellow. Warm Florida evening palette; friendliest of the four, strong for jewelry.", "#3B1F4D", "#FF6B5C", "#FFC857", "#FBEFEA", "#FBF8F5"),
 ("D", "Red Rocket", "Fire-engine red, navy, silver. Retro Americana; the loudest at highway speed.", "#0A2342", "#C8102E", "#9DA8B3", "#EEF2F6", "#F8F9FB"),
 ("E", "Lime & Black", "Black with electric lime. High-contrast and impossible to miss on US-1; reads young and tech-forward.", "#111111", "#C6FF00", "#8FBF00", "#F3F8E6", "#F8F9F6"),
 ("F", "Lime & Navy", "Navy with a softer lime and a pale lime accent. Keeps the lime energy but feels more established.", "#0B1E3A", "#B4E33D", "#7FA62A", "#EEF6DE", "#F7F9F4"),
 ("G", "Lime & Slate", "Charcoal slate with a deep lime and a yellow-green accent. The most 'premium' of the lime set; works for jewelry.", "#2B2F36", "#A4D400", "#D9E021", "#F0F5E4", "#F7F8F6"),
 ("H", "Valley Pawn family", "Deep purple, bright blue, coral: the existing Valley Pawn colors for comparison. Friendly and familiar; mid-value colors that lose contrast on a roadside sign.", "#2D1A5E", "#0099DD", "#F58C8A", "#EAF6FD", "#F7F9FB"),
]

def colorways_page():
    cards=[]
    for key,name,why,n,o,g,soft,bg in PALETTES:
        chips="".join(f'<span class="chip" style="background:{c}"><b>{c}</b></span>' for c in (n,o,g))
        cards.append(f'''<article class="cw"><header><span class="k">{key}</span><div><h2>{name}</h2><p>{why}</p></div></header>
<div class="chips">{chips}</div>
<div class="logos">
 <div class="art">{rocket1(360,n,o,g)}</div>
 <div class="row"><div class="art">{rocket2(200,n,o,g)}</div><div class="art">{rocket3(300,n,o,g)}</div></div>
 <div class="art dark" style="background:{n}">{rocket3(300,"#fff",o,g)}</div>
</div></article>''')
    return f'''<title>Rocket Pawn Colorways</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}
<style>
/* Layout: four colorway panels, each with its chips and the three logo concepts recolored, plus a reversed-on-dark test. */
:root{{--bg:#F7F8FA;--fg:#14202E;--muted:#5B6B7C;--card:#FFFFFF;--line:#D9E0E8}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:'Source Sans 3',system-ui,sans-serif;font-size:17px;line-height:1.5;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:1180px;margin:0 auto}}
h1{{font-family:Saira,sans-serif;font-weight:800;font-size:clamp(28px,4vw,40px);margin:0 0 6px}}
.lead{{color:var(--muted);max-width:72ch;margin:0 0 28px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:22px}}
@media (max-width:560px){{.grid{{grid-template-columns:1fr}}}}
.cw{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px;min-width:0;display:flex;flex-direction:column;gap:14px}}
.cw header{{display:flex;gap:14px;align-items:flex-start}}
.k{{font-family:Saira,sans-serif;font-weight:900;font-size:34px;line-height:1;color:var(--muted)}}
.cw h2{{margin:0;font-size:22px}} .cw header p{{margin:4px 0 0;color:var(--muted);font-size:15px}}
.chips{{display:flex;gap:8px;flex-wrap:wrap}}
.chip{{display:inline-flex;align-items:flex-end;width:92px;height:44px;border-radius:6px;padding:4px 6px;color:#fff;font-size:11px;font-weight:700;text-shadow:0 1px 2px rgba(0,0,0,.6)}}
.logos{{display:flex;flex-direction:column;gap:10px}}
.art{{background:#fff;border-radius:8px;padding:14px;display:flex;align-items:center;justify-content:center;min-width:0}}
.row{{display:grid;grid-template-columns:1fr 1.4fr;gap:10px}}
@media (max-width:560px){{.row{{grid-template-columns:1fr}}}}
.cta{{margin-top:26px;color:var(--muted);font-size:15px}}
</style>
<main>
<h1>Rocket Pawn &amp; Jewelry — eight colorways</h1>
<p class="lead">Same three logo concepts, eight palettes (E–G are the lime set; H is the Valley Pawn family palette for comparison). Each panel shows the primary mark, the seal, the wordmark, and the wordmark reversed on the brand's dark color (how it sits on a navy fascia sign or the website header). The website mockup has a switcher at the top so you can see each palette on the full page.</p>
<div class="grid">{"".join(cards)}</div>
<p class="cta">Domains secured 10/31: rocketpawnjewelry.com and rocketpawnandjewelry.com.</p>
</main>
'''

pal_css = "".join(f"body.pal-{k.lower()}{{--navy:{n};--accent:{o};--gold:{g};--soft:{soft}}} " for k,_,_,n,o,g,soft,_ in PALETTES)
pal_css += "@media (prefers-color-scheme: dark){" + "".join(f":root:not([data-theme='light']) body.pal-{k.lower()}{{--soft:#152033}} " for k,*_ in PALETTES) + "} " + "".join(f":root[data-theme='dark'] body.pal-{k.lower()}{{--soft:#152033}} " for k,*_ in PALETTES)
sw = '<div class="switch"><div class="in"><span>Colorway:</span>' + "".join(f'<button type="button" data-pal="{k.lower()}" aria-pressed="{"true" if k=="A" else "false"}"><i style="background:{o}"></i>{k} · {name}</button>' for k,name,_,n,o,g,_,_ in PALETTES) + '</div></div>'
sw += """<script>(function(){var b=document.body,bs=document.querySelectorAll('.switch button');function set(k){b.className=b.className.replace(/\\bpal-\\w+/g,'').trim();b.classList.add('pal-'+k);bs.forEach(function(x){x.setAttribute('aria-pressed',x.dataset.pal===k?'true':'false')});try{localStorage.setItem('rp-pal',k)}catch(e){}}
var k='a';try{k=localStorage.getItem('rp-pal')||'a'}catch(e){}set(k);bs.forEach(function(x){x.addEventListener('click',function(){set(x.dataset.pal)})});})();</script>"""
rocket_site = site(
    "Rocket Pawn & Jewelry", rocket1(380,"var(--navy)","var(--accent)","var(--gold)"), rocket3(230,"#fff","var(--accent)","var(--gold)"),
    "Fair deals, lightning fast.",
    ("#F7F8FA","#14202E",RN,RO,RG,"#EAF2FA"),
    "Saira,'Arial Narrow',sans-serif", "'Source Sans 3',system-ui,sans-serif", "rocket",
    "St. Augustine's newest pawn shop",
    "Hassle-free secured loans when you need cash fast, from a family that has been doing this since 2014. Bring it in, we loan on it.",
    "Fast, fair", pal_css, sw)
light_site = site(
    "Lighthouse Pawn & Jewelry", light1(400), light3(230).replace("viewBox","style=\"filter:brightness(0) invert(1)\" viewBox"),
    "Your guiding light on the First Coast.",
    ("#FBF9F4","#14202E",LN,LT,LA,LSAND),
    "'Alfa Slab One',Georgia,serif", "Mulish,system-ui,sans-serif", "lighthouse",
    "St. Augustine's newest pawn shop",
    "Hassle-free secured loans when you need cash, from a family that has been doing this since 2014. Bring it in, we loan on it.",
    "Steady, honest")

os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/brand_review.html","w").write(review)
open(f"{OUT}/rocket_colorways.html","w").write(colorways_page())

FONTS3=[("Russo One","'Russo One', 'Arial Black', sans-serif","Space-age and heavy. Reads like a launch badge; the widest of the three, so the wordmark needs a wide sign."),
        ("Bebas Neue","'Bebas Neue', 'Arial Narrow', sans-serif","Tall condensed signage type. The most legible from a distance and the easiest to fit on a pylon panel."),
        ("Chakra Petch","'Chakra Petch', 'Arial Narrow', sans-serif","Angular, technical, slightly retro-futurist. The most distinctive and the most 'modern pawn shop' of the set.")]
PAL2=[("Black & Red","#111111","#C8102E","#FFFFFF","#F4F4F4","#1A1A1A"),
      ("Teal & White","#19B5A3","#19B5A3","#111111","#FFFFFF","#E8F4F2")]
def type_page():
    panels=[]
    for fname,fstack,fnote in FONTS3:
        for pname,n,o,fg_on_dark,bg,soft in PAL2:
            dark = pname.startswith("Black")
            logo_light = rocket1(360,n,o,o if dark else "#111111",fstack) if dark else rocket1(360,"#111111",o,n,fstack)
            word_dark = rocket3(300,"#fff",o if dark else "#fff",o if dark else "#9BE3D8",fstack)
            panels.append(f'''<article class="tp" style="--pn:{n};--po:{o};--pbg:{bg};--psoft:{soft}">
<h3>{fname} <span>· {pname}</span></h3>
<div class="art" style="background:{bg}">{logo_light}</div>
<div class="art" style="background:{n}">{word_dark}</div>
<div class="sample" style="background:{bg};color:{'#fff' if False else '#111'}">
 <div class="h" style="font-family:{fstack};color:{n}">Pawn loans up to <b style="color:{o}">$25K</b></div>
 <div class="btns"><span class="b" style="background:{o};color:#fff">Call or text us</span><span class="b" style="background:{n};color:#fff">Get directions</span></div>
 <div class="nav" style="font-family:{fstack};color:{n}">LOANS · SHOP · SELL GOLD · SELL JEWELRY · FFL TRANSFER</div>
</div>
<p class="note">{fnote}</p>
</article>''')
    return f'''<title>Rocket Pawn Type Studies</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}
<style>
/* Layout: 3 typefaces x 2 palettes = 6 panels; each shows the mark, the reversed wordmark and a hero/nav/button sample set in that face. */
:root{{--bg:#F7F8FA;--fg:#14202E;--muted:#5B6B7C;--card:#FFFFFF;--line:#D9E0E8}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:'Source Sans 3',system-ui,sans-serif;font-size:17px;line-height:1.5;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:1180px;margin:0 auto}}
h1{{font-family:Saira,sans-serif;font-weight:800;font-size:clamp(28px,4vw,40px);margin:0 0 6px}}
.lead{{color:var(--muted);max-width:72ch;margin:0 0 28px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:22px}}
@media (max-width:540px){{.grid{{grid-template-columns:1fr}}}}
.tp{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;min-width:0;display:flex;flex-direction:column;gap:10px}}
.tp h3{{margin:0 0 4px;font-size:22px}} .tp h3 span{{color:var(--muted);font-weight:400;font-size:17px}}
.art{{border-radius:8px;padding:14px;display:flex;align-items:center;justify-content:center;min-width:0}}
.sample{{border-radius:8px;padding:16px;display:flex;flex-direction:column;gap:12px}}
.sample .h{{font-size:30px;line-height:1.05;font-weight:800}}
.btns{{display:flex;gap:8px;flex-wrap:wrap}} .b{{display:inline-block;padding:9px 14px;border-radius:7px;font-weight:800;font-size:14px}}
.nav{{font-size:13px;letter-spacing:2px;font-weight:700}}
.note{{color:var(--muted);font-size:14px;margin:0}}
</style>
<main>
<h1>Rocket Pawn &amp; Jewelry — three more typefaces</h1>
<p class="lead">The two palettes you picked, black &amp; red and teal &amp; white, set in three new typefaces (Saira, the face in the first round, is the reference). Each panel shows the primary mark, the wordmark reversed on the dark color, and a hero line, buttons and nav in that face.</p>
<div class="grid">{"".join(panels)}</div>
</main>
'''
open(f"{OUT}/rocket_type_studies.html","w").write(type_page())
open(f"{OUT}/rocket_pawn_site.html","w").write(rocket_site)
open(f"{OUT}/lighthouse_pawn_site.html","w").write(light_site)
print("built", [len(review), len(rocket_site), len(light_site)])

ROUND2=[("Shield Crest",rocket4,"Vertical rocket with a gem nose inside a crest. The most 'trusted institution' of the set; sits well on a receipt, a door decal and a polo."),
        ("R Monogram",rocket5,"A bold R with the rocket riding its leg, in a ring. Built for the app icon, social avatars and a small window cling where a full wordmark won't fit."),
        ("Trail Arc",rocket6,"Horizontal lockup: the rocket crosses above the name and its trail sweeps under the letters. Made for the fascia sign and the website header.")]
def round2_page():
    panels=[]
    for cname,fn,note in ROUND2:
        for pname,n,o,fg_on_dark,bg,soft in PAL2:
            dark = pname.startswith("Black")
            if dark:
                light = fn(None,n,o,o,fg="#111111"); on_dark = fn(None,"#1A1A1A",o,"#fff",fg="#fff")
            else:
                light = fn(None,"#111111",o,o,fg="#111111"); on_dark = fn(None,"#111111","#fff","#fff",fg="#fff")
            light = light.replace('width="None"','width="100%"'); on_dark = on_dark.replace('width="None"','width="100%"')
            panels.append(f'''<article class="tp"><h3>{cname} <span>· {pname}</span></h3>
<div class="pair"><div class="art" style="background:{bg}">{light}</div><div class="art" style="background:{n}">{on_dark}</div></div>
<p class="note">{note}</p></article>''')
    return f'''<title>Rocket Logos Round Two</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}
<style>
/* Layout: three new marks x two palettes; each panel shows the mark on light and on the brand dark. */
:root{{--bg:#F7F8FA;--fg:#14202E;--muted:#5B6B7C;--card:#FFFFFF;--line:#D9E0E8}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:'Source Sans 3',system-ui,sans-serif;font-size:17px;line-height:1.5;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:1180px;margin:0 auto}}
h1{{font-family:Saira,sans-serif;font-weight:800;font-size:clamp(28px,4vw,40px);margin:0 0 6px}}
.lead{{color:var(--muted);max-width:72ch;margin:0 0 28px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:22px}}
@media (max-width:540px){{.grid{{grid-template-columns:1fr}}}}
.tp{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;min-width:0;display:flex;flex-direction:column;gap:10px}}
.tp h3{{margin:0 0 4px;font-size:22px}} .tp h3 span{{color:var(--muted);font-weight:400;font-size:17px}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.art{{border-radius:8px;padding:14px;display:flex;align-items:center;justify-content:center;min-width:0}}
.art svg{{width:100%;max-width:260px;height:auto}}
.note{{color:var(--muted);font-size:14px;margin:0}}
</style>
<main>
<h1>Rocket Pawn &amp; Jewelry — three more logos</h1>
<p class="lead">Three new marks, different in construction from the first round (diamond badge, orbit seal, exhaust wordmark). Each is shown in black &amp; red and in teal &amp; white, on a light ground and on the brand dark. Set in Saira until you pick a typeface.</p>
<div class="grid">{"".join(panels)}</div>
</main>
'''
open(f"{OUT}/rocket_logos_round2.html","w").write(round2_page())
