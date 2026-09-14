# Kubernetes graceful shutdown: test draining under deletion

An isolated experiment for senior developers. Tested versions: **Kubernetes 1.34.0; kind 0.30.0; kubectl 1.34.0; Python container 3.13.7**. These are explicit lab versions, not a claim to use the latest releases.

## Run

From the repository root, with Python 3.11+ and a running Docker engine:

```sh
python3 deep-dives/lab.py kubernetes
```

Install kind 0.30.0 and kubectl 1.34.x first. Set `KIND=/path/to/kind` if needed. The runner creates a uniquely named cluster and uses an explicit temporary kubeconfig. It never changes your current context.

First execution downloads container images. RabbitMQ also installs Pika 1.3.2 into its disposable client container. Run labs sequentially on a workstation with limited memory. Grafana, NGINX, and OTLP publish dynamically allocated host ports bound to `127.0.0.1`. Kubernetes also creates a local kind API endpoint and a loopback Pod port-forward.

## Verified behavior

- EndpointSlice observed during deletion
- in-flight request completes during graceful deletion
- application lifecycle logs

Assertions raise an error on failure. Do not run Python with `-O`, which disables assertions. Evidence is written even for a failed run; inspect its `passed` field. A saved prior passing report is not proof that your current run passed.

## Files

- [kubernetes/pod.yml](pod.yml)
- [kubernetes/app.py](app.py)
- [Shared executable harness](../lab.py)
- [Recorded execution evidence](../evidence/kubernetes.json)
- [Technical diagram](../assets/kubernetes-flow.svg)

## Limits and cleanup

The experiment tests the named behavior, not production readiness, availability, throughput, or exactly-once external effects. Containers use synthetic data and disposable fixture credentials. Never substitute production credentials or target a shared service. The runner removes containers and their anonymous volumes, temporary files, and its dedicated network or kind cluster in `finally` blocks. BuildKit removes its uniquely tagged final image; it does not prune your shared builder cache. A forcibly killed harness may require removing its remaining `emminex-dd-` resources individually after inspecting them. Do not run broad Docker prune commands.

## Official references

- [pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [configure liveness readiness startup probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [endpoint slices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [force delete stateful set pod](https://kubernetes.io/docs/tasks/run-application/force-delete-stateful-set-pod/)
- [quick start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [socketserver](https://docs.python.org/3.13/library/socketserver.html)
- [signal](https://docs.python.org/3.13/library/signal.html)
