#!/usr/bin/env python3
"""preston_local_runner.py (2026-10-16, Joshua-approved) — answers Preston's requests ON THE MAC within ~2 minutes.

Why: the cloud "Preston assistant" task can run at most hourly, and the claude.ai task page offers no start key,
so preston_watch could only ack. This runner uses the Claude Code CLI installed at ~/.local/bin/claude
(signed in to Joshua's account) to do the same job locally.

Spawned detached by bin/preston_watch_run.sh after every watcher pass (every ~2 min). Reads the watcher's
open_requests from fleet/state/preston_assistant/watch_status.json. One run at a time (mkdir lock).
Per request: start at most 3 times, 20 min apart. Silent if the CLI is not signed in.
Prompt: fleet/state/preston_assistant/prompt.md. Log: ~/Library/Logs/valleypawn/preston-local-runner.log
"""
import datetime, json, os, subprocess, sys, time

HOME = os.path.expanduser('~')
PROJ = os.path.join(HOME, 'Documents/Claude/Projects')
OS_DIR = os.path.join(PROJ, 'Valley Pawn OS')
SD = os.path.join(OS_DIR, 'fleet/state/preston_assistant')
WATCH = os.path.join(SD, 'watch_status.json')
PROMPT = os.path.join(SD, 'prompt.md')
STATUS = os.path.join(SD, 'local_runner_status.json')
STATE = os.path.join(HOME, '.preston_local_runner_state.json')
LOCK = os.path.join(HOME, '.preston_local_runner.lock')
LOG = os.path.join(HOME, 'Library/Logs/valleypawn/preston-local-runner.log')
CLAUDE = os.path.join(HOME, '.local/bin/claude')
REFIRE_MIN, MAX_STARTS, RUN_TIMEOUT_S = 20, 3, 1500


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
            return r.returncode == 0 and 'not logged in' not in out and '"loggedin": false' not in out
    except Exception:
        return False


def main():
    # lock (stale after 30 min)
    try:
        if os.path.isdir(LOCK) and time.time() - os.path.getmtime(LOCK) > 1800:
            os.rmdir(LOCK)
        os.mkdir(LOCK)
    except Exception:
        return 0
    try:
        status = {'checked': datetime.datetime.now().isoformat(timespec='seconds')}
        if not os.path.exists(CLAUDE) or not signed_in():
            status['state'] = 'cli-not-signed-in'
            sj(STATUS, status)
            return 0
        open_reqs = lj(WATCH, {}).get('open_requests', [])
        st = lj(STATE, {})
        now = time.time()
        pick = None
        for r in sorted(open_reqs, key=lambda x: float(x['ts'])):
            starts = st.get(r['ts'], [])
            if len(starts) >= MAX_STARTS:
                continue
            if starts and now - starts[-1] < REFIRE_MIN * 60:
                continue
            pick = r
            break
        status['state'] = 'idle'
        status['open'] = len(open_reqs)
        if pick:
            st.setdefault(pick['ts'], []).append(now)
            st = {k: v for k, v in st.items() if now - float(k) < 72 * 3600}
            sj(STATE, st)
            ch = '#preston-claude' if pick['channel'] == 'C0BGXSTT4TY' else '#employee-prospects'
            prompt = open(PROMPT).read() + ('\n\nSTARTED BY THE MAC RUNNER: Preston posted a request in %s (channel %s, ts %s): "%s". '
                                            'Handle this request now, then any other unanswered ones.' % (ch, pick['channel'], pick['ts'], pick.get('text', '')))
            log('start ts=%s attempt=%d' % (pick['ts'], len(st.get(pick['ts'], []))))
            t0 = time.time()
            try:
                r = subprocess.run(['/usr/bin/perl', '-e', 'alarm %d; exec @ARGV' % RUN_TIMEOUT_S, CLAUDE, '-p', prompt,
                                    '--dangerously-skip-permissions', '--output-format', 'text'],
                                   cwd=PROJ, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=RUN_TIMEOUT_S + 60)
                rc, out = r.returncode, (r.stdout or '')[-1500:] + (r.stderr or '')[-500:]
            except Exception as e:
                rc, out = -1, str(e)[:500]
            log('done ts=%s rc=%s secs=%d tail=%s' % (pick['ts'], rc, time.time() - t0, out.replace('\n', ' ')[-600:]))
            status.update({'state': 'ran', 'last_ts': pick['ts'], 'last_rc': rc, 'last_secs': int(time.time() - t0)})
        sj(STATUS, status)
        return 0
    finally:
        try:
            os.rmdir(LOCK)
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(main())
