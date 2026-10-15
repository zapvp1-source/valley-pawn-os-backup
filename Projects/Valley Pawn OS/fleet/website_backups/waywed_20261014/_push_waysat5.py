import json,os,base64,urllib.request,urllib.parse,sys,time
D=os.path.dirname(os.path.abspath(__file__))
cred=dict(l.strip().split('=',1) for l in open('/sessions/awesome-intelligent-goldberg/mnt/Projects/Website/shop-build/.wp_app_credentials') if '=' in l)
auth='Basic '+base64.b64encode(f"{cred['WP_USER']}:{cred['WP_APP_PASSWORD']}".encode()).decode()
site=cred['WP_SITE']
def req(method,path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    r=urllib.request.Request(site+path,data=data,method=method,headers={'Authorization':auth,'User-Agent':'Mozilla/5.0','Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=90) as f: return json.load(f)
changes=json.load(open(os.path.join(D,'_new/changes.json')))
keys=list(changes)[int(sys.argv[1]):int(sys.argv[2])] if len(sys.argv)>2 else list(changes)
LP=os.path.join(D,'_new/push_log.json')
log=json.load(open(LP)) if os.path.exists(LP) else {}
for key in keys:
    typ,_id=key.split('_',1); _id=_id.replace('____','//')
    path=f"/wp-json/wp/v2/{typ}/{urllib.parse.quote(_id,safe='/')}"
    orig=open(os.path.join(D,'_full',key+'.raw.html')).read()
    new=open(os.path.join(D,'_new',key+'.raw.html')).read()
    try:
        cur=req('GET',path+'?context=edit')['content']['raw']
        if cur==new:
            log[key]='OK (already)'; print(key,log[key]); continue
        if cur!=orig:
            log[key]='SKIP changed since backup'; print(key,log[key]); continue
        req('POST',path,{'content':new})
        back=req('GET',path+'?context=edit')['content']['raw']
        log[key]='OK' if back==new else 'MISMATCH after write'
    except Exception as e:
        log[key]='ERR %s'%e
    print(key,log[key]); time.sleep(0.3)
    json.dump(log,open(LP,'w'),indent=1)
print(sum(v.startswith('OK') for v in log.values()),'/',len(log))
