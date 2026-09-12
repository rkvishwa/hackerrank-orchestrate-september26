#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-https://financeagent.knurdz.org}"
EXPECTED_IP="${EXPECTED_IP:-20.40.49.59}"
DOMAIN="${DOMAIN:-financeagent.knurdz.org}"
API_KEY="${API_KEY:-change-me}"

resolved="$(getent hosts "$DOMAIN" | awk '{print $1; exit}')"
[[ "$resolved" == "$EXPECTED_IP" ]] || { echo "DNS mismatch"; exit 1; }

curl -fsS "$BASE_URL/health" | grep -q ok
curl -fsS "$BASE_URL/ready" >/dev/null
curl -fsS -X POST "$BASE_URL/v1/decisions" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"request_id":"request_26","sync":true}' >/dev/null
echo "Live smoke checks passed"
