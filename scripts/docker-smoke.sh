#!/usr/bin/env bash
# Smoke test for the local Docker stack (docker-compose.yml + docker-compose.local.yml).
# Usage: scripts/docker-smoke.sh [base_url]   (default http://localhost:8088)
set -uo pipefail
cd "$(dirname "$0")/.."
BASE="${1:-http://localhost:8088}"
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.local.yml)
fail=0
check() { # name, command...
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "PASS  $name"; else echo "FAIL  $name"; fail=1; fi
}
json_has() { curl -fsS "$1" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if ($2) else 1)"; }

echo "== containers healthy"
for s in db redis api worker web traefik; do
  st=$("${COMPOSE[@]}" ps --format '{{.Health}}' "$s" 2>/dev/null | head -1)
  [ "$st" = "healthy" ] && echo "PASS  $s healthy" || { echo "FAIL  $s health='$st'"; fail=1; }
done

echo "== connectivity through Traefik"
check "frontend index"        bash -c "curl -fsS $BASE/ | grep -q '<div id=\"root\">'"
check "SPA fallback route"    bash -c "curl -fsS $BASE/crops/1 | grep -q '<div id=\"root\">'"
check "health"                json_has "$BASE/health" "d['status']=='ok' and d['database'] and d['redis']"
check "38 districts"          json_has "$BASE/api/districts" "len(d)==38"
check "tamil search"          json_has "$BASE/api/crops/search?q=%E0%AE%A4%E0%AE%95%E0%AF%8D%E0%AE%95%E0%AE%BE%E0%AE%B3%E0%AE%BF" "d[0]['crop']['slug']=='tomato'"
check "thanglish search"      json_has "$BASE/api/crops/search?q=thakkali" "d[0]['crop']['slug']=='tomato'"
check "security headers"      bash -c "curl -sI $BASE/ | grep -qi 'x-content-type-options: nosniff'"
check "CSP header"            bash -c "curl -sI $BASE/ | grep -qi 'content-security-policy'"

echo "== db/redis not exposed"
check "db has no published port"    bash -c "! docker port \$(${COMPOSE[*]} ps -q db) | grep -q ."
check "redis has no published port" bash -c "! docker port \$(${COMPOSE[*]} ps -q redis) | grep -q ."
check "db not reachable on host"    bash -c "! (echo > /dev/tcp/127.0.0.1/5433) 2>/dev/null"

echo "== research job via worker (no API keys => graceful failure)"
JOB=$(curl -fsS -X POST "$BASE/api/research" -H 'content-type: application/json' -d '{"crop":"Okra","district":"Namakkal","month":6}' | python3 -c "import sys,json; print(json.load(sys.stdin)['job']['id'])")
sleep 5
check "worker processed job"  json_has "$BASE/api/research/jobs/$JOB" "d['status'] in ('failed','budget_exhausted','insufficient','completed','review_required')"

echo "== persistence across restart"
"${COMPOSE[@]}" restart db redis api worker >/dev/null 2>&1
for i in $(seq 1 45); do
  n=$("${COMPOSE[@]}" ps --format '{{.Health}}' db redis api worker 2>/dev/null | grep -c '^healthy$')
  [ "$n" = "4" ] && curl -fsS "$BASE/api/districts" >/dev/null 2>&1 && break
  sleep 2
done
check "districts survive restart" json_has "$BASE/api/districts" "len(d)==38"
check "job survives restart"      json_has "$BASE/api/research/jobs/$JOB" "d['id']=='$JOB'"

[ $fail -eq 0 ] && echo "ALL DOCKER SMOKE CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
