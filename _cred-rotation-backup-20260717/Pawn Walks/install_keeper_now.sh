#!/bin/bash
SRC="/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks"
DST="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
cp "$SRC/bravo_foreground_keeper.ahk" "$DST/bravo_foreground_keeper.ahk"
cp "$SRC/_install_foreground_keeper.ps1" "$DST/_install_foreground_keeper.ps1"
echo "copied keeper + installer into project folder"
GUID='{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}'
nohup /usr/local/bin/prlctl exec "$GUID" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_install_foreground_keeper.ps1' \
  > /tmp/keeper_install.log 2>&1 &
echo "installer launched (backgrounded) pid $!"
