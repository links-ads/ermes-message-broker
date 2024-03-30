# ERMES message broker

Message broker service for the ERMES platform.

## Description

In the ERMES ecosystem, the message broker handles all the asynchronous communication, managing event-based services such as
map requests, sensor messages, and so on.

This repository provides a standard deployment, without project-specific configuration. The latter should be customized to your needs.

## Installation

The tool is run using Docker Compose, make sure to install it before proceeding.
This setup has been tested on Linux machines only, we do not exclude that it might work on other systems, up to you to test it!


### SSL Authentication

RabbitMQ is configured to use the default SSL port on `5671`, while `nginx` acts as reverse proxy.

Authentication is enabled through the `EXTERNAL` mechanism, which requires the client to provide a valid SSL certificate to connect to the broker, where the Common Name (CN) must match the username.

To facilitate the certificate generation, a script is provided in the `tools` folder, which clones the [tls-gen](https://github.com/rabbitmq/tls-gen) repository and generates the necessary files.

The steps to get a full container up and running are as follows:

1. Launch the [tools/certificates.sh](tools/certificates.sh) script.

```bash
$ bash tools/certificates.sh CN=example
```

Where `CN` is the Common Name of the certificate, if empty the hostname will be used.
In a single pass, the script will take care of:
    - generating of a Certificate Authority (CA) certificate and key, a server certificate and key, and a client certificate and key
    - copying the necessary files to the `containers/rabbitmq/certs` folder for the container to use.

2. Copy the `env.example` file to `.env` and edit it to your needs.

2. Build and run the broker container with:

```bash
$ docker compose up --build [-d]
```

3. Enter the management dashboard exposed on port `15672` and log in with the credentials provided in the `.env` file.

4. Create a new user with the same name as the CN of the client certificate, and assign it the required permissions.

5. Connect to the broker using the client certificate and the user created in the previous step. You can test the connection using the [tools/test_connection.py](tools/test_connection.py) script (remember to create a virtual environment and install `pika`).

6. Configure `nginx` or any other reverse proxy to handle both the SSL AMQP connection and the management dashboard. Check the [nginx](/nginx/) folder for an example configuration.

### Optional: additional client certificates

If you need to add more client certificates, you can use the same script as before, but adding the `gen-client` flag at the end.

```bash
$ bash tools/certificates.sh CN=example gen-client
```
This will generate a new client certificate and key, and copy them to the `containers/rabbitmq/certs` folder once again.

> [!IMPORTANT]
>
> Remember to create a new user in the RabbitMQ management dashboard with the same name as the CN of the client certificate, assign it the required permissions, and share the triplet of `ca_certificate.pem`, `client_certificate.pem`, and `client_key.pem` with the actual client, together with the selected username.
