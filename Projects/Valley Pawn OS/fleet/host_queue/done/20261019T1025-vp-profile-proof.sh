#!/bin/bash
set +e
echo "=== 0 probe before"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" probe
echo "=== 1 migrate pw-cloudcover -> pw-vp (backup copy first)"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" migrate
echo "=== 2 PROOF 1a: headed Playwright context sets session cookie + localStorage, closes normally"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-set
sleep 3
echo "=== 3 PROOF 1b: scripts' exact launch reads them back"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
echo "=== 4 PROOF 2a: real quit path - open -na (launcher, --test tabs), wait, vp_signin_close.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_front.sh" --test
sleep 30
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_close.sh"
sleep 3
echo "=== 5 PROOF 2b: scripts' exact launch reads the cookies after the real quit"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
echo "=== 6 probe after"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" probe
