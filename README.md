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

To facilitate the certificate generation, a script is provided in the [certs](certs/) folder, using `openssl` to generate the necessary files.

The steps to get a full container up and running are as follows:

1. Launch the [certs/certgen.sh](certs/certgen.sh) script to generate the necessary files, namely CA and server certificates.

```bash
# Generate the CA certificate and key
$ bash certs/certgen.sh -c example.com -o organization ca
# Generate the server certificate and key
$ bash certs/certgen.sh -c example.com -o organization server
# Generate certificate and key for every client
$ bash certs/certgen.sh -c username -o organization client
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

5. Connect to the broker using the client certificate and the user created in the previous step. You can test the connection using the [tools/test_connection.py](tools/test_connection.py) script (remember to create a virtual environment and install `pika`).

6. Configure `nginx` or similar tools to handle the reverse proxy to the management dashboard. Check the [nginx](/nginx/) folder for an example configuration.

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
