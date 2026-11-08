# CPU Guard — 2026-11-08 00:12 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:12  up 5 days,  7:25, 1 user, load averages: 11.09 10.16 9.03

## Process states (R=running, U=waiting on disk)
```
   6 R  689 S    2 U    3 Z 
1 ps
1 head
1 /usr/libexec/diskimagesiod
1 /System/Library/CoreServices/TimeMachine/backupd
```

## Top CPU right now
```
 %CPU NI   PID COMM
 41.0  0   499 /System/Library/CoreServices/TimeMachine/backupd
 30.0  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 27.7  0  1179 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 18.2  0   690 /System/Library/CoreServices/SystemUIServer.app/Contents/MacOS/SystemUIServer
  5.0  0  1731 /Applications/Claude.app/Contents/Frameworks/Claude Helper (Renderer).app/Contents/MacOS/Claude Helper (Renderer)
  4.4  0  1340 /System/Applications/Utilities/Activity Monitor.app/Contents/MacOS/Activity Monitor
  3.9  0 99012 /usr/libexec/sysmond
  2.8  0   695 /System/Library/CoreServices/Finder.app/Contents/MacOS/Finder
  2.6  0 11739 /usr/libexec/diskimagesiod
  1.5  0 27382 /bin/bash
  1.5  0   426 /System/Library/PrivateFrameworks/TCC.framework/Support/tccd
```

## Memory
```
total = 7168.00M  used = 5999.50M  free = 1168.50M  (encrypted)
System-wide memory free percentage: 78%
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
total 15987656
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov  7 13:23 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 2 joshuadavis  staff  8185647104 Nov  8 00:00 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov  8 00:00 index.db-shm
```
