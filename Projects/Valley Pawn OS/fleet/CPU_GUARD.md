# CPU Guard — 2026-11-25 00:11 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:11  up 2 days,  9:30, 1 user, load averages: 8.24 7.09 6.83

## Process states (R=running, U=waiting on disk)
```
   9 R  673 S    4 U 
1 sort
1 ps
1 head
1 /usr/libexec/diskimagesiod
1 /System/Library/PrivateFrameworks/PhotoLibraryServices.framework/Versions/A/Support/photolibraryd
1 /System/Library/Frameworks/WebKit.framework/Versions/A/XPCServices/com.apple.WebKit.WebContent.xpc/Contents/MacOS/com.apple.WebKit.WebContent
1 /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/Metadata.framework/Versions/A/Support/mds_stores
1 /System/Library/Frameworks/Contacts.framework/Support/contactsd
```

## Top CPU right now
```
 %CPU NI   PID COMM
 41.3  0   739 /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/Metadata.framework/Versions/A/Support/corespotlightd
 39.7  0   495 /System/Library/CoreServices/TimeMachine/backupd
 23.5  0 71756 /Applications/Google Drive.app/Contents/MacOS/Google Drive
 21.8  0 46450 /System/Library/PrivateFrameworks/PhotoLibraryServices.framework/Versions/A/Support/photolibraryd
 20.7  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 14.7  0  1239 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 14.6  0     1 /sbin/launchd
  9.8  0 63859 /System/Library/Frameworks/Contacts.framework/Support/contactsd
  8.5  0   588 /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/Metadata.framework/Versions/A/Support/mds_stores
  7.3  0 44431 /System/Library/PrivateFrameworks/CoreSuggestions.framework/Versions/A/Support/suggestd
  5.6  0   694 /System/Library/CoreServices/ControlCenter.app/Contents/MacOS/ControlCenter
```

## Memory
```
total = 8192.00M  used = 6916.62M  free = 1275.38M  (encrypted)
System-wide memory free percentage: 55%
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
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 24 05:26 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 24 23:33 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov 24 23:33 index.db-shm
```
