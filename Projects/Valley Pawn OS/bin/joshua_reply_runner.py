#!/usr/bin/env python3
"""joshua_reply_runner.py (2026-11-20) — acts on Joshua's text replies to Slack alerts.

Spawned (detached) by joshua_text_alert.py whenever fleet/state/joshua_text_alert/replies.jsonl has items.
One run at a time (mkdir lock). Each queued reply runs the Claude Code CLI (~/.local/bin/claude, Joshua's account)
with fleet/state/joshua_text_alert/reply_prompt.md + the alert and reply. Up to 3 attempts per reply, 10 min apart.
If the CLI is not signed in: texts Joshua once per reply "Can't — ..." and keeps the item queued so it runs
as soon as the CLI is signed back in.
Log: ~/Library/Logs/valleypawn/joshua-reply-runner.log  Status: fleet/state/joshua_text_alert/runner_status.json
"""
import datetime, json, os, subprocess, sys, time

HOME = os.path.expanduser('~')
PROJ = os.path.join(HOME, 'Documents/Claude/Projects')
OS_DIR = os.path.join(PROJ, 'Valley Pawn OS')
SD = os.path.join(OS_DIR, 'fleet/state/joshua_text_alert')
QUEUE = os.path.join(SD, 'replies.jsonl')
DONE = os.path.join(SD, 'replies_done.jsonl')
PROMPT = os.path.join(SD, 'reply_prompt.md')
STATUS = os.path.join(SD, 'runner_status.json')
STATE = os.path.join(HOME, '.joshua_reply_runner_state.json')
LOCK = os.path.join(HOME, '.joshua_reply_runner.lock')
LOG = os.path.join(HOME, 'Library/Logs/valleypawn/joshua-reply-runner.log')
CLAUDE = os.path.join(HOME, '.local/bin/claude')
SENDER = os.path.join(OS_DIR, 'bin/send_text_verified.py')
TO = '+18049304221'
MAX_TRIES, RETRY_MIN, RUN_TIMEOUT_S = 3, 10, 1500


def log(m):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, 'a') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S ') + m + '\n')


def lj(p, d):
    try:
        return json.load(open(p))
    except Exception:
        return d


def sj(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    json.dump(d, open(tmp, 'w'), indent=1)
    os.replace(tmp, p)


def signed_in():
    try:
        r = subprocess.run([CLAUDE, 'auth', 'status'], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        try:
            return bool(json.loads(r.stdout).get('loggedIn'))
        except Exception:
            out = (r.stdout + r.stderr).lower()
            return r.returncode == 0 and 'not logged in' not in out
    except Exception:
        return False


def text(body):
    r = subprocess.run(['/usr/bin/python3', SENDER, '--to', TO, '--text', body, '--task', 'joshua-reply-runner'],
                       capture_output=True, text=True, timeout=60)
    log('text rc=%s %s' % (r.returncode, body[:100]))


def read_queue():
    items = []
    try:
        for line in open(QUEUE):
            line = line.strip()
            if line:
                items.append(json.loads(line))
    except FileNotFoundError:
        pass
    return items


def write_queue(items):
    if not items:
        try:
            os.remove(QUEUE)
        except FileNotFoundError:
            pass
        return
    tmp = QUEUE + '.tmp'
    with open(tmp, 'w') as f:
        for it in items:
            f.write(json.dumps(it) + '\n')
    os.replace(tmp, QUEUE)


def main():
    try:
        if os.path.isdir(LOCK) and time.time() - os.path.getmtime(LOCK) > 1800:
            os.rmdir(LOCK)
        os.mkdir(LOCK)
    except Exception:
        return 0
    try:
        items = read_queue()
        status = {'checked': datetime.datetime.now().isoformat(timespec='seconds'), 'queued': len(items)}
        if not items:
            status['state'] = 'idle'
            sj(STATUS, status)
            return 0
        st = lj(STATE, {})
        now = time.time()
        if not os.path.exists(CLAUDE) or not signed_in():
            status['state'] = 'cli-not-signed-in'
            for it in items:
                k = str(it['rowid'])
                if not st.get('warned_' + k):
                    text("Can't — the Mac's Claude sign-in expired, so I can't act on your reply yet. It will run as soon as it's signed back in.")
                    st['warned_' + k] = now
            sj(STATE, st)
            sj(STATUS, status)
            return 0
        it = items[0]
        k = str(it['rowid'])
        tries = st.get(k, [])
        if tries and now - tries[-1] < RETRY_MIN * 60:
            status['state'] = 'waiting-retry'
            sj(STATUS, status)
            return 0
        if len(tries) >= MAX_TRIES:
            text("Can't — I tried 3 times to act on your reply \"%s\" and it didn't finish. Please handle it in Slack." % it['reply'][:60])
            with open(DONE, 'a') as f:
                f.write(json.dumps(dict(it, result='gave-up')) + '\n')
            write_queue(items[1:])
            status['state'] = 'gave-up'
            sj(STATUS, status)
            return 0
        tries.append(now)
        st[k] = tries
        sj(STATE, st)
        a = it['alert']
        ctx = ('\n\nALERT HE WAS TEXTED ABOUT:\nchannel: #%s (%s)\nmessage ts: %s\nthread ts (reply here): %s\nposted by: %s (%s)\nmessage: %s\n\n'
               'HIS TEXT REPLY (%s): %s\n\nOther recent alerts (oldest first), in case his reply refers to one of them:\n%s'
               % (a['cname'], a['channel'], a['ts'], a['thread_ts'], a['who'], a.get('user'), a['text'],
                  datetime.datetime.fromtimestamp(it['at']).strftime('%Y-%m-%d %H:%M'), it['reply'],
                  '\n'.join('- #%s %s %s: %s' % (x['cname'], x['ts'], x['who'], x['text'][:200]) for x in it.get('recent_alerts', []))))
        prompt = open(PROMPT).read() + ctx
        log('start rowid=%s attempt=%d reply=%s' % (k, len(tries), it['reply'][:100]))
        t0 = time.time()
        try:
            r = subprocess.run(['/usr/bin/perl', '-e', 'alarm %d; exec @ARGV' % RUN_TIMEOUT_S, CLAUDE, '-p', prompt,
                                '--dangerously-skip-permissions', '--output-format', 'text'],
                               cwd=PROJ, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=RUN_TIMEOUT_S + 60)
            rc, out = r.returncode, (r.stdout or '')[-1500:] + (r.stderr or '')[-500:]
        except Exception as e:
            rc, out = -1, str(e)[:500]
        log('done rowid=%s rc=%s secs=%d tail=%s' % (k, rc, time.time() - t0, out.replace('\n', ' ')[-600:]))
        if rc == 0:
            with open(DONE, 'a') as f:
                f.write(json.dumps(dict(it, result='ok', finished=datetime.datetime.now().isoformat(timespec='seconds'))) + '\n')
            write_queue(read_queue()[1:])
        status.update({'state': 'ran', 'last_rowid': k, 'last_rc': rc, 'last_secs': int(time.time() - t0)})
        sj(STATUS, status)
        return 0
    finally:
        try:
            os.rmdir(LOCK)
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(main())
