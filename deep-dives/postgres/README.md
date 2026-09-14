# PostgreSQL job queues: locks, leases, and stale workers

An isolated experiment for senior developers. Tested versions: **PostgreSQL 18.6**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py postgres
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- skip locked row without claiming it
- expired lease reclaimed with new generation
- stale worker cannot complete reclaimed job
- current lease holder completes job
- server version

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [postgres/schema.sql](schema.sql)
- [postgres/claim.sql](claim.sql)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/postgres.json)
- [Technical diagram](../assets/postgres-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [sql update](https://www.postgresql.org/docs/18/sql-update.html)
- [transaction iso](https://www.postgresql.org/docs/18/transaction-iso.html)
- [indexes partial](https://www.postgresql.org/docs/18/indexes-partial.html)
- [using explain](https://www.postgresql.org/docs/18/using-explain.html)
- [routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [functions datetime](https://www.postgresql.org/docs/18/functions-datetime.html)
