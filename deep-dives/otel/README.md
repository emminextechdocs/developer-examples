# OpenTelemetry redaction: test what still leaves the Collector

An isolated experiment for senior developers. Tested versions: **OpenTelemetry Collector Contrib 0.133.0**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py otel
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- configured span and resource attributes removed before export
- boundary test: span-event attribute survives the first pipeline
- explicit span-event transform removes the tested leak

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [otel/request.json](request.json)
- [otel/collector-events.yml](collector-events.yml)
- [otel/collector.yml](collector.yml)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/otel.json)
- [Technical diagram](../assets/otel-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [configuration](https://opentelemetry.io/docs/collector/configuration/)
- [handling sensitive data](https://opentelemetry.io/docs/security/handling-sensitive-data/)
- [transforming telemetry](https://opentelemetry.io/docs/collector/transforming-telemetry/)
- [otlp](https://opentelemetry.io/docs/specs/otlp/)
- [traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [attributesprocessor](https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector-contrib/v0.133.0/processor/attributesprocessor/README.md)
- [resourceprocessor](https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector-contrib/v0.133.0/processor/resourceprocessor/README.md)
- [fileexporter](https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector-contrib/v0.133.0/exporter/fileexporter/README.md)

- [Transform processor 0.133.0](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/v0.133.0/processor/transformprocessor/README.md)
