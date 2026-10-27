"""Person detector: YOLOX-S (OpenCV model zoo, ONNX) on onnxruntime CPU. Model at $VPST_DIR/models/yolox_s.onnx."""
import os, numpy as np, cv2
VPST = os.environ.get('VPST_DIR', os.path.expanduser('~/.vpst'))
_sess = None
def _session():  # OpenCV DNN (no onnxruntime dependency)
    global _sess
    if _sess is None:
        cv2.setNumThreads(2)
        _sess = cv2.dnn.readNetFromONNX(os.path.join(VPST, 'models', 'yolox_s.onnx'))
    return _sess

def _grids(size=640, strides=(8, 16, 32)):
    g, s = [], []
    for st in strides:
        n = size // st
        yv, xv = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
        g.append(np.stack((xv, yv), 2).reshape(-1, 2)); s.append(np.full((n * n, 1), st))
    return np.concatenate(g).astype(np.float32), np.concatenate(s).astype(np.float32)
GRIDS, STRIDES = _grids()

def people(bgr, conf=0.40, nms=0.45):
    """Return list of (x1,y1,x2,y2,score) for persons in a BGR image."""
    h, w = bgr.shape[:2]; r = min(640 / h, 640 / w)
    pad = np.full((640, 640, 3), 114, np.uint8)
    pad[:int(h * r), :int(w * r)] = cv2.resize(bgr, (int(w * r), int(h * r)))
    blob = pad.transpose(2, 0, 1)[None].astype(np.float32)
    net = _session(); net.setInput(blob); out = net.forward()[0]
    xy = (out[:, :2] + GRIDS) * STRIDES; wh = np.exp(out[:, 2:4]) * STRIDES
    score = out[:, 4] * out[:, 5]            # objectness * P(person); COCO class 0 = person
    keep = score > conf
    if not keep.any(): return []
    xy, wh, score = xy[keep], wh[keep], score[keep]
    boxes = np.concatenate([xy - wh / 2, wh], 1) / r
    idx = cv2.dnn.NMSBoxes(boxes.tolist(), score.tolist(), conf, nms)
    res = []
    for i in np.array(idx).flatten():
        x, y, bw, bh = boxes[i]; res.append((float(x), float(y), float(x + bw), float(y + bh), float(score[i])))
    return res
