# Docker BuildKit secrets: test image contents and cache behavior

An isolated experiment for senior developers. Tested versions: **Docker BuildKit via Docker Engine 29.7.2 in local verification; Alpine 3.22.1**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py buildkit
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- changing only the secret reuses the secret-consuming RUN step
- explicit cache epoch rebuilds artifact without secret file
- final image history contains no synthetic secret value
- uncached required-secret step fails when the secret is absent

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [buildkit/Dockerfile](Dockerfile)
- [buildkit/.dockerignore](.dockerignore)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/buildkit.json)
- [Technical diagram](../assets/buildkit-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [secrets](https://docs.docker.com/build/building/secrets/)
- [invalidation](https://docs.docker.com/build/cache/invalidation/)
- [dockerfile](https://docs.docker.com/reference/dockerfile/)
- [multi stage](https://docs.docker.com/build/building/multi-stage/)
- [context](https://docs.docker.com/build/building/context/)
- [history](https://docs.docker.com/reference/cli/docker/image/history/)
- [export](https://docs.docker.com/reference/cli/docker/container/export/)
- [best practices](https://docs.docker.com/build/building/best-practices/)
