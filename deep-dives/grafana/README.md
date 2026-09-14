# Grafana provisioning: test ownership and configuration drift

An isolated experiment for senior developers. Tested versions: **Grafana 12.1.1; Prometheus 3.5.0**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py grafana
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- dashboard and healthy datasource provisioned with stable UIDs
- API cannot overwrite file-owned dashboard
- file update applied without changing dashboard UID

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [grafana/dashboard.json](dashboard.json)
- [grafana/prometheus.yml](prometheus.yml)
- [grafana/provisioning/datasources/prometheus.yml](provisioning/datasources/prometheus.yml)
- [grafana/provisioning/dashboards/provider.yml](provisioning/dashboards/provider.yml)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/grafana.json)
- [Technical diagram](../assets/grafana-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [dashboard](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/dashboard/)
- [data source](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/data_source/)
- [configuration](https://grafana.com/docs/grafana/latest/administration/configuration/)
- [configure](https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/)
- [view dashboard json model](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/)
- [anonymous auth](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/anonymous-auth/)
- [roles and permissions](https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/)
