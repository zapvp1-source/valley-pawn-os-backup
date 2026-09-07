#!/usr/bin/env python3
import json, base64, urllib.request

WORK = '/tmp/vp-shop-run'
Q = chr(34)

with open(WORK + '/shop-block-wrapped.html', encoding='utf-8') as f:
    content = f.read()

creds = {}
with open('/Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k] = v

user = creds.get('WP_USER')
pw = creds.get('WP_APP_PASSWORD')
site = creds.get('WP_SITE')

token = base64.b64encode((user + ':' + pw).encode('utf-8')).decode('ascii')

payload = json.dumps({'content': content, 'status': 'publish'}).encode('utf-8')

req = urllib.request.Request(
    site + '/wp-json/wp/v2/pages/833',
    data=payload,
    method='POST',
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
    },
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        status = resp.status
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='ignore')
    status = e.code

with open(WORK + '/publish_response.json', 'w', encoding='utf-8') as f:
    f.write(body)

try:
    j = json.loads(body)
    rid = j.get('id')
    rstatus = j.get('status')
    rlink = j.get('link')
except Exception:
    rid = None
    rstatus = None
    rlink = None

print('HTTP_STATUS=' + str(status))
print('RESP_ID=' + str(rid))
print('RESP_STATUS=' + str(rstatus))
print('RESP_LINK=' + str(rlink))
