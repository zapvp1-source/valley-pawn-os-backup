#!/bin/bash
set +e
echo "=== 1 set-startup (Chrome's own settings page writes the tracked pref)"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" set-startup
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" pref-dump
echo "=== 2 PROOF 1a persist-set"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-set
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
echo "=== 3 PROOF 1b persist-get (scripts' launch)"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
echo "=== 4 PROOF 2a real quit path: open -na (launcher --test), wait, vp_signin_close.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_front.sh" --test
sleep 40
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_close.sh"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" cookie-db
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" pref-dump
echo "=== 5 PROOF 2b persist-get after the real quit"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
echo "=== 6 one more scripts' launch (second restart) to be sure"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" probe
