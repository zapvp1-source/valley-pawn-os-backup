import sys
p=sys.argv[1]; s=open(p).read()
a='''PORT=9333   # = vp_browser.DEBUG_PORT
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
MAIN='''
b='''PORT=9333   # = vp_browser.DEBUG_PORT
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
# 2026-11-21: always-on browser host (bin/vp_browser_host.py). When it is enabled the sign-in tabs open IN that
# Chrome, in one window in front, and the checks keep running; nothing is quit first. Old path below otherwise.
HOST_MODE=0
if [ "$1" != "--test" ] && /usr/bin/python3 "$OS_BIN/vp_browser_host.py" enabled; then HOST_MODE=1; fi
MAIN='''
a2='''if [ -n "$MAIN" ]; then
  /usr/bin/python3 "$OS_BIN/vp_browser.py" cdp-close'''
b2='''if [ "$HOST_MODE" = 0 ] && [ -n "$MAIN" ]; then
  /usr/bin/python3 "$OS_BIN/vp_browser.py" cdp-close'''
a3='''/usr/bin/python3 "$OS_BIN/vp_browser.py" prefs
/usr/bin/python3 "$OS_BIN/vp_browser.py" set-startup
if [ "$1" = "--test" ]; then'''
b3='''[ "$HOST_MODE" = 0 ] && /usr/bin/python3 "$OS_BIN/vp_browser.py" prefs
[ "$HOST_MODE" = 0 ] && /usr/bin/python3 "$OS_BIN/vp_browser.py" set-startup
if [ "$1" = "--test" ]; then'''
a4='''open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --remote-debugging-port=$PORT --new-window "${TABS[@]}"'''
b4='''if [ "$HOST_MODE" = 1 ]; then
  exec /usr/bin/python3 "$OS_BIN/vp_browser_host.py" signin "${TABS[@]}"
fi
open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --remote-debugging-port=$PORT --new-window "${TABS[@]}"'''
for o,n in ((a,b),(a2,b2),(a3,b3),(a4,b4)):
    assert s.count(o)==1, o[:50]
    s=s.replace(o,n)
open(p,'w').write(s); print("patched signin")
