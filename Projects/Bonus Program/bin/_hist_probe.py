import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bonus_engine as B
ctx = B.Ctx(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
            '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction', '2026-08')
h = B.load_history(ctx)
for m in sorted(h):
    print(m, {s: (h[m][s]['net_revenue'] if s in h[m] else None) for s in B.STORES})
