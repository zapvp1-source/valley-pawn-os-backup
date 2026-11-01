"""Store Conduct Watch — morning report (built 2026-10-31). DMs Joshua the previous business day's verified
moments (worst first) and uploads the clips. Catches up to 3 unreported days, oldest first. Duplicate-guarded
(DM history marker + reports/<date>/reported.json). Posts nothing for an incomplete analysis (logs it instead).
Usage: report.py [--date YYYY-MM-DD] [--render]   (--render prints the message, sends nothing)"""
import datetime as dt, glob, json, os, sys, zoneinfo
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/Documents/Claude/Projects/Valley Pawn OS/bin'))
import vp_slack
TZ = zoneinfo.ZoneInfo('America/New_York')
MAX_CLIPS = 6
SHORT = {'Workstation': 'WS', 'workstation': 'WS', 'camera': '', 'Camera': ''}

def cam_short(store, cam):
    c = cam.replace(store, '').strip()
    for k, v in SHORT.items(): c = c.replace(k, v)
    return ' '.join(c.split()) or cam

def marker(date):
    return 'Camera watch — ' + dt.date.fromisoformat(date).strftime('%a, %b %-d')

def compose(date):
    rep = os.path.join(HERE, 'reports', date)
    eps = json.load(open(os.path.join(rep, 'episodes.json'))); run = json.load(open(os.path.join(rep, 'run.json')))
    eps = [e for e in eps if int(e.get('severity', 1)) >= 2]
    lines = [f"*{marker(date)}*"]
    counts = []
    for store, info in run.get('stores', {}).items():
        n = sum(1 for e in eps if e['store'] == store)
        counts.append(f"{store} {n}")
    lines.append('Moments that need attention: ' + ' · '.join(counts))
    span = []
    for store in run.get('stores', {}):
        ts = []
        for idx in glob.glob(os.path.join(os.path.expanduser('~/.vp-studio/conduct-watch/frames'), store, '*', date, 'index.jsonl')):
            ls = [json.loads(l)['t'] for l in open(idx) if l.strip()]
            if ls: ts += [ls[0], ls[-1]]
        if ts:
            a, b = min(ts), max(ts); fmt = lambda t: dt.datetime.strptime(t, '%H:%M:%S').strftime('%-I:%M %p')
            span.append(f"{store} {fmt(a)}–{fmt(b)}")
    if span: lines.append('Watched: ' + ' · '.join(span))
    unwatched = [f"{s} {cam_short(s, c)}" for s, info in run.get('stores', {}).items() for c, ci in info.get('cams', {}).items() if ci.get('stills', 0) < 30]
    if unwatched: lines.append('No footage from: ' + ', '.join(unwatched) + ' (camera offline or not streaming)')
    if not eps:
        lines.append('Nothing serious on camera.')
        return '\n'.join(lines), []
    ranked = sorted(eps, key=lambda e: (-int(e.get('severity', 2)), e['store'], e['best_s']))
    lines.append('')
    for e in ranked[:12]:
        sev = '• *SERIOUS*' if int(e.get('severity', 2)) >= 3 else '•'
        q = f" (heard: \"{e['quote']}\")" if e.get('quote') else ''
        span = e.get('start', '') + (f"–{e['end']}" if e.get('end') and e.get('end') != e.get('start') else '')
        lines.append(f"{sev} *{e['store']}* {cam_short(e['store'], e['camera'])}, {span} — {e.get('what', '').rstrip('.')}{q}")
    if len(ranked) > 12: lines.append(f"…plus {len(ranked) - 12} more in the report folder.")
    clips = [e['clip'] for e in ranked if e.get('clip') and os.path.exists(e['clip'])][:MAX_CLIPS]
    if clips: lines.append(f"\nClips below ({len(clips)}).")
    return '\n'.join(lines), clips

def pending_dates():
    out = []
    for rep in sorted(glob.glob(os.path.join(HERE, 'reports', '20*'))):
        d = os.path.basename(rep)
        try:
            if (dt.date.today() - dt.date.fromisoformat(d)).days > 4: continue
        except ValueError: continue
        if os.path.exists(os.path.join(rep, 'reported.json')): continue
        try:
            if json.load(open(os.path.join(rep, 'run.json'))).get('complete'): out.append(d)
            else: print(d, 'analysis incomplete — not posting')
        except Exception: print(d, 'no run.json — not posting')
    return out[-3:]

def send(date, render=False):
    text, clips = compose(date)
    if render: print(text); print(clips); return True
    ch = vp_slack.dm_channel(vp_slack.JOSHUA)
    if vp_slack.has(ch, marker(date), 96):
        print(date, 'already in DM — marking reported'); json.dump({'already': True}, open(os.path.join(HERE, 'reports', date, 'reported.json'), 'w')); return True
    vp_slack.post(ch, text)
    up = 0
    for c in clips:
        try: vp_slack.upload(ch, c, os.path.basename(c)); up += 1
        except SystemExit as e: print('upload failed', c, e)
    ok = vp_slack.has(ch, marker(date), 2)   # self-verify (Hardening req. #2)
    json.dump({'posted': dt.datetime.now(TZ).isoformat(timespec='seconds'), 'clips': up, 'verified': ok},
              open(os.path.join(HERE, 'reports', date, 'reported.json'), 'w'))
    print(date, 'posted', 'verified' if ok else 'NOT VERIFIED', 'clips', up)
    return ok

if __name__ == '__main__':
    render = '--render' in sys.argv
    if '--date' in sys.argv: dates = [sys.argv[sys.argv.index('--date') + 1]]
    else: dates = pending_dates()
    if not dates: print('nothing to report')
    ok = all(send(d, render) for d in dates)
    sys.exit(0 if ok else 1)
