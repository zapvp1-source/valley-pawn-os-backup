import sys,json,re,html as H
sys.path.insert(0,'/tmp/geo'); sys.path.insert(0,'/sessions/focused-sharp-einstein/mnt/Projects/Website/analytics/bin')
from stores import *
from wp_client import WP
APPLY='--apply' in sys.argv
B="/sessions/focused-sharp-einstein/mnt/Projects/Valley Pawn OS/website_backups_geo_2026-10-05"
wp=WP()
IDS={"gold":{"culpeper":509,"waynesboro":510,"harrisonburg":511,"lexington":512,"roanoke":513},
     "jewelry":{"culpeper":594,"waynesboro":595,"harrisonburg":596,"lexington":597,"roanoke":598},
     "silver":{"culpeper":599,"waynesboro":600,"harrisonburg":601,"lexington":602,"roanoke":603},
     "coins":{"culpeper":604,"waynesboro":605,"harrisonburg":606,"lexington":607,"roanoke":608}}
WHAT={"gold":"gold jewelry, gold coins, bars, dental gold and broken or scrap gold",
      "silver":"sterling silver, silver coins, bars, rounds and flatware",
      "coins":"gold and silver coins, bullion and whole coin collections",
      "jewelry":"gold and silver jewelry, including rings, chains, bracelets and broken pieces"}
Q={"gold":"sell gold","silver":"sell silver","coins":"sell coins","jewelry":"sell jewelry"}
JONAS=('The coin shop up the street from here offered me 24% spot value for my precious metals… valley pawn met me at a much closer spot price that was genuinely FAIR even for a pawn shop. The workers and owner are very friendly and helpful as well as flexible with your needs. A+ guys! this is the only place I’ll take my metals from now on.','Jonas K.','Google review · Harrisonburg · 2026')
GOLD_GUIDE="""
  <!-- SELLING GOLD GUIDE -->
  <section class="vp-section">
    <div class="vp-container">
      <h2 class="vp-section__title">Selling Gold in {n}: What to Know Before You Go</h2>
      <p><strong>Know your karat.</strong> Look for a stamp inside a ring band or near a clasp. 10K is 41.7% pure gold, 14K is 58.3%, 18K is 75%, 22K is 91.7% and 24K is 99.9%. The higher the karat, the more each gram is worth. No stamp? We acid-test it at the counter for free.</p>
      <p><strong>Weight is everything.</strong> Gold is priced by weight times purity times the day's spot price. We weigh on a certified scale in front of you, in grams or pennyweight, and show you the math.</p>
      <p><strong>Compare offers the right way.</strong> Ask any buyer what percentage of melt value they are paying. A real number lets you compare shops, coin dealers and mail-in buyers fairly. We will tell you ours.</p>
      <p><strong>Coins and bullion are welcome too.</strong> Eagles, Maple Leafs, Krugerrands, bars and rounds — we buy bullion and coins as well as jewelry. See <a href="/sell-coins-{k}/">selling coins in {n}</a>.</p>
      <p><strong>Bring a photo ID.</strong> Virginia law requires a government-issued photo ID for every purchase. {hours_note}</p>
    </div>
  </section>
"""
def quick(cat,key):
    s=STORES[key]; n=s["name"]
    return f"""
  <!-- QUICK ANSWER -->
  <section class="vp-section">
    <div class="vp-container">
      <p style="background:#F4F0FB;border-left:5px solid #2D1A5E;padding:18px 22px;border-radius:6px;font-size:17px;line-height:1.7;margin:0;"><strong>Where can I {Q[cat]} in {n}, VA?</strong> Valley Pawn {n}, {s['addr']}, {n}, VA {s['zip']}, buys {WHAT[cat]} for cash. We test and weigh in front of you and price from the live market — no appointment needed. Open {hours_text(s)}. Call or text {s['phone']}. Rated {s['rating']} out of 5 from {s['count']} Google reviews.</p>
    </div>
  </section>
"""
def reviews_inner(cat,key):
    s=STORES[key]; n=s["name"]
    cards=f"""<div class="vp-review">
          <div class="vp-review__stars">★★★★★</div>
          <p class="vp-review__quote" style="font-size:22px;font-weight:800;">{s['rating']} out of 5</p>
          <div class="vp-review__author">{s['count']} Google reviews</div>
          <div class="vp-review__meta">Valley Pawn {n} · as of {ASOF}</div>
        </div>"""
    if key=="harrisonburg" and cat in ("gold","silver","coins"):
        q,a,m=JONAS
        cards+=f"""
        <div class="vp-review">
          <div class="vp-review__stars">★★★★★</div>
          <p class="vp-review__quote">"{q}"</p>
          <div class="vp-review__author">{a}</div>
          <div class="vp-review__meta">{m}</div>
        </div>"""
    return '<div class="vp-reviews">\n        '+cards+'\n      </div>'
for cat,m in IDS.items():
    for key,pid in m.items():
        s=STORES[key]; n=s["name"]
        st,p=wp.get_json(f"/wp/v2/pages/{pid}?context=edit"); raw=p['content']['raw']
        open(f"{B}/page_{pid}_before.html","w").write(raw)
        new=raw
        # 1 reviews block
        c1=0
        i=new.find('<div class="vp-reviews">')
        if i>0:
            depth=0; pos=i
            for mm in re.finditer(r'<div\b|</div>',new[i:]):
                depth += 1 if mm.group(0)=='<div' else -1
                if depth==0: end=i+mm.end(); break
            link='' if 'Read all our' in new[end:end+600] else f'\n      <p style="text-align:center;margin-top:24px;"><a href="{maps(s)}" target="_blank" rel="noopener" style="font-weight:700;">Read all our {n} reviews on Google →</a></p>'
            new=new[:i]+reviews_inner(cat,key)+link+new[end:]; c1=1
        new=re.sub(r'(<p class="vp-section__sub">)Real reviews from real [^<]*(</p>)', lambda mm: mm.group(1)+f"What customers say about Valley Pawn {n} on Google."+mm.group(2), new, count=1)
        # 2 quick answer before HOW IT WORKS section
        hi=new.find('How It Works</h2>'); si=new.rfind('<section',0,hi)
        # include preceding comment if present
        ci=new.rfind('<!--',0,si); 
        ins = ci if ci>0 and new[ci:si].strip().startswith('<!--') and len(new[ci:si])<60 else si
        c2=0
        if 'QUICK ANSWER' not in new and hi>0:
            new=new[:ins]+quick(cat,key)+"\n  "+new[ins:]; c2=1
        # 3 gold guide HAR + ROA
        c3=0
        if cat=="gold" and key in("harrisonburg","roanoke") and 'SELLING GOLD GUIDE' not in new:
            ri=new.find('<!-- REVIEWS -->')
            hn = "We are closed Wednesday and Sunday, so plan around those days." if not s["six"] else "We are open Monday through Saturday (Saturday until 5 PM)."
            new=new[:ri]+GOLD_GUIDE.format(n=n,k=key,hours_note=hn).strip("\n")+"\n\n  "+new[ri:]; c3=1
        # 4 aggregateRating in LocalBusiness node
        c4=0
        if '"aggregateRating"' not in new:
            new,c4=re.subn(r'("@type": "LocalBusiness",\s*"@id": "[^"]+",)', lambda mm: mm.group(1)+f'\n      "aggregateRating": {{"@type": "AggregateRating", "ratingValue": "{s["rating"]}", "reviewCount": "{s["count"]}", "bestRating": "5", "worstRating": "1"}},', new, count=1)
        fake=len(re.findall(r'Google Review · ',new))
        print(cat,key,pid,'reviews',c1,'quick',c2,'guide',c3,'agg',c4,'fake_left',fake, 'jsonok', end=' ')
        mj=re.search(r'<script type="application/ld\+json">(.*?)</script>',new,re.S)
        try: json.loads(mj.group(1)); print('Y')
        except Exception as e: print('N',e)
        open(f"{B}/page_{pid}_after.html","w").write(new)
        if APPLY and new!=raw:
            st2,b=wp._req(f"/wp/v2/pages/{pid}","POST",json.dumps({"content":new}).encode(),{"Content-Type":"application/json"}); print('  POST',st2)
