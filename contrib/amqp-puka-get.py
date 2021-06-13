#!/usr/bin/env python

from __future__ import print_function
import sys
import puka
import json

exchange = 'mqttwarn'
routing_key = 'all'

client = puka.Client('amqp://guest:guest@localhost')
promise = client.connect()
client.wait(promise)

promise = client.exchange_declare(exchange=exchange, type='direct')
client.wait(promise)

promise = client.queue_declare(exclusive=True)
queue_name = client.wait(promise)['queue']

promise = client.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)
client.wait(promise)

consume = client.basic_consume(queue=queue_name, no_ack=False)
while True:
    try:
        msg = client.wait(consume)
        print(json.dumps(msg, indent=4))
        client.basic_ack(msg)
    except KeyboardInterrupt:
        client.close()
        sys.exit(0)

