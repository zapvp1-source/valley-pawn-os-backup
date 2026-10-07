import cairosvg, os
GOLD="#F2B33D"; MANE_D="#C47F1E"; FACE="#FCE3A8"; MUZ="#FFF6E4"; NAVY="#0F1A2E"; VEST="#2E6B4F"; VEST_D="#1F4D38"
SHIRT="#FFF3D6"; BRASS="#D9A441"; INK="#2A1A0E"; PINK="#F59B8B"
DEFS='''<defs>
 <radialGradient id="mane" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="#FFD66B"/><stop offset="0.7" stop-color="#EFA936"/><stop offset="1" stop-color="#C47F1E"/></radialGradient>
 <radialGradient id="face" cx="45%" cy="38%" r="65%"><stop offset="0" stop-color="#FFF1CF"/><stop offset="0.8" stop-color="#F9D58C"/><stop offset="1" stop-color="#EDB862"/></radialGradient>
 <linearGradient id="coin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF0A8"/><stop offset="0.5" stop-color="#F3C24A"/><stop offset="1" stop-color="#B9831F"/></linearGradient>
 <radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFE7A3" stop-opacity="0.7"/><stop offset="0.55" stop-color="#F2B84B" stop-opacity="0.22"/><stop offset="1" stop-color="#F2B84B" stop-opacity="0"/></radialGradient>
 <linearGradient id="txt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF6D2"/><stop offset="0.55" stop-color="#FFD15C"/><stop offset="1" stop-color="#E39B22"/></linearGradient>
 <radialGradient id="bg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#22345A"/><stop offset="0.6" stop-color="#132240"/><stop offset="1" stop-color="#0A1326"/></radialGradient>
</defs>'''

def paw(x, y, r=34, mono=False):
    f = NAVY if mono else "#F6CF7E"
    s = '<circle cx="%d" cy="%d" r="%d" fill="%s" stroke="%s" stroke-width="5"/>' % (x, y, r, f, "#B9741A" if not mono else NAVY)
    if not mono:
        for dx in (-14, 0, 14):
            s += '<path d="M%d %d v10" stroke="#B9741A" stroke-width="4" stroke-linecap="round"/>' % (x + dx, y - r + 4)
    return s

def coin(x, y, r=36, mono=False):
    if mono:
        return '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="8"/><text x="%d" y="%d" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="%d" fill="%s">$</text>' % (x, y, r, NAVY, x, y + r * 0.42, r * 1.15, NAVY)
    return '<circle cx="%d" cy="%d" r="%d" fill="url(#coin)" stroke="#8F6418" stroke-width="5"/><circle cx="%d" cy="%d" r="%d" fill="none" stroke="#FFF0A8" stroke-width="3" opacity="0.7"/><text x="%d" y="%d" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="%d" fill="#8F6418">$</text>' % (x, y, r, x, y, r - 9, x, y + r * 0.42, r * 1.15)

def arm(path_d, mono=False):
    c = NAVY if mono else "#F6CF7E"
    return '<path d="%s" fill="none" stroke="%s" stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>' % (path_d, "#B9741A" if not mono else NAVY) + \
           ('' if mono else '<path d="%s" fill="none" stroke="%s" stroke-width="48" stroke-linecap="round" stroke-linejoin="round"/>' % (path_d, c))

def lion(pose="coin", mono=False):
    m = mono
    fill = lambda col: NAVY if m else col
    o = []
    # tail
    o.append('<path d="M650 820 q120 10 120 -90" fill="none" stroke="%s" stroke-width="22" stroke-linecap="round"/>' % fill(MANE_D))
    o.append('<circle cx="770" cy="722" r="30" fill="%s"/>' % ("url(#mane)" if not m else NAVY))
    # body / vest
    o.append('<path d="M392 600 q-30 120 -10 250 h260 q20 -130 -10 -250 z" fill="%s"/>' % fill(SHIRT))
    o.append('<path d="M392 600 q-30 120 -10 250 h96 l34 -240 z" fill="%s"/>' % fill(VEST))
    o.append('<path d="M632 600 q30 120 10 250 h-96 l-34 -240 z" fill="%s"/>' % fill(VEST))
    if not m:
        o.append('<path d="M478 850 l34 -240 l34 240" fill="none" stroke="%s" stroke-width="5"/>' % VEST_D)
        for yy in (690, 750, 810):
            o.append('<circle cx="%d" cy="%d" r="9" fill="%s" stroke="#8F6418" stroke-width="2"/>' % (470 if yy else 0, yy, BRASS))
        o.append('<rect x="560" y="700" width="50" height="10" rx="4" fill="%s"/>' % VEST_D)
        # loupe on chain from pocket
        o.append('<path d="M585 705 q-10 60 30 80" stroke="%s" stroke-width="4" fill="none" stroke-dasharray="3 5"/>' % BRASS)
        o.append('<circle cx="622" cy="800" r="20" fill="#CFE8F5" stroke="%s" stroke-width="7"/><rect x="636" y="814" width="22" height="10" rx="4" transform="rotate(45 636 814)" fill="%s"/>' % (BRASS, INK))
        # feet
    for fx in (440, 584):
        o.append('<ellipse cx="%d" cy="858" rx="62" ry="28" fill="%s" stroke="%s" stroke-width="5"/>' % (fx, fill("#F6CF7E"), fill("#B9741A")))
    front = []
    # arms per pose (drawn in FRONT of the mane)
    if pose == "wave":
        front.append(arm("M410 640 q-80 40 -60 120", m)); front.append(paw(352, 765, mono=m))
        front.append(arm("M615 640 q90 -40 110 -170", m)); front.append(paw(726, 460, 40, m))
        if not m:
            front.append('<g stroke="%s" stroke-width="7" stroke-linecap="round" fill="none"><path d="M785 420 q20 30 0 60"/><path d="M810 400 q30 50 0 100"/></g>' % GOLD)
    elif pose == "point":
        front.append(arm("M410 640 q-80 40 -60 120", m)); front.append(paw(352, 765, mono=m))
        front.append(arm("M615 650 q100 -10 190 -30", m)); front.append(paw(812, 616, 36, m))
        front.append('<path d="M840 606 l50 -10" stroke="%s" stroke-width="22" stroke-linecap="round"/>' % fill("#F6CF7E"))
    elif pose == "sold":
        front.append(arm("M410 640 q-80 40 -60 120", m)); front.append(paw(352, 765, mono=m))
        front.append(arm("M615 650 q80 0 110 -60", m))
        # hanging price tag that says SOLD, held by the string
        front.append('<path d="M726 588 l40 40" stroke="%s" stroke-width="4"/>' % (NAVY if m else "#8F6418"))
        front.append('<g transform="rotate(12 800 680)"><path d="M748 628 h120 l26 52 -26 52 h-120 z" fill="%s" stroke="%s" stroke-width="6"/>' % ("#FFFFFF" if m else "#FFF3D6", NAVY if m else "#8F6418") +
                     '<circle cx="766" cy="680" r="9" fill="none" stroke="%s" stroke-width="4"/>' % (NAVY if m else "#8F6418") +
                     '<text x="826" y="696" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="44" fill="%s">SOLD</text></g>' % (NAVY if m else "#B23A48"))
        front.append(paw(726, 588, 36, m))
    elif pose == "none":
        pass
    else:  # coin
        front.append(arm("M410 640 q-80 40 -60 120", m)); front.append(paw(352, 765, mono=m))
        front.append(arm("M615 650 q90 10 80 -80", m)); front.append(coin(700, 520, 46, m)); front.append(paw(700, 585, 34, m))
    # mane
    mane = [(512,330,205),(345,250,80),(679,250,80),(305,360,86),(719,360,86),(340,470,82),(684,470,82),(415,170,78),(609,170,78),(512,148,74),(432,515,62),(592,515,62)]
    for x, y, r in mane:
        o.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (x, y, r, "url(#mane)" if not m else NAVY))
    if not m:
        o.append('<g fill="none" stroke="%s" stroke-width="6" stroke-linecap="round" opacity="0.55"><path d="M318 260 q-18 34 8 68"/><path d="M706 260 q18 34 -8 68"/><path d="M318 405 q-14 38 18 68"/><path d="M706 405 q14 38 -18 68"/></g>' % MANE_D)
    # ears
    for ex in (402, 622):
        o.append('<circle cx="%d" cy="215" r="40" fill="%s"/>' % (ex, "#F6CF7E" if not m else "#FFFFFF"))
        o.append('<circle cx="%d" cy="215" r="22" fill="%s"/>' % (ex, "#F2A98A" if not m else NAVY))
    # face
    o.append('<ellipse cx="512" cy="355" rx="150" ry="142" fill="%s"/>' % ("url(#face)" if not m else "#FFFFFF"))
    eye = INK if not m else NAVY
    o.append('<ellipse cx="456" cy="335" rx="25" ry="30" fill="%s"/><ellipse cx="568" cy="335" rx="25" ry="30" fill="%s"/>' % (eye, eye))
    o.append('<circle cx="465" cy="323" r="9" fill="#fff"/><circle cx="577" cy="323" r="9" fill="#fff"/>')
    o.append('<path d="M430 292 q27 -17 52 -2" stroke="%s" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M542 290 q25 -15 52 2" stroke="%s" stroke-width="8" fill="none" stroke-linecap="round"/>' % (fill("#B9741A"), fill("#B9741A")))
    if not m:
        o.append('<ellipse cx="420" cy="398" rx="28" ry="16" fill="%s" opacity="0.55"/><ellipse cx="604" cy="398" rx="28" ry="16" fill="%s" opacity="0.55"/>' % (PINK, PINK))
        o.append('<ellipse cx="512" cy="408" rx="70" ry="52" fill="%s"/>' % MUZ)
    else:
        o.append('<ellipse cx="512" cy="408" rx="70" ry="52" fill="none" stroke="%s" stroke-width="6"/>' % NAVY)
    o.append('<path d="M492 383 q20 -12 40 0 q-5 22 -20 25 q-15 -3 -20 -25z" fill="%s"/>' % fill("#6B3A1E"))
    o.append('<path d="M512 408 v14" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % fill("#6B3A1E"))
    o.append('<path d="M476 424 q36 32 72 0" stroke="%s" stroke-width="6" fill="none" stroke-linecap="round"/>' % fill("#6B3A1E"))
    if not m:
        o.append('<path d="M500 436 q12 18 24 0" fill="#F27D7D"/>')
    return "".join(o + front)

def name_block(y=965, mono=False, size=118):
    if mono:
        return '<text x="512" y="%d" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="%d" fill="%s">Goldilocks</text>' % (y, size, NAVY)
    return ('<ellipse cx="512" cy="%d" rx="400" ry="100" fill="url(#halo)"/><ellipse cx="512" cy="%d" rx="290" ry="66" fill="url(#halo)"/>' % (y - 40, y - 40) +
            ''.join('<text x="512" y="%d" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="%d" fill="none" stroke="#FFC93D" stroke-width="%d" opacity="%.2f" stroke-linejoin="round">Goldilocks</text>' % (y, size, w, o) for w, o in ((34, 0.08), (22, 0.14), (12, 0.25))) +
            '<text x="512" y="%d" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="%d" fill="url(#txt)" stroke="#8F5A10" stroke-width="2">Goldilocks</text>' % (y, size))

def svg(body, w=1024, h=1100, bg="url(#bg)", vb=None):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%s">%s%s%s</svg>' % (
        w, h, vb or "0 0 %d %d" % (w, h), DEFS, ('<rect x="-500" y="-500" width="3000" height="3000" fill="%s"/>' % bg) if bg else "", body)

out = "/tmp/kit/out"; os.makedirs(out, exist_ok=True)
def save(name, s, w, h):
    open(os.path.join(out, name + ".svg"), "w").write(s)
    cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(out, name + ".png"), output_width=w, output_height=h)

# 1 main mascot with name (navy bg) + transparent versions
save("01_Goldilocks_main_with_name", svg('<g transform="translate(0,-40)">' + lion("coin") + '</g>' + name_block(1030), 1024, 1100), 2048, 2200)
save("02_Goldilocks_main_no_name_transparent", svg(lion("coin"), 1024, 900, bg=None), 2048, 1800)
# 2 poses (transparent)
for p, label in (("wave", "03_pose_waving"), ("coin", "04_pose_holding_coin"), ("point", "05_pose_pointing"), ("sold", "06_pose_sold_tag")):
    save("Goldilocks_" + label, svg(lion(p), 1024, 900, bg=None, vb="120 60 860 840"), 1720, 1680)
# 3 one-color
save("07_Goldilocks_one_color_navy", svg('<g transform="translate(0,-40)">' + lion("coin", mono=True) + '</g>' + name_block(1030, mono=True), 1024, 1100, bg=None), 2048, 2200)
# 4 slack icon (head + coin, square, navy)
save("08_Goldilocks_slack_icon", svg(lion("none"), 1024, 1024, vb="212 0 600 600"), 1024, 1024)
# contact sheet
