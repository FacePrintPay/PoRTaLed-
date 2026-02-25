#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="$ROOT/logs"; mkdir -p "$LOGDIR"
PORT="${PORT:-8081}"
nohup python3 "$ROOT/gateway_py/main.py" >"$LOGDIR/gateway_py.out.log" 2>"$LOGDIR/gateway_py.err.log" &
echo $! > "$ROOT/run/gateway_py.pid"
echo "[OK] Python gateway on :$PORT (pid $(cat "$ROOT/run/gateway_py.pid"))"
