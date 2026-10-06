#!/usr/bin/env python3
"""vp_publer.py — stdlib-only Publer API client for native agents (2026-10-05).
Same config as Refine Social Media/publer_client.py (publer_config.json + publer_accounts.json), but no
`requests` dependency so it runs under /usr/bin/python3 from launchd.
  upload(path) -> media dict (Publer S3-hosted; "path"/"url" is a public URL usable in email too)
  accounts() -> {store_key: {...publer_id...}} from publer_accounts.json
  call(method, path, payload=None)
  `python3 vp_publer.py probe` prints accounts + recent post counts (read-only)
"""
import json
import mimetypes
import os
import sys
import time
import urllib.request
import uuid

ROOT = os.path.expanduser("~/Documents/Claude/Projects/Refine Social Media")
CFG = json.load(open(os.path.join(ROOT, "publer_config.json")))
BASE = CFG.get("api_base", "https://app.publer.com/api/v1").rstrip("/")


def _headers(extra=None):
    h = {"Authorization": "Bearer-API " + CFG["api_key"], "accept": "application/json", "User-Agent": "ValleyPawnOps/1.0"}
    if CFG.get("workspace_id"):
        h["Publer-Workspace-Id"] = CFG["workspace_id"]
    h.update(extra or {})
    return h


def call(method, path, payload=None, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers=_headers({"content-type": "application/json"} if data else None))
    with urllib.request.urlopen(req, timeout=90) as r:
        b = r.read()
        return json.loads(b) if b else {}


def upload(path):
    bnd = uuid.uuid4().hex
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    parts = []
    for k, v in (("direct_upload", "true"), ("in_library", "true")):
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (bnd, k, v)).encode())
    parts.append(('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\nContent-Type: %s\r\n\r\n'
                  % (bnd, os.path.basename(path), ctype)).encode() + open(path, "rb").read() + b"\r\n")
    parts.append(("--%s--\r\n" % bnd).encode())
    req = urllib.request.Request(BASE + "/media", data=b"".join(parts), method="POST",
                                 headers=_headers({"content-type": "multipart/form-data; boundary=" + bnd}))
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def public_url(media):
    for k in ("path", "url", "original", "link"):
        v = media.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


def accounts():
    return json.load(open(os.path.join(ROOT, "publer_accounts.json")))["accounts"]


def job(job_id, wait=90):
    t0 = time.time()
    while time.time() - t0 < wait:
        r = call("GET", "/job_status/%s" % job_id)
        if (r.get("status") or "").lower() in ("complete", "completed", "failed", "error"):
            return r
        time.sleep(3)
    return {"status": "timeout"}


if __name__ == "__main__":
    import urllib.parse  # noqa: F401
    if sys.argv[1:] == ["probe"]:
        print(sorted(accounts().keys()))
        print(json.dumps(call("GET", "/posts", params={"state": "scheduled", "limit": "5"}))[:600])
import urllib.parse  # noqa: E402,F401
