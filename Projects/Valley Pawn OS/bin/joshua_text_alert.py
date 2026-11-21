#!/usr/bin/env python3
"""joshua_text_alert.py v2 (2026-11-20; v2 adds text-reply handling) — texts Joshua when Preston asks something or a store needs funds.

Joshua 2026-11-20: "anytime Preston is asking something on slack or funds are needed you need to text me also.
Only those 5 channels funds and Preston Goldilocks."

Runs from launchd (com.valleypawn.joshua-text-alert, every 2 min). Each run:
  1. Reads new messages (top-level + new thread replies) since the last run in the 6 watched channels,
     using the VP OPS bot token (vp_slack.token()).
  2. Texts Joshua (+18049304221, via send_text_verified.py) when:
       - Preston posts anything that isn't a bare ack ("ok", "ty", "thanks"), in any of the 6 channels, or
       - anyone other than Joshua posts a funds-type message in one of the 5 funds channels.
  3. Never posts to Slack. Never texts anyone but Joshua. First run only sets the starting point (no backlog blast).
State: ~/.joshua_text_alert_state.json   Log: ~/Library/Logs/valleypawn/joshua-text-alert.log
Flags: --dry-run (log what would be texted, send nothing, don't advance state)
"""
import datetime, json, os, re, subprocess, sys, time

HOME = os.path.expanduser('~')
OS_DIR = os.path.join(HOME, 'Documents/Claude/Projects/Valley Pawn OS')
sys.path.insert(0, os.path.join(OS_DIR, 'bin'))
import vp_slack  # noqa: E402

SENDER = os.path.join(OS_DIR, 'bin/send_text_verified.py')
STATE = os.path.join(HOME, '.joshua_text_alert_state.json')
STATUS = os.path.join(OS_DIR, 'fleet/state/joshua_text_alert.json')
LOG = os.path.join(HOME, 'Library/Logs/valleypawn/joshua-text-alert.log')
TO = '+18049304221'
JOSHUA = 'U03BB52MDSA'
PRESTON = 'U03BWMEM9GR'
FUNDS = {'C03BLLRN64U': 'boro-funds', 'C03BLHFJ3KN': 'pepper-funds', 'C063K8E02TW': 'roanoke-funds',
         'C03B3K5DL6T': 'lex-funds', 'C03BWRKEDUZ': 'harrisonburg-funds'}
GOLDILOCKS = {'C0BGXSTT4TY': 'preston-goldilocks'}
CHANNELS = {**FUNDS, **GOLDILOCKS}
DRY = '--dry-run' in sys.argv
ACK = re.compile(r"^\W*(ok(ay)?|k|ty|thx|thanks?( you)?|thank you|got it|will do|yes|yep|no|np|cool|great|perfect|sounds good|👍)\W*$", re.I)
FUNDS_RE = re.compile(
    r"\bfunds?\b|\bmoney\b|\bcash\b|\bshort\b|\bneed\b|\bsend\b|\btransfer\b|\bdeposit\b|\bsafe\b|\bcoh\b|\blow on\b"
    r"|\bbuy(ing|s)?\b|\bloans?\b|\$\s?\d|\b\d{3,}(\.\d\d)?\b", re.I)
FUNDS_STRONG = re.compile(r"\bfunds?\b|\bneed (some |more )?(money|cash)\b|\bshort\b|\blow on (cash|money|funds)\b|\bsend (me |us )?(money|cash|funds)\b|\btransfer\b", re.I)


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg
    with open(LOG, 'a') as f:
        f.write(line + '\n')
    print(line)


def load(p, d):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return d


def save(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, p)


_names = {}
def name(uid):
    if uid in _names:
        return _names[uid]
    n = uid
    try:
        r = vp_slack.call('users.info', params={'user': uid})
        if r.get('ok'):
            p = r['user'].get('profile', {})
            n = p.get('display_name') or p.get('real_name') or r['user'].get('real_name') or uid
    except Exception:
        pass
    _names[uid] = n
    return n


def clean(text):
    t = re.sub(r'<@(U[A-Z0-9]+)(\|[^>]*)?>', lambda m: '@' + name(m.group(1)), text or '')
    t = re.sub(r'<(https?://[^|>]+)\|([^>]+)>', r'\2', t)
    t = re.sub(r'<(https?://[^>]+)>', r'\1', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:300] + ('…' if len(t) > 300 else '')


def wants_text(ch, m):
    user, text = m.get('user'), (m.get('text') or '').strip()
    if not user or user == JOSHUA or m.get('bot_id') or m.get('subtype') not in (None, 'thread_broadcast', 'file_share'):
        return None
    if user == PRESTON:
        if not text and not m.get('files'):
            return None
        if text and ACK.match(text):
            return None
        return 'preston'
    if ch in FUNDS:
        if FUNDS_STRONG.search(text):
            return 'funds'
        hits = len(set(x.group(0).lower() for x in FUNDS_RE.finditer(text)))
        if hits >= 2:
            return 'funds'
    return None


def send(body):
    if DRY:
        log('[dry] would text: ' + body)
        return True
    r = subprocess.run(['/usr/bin/python3', SENDER, '--to', TO, '--text', body, '--task', 'joshua-text-alert'],
                       capture_output=True, text=True, timeout=60)
    ok = r.returncode == 0
    log('text %s rc=%s %s' % ('SENT' if ok else 'FAILED', r.returncode, (r.stdout or r.stderr).strip()[-200:]))
    return ok


# ---- v2 (2026-11-20): Joshua: "if I respond to the text I need you to act on it." ----
DB = os.path.join(HOME, 'Library/Messages/chat.db')
QUEUE = os.path.join(OS_DIR, 'fleet/state/joshua_text_alert/replies.jsonl')
RUNNER = os.path.join(OS_DIR, 'bin/joshua_reply_runner.py')
OURS = ('Preston asked — ', 'Funds — ', 'Test:', 'Done — ', "Can't — ", 'Working on it — ')
REPLY_WINDOW_H = 12


def _body(text, blob):
    if text:
        return text
    if not blob:
        return ''
    try:
        b = blob.split(b'NSString', 1)[1][5:]
        if b[0] == 0x81:
            n = int.from_bytes(b[1:3], 'little')
            return b[3:3 + n].decode('utf-8', 'replace')
        return b[1:1 + b[0]].decode('utf-8', 'replace')
    except Exception:
        return ''


def reply_pass(st):
    import sqlite3
    con = sqlite3.connect('file:%s?mode=ro' % DB, uri=True, timeout=5)
    try:
        rows = con.execute("""SELECT m.ROWID, m.date, m.text, m.attributedBody, m.associated_message_type
            FROM message m JOIN chat_message_join cmj ON cmj.message_id=m.ROWID JOIN chat c ON c.ROWID=cmj.chat_id
            WHERE c.chat_identifier=? AND m.ROWID>? ORDER BY m.ROWID""", (TO, int(st.get('reply_rowid') or 0))).fetchall()
    finally:
        con.close()
    if st.get('reply_rowid') is None:          # first time: start from now, no backlog
        st['reply_rowid'] = rows[-1][0] if rows else 0
        save(STATE, st)
        return
    queued = 0
    for rowid, d, text, blob, assoc in rows:
        st['reply_rowid'] = rowid
        if assoc:                              # tapbacks / reactions
            continue
        body = _body(text, blob).replace('\ufffc', '').strip()
        if not body or body.startswith(OURS):
            continue
        at = 978307200 + (d or 0) / 1e9
        prior = [a for a in st.get('alerts', []) if a['at'] <= at + 5]
        if not prior or at - prior[-1]['at'] > REPLY_WINDOW_H * 3600:
            continue                           # not a reply to an alert (note-to-self)
        item = {'rowid': rowid, 'at': at, 'reply': body, 'alert': prior[-1], 'recent_alerts': prior[-5:]}
        if DRY:
            log('[dry] would queue reply %s' % json.dumps(item)[:300])
            continue
        os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
        with open(QUEUE, 'a') as f:
            f.write(json.dumps(item) + '\n')
        queued += 1
        log('queued reply rowid=%s for alert %s %s: %s' % (rowid, prior[-1]['cname'], prior[-1]['ts'], body[:120]))
    if not DRY:
        save(STATE, st)
    if queued or os.path.exists(QUEUE):
        subprocess.Popen(['/usr/bin/python3', RUNNER], start_new_session=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    st = load(STATE, {})
    first = not st.get('since')
    now = time.time()
    since = {ch: float(st.get('since', {}).get(ch, now)) for ch in CHANNELS}
    sent = st.get('sent', {})
    alerts = st.get('alerts', [])
    pending, errors = [], []
    for ch, cname in CHANNELS.items():
        h = vp_slack.call('conversations.history', params={'channel': ch, 'limit': 50})
        if not h.get('ok'):
            errors.append('%s %s' % (cname, h.get('error')))
            continue
        for m in h.get('messages', []):
            if float(m['ts']) > since[ch]:
                pending.append((ch, m, None))
            # thread replies newer than our cutoff
            if m.get('reply_count') and float(m.get('latest_reply', 0)) > since[ch]:
                r = vp_slack.call('conversations.replies', params={'channel': ch, 'ts': m['ts'], 'limit': 100})
                for rm in (r.get('messages', [])[1:] if r.get('ok') else []):
                    if float(rm['ts']) > since[ch]:
                        pending.append((ch, rm, m))
    pending.sort(key=lambda x: float(x[1]['ts']))
    texted, failed = 0, 0
    newest = dict(since)
    for ch, m, parent in pending:
        key = ch + ':' + m['ts']
        why = None if first else wants_text(ch, m)
        ok = True
        if why and key not in sent:
            who = 'Preston' if m.get('user') == PRESTON else name(m['user'])
            label = ('Preston asked' if why == 'preston' else 'Funds') + ' — #' + CHANNELS[ch]
            body = '%s\n%s: %s' % (label, who, clean(m.get('text')) or '(sent a file)')
            if parent:
                body += '\n(in reply to: %s)' % clean(parent.get('text'))[:120]
            ok = send(body)
            if ok and not DRY:
                sent[key] = int(now)
                texted += 1
                alerts.append({'at': time.time(), 'channel': ch, 'cname': CHANNELS[ch], 'ts': m['ts'],
                               'thread_ts': (parent or {}).get('ts') or m.get('thread_ts') or m['ts'],
                               'who': who, 'user': m.get('user'), 'text': (m.get('text') or '')[:1500]})
            elif not ok:
                failed += 1
        # advance the cutoff only past messages we handled; a failed send is retried next run
        if ok:
            newest[ch] = max(newest[ch], float(m['ts']))
        else:
            break
    if not DRY:
        cutoff = now - 7 * 86400
        st = {'since': {ch: newest[ch] for ch in CHANNELS},
              'sent': {k: v for k, v in sent.items() if v > cutoff},
              'alerts': [a for a in alerts if a['at'] > cutoff][-200:],
              'reply_rowid': load(STATE, {}).get('reply_rowid')}
        save(STATE, st)
        try:
            reply_pass(st)
        except Exception as e:
            log('reply pass error %s' % e)
    save(STATUS, {'last_run': datetime.datetime.now().isoformat(timespec='seconds'), 'first_run': first,
                  'checked': len(pending), 'texted': texted, 'failed': failed, 'errors': errors, 'dry': DRY})
    log('run: first=%s checked=%d texted=%d failed=%d errors=%s' % (first, len(pending), texted, failed, errors))


if __name__ == '__main__':
    main()
