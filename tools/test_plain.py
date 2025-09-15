import argparse
import ssl
import warnings

import pika
from pika.credentials import PlainCredentials


def parse_arguments():
    parser = argparse.ArgumentParser(description="Connect to RabbitMQ server using TLS")
    parser.add_argument(
        "--username", required=True, help="Username for RabbitMQ authentication"
    )
    parser.add_argument(
        "--password", required=True, help="Password for RabbitMQ authentication"
    )
    parser.add_argument(
        "--server-host", default="localhost", help="URL of RabbitMQ server"
    )
    parser.add_argument("--server-port", default=5671, help="Port of RabbitMQ server")
    parser.add_argument(
        "--server-vhost", default="/", help="Virtual host of RabbitMQ server"
    )
    parser.add_argument("--ca-cert", "-CA", default=None, help="CA certificate file")
    return parser.parse_args()


def get_ssl_context(ca_cert_file: str | None):
    context = ssl.create_default_context(cafile=ca_cert_file)
    if ca_cert_file is None:
        warnings.warn(
            "No CA certificate was provided, skipping the hostname verification."
        )
        context.check_hostname = False  # Since you're likely using IP addresses
        context.verify_mode = ssl.CERT_NONE
    return context


def main():
    args = parse_arguments()
    credentials = PlainCredentials(args.username, args.password)
    ssl_context = get_ssl_context(args.ca_cert)
    channel = connection = None
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=credentials,
                host=args.server_host,
                port=args.server_port,
                ssl_options=pika.SSLOptions(ssl_context),
            )
        )
        channel = connection.channel()

        # Example usage: Declare a queue and bind "hello.something" messages to it
        channel.queue_declare(queue="q.hello")
        channel.queue_bind(exchange="amq.topic", queue="q.hello", routing_key="hello.#")
        # Now publish a message to the same exchange: the exchange will take care of
        # delivering the payload to every queue that matches the routing key
        channel.basic_publish(
            exchange="amq.topic", routing_key="hello", body="Hello, RabbitMQ!"
        )
        print("[Publisher] Sent 'Hello, RabbitMQ!'")

        def callback(ch, method, properties, body):
            # We expect to receive a single message,
            # after that we can stop consuming to continue the execution and exit
            print(f"[Consumer] Received message '{method.routing_key}': {body}")
            channel.stop_consuming()

        # declare how to handle messages, in this case we read from q.hello
        # and we handle messages using the `callback` function
        channel.basic_consume(
            queue="q.hello", on_message_callback=callback, auto_ack=True
        )
        # We can now start consuming, note: this is blocking!
        channel.start_consuming()

    finally:
        # the queue does not need to be created and destroyed each time
        # in a production setting, the queues will be fixed and persistent
        if channel:
            channel.queue_delete(queue="q.hello")
            # last, we close the channel and connection to free the resources
            channel.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
