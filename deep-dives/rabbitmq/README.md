# RabbitMQ confirms and acknowledgements under failure

An isolated experiment for senior developers. Tested versions: **RabbitMQ 4.1.4; Pika 1.3.2; Python container 3.13.7**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py rabbitmq
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- RabbitMQ confirms and redelivery

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [rabbitmq/recovery.py](recovery.py)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/rabbitmq.json)
- [Technical diagram](../assets/rabbitmq-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [confirms](https://www.rabbitmq.com/docs/confirms)
- [reliability](https://www.rabbitmq.com/docs/reliability)
- [consumer prefetch](https://www.rabbitmq.com/docs/consumer-prefetch)
- [queues](https://www.rabbitmq.com/docs/queues)
- [quorum queues](https://www.rabbitmq.com/docs/quorum-queues)
- [dlx](https://www.rabbitmq.com/docs/dlx)
- [blocking](https://pika.readthedocs.io/en/1.3.2/modules/adapters/blocking.html)
- [heartbeats](https://www.rabbitmq.com/docs/heartbeats)
