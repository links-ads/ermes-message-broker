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

RabbitMQ is configured to use the default SSL port on `5671` for AMQP, while `nginx` acts as reverse proxy for the web UI.

Authentication is enabled through the `PLAIN` and `EXTERNAL` mechanisms.
 - `PLAIN` requires simple **username** and **password** authentication, with an empty SSL context.
 - `EXTERNAL` is instead a key-based authentication, requiring `client_certificate.pem` and `client_key.pem`, similar to a SSH public key authentication. In this case, the certificate's Common Name (CN) in the client certificate must match the RabbitMQ username.

To facilitate the certificate generation, a script is provided in the [certs](certs/) folder, using `openssl` to generate the necessary files.

The steps to get a full container up and running are as follows:

1. Launch the [certs/certgen.sh](certs/certgen.sh) script to generate the necessary files, namely CA and server certificates.

```bash
# Generate the CA certificate and key
$ bash certs/certgen.sh -c example.com -o <organization> ca
# Generate the server certificate and key
$ bash certs/certgen.sh -c example.com -o <organization> server
# (Optional)For EXTERNAL auth, enerate certificate and key for every client
$ bash certs/certgen.sh -c <username> -o <organization> client
```

Where `-c` is the Common Name of the certificate, while `-o` is the organization name.
The script will generate the necessary files in the `certs` folder.

2. Copy the `env.example` file to `.env` and edit it to your needs, settings the admin credentials.

2. Build and run the broker container with:

```bash
$ docker compose up --build [-d]
```

3. Enter the management dashboard exposed on port `15672` and log in with the credentials provided in the `.env` file.

4. Create a new user with the same name as the CN of the client certificate, and assign it the required permissions.

### Testing the connection

In the `tools` directory you will find two simple Python scripts using `pika`. To launch them you'll first need a Python distribution and the `pika` library installed, e.g.:

```bash
$ uv venv
$ uv pip install pika
```

#### Plain Credentials

This is the easiest way to connect.
1. Create a user and assign the required permissions.

2. Launch the `tools/test_plain.py` script like so:

```bash
$ python tools/test_plain.py --username <youruser> --password <yourpass> [OPTIONAL: --ca-cert <path/to/ca_certificate.pem]
```

3. If everything goes well, the script will publish and read its own `Hello!` message. Remember to provide the CA certificate file if you have one, since it's always better to verify the host you're connecting to, unless you trust it.

#### External Credentials

This is more robust, but requires 3 files in total: one CA certificate file, one client certificate, and one client key.

1. Create the user and assign the necessary permissions.

2. Launch the `tools/test_certs.py` script:

```bash
$ python tools/test_certs.py --username <user> -CA certs/ca_certificate.pem -C certs/client_certificate.pem -K certs/client_key.pem
```

### Optional: nginx proxy

The `nginx/` folder contains an example of configuration to enable HTTPS on the RabbitMQ UI. The configuration assumes that the instance will be associated with its own registered domain, and not a subpath.
It is possible to deploy the management UI under a subpath (e.g., example.com/rabbitmq), but it requires adding the following to the `rabbitmq.conf` file (and consequently rebuild the container).

```conf
management.path_prefix = /rabbitmq
```

### Optional: additional client certificates

If you need to add more client certificates, you can use the same script as before, but adding the `client` flag at the end.

```bash
$  bash certs/certgen.sh -c new_user -o new_org client
```
This will generate a new client certificate and key in the `certs` folder, which you can share with the client.

> [!IMPORTANT]
>
> Remember to create a new user in the RabbitMQ management dashboard with the same name as the CN of the client certificate, assign it the required permissions, and share the triplet of `ca_certificate.pem`, `client_certificate.pem`, and `client_key.pem` with the actual client, together with the selected username.

> [!WARNING]
>
> The server certificate will use the Alternative Name (SAN) field to allow multiple CNs, this means that for new deployments you will need to regenerate the server certificate with the new CNs.
