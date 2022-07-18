#!/usr/bin/env python
import pika, sys, os, ssl

from datetime import datetime

import multiprocessing
import time
from random import random


def time_stamp():
    now = datetime.now()  # current date and time
    return now.strftime("%Y-%m-%dT%H:%M:%S")


def rmq_consume():
    rabbitmq_host = "rabbitmq"
    rabbitmq_user = "rmq-user"
    rabbitmq_pass = "rmq-pass"
    rabbitmq_vhost = "rmq-vhost"
    rabbitmq_queue = "rmq-queue"
    rabbitmq_usessl = False

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)

    conn_params = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=5672,
        virtual_host=rabbitmq_vhost,
        credentials=credentials,
        heartbeat=0,
        blocked_connection_timeout=1,
        socket_timeout=1,
    )

    if rabbitmq_usessl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        conn_params.port = 5671
        conn_params.ssl_options = pika.SSLOptions(ssl_context)

    # Create blocking connection
    try:
        connection = pika.BlockingConnection(conn_params)
    except:
        print("x", end="", flush=True)
        return

    # Create channel
    channel = connection.channel()
    channel.queue_declare(
        queue=rabbitmq_queue,
        durable=True,
        auto_delete=False,
        arguments={"x-queue-type": "quorum"},
    )

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(
        queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False
    )
    # print("%r Start consuming" % time_stamp())
    print(".", end="", flush=True)
    channel.start_consuming()


def start_with_timeout(timeout, function):
    # Start foo as a process
    p = multiprocessing.Process(target=function, name="Foo")
    p.start()
    time.sleep(timeout)
    p.terminate()
    p.join()


if __name__ == "__main__":
    # timeout = 2
    workers = 256
    worker_list = []
    prev_stamp = "1970-01-01T00:00:00"
    while True:
        new_stamp = time_stamp()
        if prev_stamp != new_stamp:
            print("\n%r Start consuming: " % new_stamp, end="")
            prev_stamp = new_stamp
        try:
            worker_list = [worker for worker in worker_list if worker.is_alive()]
            while len(worker_list) < workers:
                worker_list.append(
                    multiprocessing.Process(
                        target=start_with_timeout,
                        name="Foo",
                        args=(3 + random(), rmq_consume),
                    )
                )
                worker_list[-1].start()
                time.sleep(random() / workers)
            time.sleep(random() / (2 * workers))
        except KeyboardInterrupt:
            print("Interrupted")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
