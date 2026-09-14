# NGINX upstream retries: recover reads without replaying writes

An isolated experiment for senior developers. Tested versions: **NGINX 1.28.0; Python container 3.13.7**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py nginx
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- GET retried after primary 503 and succeeded at backup
- POST applied by primary then returned 503 without proxy retry
- upstream attempts captured in access log

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [nginx/backend.py](backend.py)
- [nginx/nginx.conf](nginx.conf)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/nginx.json)
- [Technical diagram](../assets/nginx-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [ngx http proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [ngx http upstream module](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)
- [ngx http log module](https://nginx.org/en/docs/http/ngx_http_log_module.html)
- [ngx http core module](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [control](https://nginx.org/en/docs/control.html)
- [rfc9110](https://www.rfc-editor.org/rfc/rfc9110.html)
- [beginners guide](https://nginx.org/en/docs/beginners_guide.html)
- [http.server](https://docs.python.org/3.13/library/http.server.html)
