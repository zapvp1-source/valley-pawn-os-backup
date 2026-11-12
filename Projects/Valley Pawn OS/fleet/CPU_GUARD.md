# CPU Guard — 2026-11-12 00:13 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:13  up 9 days,  7:26, 1 user, load averages: 5.00 6.03 7.05

## Process states (R=running, U=waiting on disk)
```
   6 R  742 S    2 U    3 Z 
1 sort
1 ps
1 head
1 awk
1 /usr/libexec/diskimagesiod
1 /usr/libexec/PerfPowerServices
1 /Applications/Google
```

## Top CPU right now
```
 %CPU NI   PID COMM
 99.3  0 30327 /Applications/Google Drive.app/Contents/MacOS/Google Drive
 20.1  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
  9.6  0 98098 /Library/Backblaze.bzpkg/bzfilelist
  7.5  0 97150 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
  6.2  0 99012 /usr/libexec/sysmond
  3.3  0 55818 /Users/joshuadavis/Library/Application Support/Claude/claude-code/2.1.309/5af865b9901c/claude.app/Contents/MacOS/claude
  3.2  0 77050 /bin/bash
  2.5  0  1185 /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
  2.2  0   417 /usr/sbin/bluetoothd
  2.2  0  4199 /System/Library/Frameworks/WebKit.framework/Versions/A/XPCServices/com.apple.WebKit.WebContent.xpc/Contents/MacOS/com.apple.WebKit.WebContent
  1.9  0   426 /System/Library/PrivateFrameworks/TCC.framework/Support/tccd
```

## Memory
```
total = 11264.00M  used = 10135.12M  free = 1128.88M  (encrypted)
System-wide memory free percentage: 52%
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
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 11 05:02 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 11 23:39 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov 11 23:39 index.db-shm
```
