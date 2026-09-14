WITH candidate AS (
  SELECT id FROM jobs
  WHERE state='ready' OR (state='running' AND lease_until<clock_timestamp())
  ORDER BY id
  FOR UPDATE SKIP LOCKED
  LIMIT 1
)
UPDATE jobs AS j
SET state='running', generation=j.generation+1,
    lease_until=clock_timestamp()+interval '30 seconds'
FROM candidate
WHERE j.id=candidate.id
RETURNING j.id,j.generation;
