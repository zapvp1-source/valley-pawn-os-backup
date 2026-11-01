import json,base64,os
os.chdir("/home/claude/staug/brand")
man=[]
for b in range(1,7):
    p=f"ai/batch{b}.json"
    if os.path.exists(p): man+=json.load(open(p))
def img(f): return "data:image/png;base64,"+base64.b64encode(open("ai/"+f,"rb").read()).decode()
def tile(e,big=False): return f'<figure class="t{" big" if big else ""}"><img src="{img(e["file"])}" alt="#{e["n"]}"><figcaption><b>#{e["n"]}</b> {e["icon"][:70]}…</figcaption></figure>'
red=[e for e in man if 51<=e["n"]<=100]; teal=[e for e in man if 101<=e["n"]<=124]; early=[e for e in man if e["n"]<=50]
byn={e["n"]:e for e in man}
short_red=[58,55,68,51,63,70,82,74,81,88,98,93]; short_teal=[101,106,104,107,121,116,124,109]
r0=[("01_three_spheres_black_red.png","Three spheres + diamond"),("02_diamond_teal.png","Diamond wordmark"),("03_ring_wordmark_black_red.png","Ring-O wordmark"),("04_pawn_ticket_teal.png","Pawn ticket"),("05_circle_black-red.png","Circle emblem"),("06_stacked_black-red.png","Stacked wordmark, gem in A"),("06b_ring_black-red.png","Ring icon lockup"),("06c_shield_lime.png","Shield, lime"),("06d_spheres_lime.png","Three spheres, lime"),("06e_hex_lime.png","Hexagon, lime")]
r0tiles="".join(f'<figure class="t"><img src="{img(f)}" alt="{c}"><figcaption>{c}</figcaption></figure>' for f,c in r0)
html=f'''<title>Rocket Pawn Logo Field</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira:wght@800&family=Source+Sans+3:wght@400;700&display=swap">
<style>
/* Layout: shortlist first (large tiles), then the full black & red field, the teal field, and the earlier pawn-first round; contact-sheet grids. */
:root{{--bg:#F7F8FA;--fg:#14202E;--muted:#5B6B7C;--card:#FFFFFF;--line:#D9E0E8;--red:#C8102E;--teal:#19B5A3}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0F1620;--fg:#EEF2F6;--muted:#A9B6C4;--card:#1A2330;--line:#2C3947;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:'Source Sans 3',system-ui,sans-serif;font-size:16px;line-height:1.5;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:1240px;margin:0 auto}}
h1{{font-family:Saira,sans-serif;font-weight:800;font-size:clamp(28px,4vw,40px);margin:0 0 6px}}
.lead{{color:var(--muted);max-width:76ch;margin:0 0 24px}}
h2{{font-size:24px;margin:40px 0 4px}} h2 small{{display:block;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:4px}}
.sub{{color:var(--muted);margin:0 0 14px;max-width:76ch}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}}
.grid.short{{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}}
.t{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px;min-width:0}}
.t img{{width:100%;height:auto;background:#fff;border-radius:4px;display:block}}
.t figcaption{{font-size:12px;color:var(--muted);margin-top:6px;line-height:1.3}} .t figcaption b{{color:var(--fg)}}
.vp{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 22px;margin-top:16px;max-width:80ch}}
.vp h3{{margin:0 0 8px}} .vp p{{margin:0 0 8px}}
.note{{font-size:13px;color:var(--muted)}}
</style>
<main>
<h1>Rocket Pawn &amp; Jewelry — the logo field</h1>
<p class="lead">124 generated concepts so far. The brief for this round: pawn shop and jewelry first, but fast, direct and explosive — every angle of "rocket" (launch trails, ignition bursts, trajectories, afterburners, countdown rings, speed vectors) without drawing a rocket ship. Numbers are stable; call them out by number. Previews are 200px; any finalist exports at full resolution from Canva.</p>

<h2><small>Shortlist</small>Black &amp; red — 12 strongest</h2>
<p class="sub">Picked for sign-readability, how fast they say "pawn + jewelry," and whether the icon can stand alone at app-icon size.</p>
<div class="grid short">{"".join(tile(byn[n],True) for n in short_red if n in byn)}</div>

<h2><small>Shortlist</small>Teal &amp; white — 8 strongest</h2>
<div class="grid short">{"".join(tile(byn[n],True) for n in short_teal if n in byn)}</div>

<h2><small>Full field</small>Black &amp; red — 50 concepts (#51–#100)</h2>
<p class="sub">25 icon ideas, each in a horizontal and a stacked lockup. The generator mostly ignored typeface instructions, so type variety is lower than icon variety; the designer round fixes that.</p>
<div class="grid">{"".join(tile(e) for e in red)}</div>

<h2><small>Full field</small>Teal &amp; white — 24 concepts (#101–#124)</h2>
<div class="grid">{"".join(tile(e) for e in teal)}</div>

<h2><small>Earlier round</small>Pawn-first, mixed palettes (#1–#50)</h2>
<p class="sub">Generated before the "use every angle of rocket" direction; kept for reference. Includes lime and red-and-white variants.</p>
<div class="grid">{r0tiles}{"".join(tile(e) for e in early)}</div>

<h2><small>Question</small>How do the Valley Pawn colors stack up?</h2>
<div class="vp">
<h3>Valley Pawn palette: bright blue, deep purple, coral, sky blue</h3>
<p>It is a friendly, modern palette and it has five stores of equity behind it, which matters if you ever want customers to connect the Florida store to the Virginia family. Two things work against it for this store. First, visibility: blue and purple are mid-value colors, so on a fascia sign they lose edge contrast at distance the same way teal does, and coral is too light to carry a sign at all; black and red beats it clearly for the roadside. Second, the whole point of a separate DBA is a separate identity, and borrowing the Valley Pawn colors gives you the cost of a new name without the benefit of a new look.</p>
<p>Where the Valley Pawn colors still earn a place: the inside story. "From the family behind Valley Pawn" on the website, the press release and the grand-opening materials can carry the Valley Pawn logo in its own colors as an endorsement mark, the way a parent brand sits in a footer. That gives you the trust transfer without diluting the new sign.</p>
<p class="note">Ranking for an exterior sign, best to worst: black &amp; red, lime &amp; black, red &amp; white, lime &amp; navy, teal &amp; white, Valley Pawn blue/purple. Ranking for "feels like jewelry and trust" up close: black &amp; red, teal &amp; white, Valley Pawn palette, lime &amp; navy, red &amp; white, lime &amp; black.</p>
</div>
</main>
'''
open("rocket_logo_field.html","w").write(html); print(len(html)//1024,"KB", len(red), len(teal), len(early))
