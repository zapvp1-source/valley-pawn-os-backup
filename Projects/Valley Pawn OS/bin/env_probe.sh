#!/bin/bash
# read-only: interpreter + tool availability for native agents
/usr/bin/python3 -c "import sys;print(sys.version)"
/usr/bin/python3 -c "import requests;print('requests', requests.__version__)" 2>&1 | tail -1
for t in ffmpeg ffprobe sips sqlite3; do printf "%s: " $t; command -v $t || ls /opt/homebrew/bin/$t /usr/local/bin/$t 2>/dev/null || echo missing; done
/usr/bin/python3 -c "import PIL;print('PIL', PIL.__version__)" 2>&1 | tail -1
