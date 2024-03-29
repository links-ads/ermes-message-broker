#!/bin/bash

# This script automates the process of cloning the RabbitMQ TLS generation utility,
# generating TLS certificates, and copying the generated certificates to a specific
# directory expected by a RabbitMQ container setup.
#
# The script operates in two main modes:
# 1. Default mode: clones the 'tls-gen' repository into the current working directory
#    (if not already cloned), generates certificates with default parameters, and copies
#    them to the specified destination.
# 2. Generate mode: If the repository is already cloned, this mode allows for generating
#    certificates with custom arguments without cloning the repository again.
#
# Usage:
#   Without arguments: 
#     ./certificates.sh
#     - Clones the 'tls-gen' repository (if necessary), generates certificates with default
#       parameters, and copies them to the destination directory.
#
#   With 'generate' argument:
#     ./certificates.sh generate [MAKE_ARGS]
#     - e.g., `.certificates.sh generate CN=ermes, skips cloning and directly generates
#       certificates with the specified MAKE_ARGS, then copies them to the destination directory.
#       This mode assumes that the 'tls-gen' repository is already present in the current working directory.
#
#   MAKE_ARGS are additional arguments passed to the `make` command used in the certificate
#   generation process, such as CN=foo, allowing for customization of the generated certificates.
#
# Note: The script assumes that the 'tls-gen' repository will be used in the current working
# directory and will not remove the repository after execution, making it suitable for scenarios
# where the repository's presence is needed for subsequent operations.

# Enable strict error handling
set -euo pipefail

# Global variables
REPO_URL="https://github.com/rabbitmq/tls-gen"
REPO_DIR="tls-gen" # Name of the directory to clone into
CERTS_DEST="$(pwd)/containers/rabbitmq/certs"

# Function to clone the repository
clone_repo() {
    local url="$1"
    local repo_dir="$2"
    
    if [ ! -d "$repo_dir" ]; then
        echo "Cloning repository into $repo_dir"
        if ! git clone "$url" "$repo_dir"; then
            printf "Failed to clone repository: %s\n" "$url" >&2
            return 1
        fi
    else
        echo "Repository directory $repo_dir already exists. Skipping clone."
    fi
}

# Function to generate TLS certificates with passed arguments
generate_certs() {
    local repo_dir="$1"
    shift # Shift arguments to pass additional ones to make
    
    echo "Generating TLS certificates"
    pushd "${repo_dir}/basic" > /dev/null
    if ! make "$@"; then
        printf "Failed to generate TLS certificates\n" >&2
        popd > /dev/null
        return 1
    fi
    popd > /dev/null
}

# Function to copy generated certificates to the destination
copy_certs() {
    local repo_dir="$1"
    local certs_dest="$2"
    
    echo "Copying certificates to $certs_dest"
    mkdir -p "$certs_dest"
    if ! cp -r "${repo_dir}/basic/result/." "$certs_dest"; then
        printf "Failed to copy TLS certificates to %s\n" "$certs_dest" >&2
        return 1
    fi
}

# Main function
main() {
    if [[ $# -gt 0 && "$1" == "generate" ]]; then
        # If the first argument is 'generate', shift it and proceed without cloning
        shift
        generate_certs "$REPO_DIR" "$@"
        copy_certs "$REPO_DIR" "$CERTS_DEST"
    else
        # Default behavior: clone if necessary, generate with no custom arguments, and copy
        clone_repo "$REPO_URL" "$REPO_DIR"
        generate_certs "$REPO_DIR"
        copy_certs "$REPO_DIR" "$CERTS_DEST"
    fi
    printf "TLS certificates have been successfully processed.\n"
}

# Execute the main function with all passed arguments
main "$@"