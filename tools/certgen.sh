#!/bin/bash

# Initialize variables for CN and ORG
cn=""
org=""

# Destination directory for certificates
cert_dir="certs"
ca_cert="$cert_dir/ca_certificate.pem"
ca_key="$cert_dir/ca_key.pem"
server_cert="$cert_dir/server_certificate.pem"
server_csr="$cert_dir/server_csr.pem"
server_key="$cert_dir/server_key.pem"

# Parse command line options for CN and ORG
while getopts ":c:o:" opt; do
  case ${opt} in
    c )
      cn=$OPTARG
      ;;
    o )
      org=$OPTARG
      ;;
    \? )
      printf "Invalid option: $OPTARG\n" 1>&2
      exit 1
      ;;
    : )
      printf "Invalid option: $OPTARG requires an argument\n" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

# Function to generate CA files
generate_ca() {
    openssl genrsa -out $ca_key 2048
    openssl req -x509 -sha256 -new -nodes -days 3650 \
      -key $ca_key -out $ca_cert
}

# Function to generate server certificate
generate_server_cert() {
    openssl genrsa -out $server_key 2048
    openssl req -new -key $server_key -out $server_csr \
      -subj "/O=$org/CN=$cn" \
      -addext "subjectAltName = DNS:localhost,DNS:$cn,DNS:*.$cn"
    openssl x509 -req -in $server_csr -CA $ca_cert -CAkey $ca_key -CAcreateserial \
      -out $server_cert -days 3650  -sha256
}

# Function to generate client certificate
generate_client_cert() {
    openssl genrsa -out "$cert_dir/client_${org}_key.pem" 2048
    openssl req -new -key "$cert_dir/client_${org}_key.pem" -out "$cert_dir/client_${org}_csr.pem" \
      -subj "/O=$org/CN=$cn" \
      -addext "subjectAltName = DNS:localhost,DNS:$cn,DNS:*.$cn"
    openssl x509 -req -in "$cert_dir/client_${org}_csr.pem" \
      -CA $ca_cert -CAkey $ca_key -CAcreateserial \
      -out "$cert_dir/client_${org}_certificate.pem" -days 3650 -sha256
}

# Main function to handle user commands
main() {
    if [[ -z "$cn" || -z "$org" ]]; then
        printf "CN and ORG must be provided. Usage: %s -c <CN> -o <ORG> {ca|server|client}\n" "$0" >&2
        exit 1
    fi

    case "$1" in
        ca)
            generate_ca
            printf "CA certificate generated successfully.\n"
            ;;
        server)
            generate_server_cert
            printf "Server certificate generated successfully.\n"
            ;;
        client)
            generate_client_cert
            printf "Client certificate generated successfully.\n"
            ;;
        *)
            printf "Usage: %s -c <CN> -o <ORG> ca|server|client\n" "$0" >&2
            return 1
            ;;
    esac
}

main "$@"