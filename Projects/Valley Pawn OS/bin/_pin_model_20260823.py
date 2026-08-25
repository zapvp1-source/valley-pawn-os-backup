import shutil, re
p='/Users/joshuadavis/Documents/Claude/Scheduled/vp-presence-audit-weekly/SKILL.md'
s=open(p).read()
shutil.copy(p, p+'.bak-precreate')
if re.search(r'^model:', s, re.M):
    print('model line already present')
else:
    # insert into frontmatter (after the description line, before closing ---)
    lines=s.split('\n')
    if lines[0].strip()=='---':
        end=lines.index('---',1)
        lines.insert(end,'model: claude-sonnet-5')
        s='\n'.join(lines)
        open(p,'w').write(s)
        print('model pinned at line',end)
    else:
        print('NO FRONTMATTER — head:', repr(s[:120]))
print('---- frontmatter ----')
print('\n'.join(open(p).read().split('\n')[:8]))
