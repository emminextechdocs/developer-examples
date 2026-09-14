# Redis Streams: recover pending work without losing ownership

An isolated experiment for senior developers. Tested versions: **Redis 8.2.1**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py redis
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- first delivery assigned to worker-a
- new-message read does not recover pending work
- pending entry survives clean AOF-backed restart
- worker-b claims the same event
- ack clears pending state without deleting stream entry

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/redis.json)
- [Technical diagram](../assets/redis-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [xreadgroup](https://redis.io/docs/latest/commands/xreadgroup/)
- [xautoclaim](https://redis.io/docs/latest/commands/xautoclaim/)
- [xack](https://redis.io/docs/latest/commands/xack/)
- [xpending](https://redis.io/docs/latest/commands/xpending/)
- [xgroup create](https://redis.io/docs/latest/commands/xgroup-create/)
- [xtrim](https://redis.io/docs/latest/commands/xtrim/)
- [persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
