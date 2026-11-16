# Disk Guard — 2026-11-15 12:19:32

Native agents com.valleypawn.disk-guard (clean, daily 4:10 AM) + disk-guard-report (Sun 4:20 AM).
Script: Valley Pawn OS/bin/disk_guard.sh. Stopgap until the 2TB Mac Studio arrives (mid-Dec 2026).

## Volume
```
Filesystem      Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5    494G    410G     48G    90%    3.3M  465M    1%   /System/Volumes/Data
```
Swap files: 0.0 GB · Time Machine local snapshots: 2

## Biggest places (GB)
| GB | Path |
|---|---|
| 67.4 | ~/Parallels |
| 47.2 | ~/Library/Application Support |
| 27.5 | ~/Library/Mail |
| 26.6 | ~/Library/Mobile Documents |
| 21.4 | /Applications |
| 19.4 | ~/.vp-studio |
| 19.1 | ~/Pictures |
| 13.1 | ~/Library/Containers |
| 11.1 | ~/Documents |
| 10.8 | ~/Library/Messages |
| 9.8 | ~/Library/Caches |
| 9.3 | ~/Desktop |
| 8.4 | ~/.ollama |
| 6.9 | ~/Downloads |
| 6.3 | /Library |
| 3.0 | ~/Library/Group Containers |
| 0.3 | ~/.cache |
| 0.2 | ~/Music |
| 0.2 | ~/Library/Logs |
| 0.1 | ~/Library/CloudStorage |
| 0.0 | ~/Movies |
| 0.0 | ~/Applications (Parallels) |
| 0.0 | ~/.npm |
| 0.0 | ~/.Trash |

### Top 10 inside ~/Library/Application Support (GB)
```
  36.0  ~/Library/Application Support/Claude
   5.4  ~/Library/Application Support/Google
   1.8  ~/Library/Application Support/Slack
   0.8  ~/Library/Application Support/com.apple.wallpaper
   0.4  ~/Library/Application Support/HealthOS
   0.4  ~/Library/Application Support/zoom.us
   0.4  ~/Library/Application Support/WebEx Folder
   0.4  ~/Library/Application Support/Spotify
   0.4  ~/Library/Application Support/FileProvider
   0.4  ~/Library/Application Support/valleypawn
```

### Top 10 inside ~/Library/Containers (GB)
```
   3.5  ~/Library/Containers/com.apple.podcasts
   1.4  ~/Library/Containers/com.tinyspeck.slackmacgap
   1.3  ~/Library/Containers/com.apple.mail
   1.3  ~/Library/Containers/com.apple.AMPArtworkAgent
   1.3  ~/Library/Containers/com.apple.Safari
   1.1  ~/Library/Containers/com.microsoft.teams2
   0.5  ~/Library/Containers/com.apple.photolibraryd
   0.5  ~/Library/Containers/com.apple.geod
   0.4  ~/Library/Containers/com.apple.mediaanalysisd
   0.4  ~/Library/Containers/com.apple.CloudDocs.iCloudDriveFileProvider
```

### Top 10 inside ~/Library/Group Containers (GB)
```
   0.9  ~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts
   0.6  ~/Library/Group Containers/group.com.apple.FaceTime
   0.5  ~/Library/Group Containers/UBF8T346G9.Office
   0.3  ~/Library/Group Containers/group.com.apple.replicatord
   0.2  ~/Library/Group Containers/group.com.apple.VoiceMemos.shared
   0.1  ~/Library/Group Containers/group.com.apple.notes
   0.1  ~/Library/Group Containers/group.com.apple.news
   0.1  ~/Library/Group Containers/group.com.apple.reminders
   0.0  ~/Library/Group Containers/UBF8T346G9.com.microsoft.teams
   0.0  ~/Library/Group Containers/group.com.apple.contacts
```

### Top 10 inside ~/Library/Caches (GB)
```
   3.8  ~/Library/Caches/claude-cli-nodejs
   2.2  ~/Library/Caches/Google
   1.2  ~/Library/Caches/valleypawn
   0.4  ~/Library/Caches/CloudKit
   0.4  ~/Library/Caches/com.spotify.client
   0.3  ~/Library/Caches/com.apple.textunderstandingd
   0.3  ~/Library/Caches/com.tinyspeck.slackmacgap.ShipIt
   0.3  ~/Library/Caches/SiriTTS
   0.2  ~/Library/Caches/com.apple.AppleMediaServices
   0.2  ~/Library/Caches/GeoServices
```

### Top 10 inside ~/Documents (GB)
```
  10.5  ~/Documents/Claude
   0.3  ~/Documents/Recordings
   0.2  ~/Documents/Zoom
   0.0  ~/Documents/.tmp.driveupload
   0.0  ~/Documents/STATEMENT 2015-2024.zip
   0.0  ~/Documents/STATEMENT 2015-2024 2.zip
   0.0  ~/Documents/CustomerReport.pdf
   0.0  ~/Documents/proof_44406-1.pdf
   0.0  ~/Documents/Scan_20260907 (2).pdf
   0.0  ~/Documents/Scan_20260907 (2) 2.pdf
```

### Top 10 inside ~/Documents/Claude/Projects (GB)
```
   1.3  ~/Documents/Claude/Projects/Refine Social Media
   1.3  ~/Documents/Claude/Projects/Unified Search
   1.0  ~/Documents/Claude/Projects/Valley Pawn OS
   1.0  ~/Documents/Claude/Projects/Call Analysis
   1.0  ~/Documents/Claude/Projects/Store Conduct Watch
   0.9  ~/Documents/Claude/Projects/Training Program
   0.8  ~/Documents/Claude/Projects/Bravo Data Extraction
   0.5  ~/Documents/Claude/Projects/Zoom Call Pipeline
   0.4  ~/Documents/Claude/Projects/Valley Pawn Studios
   0.3  ~/Documents/Claude/Projects/eBay
```

### Top 10 inside ~/Library/CloudStorage (GB)
```
   0.1  ~/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com
   0.0  ~/Library/CloudStorage/Claude outputs
   0.0  ~/Library/CloudStorage/.DS_Store
```

## Files over 2 GB anywhere in home
```
  10.0 ~/Library/Application Support/Claude/vm_bundles/claudevm.bundle/rootfs.img
   9.5 ~/Library/Application Support/Claude/vm_bundles/claudevm.bundle/sessiondata.img
   3.6 ~/Library/Mobile Documents/com~apple~CloudDocs/01 Business/Full Circle Finance (Valley Pawn)/06 Operations/Chekkit Managment copy.mov
   2.6 ~/Desktop/_deleted_installers_20260904/Microsoft_365_and_Office_16.104.25121423_Installer.pkg
   2.5 ~/Desktop/_deleted_installers_20260904/Microsoft_365_and_Office_16.105.26011018_Installer.pkg
```

## Recent guard actions
```
2026-11-15 12:19:31 [report] cleared cache /Users/joshuadavis/.npm/_cacache (0.1 GB)
2026-11-15 12:19:32 [report] cleared cache /Users/joshuadavis/Library/Caches/pip (0.4 GB)
2026-11-15 12:19:32 [report] cleared cache /Users/joshuadavis/Library/Caches/Homebrew (0.4 GB)
2026-11-15 12:19:32 [report] deleted 105 log/crash files older than 30 days
2026-11-15 12:19:32 [report] free 44 GB -> 44 GB
```
