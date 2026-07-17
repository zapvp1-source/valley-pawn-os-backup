#!/usr/bin/env python3
"""
vp-agent — Valley Pawn's local, model-agnostic AI agent runner.

PURPOSE
    Redundancy layer for the Claude/Cowork automation stack. If Claude is
    unavailable (outage, terms change, discontinued), this runner executes the
    same SKILL.md playbooks under /Users/joshuadavis/Documents/Claude/Scheduled/
    using ANY configured LLM engine:
        - "anthropic"  : Anthropic API (native /v1/messages)
        - "openai"     : OpenAI API (or any OpenAI-compatible endpoint)
        - "ollama"     : Local model on this Mac via Ollama (zero-vendor mode)

    Zero third-party dependencies — pure Python stdlib — so it runs on the
    stock macOS python3 forever, with nothing to break or re-install.

USAGE
    python3 vp_agent.py --skill /path/to/SKILL.md            # run a playbook
    python3 vp_agent.py --skill ... --engine ollama           # override engine
    python3 vp_agent.py --prompt "one-off instruction"        # ad-hoc task
    python3 vp_agent.py --selftest                            # check engines

CONFIG
    config.json next to this file. API keys are NEVER stored in config —
    they're read at runtime from macOS Keychain:
        security find-generic-password -s vp-agent-anthropic-key -w
        security find-generic-password -s vp-agent-openai-key -w
    (Ollama needs no key — it's local.)

SECURITY MODEL
    - The agent can run shell commands as your user, same as Claude's
      osascript bridge does today. Every command and its output is logged to
      logs/<task>_<timestamp>.log for a full audit trail.
    - Iteration cap + per-command timeout prevent runaway loops.
    - Keys live only in Keychain; this file and config.json are safe to back
      up to GitHub.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")

DEFAULT_CONFIG = {
    "engine": "anthropic",
    "engines": {
        "anthropic": {
            "endpoint": "https://api.anthropic.com/v1/messages",
            "model": "claude-sonnet-4-5",
            "keychain_service": "vp-agent-anthropic-key",
            "max_tokens": 4096
        },
        "openai": {
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-4o",
            "keychain_service": "vp-agent-openai-key",
            "max_tokens": 4096
        },
        "ollama": {
            "endpoint": "http://localhost:11434/v1/chat/completions",
            "model": "qwen2.5:14b",
            "keychain_service": None,
            "max_tokens": 4096
        }
    },
    "max_iterations": 40,
    "shell_timeout_seconds": 300
}

SYSTEM_PROMPT = """You are vp-agent, an autonomous task runner for Full Circle Finance Inc / Valley Pawn, \
running locally on Joshua's Mac Studio. You execute business automation playbooks (SKILL.md files) end to end \
without asking questions — no one is watching.

You have these tools. To use one, reply with ONLY a JSON object (no other text, no markdown fences):
  {"tool": "shell", "command": "<bash command>"}          — run a shell command (macOS, your user account)
  {"tool": "read_file", "path": "<absolute path>"}         — read a text file
  {"tool": "write_file", "path": "<absolute path>", "content": "<content>"}  — write a text file
  {"tool": "done", "summary": "<what you accomplished or why you stopped>"}  — REQUIRED final call

Rules:
- One tool call per reply. After each call you'll get the result and can decide the next step.
- Follow the playbook exactly. Never invent data. If truly blocked, call done with a clear explanation.
- Never print secrets/API keys in your replies. Retrieve them inline in shell commands only.
- Keep going until the task is finished or genuinely blocked, then call done."""


def log_path_for(task_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", task_name)[:60]
    return os.path.join(LOG_DIR, f"{safe}_{stamp}.log")


class Logger:
    def __init__(self, path):
        self.path = path
        self.fh = open(path, "a")

    def log(self, tag, msg):
        line = f"{datetime.datetime.utcnow().isoformat()}Z [{tag}] {msg}"
        self.fh.write(line + "\n")
        self.fh.flush()
        print(line[:400])


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    with open(CONFIG_PATH, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    return dict(DEFAULT_CONFIG)


def keychain_secret(service):
    if not service:
        return None
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


# ---------------- LLM adapters ----------------

def call_anthropic(cfg, messages, system):
    key = keychain_secret(cfg.get("keychain_service"))
    if not key:
        raise RuntimeError(f"No API key in Keychain service '{cfg.get('keychain_service')}'")
    body = {
        "model": cfg["model"],
        "max_tokens": cfg.get("max_tokens", 4096),
        "system": system,
        "messages": messages,
    }
    req = urllib.request.Request(
        cfg["endpoint"],
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)
    parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    return "".join(parts)


def call_openai_compat(cfg, messages, system):
    key = keychain_secret(cfg.get("keychain_service"))
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = {
        "model": cfg["model"],
        "max_tokens": cfg.get("max_tokens", 4096),
        "messages": [{"role": "system", "content": system}] + messages,
    }
    req = urllib.request.Request(cfg["endpoint"], data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"]


def call_llm(engine_name, engine_cfg, messages, system):
    if engine_name == "anthropic":
        return call_anthropic(engine_cfg, messages, system)
    return call_openai_compat(engine_cfg, messages, system)


# ---------------- tool execution ----------------

def parse_tool_call(text):
    """Extract the first JSON object from the model's reply."""
    text = text.strip()
    # strip markdown fences if the model added them anyway
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    # find first { ... } balanced block
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def execute_tool(call, config, logger):
    tool = call.get("tool")
    if tool == "shell":
        cmd = call.get("command", "")
        logger.log("SHELL", cmd)
        try:
            out = subprocess.run(
                ["/bin/bash", "-c", cmd],
                capture_output=True, text=True,
                timeout=config.get("shell_timeout_seconds", 300),
            )
            result = f"exit={out.returncode}\nstdout:\n{out.stdout[-6000:]}\nstderr:\n{out.stderr[-2000:]}"
        except subprocess.TimeoutExpired:
            result = "ERROR: command timed out"
        logger.log("RESULT", result[:1000])
        return result
    if tool == "read_file":
        path = call.get("path", "")
        logger.log("READ", path)
        try:
            with open(path, errors="replace") as f:
                content = f.read()
            return content[:20000] + ("\n...[truncated]" if len(content) > 20000 else "")
        except Exception as e:
            return f"ERROR: {e}"
    if tool == "write_file":
        path = call.get("path", "")
        logger.log("WRITE", path)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(call.get("content", ""))
            return f"OK: wrote {len(call.get('content', ''))} bytes to {path}"
        except Exception as e:
            return f"ERROR: {e}"
    return f"ERROR: unknown tool '{tool}'"


# ---------------- agent loop ----------------

def run_task(instructions, task_name, engine_override=None):
    config = load_config()
    engine_name = engine_override or config["engine"]
    engine_cfg = config["engines"][engine_name]
    logger = Logger(log_path_for(task_name))
    logger.log("START", f"task={task_name} engine={engine_name} model={engine_cfg['model']}")

    messages = [{"role": "user", "content": f"TASK PLAYBOOK (execute end to end):\n\n{instructions}"}]

    for i in range(config.get("max_iterations", 40)):
        try:
            reply = call_llm(engine_name, engine_cfg, messages, SYSTEM_PROMPT)
        except Exception as e:
            logger.log("FATAL", f"LLM call failed: {e}")
            return 1
        messages.append({"role": "assistant", "content": reply})
        call = parse_tool_call(reply)
        if call is None:
            messages.append({"role": "user", "content":
                "Your reply contained no valid tool-call JSON. Reply with ONLY one JSON object using the tools defined."})
            continue
        if call.get("tool") == "done":
            logger.log("DONE", call.get("summary", ""))
            print(f"\n=== TASK COMPLETE ===\n{call.get('summary', '')}")
            return 0
        result = execute_tool(call, config, logger)
        messages.append({"role": "user", "content": f"TOOL RESULT:\n{result}"})

    logger.log("FATAL", "hit max_iterations without done()")
    return 1


def selftest():
    config = load_config()
    print(f"Default engine: {config['engine']}")
    for name, cfg in config["engines"].items():
        status = []
        if cfg.get("keychain_service"):
            status.append("key: " + ("FOUND" if keychain_secret(cfg["keychain_service"]) else "MISSING"))
        else:
            status.append("key: not needed")
        # reachability
        try:
            probe = cfg["endpoint"].rsplit("/", 2)[0]
            urllib.request.urlopen(probe, timeout=5)
            status.append("endpoint: reachable")
        except urllib.error.HTTPError:
            status.append("endpoint: reachable")
        except Exception as e:
            status.append(f"endpoint: UNREACHABLE ({type(e).__name__})")
        print(f"  {name:10s} model={cfg['model']:24s} {' | '.join(status)}")


def main():
    ap = argparse.ArgumentParser(description="vp-agent — local model-agnostic task runner")
    ap.add_argument("--skill", help="path to SKILL.md playbook")
    ap.add_argument("--prompt", help="ad-hoc instruction instead of a skill file")
    ap.add_argument("--engine", help="override engine: anthropic | openai | ollama")
    ap.add_argument("--selftest", action="store_true", help="check engine config/keys/reachability")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return 0
    if args.skill:
        with open(args.skill) as f:
            instructions = f.read()
        task_name = os.path.basename(os.path.dirname(os.path.abspath(args.skill))) or "skill"
        return run_task(instructions, task_name, args.engine)
    if args.prompt:
        return run_task(args.prompt, "adhoc", args.engine)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
