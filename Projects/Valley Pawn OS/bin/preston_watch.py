#!/usr/bin/env python3
"""preston_watch.py v2 (2026-10-08) — native watcher that makes Preston's requests start within ~1 minute.

Runs from launchd (com.valleypawn.preston-watch, every 2 min). Each invocation makes TWO passes ~55 s apart,
so a new request is seen within about a minute.

Each pass:
  1. Reads the last 20 messages of #preston-claude (every Preston message is a request) and #employee-prospects
     (only Preston messages that address Claude), as the VP OPS ENGINE bot.
  2. A Preston message from the last 72 h is OPEN until Joshua's account (how Claude posts) replies in its
     thread or later in the channel.
  3. New OPEN message -> one short reply in his thread ("Got it — on it") and immediately starts the cloud
     scheduled task "Preston assistant" through its fire endpoint. The cloud task does the work.
  4. Still OPEN 20 min after a start -> start it again (max 3 starts per message). Still OPEN after 90 min ->
     one FAILURE_LEDGER row (fleet-guardian handles it). No DMs, no channel noise.
  5. Writes Valley Pawn OS/fleet/state/preston_assistant/watch_status.json.

v1 bug fixed: v1 only acked the first message of a "pending burst" measured against ~/preston_claude_last_ts.txt,
which only the retired Cowork task advanced. After that task stopped (9/16) every later request counted as part
of the same old burst, so nothing was ever acked again. v2 tracks each message on its own and never reads that file.

Fire key: Keychain service `vp-preston-assistant-fire-token` (saved by "Install Preston Assistant Key.command").
Without it the watcher still acks, and the hourly cloud run picks the request up.
"""
import datetime, getpass, json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

HOME = os.path.expanduser('~')
OS_DIR = os.path.join(HOME, 'Documents/Claude/Projects/Valley Pawn OS')
STATE_DIR = os.path.join(OS_DIR, 'fleet/state/preston_assistant')
STATUS_FILE = os.path.join(STATE_DIR, 'watch_status.json')
CONFIG_FILE = os.path.join(STATE_DIR, 'config.json')
STATE_FILE = os.path.join(HOME, '.preston_watch_state_v2.json')
LEDGER = os.path.join(OS_DIR, 'fleet/FAILURE_LEDGER.md')
INSTALLER = os.path.join(OS_DIR, 'Install Preston Assistant Key.command')
LOG = os.path.join(HOME, 'Library/Logs/valleypawn/preston-watch.log')

PRESTON_CH = 'C0BGXSTT4TY'      # #preston-claude — every Preston message is a request
PROSPECTS_CH = 'C0BQDRXRPEJ'    # #employee-prospects — only messages that address Claude
PRESTON = 'U03BWMEM9GR'
JOSHUA = 'U03BB52MDSA'
SLACK_SERVICE = 'vp-ops-slack-bot-token'
FIRE_SERVICE = 'vp-preston-assistant-fire-token'
DEFAULT_ROUTINE = 'trig_01CjJusgBC2hkcCg5GHziHtC'
WINDOW_H = 72
REFIRE_MIN = 20
MAX_FIRES = 3
LEDGER_MIN = 90
PASS_GAP_S = 55
ACK_TEXT = 'Got it, Preston — on it. I will post back here as soon as it is done.'
DRY = '--dry-run' in sys.argv
ONE_PASS = '--once' in sys.argv or DRY


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg
    with open(LOG, 'a') as f:
        f.write(line + '\n')
    print(line)


def keychain(service, with_account=True):
    for extra in ((['-a', getpass.getuser()] if with_account else []), []):
        try:
            r = subprocess.run(['security', 'find-generic-password', '-s', service] + extra + ['-w'],
                               capture_output=True, text=True, timeout=10)
            if r.stdout.strip():
                return r.stdout.strip()
        except Exception:
            pass
    return None


def slack(token, method, payload, get=False):
    if get:
        req = urllib.request.Request('https://slack.com/api/' + method + '?' + urllib.parse.urlencode(payload),
                                     headers={'Authorization': 'Bearer ' + token})
    else:
        req = urllib.request.Request('https://slack.com/api/' + method, data=json.dumps(payload).encode(),
                                     headers={'Authorization': 'Bearer ' + token,
                                              'Content-Type': 'application/json; charset=utf-8'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def load_json(p, default):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, p)


def addresses_claude(text):
    t = (text or '').strip().lower()
    return t.startswith('claude') or 'claude can' in t or 'claude,' in t or 'get him to' in t or 'claude is' in t


def answered(token, channel, msg, history):
    ts = float(msg['ts'])
    if any(m.get('user') == JOSHUA and float(m['ts']) > ts and not m.get('thread_ts') for m in history):
        # A later top-level post from Joshua's account counts only in #preston-claude (it is a 1:1 channel).
        if channel == PRESTON_CH:
            return True
    if msg.get('reply_count'):
        r = slack(token, 'conversations.replies', {'channel': channel, 'ts': msg['ts'], 'limit': 50}, get=True)
        if r.get('ok'):
            return any(m.get('user') == JOSHUA and float(m['ts']) > ts for m in r.get('messages', [])[1:])
    return False


def fire(routine_id, key, text):
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/claude_code/routines/%s/fire' % routine_id,
        data=json.dumps({'text': text}).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + key, 'anthropic-beta': 'experimental-cc-routine-2026-04-01',
                 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return True, 'http %d' % r.status
    except urllib.error.HTTPError as e:
        return False, 'http %d %s' % (e.code, e.read().decode(errors='replace')[:200])
    except Exception as e:
        return False, type(e).__name__ + ' ' + str(e)[:200]


def ledger_row(text):
    try:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M ET')
        with open(LEDGER, 'a') as f:
            f.write('| %s | preston-assistant | %s | NEEDS_HUMAN: no | OPEN |\n' % (now, text))
    except Exception as e:
        log('ledger write failed ' + str(e))


def one_pass(token, fire_key, routine_id, state):
    now = time.time()
    cutoff = now - WINDOW_H * 3600
    open_msgs, errors = [], []
    for ch in (PRESTON_CH, PROSPECTS_CH):
        h = slack(token, 'conversations.history', {'channel': ch, 'limit': 20}, get=True)
        if not h.get('ok'):
            errors.append('%s %s' % (ch, h.get('error')))
            continue
        hist = h.get('messages', [])
        for m in hist:
            if m.get('user') != PRESTON or m.get('subtype') or float(m['ts']) < cutoff:
                continue
            if ch == PROSPECTS_CH and not addresses_claude(m.get('text')):
                continue
            if answered(token, ch, m, hist):
                state['done'][m['ts']] = datetime.datetime.now().isoformat(timespec='seconds')
                continue
            open_msgs.append((ch, m))
    open_msgs.sort(key=lambda x: float(x[1]['ts']))

    for ch, m in open_msgs:
        rec = state['open'].setdefault(m['ts'], {'channel': ch, 'acked': None, 'fires': [], 'ledger': False})
        if not rec['acked']:
            if DRY:
                log('[dry] would ack %s %s' % (ch, m['ts']))
            else:
                r = slack(token, 'chat.postMessage', {'channel': ch, 'thread_ts': m['ts'], 'text': ACK_TEXT})
                log('ack %s %s %s' % (ch, m['ts'], 'sent' if r.get('ok') else 'FAILED ' + str(r.get('error'))))
            rec['acked'] = datetime.datetime.now().isoformat(timespec='seconds')
        last_fire = rec['fires'][-1]['at'] if rec['fires'] else 0
        if fire_key and len(rec['fires']) < MAX_FIRES and (not rec['fires'] or now - last_fire >= REFIRE_MIN * 60):
            text = ('Started by the Mac watcher: Preston posted a new request in %s at ts %s. Handle it now.'
                    % ('#preston-claude' if ch == PRESTON_CH else '#employee-prospects', m['ts']))
            if DRY:
                log('[dry] would fire for ' + m['ts'])
            else:
                ok, detail = fire(routine_id, fire_key, text)
                rec['fires'].append({'at': now, 'ok': ok, 'detail': detail})
                log('fire %s %s %s' % (m['ts'], 'ok' if ok else 'FAILED', detail))
        age_min = (now - float(m['ts'])) / 60
        if age_min >= LEDGER_MIN and not rec['ledger'] and not DRY:
            ledger_row('A request from Preston has been waiting %d minutes without an answer.' % age_min)
            rec['ledger'] = True

    # forget anything answered or out of the window
    open_ts = {m['ts'] for _, m in open_msgs}
    state['open'] = {ts: v for ts, v in state['open'].items() if ts in open_ts}
    state['done'] = {ts: v for ts, v in state['done'].items() if float(ts) >= cutoff}
    return open_msgs, errors


def main():
    token = keychain(SLACK_SERVICE)
    if not token or not token.startswith('xoxb-'):
        token = os.environ.get('SLACK_BOT_TOKEN', '').strip()
    if not token.startswith('xoxb-'):
        log('ERROR no slack token'); return 1
    fire_key = keychain(FIRE_SERVICE)
    routine_id = load_json(CONFIG_FILE, {}).get('routine_id', DEFAULT_ROUTINE)
    try:  # keep the one-time key installer double-clickable
        if os.path.exists(INSTALLER) and not os.access(INSTALLER, os.X_OK):
            os.chmod(INSTALLER, 0o755)
    except Exception:
        pass
    state = load_json(STATE_FILE, {'open': {}, 'done': {}})
    state.setdefault('open', {}); state.setdefault('done', {})
    passes = 1 if ONE_PASS else 2
    open_msgs, errors = [], []
    for i in range(passes):
        if i:
            time.sleep(PASS_GAP_S)
        try:
            open_msgs, errors = one_pass(token, fire_key, routine_id, state)
        except Exception as e:
            errors = [type(e).__name__ + ' ' + str(e)[:200]]
            log('ERROR pass %d %s' % (i, errors[0]))
        save_json(STATE_FILE, state)
    status = {
        'checked': datetime.datetime.now().isoformat(timespec='seconds'),
        'version': 2,
        'fire_key_installed': bool(fire_key),
        'routine_id': routine_id,
        'open_requests': [{'channel': ch, 'ts': m['ts'], 'text': (m.get('text') or '')[:160]} for ch, m in open_msgs],
        'tracking': state['open'],
        'errors': errors,
    }
    if not DRY:
        save_json(STATUS_FILE, status)
    log('ok open=%d fire_key=%s errors=%d' % (len(open_msgs), bool(fire_key), len(errors)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
