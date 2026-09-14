#!/usr/bin/env bash
# Source from the repository root in Bash. Every database belongs to this invocation.
set -euo pipefail
pg_lab="emminex-pg-manual-$$"
trap 'docker rm -f -v "$pg_lab" >/dev/null 2>&1 || true' EXIT
docker run -d --name "$pg_lab" -e POSTGRES_PASSWORD=local-lab-only postgres:18.6 >/dev/null
psql_lab() {
  docker exec -i -e PGPASSWORD=local-lab-only "$pg_lab" \
    psql -h 127.0.0.1 -U postgres -d postgres -v ON_ERROR_STOP=1 -Atq "$@"
}
ready=false
for attempt in {1..60}; do
  if psql_lab -c 'SELECT 1;' >/dev/null 2>&1; then ready=true; break; fi
  sleep 1
done
"$ready" || { echo 'PostgreSQL did not become ready' >&2; exit 1; }
