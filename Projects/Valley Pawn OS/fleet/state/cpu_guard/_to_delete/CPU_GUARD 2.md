# CPU Guard — 2026-11-07 13:33 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
13:33  up 4 days, 20:46, 1 user, load averages: 282.54 261.86 260.89

## Process states (R=running, U=waiting on disk)
```
 135 R  460 S    2 Z 
13 /Applications/Google
7 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
6 /System/Library/Frameworks/WebKit.framework/Versions/A/XPCServices/com.apple.WebKit.WebContent.xpc/Contents/MacOS/com.apple.WebKit.WebContent
2 awk
2 /usr/sbin/distnoted
2 /usr/sbin/cfprefsd
2 /System/Library/PrivateFrameworks/TCC.framework/Support/tccd
2 /System/Library/Frameworks/QuickLookUI.framework/Versions/A/XPCServices/QuickLookUIService.xpc/Contents/MacOS/QuickLookUIService
```

## Top CPU right now
```
 %CPU NI   PID COMM
148.7  0 29306 /System/Library/Frameworks/WebKit.framework/Versions/A/XPCServices/com.apple.WebKit.WebContent.xpc/Contents/MacOS/com.apple.WebKit.WebContent
114.6  0 29300 /Applications/Google Drive.app/Contents/MacOS/Google Drive
 87.4 10 76393 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
 72.4 10 76405 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
 70.2 10 76394 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
 70.1 10 76401 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
 52.9  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 32.7 10 76046 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
 31.6 10 76052 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
 28.4  0  1179 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 24.0  0   677 /System/Library/PrivateFrameworks/CloudKitDaemon.framework/Support/cloudd
```

## Memory
```
total = 10240.00M  used = 9249.25M  free = 990.75M  (encrypted)
System-wide memory free percentage: 49%
```

## Camera agents (nice should be 10)
```
76016 10  10.8 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python watch.py L
76043 10  20.3 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python watch.py C
76046 10  30.4 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python watch.py W
76052 10  34.0 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python watch.py H
76377 10   0.1 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python counter.py
76393 10  68.3 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python counter.py
76394 10  54.3 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python counter.py
76401 10  52.5 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python counter.py
76405 10  63.2 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python counter.py
84748 10  17.1 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python watch.py R
```

## Hot processes (pid, consecutive 5-min samples >150%, %cpu, name)
```
```

## Large files changing inside Documents (last scan)
```
/Users/joshuadavis/Documents/.tmp.driveupload/125437
```

## Last relocation pass
```
OK already relocated: /Users/joshuadavis/Documents/Claude/Projects/Unified Search/index.db -> /Users/joshuadavis/.vp-studio/offsync/unified-search/index.db
OK already relocated: /Users/joshuadavis/Documents/Claude/Projects/Store Traffic Counter/dets -> /Users/joshuadavis/.vp-studio/offsync/store-traffic/dets
OK already relocated: /Users/joshuadavis/Documents/Claude/Projects/Store Traffic Counter/tracks -> /Users/joshuadavis/.vp-studio/offsync/store-traffic/tracks
OK already relocated: /Users/joshuadavis/Documents/Claude/Projects/Store Traffic Counter/audit -> /Users/joshuadavis/.vp-studio/offsync/store-traffic/audit
OK already relocated: /Users/joshuadavis/Documents/Claude/Projects/Store Traffic Counter/evidence -> /Users/joshuadavis/.vp-studio/offsync/store-traffic/evidence
/Users/joshuadavis/.vp-studio/offsync/store-traffic:
total 0
drwxr-xr-x@ 6 joshuadavis  staff  192 Nov  7 13:26 .
drwxr-xr-x@ 4 joshuadavis  staff  128 Nov  7 13:23 ..
drwxr-xr-x@ 7 joshuadavis  staff  224 Nov  7 13:25 audit
drwxr-xr-x@ 7 joshuadavis  staff  224 Nov  7 13:25 dets
drwxr-xr-x@ 8 joshuadavis  staff  256 Nov  7 13:26 evidence
drwxr-xr-x@ 9 joshuadavis  staff  288 Nov  7 13:25 tracks

/Users/joshuadavis/.vp-studio/offsync/unified-search:
total 15987656
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov  7 13:23 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 2 joshuadavis  staff  8185647104 Nov  7 13:26 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov  7 13:26 index.db-shm
```
