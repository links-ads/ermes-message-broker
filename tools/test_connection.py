import argparse
import os
import ssl

import pika


def parse_arguments():
    parser = argparse.ArgumentParser(description="Connect to RabbitMQ server using TLS")
    parser.add_argument(
        "--username", default="admin", help="Username for RabbitMQ authentication"
    )
    parser.add_argument(
        "--password", default="admin", help="Password for RabbitMQ authentication"
    )
    parser.add_argument(
        "--server-host", default="localhost", help="URL of RabbitMQ server"
    )
    parser.add_argument("--server-port", default=5671, help="Port of RabbitMQ server")
    parser.add_argument(
        "--server-vhost", default="/", help="Virtual host of RabbitMQ server"
    )
    parser.add_argument(
        "--ca-cert-file", "-CA", required=True, help="File to the CA certificate file"
    )
    parser.add_argument(
        "--cert-file", "-C", required=True, help="File to the client certificate file"
    )
    parser.add_argument(
        "--key-file", "-K", required=True, help="File to the client key file"
    )
    return parser.parse_args()


def get_tls_parameters(hostname: str, ca_cert_file: str, cert_file: str, key_file: str):
    context = ssl.create_default_context(cafile=ca_cert_file)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(
        certfile=cert_file,
        keyfile=key_file,
    )
    return pika.SSLOptions(context, server_hostname=hostname)


def main():
    args = parse_arguments()
    ca_file = os.path.abspath(args.ca_cert_file)
    cert_file = os.path.abspath(args.cert_file)
    key_file = os.path.abspath(args.key_file)
    assert os.path.exists(ca_file), f"CA certificate file not found: {ca_file}"
    assert os.path.exists(cert_file), f"Client certificate file not found: {cert_file}"
    assert os.path.exists(key_file), f"Client key file not found: {key_file}"

    credentials = pika.credentials.ExternalCredentials()
    ssl_options = get_tls_parameters(args.server_host, ca_file, cert_file, key_file)

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=credentials,
                host=args.server_host,
                port=args.server_port,
                ssl_options=ssl_options,
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
        channel.queue_delete(queue="q.hello")
        # last, we close the channel and connection to free the resources
        channel.close()
        connection.close()


if __name__ == "__main__":
    main()
