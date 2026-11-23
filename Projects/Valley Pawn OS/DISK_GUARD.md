# Disk Guard — 2026-11-22 14:43:33

Native agents com.valleypawn.disk-guard (clean, daily 4:10 AM) + disk-guard-report (Sun 4:20 AM).
Script: Valley Pawn OS/bin/disk_guard.sh. Stopgap until the 2TB Mac Studio arrives (mid-Dec 2026).

## Volume
```
Filesystem      Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5    494G    415G     54G    89%    2.3M  523M    0%   /System/Volumes/Data
```
Swap files: 0.0 GB · Time Machine local snapshots: 1

## Biggest places (GB)
| GB | Path |
|---|---|
| 67.8 | ~/Parallels |
| 52.1 | ~/Library/Application Support |
| 27.9 | ~/Library/Mail |
| 23.0 | ~/Library/Mobile Documents |
| 22.0 | ~/Library/Containers |
| 20.7 | /Applications |
| 19.4 | ~/Pictures |
| 19.3 | ~/.vp-studio |
| 11.7 | ~/Documents |
| 10.9 | ~/Library/Messages |
| 8.4 | ~/.ollama |
| 6.4 | ~/Downloads |
| 6.3 | /Library |
| 5.9 | ~/Library/Caches |
| 3.2 | ~/Desktop |
| 3.0 | ~/Library/Group Containers |
| 0.4 | ~/Library/CloudStorage |
| 0.3 | ~/.cache |
| 0.2 | ~/Music |
| 0.2 | ~/Library/Logs |
| 0.0 | ~/Movies |
| 0.0 | ~/Applications (Parallels) |
| 0.0 | ~/.npm |
| 0.0 | ~/.Trash |

### Top 10 inside ~/Library/Application Support (GB)
```
  40.1  ~/Library/Application Support/Claude
   5.4  ~/Library/Application Support/Google
   1.8  ~/Library/Application Support/Slack
   1.2  ~/Library/Application Support/com.apple.wallpaper
   0.5  ~/Library/Application Support/valleypawn
   0.4  ~/Library/Application Support/HealthOS
   0.4  ~/Library/Application Support/zoom.us
   0.4  ~/Library/Application Support/WebEx Folder
   0.4  ~/Library/Application Support/Spotify
   0.4  ~/Library/Application Support/FileProvider
```

### Top 10 inside ~/Library/Containers (GB)
```
  11.6  ~/Library/Containers/com.apple.podcasts
   1.7  ~/Library/Containers/com.tinyspeck.slackmacgap
   1.3  ~/Library/Containers/com.apple.mail
   1.3  ~/Library/Containers/com.apple.AMPArtworkAgent
   1.2  ~/Library/Containers/com.apple.Safari
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

### Top 10 inside ~/Documents/Claude/Projects (GB)
```
   1.4  ~/Documents/Claude/Projects/Refine Social Media
   1.3  ~/Documents/Claude/Projects/Unified Search
   1.1  ~/Documents/Claude/Projects/Valley Pawn OS
   1.0  ~/Documents/Claude/Projects/Call Analysis
   1.0  ~/Documents/Claude/Projects/Training Program
   1.0  ~/Documents/Claude/Projects/Store Conduct Watch
   0.8  ~/Documents/Claude/Projects/Bravo Data Extraction
   0.5  ~/Documents/Claude/Projects/Zoom Call Pipeline
   0.4  ~/Documents/Claude/Projects/Valley Pawn Studios
   0.3  ~/Documents/Claude/Projects/eBay
```

### Top 10 inside ~/Library/CloudStorage (GB)
```
   0.4  ~/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com
   0.0  ~/Library/CloudStorage/Claude outputs
   0.0  ~/Library/CloudStorage/.DS_Store
```

## Files over 2 GB anywhere in home
```
  61.5 ~/Parallels/Windows 11.pvm/harddisk.hdd/harddisk.hdd.0.{5fbaabe3-6958-40ff-92a7-860e329aab41}.hds
  10.0 ~/Library/Application Support/Claude/vm_bundles/claudevm.bundle/rootfs.img
   9.9 ~/Library/Application Support/Claude/vm_bundles/claudevm.bundle/sessiondata.img
   8.4 ~/.ollama/models/blobs/sha256-2049f5674b1e92b4464e5729975c9689fcfbf0b0e4443ccf10b5339f370f9a54
   7.6 ~/.vp-studio/offsync/unified-search/index.db
```

## Recent guard actions
```
2026-11-18 04:10:05 [clean] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-18 04:10:05 [clean] free 25 GB -> 25 GB
2026-11-19 04:10:03 [clean] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-19 04:10:03 [clean] free 28 GB -> 28 GB
2026-11-20 04:10:04 [clean] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-20 04:10:04 [clean] free 41 GB -> 41 GB
2026-11-21 04:10:04 [clean] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-21 04:10:05 [clean] free 34 GB -> 34 GB
2026-11-22 04:10:05 [clean] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-22 04:10:05 [clean] free 20 GB -> 20 GB
2026-11-22 04:20:05 [report] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-22 04:20:05 [report] free 18 GB -> 18 GB
2026-11-22 04:40:15 [report] report written
2026-11-22 14:43:29 [report] trimmed claude-cli-nodejs cache (was 0.0 GB, kept last 7 days)
2026-11-22 14:43:33 [report] free 49 GB -> 49 GB
```
