#!/usr/bin/env python3
"""vp_ai.py — one shared way for native agents to ask Claude for copy or structured extraction.
Key: Keychain service `vp-agent-anthropic-key` (same key the Chekkit responder uses since 9/2026).
  vp_ai.ask(prompt, system="", model=None, max_tokens=2000, content=None, local_ok=None) -> text
  vp_ai.ask_json(prompt, system="", ...) -> dict/list parsed from the first JSON value in the answer

2026-11-09 — AUTOMATIC FALLBACK (continuity plan, "IF CLAUDE GOES DOWN" guide in Drive -> Life OS):
  If the Claude call fails for ANY reason (no key, account cut off, usage cap, outage, network), a
  TEXT-ONLY request is retried on the free local engine (Ollama on this Mac, model in the config).
  Requests carrying images/documents are not retried locally (the local model has no vision) and
  raise exactly as before. Callers that publish to customers or the public are on a deny list and
  never fall back — they fail as before so a person covers them.
  Config: Valley Pawn OS/fleet/ai_fallback.json
      mode: "auto" (Claude first, local on failure — default) | "local" (skip Claude; use during an
            outage so jobs don't wait on dead calls) | "anthropic" (old behaviour, no fallback)
      deny_callers: script file names that must never use the local engine
  Every fallback is logged to ~/Library/Logs/valleypawn/vp-ai.log and fleet/state/vp_ai_engine.json.
  vp_ai.LAST_ENGINE is "anthropic" or "local" after each successful call.
  When Claude works, behaviour is byte-for-byte what it was before.
"""
import datetime
import getpass
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

API = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5-5"

OS_DIR = os.path.join(os.path.expanduser("~"), "Documents/Claude/Projects/Valley Pawn OS")
CONFIG = os.path.join(OS_DIR, "fleet/ai_fallback.json")
STATE = os.path.join(OS_DIR, "fleet/state/vp_ai_engine.json")
LOG = os.path.join(os.path.expanduser("~"), "Library/Logs/valleypawn/vp-ai.log")
DEFAULTS = {"mode": "auto", "local_url": "http://127.0.0.1:11434", "local_model": "qwen2.5:14b",
            "local_timeout_s": 600, "deny_callers": ["review_reply.py", "social_weekly.py", "comedy_weekly.py",
                                                      "chekkit_ai_responder.py"]}
LAST_ENGINE = None


def _cfg():
    c = dict(DEFAULTS)
    try:
        with open(CONFIG) as f:
            c.update(json.load(f))
    except Exception:
        pass
    return c


def _caller():
    try:
        return os.path.basename(sys.argv[0]) or "?"
    except Exception:
        return "?"


def _note(event, **kw):
    """Best effort: one log line + small state file. Never raises."""
    now = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write("%s %s caller=%s %s\n" % (now, event, _caller(),
                                              " ".join("%s=%s" % (k, str(v).replace("\n", " ")[:200]) for k, v in kw.items())))
    except Exception:
        pass
    try:
        st = {}
        try:
            with open(STATE) as f:
                st = json.load(f)
        except Exception:
            pass
        st[event] = dict(kw, at=now, caller=_caller())
        tmp = STATE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(st, f, indent=1)
        os.replace(tmp, STATE)
    except Exception:
        pass


def key():
    for extra in (["-a", getpass.getuser()], []):
        r = subprocess.run(["security", "find-generic-password", "-s", "vp-agent-anthropic-key"] + extra + ["-w"],
                           capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            return r.stdout.strip()
    raise RuntimeError("no Anthropic key in Keychain (vp-agent-anthropic-key)")


def _ask_anthropic(prompt, system, model, max_tokens, content):
    body = {"model": model or MODEL, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content if content is not None else prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": key(), "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:   # 2026-10-31: keep the API's own reason (dress code 400s were opaque)
        try:
            detail = e.read().decode("utf-8", "replace")[:400]
        except Exception:
            detail = ""
        raise RuntimeError("HTTP %s from Anthropic API: %s" % (e.code, detail)) from None
    return "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")


def _text_only(prompt, content):
    """Return the request as plain text, or None if it carries images/documents."""
    if content is None:
        return prompt
    if isinstance(content, str):
        return content
    parts = []
    for b in content if isinstance(content, list) else [content]:
        if not isinstance(b, dict) or b.get("type") != "text":
            return None
        parts.append(b.get("text", ""))
    return "\n\n".join(parts)


def _ask_local(text, system, max_tokens, cfg):
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": text}]
    body = {"model": cfg["local_model"], "messages": msgs, "stream": False,
            "options": {"num_predict": max(int(max_tokens), 16), "temperature": 0.2}}
    req = urllib.request.Request(cfg["local_url"].rstrip("/") + "/api/chat", data=json.dumps(body).encode(),
                                 method="POST", headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=cfg.get("local_timeout_s", 600)) as r:
        resp = json.load(r)
    return (resp.get("message") or {}).get("content", "")


def ask(prompt, system="", model=None, max_tokens=2000, content=None, local_ok=None):
    global LAST_ENGINE
    cfg = _cfg()
    mode = cfg.get("mode", "auto")
    allowed = (local_ok if local_ok is not None else _caller() not in cfg.get("deny_callers", [])) and mode != "anthropic"
    text = _text_only(prompt, content) if allowed else None
    err = None
    if mode != "local" or text is None:
        try:
            out = _ask_anthropic(prompt, system, model, max_tokens, content)
            LAST_ENGINE = "anthropic"
            return out
        except Exception as e:
            err = e
            if text is None:
                raise
    try:
        out = _ask_local(text, system, max_tokens, cfg)
    except Exception as le:
        _note("local_failed", reason=type(le).__name__ + " " + str(le)[:150],
              claude_error=(str(err)[:150] if err else "mode=local"))
        if err is not None:
            raise err
        raise RuntimeError("local AI engine failed: %s" % le) from None
    LAST_ENGINE = "local"
    _note("fallback", mode=mode, claude_error=(str(err)[:150] if err else "skipped (mode=local)"),
          model=cfg["local_model"])
    return out


def ask_json(prompt, system="", **kw):
    out = ask(prompt, system, **kw)
    m = re.search(r"(\{.*\}|\[.*\])", out, re.S)
    if not m:
        raise ValueError("no JSON in answer: " + out[:200])
    return json.loads(m.group(1), strict=False)


if __name__ == "__main__":   # self-test: python3 vp_ai.py --selftest [--local]
    if "--selftest" in sys.argv:
        lo = "--local" in sys.argv
        try:
            if lo:
                c = _cfg()
                print("local:", _ask_local("Reply with exactly the word OK.", "", 10, c).strip()[:40], "model=" + c["local_model"])
            else:
                print("auto:", ask("Reply with exactly the word OK.", max_tokens=10).strip()[:40], "engine=" + str(LAST_ENGINE))
        except Exception as e:
            print("FAIL", type(e).__name__, str(e)[:300])
            sys.exit(1)
