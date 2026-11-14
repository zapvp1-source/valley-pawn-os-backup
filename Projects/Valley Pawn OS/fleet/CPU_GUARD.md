# CPU Guard — 2026-11-14 00:14 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:14  up 11 days,  7:27, 1 user, load averages: 9.86 12.32 13.17

## Process states (R=running, U=waiting on disk)
```
   9 R  650 S    2 U    3 Z 
1 sort
1 ps
1 head
1 /usr/sbin/cfprefsd
1 /usr/libexec/diskimagesiod
1 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
1 /System/Library/Frameworks/CoreSpotlight.framework/spotlightknowledged
1 /System/Library/CoreServices/TimeMachine/backupd
```

## Top CPU right now
```
 %CPU NI   PID COMM
 47.6  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 30.4  0 16267 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
 26.2  0 30327 /Applications/Google Drive.app/Contents/MacOS/Google Drive
 20.7  0   403 /usr/libexec/dasd
 14.7  0 97150 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 11.0  0 99012 /usr/libexec/sysmond
 10.6  0 95582 /System/Library/Frameworks/CoreSpotlight.framework/spotlightknowledged
  7.2  0   499 /System/Library/CoreServices/TimeMachine/backupd
  6.7  0   688 /System/Library/CoreServices/ControlCenter.app/Contents/MacOS/ControlCenter
  5.0  0   690 /System/Library/CoreServices/SystemUIServer.app/Contents/MacOS/SystemUIServer
  4.8  0   646 /usr/sbin/cfprefsd
```

## Memory
```
total = 9216.00M  used = 8668.31M  free = 547.69M  (encrypted)
System-wide memory free percentage: 62%
```

## Camera agents (nice should be 10)
```
```

## Hot processes (pid, consecutive 5-min samples >150%, %cpu, name)
```
```

## Large files changing inside Documents (last scan)
```
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
total 15987720
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 13 05:27 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 13 23:34 index.db
-rw-r--r--@ 1 joshuadavis  staff       65536 Nov 13 23:34 index.db-shm
```
