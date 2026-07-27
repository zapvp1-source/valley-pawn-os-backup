---
name: nightly-desktop-cleanup
description: Sort loose Desktop files into type-based folders every night at 3 AM
model: claude-sonnet-5
---


Clean up Joshua's macOS Desktop by sorting loose files into type-based folders. Use the mcp__Control_your_Mac__osascript tool (load via ToolSearch if deferred) to run shell commands via `do shell script`. Do NOT use computer-use/screen control — this is a pure shell task.

Run this exact logic:

1. Ensure these folders exist on ~/Desktop: Documents, Photos, Spreadsheets, Videos, Other.
2. Move only loose FILES (find ~/Desktop -maxdepth 1 -type f) into them by extension (case-insensitive):
   - pdf, docx, doc, eml → Documents
   - png, jpg, jpeg, heic → Photos
   - xlsx, csv, xltx, xls → Spreadsheets
   - mov, mp4 → Videos
   - everything else → Other
3. SKIP (leave in place): .DS_Store, .localized, Thumbs.db, desktop.ini, any file starting with ~$ (Office lock files), and ALL directories/folders. Never touch existing folders.
4. Use mv -n (no overwrite). If a name collision occurs, leave the file in place.

Example one-liner (adapt as needed):
cd ~/Desktop && mkdir -p Documents Photos Spreadsheets Videos Other && find . -maxdepth 1 -type f | while IFS= read -r f; do n=$(basename "$f"); case "$n" in .DS_Store|.localized|Thumbs.db|desktop.ini|'~$'*) continue;; esac; ext=$(echo "${n##*.}" | tr 'A-Z' 'a-z'); case "$ext" in pdf|docx|doc|eml) d=Documents;; png|jpg|jpeg|heic) d=Photos;; xlsx|csv|xltx|xls) d=Spreadsheets;; mov|mp4) d=Videos;; *) d=Other;; esac; mv -n "$f" "$d/"; done

Afterward, report briefly: how many files were moved into each folder (or "Desktop already clean" if nothing moved). Do not delete anything.

<!-- migrated to working model 2026-06-15 -->