# usage: python3 mkpdf.py /abs/brief.html /abs/brief.pdf   (CLOUD session: playwright + chromium + pdfinfo)
# Auto-fit: renders at scale 1.0 and steps down (to 0.80 minimum) until the brief is exactly ONE Letter page.
# Exit 0 = one page; exit 3 = still more than one page at 0.80 (cut content, do not ship).
import sys, subprocess, re
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]
def pages(p):
    o = subprocess.run(['pdfinfo', p], capture_output=True, text=True).stdout
    return int(re.search(r'Pages:\s+(\d+)', o).group(1))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto('file://' + src)
    for sc in (1.0, 0.96, 0.92, 0.88, 0.84, 0.80):
        pg.pdf(path=out, format='Letter', print_background=True, prefer_css_page_size=True, scale=sc)
        n = pages(out)
        if n == 1:
            print('ONE PAGE at scale', sc); b.close(); sys.exit(0)
    b.close()
print('STILL', n, 'PAGES at scale 0.80 - cut content'); sys.exit(3)
