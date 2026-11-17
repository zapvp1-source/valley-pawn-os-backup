import base64,json,urllib.request,os
C=dict(l.strip().split('=',1) for l in open(os.path.expanduser('~/mnt/Projects/Website/shop-build/.wp_app_credentials')) if '=' in l)
AUTH='Basic '+base64.b64encode((C['WP_USER']+':'+C['WP_APP_PASSWORD']).encode()).decode()
def wp(path,payload=None,method='GET'):
    r=urllib.request.Request(C['WP_SITE']+'/wp-json/wp/v2'+path,data=json.dumps(payload).encode() if payload is not None else None,method=method,headers={'Authorization':AUTH,'Content-Type':'application/json','User-Agent':'vp-audit'})
    with urllib.request.urlopen(r,timeout=60) as x: return json.load(x)
