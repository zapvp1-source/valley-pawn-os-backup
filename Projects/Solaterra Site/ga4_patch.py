import re,sys
p='/tmp/sol/site/index.html'; s=open(p).read()
def dec(h):
    k=int(h[:2],16); return ''.join(chr(int(h[i:i+2],16)^k) for i in range(2,len(h),2))
# restore plain emails
s=re.sub(r'href="/cdn-cgi/l/email-protection#([0-9a-f]+)"',lambda m:'href="mailto:'+dec(m.group(1))+'"',s)
s=re.sub(r'<span class="__cf_email__" data-cfemail="([0-9a-f]+)">\[email&#160;protected\]</span>',lambda m:dec(m.group(1)),s)
s=s.replace('<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script>','')
assert 'cdn-cgi' not in s and 'cfemail' not in s
GA=sys.argv[1]
head=f'''<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());gtag('config','{GA}',{{send_page_view:false}});
</script>
'''
i=s.index('<link rel="icon"'); s=s[:i]+head+s[i:]
track='''<script>
// ---- analytics: virtual page views + lead events ----
(function(){
  function ev(n,p){ try{ if(window.gtag) gtag('event',n,p||{}); }catch(e){} }
  window.solTrack=ev;
  var last=null;
  function pv(){ var n=(location.hash||'#home').replace('#','')||'home'; if(n===last) return; last=n;
    ev('page_view',{page_title:document.title+' | '+n,page_location:location.origin+'/'+(n==='home'?'':'#'+n),page_path:'/'+(n==='home'?'':n)}); }
  window.addEventListener('hashchange',pv); document.addEventListener('DOMContentLoaded',pv);
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a'); if(!a) return;
    var h=a.getAttribute('href')||''; var where=(a.closest('footer')?'footer':a.closest('header')?'header':'body');
    if(h.indexOf('tel:')===0) ev('phone_click',{link_location:where});
    else if(h.indexOf('mailto:')===0) ev('email_click',{link_location:where});
    else if(h.indexOf('google.com/maps')>-1) ev('review_link_click',{link_location:where});
    else if(h.indexOf('facebook.com')>-1) ev('facebook_click',{link_location:where});
    else if(h==='#about' && /estimate|quote|property|ask|check/i.test(a.textContent)) ev('estimate_cta_click',{cta_text:a.textContent.trim().slice(0,60)});
  },true);
})();
</script>
'''
s=s.replace('<script>\nfunction showPage(name)',track+'<script>\nfunction showPage(name)',1)
assert 'solTrack' in s
# lead events on form result
s=s.replace("""        if (result.ok) {
          msg.className = 'form-msg ok';""","""        if (result.ok) {
          if(window.solTrack) solTrack('generate_lead',{form:'free_estimate',service:(document.getElementById('f-service')||{}).value||''});
          msg.className = 'form-msg ok';""",1)
s=s.replace("""        } else {
          msg.className = 'form-msg err';""","""        } else {
          if(window.solTrack) solTrack('form_error',{form:'free_estimate',detail:String((result.data&&result.data.message)||'').slice(0,90)});
          msg.className = 'form-msg err';""",1)
s=s.replace("""      .catch(function(){
        btn.disabled = false;""","""      .catch(function(){
        if(window.solTrack) solTrack('form_error',{form:'free_estimate',detail:'network'});
        btn.disabled = false;""",1)
assert s.count('generate_lead')==1 and s.count("form_error")==2
open(p,'w').write(s); print('ok')
