CREATE TABLE jobs (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  state text NOT NULL DEFAULT 'ready' CHECK (state IN ('ready','running','done')),
  generation bigint NOT NULL DEFAULT 0,
  lease_until timestamptz,
  payload jsonb NOT NULL
);
CREATE INDEX jobs_ready ON jobs (id) WHERE state='ready';
CREATE INDEX jobs_expired ON jobs (lease_until, id) WHERE state='running';
INSERT INTO jobs(payload) VALUES ('{"order_id":"ord-1"}'), ('{"order_id":"ord-2"}');
