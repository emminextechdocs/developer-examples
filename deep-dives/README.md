# Senior developer deep dives

Ten runnable, isolated experiments with failure assertions, recorded evidence, and editable technical diagrams. The accompanying tutorials are published under Emmanuel Oyibo’s byline at [Emminex Techdocs](https://emminextechdocs.com/blog).

## Experiments

| Lab | Question |
| --- | --- |
| [postgres](postgres/README.md) | PostgreSQL job queues: locks, leases, and stale workers |
| [redis](redis/README.md) | Redis Streams: recover pending work without losing ownership |
| [kafka](kafka/README.md) | Kafka offset commits: reproduce replay and control progress |
| [rabbitmq](rabbitmq/README.md) | RabbitMQ confirms and acknowledgements under failure |
| [prometheus](prometheus/README.md) | Test Prometheus SLO alerts before they page your team |
| [grafana](grafana/README.md) | Grafana provisioning: test ownership and configuration drift |
| [nginx](nginx/README.md) | NGINX upstream retries: recover reads without replaying writes |
| [otel](otel/README.md) | OpenTelemetry redaction: test what still leaves the Collector |
| [buildkit](buildkit/README.md) | Docker BuildKit secrets: test image contents and cache behavior |
| [kubernetes](kubernetes/README.md) | Kubernetes graceful shutdown: test draining under deletion |

## Prerequisites and execution

Python 3.11+, Docker, and network access for pinned-version images. Kubernetes additionally needs kind 0.30.0 and kubectl 1.34.x. The Python scripts use the standard library on the host. Read each lab’s README before running it.

```sh
python3 deep-dives/walkthrough.py postgres
```

Run one lab at a time on a memory-constrained workstation. These tests create disposable infrastructure; they never target an existing database, cluster context, or production endpoint. Do not run with `python -O`. The code intentionally contains synthetic credentials and incomplete configurations used as negative-test fixtures; their article and test context explain the boundary being demonstrated.

## Interactive walkthroughs

`walkthrough.py` runs the same assertions as `lab.py` and prints selected executed commands and responses. It does not replay saved results. Its optional `--hold 30` leaves the completed terminal visible for a capture; it does not retain the lab containers.

- [PostgreSQL manual sequence](postgres/manual.sh): `bash deep-dives/postgres/manual.sh`.
- [Redis manual sequence](redis/manual.sh): `bash deep-dives/redis/manual.sh`.
- [Live Prometheus and Grafana](observability/README.md): synthetic metrics and a provisioned dashboard, with browser URLs and cleanup commands.
- [RabbitMQ management UI](rabbitmq/ui/README.md): inspect Unacked → Ready after the client connection closes.

The manual database scripts also expose `session.sh` helpers for the command-by-command article paths. Source them inside a fresh Bash session from the repository root; exiting that session removes its container.

## Evidence and screenshots

`evidence/<lab>.json` records real commands, responses, assertions, and a passing flag. Values and timings are from the recorded run, not a benchmark. The editable SVGs illustrate the tested semantics. Browser screenshots of execution reports are clearly labelled as reports, not product interfaces. The Grafana dashboard image is a screenshot of the running product.

To regenerate report screenshots after passing all ten labs:

```sh
npm ci --prefix deep-dives
npx --prefix deep-dives playwright install chromium
node deep-dives/render.mjs
```

Alternatively set `CHROME_EXECUTABLE` to a local Chromium/Chrome executable. To capture the live Grafana view while its test runs, set `CAPTURE_SCREENSHOTS=1` and the same browser configuration before running that lab. Screenshots are captured at 2x device scale.

## Verification scope

Local experiments verify specific behaviors on the documented versions. They do not establish production availability, complete privacy compliance, arbitrary crash safety, or universal performance. Every lab has cleanup, bounded waits, and an independently inspectable assertion record. Official sources and article review notes remain distinct from experimental results.
