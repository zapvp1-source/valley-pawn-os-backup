#!/bin/bash
# conduct_watch_setup.sh — idempotent host setup for Store Conduct Watch (built 2026-10-31). Self-verifying; prints OK/FAIL.
# Dedicated venv (does not touch the Store Traffic venv): aiortc + PyAV + Pillow + numpy + faster-whisper.
set -u
VENV="$HOME/.vp-studio/conduct-watch-venv"
HBPY="$(ls /opt/homebrew/bin/python3.1[0-9] 2>/dev/null | sort -V | tail -1)"
[ -x "$VENV/bin/python" ] || "$HBPY" -m venv "$VENV"
"$VENV/bin/python" -m pip install -q --upgrade pip 2>&1 | tail -1
"$VENV/bin/python" -m pip install -q aiortc av pillow numpy faster-whisper opencv-python-headless 2>&1 | tail -3
mkdir -p "$HOME/.vp-studio/conduct-watch"
"$VENV/bin/python" - <<'PYEOF'
import av, aiortc, PIL, numpy
print('OK deps av', av.__version__, 'aiortc', aiortc.__version__, 'Pillow', PIL.__version__)
for c in ['h264_videotoolbox', 'libx264', 'mpeg4', 'aac']:
    try: av.codec.Codec(c, 'w'); print('OK codec', c)
    except Exception as e: print('NO codec', c)
from faster_whisper import WhisperModel
import numpy as np, time
m = WhisperModel('base.en', device='cpu', compute_type='int8'); t = time.time()
m.transcribe(np.zeros(16000 * 5, dtype=np.float32), vad_filter=True); print('OK whisper base.en loaded', round(time.time() - t, 1), 's')
PYEOF
df -h "$HOME" | tail -1
sysctl -n hw.ncpu hw.memsize machdep.cpu.brand_string 2>/dev/null
