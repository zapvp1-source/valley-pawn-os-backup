#!/usr/bin/env python3
"""Phase 0.1 (SCHEDULED_TASK_RELIABILITY_PLAN.md): repair malformed frontmatter so the
`model:` pin is INSIDE the first `---` block (the only place the app reads it), and remove the
stray duplicate frontmatter fragment that follows it. Backup: SKILL.md.bak-modelpin-20260904
(only taken once; a second run does not overwrite the original backup)."""
import os, re, shutil

SCHED = os.path.expanduser('~/Documents/Claude/Scheduled')
TASKS = {
    'document-photos-index-refresh': 'claude-sonnet-5',
    'mail-brief-reply-executor': 'claude-sonnet-5',
    'preston-claude-evening-check': 'claude-sonnet-5',
    'vp-community-weekly': 'claude-sonnet-5',
    'vp-deal-reels-weekly': 'claude-sonnet-5',
    'vp-engagement-weekly': 'claude-sonnet-5',
    'vp-staff-video-chase': 'claude-sonnet-5',
}
STAMP = 'bak-modelpin-20260904'
FM_KEY = re.compile(r'^(name|description|model):')

def fix(tid, default_model):
    p = os.path.join(SCHED, tid, 'SKILL.md')
    s = open(p, encoding='utf-8').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    lines = s.split(nl)
    if lines[0].strip() != '---':
        return f'{tid}: SKIP (no leading ---)'
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if end is None:
        return f'{tid}: SKIP (unterminated frontmatter)'
    fm = [l for l in lines[1:end] if not re.match(r'^model:', l)]
    model = next((l.split(':',1)[1].strip() for l in lines[1:end] if re.match(r'^model:\s*\S', l)), None)
    rest = lines[end+1:]
    # strip stray fragment: blank lines, bare model:/name:/description: lines, and a
    # --- ... --- block made only of frontmatter keys / blanks, all within the first 12 lines
    i = 0
    removed = []
    while i < len(rest) and i < 12:
        l = rest[i]
        if l.strip() == '':
            i += 1; continue
        if FM_KEY.match(l):
            if l.startswith('model:') and model is None:
                model = l.split(':',1)[1].strip()
            removed.append(l); i += 1; continue
        if l.strip() == '---':
            j = next((k for k in range(i+1, min(len(rest), i+12)) if rest[k].strip() == '---'), None)
            if j is not None and all(rest[k].strip() == '' or FM_KEY.match(rest[k]) for k in range(i+1, j)):
                for k in range(i+1, j):
                    if rest[k].startswith('model:') and model is None:
                        model = rest[k].split(':',1)[1].strip()
                removed.extend(rest[i:j+1]); i = j+1; continue
        break
    rest = rest[i:]
    model = model or default_model
    if not os.path.exists(p + '.' + STAMP):
        shutil.copy2(p, p + '.' + STAMP)
    new = ['---'] + fm + [f'model: {model}', '---'] + rest
    open(p, 'w', encoding='utf-8').write(nl.join(new))
    return f'{tid}: model={model}; removed {len(removed)} stray line(s)'

if __name__ == '__main__':
    for t, m in TASKS.items():
        print(fix(t, m))
