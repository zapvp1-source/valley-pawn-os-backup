#!/usr/bin/env python3
"""Deck stats (read-only): categorize the AI text responder's October first-text replies by the reason it logged."""
import json,glob,re,collections,sys
D=sys.argv[1]
rules=[('Other (thanks, jobs, lost item, app sign-in, layaway, rental)',r'job|^greeting'),('Firearms',r'firearm|ffl|gun|crossbow|scope|barnett|muzzle'),
 ('Loan payment / extension / payoff',r'loan (payment|extension|due|balance|status|hold)|payoff|past-due|late pawn|payment|extension|vague loan'),
 ('Gold, silver, jewelry, coins, watches',r'gold|silver|jewel|ring|pendant|necklace|coin|watch|chain'),
 ('Hours / location / open?',r'hours|store open question|address|greeting'),
 ('New pawn loan on an item',r'pawn|loan (inquiry|request)|bike loan|laptop loan'),
 ('Selling an item / what will you give me',r'sell|offer|quote|photos|selling|item details|need details|needs details|collectible|lot'),
 ('Do you have X / price of an item',r'item inquiry|stock|inventory|price|guitar|unsure if taken|in-store item|not on (our )?list|not listed|not in listed|lists|trailer|tool|radio|stereo|boots|records|vehicle|sneakers|cards|item sale|item not|item inquiry|inquiry'),
]
C=collections.Counter(); M=collections.defaultdict(list); n=0
for f in sorted(glob.glob(D+'/events-2026-10-*.jsonl')):
    for l in open(f):
        e=json.loads(l)
        if e['action']!='reply': continue
        n+=1; r=e['reason'].lower(); cat='Other (thanks, jobs, lost item, app sign-in, layaway, rental)'
        for c,p in rules:
            if re.search(p,r): cat=c; break
        C[cat]+=1; M[cat].append(e['reason'])
print('AI first-text replies Oct:',n)
for c,v in C.most_common(): print(f"{v:4d} {100*v/n:5.1f}% {c}")
if '-v' in sys.argv:
    for c in M: print('\n##',c); print('; '.join(M[c]))
