# ERMES message broker

Message broker service for the ERMES platform.

## Description

In the ERMES ecosystem, the message broker handles all the asynchronous communication, managing event-based services such as
map requests, sensor messages, and so on.

This repository provides a standard deployment, without project-specific configuration. The latter should be customized to your needs.

## Installation

The tool is run using Docker Compose, make sure to install it before proceeding.
This setup has been tested on Linux machines only, we do not exclude that it might work on other systems, up to you to test it!


### SSL Configuration through Nginx
RabbitMQ itself is configured to use the default port on `5672`, while `nginx` handles the SSL and reverse proxy part.
The steps to configure this communication are as follows:

1. Register a new subdomain, e.g. `bus.example.com` for the IP of the machine you deployed this RMQ container.

2. Generate a standard SSL certificate using certbot: this will serve for both the HTTPS management dashboard and the AMQP connections.

3. Following the files in the [nginx](nginx/) folder, configure your server accordingly:

    - customize the `bus.example.conf` file to your needs, and place it under `/etc/nginx/sites-available/` (with the usual soft link to enable it).
    - customize `bus.example.certificates.conf` and `bus.example.tcp.conf` to your needs, then place them under `/etc/nginx/snippets`

4. Add the custom snippets to your main `nginx.conf`:

```conf
events {
    ...
}

http {
    ...
}

# TCP or UDP streams
stream {
    include /etc/nginx/snippets/bus.example.tcp.conf;
    ...
}
```

5. Once you've done all this, remember to edit the `env.example` file to your needs: copy it, rename it `.env`, and change every variable according to your configuration. In a usual Certbot installation, the location of your certificates should be `/etc/letsencrypt/live/bus.example.com/*` or similar.

6. You can test if everything is working by `sudo nginx -t`, and hopefully, reload the configuration to apply changes (`sudo systemctl reload nginx` or similar).

7. Once everything is ready on the main machine, simply launch the broker container with:

```bash
$ docker compose up
```

8. Enjoy your message bus!
