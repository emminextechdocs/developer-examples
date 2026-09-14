# Kafka offset commits: reproduce replay and control progress

An isolated experiment for senior developers. Tested versions: **Apache Kafka 4.1.0; Eclipse Temurin JDK 21.0.8+9**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py kafka
```

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- Kafka offset replay and committed resume

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [kafka/Replay.java](Replay.java)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/kafka.json)
- [Technical diagram](../assets/kafka-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [quickstart](https://kafka.apache.org/41/getting-started/quickstart/)
- [KafkaConsumer](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)
- [OffsetAndMetadata](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/OffsetAndMetadata.html)
- [consumer configs](https://kafka.apache.org/41/configuration/consumer-configs/)
- [producer configs](https://kafka.apache.org/41/configuration/producer-configs/)
- [design](https://kafka.apache.org/41/design/design/)
- [basic kafka operations](https://kafka.apache.org/41/operations/basic-kafka-operations/)
- [KafkaProducer](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)
