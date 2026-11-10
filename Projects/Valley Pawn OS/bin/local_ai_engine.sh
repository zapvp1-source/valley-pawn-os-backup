#!/bin/bash
# local_ai_engine.sh status|ensure  (2026-11-09, continuity plan)
# The free local AI engine (Ollama) that bin/vp_ai.py falls back to when Claude is unavailable.
#   status  read-only: binary, service, model store, installed models, does it answer
#   ensure  make it run at login and have the model in fleet/ai_fallback.json: brew install if the
#           binary is missing, `brew services start ollama`, `ollama pull <model>` if missing. Idempotent.
MODE="${1:-status}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
MODEL=$(/usr/bin/python3 -c "import json;print(json.load(open('$OS/fleet/ai_fallback.json')).get('local_model','qwen2.5:14b'))" 2>/dev/null || echo qwen2.5:14b)
echo "model wanted: $MODEL"
echo "binary: $(command -v ollama || echo MISSING)"
echo "brew: $(command -v brew || echo MISSING)"
brew services list 2>/dev/null | grep -i ollama || echo "brew service: not listed"
echo "model store: $(du -sh "$HOME/.ollama/models" 2>/dev/null | cut -f1 || echo none)"
answers() { curl -s -m 5 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; }
if [ "$MODE" = "ensure" ]; then
  if ! command -v ollama >/dev/null 2>&1; then echo "installing ollama via brew"; brew install ollama 2>&1 | tail -5; fi
  brew services start ollama 2>&1 | tail -3
  for i in $(seq 1 30); do answers && break; sleep 2; done
  if answers && ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$MODEL"; then
    echo "pulling $MODEL (one time, free download)"; ollama pull "$MODEL" 2>&1 | tail -3
  fi
fi
if answers; then echo "engine: ANSWERING"; ollama list 2>/dev/null; else echo "engine: NOT ANSWERING"; fi
exit 0
