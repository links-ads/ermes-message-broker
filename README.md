# ERMES message broker

Message broker service for the ERMES platform.

## Description

In the ERMES ecosystem, the message broker handles all the asynchronous communication, managing event-based services such as
map requests, sensor messages, and so on.

This repository provides a standard deployment, without project-specific configuration. The latter should be customized to your needs.

## Installation

The tool is run using Docker Compose, make sure to install it before proceeding.
This setup has been tested on Linux machines only, we do not exclude that it might work on other systems, up to you to test it!

```bash
$ docker compose up
```
