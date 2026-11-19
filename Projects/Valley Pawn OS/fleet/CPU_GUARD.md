# CPU Guard — 2026-11-19 00:11 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:11  up 16 days,  7:25, 2 users, load averages: 9.78 14.30 15.62

## Process states (R=running, U=waiting on disk)
```
   8 R  696 S    1 U    3 Z 
1 sort
1 ps
1 head
1 /usr/libexec/diskimagesiod
1 /usr/libexec/dasd
1 /System/Library/CoreServices/TimeMachine/backupd
1 /System/Library/CoreServices/SystemUIServer.app/Contents/MacOS/SystemUIServer
1 /System/Library/CoreServices/Finder.app/Contents/MacOS/Finder
```

## Top CPU right now
```
 %CPU NI   PID COMM
 34.0  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 33.4  0 97150 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 22.8  0   499 /System/Library/CoreServices/TimeMachine/backupd
 15.8  0   756 /System/Library/ExtensionKit/Extensions/WallpaperAerialsExtension.appex/Contents/MacOS/WallpaperAerialsExtension
 14.4  0   403 /usr/libexec/dasd
 13.1  0   690 /System/Library/CoreServices/SystemUIServer.app/Contents/MacOS/SystemUIServer
  6.7  0 99012 /usr/libexec/sysmond
  6.5  0 58188 /System/Library/Frameworks/VideoToolbox.framework/Versions/A/XPCServices/VTDecoderXPCService.xpc/Contents/MacOS/VTDecoderXPCService
  3.0  0 21798 /bin/bash
  2.3  0   426 /System/Library/PrivateFrameworks/TCC.framework/Support/tccd
  2.3  0   695 /System/Library/CoreServices/Finder.app/Contents/MacOS/Finder
```

## Memory
```
total = 12288.00M  used = 10970.00M  free = 1318.00M  (encrypted)
System-wide memory free percentage: 50%
```

## Camera agents (nice should be 10)
```
21786  0   0.0 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python /Users
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
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 18 05:25 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 18 23:34 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov 18 23:34 index.db-shm
```
