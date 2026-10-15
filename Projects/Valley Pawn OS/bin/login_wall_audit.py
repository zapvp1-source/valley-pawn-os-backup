#!/usr/bin/env python3
"""login_wall_audit.py — READ-ONLY. Lists every scheduled task (enabled or not) whose SKILL.md drives a
web site that needs a signed-in browser session, so each one can be moved to an API or retired.
Writes fleet/LOGIN_WALL_AUDIT.json. Built 2026-10-14 (LOGINS project)."""
import glob, json, os, re, collections
HOME = os.path.expanduser("~")
SCHED = os.path.join(HOME, "Documents/Claude/Scheduled")
OUT = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/LOGIN_WALL_AUDIT.json")
REG = sorted(glob.glob(os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")), key=os.path.getmtime)
SITES = {
 'gusto': r'app\.gusto\.com', 'zoom-web': r'zoom\.us/(myhome|signin|pbx|profile|account)|zoom\.us/[a-z]', 'northwest': r'northwestregisteredagent',
 'google-home': r'home\.google\.com', 'google-web(jdavis)': r'mymaps|maps\.google\.com/maps/d|gemini\.google|analytics\.google\.com|search\.google\.com/search-console|business\.google\.com',
 'bing-places': r'bingplaces', 'cloud-cover': r'cloud ?cover|pandora', 'chekkit-web': r'app\.chekkit|chekkit\.io', 'guesty-web': r'app\.guesty',
 'retail-brilliance': r'retailbrilliance', 'talentlms-web': r'talentlms\.com', 'indeed': r'employers\.indeed|indeed\.com',
 't-mobile': r't-mobile\.com|tmobile', 'amazon': r'amazon\.com', 'ebay-web': r'ebay\.com/(sh|sl|mys|ws)', 'brightlocal': r'brightlocal',
 'apple-business': r'businessconnect\.apple', 'yelp-biz': r'biz\.yelp', 'meta-web': r'business\.facebook|facebook\.com', 'publer-web': r'app\.publer',
 'canva-web': r'canva\.com', 'brevo-web': r'app\.brevo', 'qbo-web': r'qbo\.intuit|app\.qbo', 'airbnb': r'airbnb\.com', 'vrbo': r'vrbo\.com',
 'gunbroker': r'gunbroker', 'leadsonline': r'leadsonline', 'atf': r'fflezcheck|atf\.gov', 'vsp': r'ereceivables|vsp\.virginia', 'wells-fargo': r'wellsfargo',
 'bluedog': r'bluedogpayments', 'slack-web': r'app\.slack\.com|api\.slack\.com/apps', 'controlio': r'controlio', 'mobilepawn': r'mobilepawn',
}
BROWSER = re.compile(r"claude-in-chrome|Claude_Browser|claude in chrome|browser pane|navigate", re.I)
reg = {}
if REG:
    for t in json.load(open(REG[-1])).get('scheduledTasks', []):
        reg[t.get('id')] = t
rows = []
for p in sorted(glob.glob(os.path.join(SCHED, '*/SKILL.md'))):
    tid = os.path.basename(os.path.dirname(p))
    try: s = open(p, errors='replace').read()
    except Exception as e: continue
    if not BROWSER.search(s): continue
    hits = sorted(k for k, rx in SITES.items() if re.search(rx, s, re.I))
    if not hits: continue
    t = reg.get(tid, {})
    retired = bool(re.search(r'^\s*(RETIRED|This task is retired)', s[:600], re.I | re.M))
    rows.append({'task': tid, 'enabled': bool(t.get('enabled')), 'cron': t.get('cronExpression') or t.get('schedule'),
                 'sites': hits, 'retired_stub': retired, 'lines': s.count('\n')})
by = collections.defaultdict(list)
for r in rows:
    if r['enabled'] and not r['retired_stub']:
        for s in r['sites']: by[s].append(r['task'])
json.dump({'registry': REG[-1] if REG else None, 'tasks': rows, 'enabled_by_site': by}, open(OUT, 'w'), indent=1)
print('tasks with browser+login sites:', len(rows), 'enabled:', sum(1 for r in rows if r['enabled'] and not r['retired_stub']))
for s, ts in sorted(by.items(), key=lambda x: -len(x[1])): print(f'{s:22} {len(ts):3}  ' + ', '.join(ts))
