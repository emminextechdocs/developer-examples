# Watch a pending RabbitMQ delivery in the management UI

From the repository root, with Docker Compose v2:

```sh
docker compose -p emminex-rabbit-ui -f deep-dives/rabbitmq/ui/compose.yml up -d
```

Open http://127.0.0.1:15674 and sign in with `lab` / `local-lab-only`. Select **Queues and Streams**, then **orders-ui**. Wait for the management statistics refresh. The helper publishes one persistent synthetic order with a publisher confirm, retrieves it with `basic_get(auto_ack=False)`, and leaves the connection open. Expected counts: Ready 0, Unacked 1. The Consumers count is 0 because this is a polling `basic_get` client, not a registered push consumer.

Stop that client:

```sh
docker compose -p emminex-rabbit-ui -f deep-dives/rabbitmq/ui/compose.yml stop consumer
```

After connection closure and a statistics refresh, expect Ready 1, Unacked 0. This shows requeueing; it does not show that another client processed or acknowledged the order. The separate `python3 deep-dives/walkthrough.py rabbitmq` test verifies redelivery and acknowledgement.

The UI is bound to host loopback. Remove the fixture when finished:

```sh
docker compose -p emminex-rabbit-ui -f deep-dives/rabbitmq/ui/compose.yml down -v
```

See [RabbitMQ's management guide](https://www.rabbitmq.com/docs/management) and [acknowledgement guide](https://www.rabbitmq.com/docs/confirms).
