#!/usr/bin/env python3
"""preston_watch.py — native, zero-Claude-usage watcher for #preston-claude.

Runs every 2 minutes via launchd (com.valleypawn.preston-watch). Purpose: make Preston feel
answered within minutes even though the Cowork task that does the actual work
(preston-interactive-assistant) can only be dispatched on its cron and may queue behind the
3-slot dispatcher.

What it does each pass:
  1. Reads ~/preston_claude_last_ts.txt (the Cowork task's dedupe cutoff = last message it handled).
  2. Pulls the last 20 messages from C0BGXSTT4TY as the VP OPS ENGINE bot.
  3. Any Preston (U03BWMEM9GR) message newer than the cutoff is PENDING.
  4. First time a pending burst is seen -> one short plain-language ack in-channel.
     (One ack per burst: further messages inside the same pending window are not re-acked.)
  5. If the OLDEST pending message is older than ESCALATE_MIN and we haven't said so yet ->
     one plain DM to Joshua. Never technical. Once per message.
  6. Writes ~/preston_claude_pending.json for the Cowork task / humans to inspect.

Never touches the dedupe file. Never does the work. Additive to the Cowork task.
State: ~/.preston_watch_state.json. Log: ~/Library/Logs/valleypawn/preston-watch.log
"""
import json, os, subprocess, getpass, urllib.request, datetime, sys

HOME = os.path.expanduser('~')
CHANNEL = 'C0BGXSTT4TY'
PRESTON = 'U03BWMEM9GR'
JOSHUA = 'U03BB52MDSA'
CUTOFF_FILE = os.path.join(HOME, 'preston_claude_last_ts.txt')
STATE_FILE = os.path.join(HOME, '.preston_watch_state.json')
PENDING_FILE = os.path.join(HOME, 'preston_claude_pending.json')
LOG = os.path.join(HOME, 'Library/Logs/valleypawn/preston-watch.log')
KEYCHAIN_SERVICE = 'vp-ops-slack-bot-token'
ESCALATE_MIN = 60          # minutes a request may sit before Joshua hears about it
ACTIVE_HOURS = (7, 22)     # local; outside this window the ack wording changes and no escalation
DRY = '--dry-run' in sys.argv

ACK_TEXT = 'Got it, Preston — on it. I will post back here as soon as it is done.'
ACK_TEXT_OFFHOURS = 'Got it, Preston — I will pick this up first thing at 7 AM and post back here.'


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg
    with open(LOG, 'a') as f:
        f.write(line + '\n')
    print(line)


def get_token():
    try:
        r = subprocess.run(['security', 'find-generic-password', '-s', KEYCHAIN_SERVICE,
                            '-a', getpass.getuser(), '-w'], capture_output=True, text=True, timeout=10)
        t = r.stdout.strip()
        if t.startswith('xoxb-'):
            return t
    except Exception:
        pass
    t = os.environ.get('SLACK_BOT_TOKEN', '').strip()
    return t if t.startswith('xoxb-') else None


def slack(token, method, payload=None, get=False):
    if get:
        q = urllib.parse.urlencode(payload or {})
        req = urllib.request.Request('https://slack.com/api/' + method + '?' + q,
                                     headers={'Authorization': 'Bearer ' + token})
    else:
        req = urllib.request.Request('https://slack.com/api/' + method,
                                     data=json.dumps(payload or {}).encode(),
                                     headers={'Authorization': 'Bearer ' + token,
                                              'Content-Type': 'application/json; charset=utf-8'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


import urllib.parse


def load_json(p, default):
    try:
        return json.load(open(p))
    except Exception:
        return default


def main():
    token = get_token()
    if not token:
        log('ERROR no slack token'); return 1
    try:
        cutoff = float(open(CUTOFF_FILE).read().strip())
    except Exception:
        cutoff = 0.0
    state = load_json(STATE_FILE, {'acked': {}, 'escalated': {}})
    hist = slack(token, 'conversations.history', {'channel': CHANNEL, 'limit': 20}, get=True)
    if not hist.get('ok'):
        log('ERROR history ' + str(hist.get('error'))); return 1
    msgs = hist.get('messages', [])
    pending = [m for m in msgs if m.get('user') == PRESTON and not m.get('subtype')
               and float(m['ts']) > cutoff]
    pending.sort(key=lambda m: float(m['ts']))
    now = datetime.datetime.now()
    active = ACTIVE_HOURS[0] <= now.hour < ACTIVE_HOURS[1]

    # prune state entries older than the cutoff (already handled)
    for k in ('acked', 'escalated'):
        state[k] = {ts: v for ts, v in state.get(k, {}).items() if float(ts) > cutoff}

    json.dump({'checked': now.isoformat(timespec='seconds'), 'cutoff': cutoff,
               'pending': [{'ts': m['ts'], 'text': (m.get('text') or '')[:200]} for m in pending]},
              open(PENDING_FILE, 'w'), indent=1)

    if not pending:
        json.dump(state, open(STATE_FILE, 'w'))
        log('ok no pending'); return 0

    # ---- ack: one per burst. A burst = pending messages none of which is acked yet.
    unacked = [m for m in pending if m['ts'] not in state['acked']]
    if unacked and not any(m['ts'] in state['acked'] for m in pending):
        # Skip the ack if a Claude/Joshua reply already landed after Preston's newest message
        newest_ts = float(pending[-1]['ts'])
        replied = any(m.get('user') == JOSHUA and float(m['ts']) > newest_ts for m in msgs)
        if not replied:
            text = ACK_TEXT if active else ACK_TEXT_OFFHOURS
            if DRY:
                log('[dry] would ack: ' + text)
            else:
                r = slack(token, 'chat.postMessage', {'channel': CHANNEL, 'text': text})
                log('ack ' + ('sent' if r.get('ok') else 'FAILED ' + str(r.get('error'))))
        else:
            log('ack skipped (already replied)')
    for m in unacked:
        state['acked'][m['ts']] = now.isoformat(timespec='seconds')

    # ---- escalation: oldest pending older than ESCALATE_MIN, active hours only, once per msg
    oldest = pending[0]
    age_min = (now - datetime.datetime.fromtimestamp(float(oldest['ts']))).total_seconds() / 60
    if active and age_min >= ESCALATE_MIN and oldest['ts'] not in state['escalated']:
        when = datetime.datetime.fromtimestamp(float(oldest['ts'])).strftime('%-I:%M %p')
        text = ('Preston asked for something in his channel at ' + when +
                ' and it has not been picked up yet. Nothing needed from you unless it is urgent — flagging so you know.')
        if DRY:
            log('[dry] would escalate: ' + text)
        else:
            op = slack(token, 'conversations.open', {'users': JOSHUA})
            if op.get('ok'):
                r = slack(token, 'chat.postMessage', {'channel': op['channel']['id'], 'text': text})
                log('escalation ' + ('sent' if r.get('ok') else 'FAILED ' + str(r.get('error'))))
        state['escalated'][oldest['ts']] = now.isoformat(timespec='seconds')

    json.dump(state, open(STATE_FILE, 'w'))
    log('ok pending=%d oldest_age_min=%.0f' % (len(pending), age_min))
    return 0


if __name__ == '__main__':
    sys.exit(main())
