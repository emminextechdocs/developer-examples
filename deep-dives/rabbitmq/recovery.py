"""Publisher confirms, unroutable publications, and manual acknowledgement."""
import pika

parameters = pika.ConnectionParameters("localhost", heartbeat=30, blocked_connection_timeout=10)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue="orders", durable=True)
channel.confirm_delivery()
try:
    channel.basic_publish(exchange="", routing_key="missing-queue", body=b"ord-0", mandatory=True)
except pika.exceptions.UnroutableError:
    print("PASS unroutable mandatory publication rejected", flush=True)
else:
    raise AssertionError("Expected UnroutableError")
channel.basic_publish(exchange="", routing_key="orders", body=b"ord-42", mandatory=True,
                      properties=pika.BasicProperties(delivery_mode=2, message_id="ord-42"))
print("PASS publisher confirm received; consumer has not acknowledged", flush=True)
method, properties, body = channel.basic_get("orders", auto_ack=False)
assert body == b"ord-42"
assert not method.redelivered
print("PASS first delivery received without acknowledgement", flush=True)
connection.close()

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
import time
deadline = time.monotonic() + 10
while True:
    method, properties, body = channel.basic_get("orders", auto_ack=False)
    if method is not None:
        break
    if time.monotonic() > deadline:
        raise AssertionError("Unacknowledged message was not requeued")
    time.sleep(0.1)
assert body == b"ord-42" and method.redelivered
print("PASS disconnected consumer's message redelivered", flush=True)
channel.basic_ack(method.delivery_tag)
method, _, _ = channel.basic_get("orders", auto_ack=False)
assert method is None
print("PASS acknowledgement removed message from queue", flush=True)
connection.close()
