# Live Prometheus and Grafana companion

Run from the repository root with Docker Compose v2:

```sh
docker compose -p emminex-observe -f deep-dives/observability/compose.yml up -d
```

- Prometheus: http://127.0.0.1:19090. In Query, evaluate `service:slow_requests:ratio5m`.
- Grafana: http://127.0.0.1:13000/d/reliability-lab. Anonymous access is Viewer. Local admin credentials are `admin` / `local-lab-only`.
- Wait for scrapes and evaluations. The synthetic slow fraction settles near 0.02. The alert becomes firing after its expression has remained true for two minutes.
- `metrics.py` generates synthetic cumulative counters at about 100 observations per second, with about 98% in the 300ms bucket. These are generated observations, not traffic from a real checkout service and not a benchmark.
- `prometheus.yml` loads the same alert rules tested by the Prometheus unit lab. The provisioned companion dashboard adds traffic, slow-fraction, and burn-rate panels to the original self-scrape example. It retains the same dashboard and data source UIDs.

Only the two browser ports are bound to host loopback. The collector and Grafana configuration are a disposable development fixture. No Alertmanager is configured, so a firing alert does not send a notification.

Check the rules independently:

```sh
docker run --rm -v "$PWD/deep-dives/prometheus:/work:ro" -w /work \
  --entrypoint /bin/promtool prom/prometheus:v3.5.0 test rules tests.yml
```

Stop the companion and remove its local data:

```sh
docker compose -p emminex-observe -f deep-dives/observability/compose.yml down -v
```

Protocol references: [Prometheus text exposition](https://prometheus.io/docs/instrumenting/exposition_formats/), [alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/), [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/).
