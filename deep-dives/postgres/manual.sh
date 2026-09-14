#!/usr/bin/env bash
# Run the complete sequence with assertions and automatic cleanup.
source deep-dives/postgres/session.sh
psql_lab < deep-dives/postgres/schema.sql
echo '1. Hold job 1 in a separate transaction'
psql_lab -c "SET application_name='manual-locker'; BEGIN; SELECT id FROM jobs WHERE id=1 FOR UPDATE; SELECT pg_sleep(5); ROLLBACK;" >/dev/null &
locker=$!
locked=false
for attempt in {1..50}; do
  if [ "$(psql_lab -c "SELECT count(*) FROM pg_stat_activity WHERE application_name='manual-locker' AND wait_event='PgSleep';")" = 1 ]; then locked=true; break; fi
  sleep 0.1
done
"$locked" || { echo 'Lock holder did not reach its wait' >&2; exit 1; }
claim=$(psql_lab < deep-dives/postgres/claim.sql)
echo "Claim while job 1 is locked: $claim"
[ "$claim" = '2|1' ]
wait "$locker"
claim=$(psql_lab < deep-dives/postgres/claim.sql)
echo "2. Claim after rollback: $claim"
[ "$claim" = '1|1' ]
psql_lab -c "UPDATE jobs SET lease_until=clock_timestamp()-interval '1 second' WHERE id=1;"
claim=$(psql_lab < deep-dives/postgres/claim.sql)
echo "3. Reclaim after forced expiry: $claim"
[ "$claim" = '1|2' ]
for generation in 1 2; do
  changed=$(psql_lab -c "WITH completed AS (UPDATE jobs SET state='done' WHERE id=1 AND state='running' AND generation=$generation AND lease_until>clock_timestamp() RETURNING id) SELECT count(*) FROM completed;")
  echo "Completion with generation $generation: $changed row(s)"
  [ "$changed" = "$((generation - 1))" ]
done
echo 'PASS: skipped lock, reclaimed lease, rejected stale completion'
