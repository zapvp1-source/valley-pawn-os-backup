import os, json, re

base = os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_lodestar')
man = json.load(open(os.path.join(base, '_manifest.json')))

found = []
for m in man:
    p = open(os.path.join(base, 'ldr_%04d.txt' % m['i'])).read(400)
    mm = re.search(r'PATH: (.+)', p)
    if not mm:
        continue
    path = mm.group(1).strip()
    msgdir = os.path.dirname(path)                 # .../Messages
    parent = os.path.dirname(msgdir)               # .../<n>
    msgid = os.path.basename(path).split('.')[0]
    adir = os.path.join(parent, 'Attachments', msgid)
    if os.path.isdir(adir):
        files = []
        for root, dirs, fs in os.walk(adir):
            for f in fs:
                fp = os.path.join(root, f)
                files.append({'f': f, 'p': fp, 'size': os.path.getsize(fp)})
        if files:
            found.append({'i': m['i'], 'subject': m['subject'], 'ts': m['ts'], 'files': files})

out = os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_lodestar_attachments.json')
json.dump(found, open(out, 'w'), indent=1)

exts = {}
for e in found:
    for f in e['files']:
        ext = os.path.splitext(f['f'])[1].lower()
        exts[ext] = exts.get(ext, 0) + 1
print('emails with attachments:', len(found))
print('ext counts:', exts)
