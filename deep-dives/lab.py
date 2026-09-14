#!/usr/bin/env python3
"""Run isolated, executable documentation experiments. Requires Python 3.11+ and Docker."""
import contextlib
import argparse
import datetime
import json
import pathlib
import subprocess
import sys
import time
import uuid
import urllib.request
import urllib.error
import tempfile
import shutil
import base64
import tarfile
import io
import os
import concurrent.futures
import re

ROOT = pathlib.Path(__file__).resolve().parent
EVENTS = []


def run(*args, input=None, check=True, timeout=180):
    result = subprocess.run(args, input=input, text=True, capture_output=True, timeout=timeout)
    EVENTS.append({"command": list(args), "stdout": result.stdout, "stderr": result.stderr, "exit": result.returncode})
    if check and result.returncode:
        raise RuntimeError(f"{args}: {result.stderr}\n{result.stdout}")
    return result.stdout.strip()


def wait_until(fn, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = fn()
            if value:
                return value
        except (RuntimeError, ValueError, OSError):
            pass
        time.sleep(0.25)
    raise TimeoutError("Condition did not become true before the deadline")


def record(name, actual):
    print(f"PASS {name}: {actual}", flush=True)
    EVENTS.append({"assertion": name, "actual": actual})


@contextlib.contextmanager
def container(image, *options, command=()):
    name = "emminex-dd-" + uuid.uuid4().hex[:10]
    try:
        run("docker", "run", "-d", "--name", name, *options, image, *command)
        yield name
    except BaseException:
        run("docker", "logs", "--tail", "50", name, check=False)
        raise
    finally:
        run("docker", "rm", "-f", "-v", name, check=False)


def postgres():
    image = "postgres:18.6-alpine"
    with container(image, "-e", "POSTGRES_PASSWORD=local-lab-only") as c:
        def sql(text):
            return run("docker", "exec", "-e", "PGPASSWORD=local-lab-only", "-i", c, "psql", "-h", "127.0.0.1", "-U", "postgres", "-XqAt", "-v", "ON_ERROR_STOP=1", input=text)
        # The image's temporary initialization server accepts Unix sockets only.
        # TCP readiness waits for the final server, after initialization finishes.
        wait_until(lambda: sql("SELECT 1;") == "1")
        sql((ROOT / "postgres/schema.sql").read_text())
        locker = subprocess.Popen(["docker", "exec", c, "psql", "-U", "postgres", "-XAt", "-c",
            "SET application_name='dd-locker'; BEGIN; SELECT id FROM jobs WHERE id=1 FOR UPDATE; SELECT pg_sleep(5); ROLLBACK;"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            wait_until(lambda: sql("SELECT count(*) FROM pg_stat_activity WHERE application_name='dd-locker' AND wait_event='PgSleep';") == "1")
            claimed = sql((ROOT / "postgres/claim.sql").read_text())
            assert claimed == "2|1", claimed
            record("skip locked row without claiming it", claimed)
            out, err = locker.communicate(timeout=15)
            assert locker.returncode == 0, err
            EVENTS.append({"concurrent_locker_stdout": out})
        finally:
            if locker.poll() is None:
                locker.terminate()
                locker.wait(timeout=10)
        assert sql((ROOT / "postgres/claim.sql").read_text()) == "1|1"
        sql("UPDATE jobs SET lease_until=clock_timestamp()-interval '1 second' WHERE id=1;")
        reclaimed = sql((ROOT / "postgres/claim.sql").read_text())
        assert reclaimed == "1|2", reclaimed
        record("expired lease reclaimed with new generation", reclaimed)
        stale = sql("WITH done AS (UPDATE jobs SET state='done' WHERE id=1 AND generation=1 AND state='running' RETURNING id) SELECT count(*) FROM done;")
        assert stale == "0"
        record("stale worker cannot complete reclaimed job", stale)
        current = sql("WITH done AS (UPDATE jobs SET state='done' WHERE id=1 AND generation=2 AND state='running' AND lease_until>clock_timestamp() RETURNING id) SELECT count(*) FROM done;")
        assert current == "1"
        record("current lease holder completes job", current)
        record("server version", sql("SHOW server_version;"))


def redis():
    with container("redis:8.2.1-alpine", command=("redis-server", "--appendonly", "yes", "--appendfsync", "always")) as c:
        def cli(*args):
            return run("docker", "exec", c, "redis-cli", "--json", *map(str, args))
        wait_until(lambda: cli("PING") == '"PONG"')
        cli("XGROUP", "CREATE", "orders", "workers", "0", "MKSTREAM")
        event = json.loads(cli("XADD", "orders", "*", "order_id", "ord-42"))
        first = json.loads(cli("XREADGROUP", "GROUP", "workers", "worker-a", "COUNT", "1", "STREAMS", "orders", ">"))
        assert event in json.dumps(first)
        record("first delivery assigned to worker-a", event)
        assert json.loads(cli("XREADGROUP", "GROUP", "workers", "worker-b", "COUNT", "1", "STREAMS", "orders", ">")) is None
        record("new-message read does not recover pending work", "null")
        run("docker", "restart", c)
        wait_until(lambda: cli("PING") == '"PONG"')
        pending = json.loads(cli("XPENDING", "orders", "workers"))
        assert pending[0] == 1
        record("pending entry survives clean AOF-backed restart", pending[0])
        claimed = wait_until(lambda: (r if (r := json.loads(cli("XAUTOCLAIM", "orders", "workers", "worker-b", "100", "0-0", "COUNT", "10")))[1] else None))
        assert claimed[1][0][0] == event
        record("worker-b claims the same event", claimed)
        assert cli("XACK", "orders", "workers", event) == "1"
        assert cli("XACK", "orders", "workers", event) == "0"
        assert json.loads(cli("XPENDING", "orders", "workers"))[0] == 0
        assert cli("XLEN", "orders") == "1"
        record("ack clears pending state without deleting stream entry", {"pending": 0, "length": 1})


def kafka():
    with container("apache/kafka:4.1.0", "-v", f"{ROOT / 'kafka'}:/work:ro") as c:
        def kafka_cmd(script, *args):
            return run("docker", "exec", c, f"/opt/kafka/bin/{script}.sh", *args)
        wait_until(lambda: "orders" in kafka_cmd("kafka-topics", "--bootstrap-server", "localhost:9092", "--create", "--if-not-exists", "--topic", "orders", "--partitions", "1", "--replication-factor", "1"), timeout=90)
        with tempfile.TemporaryDirectory() as directory:
            run("docker", "cp", f"{c}:/opt/kafka/libs", directory)
            output = run("docker", "run", "--rm", "--network", f"container:{c}",
                         "-v", f"{directory}/libs:/libs:ro", "-v", f"{ROOT / 'kafka'}:/work:ro",
                         "eclipse-temurin:21.0.8_9-jdk-alpine", "java", "--class-path", "/libs/*", "/work/Replay.java")
        assert "REPLAY after consumer close: offset=0" in output
        assert "RESUME next record: offset=1 key=ord-2" in output
        record("Kafka offset replay and committed resume", output)


def rabbitmq():
    with container("rabbitmq:4.1.4-management-alpine") as c:
        wait_until(lambda: "Ping succeeded" in run("docker", "exec", "--user", "rabbitmq", c, "rabbitmq-diagnostics", "ping"), timeout=90)
        output = run("docker", "run", "--rm", "--network", f"container:{c}", "-v", f"{ROOT / 'rabbitmq'}:/work:ro",
                     "python:3.13.7-alpine", "sh", "-c", "pip install --quiet pika==1.3.2 && python /work/recovery.py")
        assert output.count("PASS") == 5, output
        record("RabbitMQ confirms and redelivery", output)


def prometheus():
    output = run("docker", "run", "--rm", "-v", f"{ROOT / 'prometheus'}:/work:ro", "-w", "/work",
                 "--entrypoint", "/bin/promtool", "prom/prometheus:v3.5.0", "test", "rules", "tests.yml")
    assert "SUCCESS" in output, output
    record("PromQL firing, pending, idle, missing-data, counter-reset and scrape-failure fixtures", output)


def http_json(url, data=None, auth=False):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = "Basic " + base64.b64encode(b"admin:local-lab-only").decode()
    req = urllib.request.Request(url, data=None if data is None else json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.load(response)


def grafana():
    network = "emminex-dd-" + uuid.uuid4().hex[:10]
    run("docker", "network", "create", network)
    try:
        with tempfile.TemporaryDirectory() as directory:
            # Grafana runs as a non-root user on Linux bind mounts.
            pathlib.Path(directory).chmod(0o755)
            dashboard_path = pathlib.Path(directory) / "dashboard.json"
            shutil.copyfile(ROOT / "grafana/dashboard.json", dashboard_path)
            with container("prom/prometheus:v3.5.0", "--network", network, "--network-alias", "metrics",
                           "-v", f"{ROOT / 'grafana/prometheus.yml'}:/etc/prometheus/prometheus.yml:ro"):
                with container("grafana/grafana:12.1.1", "--network", network, "-p", "127.0.0.1::3000",
                               "-e", "GF_SECURITY_ADMIN_PASSWORD=local-lab-only",
                               "-e", "GF_AUTH_ANONYMOUS_ENABLED=true", "-e", "GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer",
                               "-v", f"{ROOT / 'grafana/provisioning'}:/etc/grafana/provisioning:ro",
                               "-v", f"{directory}:/var/lib/grafana/dashboards:ro") as c:
                    port = run("docker", "port", c, "3000/tcp").rsplit(":", 1)[1]
                    url = "http://127.0.0.1:" + port
                    wait_until(lambda: http_json(url + "/api/health").get("database") == "ok")
                    dashboard = wait_until(lambda: http_json(url + "/api/dashboards/uid/reliability-lab"))
                    assert dashboard["meta"]["provisioned"] is True
                    assert dashboard["dashboard"]["panels"][0]["datasource"]["uid"] == "prom-lab"
                    health = wait_until(lambda: http_json(url + "/api/datasources/uid/prom-lab/health", auth=True))
                    assert health["status"] == "OK", health
                    record("dashboard and healthy datasource provisioned with stable UIDs", health)
                    try:
                        http_json(url + "/api/dashboards/db", {"dashboard": dashboard["dashboard"], "overwrite": True}, auth=True)
                    except urllib.error.HTTPError as error:
                        response = error.read().decode()
                        assert error.code == 400 and "provisioned" in response, response
                        record("API cannot overwrite file-owned dashboard", response)
                    else:
                        raise AssertionError("File-owned dashboard accepted an API overwrite")
                    changed = json.loads(dashboard_path.read_text())
                    changed["title"] = "Provisioned reliability dashboard: revised"
                    dashboard_path.write_text(json.dumps(changed))
                    wait_until(lambda: http_json(url + "/api/dashboards/uid/reliability-lab")["dashboard"]["title"] == changed["title"])
                    record("file update applied without changing dashboard UID", changed["title"])
                    if os.environ.get("CAPTURE_SCREENSHOTS") == "1":
                        run("node", str(ROOT / "render.mjs"), "--url", url + "/d/reliability-lab?orgId=1&from=now-1m&to=now",
                            str(ROOT / "assets/grafana-dashboard.png"))
    finally:
        run("docker", "network", "rm", network, check=False)


def nginx():
    network = "emminex-dd-" + uuid.uuid4().hex[:10]
    run("docker", "network", "create", network)
    try:
        with contextlib.ExitStack() as stack:
            for name in ("a", "b"):
                backend = stack.enter_context(container("python:3.13.7-alpine", "--network", network, "--network-alias", name,
                    "-e", f"BACKEND_NAME={name}", "-v", f"{ROOT / 'nginx'}:/work:ro", command=("python", "/work/backend.py")))
                wait_until(lambda: run("docker", "exec", backend, "python", "-c", "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/stats').status)") == "200")
            c = stack.enter_context(container("nginx:1.28.0-alpine", "--network", network, "-p", "127.0.0.1::8080",
                "-v", f"{ROOT / 'nginx/nginx.conf'}:/etc/nginx/nginx.conf:ro"))
            port = run("docker", "port", c, "8080/tcp").rsplit(":", 1)[1]
            url = "http://127.0.0.1:" + port
            response = wait_until(lambda: http_json(url))
            assert response["backend"] == "b"
            record("GET retried after primary 503 and succeeded at backup", response)
            try:
                http_json(url, {"order_id": "ord-42"})
            except urllib.error.HTTPError as error:
                response = json.loads(error.read())
                assert error.code == 503 and response == {"backend": "a", "posts": 1}, response
                record("POST applied by primary then returned 503 without proxy retry", response)
            else:
                raise AssertionError("POST unexpectedly succeeded at backup")
            output = run("docker", "logs", c)
            record("upstream attempts captured in access log", "\n".join(line for line in output.splitlines() if line.startswith(("GET ", "POST "))))
    finally:
        run("docker", "network", "rm", network, check=False)


def otel_export(config):
    with tempfile.TemporaryDirectory() as directory:
        pathlib.Path(directory).chmod(0o777)
        with container("otel/opentelemetry-collector-contrib:0.133.0", "-p", "127.0.0.1::4318",
                       "-v", f"{ROOT / 'otel' / config}:/etc/otelcol-contrib/config.yaml:ro",
                       "-v", f"{directory}:/evidence") as c:
            port = run("docker", "port", c, "4318/tcp").rsplit(":", 1)[1]
            payload = json.loads((ROOT / "otel/request.json").read_text())
            wait_until(lambda: http_json("http://127.0.0.1:" + port + "/v1/traces", payload) is not None)
            path = pathlib.Path(directory) / "traces.json"
            wait_until(lambda: path.exists() and path.stat().st_size > 0)
            return json.loads(path.read_text().splitlines()[0])


def otel():
    export = otel_export("collector.yml")
    resource = export["resourceSpans"][0]
    span = resource["scopeSpans"][0]["spans"][0]
    attrs = {a["key"]: a["value"] for a in span["attributes"]}
    assert "user.email" not in attrs and "http.request.header.authorization" not in attrs
    assert attrs["customer.tier"]["stringValue"] == "pro"
    assert all(a["key"] != "host.name" for a in resource["resource"]["attributes"])
    record("configured span and resource attributes removed before export", attrs)
    assert "event-probe@example.test" in json.dumps(span["events"])
    record("boundary test: span-event attribute survives the first pipeline", span["events"])
    (ROOT / "evidence/otel-export-before.json").write_text(json.dumps(export, indent=2) + "\n")
    fixed = otel_export("collector-events.yml")
    assert "event-probe@example.test" not in json.dumps(fixed)
    assert "synthetic-person@example.test" not in json.dumps(fixed)
    assert "Bearer synthetic-test-value" not in json.dumps(fixed)
    assert "synthetic-host" not in json.dumps(fixed)
    assert "customer.tier" in json.dumps(fixed)
    record("explicit span-event transform removes the tested leak", "All three synthetic sensitive values absent; customer.tier retained")
    (ROOT / "evidence/otel-export-after.json").write_text(json.dumps(fixed, indent=2) + "\n")


def buildkit():
    tag = "emminex-dd-build:" + uuid.uuid4().hex[:10]
    try:
        with tempfile.TemporaryDirectory() as directory:
            token = pathlib.Path(directory) / "token"
            token.write_text("synthetic-token-alpha")
            def build(epoch):
                result = subprocess.run(["docker", "build", "--progress=plain", "--secret", f"id=token,src={token}",
                    "--build-arg", f"CACHE_EPOCH={epoch}", "--build-arg", f"LAB_RUN={tag}", "-t", tag, str(ROOT / "buildkit")], capture_output=True, text=True, timeout=180)
                EVENTS.append({"build_epoch": epoch, "stdout": result.stdout, "stderr": result.stderr, "exit": result.returncode})
                assert result.returncode == 0, result.stderr
                assert "synthetic-token-" not in result.stdout + result.stderr, "Secret sentinel appeared in build logs"
                return result.stderr
            build("1")
            token.write_text("synthetic-token-beta")
            second = build("1")
            assert re.search(r"#(\d+) \[build [^\]]+\] RUN --mount=type=secret[^\n]*\n#\1 CACHED", second), second
            record("changing only the secret reuses the secret-consuming RUN step", "CACHED")
            build("2")
            cid = run("docker", "create", tag, "/unused")
            try:
                archive = pathlib.Path(directory) / "rootfs.tar"
                run("docker", "export", "-o", str(archive), cid)
                with tarfile.open(archive) as files:
                    artifact = files.extractfile("artifact").read().decode().strip()
                    assert artifact == "2"
                    assert all("run/secrets" not in n for n in files.getnames())
                assert b"synthetic-token-" not in archive.read_bytes()
                record("explicit cache epoch rebuilds artifact without secret file", artifact)
            finally:
                run("docker", "rm", cid, check=False)
            history = run("docker", "history", "--no-trunc", tag)
            assert "synthetic-token-" not in history
            record("final image history contains no synthetic secret value", history)
            missing = subprocess.run(["docker", "build", "--progress=plain", "--build-arg", "CACHE_EPOCH=missing-secret", "--build-arg", f"LAB_RUN={tag}",
                "-t", tag, str(ROOT / "buildkit")], text=True, capture_output=True, timeout=180)
            EVENTS.append({"missing_secret_exit": missing.returncode, "stderr": missing.stderr})
            assert missing.returncode != 0 and "secret" in missing.stderr and "not found" in missing.stderr
            record("uncached required-secret step fails when the secret is absent", missing.returncode)
    finally:
        run("docker", "image", "rm", tag, check=False)


def kubernetes():
    kind = os.environ.get("KIND", "kind")
    cluster = "emminex-dd-" + uuid.uuid4().hex[:8]
    with tempfile.TemporaryDirectory() as directory:
        config = pathlib.Path(directory) / "kubeconfig"
        def kubectl(*args):
            return run("kubectl", "--kubeconfig", str(config), *args)
        try:
            run(kind, "create", "cluster", "--name", cluster, "--kubeconfig", str(config), "--image", "kindest/node:v1.34.0", "--wait", "120s", timeout=300)
            kubectl("create", "configmap", "draining-app", "--from-file", str(ROOT / "kubernetes/app.py"))
            kubectl("apply", "-f", str(ROOT / "kubernetes/pod.yml"))
            kubectl("wait", "--for=condition=Ready", "pod/draining-app", "--timeout=120s")
            with open(pathlib.Path(directory) / "forward.log", "w+") as forwardlog:
                forward = subprocess.Popen(["kubectl", "--kubeconfig", str(config), "port-forward", "pod/draining-app", ":8080", "--address", "127.0.0.1"], stdout=forwardlog, stderr=forwardlog, text=True)
                logs = subprocess.Popen(["kubectl", "--kubeconfig", str(config), "logs", "-f", "draining-app"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    def port_ready():
                        forwardlog.seek(0)
                        content = forwardlog.read()
                        import re
                        match = re.search(r"127\.0\.0\.1:(\d+)", content)
                        return match.group(1) if match else None
                    port = wait_until(port_ready)
                    url = "http://127.0.0.1:" + port
                    # The work handler intentionally runs for six seconds.
                    def request():
                        with urllib.request.urlopen(url + "/work", timeout=15) as response:
                            return json.load(response)
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(request)
                        wait_until(lambda: "work_started" in kubectl("logs", "draining-app"))
                        kubectl("delete", "pod", "draining-app", "--wait=false")
                        endpoint = json.loads(kubectl("get", "endpointslice", "-l", "kubernetes.io/service-name=draining-app", "-o", "json"))
                        record("EndpointSlice observed during deletion", [e["conditions"] for item in endpoint["items"] for e in item["endpoints"]])
                        response = future.result(timeout=15)
                        assert response == {"completed": True}, response
                        record("in-flight request completes during graceful deletion", response)
                    output, errors = logs.communicate(timeout=30)
                    assert '"event": "sigterm"' in output and '"event": "shutdown_complete"' in output, output + errors
                    record("application lifecycle logs", output)
                finally:
                    for process in (forward, logs):
                        if process.poll() is None:
                            process.terminate()
                            process.wait(timeout=10)
        finally:
            run(kind, "delete", "cluster", "--name", cluster, check=False)


LABS = {"postgres": postgres, "redis": redis, "kafka": kafka, "rabbitmq": rabbitmq,
        "prometheus": prometheus, "grafana": grafana, "nginx": nginx, "otel": otel,
        "buildkit": buildkit, "kubernetes": kubernetes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", choices=LABS)
    name = parser.parse_args().lab
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ok = False
    try:
        LABS[name]()
        ok = True
    finally:
        output = ROOT / "evidence" / f"{name}.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps({"lab": name, "started_at": start, "passed": ok, "events": EVENTS}, indent=2) + "\n")
    print(f"Evidence saved to {output}")


if __name__ == "__main__":
    main()
