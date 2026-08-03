#!/usr/bin/env python3
"""Download full-res photos for all audit candidates."""
import urllib.request, os, time

candidates_pics = {
    '397904240644': ['https://i.ebayimg.com/00/s/MTIwMFg2MjA=/z/IT4AAeSwwtlp9jpf/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg3NTg=/z/Q64AAeSwEeNp9jpf/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg2MzA=/z/mgcAAeSwYi9p9jpg/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg2MDY=/z/KkEAAeSwKuhp9jpg/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFgxMTcw/z/nRYAAeSwnSNp9jpg/$_1.JPG?set_id=2'],
    '397668289749': ['https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/AWIAAeSwA1Jppf4T/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/uCwAAeSwpcpppf4T/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/D2UAAeSwhYxppf4T/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/~icAAeSwIHFppf4U/$_1.JPG?set_id=2'],
    '398147106908': ['https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/vYEAAeSwyJVqTBaU/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/CjAAAeSwSGtqTBaU/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/wOUAAeSwpEhqTBaU/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/CW0AAeSwt-ZqTBaU/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/BroAAeSwCOdqTBaV/$_1.JPG?set_id=2'],
    '388596822601': ['https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/Y7UAAeSwxoRqSrvc/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/quMAAeSwGGJqSrvc/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/jWIAAeSw7spqSrvd/$_1.JPG?set_id=880000500F'],
    '800161061900': ['https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/OUUAAeSwrLtqSrz5/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/tGEAAeSwYclqSrz6/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/qxAAAeSwAnNqSrz6/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/T7EAAeSwhyJqSrz7/$_1.JPG?set_id=880000500F'],
    '800360267687': ['https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/2WYAAeSwrptqWnBe/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/kYAAAeSwms5qWnBe/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/TCIAAeSwUKRqWnBf/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/424AAeSwEbBqWnBf/$_1.JPG?set_id=2'],
    '800055373631': ['https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/ZO4AAeSwYoFqSr1x/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/B3YAAeSwsMJqSr1y/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/-XoAAeSwEBRqSr1z/$_1.JPG?set_id=880000500F'],
    '800406852492': ['https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/JJgAAeSwrBNqZQVm/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/t8EAAeSwvdxqZQVm/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/BLsAAeSw-~pqZQVm/$_1.JPG?set_id=2'],
    '158076113078': ['https://i.ebayimg.com/00/s/NzY1WDEwMjA=/z/BXUAAeSw5lRqUrwC/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/6X4AAeSw0ttqUrwC/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/krEAAeSwAbdqUrwD/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/n~8AAeSw0ZZqUrwD/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/m4gAAeSwlDZqUrwD/$_1.JPG?set_id=2'],
    '157895971112': ['https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/mF4AAeSwEJNqSrqq/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/OTAwWDEyMDA=/z/-3cAAeSwPghqSrqq/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/OTAwWDEyMDA=/z/vG0AAeSw4qlqSrqr/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/phsAAeSw7UVqSrqs/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/OTAwWDEyMDA=/z/WCAAAeSwNlxqSrqs/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/OTAwWDEyMDA=/z/mjAAAeSw3bRqSrqt/$_1.JPG?set_id=880000500F'],
    '157840648182': ['https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/LvcAAeSwt8NqSrr1/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/UGoAAeSwINNqSrr2/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/1y0AAeSwJxVqSrr3/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/nPcAAeSw50hqSrr3/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NzU0WDEwMjA=/z/KMUAAeSw40VqSrr4/$_1.JPG?set_id=880000500F'],
    '157921257295': ['https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/ptAAAeSwRZpqSrsB/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/o8kAAeSw5w9qSrsB/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MzYyWDg1OA==/z/jaYAAeSwejpqSrsC/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MzU1WDg1OA==/z/o8EAAeSwTidqSrsD/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/Q0cAAeSwAr9qSrsD/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NzY1WDEwMjA=/z/kzQAAeSwhnRqSrsE/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/Njg1WDEwMTI=/z/d3cAAeSwN~dqSrsF/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAyMFg3NjU=/z/dFgAAeSw8z5qSrsG/$_1.JPG?set_id=880000500F'],
    '306692304250': ['https://i.ebayimg.com/00/s/OTAwWDEyMDA=/z/1lsAAeSwXWBqSsGr/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/be0AAeSwqYlqSsGs/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/ioQAAeSwxoRqSsGs/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/bbwAAeSwHitqSsGt/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/wQsAAeSwhnRqSsGu/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTIwMFg5MDA=/z/ugEAAeSwFolqSsGv/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/OTAwWDEyMDA=/z/cxoAAeSw779qSsGw/$_1.JPG?set_id=880000500F'],
    '297455886815': ['https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/uJ4AAeSwALdqSr5j/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/rL0AAeSwhs1qSr5k/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/WwUAAeSwMJ5qSr5k/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/WAkAAeSwHitqSr5l/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/HZYAAeSwSVtqSr5m/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/lrgAAeSwupxqSr5n/$_1.JPG?set_id=880000500F'],
    '298226614316': ['https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/ZG0AAeSwmo9qSr9Y/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/uMIAAeSwCOdqSr9Z/$_1.JPG?set_id=880000500F'],
    '307000372642': ['https://i.ebayimg.com/00/s/MTAwMFg3NTA=/z/-I0AAeSwKEZqSr9F/$_1.JPG?set_id=880000500F'],
    '298122752867': ['https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/yosAAeSwSGtqSr9T/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/WnQAAeSwMKdqSr9U/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/SrQAAeSw0TVqSr9U/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/XVkAAeSwrAxqSr9V/$_1.JPG?set_id=880000500F'],
    '298510416155': ['https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/X4MAAeSw5V9qWTjr/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/zaYAAeSwvTxqWTjr/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/PXAAAeSwwrlqWTjr/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/hCsAAeSwAY9qWTjs/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/rPkAAeSwSFFqWTjs/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/SCgAAeSwsIxqWTjs/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/kIcAAeSw0ttqWTjs/$_1.JPG?set_id=2','https://i.ebayimg.com/00/s/NzUwWDEwMDA=/z/6rsAAeSwRTtqWTjs/$_1.JPG?set_id=2'],
    '306888773521': ['https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/e4wAAeSwmppqSr~K/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/khYAAeSwrzFqSr~K/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/wAIAAeSwb~BqSr~L/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/Tp8AAeSwt8NqSr~M/$_1.JPG?set_id=880000500F'],
    '297718886438': ['https://i.ebayimg.com/00/s/NTY3WDEwMDg=/z/8r8AAeSwkSpqSsD1/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/THAAAeSw6rdqSsD2/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/UoIAAeSw~VhqSsD3/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/4G4AAeSwG7dqSsD4/$_1.JPG?set_id=880000500F','https://i.ebayimg.com/00/s/MTAwOFg1Njc=/z/y8UAAeSwyeRqSsD4/$_1.JPG?set_id=880000500F'],
}

outdir = '/Users/joshuadavis/Documents/Claude/Projects/eBay/audit/fullres'
os.makedirs(outdir, exist_ok=True)

total = sum(len(v) for v in candidates_pics.values())
done = 0
for iid, pics in candidates_pics.items():
    for pi, url in enumerate(pics[:8]):
        dest = f'{outdir}/{iid}_{pi}.jpg'
        if os.path.exists(dest):
            done += 1
            continue
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=30).read()
            open(dest, 'wb').write(data)
            done += 1
        except Exception as e:
            print(f'err {iid} p{pi}: {e}')
        time.sleep(0.05)

print(f'done: {done}/{total} files in {outdir}')
