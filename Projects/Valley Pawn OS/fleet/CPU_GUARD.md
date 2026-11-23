# CPU Guard — 2026-11-23 00:14 EST

Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script.

## Load
0:14  up  9:32, 1 user, load averages: 15.63 12.45 11.24

## Process states (R=running, U=waiting on disk)
```
  21 R  829 S    1 U 
1 sort
1 ps
1 head
1 awk
1 /usr/sbin/cfprefsd
1 /usr/libexec/sysmond
1 /usr/libexec/nsurlsessiond
1 /usr/libexec/duetexpertd
```

## Top CPU right now
```
 %CPU NI   PID COMM
 63.3  0  1778 /System/Library/Frameworks/Contacts.framework/Support/contactsd
 50.6  0 22966 /System/Library/Frameworks/CoreSpotlight.framework/spotlightknowledged
 47.2  0 54277 /System/Library/Frameworks/AddressBook.framework/Versions/A/Helpers/AddressBookManager.app/Contents/MacOS/AddressBookManager
 26.2  0   425 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer
 23.2  0  1239 /Applications/Parallels Desktop.app/Contents/MacOS//Parallels VM.app/Contents/MacOS/prl_vm_app
 21.8  0   780 /System/Library/ExtensionKit/Extensions/WallpaperAerialsExtension.appex/Contents/MacOS/WallpaperAerialsExtension
 20.9  0   433 /usr/libexec/runningboardd
 12.2  0  1120 /usr/libexec/sysmond
 10.6  0   739 /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/Metadata.framework/Versions/A/Support/corespotlightd
  8.5  0  3383 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
  6.3  0   802 /System/Library/Frameworks/VideoToolbox.framework/Versions/A/XPCServices/VTDecoderXPCService.xpc/Contents/MacOS/VTDecoderXPCService
```

## Memory
```
total = 0.00M  used = 0.00M  free = 0.00M  (encrypted)
System-wide memory free percentage: 65%
```

## Camera agents (nice should be 10)
```
54347  0   0.0 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python /Users
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
drwxr-xr-x@ 5 joshuadavis  staff         160 Nov 22 05:12 .
drwxr-xr-x@ 4 joshuadavis  staff         128 Nov  7 13:23 ..
-rw-r--r--@ 1 joshuadavis  staff  8185647104 Nov 22 23:47 index.db
-rw-r--r--@ 1 joshuadavis  staff       32768 Nov 22 23:47 index.db-shm
```
