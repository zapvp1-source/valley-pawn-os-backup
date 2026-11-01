"""Reads image paths (one per line) on stdin, prints JSON {path: person_count}. Runs in its own process so OpenCV's
bundled FFmpeg never shares a process with PyAV's (duplicate libavdevice classes on macOS)."""
import json, os, sys
os.environ.setdefault('VPST_DIR', os.path.expanduser('~/.vp_secrets/store_traffic'))
sys.path.insert(0, os.path.expanduser('~/Documents/Claude/Projects/Store Traffic Counter'))
import cv2, detector
out = {}
for p in sys.stdin.read().splitlines():
    try:
        img = cv2.imread(p); out[p] = -1 if img is None else len(detector.people(img, conf=0.35))
    except Exception:
        out[p] = -1
print(json.dumps(out))
