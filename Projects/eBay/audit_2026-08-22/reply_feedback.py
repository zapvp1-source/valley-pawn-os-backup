import json, os, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
NS = 'urn:ebay:apis:eBLBaseComponents'


def call(tok, name, inner):
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            ) % (name, tok, inner, name)
    h = {'X-EBAY-API-SITEID': '0', 'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
         'X-EBAY-API-CALL-NAME': name, 'X-EBAY-API-APP-NAME': ns['APP_ID'],
         'X-EBAY-API-DEV-NAME': ns['DEV_ID'], 'X-EBAY-API-CERT-NAME': ns['CERT_ID'],
         'X-EBAY-API-IAF-TOKEN': tok, 'Content-Type': 'text/xml'}
    with urlopen(Request('https://api.ebay.com/ws/api.dll', data=body.encode(), headers=h), timeout=90) as r:
        return ET.fromstring(r.read().decode())


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text else d


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# store, FeedbackID, TargetUserID (the buyer who left it), ItemID, CommentType, reply text
# brand voice per valley-pawn-context: warm, confident, honest ("What's Right Is Right")
REPLIES = [
    ('Harrisonburg', '2830482609015', 'danarmen_44', '800242774391', 'Neutral',
     "Thanks for the honest feedback and glad the console itself is working great. You're right that "
     "should have been listed clearly up front, and we're sorry it wasn't. If you'd still like a "
     "charger, message us anytime and we'll take care of it."),
    ('Lexington', '2609016212012', 'kenfried7', '157781697638', 'Negative',
     "We're sorry the set didn't match what the listing said -- that's on us to get right, not you. "
     "If you still have this item, please message us and we'll make it right with a return or partial "
     "refund, whichever works best for you."),
    ('Roanoke', '2814396613019', 'scottsamma', '306888657551', 'Neutral',
     "Sorry we missed your message and that the buckle needed repair -- neither should have happened. "
     "Please send us the repair receipt and we'll reimburse you; message us here or call the store "
     "directly and we'll take care of it right away."),
]

st_path = os.path.expanduser('~/ebay_feedback_reply_state.json')
st = json.load(open(st_path)) if os.path.exists(st_path) else {}
results = []
for store, fid, buyer, item, ctype, reply_text in REPLIES:
    key = fid
    if key in st:
        results.append((store, fid, 'already replied per state file'))
        continue
    inner = ('<TargetUserID>%s</TargetUserID>'
             '<ItemID>%s</ItemID>'
             '<ResponseText><![CDATA[%s]]></ResponseText>'
             '<ResponseType>Reply</ResponseType>'
             '<FeedbackID>%s</FeedbackID>'
             ) % (buyer, item, reply_text, fid)
    r = call(TOK[store], 'RespondToFeedback', inner)
    ack = T(r, 'Ack')
    errs = [T(e, 'LongMessage') for e in r.findall('.//{%s}Errors' % NS)]
    results.append((store, fid, ack, errs[:2]))
    if ack in ('Success', 'Warning'):
        st[key] = {'store': store, 'item': item, 'buyer': buyer, 'reply': reply_text,
                   'ts': time.strftime('%Y-%m-%dT%H:%M:%S')}
        json.dump(st, open(st_path, 'w'), indent=1)
    time.sleep(0.3)

for r in results:
    print(r)
