#!/usr/bin/env bash
# Source from the repository root in Bash. No Redis port is published.
set -euo pipefail
redis_lab="emminex-redis-manual-$$"
trap 'docker rm -f -v "$redis_lab" >/dev/null 2>&1 || true' EXIT
docker run -d --name "$redis_lab" redis:8.2.1 \
  redis-server --appendonly yes --appendfsync always >/dev/null
redis_lab_cli() { docker exec "$redis_lab" redis-cli --raw "$@"; }
wait_redis() {
  for attempt in {1..60}; do
    if [ "$(redis_lab_cli PING 2>/dev/null || true)" = PONG ]; then return; fi
    sleep 1
  done
  echo 'Redis did not become ready' >&2; return 1
}
wait_redis
