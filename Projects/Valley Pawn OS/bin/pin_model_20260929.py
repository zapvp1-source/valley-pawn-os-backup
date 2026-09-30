#!/usr/bin/env python3
"""Pin model: claude-sonnet-5 into the frontmatter of monthly-mobilepawn-participation + monthly-gift-card-store-credit. Idempotent, backs up first. (2026-09-29)"""
import os, shutil
S = os.path.expanduser('~/Documents/Claude/Scheduled')
for tid in ('monthly-mobilepawn-participation', 'monthly-gift-card-store-credit'):
    p = os.path.join(S, tid, 'SKILL.md')
    if not os.path.isfile(p):
        print(tid, 'MISSING'); continue
    s = open(p, encoding='utf-8').read()
    if not s.startswith('---\n'):
        print(tid, 'NO FRONTMATTER — left untouched'); continue
    end = s.index('\n---', 4)
    fm = s[4:end]
    if any(l.startswith('model:') for l in fm.split('\n')):
        print(tid, 'already pinned:', [l for l in fm.split('\n') if l.startswith('model:')][0]); continue
    b = p + '.bak-modelpin-20260929'
    if not os.path.exists(b): shutil.copy2(p, b)
    s = '---\n' + fm + '\nmodel: claude-sonnet-5' + s[end:]
    open(p, 'w', encoding='utf-8').write(s)
    chk = open(p, encoding='utf-8').read()
    print(tid, 'PINNED' if 'model: claude-sonnet-5' in chk[:chk.index('\n---', 4)] else 'VERIFY FAILED')
