#!/usr/bin/env python3
"""
INCIDENT REMEDIATION 2026-08-22.

Cause: secure_creds_sweep.py verified each rewritten script by exec()ing it. Those scripts are
operational, not importable - module-level code ran and made LIVE eBay revisions.

Step 1 here: restore every script the sweep rewrote from its .bak-2026-08-22 backup, EXCEPT
ebay_weekly_rankings.py, whose separate (correct, verified) secrets migration must be kept.
Then compile-check every restored file. No exec() this time.
"""
import os, glob, shutil, stat, py_compile, sys

HOME = os.path.expanduser('~')
KEEP = {'ebay_weekly_rankings.py'}  # correctly migrated by secure_creds.py, do not roll back

baks = sorted(glob.glob(os.path.join(HOME, '*.bak-2026-08-22')))
restored, kept, bad = [], [], []
for bak in baks:
    orig = bak[:-len('.bak-2026-08-22')]
    name = os.path.basename(orig)
    if name in KEEP:
        kept.append(name)
        continue
    shutil.copy2(bak, orig)
    try:
        py_compile.compile(orig, doraise=True)
        os.chmod(orig, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        restored.append(name)
    except Exception as e:
        bad.append((name, str(e)[:120]))

print('RESTORED (%d):' % len(restored))
for n in restored:
    print('   ', n)
print('KEPT MIGRATED (not rolled back):', kept)
if bad:
    print('COMPILE FAILURES:')
    for n, e in bad:
        print('   ', n, e)

# confirm the 4 launchd-critical scripts still resolve creds WITHOUT exec'ing them
print('\nstatic check of launchd-critical scripts:')
for n in ['ebay_daily_listings.py', 'ebay_efficiency_weekly.py', 'ebay_markdown_engine.py',
          'ebay_weekly_rankings.py']:
    p = os.path.join(HOME, n)
    src = open(p).read()
    has_creds = ('APP_ID' in src) or ('_VP_APP' in src) or ('APP=' in src) or ('APP =' in src)
    ok_compile = True
    try:
        py_compile.compile(p, doraise=True)
    except Exception as e:
        ok_compile = False
    print('   %-30s compiles=%s creds_ref=%s  bytes=%d' % (n, ok_compile, has_creds, len(src)))
