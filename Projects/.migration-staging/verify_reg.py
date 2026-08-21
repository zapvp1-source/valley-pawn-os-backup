import json,os,time
p=os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json')
NEW=['precious-metals-settlement-handler','quarterly-capex-sweep','bravo-preflight-relaunch','monthly-ebay-ratings-sweep','hiring-inbox-watch','monthly-scrap-rankings','vp-ai-visibility-autofix','vp-ai-search-autofix']
d=json.load(open(p))
ids={t['id'] for t in d['scheduledTasks']}
print('mtime:',time.ctime(os.path.getmtime(p)))
print('count:',len(d['scheduledTasks']))
print('new present:',sum(1 for n in NEW if n in ids),'/',len(NEW))
print('missing:',[n for n in NEW if n not in ids])
