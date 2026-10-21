#!/bin/bash
# 2026-10-20: re-prove the sign-in quit path with the new CDP close (expect exit_type 'Normal') + session-cookie survival, then the Northwest render
echo "== 1. test window (open -na, off-screen, cookie-setting tabs)"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_front.sh" --test
sleep 40
echo "== 2. close via CDP (fallback SIGTERM)"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_close.sh"
echo "== 3. scripts' launch reads the cookies back"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" persist-get
echo "== 4. northwest render (autofill detection; outside the SMS window = must stop without clicking)"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --probe
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --render --diag
echo "== 5. exit type after the render"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" exit-type
