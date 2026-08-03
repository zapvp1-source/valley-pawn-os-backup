#!/usr/bin/env python3
# Regenerates the LIVE STATE block inside BUSINESS_OS.md and appends detected
# changes to CHANGELOG.md. Hand-written sections of BUSINESS_OS.md are never touched.
# Runs daily. Additive by design: only the delimited block is rewritten.

import json, os, re, glob, datetime, subprocess

OS_DIR = '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS'
BOS = os.path.join(OS_DIR, 'BUSINESS_OS.md')
CHANGELOG = os.path.join(OS_DIR, 'CHANGELOG.md')
SNAP = os.path.join(OS_DIR, '.live_state_snapshot.json')
SCHED = '/Users/joshuadavis/Documents/Claude/Scheduled'
PROJ = '/Users/joshuadavis/Documents/Claude/Projects'
REGGLOB = os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json')
BEGIN = '<!-- LIVE-STATE:BEGIN - machine generated, do not hand-edit -->'
END = '<!-- LIVE-STATE:END -->'
TODAY = datetime.date.today().isoformat()


def load_registry():
    files = sorted(glob.glob(REGGLOB), key=os.path.getmtime, reverse=True)
    if not files:
        return [], {}
    d = json.load(open(files[0]))
    return d.get('scheduledTasks', []), d.get('recordedSkips', {})


def launch_agents():
    out = []
    for p in sorted(glob.glob(os.path.expanduser('~/Library/LaunchAgents/*.plist'))):
        n = os.path.basename(p)
        if 'valleypawn' in n.lower() or 'vpops' in n.lower():
            out.append((n, 'installed'))
    for p in sorted(glob.glob(os.path.expanduser('~/Library/LaunchAgents/*.plist.disabled'))):
        n = os.path.basename(p)
        if 'valleypawn' in n.lower() or 'vpops' in n.lower():
            out.append((n, 'DISABLED'))
    try:
        loaded = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        loaded = ''
    return out, [l.split()[-1] for l in loaded.splitlines() if 'valleypawn' in l.lower()]


def projects():
    rows = []
    for d in sorted(os.listdir(PROJ)):
        fp = os.path.join(PROJ, d)
        if not os.path.isdir(fp) or d.startswith('.'):
            continue
        m = datetime.date.fromtimestamp(os.path.getmtime(fp)).isoformat()
        st = ''
        for cand in ('STATUS.md', 'README.md'):
            c = os.path.join(fp, cand)
            if os.path.isfile(c):
                st = cand
                break
        rows.append((m, d, st))
    return sorted(rows, reverse=True)


def build_state():
    tasks, skips = load_registry()
    agents, loaded = launch_agents()
    folders = [x for x in os.listdir(SCHED)
               if not x.startswith('_') and os.path.isfile(os.path.join(SCHED, x, 'SKILL.md'))]
    reg_ids = {t['id'] for t in tasks}
    enabled = [t for t in tasks if t.get('enabled')]
    return {
        'date': TODAY,
        'task_folders': len(folders),
        'registered': len(tasks),
        'enabled': len(enabled),
        'disabled': len(tasks) - len(enabled),
        'unregistered': sorted(set(folders) - reg_ids),
        'enabled_ids': sorted(t['id'] for t in enabled),
        'skip_total': sum(len(v) for v in skips.values()),
        'agents': agents,
        'agents_loaded': sorted(loaded),
        'projects': projects(),
    }


def render(s):
    L = []
    L.append(BEGIN)
    L.append('')
    L.append('# LIVE STATE - auto-refreshed ' + s['date'])
    L.append('')
    L.append('This block is regenerated daily from the machine itself. It is the ONLY')
    L.append('section of this document guaranteed current. If a hand-written section')
    L.append('below disagrees with this block, THIS BLOCK WINS.')
    L.append('')
    L.append('## Scheduled automations')
    L.append('')
    L.append('| Metric | Count |')
    L.append('|---|---|')
    L.append('| Task folders on disk | ' + str(s['task_folders']) + ' |')
    L.append('| Registered with scheduler | ' + str(s['registered']) + ' |')
    L.append('| Enabled (will fire) | ' + str(s['enabled']) + ' |')
    L.append('| Registered but disabled | ' + str(s['disabled']) + ' |')
    L.append('| On disk but never registered | ' + str(len(s['unregistered'])) + ' |')
    L.append('| Recorded skips (usage cap) | ' + str(s['skip_total']) + ' |')
    L.append('')
    L.append('### Enabled tasks')
    L.append('')
    L.append(', '.join('`' + i + '`' for i in s['enabled_ids']) or '_none_')
    L.append('')
    L.append('### On disk but NOT registered (never fire)')
    L.append('')
    L.append(', '.join('`' + i + '`' for i in s['unregistered']) or '_none_')
    L.append('')
    L.append('## Native launchd agents (run without Claude)')
    L.append('')
    if s['agents']:
        L.append('| Agent | File state | Currently loaded |')
        L.append('|---|---|---|')
        for n, st in s['agents']:
            base = n.replace('.disabled', '')
            key = base.replace('.plist', '')
            L.append('| `' + base + '` | ' + st + ' | ' + ('YES' if key in s['agents_loaded'] else 'no') + ' |')
    else:
        L.append('_none installed_')
    L.append('')
    L.append('## Project folders by last activity')
    L.append('')
    L.append('| Last touched | Project | Status file |')
    L.append('|---|---|---|')
    for m, d, st in s['projects'][:40]:
        L.append('| ' + m + ' | ' + d + ' | ' + (st or '-') + ' |')
    L.append('')
    L.append(END)
    return chr(10).join(L)


def diff(old, new):
    if not old:
        return ['Live-state tracking initialised.']
    out = []
    for k, label in (('enabled', 'enabled scheduled tasks'),
                     ('registered', 'registered scheduled tasks'),
                     ('task_folders', 'task folders on disk')):
        if old.get(k) != new.get(k):
            out.append(label.capitalize() + ': ' + str(old.get(k)) + ' -> ' + str(new.get(k)))
    a, b = set(old.get('enabled_ids', [])), set(new.get('enabled_ids', []))
    for t in sorted(b - a):
        out.append('ENABLED: ' + t)
    for t in sorted(a - b):
        out.append('DISABLED: ' + t)
    oa = {n for n, _ in old.get('agents', [])}
    nb = {n for n, _ in new.get('agents', [])}
    for n in sorted(nb - oa):
        out.append('Native agent appeared: ' + n)
    for n in sorted(oa - nb):
        out.append('Native agent removed: ' + n)
    ol, nl = set(old.get('agents_loaded', [])), set(new.get('agents_loaded', []))
    for n in sorted(nl - ol):
        out.append('Native agent LOADED: ' + n)
    for n in sorted(ol - nl):
        out.append('Native agent STOOD DOWN: ' + n)
    return out


def main():
    new = build_state()
    old = json.load(open(SNAP)) if os.path.exists(SNAP) else None

    block = render(new)
    if os.path.exists(BOS):
        txt = open(BOS, encoding='utf-8', errors='ignore').read()
    else:
        txt = '# Valley Pawn Business OS' + chr(10)
    if BEGIN in txt and END in txt:
        pre = txt.split(BEGIN)[0]
        post = txt.split(END, 1)[1]
        txt = pre + block + post
    else:
        lines = txt.split(chr(10))
        insert_at = 1 if lines and lines[0].startswith('#') else 0
        txt = chr(10).join(lines[:insert_at]) + chr(10) + chr(10) + block + chr(10) + chr(10) + chr(10).join(lines[insert_at:])
    open(BOS, 'w', encoding='utf-8').write(txt)

    changes = diff(old, new)
    if changes:
        entry = ['## ' + TODAY, '']
        for c in changes:
            entry.append('- ' + c)
        entry.append('')
        head = '# Valley Pawn - Enterprise Changelog' + chr(10) + chr(10) + 'Newest first. Material changes to the business operating system. Read this BEFORE any build, fix or diagnosis.' + chr(10) + chr(10)
        existing = ''
        if os.path.exists(CHANGELOG):
            existing = open(CHANGELOG, encoding='utf-8', errors='ignore').read()
            if existing.startswith('#'):
                parts = existing.split(chr(10) + chr(10), 2)
                existing = parts[2] if len(parts) > 2 else ''
        open(CHANGELOG, 'w', encoding='utf-8').write(head + chr(10).join(entry) + chr(10) + existing)

    json.dump(new, open(SNAP, 'w'), indent=1)
    print('BUSINESS_OS.md live-state refreshed for ' + TODAY)
    print('changes detected: ' + str(len(changes)))
    for c in changes:
        print('  - ' + c)


if __name__ == '__main__':
    main()
