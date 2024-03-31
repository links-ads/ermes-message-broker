ARG RABBITMQ_VERSION=3.12-management-alpine

FROM rabbitmq:${RABBITMQ_VERSION}

ARG RABBITMQ_PLUGINS="rabbitmq_auth_mechanism_ssl"

# Copy certificates and make them accessible to the rabbitmq user
COPY certs/ca_certificate.pem certs/server_certificate.pem certs/server_key.pem /etc/rabbitmq/certs/
RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/certs


# Copy the configuration file
COPY containers/rabbitmq/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
RUN rabbitmq-plugins enable --offline ${RABBITMQ_PLUGINS}
