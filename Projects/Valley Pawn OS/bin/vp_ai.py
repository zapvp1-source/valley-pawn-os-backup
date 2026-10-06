#!/usr/bin/env python3
"""vp_ai.py — one shared way for native agents to ask Claude for copy or structured extraction.
Key: Keychain service `vp-agent-anthropic-key` (same key the Chekkit responder uses since 9/2026).
  vp_ai.ask(prompt, system="", model=None, max_tokens=2000) -> text
  vp_ai.ask_json(prompt, system="", ...) -> dict/list parsed from the first JSON value in the answer
"""
import getpass
import json
import re
import subprocess
import urllib.request

API = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5-5"


def key():
    for extra in (["-a", getpass.getuser()], []):
        r = subprocess.run(["security", "find-generic-password", "-s", "vp-agent-anthropic-key"] + extra + ["-w"],
                           capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            return r.stdout.strip()
    raise RuntimeError("no Anthropic key in Keychain (vp-agent-anthropic-key)")


def ask(prompt, system="", model=None, max_tokens=2000, content=None):
    body = {"model": model or MODEL, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content if content is not None else prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": key(), "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    return "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")


def ask_json(prompt, system="", **kw):
    out = ask(prompt, system, **kw)
    m = re.search(r"(\{.*\}|\[.*\])", out, re.S)
    if not m:
        raise ValueError("no JSON in answer: " + out[:200])
    return json.loads(m.group(1), strict=False)
