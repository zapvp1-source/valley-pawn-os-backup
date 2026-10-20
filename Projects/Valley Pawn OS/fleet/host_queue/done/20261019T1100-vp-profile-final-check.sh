#!/bin/bash
set +e
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_close.sh"
echo "close rc=$?"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/cloudcover_profile_prefs.py"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" set-startup
echo "set-startup rc=$?"
