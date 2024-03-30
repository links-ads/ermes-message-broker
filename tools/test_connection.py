import argparse
import os
import ssl

import pika


def parse_arguments():
    parser = argparse.ArgumentParser(description="Connect to RabbitMQ server using TLS")
    parser.add_argument("--username", default="admin", help="Username for RabbitMQ authentication")
    parser.add_argument("--password", default="admin", help="Password for RabbitMQ authentication")
    parser.add_argument("--server-host", default="localhost", help="URL of RabbitMQ server")
    parser.add_argument("--server-port", default=5671, help="Port of RabbitMQ server")
    parser.add_argument("--server-vhost", default="/", help="Virtual host of RabbitMQ server")
    parser.add_argument("--ca-cert-file", "-CA", required=True, help="File to the CA certificate file")
    parser.add_argument("--cert-file", "-C", required=True, help="File to the client certificate file")
    parser.add_argument("--key-file", "-K", required=True, help="File to the client key file")
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

        # Example usage: Declare a queue and publish a message
        channel.queue_declare(queue="hello")
        channel.basic_publish(exchange="", routing_key="hello", body="Hello, RabbitMQ!")
        print(" [x] Sent 'Hello, RabbitMQ!'")

        connection.close()
    except pika.exceptions.AMQPError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
