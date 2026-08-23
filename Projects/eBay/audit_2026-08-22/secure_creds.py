#!/usr/bin/env python3
"""
Move the eBay secrets out of ~/ebay_weekly_rankings.py into ~/.vp_secrets/ (2026-08-22).

ADDITIVE / interface-preserving: after this runs, ebay_weekly_rankings.py still defines
SLACK_WEBHOOK, APP_ID, DEV_ID, CERT_ID and STORES at module level with identical values, so all
~30 scripts that `exec()` it (and the 4 launchd agents) keep working unchanged. Only the *source*
of those values moves.

Backs up the original to ~/ebay_weekly_rankings.py.bak-2026-08-22 before touching anything.
"""
import os
import re
import shutil
import stat

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
SEC_DIR = os.path.join(HOME, '.vp_secrets')
SEC_FILE = os.path.join(SEC_DIR, 'ebay_store_tokens.py')
BAK = SRC + '.bak-2026-08-22'

text = open(SRC).read()

if 'vp_secrets' in text and 'ebay_store_tokens' in text:
    print('ALREADY MIGRATED - nothing to do')
    raise SystemExit(0)

lines = text.split('\n')

# --- locate the literal blocks ---
webhook = None
app = dev = cert = None
store_start = store_end = None
webhook_idx = None
idx_app = idx_dev = idx_cert = None
for i, ln in enumerate(lines):
    if ln.startswith('SLACK_WEBHOOK'):
        webhook = ln.split('=', 1)[1].strip().strip('"').strip("'")
        webhook_idx = i
    elif ln.startswith('APP_ID'):
        app = ln.split('=', 1)[1].strip().strip('"').strip("'")
        idx_app = i
    elif ln.startswith('DEV_ID'):
        dev = ln.split('=', 1)[1].strip().strip('"').strip("'")
        idx_dev = i
    elif ln.startswith('CERT_ID'):
        cert = ln.split('=', 1)[1].strip().strip('"').strip("'")
        idx_cert = i
    elif ln.startswith('STORES = ['):
        store_start = i
    elif store_start is not None and store_end is None and ln.strip() == ']':
        store_end = i

assert None not in (webhook, app, dev, cert, store_start, store_end), 'could not locate all blocks'
store_block = '\n'.join(lines[store_start:store_end + 1])
print('located: webhook line %d, creds %d-%d, STORES %d-%d' % (webhook_idx, idx_app, idx_cert, store_start, store_end))

# --- write the secrets file ---
os.makedirs(SEC_DIR, exist_ok=True)
sec = ('"""Valley Pawn eBay secrets - single source of truth. Created 2026-08-22.\n'
       'Moved here out of ~/ebay_weekly_rankings.py, which was world-executable and plaintext.\n'
       'Loaded by ebay_weekly_rankings.py, which every other eBay script exec()s for STORES.\n'
       'NEVER commit this file or copy these values anywhere else.\n"""\n\n'
       'SLACK_WEBHOOK = "%s"\n\n'
       'APP_ID  = "%s"\n'
       'DEV_ID  = "%s"\n'
       'CERT_ID = "%s"\n\n'
       '%s\n') % (webhook, app, dev, cert, store_block)
open(SEC_FILE, 'w').write(sec)
os.chmod(SEC_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600
print('wrote', SEC_FILE, 'mode 600')

# --- back up original ---
shutil.copy2(SRC, BAK)
os.chmod(BAK, stat.S_IRUSR | stat.S_IWUSR)
print('backed up ->', BAK)

# --- rewrite the source to load from the secrets file ---
loader = '''# -- secrets loaded from ~/.vp_secrets/ebay_store_tokens.py (moved 2026-08-22) --
# Interface unchanged: SLACK_WEBHOOK / APP_ID / DEV_ID / CERT_ID / STORES are still defined here
# at module level, so every script that exec()s this file keeps working exactly as before.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_store_tokens import SLACK_WEBHOOK, APP_ID, DEV_ID, CERT_ID, STORES  # noqa: F401
'''

new = lines[:webhook_idx] + [loader] + lines[store_end + 1:]
# drop the now-orphaned comment banners for the removed blocks
out = []
for ln in new:
    if ln.strip().startswith('#') and ('EBAY APP CREDENTIALS' in ln or 'STORE TOKENS' in ln or ln.strip().startswith('# ── SLACK')):
        continue
    out.append(ln)

open(SRC, 'w').write('\n'.join(out))
os.chmod(SRC, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # 700, was 701 (world-executable)
print('rewrote', SRC, 'mode 700')

# --- verify the interface still resolves ---
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
ok = (ns.get('APP_ID') == app and ns.get('DEV_ID') == dev and ns.get('CERT_ID') == cert
      and ns.get('SLACK_WEBHOOK') == webhook and len(ns.get('STORES', [])) == 5)
print('VERIFY interface intact:', ok, '| stores:', [s['name'] for s in ns.get('STORES', [])])
if not ok:
    shutil.copy2(BAK, SRC)
    print('!! VERIFY FAILED - original restored from backup')
    raise SystemExit(1)
print('grep for leftover literals in source:')
resid = [l for l in open(SRC).read().split('\n') if 'hooks.slack.com' in l or 'PRD-' in l or 'v^1.1#' in l]
print('  residual secret lines:', len(resid))
print('DONE')
