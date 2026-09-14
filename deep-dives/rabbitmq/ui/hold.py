"""Leave one real delivery unacknowledged for inspection in RabbitMQ management."""
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='broker', credentials=pika.PlainCredentials('lab', 'local-lab-only'), heartbeat=30))
channel = connection.channel()
channel.queue_declare(queue='orders-ui', durable=True)
channel.confirm_delivery()
channel.basic_publish('', 'orders-ui', b'{"order_id":"ord-42"}', mandatory=True,
                      properties=pika.BasicProperties(delivery_mode=2, message_id='ord-42'))
method, properties, body = channel.basic_get('orders-ui', auto_ack=False)
assert method is not None
print('Confirmed publication; holding delivery without acknowledgement:', body.decode(), flush=True)
try:
    while True:
        connection.process_data_events(time_limit=1)
        time.sleep(.1)
finally:
    connection.close()
