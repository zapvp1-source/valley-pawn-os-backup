import json, threading, http.server, functools, socketserver
from playwright.sync_api import sync_playwright
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(('127.0.0.1',8765),functools.partial(Q,directory='/tmp/sol/site')); threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE='http://127.0.0.1:8765/'
results=[]
def ok(name,cond,detail=''): results.append((('PASS' if cond else 'FAIL'),name,detail))
form_mode={'m':'ok'}; form_posts=[]; gtm_loaded=[]
def route(r):
    u=r.request.url
    if u.startswith(BASE): return r.continue_()
    if 'googletagmanager.com/gtag/js' in u:
        gtm_loaded.append(u); return r.fulfill(status=200,content_type='application/javascript',body='/*stub*/')
    if 'formsubmit.co' in u:
        form_posts.append((u, r.request.post_data or ''))
        if form_mode['m']=='ok': return r.fulfill(status=200,content_type='application/json',body='{"success":"true","message":"The form was submitted successfully."}')
        if form_mode['m']=='bad': return r.fulfill(status=400,content_type='application/json',body='{"success":"false","message":"This form needs Activation."}')
        return r.abort()
    return r.abort()   # block everything else external
def events(p):
    return p.evaluate("""()=>dataLayer.filter(a=>a[0]==='event').map(a=>({n:a[1],p:a[2]}))""")
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for vp,label in [({'width':1366,'height':800},'desktop'),({'width':390,'height':844},'mobile')]:
        ctx=b.new_context(viewport=vp); p=ctx.new_page(); errs=[]
        p.on('pageerror',lambda e: errs.append(str(e)))
        p.on('dialog',lambda d: d.dismiss())
        ctx.route('**/*',route)
        p.goto(BASE); p.wait_for_timeout(600)
        cfg=p.evaluate("()=>dataLayer.filter(a=>a[0]==='config').map(a=>[a[1],a[2]])")
        ok(f'[{label}] GA4 config fires (page views handled manually)', cfg and cfg[0][1].get('send_page_view')==False, str(cfg))
        ev=events(p); pv=[e for e in ev if e['n']=='page_view']
        ok(f'[{label}] home page_view on load', len(pv)==1 and pv[0]['p']['page_path']=='/', str(pv))
        for sec in ['stump-grinding','forestry-mulching','service-area','about']:
            p.evaluate(f"location.hash='{sec}'"); p.wait_for_timeout(250)
        paths=[e['p']['page_path'] for e in events(p) if e['n']=='page_view']
        ok(f'[{label}] section page_views', paths==['/','/stump-grinding','/forestry-mulching','/service-area','/about'], str(paths))
        # link clicks: intercept navigation by preventing default after our capture listener
        p.evaluate("""()=>document.addEventListener('click',e=>{const a=e.target.closest('a');if(a&&/^(tel:|mailto:|https?:)/.test(a.getAttribute('href')))e.preventDefault();})""")
        def click_first(sel):
            return p.evaluate(f"""()=>{{const a=[...document.querySelectorAll('{sel}')]; if(!a.length) return 0; a.forEach(x=>x.click()); return a.length}}""")
        n_tel=click_first('a[href^="tel:"]'); n_mail=click_first('a[href^="mailto:"]')
        n_rev=click_first('a[href*="google.com/maps"]'); n_fb=click_first('a[href*="facebook.com"]')
        ev=events(p); c=lambda n: sum(1 for e in ev if e['n']==n)
        ok(f'[{label}] phone_click per tel link', n_tel>0 and c('phone_click')==n_tel, f'links={n_tel} events={c("phone_click")}')
        ok(f'[{label}] email_click per mailto link', n_mail>0 and c('email_click')==n_mail, f'links={n_mail} events={c("email_click")}')
        ok(f'[{label}] review_link_click', n_rev>0 and c('review_link_click')==n_rev, f'links={n_rev} events={c("review_link_click")}')
        ok(f'[{label}] facebook_click', n_fb>0 and c('facebook_click')==n_fb, f'links={n_fb} events={c("facebook_click")}')
        p.evaluate("location.hash='home'"); p.wait_for_timeout(250)
        p.evaluate("""()=>{const a=[...document.querySelectorAll('a[href="#about"]')].find(x=>/estimate/i.test(x.textContent)); a&&a.click()}""")
        p.wait_for_timeout(250)
        ok(f'[{label}] estimate_cta_click', any(e['n']=='estimate_cta_click' for e in events(p)))
        # form: success
        def fill_submit():
            p.evaluate("location.hash='about'"); p.wait_for_timeout(300)
            p.fill('#f-name','TEST - Claude analytics check'); p.fill('#f-phone','8655550100')
            p.fill('#f-area','Harriman, TN'); p.select_option('#f-service','Forestry Mulching')
            p.click('#intake-form button[type=submit]'); p.wait_for_timeout(700)
        form_mode['m']='ok'; fill_submit()
        gl=[e for e in events(p) if e['n']=='generate_lead']
        ok(f'[{label}] generate_lead on successful submit (with service)', len(gl)==1 and gl[0]['p']['service']=='Forestry Mulching', str(gl))
        ok(f'[{label}] success message shown to visitor', 'Thanks' in p.inner_text('#form-msg'), p.inner_text('#form-msg'))
        form_mode['m']='bad'; fill_submit()
        fe=[e for e in events(p) if e['n']=='form_error']
        ok(f'[{label}] form_error on rejected submit', len(fe)==1 and 'Activation' in fe[0]['p']['detail'], str(fe))
        form_mode['m']='down'; fill_submit()
        fe=[e for e in events(p) if e['n']=='form_error']
        ok(f'[{label}] form_error on network failure', len(fe)==2 and fe[1]['p']['detail']=='network', str(fe))
        ok(f'[{label}] no generate_lead on failures', sum(1 for e in events(p) if e['n']=='generate_lead')==1)
        hero=p.evaluate("""()=>fetch('solaterra_hero.jpg').then(r=>r.headers.get('content-type'))""")
        ok(f'[{label}] hero image served as image', hero and 'image' in hero, hero)
        ok(f'[{label}] no JavaScript errors', not errs, str(errs))
        ok(f'[{label}] gtag library requested', bool(gtm_loaded))
        ctx.close()
    b.close()
for r in results: print(*r, sep=' | ')
print('form posts intercepted (none reached FormSubmit):', len(form_posts))
print('TOTAL', sum(r[0]=='PASS' for r in results),'/',len(results))
