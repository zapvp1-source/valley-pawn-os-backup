#!/usr/bin/env python3
"""
Sweep the remaining plaintext eBay secrets out of the ~/*.py scripts (2026-08-22).

Replaces literal APP_ID / DEV_ID / CERT_ID / SLACK webhook assignments with loads from
~/.vp_secrets/ebay_store_tokens.py. Store OAuth tokens were already centralised by
secure_creds.py; this handles the app credentials + webhooks that were copy-pasted around.

Safety:
  * every file backed up to <file>.bak-2026-08-22 first
  * after rewrite the file is compiled AND exec'd; if it fails, the backup is restored
  * only literal assignment lines are touched - no logic is modified
  * DRY RUN by default, --apply to write
"""
import os
import re
import shutil
import stat
import sys

HOME = os.path.expanduser('~')
SECRETS = os.path.join(HOME, '.vp_secrets', 'ebay_store_tokens.py')
sys.path.insert(0, os.path.join(HOME, '.vp_secrets'))
from ebay_store_tokens import SLACK_WEBHOOK, APP_ID, DEV_ID, CERT_ID  # noqa

APPLY = '--apply' in sys.argv
STAMP = '.bak-2026-08-22'

LOADER = ('import os as _vos, sys as _vsys\n'
          '_vsys.path.insert(0, _vos.path.expanduser("~/.vp_secrets"))\n'
          'from ebay_store_tokens import SLACK_WEBHOOK as _VP_HOOK, APP_ID as _VP_APP, '
          'DEV_ID as _VP_DEV, CERT_ID as _VP_CERT\n')

# name in file -> secret value
LITERALS = {APP_ID: '_VP_APP', DEV_ID: '_VP_DEV', CERT_ID: '_VP_CERT', SLACK_WEBHOOK: '_VP_HOOK'}

targets = sorted(set(
    [os.path.join(HOME, f) for f in os.listdir(HOME)
     if f.endswith('.py') and (f.startswith('ebay_') or f.startswith('qf_'))]
))

changed, skipped, failed = [], [], []
for path in targets:
    try:
        src = open(path).read()
    except Exception:
        continue
    if not any(lit in src for lit in LITERALS):
        skipped.append((os.path.basename(path), 'no literals'))
        continue

    new = src
    for lit, var in LITERALS.items():
        new = new.replace('"%s"' % lit, var).replace("'%s'" % lit, var)
    if new == src:
        skipped.append((os.path.basename(path), 'no quoted match'))
        continue

    # insert loader after the last top-level import block near the top
    lines = new.split('\n')
    ins = 0
    for i, ln in enumerate(lines[:60]):
        if ln.startswith('import ') or ln.startswith('from '):
            ins = i + 1
    lines.insert(ins, LOADER)
    new = '\n'.join(lines)

    if not APPLY:
        n = sum(src.count('"%s"' % l) + src.count("'%s'" % l) for l in LITERALS)
        changed.append((os.path.basename(path), '%d literal(s) WOULD move' % n))
        continue

    bak = path + STAMP
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        os.chmod(bak, stat.S_IRUSR | stat.S_IWUSR)
    open(path, 'w').write(new)
    # verify
    ok, err = True, ''
    try:
        compile(new, path, 'exec')
        ns = {'__name__': 'notmain'}
        try:
            exec(compile(new, path, 'exec'), ns)
        except SystemExit:
            pass
        if not (ns.get('APP_ID') or ns.get('APP') or ns.get('_VP_APP')):
            ok, err = False, 'creds did not resolve'
    except Exception as e:
        ok, err = False, '%s: %s' % (type(e).__name__, str(e)[:90])
    if ok:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        changed.append((os.path.basename(path), 'migrated + verified'))
    else:
        shutil.copy2(bak, path)
        failed.append((os.path.basename(path), 'RESTORED - ' + err))

print('=== %s ===' % ('APPLIED' if APPLY else 'DRY RUN'))
for n, m in changed:
    print('  CHANGED  %-38s %s' % (n, m))
for n, m in failed:
    print('  FAILED   %-38s %s' % (n, m))
print('  (%d skipped, no literals)' % len(skipped))

# residual scan
resid = []
for path in targets:
    s = open(path).read()
    hits = [l for l in LITERALS if l in s]
    if hits:
        resid.append((os.path.basename(path), len(hits)))
print('\nresidual files still holding literals:', len(resid))
for n, c in resid[:20]:
    print('   ', n, c)
