#!/bin/bash

set -eou pipefail

# Default to current install version, but allow -v <version> override
version=$(<"./.HA_VERSION")
while getopts v: flag
do
    case "${flag}" in
        v) version=${OPTARG};;
    esac
done


docker pull "ghcr.io/home-assistant/home-assistant:${version}"

docker run --rm \
        --entrypoint "" \
        "ghcr.io/home-assistant/home-assistant:${version}" \
        python -m homeassistant --version
    env_file_arg=""
    docker run --rm \
        --entrypoint "" \
        -v $(pwd):/github/workspace \
        -v $(pwd)/secrets_ci.yaml:/github/workspace/secrets.yaml \
        --workdir /github/workspace \
        "ghcr.io/home-assistant/home-assistant:${version}" \
        python -m homeassistant \
            --config "." \
            --script check_config
