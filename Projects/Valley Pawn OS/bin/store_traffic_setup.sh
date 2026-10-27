#!/bin/bash
# store_traffic_setup.sh — one-time/idempotent host setup for the Store Traffic door counter (built 2026-10-26).
# Installs Python deps (user site, system python3), downloads the YOLOX-S person model, and creates the
# secret-handoff keypair: private key stays in ~/.vp_secrets/store_traffic, public key is written to
# Projects/Store Traffic Counter/handoff/host_pubkey.pem so a session can encrypt the camera API secret
# for this Mac without the plaintext ever touching iCloud/Drive. Self-verifying; prints OK/FAIL lines.
set -u
PY=/usr/bin/python3
SEC="$HOME/.vp_secrets/store_traffic"
PROJ="$HOME/Documents/Claude/Projects/Store Traffic Counter"
mkdir -p "$SEC/models" "$PROJ/handoff"; chmod 700 "$SEC"
"$PY" -m pip install --user -q --upgrade pip 2>&1 | tail -1
# Dedicated venv on Homebrew Python (system 3.9 is too old for current aiortc/PyAV). Detector uses OpenCV DNN.
VENV="$HOME/.vp-studio/store-traffic-venv"
HBPY="$(ls /opt/homebrew/bin/python3.1[0-9] 2>/dev/null | sort -V | tail -1)"
[ -x "$VENV/bin/python" ] || "$HBPY" -m venv "$VENV"
"$VENV/bin/python" -m pip install -q --upgrade pip 2>&1 | tail -1
"$VENV/bin/python" -m pip install -q aiortc opencv-python-headless numpy cryptography 2>&1 | tail -3
[ -s "$SEC/models/yolox_s.onnx" ] || curl -sSL -o "$SEC/models/yolox_s.onnx" \
  "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/object_detection_yolox/object_detection_yolox_2022nov.onnx"
"$PY" - <<'PYEOF'
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
sec = os.path.expanduser('~/.vp_secrets/store_traffic'); priv = os.path.join(sec, 'handoff_key.pem')
pub = os.path.expanduser('~/Documents/Claude/Projects/Store Traffic Counter/handoff/host_pubkey.pem')
if not os.path.exists(priv):
    k = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    open(priv, 'wb').write(k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    os.chmod(priv, 0o600)
k = serialization.load_pem_private_key(open(priv, 'rb').read(), None)
open(pub, 'wb').write(k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
print('OK keypair; pubkey ->', pub)
PYEOF
"$VENV/bin/python" -c "import aiortc, cv2, numpy; from aiortc import RTCBundlePolicy; print('OK deps aiortc', aiortc.__version__, 'cv2', cv2.__version__)" 2>&1 | tail -1
"$VENV/bin/python" --version
[ -s "$SEC/models/yolox_s.onnx" ] && echo "OK model $(wc -c < "$SEC/models/yolox_s.onnx") bytes" || echo "FAIL model"
"$PY" --version
