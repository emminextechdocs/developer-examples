# Test Prometheus SLO alerts before they page your team

An isolated experiment for senior developers. Tested versions: **Prometheus / promtool 3.5.0**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py prometheus
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- PromQL firing, pending, idle, missing-data, counter-reset and scrape-failure fixtures

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [prometheus/tests.yml](tests.yml)
- [prometheus/rules.yml](rules.yml)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/prometheus.json)
- [Technical diagram](../assets/prometheus-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [unit testing rules](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)
- [alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [recording rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [operators](https://prometheus.io/docs/prometheus/latest/querying/operators/)
- [histograms](https://prometheus.io/docs/practices/histograms/)
- [instrumentation](https://prometheus.io/docs/practices/instrumentation/)
- [basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
