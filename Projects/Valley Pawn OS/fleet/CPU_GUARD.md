# CPU Guard — 2026-11-11 00:13 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:13  up 8 days,  7:26, 1 user, load averages: 5.02 7.52 8.89

## Process states (R=running, U=waiting on disk)
```
   8 R  747 S    3 U    3 Z 
1 ps
1 head
1 /usr/libexec/dasd
1 /System/Library/PrivateFrameworks/XprotectFramework.framework/Versions/A/XPCServices/XProtectBridgeService.xpc/Contents/MacOS/XProtectBridgeService
1 /System/Library/PrivateFrameworks/StorageManagement.framework/PlugIns/ApplicationsStorageExtension.appex/Contents/MacOS/ApplicationsStorageExtension
1 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
1 /System/Library/CoreServices/TimeMachine/backupd
1 /System/Applications/Mail.app/Contents/PlugIns/MailStorageManagement.appex/Contents/MacOS/MailStorageManagement
```

## Top CPU right now
```
 %CPU NI   PID COMM
 54.3  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 43.2  0 78466 /System/Library/PrivateFrameworks/StorageManagement.framework/PlugIns/ApplicationsStorageExtension.appex/Contents/MacOS/ApplicationsStorageExtension
 34.7  0 78465 /System/Applications/Mail.app/Contents/PlugIns/MailStorageManagement.appex/Contents/MacOS/MailStorageManagement
 32.9  0 54073 /Applications/Google Drive.app/Contents/MacOS/Google Drive
 20.5  0 16267 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
 18.5  0   499 /System/Library/CoreServices/TimeMachine/backupd
 10.2  0   714 /System/Library/PrivateFrameworks/FileProvider.framework/Support/fileproviderd
  9.3  0 97150 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
  8.5  0   493 /usr/libexec/syspolicyd
  7.9  0 99012 /usr/libexec/sysmond
  7.4  0   706 /System/Library/PrivateFrameworks/iCloudDriveCore.framework/Versions/A/Support/bird
```

## Memory
```
total = 17408.00M  used = 15931.75M  free = 1476.25M  (encrypted)
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
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 10 05:21 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 11 00:01 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov 11 00:00 index.db-shm
```
