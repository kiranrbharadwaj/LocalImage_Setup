#!/bin/zsh
set -eu
repo_dir="${0:A:h}"
cd "$repo_dir/.runtime/ComfyUI"
if [[ ! -x .venv/bin/python ]]; then
  print 'Run scripts/setup.py first.'
  exit 1
fi
if /usr/sbin/lsof -nP -iTCP:8188 -sTCP:LISTEN >/dev/null 2>&1; then
  print 'Port 8188 is already in use. Open http://127.0.0.1:8188 or stop that instance before starting another.'
  exit 1
fi
export HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1
export HF_HOME="$repo_dir/.runtime/cache/huggingface"
print 'ComfyUI will open at http://127.0.0.1:8188. Stop with Control-C.'
exec /usr/bin/sandbox-exec -f "$repo_dir/scripts/local-only.sb" .venv/bin/python main.py \
  --listen 127.0.0.1 --port 8188 --offline --disable-all-custom-nodes \
  --disable-metadata --reserve-vram 8 --bf16-text-enc --cache-none --fast-disk --preview-method none
