#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for n in api worker web; do
  if [ -f "$ROOT/.run/$n.pid" ]; then
    pid=$(cat "$ROOT/.run/$n.pid"); pkill -P "$pid" 2>/dev/null; kill "$pid" 2>/dev/null && echo "stopped $n"
    rm -f "$ROOT/.run/$n.pid"
  fi
done
exit 0
