#!/usr/bin/env python3
"""Probe: upload one comedy reel to Publer media library and print the raw response,
so the publish script is built around the real payload shape, not an assumption."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient

p = PublerClient()
f = ROOT / "reels" / "humobjectpov20260822poolrobot.mp4"
print("uploading", f, f.stat().st_size, "bytes")
resp = p.upload_media(str(f))
print(json.dumps(resp, indent=2)[:3000])
Path(ROOT / "manifests" / "_probe_media_20260822.json").write_text(json.dumps(resp, indent=2))
