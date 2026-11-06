#!/usr/bin/env bash
# Usage: scripts/health-check.sh https://your.domain
set -uo pipefail
BASE="${1:?usage: health-check.sh <base-url>}"
fail=0
chk() { if curl -fsS --max-time 15 "$2" -o /tmp/hc.out && python3 -c "import json;d=json.load(open('/tmp/hc.out'));assert $3" 2>/dev/null; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }
curl -fsS --max-time 15 "$BASE/" | grep -q 'id="root"' && echo "PASS frontend" || { echo "FAIL frontend"; fail=1; }
chk health "$BASE/health" "d['status']=='ok' and d['database'] and d['redis']"
chk districts "$BASE/api/districts" "len(d)==38"
chk search "$BASE/api/crops/search?q=thakkali" "d[0]['crop']['slug']=='tomato'"
curl -sI "$BASE/" | grep -qi 'strict-transport-security\|x-content-type-options' && echo "PASS headers" || echo "WARN headers"
exit $fail
