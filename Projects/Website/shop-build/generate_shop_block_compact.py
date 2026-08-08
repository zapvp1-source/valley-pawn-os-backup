#!/usr/bin/env python3
"""Valley Pawn /shop/ COMPACT block generator.
Reads items.json ({colors:{}, items:[{t,p,u,img,s}]}) -> writes shop-block-compact.html.
Unlike generate_shop_block.py (static server-rendered cards, ~1KB/item), this version
embeds a compact JSON payload and renders cards client-side via JS -> ~115 bytes/item,
used when payload size must stay small (e.g. passing through a token-limited channel).
Weapons-adjacent items are excluded exactly as in the static generator."""
import json, re, html, sys

BLOCK = json.load(open("items.json"))
ITEMS = BLOCK["items"]
STORE_ORDER = ["Culpeper","Waynesboro","Harrisonburg","Lexington","Roanoke"]
COLORS = {"Culpeper":"#0099DD","Waynesboro":"#2D1A5E","Harrisonburg":"#E07A5F","Lexington":"#3DB8E8","Roanoke":"#2A9D8F"}

BAN = re.compile(r"\b(gun|guns|rifle|pistol|handgun|firearm|ammo|ammun|magazine|tactical|holster|silencer|suppressor|scope|red dot|optic|bayonet|knife|blade|dagger|machete)\b", re.I)
ITEMS = [i for i in ITEMS if not BAN.search(i["t"])]

counts = {s:0 for s in STORE_ORDER}
for i in ITEMS: counts[i["s"]] = counts.get(i["s"],0)+1
total = len(ITEMS)

compact = []
for i in ITEMS:
    iid = i["u"].rsplit("/",1)[-1]
    imgid = i["img"].split("/g/")[1].split("/")[0]
    compact.append([iid, imgid, i["t"], i["p"], STORE_ORDER.index(i["s"])])
DATA = "[\n" + ",\n".join(json.dumps(item, separators=(",",":")) for item in compact) + "\n]"
COLORS_JSON = json.dumps(COLORS, separators=(",",":"))
STORES_JSON = json.dumps(STORE_ORDER, separators=(",",":"))

STYLE = """<style>
.vp-shop-app{--vp-blue:#0099DD;--vp-purple:#2D1A5E;--ink:#1d2530;--muted:#6b7480;--line:#e7eaee;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);max-width:1180px;margin:0 auto}
.vp-shop-app *{box-sizing:border-box}
.vp-shop-app .vp-lead{text-align:center;padding:8px 16px 4px;color:var(--muted);font-size:15px;line-height:1.5}
.vp-shop-app .vp-lead b{color:var(--ink)}
.vp-srow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:14px 4px 4px}
.vp-shop-app #vpSearch{flex:1;min-width:220px;font-size:15px;padding:11px 15px;border:1.5px solid var(--line);border-radius:11px;outline:none}
.vp-shop-app #vpSearch:focus{border-color:var(--vp-blue)}
.vp-shop-app #vpSort{font-size:14px;padding:11px 12px;border:1.5px solid var(--line);border-radius:11px;background:#fff;cursor:pointer}
.vp-count{font-size:13px;color:var(--muted);font-weight:600;white-space:nowrap}
.vp-chips{display:flex;flex-wrap:wrap;gap:9px;padding:12px 4px}
.vp-chip{border:1.5px solid var(--line);background:#fff;color:var(--ink);font:inherit;font-size:13.5px;font-weight:600;padding:8px 14px;border-radius:22px;cursor:pointer;transition:all .13s}
.vp-chip b{color:var(--muted);margin-left:3px}
.vp-chip:hover{border-color:var(--c,var(--vp-blue))}
.vp-chip.is-active{background:var(--c,var(--vp-purple));border-color:var(--c,var(--vp-purple));color:#fff}
.vp-chip.is-active b{color:rgba(255,255,255,.8)}
.vp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:18px;padding:16px 0 8px}
.vp-card{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;display:flex;flex-direction:column;transition:transform .15s,box-shadow .15s}
.vp-card:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(45,26,94,.13)}
.vp-card__img{position:relative;display:block;aspect-ratio:1/1;background:#f1f3f5;overflow:hidden}
.vp-card__img img{width:100%;height:100%;object-fit:cover;display:block}
.vp-badge{position:absolute;top:10px;left:10px;color:#fff;font-size:11px;font-weight:700;padding:4px 9px;border-radius:20px}
.vp-card__b{padding:13px 14px 15px;display:flex;flex-direction:column;flex:1}
.vp-card__t{margin:0 0 12px;font-size:14px;line-height:1.35;font-weight:600;min-height:38px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.vp-card__t a{color:var(--ink);text-decoration:none}
.vp-card__r{margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:10px}
.vp-price{font-size:19px;font-weight:800;color:var(--vp-purple)}
.vp-buy{background:var(--vp-blue);color:#fff;text-decoration:none;font-weight:700;font-size:13.5px;padding:9px 14px;border-radius:9px;white-space:nowrap}
.vp-buy:hover{background:var(--vp-purple)}
.vp-empty{display:none;text-align:center;color:var(--muted);padding:44px 20px;font-size:15px}
.vp-foot{text-align:center;color:var(--muted);font-size:12.5px;line-height:1.6;padding:22px 16px 8px}
@media(max-width:560px){.vp-grid{grid-template-columns:repeat(auto-fill,minmax(158px,1fr));gap:12px}.vp-price{font-size:17px}}
</style>"""

SCRIPT = """<script id="vp-shop-data" type="application/json">""" + DATA + """</script>
<script>
(function(){
var app=document.currentScript.closest('.vp-shop-app')||document.querySelector('.vp-shop-app');if(!app)return;
var STORES=""" + STORES_JSON + """;
var COLORS=""" + COLORS_JSON + """;
var raw=JSON.parse(document.getElementById('vp-shop-data').textContent);
var ITEMS=raw.map(function(r){return {id:r[0],img:r[1],t:r[2],p:r[3],s:STORES[r[4]]};});
var grid=app.querySelector('.vp-grid'),empty=app.querySelector('.vp-empty'),countEl=app.querySelector('.vp-count'),chipsEl=app.querySelector('.vp-chips');
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function num(p){var m=String(p).replace(/[^0-9.]/g,'');return parseFloat(m)||0;}
var counts={};STORES.forEach(function(s){counts[s]=0;});
ITEMS.forEach(function(i){counts[i.s]=(counts[i.s]||0)+1;});
var chipsHtml='<button class="vp-chip is-active" data-store="all">All Stores <b>'+ITEMS.length+'</b></button>';
STORES.forEach(function(s){if(counts[s])chipsHtml+='<button class="vp-chip" data-store="'+s+'" style="--c:'+(COLORS[s]||'#2D1A5E')+'">'+s+' <b>'+counts[s]+'</b></button>';});
chipsEl.innerHTML=chipsHtml;
var frag=document.createDocumentFragment();
ITEMS.forEach(function(i){
 var url='https://www.ebay.com/itm/'+i.id;
 var imgUrl='https://i.ebayimg.com/images/g/'+i.img+'/s-l500.webp';
 var art=document.createElement('article');
 art.className='vp-card';art.dataset.store=i.s;art.dataset.title=(i.t+' '+i.s).toLowerCase();art.dataset.price=num(i.p);
 art.innerHTML='<a class="vp-card__img" href="'+url+'" target="_blank" rel="noopener nofollow"><img loading="lazy" src="'+imgUrl+'" alt="'+esc(i.t)+'"><span class="vp-badge" style="background:'+(COLORS[i.s]||'#2D1A5E')+'">'+i.s+'</span></a><div class="vp-card__b"><h3 class="vp-card__t"><a href="'+url+'" target="_blank" rel="noopener nofollow">'+esc(i.t)+'</a></h3><div class="vp-card__r"><span class="vp-price">'+esc(i.p)+'</span><a class="vp-buy" href="'+url+'" target="_blank" rel="noopener nofollow">Buy Now &rsaquo;</a></div></div>';
 frag.appendChild(art);
});
grid.appendChild(frag);
var cards=[].slice.call(grid.querySelectorAll('.vp-card'));
var s={store:'all',q:'',sort:'feat'};
function apply(){var q=s.q.toLowerCase().split(/\\s+/).filter(Boolean);var shown=0;
 cards.forEach(function(c){var ok=(s.store==='all'||c.dataset.store===s.store);
  if(ok&&q.length){var h=c.dataset.title;ok=q.every(function(w){return h.indexOf(w)>-1});}
  c.style.display=ok?'':'none';if(ok)shown++;});
 if(s.sort!=='feat'){var vis=cards.filter(function(c){return c.style.display!=='none'});
  vis.sort(function(a,b){var d=a.dataset.price-b.dataset.price;return s.sort==='lo'?d:-d;});
  vis.forEach(function(c){grid.appendChild(c);});}
 if(empty)empty.style.display=shown?'none':'block';
 if(countEl)countEl.textContent=shown+(shown===1?' item':' items');}
chipsEl.querySelectorAll('.vp-chip').forEach(function(ch){ch.addEventListener('click',function(){
 chipsEl.querySelectorAll('.vp-chip').forEach(function(c){c.classList.remove('is-active')});
 ch.classList.add('is-active');s.store=ch.dataset.store;apply();});});
var t;var si=app.querySelector('#vpSearch');if(si)si.addEventListener('input',function(e){clearTimeout(t);t=setTimeout(function(){s.q=e.target.value.trim();apply();},120);});
var so=app.querySelector('#vpSort');if(so)so.addEventListener('change',function(e){s.sort=e.target.value;apply();});
apply();
})();
</script>"""

block = f'''<!-- wp:html -->
<!-- VP-SHOP-START : auto-generated by vp-website-shop-nightly. Do not hand-edit between markers. -->
<div class="vp-shop-app">
{STYLE}
<p class="vp-lead">Real inventory from all five Valley Pawn stores — inspected, tested, and backed by our <b>30-day warranty</b>. Search it, then tap any item to check out securely.</p>
<div class="vp-srow">
  <input id="vpSearch" type="search" placeholder="Search all inventory — e.g. Snap-on, gold, Xbox, guitar…" autocomplete="off">
  <select id="vpSort"><option value="feat">Sort: Featured</option><option value="lo">Price: Low &rarr; High</option><option value="hi">Price: High &rarr; Low</option></select>
  <span id="vpCount" class="vp-count"></span>
</div>
<div class="vp-chips"></div>
<div class="vp-grid"></div>
<div class="vp-empty">No items match your search. Try another keyword or a different store.</div>
<div class="vp-foot">Checkout is handled securely through Valley Pawn's verified eBay stores (Top Rated Seller). Total items: {total}.</div>
{SCRIPT}
</div>
<!-- VP-SHOP-END -->
<!-- /wp:html -->'''

open("shop-block-compact.html","w").write(block)
print(f"OK total={total} counts={counts} bytes={len(block)}")
