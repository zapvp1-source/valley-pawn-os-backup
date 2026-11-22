# CPU Guard — 2026-11-22 00:10 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:10  up 19 days,  7:23, 3 users, load averages: 12.71 17.14 17.83

## Process states (R=running, U=waiting on disk)
```
   8 R  789 S    3 U    3 Z 
1 sort
1 ps
1 head
1 /usr/libexec/logd
1 /usr/libexec/diskimagesiod
1 /usr/libexec/dasd
1 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
1 /System/Library/PrivateFrameworks/EmailDaemon.framework/Versions/A/maild
```

## Top CPU right now
```
 %CPU NI   PID COMM
 41.2  0   499 /System/Library/CoreServices/TimeMachine/backupd
 28.4  0   690 /System/Library/CoreServices/SystemUIServer.app/Contents/MacOS/SystemUIServer
 26.2  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 17.9  0 97150 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 13.0  0   756 /System/Library/ExtensionKit/Extensions/WallpaperAerialsExtension.appex/Contents/MacOS/WallpaperAerialsExtension
 11.7  0   403 /usr/libexec/dasd
 11.3  0   350 /usr/libexec/logd
  9.9  0 33069 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
  8.4  0 99012 /usr/libexec/sysmond
  4.4  0 58188 /System/Library/Frameworks/VideoToolbox.framework/Versions/A/XPCServices/VTDecoderXPCService.xpc/Contents/MacOS/VTDecoderXPCService
  3.9  0   714 /System/Library/PrivateFrameworks/FileProvider.framework/Support/fileproviderd
```

## Memory
```
total = 22528.00M  used = 21608.19M  free = 919.81M  (encrypted)
System-wide memory free percentage: 43%
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
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 21 05:04 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 21 22:40 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov 21 22:40 index.db-shm
```
