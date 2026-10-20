#!/bin/bash
set +e
echo "=== 1 pref-dump before"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" pref-dump
echo "=== 2 persist-set"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-set
echo "=== 3 cookie-db after set (is the session cookie on disk?)"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
echo "=== 4 pref-dump after a Playwright run"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" pref-dump
echo "=== 5 persist-get plain"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
echo "=== 6 cookie-db after get"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
echo "=== 7 pref-dump"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" pref-dump
echo "=== 8 persist-set again, then persist-get --crashed (experiment)"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-set
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get --crashed
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" pref-dump
