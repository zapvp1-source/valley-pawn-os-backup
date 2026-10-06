import sys,json,re,html as H
sys.path.insert(0,'/tmp/geo'); sys.path.insert(0,'/sessions/focused-sharp-einstein/mnt/Projects/Website/analytics/bin')
from stores import *
from wp_client import WP
APPLY='--apply' in sys.argv
B="/sessions/focused-sharp-einstein/mnt/Projects/Valley Pawn OS/website_backups_geo_2026-10-05"
import os; os.makedirs(B,exist_ok=True)
wp=WP()
CSS="""<style>
.vp-loc{max-width:1000px;margin:0 auto;padding:10px 24px 50px;color:#333;font-size:17px;line-height:1.75}
.vp-loc h2{color:#2D1A5E;font-size:28px;font-weight:800;margin:42px 0 12px}
.vp-loc h3{color:#008ED1;font-size:20px;font-weight:700;margin:22px 0 6px}
.vp-loc .vp-qa{background:#F4F0FB;border-left:5px solid #2D1A5E;padding:18px 22px;border-radius:6px;margin:30px 0 10px}
.vp-loc .vp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:10px}
.vp-loc .vp-card{border:1px solid #e3def0;border-radius:8px;padding:16px 18px;background:#fff}
.vp-loc .vp-card h3{margin-top:0}
.vp-loc .vp-rating{font-size:22px;font-weight:800;color:#2D1A5E}
.vp-loc table{border-collapse:collapse;width:100%;max-width:520px}
.vp-loc td{padding:6px 10px;border-bottom:1px solid #eee}
.vp-loc .vp-cta a{display:inline-block;margin:6px 8px 6px 0;padding:12px 18px;border-radius:6px;background:#008ED1;color:#fff !important;font-weight:700;text-decoration:none}
.vp-loc .vp-cta a.alt{background:#2D1A5E}
.vp-loc ol li,.vp-loc ul li{margin-bottom:6px}
</style>"""
def day_rows(s):
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    out=[]
    for d in days:
        if d=="Sunday": v="Closed"
        elif d=="Wednesday" and not s["six"]: v="Closed"
        elif d=="Saturday" and s["six"]: v="10:00 AM – 5:00 PM"
        else: v="10:00 AM – 6:00 PM"
        out.append(f"<tr><td>{d}</td><td>{v}</td></tr>")
    return "".join(out)
def build(key):
    s=STORES[key]; n=s["name"]; full=f"{s['addr']}, {n}, VA {s['zip']}"
    others=[STORES[k] for k in STORES if k!=key]
    wed = (f"Yes. Valley Pawn {n} is open Wednesdays, 10 AM–6 PM. It is one of two Valley Pawn stores open on Wednesday (Culpeper and Roanoke)." if s["six"]
           else f"No. Valley Pawn {n} is closed on Wednesdays and Sundays. If you need a store on a Wednesday, our Culpeper and Roanoke locations are open 10 AM–6 PM.")
    faqs=[
     (f"Where is the pawn shop in {n}, VA?", f"Valley Pawn {n} is at {full}. Call or text {s['phone']}."),
     (f"What are Valley Pawn {n}'s hours?", f"{hours_text(s)}."),
     (f"Is Valley Pawn {n} open on Wednesday?", wed),
     (f"How much can I borrow on a pawn loan in {n}?", "Loan amounts are based on the value of the item you bring in, from a couple hundred dollars up to $25,000 on the right collateral. There is no credit check and nothing is reported to the credit bureaus."),
     (f"Can I sell gold in {n} without an appointment?", f"Yes. Walk in any time we are open. We test and weigh your gold, silver or coins in front of you and price them from the live market. Bring a government-issued photo ID, which Virginia law requires."),
     ("Does a pawn loan affect my credit?", "No. Pawn loans require no credit check and are not reported to credit bureaus. If you choose not to repay, the item covers the loan and nothing else is owed."),
     (f"Does Valley Pawn {n} accept firearm transfers?", "Yes. All five Valley Pawn stores accept incoming FFL transfers. The transfer fee is $25 per firearm, due at pickup. See our FFL transfer page for this store's license copy."),
    ]
    faq_html="".join(f"<h3>{H.escape(q)}</h3><p>{H.escape(a)}</p>" for q,a in faqs)
    other_html="".join(f'<li><a href="/locations/{o["name"].lower()}/">Valley Pawn {o["name"]}</a> — {o["addr"]}, {o["name"]}, VA {o["zip"]} · {o["phone"]}</li>' for o in others)
    k=key
    body=f"""<!-- wp:html -->
{CSS}
<div class="vp-loc">
<div class="vp-qa"><p><strong>Pawn shop in {n}, VA:</strong> Valley Pawn {n} is a family-owned pawn shop at {full}. We make no-credit-check pawn loans up to $25,000, buy gold, silver, coins and jewelry at live market prices, and sell quality pre-owned merchandise backed by a 30-day warranty. Open {hours_text(s)}. Call or text {s['phone']}.</p></div>
<p class="vp-cta"><a href="tel:{s['tel']}">📞 Call {s['phone']}</a><a href="sms:{s['tel']}">💬 Text {s['phone']}</a><a class="alt" href="{maps(s)}" target="_blank" rel="noopener">📍 Directions</a></p>

<h2>What you can do at Valley Pawn {n}</h2>
<div class="vp-grid">
<div class="vp-card"><h3>Pawn loans up to $25,000</h3><p>Bring in anything of value — jewelry, gold, electronics, tools, instruments and more. We appraise it with real market data and hand you cash the same visit. No credit check. <a href="/loans/">How pawn loans work →</a></p></div>
<div class="vp-card"><h3>Sell gold &amp; silver</h3><p>We test and weigh your gold and silver in front of you and price it from the live spot market. <a href="/sell-gold-{k}/">Sell gold in {n}</a> · <a href="/sell-silver-{k}/">Sell silver</a></p></div>
<div class="vp-card"><h3>Sell coins &amp; jewelry</h3><p>Bullion, coin collections, rings, chains and broken pieces — bring them as they are. <a href="/sell-coins-{k}/">Sell coins in {n}</a> · <a href="/sell-jewelry-{k}/">Sell jewelry</a></p></div>
<div class="vp-card"><h3>Shop pre-owned for less</h3><p>Electronics, tools, jewelry, musical instruments and more, usually well below retail. Everything we sell carries a 30-day warranty. <a href="/retail/">See what we carry →</a></p></div>
<div class="vp-card"><h3>Free layaway &amp; the MobilePawn app</h3><p>Put an item on free layaway, then pay or extend a loan and check due dates from your phone. <a href="/app/">Get the free app →</a></p></div>
<div class="vp-card"><h3>FFL transfers</h3><p>Buying a firearm online? Have it shipped to this store. $25 per transfer, due at pickup. <a href="/ffl-transfer/">Transfer details &amp; our license →</a></p></div>
</div>

<h2>How a pawn loan works in {n}</h2>
<ol>
<li><strong>Bring your item in.</strong> No appointment needed. Bring a government-issued photo ID, which Virginia law requires for every pawn and purchase.</li>
<li><strong>Get a fair offer.</strong> We look up what your item is worth using current market data, not guesswork, and show you how we got to the number.</li>
<li><strong>Walk out with cash.</strong> We hold your item safely while you have the loan. Loans run on a set term (typically 30 days) with extensions available.</li>
<li><strong>Pick it back up.</strong> Repay the loan plus fees and your item is yours again. If you decide not to, the item covers the loan — nothing is reported to your credit and nothing else is owed.</li>
</ol>

<h2>Hours</h2>
<table>{day_rows(s)}</table>
<p>Prices on gold and silver move every day, so we quote from the live market at the counter. Questions before you come in? Call or text <a href="tel:{s['tel']}">{s['phone']}</a> or email <a href="mailto:{s['email']}">{s['email']}</a>.</p>

<h2>What {n} customers say</h2>
<p><span class="vp-rating">★ {s['rating']} out of 5</span> from {s['count']} Google reviews (as of {ASOF}).</p>
<p><a href="{maps(s)}" target="_blank" rel="noopener">Read every Valley Pawn {n} review on Google →</a></p>

<h2>Who we serve</h2>
<p>Customers come to Valley Pawn {n} from across {s['areas']}. Valley Pawn locations have served Virginia communities since 1988, and the company is family-owned and run by people who live here. Our promise is simple: <strong>What's Right Is Right.</strong></p>

<h2>Common questions about Valley Pawn {n}</h2>
{faq_html}

<h2>Other Valley Pawn locations</h2>
<ul>{other_html}</ul>
<p><a href="/locations/">See all five Valley Pawn locations →</a></p>
</div>
<!-- /wp:html -->"""
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"PawnShop","@id":f"https://thevalleypawn.com/locations/{k}/#store","name":f"Valley Pawn {n}","url":f"https://thevalleypawn.com/locations/{k}/","telephone":s["phone"],"email":s["email"],
       "image":"https://i0.wp.com/thevalleypawn.com/wp-content/uploads/2026/03/vp_logo_name-no-tag.png","priceRange":"$",
       "address":{"@type":"PostalAddress","streetAddress":s["street"],"addressLocality":n,"addressRegion":"VA","postalCode":s["zip"],"addressCountry":"US"},
       "openingHoursSpecification":hours_spec(s),"hasMap":maps(s),
       "aggregateRating":{"@type":"AggregateRating","ratingValue":s["rating"],"reviewCount":s["count"],"bestRating":"5","worstRating":"1"},
       "areaServed":[x.strip().replace("the rest of ","") for x in re.split(r",| and ",s["areas"]) if x.strip()],
       "makesOffer":[{"@type":"Offer","itemOffered":{"@type":"Service","name":"Pawn loans up to $25,000, no credit check"}},{"@type":"Offer","itemOffered":{"@type":"Service","name":"Gold, silver, coin and jewelry buying"}},{"@type":"Offer","itemOffered":{"@type":"Service","name":"FFL firearm transfers"}}],
       "parentOrganization":{"@type":"Organization","name":"Valley Pawn","url":"https://thevalleypawn.com"}},
      {"@type":"FAQPage","@id":f"https://thevalleypawn.com/locations/{k}/#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}]}
    return body, ld, faqs
def words(t):
    t=re.sub(r'<(script|style)[^>]*>.*?</\1>','',t,flags=re.S); return len(re.findall(r"[A-Za-z']+",H.unescape(re.sub(r'<[^>]+>',' ',t))))
for key,s in STORES.items():
    st,p=wp.get_json(f"/wp/v2/pages/{s['pid']}?context=edit")
    raw=p['content']['raw']
    open(f"{B}/page_{s['pid']}_before.html","w").write(raw)
    # cut: keep hero + map/NAP group (everything before the gray group), drop gray group + old ld+json
    gi=raw.find('<!-- wp:group {"style":{"color":{"background":"#f5f5f5"}')
    assert gi>0, key
    head=raw[:gi]
    body,ld,faqs=build(key)
    new=head+body+'\n\n<!-- wp:html -->\n<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>\n<!-- /wp:html -->'
    # hours line in NAP: keep. fix missing tel + sms
    open(f"{B}/page_{s['pid']}_after.html","w").write(new)
    print(key, s['pid'], 'words', words(raw),'->',words(new))
    if APPLY:
        md=f"Valley Pawn {s['name']}, {s['addr']}: pawn loans up to $25K with no credit check, gold, silver & coin buying, 30-day warranty. Rated {s['rating']}★ on Google."
        st2,b=wp._req(f"/wp/v2/pages/{s['pid']}","POST",json.dumps({"content":new,"meta":{"_yoast_wpseo_metadesc":md[:160]}}).encode(),{"Content-Type":"application/json"})
        print('  POST',st2,len(md))
