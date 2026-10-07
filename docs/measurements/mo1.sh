#!/usr/bin/env bash
# MO-1: time the count endpoint. 1 warm-up call, then 5 timed calls.
# Logs in once and uses a token, same as the browser page does.
# Usage: ./mo1.sh <task_id> [query]   e.g. ./mo1.sh 2 "?group_by=shape_type"

TASK_ID=${1:-2}
QUERY=${2:-}
URL="http://localhost:8080/api/test/tasks/${TASK_ID}/annotation-counts${QUERY}"

TOKEN=$(curl -s -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"Admin12345"}' \
    http://localhost:8080/api/auth/login | python -c "import sys, json; print(json.load(sys.stdin)['key'])")

echo "URL: $URL"
echo "Date: $(date)"
curl -s -o /dev/null -H "Authorization: Token $TOKEN" "$URL"
for run in 1 2 3 4 5; do
    curl -s -o /dev/null -H "Authorization: Token $TOKEN" -w "run $run: %{http_code} %{time_total}s\n" "$URL"
done
