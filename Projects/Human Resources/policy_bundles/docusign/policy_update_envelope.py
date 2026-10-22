#!/usr/bin/env python3
"""Monthly Policy Update -> one DocuSign envelope definition per employee (zero logins; the DocuSign connector sends).
Usage:
  python3 policy_update_envelope.py ../manifests/<YYYY-MM>.json recipients.json OUTDIR [--draft]
recipients.json = [{"name": "First Last", "email": "x@y"}]  (active employees from the Gusto connector; never a store mailbox)
Writes OUTDIR/<slug>__<email>.json (envelopeDefinition for mcp__Docusign__createEnvelope, accountId 320a0ff8-3001-4e1a-93b4-4fc3004b1116)
and OUTDIR/<slug>__preview.txt (exactly the text that lands on the form). Exit 2 = content too long / missing -> fix the manifest.
--draft => status "created" (nobody is emailed; used for Joshua's preview and for proofing)."""
import json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
FORM_URL = os.environ.get('VP_POLICY_UPDATE_FORM_URL', '')
if not FORM_URL and os.path.exists(os.path.join(HERE, 'FORM_URL.txt')):
    FORM_URL = open(os.path.join(HERE, 'FORM_URL.txt')).read().strip()
MAX = 3800                     # DocuSign text tab limit is 4000; keep a margin
SMALL = 40
LAYOUT = json.load(open(os.path.join(HERE, 'layout_policy_update.json')))

def die(m): print(m, file=sys.stderr); sys.exit(2)

def compose(man):
    new = '\n'.join('• ' + s.strip() for s in man['whats_new'])
    blocks = []
    for p in man.get('policies', []):
        b = [f"{p['title'].upper()}  ({p.get('area','')} · starts {p.get('starts', man['policy_day'])})", f"THE RULE: {p['box']}"]
        b += ['→ ' + l.lstrip('→ ').strip() for l in p['lines']]
        blocks.append('\n'.join(b))
    for a in man.get('attachments_text', []):
        blocks.append(f"{a['title'].upper()}  ({a.get('area','')})\n{a['text'].strip()}")
    pol1, pol2 = [], []
    for b in blocks:   # fill page 2 first, overflow to page 3, never split a policy
        if not pol2 and len('\n\n'.join(pol1 + [b])) <= MAX: pol1.append(b)
        else: pol2.append(b)
    f = {'month': man['month'], 'day': man['policy_day'].split(', ', 1)[-1], 'signby': man['sign_by'].split(', ', 1)[-1],
         'new': new, 'pol1': '\n\n'.join(pol1) or '(No new policies this month.)', 'pol2': '\n\n'.join(pol2) or '(Nothing further this month.)',
         'hb': f"v{man['handbook']}" + (' (NEW this month)' if man.get('handbook_new') else ''),
         'pp': f"v{man['pp']}" + (' (NEW this month)' if man.get('pp_new') else ''),
         'ref': f"PU-{man['slug']}"}
    for k, v in f.items():
        lim = MAX if k in ('new', 'pol1', 'pol2') else SMALL
        if not v.strip(): die(f'missing {k}')
        if len(v) > lim: die(f'{k} is {len(v)} chars; max {lim}. Shorten the manifest text.')
    return f

def tab(anchor, w, h, value):
    return {'documentId': '1', 'recipientId': '1', 'anchorString': f'\\{anchor}\\', 'anchorUnits': 'pixels',
            'anchorXOffset': '0', 'anchorYOffset': '4', 'anchorIgnoreIfNotPresent': 'false',
            'width': str(w), 'height': str(h), 'font': 'helvetica', 'fontSize': 'Size9', 'maxLength': '4000',
            'tabLabel': anchor, 'locked': 'true', 'required': 'true', 'value': value}

def envelope(man, f, person, draft):
    if not FORM_URL.startswith('https://'): die('FORM_URL not set (FORM_URL.txt)')
    if not person.get('email') or not person.get('name'): die(f'recipient needs name + email: {person}')
    texts = [tab(f'f_{k}', *LAYOUT[k], v) for k, v in f.items()]
    n = tab('n_1', *LAYOUT['n_1'], person['name']); n['anchorYOffset'] = '2'; texts.append(n)
    first = person['name'].split()[0]
    return {'status': 'created' if draft else 'sent',
            'emailSubject': f"Valley Pawn — {man['month']} Policy Update — please sign by {f['signby']}",
            'emailBlurb': (f"Hi {first}, this is the {man['month']} Policy Update: everything new or changed this month, in one place. "
                           f"Please read all four pages and sign once by {f['signby']}. Questions: ask your store manager, Preston, "
                           "or Goldilocks in #ask-goldilocks."),
            'documents': [{'documentId': '1', 'name': f"Valley Pawn Policy Update {man['slug']}.pdf", 'remoteUrl': FORM_URL}],
            'recipients': {'signers': [{'email': person['email'], 'name': person['name'], 'recipientId': '1', 'routingOrder': '1',
                'tabs': {'textTabs': texts,
                         'signHereTabs': [{'documentId': '1', 'recipientId': '1', 'anchorString': '\\s_1\\', 'anchorUnits': 'pixels',
                                           'anchorXOffset': '0', 'anchorYOffset': '0', 'tabLabel': 'sig_1'}],
                         'dateSignedTabs': [{'documentId': '1', 'recipientId': '1', 'anchorString': '\\d_1\\', 'anchorUnits': 'pixels',
                                             'anchorXOffset': '0', 'anchorYOffset': '0', 'tabLabel': 'date_1'}]}}]},
            'customFields': {'textCustomFields': [{'name': 'vp_policy_update', 'value': man['slug'], 'show': 'false', 'required': 'false'}]},
            'notification': {'useAccountDefaults': 'false',
                             'reminders': {'reminderEnabled': 'true', 'reminderDelay': '3', 'reminderFrequency': '3'},
                             'expirations': {'expireEnabled': 'true', 'expireAfter': '30', 'expireWarn': '5'}}}

if __name__ == '__main__':
    if len(sys.argv) < 4: die(__doc__)
    man = json.load(open(sys.argv[1])); people = json.load(open(sys.argv[2])); out = sys.argv[3]; draft = '--draft' in sys.argv
    os.makedirs(out, exist_ok=True); f = compose(man)
    with open(os.path.join(out, f"{man['slug']}__preview.txt"), 'w') as fh:
        for k, v in f.items(): fh.write(f'===== {k} ({len(v)} chars)\n{v}\n\n')
    seen = set()
    for p in people:
        e = p['email'].strip().lower()
        if e in seen: die(f'duplicate recipient {e}')
        seen.add(e)
        json.dump(envelope(man, f, p, draft), open(os.path.join(out, f"{man['slug']}__{re.sub(r'[^a-z0-9]+','_',e)}.json"), 'w'), indent=1, ensure_ascii=False)
    print(f"OK {len(people)} envelope(s) {'DRAFT' if draft else 'SEND'} -> {out}; lengths " + ', '.join(f'{k}={len(v)}' for k, v in f.items()))
